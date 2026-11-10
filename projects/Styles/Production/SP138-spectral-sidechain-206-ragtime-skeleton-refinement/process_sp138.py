# -*- coding: utf-8 -*-
"""SP-138 Spectral Sidechain applied to 206-ragtime-skeleton-refinement.

Absolute-layer method (Art DSP Canvas 2.0-style): render the solo-piano rag
(3 voices: Melody ch0 / Bass ch1 / Comp ch2, all GM program 1) as separate
stems, then separate the competing registers spectrally — duck each voice's
bands where a competing voice is loud — re-sum to the treated mix.

Treatments (all levels whole-piece = absolute layer):
  - full_mix          dry FluidSynth reference (no sidechain)
  - canvas2mix        Canvas2Mix separation across the 3 stems (main)
  - bass_duck         classic pump: stride bass sidechains melody+comp (alt)
"""
import os
import gc
import subprocess
import json
import numpy as np

from sound.effects.spectral_sidechain import SpectralSidechain, Canvas2Mix, BlobMap
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

SRC_MIDI = ("/opt/data/repos/musicom/projects/Styles/Ragtime/"
            "206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid")
SF = discover_soundfont()
FLUID = fluidsynth_bin()
BPM = 120.0
STYLE = "ragtime"          # -> target_for_style fallback -14.0 LUFS

SC_KWARGS = dict(fft_size=2048, n_bands=12, f_lo=40.0, f_hi=16000.0,
                 threshold_db=-35.0, ratio=8.0, knee_db=6.0,
                 attack_ms=5.0, release_ms=120.0, mix=1.0)


def log(*a):
    print(*a, flush=True)


# ---- 1. full mix (dry reference) --------------------------------------
mix_path = os.path.join(AUD, "full_mix.wav")
r = subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", mix_path, SF, SRC_MIDI],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr[-500:]
audio, sr = read_wav(mix_path)
N = len(audio)
dur = N / sr
log("full_mix:", audio.shape, "sr", sr, "dur_s", round(dur, 2))

# ---- 2. stems ----------------------------------------------------------
pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=sr)
stems = pipe.render_stems(SRC_MIDI, STEM, format="wav")
stem_keys = sorted(stems.keys())
log("stems:", stem_keys)
assert len(stem_keys) == 3, f"expected 3 stems, got {len(stem_keys)}"
# track order == mid.tracks[1..3] order == Melody, Bass, Comp (audit-confirmed)
MEL, BAS, CMP = [os.path.join(STEM, stems[k]) for k in stem_keys]

smel, _ = read_wav(MEL)
sbass, _ = read_wav(BAS)
scmp, _ = read_wav(CMP)
# downmix each stem to mono for spectral separation
mono = lambda a: a.mean(axis=1) if a.ndim == 2 else a
m_mel, m_bas, m_cmp = mono(smel), mono(sbass), mono(scmp)
# pad all to the full-mix length (equal tick length guarantees close; pad tail)
Lmax = N
for name, arr in (("mel", m_mel), ("bas", m_bas), ("cmp", m_cmp)):
    pass
m_mel = np.pad(m_mel, (0, max(0, Lmax - len(m_mel))))[:Lmax]
m_bas = np.pad(m_bas, (0, max(0, Lmax - len(m_bas))))[:Lmax]
m_cmp = np.pad(m_cmp, (0, max(0, Lmax - len(m_cmp))))[:Lmax]
log("stem mono lens:", m_mel.shape, m_bas.shape, m_cmp.shape)

# ---- 3a. Canvas2Mix (main SP-138 treatment) ----------------------------
cm = Canvas2Mix(sr=sr, **SC_KWARGS)
sep = cm.process([m_mel, m_bas, m_cmp])   # each ducked by loudest other
cmix = sep[0] + sep[1] + sep[2]
cmix_stereo = np.stack([cmix, cmix], axis=1).astype(np.float32)
write_wav(os.path.join(AUD, "canvas2mix_raw.wav"), cmix_stereo, sr, normalize=True)
del sep
gc.collect()
log("canvas2mix done")

# blob map (Canvas descriptor) of the treated vs dry mix for the report
blob = BlobMap(sr=sr)
blobs_dry = blob.analyze(np.ascontiguousarray(smel.T))
blobs_treated = blob.analyze(np.ascontiguousarray(cmix_stereo.T))


def blob_avg(bl):
    return tuple(round(float(np.mean([b[i] for b in bl])), 3) for i in range(3))


log("blob dry (pan,height,depth avg):", blob_avg(blobs_dry))
log("blob treated:", blob_avg(blobs_treated))

# ---- 3b. bass_duck variant (classic pump) ------------------------------
sc = SpectralSidechain(sr=sr, **SC_KWARGS)
duck_target = m_mel + m_cmp          # melody + comp = "main"
duck_out = sc.process(duck_target, m_bas)   # stride bass = sidechain
bduck_stereo = np.stack([duck_out, duck_out], axis=1).astype(np.float32)
write_wav(os.path.join(AUD, "bass_duck_raw.wav"), bduck_stereo, sr, normalize=True)
del duck_target, duck_out, m_bas, m_cmp, smel, sbass, scmp, cmix
gc.collect()
log("bass_duck done")

# ---- 4. spectral / pitch sanity ----------------------------------------
def spectral_report(name, sig):
    mono = sig.mean(axis=1) if sig.ndim == 2 else sig
    mag = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sr)
    band = (freqs >= 50) & (freqs <= 1000)
    bb = mag[band]
    ff = freqs[band]
    dom = float(ff[int(np.argmax(bb))])
    total = float(np.sum(mag ** 2))
    harmonic = float(np.sum(mag[band] ** 2) / max(total, 1e-9))
    # low-band energy retention (sidechain ducks lows first)
    low = (freqs >= 40) & (freqs < 300)
    low_frac = float(np.sum(mag[low] ** 2) / max(total, 1e-9))
    return {"dominant_hz": round(dom, 1), "band_energy_frac": round(harmonic, 4),
            "low_energy_frac": round(low_frac, 4)}


spec = {}
for name in ("full_mix", "canvas2mix", "bass_duck"):
    src = os.path.join(AUD, name + ".wav" if name == "full_mix" else name + "_raw.wav")
    a, _ = read_wav(src)
    spec[name] = spectral_report(name, a)
    log("SPECTRAL", name, spec[name])
    del a
    gc.collect()

# ---- 5. master ---------------------------------------------------------
target = target_for_style(STYLE)
log("LUFS target for", STYLE, "=", target)
rep = {}
raw_of = {"full_mix": "full_mix.wav",
          "canvas2mix": "canvas2mix_raw.wav",
          "bass_duck": "bass_duck_raw.wav"}
for name in ("canvas2mix", "bass_duck", "full_mix"):
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

# ---- 6. silence profile ------------------------------------------------
def silence_profile(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [round(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))), 4)
           for s in range(0, len(mono) - sr, sr)]
    gaps = sum(1 for v in rms if v < 0.005)
    return {"silence_ratio": round(silent, 4), "low_rms_seconds": gaps,
            "n_seconds": len(rms), "per_second_rms": rms}


prof = {}
for name in ("full_mix", "canvas2mix", "bass_duck"):
    a, _ = read_wav(os.path.join(AUD, name + ".wav"))
    prof[name] = silence_profile(a)
    log("SILENCE", name, prof[name]["silence_ratio"],
        "low_rms_sec", prof[name]["low_rms_seconds"], "/", prof[name]["n_seconds"])
    del a
    gc.collect()

# ---- 7. Opus OGG -------------------------------------------------------
for name in ("full_mix", "canvas2mix", "bass_duck"):
    wav = os.path.join(AUD, name + ".wav")
    ogg = os.path.join(AUD, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "128k", ogg], capture_output=True, text=True)
    log(name, "ogg", os.path.getsize(ogg), "B")

# ---- 8. sidecars -------------------------------------------------------
with open(os.path.join(ANA, "silence_profile.json"), "w") as f:
    json.dump(prof, f, indent=2)
with open(os.path.join(ANA, "spectral.json"), "w") as f:
    json.dump(spec, f, indent=2)
prov = {
    "method": "SP-138", "module": "sound.effects.spectral_sidechain",
    "style": STYLE, "bpm": BPM, "soundfont": SF,
    "stem_order": {"track00": "Melody (ch0)", "track01": "Bass (ch1)",
                   "track02": "Comp (ch2)"},
    "sidechain_params": SC_KWARGS,
    "treatments": {
        "canvas2mix": "Canvas2Mix separation across 3 stems (each ducked by loudest competing track)",
        "bass_duck": "stride bass sidechains melody+comp (classic spectral pump)",
    },
    "blob_map": {"dry_avg": blob_avg(blobs_dry),
                 "treated_avg": blob_avg(blobs_treated)},
    "master": rep, "dur_s": round(dur, 2), "pitch": spec,
}
with open(os.path.join(AUD, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)

log("DONE. outputs in", AUD)
log(json.dumps(rep, indent=2))