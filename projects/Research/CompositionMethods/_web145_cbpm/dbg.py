import numpy as np
FS = 44100
n = 12 * FS
t = np.arange(n) / FS
T60 = 8.0
y = np.sin(2 * np.pi * 1171.5 * t) * 10 ** (-3 * t / T60)

def meas(y, fc, bw=8.0):
    n = len(y)
    fr = np.fft.rfftfreq(n, 1 / FS)
    S = np.fft.rfft(y)
    S[(fr < fc - bw) | (fr > fc + bw)] = 0
    z = np.abs(np.fft.ifft(S, n=n))
    w = int(0.1 * FS)
    m = len(z) // w
    e = np.sqrt(np.mean(z[: m * w].reshape(m, w) ** 2, axis=1)) + 1e-12
    tt = np.arange(m) * 0.1
    db = 20 * np.log10(e / e[0])
    idx = np.where((db < -5) & (db > -40))[0]
    print("n idx", len(idx), db[:5], db[idx[0]] if len(idx) else None)
    slope = np.polyfit(tt[idx], db[idx], 1)[0]
    return -60 / slope, db

print(meas(y, 1171.5))
