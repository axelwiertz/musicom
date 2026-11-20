import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y_unit, errs, E = S.synthesise(tgt, iters=40)

rng = np.random.default_rng(11)
base = rng.standard_normal(S.N)
bb = S.analyse_bands(base, H)
Ab = hilbert(bb, axis=1)
phase = np.angle(Ab)

Efull = np.empty((S.NB, S.N))
tt = np.arange(E.shape[1]) * S.DEC + S.DEC / 2
for b in range(S.NB):
    Efull[b] = np.maximum(np.interp(np.arange(S.N), tt, E[b]), 1e-6) ** (1 / 0.3)

variants = {}
variants["analytic_phase"] = np.real((Efull * np.exp(1j * phase)).sum(axis=0))

# also test: re-impose the target envelope in the analysis domain using the
# *target's own* fine structure (upper bound / consistency check)
tb = S.analyse_bands(x, H)
tA = hilbert(tb, axis=1)
tp = np.angle(tA)
variants["target_phase_oracle"] = np.real((Efull * np.exp(1j * tp)).sum(axis=0))

for name, y in variants.items():
    y = y - y.mean()
    y = y / np.abs(y).max() * 0.89
    out = S.stats_of(y, H)
    dm = np.abs(out["mom"] - tgt["mom"])
    rel = dm / np.maximum(np.abs(tgt["mom"]), 1e-9)
    print(f"{name:22s} mom abs max {np.round(dm.max(axis=0),3)} relmax {np.round(rel.max(axis=0),3)} "
          f"corr {np.linalg.norm(out['corr']-tgt['corr'])/np.linalg.norm(tgt['corr']):.4f}")
