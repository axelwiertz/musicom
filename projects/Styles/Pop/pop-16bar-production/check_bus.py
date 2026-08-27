import numpy as np, os
from sound.utils.io import read_wav

# Verify the stereo bus before mastering has L != R
stems_dir = 'Audio/stems'
pans = [-0.5, 0.0, 0.5, 0.0]
n = 1632576
bus = np.zeros((n, 2), dtype=np.float64)
files = sorted(f for f in os.listdir(stems_dir) if f.endswith('.wav'))
for i, sf in enumerate(files):
    a, _ = read_wav(os.path.join(stems_dir, sf))
    if a.ndim == 2:
        a = a.mean(axis=1)
    a = a[:n]
    pad = max(0, n - len(a))
    if pad:
        a = np.pad(a, (0, pad))
    pan = pans[i % len(pans)]
    gL = np.sqrt((1 - pan) / 2) if pan <= 0 else np.sqrt((1 + pan) / 2)
    gR = np.sqrt((1 + pan) / 2) if pan <= 0 else np.sqrt((1 - pan) / 2)
    bus[:, 0] += a * gL
    bus[:, 1] += a * gR

print(f'Stereo bus: shape={bus.shape}')
diff = np.max(np.abs(bus[:, 0] - bus[:, 1]))
print(f'Max |L - R|: {diff:.6f}  {"REAL STEREO" if diff > 1e-4 else "MONO!"}')
corr = np.corrcoef(bus[:, 0], bus[:, 1])[0, 1]
print(f'L/R correlation: {corr:.6f}')
