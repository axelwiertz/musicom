# -*- coding: utf-8 -*-
"""Silence + duration check for 075-disco-pcfg renders."""
import wave
import numpy as np

for f in ("Audio/075-disco-pcfg.wav", "Audio/075-disco-pcfg-phase1.wav"):
    w = wave.open(f, "rb")
    n = w.getnframes()
    sr = w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    mono = a.reshape(-1, 2).mean(axis=1) if w.getnchannels() == 2 else a
    silent = np.sum(np.abs(mono) < 0.001) / len(mono)
    dur = n / sr
    rms = np.sqrt((mono ** 2).mean())
    print("%s: dur=%.1fs silent=%.1f%% rms=%.4f peak=%.3f" % (
        f, dur, silent * 100.0, rms, np.abs(mono).max()))
    # per-second RMS map (tail padding legit, mid-track gaps suspect)
    sec = int(dur)
    rms_map = []
    for i in range(sec):
        seg = mono[i * sr:(i + 1) * sr]
        rms_map.append(float(np.sqrt((seg ** 2).mean())))
    quiet = [i for i, r in enumerate(rms_map) if r < 0.005]
    print("  quiet seconds:", quiet if quiet else "none")
