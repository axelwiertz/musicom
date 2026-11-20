import numpy as np
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
print("x", x.shape, "H", H.shape, "sum gain range", H.sum(0).min(), H.sum(0).max())
bands = S.analyse_bands(x, H)
print("bands", bands.shape)
env = np.abs(__import__("scipy.signal", fromlist=["hilbert"]).hilbert(bands, axis=1))
print("env", env.shape)
c = S.compress(env)
print("c", c.shape)
d = S.decimate(c)
print("dec", d.shape)
C = S.corr_matrix(d)
print("C", C.shape, np.isnan(C).sum())
print("msqrt", S.msqrt(C, invert=True).shape, S.msqrt(C).shape)
