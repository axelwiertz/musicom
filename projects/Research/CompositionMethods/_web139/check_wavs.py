#!/usr/bin/env python3
"""Sanity-check the demo WAV spectra (oboe ~295 Hz rich, chanter ~466 Hz)."""
import wave, numpy as np

for path, label in (('sp139_demo_oboe.wav', 'oboe'), ('sp139_demo_chanter.wav', 'chanter')):
    w = wave.open(path, 'rb')
    n = w.getnframes(); fs = w.getframerate()
    x = np.frombuffer(w.readframes(n), dtype='<i2').astype(float)/32767.0
    seg = x[int(0.3*fs):int(1.1*fs)]
    X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1/fs)
    m = (fr > 40) & (fr < 4000)
    pk = fr[m][np.argmax(X[m])]
    hs = []
    for k in range(1, 7):
        mm = (fr > pk*k*0.98) & (fr < pk*k*1.02)
        hs.append(20*np.log10(float(X[mm].max())/float(X[m].max())) if mm.any() else -120)
    print(f"{label}: fs={fs} n={n} dur={n/fs:.2f}s peak={pk:.1f} Hz | hdB={[f'{d:.1f}' for d in hs]}")
