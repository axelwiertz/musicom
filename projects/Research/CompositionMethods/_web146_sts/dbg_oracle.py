import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
bands = S.analyse_bands(x, H)
A = hilbert(bands, axis=1)
env = np.abs(A)
cenv = S.decimate(S.compress(env))
tt = np.arange(cenv.shape[1]) * S.DEC + S.DEC / 2

Efull = np.empty((S.NB, S.N))
for b in range(S.NB):
    Efull[b] = np.maximum(np.interp(np.arange(S.N), tt, cenv[b]), 1e-6) ** (1 / 0.3)

for name, y in (
    ("oracle_analytic", np.real((Efull * np.exp(1j * np.angle(A))).sum(0))),
    ("oracle_fullsample", (env * np.exp(1j * np.angle(A))).real.sum(0)),
):
    err = np.linalg.norm(y - x) / np.linalg.norm(x)
    sp = np.abs(np.fft.rfft(y)) ** 2
    fr = np.fft.rfftfreq(y.size, 1 / S.FS)
    print(name, "rel err vs x", round(float(err), 4),
          "centroid", round(float((sp * fr).sum() / sp.sum()), 1),
          "hi-frac", round(float(sp[fr > 4000].sum() / sp.sum()), 3))
