#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Direct engine-level pitch test + artifact chroma comparison."""
import json
import wave
from pathlib import Path

import numpy as np

from sound.synthesis.karplus_strong import karplus_strong, midi_to_freq

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP011-karplus-hiphop-boombap")


def acf_f0(seg, sr, lo_hz=50.0, hi_hz=1500.0):
    s = seg - seg.mean()
    ac = np.correlate(s, s, "full")[len(s) - 1:]
    ac = ac / ac[0] if ac[0] > 0 else ac
    lo, hi = int(sr / hi_hz), min(int(sr / lo_hz), len(ac) - 1)
    lag = lo + int(np.argmax(ac[lo:hi]))
    return sr / lag, float(ac[lo:hi].max())


print("=== ENGINE TEST: karplus_strong single notes ===")
eng = []
for midi in (36, 40, 45, 52, 60, 72, 84):
    for lg, dur in ((0.9995, 1.4), (0.9986, 1.0), (0.9840, 0.25)):
        sig = karplus_strong(midi, dur, vel=100, loop_gain=lg, sr=SR)
        f0, conf = acf_f0(sig[int(0.05 * SR):int(0.35 * SR)], SR)
        exp = midi_to_freq(midi)
        seg = sig[int(0.05 * SR):int(0.35 * SR)]
        w = seg * np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(w))
        ff = np.fft.rfftfreq(len(w), 1 / SR)
        bm = (ff >= 50) & (ff <= 2000)
        hs = sum(float(np.sum(spec[(ff >= exp * h * 0.97) & (ff <= exp * h * 1.03)])) for h in range(1, 9))
        share = 100 * hs / max(float(np.sum(spec[bm])), 1e-12)
        ratio = f0 / exp
        eng.append({"midi": midi, "loop_gain": lg, "exp": round(exp, 1),
                    "acf_f0": round(f0, 1), "ratio": round(ratio, 3), "conf": round(conf, 3),
                    "harm_share_pct": round(share, 1)})
        print(f"midi {midi:3d} lg={lg} exp={exp:7.1f} acf={f0:7.1f} ratio={ratio:.3f} "
              f"conf={conf:.2f} harm%={share:5.1f}")

# ---- artifact chroma vs FluidSynth GM reference chroma ----
def read_mono(p):
    with wave.open(str(p), "rb") as wf:
        sr, nch = wf.getframerate(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return raw.reshape(-1, nch).mean(axis=1), sr


def chroma(mono, sr, fmin=55.0, fmax=2000.0):
    win, hop = int(0.4 * sr), int(0.2 * sr)
    acc = np.zeros(12)
    for w0 in range(0, max(1, len(mono) - win), hop):
        seg = mono[w0:w0 + win] * np.hanning(win)
        spec = np.abs(np.fft.rfft(seg))
        ff = np.fft.rfftfreq(win, 1 / sr)
        m = (ff >= fmin) & (ff <= fmax)
        f, s = ff[m], spec[m]
        if s.sum() <= 0:
            continue
        # map each bin to nearest pitch class (log-frequency fold)
        pc = np.round(12 * np.log2(f / 440.0)).astype(int) % 12
        for k in range(12):
            acc[k] += float(np.sum(s[pc == k]))
    return acc


ks, sr1 = read_mono(OUT / "Audio/SP011-karplus-hiphop-boombap.wav")
refp = OUT / "Analysis/ref_fluidsynth_gm.wav"
result = {"engine": eng}
SRC = Path("/opt/data/repos/musicom/projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid")
if not refp.exists():
    import subprocess

    from utilities.env import fluidsynth_bin, soundfont_path
    subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(refp),
                    soundfont_path(), str(SRC)], check=True, capture_output=True)
if refp.exists():
    gm, sr2 = read_mono(refp)
    ck, cg = chroma(ks, sr1), chroma(gm, sr2)
    ckn, cgn = ck / ck.sum(), cg / cg.sum()
    cos = float(np.dot(ckn, cgn) / (np.linalg.norm(ckn) * np.linalg.norm(cgn)))
    # best rotation (key) match
    rots = [float(np.dot(np.roll(ckn, r), cgn) / (np.linalg.norm(ckn) * np.linalg.norm(cgn))) for r in range(12)]
    result["chroma"] = {"ks_profile": [round(float(x), 4) for x in ckn],
                        "gm_profile": [round(float(x), 4) for x in cgn],
                        "cosine_similarity": round(cos, 4),
                        "best_rotation_semitones": int(np.argmax(rots)),
                        "best_rotation_cosine": round(max(rots), 4)}
    print("\nchroma KS :", np.round(ckn, 3).tolist())
    print("chroma GM :", np.round(cgn, 3).tolist())
    print("cosine:", round(cos, 4), "best rot:", int(np.argmax(rots)), round(max(rots), 4))
else:
    print("\n(no GM reference present)")

(OUT / "Analysis/pitch_verification.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result["chroma"] if "chroma" in result else {}, indent=1))
