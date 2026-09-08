#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compare pitch metrics: base FluidSynth vs shimmer mix."""
import sys, numpy as np, wave

def read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes(); ch = w.getnchannels()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        a = (a[0::2] + a[1::2]) * 0.5
    return a

def metrics(x, sr=44100, hop=0.5):
    n_win = int(sr * hop)
    frames = []
    fft_freqs = np.fft.rfftfreq(n_win, 1.0 / sr)
    for lo in range(0, len(x) - n_win, n_win):
        seg = x[lo:lo + n_win] * np.hanning(n_win)
        spec = np.abs(np.fft.rfft(seg))
        m = (fft_freqs >= 50) & (fft_freqs <= 1000)
        if not np.any(m):
            continue
        dom = fft_freqs[m][np.argmax(spec[m])]
        frames.append(float(dom))
    frames = np.array(frames)
    f0 = float(np.median(frames)) if len(frames) else 0.0
    n_fft = 1 << 14
    seg = x[:n_fft] * np.hanning(n_fft)
    spec = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(n_fft, 1.0 / sr)
    tot = float(np.sum(spec[(fr >= 50) & (fr <= 1000)] ** 2))
    he = 0.0
    for k in range(1, 9):
        fc = f0 * k
        mm = (fr >= fc - 15) & (fr <= fc + 15)
        if np.any(mm):
            he += float(np.sum(spec[mm] ** 2))
    he_ratio = he / tot if tot > 1e-12 else 0.0
    silent = float(np.sum(np.abs(x) < 0.001) / len(x))
    rms = [float(np.sqrt(np.mean(x[s * sr:(s + 1) * sr] ** 2)))
           for s in range(int(len(x) / sr) + 1) if len(x[s * sr:(s + 1) * sr])]
    return dict(f0=f0, he=he_ratio, n_frames=len(frames), nz=int(np.sum(frames > 0)),
                silent=silent, peak=float(np.max(np.abs(x))), dur=len(x) / sr,
                rms_min=min(rms), rms_max=max(rms))

OUT = "/opt/data/projects/Styles/Production/SP035-shimmer-tango-dramatic"
for name in ["base_fluidsynth.wav", "SP035-shimmer-tango-dramatic_full_mix.wav"]:
    m = metrics(read_wav(OUT + "/" + name))
    print(name)
    for k, v in m.items():
        if k != "rms":
            print(f"   {k}: {v}")
