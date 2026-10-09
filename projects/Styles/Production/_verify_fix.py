#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify glitch_chopper fix: demo + silence sanity on a synthetic bar."""
import numpy as np
from sound.effects.glitch_chopper import demo, GlitchChopper

print(demo())

# silence sanity: quant=8 on a busy synthetic signal must NOT be ~half-zero
sr = 44100
rng = np.random.default_rng(5)
t = np.arange(sr * 4) / sr
# two bars of dense-ish content: 120 bpm kick + noise bed
sig = np.zeros(sr * 4)
for k in range(16):
    idx = int(k * 0.25 * sr)
    seg_t = np.arange(int(0.1 * sr)) / sr
    e = min(idx + len(seg_t), len(sig))
    sig[idx:e] += np.sin(2 * np.pi * (70 - 30 * seg_t[:e - idx] * 8) * seg_t[:e - idx]) * np.exp(-seg_t[:e - idx] * 20)
sig += rng.standard_normal(len(sig)) * 0.03
st = np.stack([sig, np.roll(sig, 500)], axis=1)

gc = GlitchChopper(sample_rate=sr, bpm=120, seed=3)
out = gc.process(st, glitch_p=0.3, reverse_p=0.25, quant=8)
mono = out[:, 0]
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100
peak = float(np.abs(mono).max())
print(f"quant=8 glitched: peak={peak:.3f} silence={sil:.2f}% finite={np.all(np.isfinite(out))}")
assert sil < 40.0, f"silence too high: {sil:.2f}%"
print("silence sanity OK")
