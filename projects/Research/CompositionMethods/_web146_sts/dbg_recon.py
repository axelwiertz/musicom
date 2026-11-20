import numpy as np
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
b = S.analyse_bands(x, H)
print("x rms", np.sqrt((x**2).mean()), "sum bands rms", np.sqrt((b.sum(0)**2).mean()))
print("recon rel err", np.linalg.norm(b.sum(0) - x) / np.linalg.norm(x))
print("energy in bands", (b**2).sum(), "energy x", (x**2).sum())
print("H sum stats", H.sum(0).min(), H.sum(0).max(), H.sum(0).mean())
print("H rows nonzero counts", (H > 1e-12).sum(1)[:5], "...", (H > 1e-12).sum(1)[-3:])
