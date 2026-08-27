import numpy as np, os
from sound.utils.io import read_wav

print('Per-stage L/R correlation (near 1 = mono-compatible):')
for f in sorted(os.listdir('Audio/master')):
    if not f.endswith('.wav'):
        continue
    a, _ = read_wav(f'Audio/master/{f}')
    if a.ndim == 2:
        corr = np.corrcoef(a[:, 0], a[:, 1])[0, 1]
    else:
        corr = 1.0
    print(f'  {f:<26} corr={corr:.6f}')
