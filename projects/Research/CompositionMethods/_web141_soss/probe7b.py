#!/usr/bin/env python3
"""Per-image alias suppression distribution: naive vs polyBLEP at f0=331."""
import numpy as np
import importlib.util

src = open('verify_sp141.py').read()
head = src[:src.index('# --------------------------------------------------------------------- #\n# Checks')]
ns = {}
exec(head, ns)
render_soss = ns['render_soss']
FS = ns['FS']

def floor_imgs(polyblep_on):
    f_al = 331.0
    y = render_soss(f_al, 2.0, n_osc=1, spread_cents=0.0, fb=0.0, seed=1,
                    polyblep_on=polyblep_on)
    X = np.abs(np.fft.rfft(y * np.hanning(len(y))))
    f = np.fft.rfftfreq(len(y), 1.0 / FS)
    Xf = dict(zip(f, X))
    inband = {k * f_al for k in range(1, 67)}
    out = []
    for k in range(67, 300):
        fk = k * f_al
        im = abs(44100.0 * round(fk / 44100.0) - fk)
        if 1000.0 <= im <= 20000.0 and not any(abs(im - h) < 5.0 for h in inband):
            b = min(f, key=lambda q: abs(q - im))
            out.append((im, Xf[b]))
    return out

a = dict(floor_imgs(False))
b = dict(floor_imgs(True))
imgs = sorted(a.keys())
diffs = [20 * np.log10(a[i] / b[i]) for i in imgs]
print("n images:", len(imgs))
print("suppression dB: min %.1f  median %.1f  mean %.1f  max %.1f"
      % (min(diffs), np.median(diffs), np.mean(diffs), max(diffs)))
print("worst 8 (image Hz: dB):")
for i in sorted(imgs, key=lambda q: 20*np.log10(a[q]/b[q]))[:8]:
    print(f"   {i:>7.0f}: {20*np.log10(a[i]/b[i]):6.1f} dB")
print("best 8:")
for i in sorted(imgs, key=lambda q: 20*np.log10(a[q]/b[q]))[-8:]:
    print(f"   {i:>7.0f}: {20*np.log10(a[i]/b[i]):6.1f} dB")
