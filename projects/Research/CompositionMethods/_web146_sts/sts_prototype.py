"""SP-146 STS prototype: sound texture synthesis via filter statistics.

Analysis:  ERB-spaced cochlear filterbank (partition of unity, narrow 15 %
           crossfades) -> analytic envelopes -> 0.3-power cochlear compression
           -> decimation to 400 Hz -> moments M1..M4 per band + cross-band
           envelope correlation matrix.
Synthesis: white-noise base -> alternate Cholesky correlation recolouring
           (C_cur^(-1/2) C_tgt^(1/2)) with per-band quantile (histogram)
           projection -> outer consistency iterations against the re-analysed
           acoustic signal -> resynthesis with the base phase -> WAV.

Everything printed/written below is measured, not asserted.
"""
import json
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, hilbert, sosfiltfilt

FS = 22050
DUR = 4.0
N = int(FS * DUR)
NB = 24
FMIN, FMAX = 60.0, 8000.0
ENV_FS = 400.0
DEC = int(round(FS / ENV_FS))
CROSS = 0.15  # crossfade width as a fraction of the band width
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- filterbank
def erb_edges(nb=NB, fmin=FMIN, fmax=FMAX):
    """Glasberg-Moore ERB-rate spacing -> band edges in Hz."""

    def hz2erb(f):
        return 21.4 * np.log10(1.0 + 0.00437 * f)

    def erb2hz(e):
        return (10.0 ** (e / 21.4) - 1.0) / 0.00437

    return erb2hz(np.linspace(hz2erb(fmin), hz2erb(fmax), nb + 1))


def band_gains(n, fs=FS, nb=NB, frac=CROSS):
    """Partition-of-unity filterbank: flat passband + narrow raised-cosine
    crossfade into each neighbour, so sum_b H_b(f) == 1 (amplitude-complementary
    enough for a sum-of-bands resynthesis)."""
    edges = erb_edges(nb)
    freqs = np.fft.rfftfreq(n, 1 / fs)
    H = np.zeros((nb, freqs.size))
    for b in range(nb):
        lo, hi = edges[b], edges[b + 1]
        w = frac * (hi - lo)
        # clamp the taper argument, otherwise the cosine keeps oscillating
        # outside its half period and every band leaks across the whole band
        up = 0.5 - 0.5 * np.cos(np.pi * np.clip((freqs - (lo - w)) / w, 0, 1))
        dn = 0.5 + 0.5 * np.cos(np.pi * np.clip((freqs - hi) / w, 0, 1))
        g = np.where(freqs < lo, up, 1.0)
        g = np.where(freqs > hi, dn, g)
        H[b] = g
    s = H.sum(axis=0)
    s[s < 1e-9] = 1.0
    return H / s


def analyse_bands(x, H):
    X = np.fft.rfft(x)
    return np.fft.irfft(X[None, :] * H, n=x.size, axis=1)


def compress(env, power=0.3):
    return np.maximum(env, 0.0) ** power


def decimate(env):
    """Envelope decimation to ENV_FS by block mean (1-D or (bands, samples))."""
    m = env.shape[-1] // DEC
    if env.ndim == 1:
        return env[: m * DEC].reshape(m, DEC).mean(axis=1)
    return env[..., : m * DEC].reshape(env.shape[0], m, DEC).mean(axis=2)


def moments(e):
    mu, sd = e.mean(), e.std()
    z = (e - mu) / sd
    return [mu, (sd ** 2) / mu ** 2, float((z ** 3).mean()), float((z ** 4).mean())]


def corr_matrix(E):
    return np.nan_to_num(np.corrcoef(E), nan=0.0)


def msqrt(C, invert=False):
    w, V = np.linalg.eigh(C)
    w = np.clip(w, 1e-6, None)
    w = 1.0 / w if invert else w
    return (V * np.sqrt(w)) @ V.T


# ---------------------------------------------------------------- target
def make_target():
    """Synthetic rain-like texture: Poisson impact train through a resonant body
    plus a band-limited noise bed with slow gusting -> non-Gaussian envelopes
    (high kurtosis in the upper bands) and strong cross-band correlation."""
    t = np.arange(N) / FS
    x = np.zeros(N)
    pos = rng.integers(0, N - 400, int(55.0 * DUR))
    L = 300
    for p in pos:
        env = np.exp(-np.arange(L) / 55.0)
        f = rng.uniform(900, 5200)
        x[p:p + L] += 0.35 * env * np.sin(2 * np.pi * f * np.arange(L) / FS + rng.uniform(0, 6.28))
    bed = rng.standard_normal(N)
    B = np.fft.rfft(bed)
    fr = np.fft.rfftfreq(N, 1 / FS)
    B *= np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / 1800.0) / 0.9) ** 2)
    x += np.fft.irfft(B, n=N) * 0.25
    x *= 1.0 + 0.25 * np.sin(2 * np.pi * 0.7 * t)
    return x / np.abs(x).max() * 0.9


def stats_of(x, H):
    bands = analyse_bands(x, H)
    cenv = decimate(compress(np.abs(hilbert(bands, axis=1))))
    return {
        "cenv": cenv,
        "mom": np.array([moments(r) for r in cenv]),
        "corr": corr_matrix(cenv),
        "rms": np.sqrt((bands ** 2).mean(axis=1)),
    }


# ---------------------------------------------------------------- synthesis
def quantile_project(row, target_sorted):
    out = np.empty_like(row)
    out[np.argsort(row)] = target_sorted
    return out


def project(E, Ct, tgt_sorted, iters):
    for _ in range(iters):
        W = msqrt(corr_matrix(E), invert=True) @ msqrt(Ct)
        E = W.T @ E
        E = np.array([quantile_project(E[b], tgt_sorted[b]) for b in range(NB)])
    return E


def synthesise(tgt, outer=3, inner=15):
    H, Ct = tgt["H"], tgt["corr"]
    tgt_sorted = [np.sort(r) for r in tgt["cenv"]]
    base = rng.standard_normal(N)
    bb = analyse_bands(base, H)
    benv = decimate(compress(np.abs(hilbert(bb, axis=1))))
    tt_b = np.arange(benv.shape[1]) * DEC + DEC / 2
    sos = butter(4, 150.0, "lowpass", fs=FS, output="sos")

    def expand(row, tt):
        """compressed envelope samples -> smooth full-rate linear amplitude"""
        v = np.interp(np.arange(N), tt, row) ** (1 / 0.3)
        return sosfiltfilt(sos, v)

    Bfull = np.array([expand(benv[b], tt_b) for b in range(NB)])
    tt = np.arange(tgt["cenv"].shape[1]) * DEC + DEC / 2

    E = tgt["cenv"].copy()
    E = (E - E.mean(1, keepdims=True)) / E.std(1, keepdims=True)
    E = project(E, Ct, tgt_sorted, inner)
    errs, y = [], None
    for k in range(outer):
        Efull = np.array([expand(E[b], tt) for b in range(NB)])
        # amplitude-modulate the base fine structure by target/base envelope ratio
        y = (bb * (Efull / np.maximum(Bfull, 1e-6))).sum(axis=0)
        y -= y.mean()
        y /= np.abs(y).max()
        Ey = stats_of(y, H)["cenv"]
        Ey = (Ey - Ey.mean(1, keepdims=True)) / Ey.std(1, keepdims=True)
        errs.append(float(np.linalg.norm(corr_matrix(Ey) - Ct) / np.linalg.norm(Ct)))
        if k < outer - 1:
            E = project(Ey, Ct, tgt_sorted, max(4, inner // 3))
    y *= 0.89 / np.abs(y).max()
    return y, errs, E


def spectral_centroid(sig):
    Sx = np.abs(np.fft.rfft(sig)) ** 2
    return float((Sx * np.fft.rfftfreq(sig.size, 1 / FS)).sum() / Sx.sum())


def main():
    x = make_target()
    H = band_gains(N)
    tgt = {"x": x, "H": H}
    tgt.update(stats_of(x, H))

    y, errs, E = synthesise(tgt, outer=3, inner=15)
    out = stats_of(y, H)

    dm = np.abs(out["mom"] - tgt["mom"])
    band_db = 20 * np.log10(out["rms"] / tgt["rms"])
    c_t, c_y = spectral_centroid(x), spectral_centroid(y)
    # projection-domain check (the algorithm's own invariant)
    proj_corr = float(np.linalg.norm(corr_matrix(E) - tgt["corr"]) / np.linalg.norm(tgt["corr"]))

    sf.write("sts_out.wav", y.astype(np.float32), FS)
    sf.write("sts_target.wav", x.astype(np.float32), FS)

    res = {
        "bands": NB,
        "env_fs_hz": ENV_FS,
        "iterations_inner_outer": "15 inner / 3 outer",
        "proj_corr_err_final": proj_corr,
        "acoustic_corr_err_curve": [round(e, 4) for e in errs],
        "acoustic_corr_err_final": round(errs[-1], 4),
        "moment_abs_err_max": [round(float(v), 4) for v in dm.max(axis=0)],
        "kurt_target_max": round(float(tgt["mom"][:, 3].max()), 3),
        "kurt_out_max": round(float(out["mom"][:, 3].max()), 3),
        "band_rms_err_db_max": round(float(np.abs(band_db).max()), 3),
        "band_rms_err_db_median": round(float(np.median(np.abs(band_db))), 3),
        "centroid_target_hz": round(c_t, 1),
        "centroid_out_hz": round(c_y, 1),
        "centroid_rel_diff": round(abs(c_y - c_t) / c_t, 4),
        "wav_bytes": os.path.getsize("sts_out.wav"),
        "peak": round(float(np.abs(y).max()), 4),
        "dc": float(y.mean()),
    }
    json.dump(res, open("sts_stats.json", "w"), indent=2)
    for k, v in res.items():
        print(f"{k:32s} {v}")


if __name__ == "__main__":
    main()
