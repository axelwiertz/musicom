import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))

y_unit, errs, E = S.synthesise(tgt, iters=40)

# --- variant A: unit-phasor carrier (current) -------------------------------
# --- variant B: AM of the base noise bands by the target/base envelope ratio
rng = np.random.default_rng(7)
base = rng.standard_normal(S.N)
bb = S.analyse_bands(base, H)
benv = np.abs(hilbert(bb, axis=1))
Efull = np.empty((S.NB, S.N))
tt = np.arange(E.shape[1]) * S.DEC + S.DEC / 2
for b in range(S.NB):
    Efull[b] = np.maximum(np.interp(np.arange(S.N), tt, E[b]), 1e-6) ** (1 / 0.3)
yb = (bb * (Efull / np.maximum(benv, 1e-9))).sum(axis=0)

for name, y in (("unit", y_unit), ("am", yb)):
    y = y - y.mean()
    y = y / np.abs(y).max() * 0.89
    out = S.stats_of(y, H)
    dm = np.abs(out["mom"] - tgt["mom"])
    rel = dm / np.maximum(np.abs(tgt["mom"]), 1e-9)
    print(name, "mom abs max", dm.max(axis=0), "rel max per moment", rel.max(axis=0),
          "corr err", np.linalg.norm(out["corr"] - tgt["corr"]) / np.linalg.norm(tgt["corr"]))
