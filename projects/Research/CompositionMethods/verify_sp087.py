"""Verify SP-087 TASS NumPy sketch: shell partials, service-manual decay law, HP noise, determinism."""
import numpy as np

fs = 44100
f_L, f_H = 238.0, 476.0   # service-manual typical shell partials (Hz)
T_D_SHELL = 0.060          # service-manual "decay time": time to 1/10 amplitude (-20 dB), s
T_D_NOISE = 0.075          # noise burst decay time to 1/10 amplitude, s
FC = 1000.0                # noise highpass cutoff, Hz (Tone mid)
DUR = 0.6
rng = np.random.default_rng(808)

n = int(fs * DUR)
t = np.arange(n) / fs
tau_s = T_D_SHELL / np.log(10.0)   # 1/e time from -20 dB time
tau_n = T_D_NOISE / np.log(10.0)

shell = (np.sin(2 * np.pi * f_L * t) + np.sin(2 * np.pi * f_H * t)) * np.exp(-t / tau_s)
white = rng.standard_normal(n)
a = np.exp(-2 * np.pi * FC / fs)    # one-pole highpass coefficient
hp = np.empty(n)
prev_x, prev_y = 0.0, 0.0
for i in range(n):
    hp[i] = white[i] - prev_x + a * prev_y
    prev_x, prev_y = white[i], hp[i]
noise = hp * np.exp(-t / tau_n)
y = 0.5 * shell + 0.4 * noise / (np.abs(noise).max() + 1e-12)

# 1. shell partials via zero-padded FFT (first 150 ms, Hann)
seg = shell[:int(fs * 0.15)] * np.hanning(int(fs * 0.15))
spec = np.abs(np.fft.rfft(seg, n=32768))
freqs = np.fft.rfftfreq(32768, 1 / fs)
peaks = freqs[np.argsort(spec)[-2:]]
print("shell FFT peaks:", sorted(round(float(p), 1) for p in peaks))
assert any(abs(p - f_L) < 3 for p in peaks), "missing 238 Hz partial"
assert any(abs(p - f_H) < 3 for p in peaks), "missing 476 Hz partial"

# 2. service-manual decay law per partial via coherent demodulation
#    (the two octave partials beat against each other, so a raw rectified
#    envelope hits nulls long before the true decay — demodulate each)
def partial_env(x, f0):
    w = int(fs * 0.02)
    win = np.ones(w) / w
    I = np.convolve(x * np.cos(2 * np.pi * f0 * t), win, mode="same")
    Q = np.convolve(x * np.sin(2 * np.pi * f0 * t), win, mode="same")
    return 2 * np.sqrt(I ** 2 + Q ** 2)

for f0 in (f_L, f_H):
    pe = partial_env(shell, f0)
    pe_db = 20 * np.log10(pe / (pe.max() + 1e-12) + 1e-12)
    idx = int(np.argmax(pe_db[int(fs * 0.01):] <= -20) + fs * 0.01)
    t20 = idx / fs * 1000
    Q = tau_s * np.pi * f0
    print(f"partial {f0:.0f} Hz: -20dB ms:", round(float(t20), 1), "Q:", round(float(Q), 2))
    assert 50 < t20 < 75, f"shell decay out of range @ {f0} Hz"
    assert 12 < Q < 45, f"Q out of range @ {f0} Hz"

# 3. noise layer spectral centroid well above cutoff (highpass working)
seg_n = noise[:int(fs * 0.15)] * np.hanning(int(fs * 0.15))
spec_n = np.abs(np.fft.rfft(seg_n))
freqs_n = np.fft.rfftfreq(len(seg_n), 1 / fs)
cent = float((freqs_n * spec_n).sum() / (spec_n.sum() + 1e-12))
print("noise centroid Hz:", round(cent))
assert cent > 2500, "highpass not effective"

# 4. energy concentrated: 99.9% within 400 ms
e = np.cumsum(y ** 2)
frac = float(e[int(fs * 0.4)] / e[-1])
print("energy frac @400ms:", round(frac, 4))
assert frac > 0.999, "tail too long"

# 5. determinism: same seed reproduces the noise exactly
rng2 = np.random.default_rng(808)
assert (rng2.standard_normal(n) == white).all(), "seed not deterministic"

print("SP-087 SKETCH: ALL CHECKS PASS")
