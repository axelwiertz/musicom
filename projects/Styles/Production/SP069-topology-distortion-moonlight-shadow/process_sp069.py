# -*- coding: utf-8 -*-
"""SP-069 Switched Discrete Distortion Topology Bank (FuzzBillion-style)
applied to moonlight-shadow (pop, E major, 126 BPM, 32 bars).

Absolute-layer method: run the WHOLE piece through the 11-switch nonlinear
chain. Two circuit variants + dry reference:
  - full_mix   dry FluidSynth reference (no distortion), mastered
  - fuzz_ge    germanium/soft-saturation chain (main SP-069 treatment)
  - fuzz_hard  transformer+CMOS+opamp hard-clip chain (alt)

Mastering to pop target (target_for_style), -1 dBTP ceiling. Dual artifacts:
WAV + Opus OGG, plus per-track stems for DAW import.
"""
import os
import gc
import json
import subprocess

import numpy as np

from sound.effects.topology_distortion import FuzzBillion, circuit_count, random_code
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
ANA = os.path.join(HERE, "Analysis")
STEM = os.path.join(AUD, "stems")
for d in (AUD, MID, ANA, STEM):
    os.makedirs(d, exist_ok=True)

SRC_MIDI = os.path.join(MID, "moonlight-shadow-clean.mid")
SF = discover_soundfont()
FLUID = fluidsynth_bin()
STYLE = "pop"
BPM = 126


def log(*a):
    print(*a, flush=True)


# ---- 1. dry full mix (reference) ---------------------------------------
mix_path = os.path.join(AUD, "full_mix.wav")
r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", mix_path, SF, SRC_MIDI],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)
N = len(audio)
dur = N / sr
log("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))

# ---- 2. stems -----------------------------------------------------------
pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=sr)
stems = pipe.render_stems(SRC_MIDI, STEM, format="wav")
stem_keys = sorted(stems.keys())
log("stems:", stem_keys)

# ---- 3. FuzzBillion circuits --------------------------------------------
fb = FuzzBillion(sample_rate=sr)
total_circuits = circuit_count()
log("distinct circuits: %d (10**11)" % total_circuits)

code_ge = fb.random_circuit(seed=6901)
name_ge = fb.circuit_name()
code_hard = random_code(seed=6902)
fb.code = code_hard
name_hard = fb.circuit_name()
log("circuit A (fuzz_ge):", code_ge)
log("circuit B (fuzz_hard):", code_hard)

# profile each circuit on a steady 220 Hz sine
prof_ge = fb.profile(freq=220.0, code=code_ge, gain=2.0)
prof_hard = fb.profile(freq=220.0, code=code_hard, gain=3.0)
log("profile fuzz_ge:", prof_ge)
log("profile fuzz_hard:", prof_hard)


def distort(wav_path, out_raw, code, gain, io_mode):
    a, sr2 = read_wav(wav_path)
    out = fb.process(a, code=code, gain=gain, io_mode=io_mode)
    out = np.asarray(out, dtype=np.float32)
    write_wav(out_raw, out, sr2, normalize=True)
    del a, out
    gc.collect()


# fuzz_ge: germanium-ish soft chain (main)
distort(mix_path, os.path.join(AUD, "fuzz_ge_raw.wav"), code_ge, 2.0, "inst")
# fuzz_hard: transformer+cmos+opamp chain (alt)
distort(mix_path, os.path.join(AUD, "fuzz_hard_raw.wav"), code_hard, 3.0, "line")
log("distortion renders done")

# ---- 4. spectral / pitch sanity ----------------------------------------
def spectral_report(name, sig):
    mono = sig.mean(axis=1) if sig.ndim == 2 else sig
    mono = mono - mono.mean()
    n = len(mono)
    mag = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    band = (freqs >= 50) & (freqs <= 1000)
    bb = mag[band]
    ff = freqs[band]
    dom = float(ff[int(np.argmax(bb))])
    total = float(np.sum(mag ** 2)) + 1e-18
    band_frac = float(np.sum(bb ** 2) / total)
    low = (freqs >= 40) & (freqs < 300)
    low_frac = float(np.sum(mag[low] ** 2) / total)
    return {"dominant_hz": round(dom, 1), "band_energy_frac": round(band_frac, 4),
            "low_energy_frac": round(low_frac, 4)}


spec = {}
for name in ("full_mix", "fuzz_ge", "fuzz_hard"):
    src = os.path.join(AUD, name + (".wav" if name == "full_mix" else "_raw.wav"))
    a, _ = read_wav(src)
    spec[name] = spectral_report(name, a)
    log("SPECTRAL", name, spec[name])
    del a
    gc.collect()

# ---- 5. master ----------------------------------------------------------
target = target_for_style(STYLE)
log("LUFS target for", STYLE, "=", target)
rep = {}
raw_of = {"full_mix": "full_mix.wav", "fuzz_ge": "fuzz_ge_raw.wav",
          "fuzz_hard": "fuzz_hard_raw.wav"}
for name in ("fuzz_ge", "fuzz_hard", "full_mix"):
    a, sr2 = read_wav(os.path.join(AUD, raw_of[name]))
    log("mastering", name, "...")
    mastered, rp = master(a.astype(np.float32), target_lufs=target,
                          ceiling_db=-1.0, sample_rate=sr2)
    write_wav(os.path.join(AUD, name + ".wav"), mastered, sr2, normalize=False)
    rep[name] = {"target_lufs": target,
                 "integrated_lufs": round(rp["integrated_lufs"], 2),
                 "true_peak_db": round(rp["true_peak_db"], 2)}
    log("MASTER", name, "lufs", round(rp["integrated_lufs"], 2),
        "tp", round(rp["true_peak_db"], 2))
    del a, mastered
    gc.collect()

# ---- 6. silence profile -------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for v in rms if v < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}


prof = {}
for name in ("full_mix", "fuzz_ge", "fuzz_hard"):
    a, _ = read_wav(os.path.join(AUD, name + ".wav"))
    prof[name] = silence_profile(a)
    log("SILENCE", name, prof[name]["silence_ratio"],
        "low_rms_sec", prof[name]["low_rms_seconds"], "/", prof[name]["n_seconds"])
    del a
    gc.collect()

# ---- 7. Opus OGG --------------------------------------------------------
for name in ("full_mix", "fuzz_ge", "fuzz_hard"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "128k", ogg], capture_output=True, text=True)
    log(name, "ogg", os.path.getsize(ogg), "B")

# ---- 8. sidecars --------------------------------------------------------
with open(os.path.join(ANA, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)
with open(os.path.join(ANA, "spectral.json"), "w") as f:
    json.dump(spec, f, indent=2)

prov = {
    "method": "SP-069", "module": "sound.effects.topology_distortion",
    "style": STYLE, "bpm": BPM, "soundfont": SF,
    "engine": "FuzzBillion (11-switch discrete distortion topology bank)",
    "distinct_circuits": total_circuits,
    "circuits": {
        "fuzz_ge": {"code": list(code_ge), "name": name_ge,
                    "gain": 2.0, "io_mode": "inst", "profile": prof_ge},
        "fuzz_hard": {"code": list(code_hard), "name": name_hard,
                      "gain": 3.0, "io_mode": "line", "profile": prof_hard},
    },
    "treatments": {
        "fuzz_ge": "germanium-soft 11-stage chain, instrument level (main)",
        "fuzz_hard": "transformer+CMOS+opamp hard-clip chain, line level (alt)",
        "full_mix": "dry FluidSynth reference (no distortion)",
    },
    "master": rep, "dur_s": round(dur, 2), "pitch": spec,
}
with open(os.path.join(AUD, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)

log("DONE. outputs in", AUD)
log(json.dumps(rep, indent=2))
