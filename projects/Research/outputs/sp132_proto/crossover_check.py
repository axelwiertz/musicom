"""Addendum: Linkwitz-Riley 4th-order crossover check + cabinet reflection comb."""
import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz

FS = 48000.0
fc = 800.0
sos_lp = butter(2, fc/(FS/2), btype="low", output="sos")
sos_hp = butter(2, fc/(FS/2), btype="high", output="sos")

# LR4 = two cascaded 2nd-order Butterworth sections of the same type
def lr4(kind):
    return np.concatenate([butter(2, fc/(FS/2), btype=kind, output="sos"),
                           butter(2, fc/(FS/2), btype=kind, output="sos")])

w, hlp = sosfreqz(lr4("low"), worN=8192, fs=FS)
_, hhp = sosfreqz(lr4("high"), worN=8192, fs=FS)
mag = np.abs(hlp + hhp)
print("=== LR4 (2x Butterworth-2) sum ===")
for f in (100, 400, 700, 800, 900, 2000, 8000):
    i = np.argmin(np.abs(w-f))
    print(f"  {f:>5} Hz  |H_lp+H_hp| = {mag[i]:.6f}  ({20*np.log10(mag[i]):+.4f} dB)")
print(f"  max deviation over 20 Hz..20 kHz: "
      f"{np.max(np.abs(20*np.log10(mag[(w>20)&(w<20000)]))):.4f} dB")
print(f"  -6 dB point at fc: {20*np.log10(np.abs(hlp[np.argmin(np.abs(w-fc))])):.2f} dB per band")

print("\n=== Cabinet/louvre reflection comb (delay 2.5 ms, 0.8 gain) ===")
n = 8192
imp = np.zeros(n); imp[0] = 1.0
d = int(0.0025*FS)
imp[d] = 0.8
H = np.abs(np.fft.rfft(imp))
f = np.fft.rfftfreq(n, 1/FS)
band = (f > 50) & (f < 4000)
nul_idx = np.where(band)[0][np.argsort(H[band])[:3]]
print(f"  three deepest nulls: {np.round(f[nul_idx])} Hz "
      f"(theory odd multiples of 1/(2tau) = 200/600/1000 Hz)")
print(f"  comb depth = {20*np.log10(H.min()/H.max()):.1f} dB")
