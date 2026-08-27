"""Sound check for SP002 polyphonic stack render."""
import numpy as np
from scipy.io import wavfile
from pathlib import Path

WAV = Path("/opt/data/projects/Styles/Production/SP002-polyphonic-stack-steel-guitar/Audio/SP002-polyphonic-stack-steel-guitar.wav")

sr, data = wavfile.read(WAV)
print(f"SR={sr} shape={data.shape} dtype={data.dtype}")
if data.ndim == 2:
    left = data[:, 0].astype(np.float64)
    right = data[:, 1].astype(np.float64)
else:
    left = data.astype(np.float64)
    right = left.copy()
mono = 0.5 * (left + right)

dur = len(mono) / sr
print(f"duration={dur:.3f}s  samples={len(mono)}")

peak_l = np.max(np.abs(left)) / 32768.0
peak_r = np.max(np.abs(right)) / 32768.0
print(f"peak L={peak_l:.4f} ({20*np.log10(peak_l):.1f} dBFS)  R={peak_r:.4f} ({20*np.log10(peak_r):.1f} dBFS)")

rms = np.sqrt(np.mean(mono ** 2)) / 32768.0
print(f"RMS={rms:.5f} ({20*np.log10(rms):.1f} dBFS)")

# silence fraction
silent = np.sum(np.abs(mono) < 0.001 * 32768) / len(mono)
print(f"silence fraction (<0.001): {silent:.4f}")

# per-second RMS profile
sec = int(sr)
print("\nper-second RMS profile:")
for i in range(int(dur)):
    seg = mono[i*sec:(i+1)*sec]
    if len(seg) == 0:
        continue
    r = np.sqrt(np.mean(seg ** 2)) / 32768.0
    db = 20 * np.log10(r) if r > 1e-9 else -120
    bars = int(np.clip((db + 60) / 60 * 40, 0, 40))
    print(f"  {i:2d}s: {db:6.1f} dBFS {'#'*bars}")

# spectral centroid / balance per channel
def spectral_stats(sig):
    n = len(sig)
    win = np.hanning(n)
    spec = np.abs(np.fft.rfft(sig * win))
    freqs = np.fft.rfftfreq(n, 1/sr)
    total = np.sum(spec)
    centroid = np.sum(freqs * spec) / total if total > 0 else 0
    # fundamental check near D4 293.66
    def band_energy(f0, f1):
        m = (freqs >= f0) & (freqs <= f1)
        return np.sum(spec[m])
    return centroid, band_energy(270, 320), band_energy(540, 640), band_energy(1000, 3000)

for name, sig in (("L", left), ("R", right)):
    c, d4, d4x2, high = spectral_stats(sig)
    print(f"\n{name}: centroid={c:.0f} Hz  D4(270-320)={d4:.0f}  D4x2(540-640)={d4x2:.0f}  high(1-3k)={high:.0f}")

# stereo correlation
corr = np.corrcoef(left, right)[0, 1]
print(f"\nstereo corr L/R = {corr:.4f}")

# DC offset
print(f"DC offset L={np.mean(left):.3f} R={np.mean(right):.3f}")
