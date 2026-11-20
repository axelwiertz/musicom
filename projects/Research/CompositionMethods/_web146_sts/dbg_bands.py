import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y, errs, E = S.synthesise(tgt, outer=1, inner=15)
out = S.stats_of(y, H)
print("band  tgt_rms   out_rms   ratio   tgt_env_mean  E_mean")
for b in range(S.NB):
    print(f"{b:3d} {tgt['rms'][b]:9.5f} {out['rms'][b]:9.5f} {out['rms'][b]/tgt['rms'][b]:7.3f} "
          f"{tgt['cenv'][b].mean():12.4f} {E[b].mean():8.4f}")
