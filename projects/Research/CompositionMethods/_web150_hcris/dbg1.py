import numpy as np
from verify_hcris import TwoPole, jet_drive, phase_condition_f, measure_freq, FS
from scipy.signal import freqz

f0, Q = 440.0, 22.07
sig = jet_drive(f0, Q, 800.0, FS, 0.30, seed=3)
print("sig stats", np.nanmin(sig), np.nanmax(sig), np.isnan(sig).sum(), len(sig))
print("rms head/tail", np.std(sig[:1000]), np.std(sig[-1000:]))

res = TwoPole(f0, Q, FS)
b, a = res.coeffs()
print("b,a", b, a, "r", res.r)
f = np.linspace(0.3 * f0, f0 * 0.999, 5)
w, h = freqz(b, a, worN=f, fs=FS)
print("phase at few f", np.angle(h), w)
tau = 0.004 / (0.4 * 0.6 * np.sqrt(2 * 800 / 1.204))
print("tau", tau, "2pif tau at f0", 2 * np.pi * f0 * tau)
print("pred", phase_condition_f(f0, Q, tau, FS))
print("meas", measure_freq(sig[2400:], FS))
