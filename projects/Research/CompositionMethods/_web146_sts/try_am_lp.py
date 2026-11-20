import numpy as np
from scipy.signal import hilbert, butter, sosfiltfilt
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y, errs, E = S.synthesise(tgt, outer=1, inner=15)

rng = np.random.default_rng(7)
base = rng.standard_normal(S.N)
bb = S.analyse_bands(base, H)
cbe = S.decimate(S.compress(np.abs(hilbert(bb, axis=1))))
tt = np.arange(cbe.shape[1]) * S.DEC + S.DEC / 2
ttE = np.arange(E.shape[1]) * S.DEC + S.DEC / 2
sos = butter(4, 150.0, "lowpass", fs=S.FS, output="sos")

def up(row, tt):
    v = np.interp(np.arange(S.N), tt, row) ** (1 / 0.3)
    return sosfiltfilt(sos, v)

smooth = np.array([up(cbe[b], tt) for b in range(S.NB)])
Efull = np.array([up(E[b], ttE) for b in range(S.NB)])

y2 = (bb * (Efull / np.maximum(smooth, 1e-6))).sum(0)
y2 -= y2.mean(); y2 *= 0.89 / np.abs(y2).max()
out = S.stats_of(y2, H)
fr = np.fft.rfftfreq(y2.size, 1 / S.FS)
sp = np.abs(np.fft.rfft(y2)) ** 2
dm = np.abs(out["mom"] - tgt["mom"])
print("corr err", np.linalg.norm(out["corr"] - tgt["corr"]) / np.linalg.norm(tgt["corr"]))
print("mom abs max", np.round(dm.max(0), 3))
print("hi-frac>4k", sp[fr > 4000].sum() / sp.sum(), "centroid", (sp * fr).sum() / sp.sum(), "target", 2574.8)
