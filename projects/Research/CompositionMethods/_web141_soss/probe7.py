#!/usr/bin/env python3
"""Probe spectrum near Nyquist for naive vs polyBLEP saw at f0=1000."""
import numpy as np
import importlib.util, sys

spec = importlib.util.spec_from_file_location('v', 'verify_sp141.py')
# don't run the whole script; import module-level defs via exec of the head
src = open('verify_sp141.py').read()
head = src[:src.index('# --------------------------------------------------------------------- #\n# Checks')]
ns = {}
exec(head, ns)
render_soss = ns['render_soss']
FS = ns['FS']

f_al = 1000.0
na = render_soss(f_al, 1.0, n_osc=1, spread_cents=0.0, fb=0.0, seed=1, polyblep_on=False)
pb = render_soss(f_al, 1.0, n_osc=1, spread_cents=0.0, fb=0.0, seed=1, polyblep_on=True)
for name, x in [('naive', na), ('polyblep', pb)]:
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / FS)
    fund = X[np.argmin(np.abs(f - 1000.0))]
    print(f"== {name}: fund={fund:.3e}")
    for fr in [19000, 20000, 21000, 21100, 21150, 21500, 22000, 22050-10]:
        m = X[np.argmin(np.abs(f - fr))] / fund
        print(f"   {fr:>7.0f} Hz : {20*np.log10(m):7.1f} dB")
