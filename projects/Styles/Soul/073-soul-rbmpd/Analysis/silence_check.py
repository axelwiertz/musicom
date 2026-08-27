#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silence / level sanity check for rendered WAVs."""
import sys
import wave

import numpy as np

def analyze(path):
    with wave.open(path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        raw = wf.readframes(n)
    mono = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    # de-interleave if stereo
    if wf.getnchannels() == 2:
        mono = mono[0::2]
    silent = float(np.sum(np.abs(mono) < 0.001)) / len(mono)
    peak = float(np.max(np.abs(mono)))
    dur = len(mono) / sr
    # per-second RMS map (first 20 sec)
    rms_per_sec = []
    sec = sr
    for i in range(0, min(len(mono), 20 * sec), sec):
        chunk = mono[i:i + sec]
        rms = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) else 0.0
        rms_per_sec.append(round(rms, 4))
    print("%s: dur=%.1fs peak=%.3f silent=%.1f%% rms/s=%s" % (
        path, dur, peak, silent * 100.0, rms_per_sec))
    return silent, peak

ok = True
for p in sys.argv[1:]:
    s, pk = analyze(p)
    if s > 0.30:
        print("  !! SUSPECT: >30%% silence", p)
        ok = False
    if pk < 0.05:
        print("  !! SUSPECT: very low peak", p)
        ok = False
print("SILENCE_CHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
