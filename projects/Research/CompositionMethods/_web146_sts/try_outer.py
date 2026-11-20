import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
rng = np.random.default_rng(7)
base = rng.standard_normal(S.N)
bb = S.analyse_bands(base, H)
phase = np.angle(hilbert(bb, axis=1))
Ct = tgt["corr"]
tgt_sorted = [np.sort(r) for r in tgt["cenv"]]
tt = np.arange(tgt["cenv"].shape[1]) * S.DEC + S.DEC / 2


def project(E, iters=15):
    for _ in range(iters):
        Cc = S.corr_matrix(E)
        W = S.msqrt(Cc, invert=True) @ S.msqrt(Ct)
        E = W.T @ E
        E = np.array([S.quantile_project(E[b], tgt_sorted[b]) for b in range(S.NB)])
    return E


E = tgt["cenv"].copy()
E = (E - E.mean(1, keepdims=True)) / E.std(1, keepdims=True)
E = project(E, 2)
for outer in range(5):
    Efull = np.empty((S.NB, S.N))
    for b in range(S.NB):
        Efull[b] = np.maximum(np.interp(np.arange(S.N), tt, E[b]), 1e-6) ** (1 / 0.3)
    y = np.real((Efull * np.exp(1j * phase)).sum(0))
    y -= y.mean(); y /= np.abs(y).max()
    out = S.stats_of(y, H)
    dm = np.abs(out["mom"] - tgt["mom"])
    print(f"outer {outer}  corr {np.linalg.norm(out['corr']-Ct)/np.linalg.norm(Ct):.4f} "
          f"mom relmax {np.round((dm/np.maximum(np.abs(tgt['mom']),1e-9)).max(0),3)}")
    Ey = out["cenv"]
    E = (Ey - Ey.mean(1, keepdims=True)) / Ey.std(1, keepdims=True)
    E = project(E, 8)
