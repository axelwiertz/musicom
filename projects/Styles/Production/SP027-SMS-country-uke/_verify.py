# -*- coding: utf-8 -*-
"""Verify outputs: durations, non-empty, RMS sanity."""
import os
import numpy as np
from scipy.io import wavfile

OUT_DIR = '/opt/data/projects/Styles/Production/SP027-SMS-country-uke'
for name in ('country_uke_base.wav', 'country_uke_SP027_SMS.wav',
             'country_uke_SP027_deterministic.wav', 'country_uke_SP027_stochastic.wav'):
    p = os.path.join(OUT_DIR, name)
    sr, a = wavfile.read(p)
    if a.ndim > 1:
        a = a.mean(axis=1)
    a = a.astype(float)
    rms = np.sqrt(np.mean(a**2))
    dur = len(a) / sr
    print(f'{name}: sz={os.path.getsize(p)} sr={sr} dur={dur:.2f}s rms={rms:.4f}')

ogg = os.path.join(OUT_DIR, 'country_uke_SP027_SMS.ogg')
print('OGG:', ogg, 'size=', os.path.getsize(ogg))
