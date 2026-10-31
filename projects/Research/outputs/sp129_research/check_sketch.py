import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
from scipy.signal import fftconvolve
C, A = 343.0, 0.0875
FC = C / (2 * np.pi * A)

def plant(n, fs=48000, span_deg=60.0, dist=1.0):
    f = rfftfreq(n, 1 / fs); th = np.deg2rad(span_deg / 2)
    spk = np.array([[dist*np.cos(th), dist*np.sin(th)], [dist*np.cos(th), -dist*np.sin(th)]])
    ears = np.array([[0.0, -A], [0.0, A]]); w = 2j*np.pi*f
    H = np.zeros((2, 2, f.size), complex)
    for e in range(2):
        for s in range(2):
            r = np.linalg.norm(spk[s] - ears[e]); h = np.exp(-w*r/C)/r
            if e != s:
                h /= (1 + w/(2*np.pi*FC))
            H[e, s] = h
    return H, f

def invert(H, beta=1e-4):
    Cc = np.empty_like(H)
    for k in range(H.shape[2]):
        h = H[:, :, k]
        Cc[:, :, k] = h.conj().T @ np.linalg.inv(h @ h.conj().T + beta*np.eye(2))
    return Cc

def process(x, Cc, n, pre_delay=0):
    hop = n // 2
    xd = np.pad(x, ((0, 0), (hop + pre_delay, 0))); y = np.zeros_like(x)
    for start in range(0, x.shape[1], hop):
        seg = xd[:, start:start + n]
        X = rfft(seg, n, axis=1)
        Y = np.stack([Cc[o, 0]*X[0] + Cc[o, 1]*X[1] for o in (0, 1)])
        out = irfft(Y, n, axis=1)[:, hop:]
        m = min(hop, x.shape[1] - start)
        y[:, start:start + m] = out[:, :m]
    return y

n = 4096
H, f = plant(n)
Cc = invert(H, 1e-4)
hir = irfft(Cc, 8192, axis=1)
N = 12000
x = np.random.default_rng(0).standard_normal((2, N))
ref = np.zeros_like(x)
for o in range(2):
    for i in range(2):
        ref[o] += fftconvolve(x[i], hir[o, i])[:N]
ref = np.concatenate([np.zeros((2, 144)), ref[:, :N-144]], axis=1)
out = process(x, Cc, n, pre_delay=144)
e = 20*np.log10(np.sqrt(((out-ref)[:, 1000:]**2).mean()) / np.sqrt((ref[:, 1000:]**2).mean()))
print(f"[sketch] overlap-save vs direct IR convolution: {e:.1f} dB")

sig = np.sin(2*np.pi*440*np.arange(N)/48000)
B = np.stack([sig, sig])
S = process(B, Cc, n, pre_delay=144)
E = np.zeros_like(B)
for a in range(2):
    for b in range(2):
        E[a] += irfft(H[a, b]*rfft(np.roll(S[b], -144)), N)
print("[closed loop] centre-source error",
      round(float(20*np.log10(np.sqrt(((E-B)[:, 1000:]**2).mean()) / np.sqrt((B[:, 1000:]**2).mean()))), 1), "dB")
