# -*- coding: utf-8 -*-
"""Deep resonance analysis: did SP-119 actually suppress narrowband resonances?

Compares full_mix.wav (raw reference) vs sp119_suppressed_raw.wav (SP-119, pre-master).
Measures: (a) waveform delta, (b) narrowband excess-over-median reduction in
the midrange (the quantity SP-119 targets), (c) per-band crest reduction.
"""
import os
import numpy as np
from sound.utils.io import read_wav

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "Audio")


def excess_dB_sum(x, lo=200.0, hi=6000.0, width=7, thr_db=0.0):
    """Sum of positive (mag_db - median_baseline - thr) in the midrange."""
    mono = x.mean(axis=1) if x.ndim == 2 else x
    sr = 44100
    n = len(mono)
    fft = 4096
    hops = list(range(0, n - fft + 1, fft // 2))
    ex_total = 0.0
    for s in hops:
        seg = mono[s:s + fft] * np.hanning(fft)
        Y = np.abs(np.fft.rfft(seg))
        fr = np.fft.rfftfreq(fft, 1 / sr)
        m = (fr >= lo) & (fr <= hi)
        mag = Y[m]
        if mag.size == 0:
            continue
        with np.errstate(divide="ignore"):
            db = 20.0 * np.log10(mag + 1e-12)
        half = width // 2
        base = np.array([np.median(db[max(0, i - half):i + half + 1])
                         for i in range(len(db))])
        ex = db - base - thr_db
        ex_total += float(np.sum(ex[ex > 0]))
    return ex_total


before = read_wav(os.path.join(AUD, "full_mix.wav"))[0]
after = read_wav(os.path.join(AUD, "sp119_suppressed_raw.wav"))[0]

diff = np.abs(after.astype(np.float64) - before.astype(np.float64))
print("waveform max_abs_diff:", float(diff.max()))
print("waveform mean_abs_diff:", float(diff.mean()))
print("waveform rms_diff:", float(np.sqrt(np.mean(diff ** 2))))

ex_before = excess_dB_sum(before)
ex_after = excess_dB_sum(after)
print("midrange_excess_dB_before:", round(ex_before, 1))
print("midrange_excess_dB_after:", round(ex_after, 1))
print("midrange_excess_reduction_pct:", round(100 * (ex_before - ex_after) / (ex_before + 1e-9), 2))
