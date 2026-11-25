import numpy as np
from scipy.signal import lfilter, hilbert

FS = 48000
f0, Q = 440.0, 22.07
w0 = 2 * np.pi * f0 / FS
alpha = np.sin(w0) / (2 * Q)
a0 = 1 + alpha
b = [alpha / a0, 0.0, -alpha / a0]
a = [1.0, -2 * np.cos(w0) / a0, (1 - alpha) / a0]
imp = np.zeros(FS)
imp[0] = 1.0
x = lfilter(b, a, imp)

block = 0.005
env = np.abs(hilbert(x))
n = int(block * FS)
nb = len(env) // n
rms = np.sqrt((env[:nb * n].reshape(nb, n) ** 2).mean(axis=1)) + 1e-30
print("argmax", np.argmax(rms), "len", len(rms))
i0 = int(np.argmax(rms))
i0 += max(2, int(0.01 * FS) // n)
seg = rms[i0:]
keep = seg > seg[0] * 1e-3
seg2 = seg[keep]
print("i0", i0, "seg0", seg[0], "nseg", len(seg), "kept", len(seg2))
print("seg2", seg2[:8], seg2[-3:])
t = np.arange(len(seg2)) * block
s = np.polyfit(t, np.log(seg2), 1)[0]
print("tau", -1 / s * 1e3)
# trim more aggressively: only 3 tau
keep2 = seg > seg[0] * 0.02
s2 = np.polyfit(np.arange(keep2.sum()) * block, np.log(seg[keep2]), 1)[0]
print("tau(0.02 cut)", -1 / s2 * 1e3, "blocks kept", keep2.sum())
print("ratio seg2[3]/seg2[2]", seg2[3] / seg2[2], "theory", np.exp(-0.005 / 0.015966))
print("mean ratio", np.exp(np.mean(np.diff(np.log(seg2)))))
