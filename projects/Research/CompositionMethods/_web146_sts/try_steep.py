import numpy as np
from scipy.signal import hilbert
import sts_prototype as S

# steep partition-of-unity filterbank: flat passband + narrow raised-cosine
# crossfade (15% of band width) into each neighbour


def band_gains_steep(n, fs=S.FS, nb=S.NB, frac=0.15):
    edges = S.erb_edges(nb)
    freqs = np.fft.rfftfreq(n, 1 / fs)
    H = np.zeros((nb, freqs.size))
    for b in range(nb):
        lo, hi = edges[b], edges[b + 1]
        wl = frac * (hi - lo)
        wh = frac * (hi - lo)
        g = np.ones_like(freqs)
        g = np.where(freqs < lo, np.clip(0.5 - 0.5 * np.cos(np.pi * (freqs - (lo - wl)) / wl), 0, 1), g)
        g = np.where(freqs > hi, np.clip(0.5 + 0.5 * np.cos(np.pi * (freqs - hi) / wh), 0, 1), g)
        H[b] = g
    s = H.sum(axis=0)
    s[s < 1e-9] = 1.0
    return H / s


x = S.make_target()
H = band_gains_steep(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y, errs, E = S.synthesise(tgt, iters=25)
y = y - y.mean(); y /= np.abs(y).max()
out = S.stats_of(y, H)
dm = np.abs(out["mom"] - tgt["mom"])
print("proj corr", errs[0], "->", errs[-1])
print("acoustic corr", np.linalg.norm(out["corr"] - tgt["corr"]) / np.linalg.norm(tgt["corr"]))
print("mom abs max", np.round(dm.max(0), 3), "rel", np.round((dm / np.maximum(np.abs(tgt["mom"]), 1e-9)).max(0), 3))
print("kurt target max", tgt["mom"][:, 3].max(), "out max", out["mom"][:, 3].max())
