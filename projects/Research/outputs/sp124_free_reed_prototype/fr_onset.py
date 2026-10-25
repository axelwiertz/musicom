"""SP-124 onset sweep + timbre check on the validated parameter set."""
import numpy as np
from fr_sweep import run, analyse, FS

F0 = 194.0
ZETA, RRAD, VC, AF = 0.02, 4e7, 2e-5, 1.0

print(f"f0(reed, free) = {F0} Hz   zeta={ZETA} Rrad={RRAD:.0e} Vc={VC:.0e}")
print(f"{'pm[Pa]':>8} {'rms':>11} {'fpeak[Hz]':>10} {'cents':>7} {'tonal':>6}")
prev = None
for pm in (50, 100, 150, 200, 250, 300, 400, 600, 800, 1000, 1500, 2000, 2500, 3000, 4000):
    x = run(F0, float(pm), ZETA, RRAD, VC, af_ratio=AF)
    rms, fp, tonal = analyse(x, F0)
    print(f"{pm:8d} {rms:11.4e} {fp:10.1f} {1200*np.log2(fp/F0) if fp>0 else float('nan'):7.1f} {tonal:6.3f}")

# harmonic structure at a working pressure
x = run(F0, 1500.0, ZETA, RRAD, VC, af_ratio=AF)
seg = x[int(0.2 * FS):int(0.2 * FS) + 16384]
X = np.abs(np.fft.rfft(seg * np.hanning(seg.size)))
f = np.fft.rfftfreq(seg.size, 1 / FS)
fund = f[np.argmax(X * (f < 400))]
harm = [float(X[int(round(k * fund * seg.size / FS))]) for k in range(1, 13)]
harm = np.array(harm) / harm[0]
print("\nharmonic amplitudes / H1 at pm=1500 Pa (f0=%.1f Hz):" % fund)
print("  ", " ".join(f"H{k}={v:.2f}" for k, v in enumerate(harm, 1)))
print("spectral centroid (0-10 kHz): %.0f Hz" %
      (np.sum(f[f < 10000] * X[f < 10000]) / np.sum(X[f < 10000])))

a = run(F0, 1500.0, ZETA, RRAD, VC, af_ratio=AF)
b = run(F0, 1500.0, ZETA, RRAD, VC, af_ratio=AF)
print("deterministic:", bool(np.array_equal(a, b)))
