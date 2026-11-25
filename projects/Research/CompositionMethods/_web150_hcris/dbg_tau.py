import numpy as np
from scipy.signal import lfilter, hilbert
import sys
sys.argv = ['x']
import importlib.util
spec = importlib.util.spec_from_file_location("vh", "verify_hcris.py")
# avoid running: read the class by exec of only the class? simpler: re-declare
FS = 48000
f0, Q = 440.0, 22.07
w0 = 2 * np.pi * f0 / FS
alpha = np.sin(w0) / (2 * Q)
a0 = 1 + alpha
b = [alpha / a0, 0.0, -alpha / a0]
a = [1.0, -2 * np.cos(w0) / a0, (1 - alpha) / a0]
imp = np.zeros(FS)
imp[0] = 1.0
ir = lfilter(b, a, imp)
print("poles", np.roots(a), "tau th", Q / (np.pi * f0) * 1e3, "ms")
env = np.abs(hilbert(ir))
n = 240
nb = len(env) // n
rms = np.sqrt((env[:nb * n].reshape(nb, n) ** 2).mean(axis=1))
print("rms head", rms[:8])
print("ratio consecutive", (rms[1:6] / rms[:5]))
for start, end in [(2, 200), (5, 100), (10, 90), (2, 60)]:
    seg = rms[start:end]
    t = np.arange(len(seg)) * n / FS
    s = np.polyfit(t, np.log(seg), 1)[0]
    print(start, end, "tau=%.2f ms" % (-1e3 / s))
# full-resolution fit between 10 and 50 ms
i1, i2 = int(0.010 * FS), int(0.050 * FS)
t = np.arange(i2 - i1) / FS
s = np.polyfit(t, np.log(env[i1:i2]), 1)[0]
print("full-res tau 10-50ms", -1e3 / s)
