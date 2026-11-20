import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tb = S.analyse_bands(x, H)
print("target band rms  low->high:", np.round(np.sqrt((tb**2).mean(1)), 5))
rng = np.random.default_rng(7)
base = rng.standard_normal(S.N)
bb = S.analyse_bands(base, H)
print("base band rms    low->high:", np.round(np.sqrt((bb**2).mean(1)), 5))
print("bandwidths:", np.round(S.erb_edges(S.NB)[1:] - S.erb_edges(S.NB)[:-1], 1))
