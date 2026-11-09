# -*- coding: utf-8 -*-
"""SP-113 Supervariable VCF applied to the reworked pop-ballad HITL candidate.

Absolute-layer method: render the whole mix via FluidSynth (dry), apply the
Supervariable VCF as a single production layer (continuously-morphing filter
character across the piece + a 4-pole LP variant), master both to the genre
target.
"""
import os
import gc
import subprocess
import json
import numpy as np

from sound.effects.supervariable_filter import SuperVariableFilter
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")
MID = os.path.join(HERE, "MIDI")
ANA = os.path.join(HERE, "Analysis")
for d in (AUD, MID, ANA):
    os.makedirs(d, exist_ok=True)

SRC_MIDI = os.path.join(MID, "pop-ballad-hitl-cand3-reworked.mid")
SF = discover_soundfont()
FLUID = fluidsynth_bin()
BPM = 72.0
STYLE = "pop"
# one full piece-length profile arc: ~72 s period -> 93 s piece ~ 1.3 cycles
PERIOD_S = 72.0


def log(*a):
    print(*a, flush=True)


# ---- 1. render full mix (dry reference) --------------------------------
mix_path = os.path.join(AUD, "full_mix.wav")
r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                    "-F", mix_path, SF, SRC_MIDI],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)
N = len(audio)
dur = N / sr
log("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))

# ---- 2. SP-113 supervariable VCF ---------------------------------------
vcf = SuperVariableFilter(sample_rate=sr)

# 2a. profile sweep: slow voltage-controlled character morph HP->notch->LP
t = np.arange(N) / sr
sweep = np.cos(2.0 * np.pi * t / PERIOD_S)   # +1 -> -1 -> +1 over 72 s
log("SVCF profile-sweep processing ...")
L = audio[:, 0].astype(np.float64)
R = audio[:, 1].astype(np.float64)
yL = vcf.process(L, cutoff=1200.0, res=0.35, profile=0.0, bandwidth=0.2,
                 order=2, mode="classic", profile_mod=sweep * 0.85)
yR = vcf.process(R, cutoff=1200.0, res=0.35, profile=0.0, bandwidth=0.2,
                 order=2, mode="classic", profile_mod=sweep * 0.85)
del L, R
gc.collect()
sweep_wet = np.stack([yL, yR], axis=1).astype(np.float32)
write_wav(os.path.join(AUD, "svcf_sweep_raw.wav"), sweep_wet, sr, normalize=True)
del yL, yR
gc.collect()
log("svcf_sweep done", sweep_wet.shape)

# 2b. lp24 variant: 4-pole LP, fixed (dark warmth)
log("SVCF lp24 processing ...")
L = audio[:, 0].astype(np.float64)
R = audio[:, 1].astype(np.float64)
yL = vcf.process(L, cutoff=2600.0, res=0.2, profile=1.0, order=4, mode="lp24")
yR = vcf.process(R, cutoff=2600.0, res=0.2, profile=1.0, order=4, mode="lp24")
del L, R
gc.collect()
lp24_wet = np.stack([yL, yR], axis=1).astype(np.float32)
write_wav(os.path.join(AUD, "svcf_lp24_raw.wav"), lp24_wet, sr, normalize=True)
del yL, yR
gc.collect()
log("svcf_lp24 done", lp24_wet.shape)
del audio
gc.collect()

# ---- 3. pitch / spectral sanity ----------------------------------------
def spectral_report(name, sig):
    mono = sig.mean(axis=1) if sig.ndim == 2 else sig
    # harmonic energy in first 8 harmonics of lowest strong fundamental
    mag = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sr)
    band = (freqs >= 50) & (freqs <= 1000)
    # dominant peak in 50-1000 Hz
    bb = mag[band]
    ff = freqs[band]
    dom = float(ff[int(np.argmax(bb))])
    total = float(np.sum(mag ** 2))
    harmonic = float(np.sum(mag[band] ** 2) / max(total, 1e-9))
    return {"dominant_hz": round(dom, 1), "band_energy_frac": round(harmonic, 4)}

spec = {}
for name in ("full_mix", "svcf_sweep", "svcf_lp24"):
    a, _ = read_wav(os.path.join(AUD, name + "_raw.wav" if name != "full_mix" else "full_mix.wav"))
    spec[name] = spectral_report(name, a)
    log("SPECTRAL", name, spec[name])
    del a
    gc.collect()

# ---- 4. master (both SVCF variants + reference) ------------------------
target = target_for_style(STYLE)
rep = {}
# map variant -> source raw file
raw_of = {"full_mix": "full_mix.wav",
          "svcf_sweep": "svcf_sweep_raw.wav",
          "svcf_lp24": "svcf_lp24_raw.wav"}
for name in ("svcf_sweep", "svcf_lp24", "full_mix"):
    a, sr2 = read_wav(os.path.join(AUD, raw_of[name]))
    log("mastering", name, "...")
    mastered, rp = master(a.astype(np.float32), target_lufs=target,
                          ceiling_db=-1.0, sample_rate=sr2)
    write_wav(os.path.join(AUD, name + ".wav"), mastered, sr2, normalize=False)
    rep[name] = {"target_lufs": target,
                 "integrated_lufs": round(rp["integrated_lufs"], 2),
                 "true_peak_db": round(rp["true_peak_db"], 2)}
    log("MASTER", name, "target", target,
        "lufs", round(rp["integrated_lufs"], 2),
        "tp", round(rp["true_peak_db"], 2))
    del a, mastered
    gc.collect()

# ---- 5. silence profile ------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for v in rms if v < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}

prof = {}
for name in ("full_mix", "svcf_sweep", "svcf_lp24"):
    a, _ = read_wav(os.path.join(AUD, name + ".wav"))
    prof[name] = silence_profile(a)
    log("SILENCE", name, prof[name]["silence_ratio"],
        "low_rms_sec", prof[name]["low_rms_seconds"], "/", prof[name]["n_seconds"])
    del a
    gc.collect()

# ---- 6. Opus OGG -------------------------------------------------------
for name in ("full_mix", "svcf_sweep", "svcf_lp24"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "128k", ogg], capture_output=True, text=True)
    log(name, "ogg", os.path.getsize(ogg), "B")

# ---- 7. sidecars -------------------------------------------------------
with open(os.path.join(ANA, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)
with open(os.path.join(ANA, "spectral.json"), "w") as f:
    json.dump(spec, f, indent=2)
prov = {
    "method": "SP-113", "module": "sound.effects.supervariable_filter",
    "style": STYLE, "bpm": BPM,
    "filter": {
        "profile": "voltage-controlled morph HP->notch->LP (classic arc)",
        "cutoff_hz": 1200.0, "res": 0.35, "bandwidth": 0.2, "order": 2,
        "profile_mod": f"cos(2pi t/{PERIOD_S}s) * 0.85",
        "lp24_variant": {"cutoff_hz": 2600.0, "res": 0.2, "order": 4},
    },
    "soundfont": SF, "master": rep, "dur_s": round(dur, 2),
    "pitch": spec,
}
with open(os.path.join(AUD, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)

log("DONE. outputs in", AUD)
log(json.dumps(rep, indent=2))