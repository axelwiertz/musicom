import numpy as np
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y, errs, E = S.synthesise(tgt, outer=1, inner=15)
print("y finite", np.isfinite(y).all(), "len", y.size, "peak", np.abs(y).max())
sp = np.abs(np.fft.rfft(y)) ** 2
fr = np.fft.rfftfreq(y.size, 1 / S.FS)
idx = np.argsort(sp)[-10:]
print("top bins:", [(round(float(fr[i]), 1), round(float(sp[i] / sp.sum() * 100), 2)) for i in sorted(idx)])
print("energy >8k", sp[fr > 8000].sum() / sp.sum())
print("E row0 first 8", np.round(E[0][:8], 4), "target", np.round(tgt["cenv"][0][:8], 4))
print("E min/max", E.min(), E.max())
