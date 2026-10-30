"""SP-128 EMD/HHT verification: sifting correctness, filter-bank property,
instantaneous-frequency resynthesis, mode mixing / EEMD reconstruction loss,
transient concentration, cost. Optional TEST 9 runs on a real musicom render.

Run:  $MUSICOM_PYTHON verify_sp128_emd.py
"""
import time
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal import hilbert

FS = 44100
rng = np.random.default_rng(1280)


def _extrema(x):
    d = np.diff(np.sign(np.diff(x)))
    return np.where(d < 0)[0] + 1, np.where(d > 0)[0] + 1


def _envelope(x):
    n = len(x)
    maxi, mini = _extrema(x)
    if len(maxi) < 2 or len(mini) < 2:
        return None, None
    tgrid = np.arange(n)
    tm = np.concatenate(([0], maxi, [n - 1]))
    ym = np.concatenate(([x[maxi[0]]], x[maxi], [x[maxi[-1]]]))
    tn = np.concatenate(([0], mini, [n - 1]))
    yn = np.concatenate(([x[mini[0]]], x[mini], [x[mini[-1]]]))
    return (CubicSpline(tm, ym, bc_type="natural")(tgrid),
            CubicSpline(tn, yn, bc_type="natural")(tgrid))


def sift(x, sd_thresh=0.2, max_iter=10):
    h = np.asarray(x, dtype=float).copy()
    for _ in range(max_iter):
        up, lo = _envelope(h)
        if up is None:
            return h
        h_new = h - 0.5 * (up + lo)
        sd = np.sum((h - h_new) ** 2) / max(np.sum(h ** 2), 1e-30)
        h = h_new
        if sd < sd_thresh:
            break
    return h


def emd(x, max_imfs=6, sd_thresh=0.2, max_sift=10, min_extrema=4):
    res = np.asarray(x, dtype=float).copy()
    imfs = []
    for _ in range(max_imfs):
        if np.count_nonzero(np.diff(np.sign(np.diff(res)))) < min_extrema:
            break
        imf = sift(res, sd_thresh=sd_thresh, max_iter=max_sift)
        if np.count_nonzero(np.diff(np.sign(np.diff(imf)))) < 2:
            break
        imfs.append(imf)
        res = res - imf
    return (np.array(imfs) if imfs else np.zeros((0, len(x)))), res


def inst_freq(imf):
    z = hilbert(imf)
    return np.abs(z), np.gradient(np.unwrap(np.angle(z))) * FS / (2 * np.pi)


def centroid(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / FS)
    return float(np.sum(f * X) / max(np.sum(X), 1e-30))


t = np.arange(int(1.0 * FS)) / FS
tone = 1.0 * np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 660 * t)
burst = np.zeros_like(t)
i0 = int(0.40 * FS)
burst[i0:i0 + 800] = 0.9 * rng.standard_normal(800) * np.exp(-np.arange(800) / 120.0)
trend = 0.6 * np.cos(2 * np.pi * 1.2 * t)
sig = tone + burst + trend

print("=== TEST 1: exact reconstruction (sum of IMFs + residue == input) ===")
t0 = time.time()
imfs, res = emd(sig)
elapsed = time.time() - t0
recon = (imfs.sum(axis=0) if len(imfs) else 0) + res
err = np.max(np.abs(recon - sig)) / np.max(np.abs(sig))
print(f"  n_imfs={len(imfs)}  max_rel_recon_error={err:.3e}  time={elapsed:.2f}s / 1.0 s @ {FS} Hz")

print("\n=== TEST 2: Flandrin filter-bank property (spectral centroid per IMF) ===")
cents = [centroid(m) for m in imfs] + [centroid(res)]
print("  centroids (IMFs then residue):", [round(c, 1) for c in cents])
print("  strictly decreasing high->low:", all(cents[i] > cents[i + 1] for i in range(len(cents) - 1)))

print("\n=== TEST 3: Hilbert IF tracks the partials ===")
for k, m in enumerate(imfs):
    a, f = inst_freq(m)
    w = a > 0.3 * a.max()
    print(f"  IMF{k+1}: median IF (high-energy) {np.median(f[w]):8.1f} Hz | spectral centroid {cents[k]:7.1f} Hz")

print("\n=== TEST 4: per-IMF transposition via IF scaling (r = 1.5) ===")
r = 1.5
for k, m in enumerate(imfs[:3]):
    a, f = inst_freq(m)
    w = a > 0.3 * a.max()
    y = a * np.cos(2 * np.pi * np.cumsum(r * f) / FS)
    fo = np.fft.rfftfreq(len(m), 1 / FS)
    po = fo[np.argmax(np.abs(np.fft.rfft(m)))]
    pn = fo[np.argmax(np.abs(np.fft.rfft(y)))]
    print(f"  IMF{k+1}: IF-med {np.median(f[w]):7.1f} | argmax {po:7.1f} -> {pn:7.1f} Hz "
          f"(target {r*po:7.1f}, ratio {pn/max(po,1e-9):.3f})")

print("\n=== TEST 5: mode mixing — IMF index carrying the 220 Hz partial ===")
f = np.fft.rfftfreq(len(t), 1 / FS)
band = np.abs(f - 220) < 15


def imf_at_220(ims):
    e = [float(np.abs(np.fft.rfft(m))[band].sum()) for m in ims]
    return int(np.argmax(e)) if e else -1


ids = [imf_at_220(emd(tone + (0.05 * rng.standard_normal(len(t)) if s else 0.0))[0]) for s in range(5)]
print("  indices across tiny perturbations:", ids, "-> stable:", len(set(ids)) == 1)

print("\n=== TEST 6: EEMD ensemble mean is NOT an exact decomposition ===")
K = len(imfs)
acc = np.zeros((K, len(t)))
for _ in range(6):
    x = sig + 0.3 * np.std(sig) * rng.standard_normal(len(t))
    im, _ = emd(x, max_imfs=K)
    pad = np.zeros((K, len(t)))
    pad[: len(im)] = im[:K]
    acc += pad
eem = acc / 6
print(f"  EEMD-mean sum rel error vs signal: {np.max(np.abs(eem.sum(0)-sig))/np.max(np.abs(sig)):.3e} "
      f"(plain EMD: {err:.3e})")
print("  EEMD-mean centroids:", [round(centroid(m), 1) for m in eem])

print("\n=== TEST 7: transient concentration per IMF (own energy inside burst window) ===")
seg = slice(i0, i0 + 2000)
for k, m in enumerate(imfs):
    c = float(np.sum(m[seg] ** 2) / max(np.sum(m ** 2), 1e-30))
    print(f"  IMF{k+1}: {100*c:5.1f} % of this IMF's energy sits in the 45 ms burst window "
          f"(uniform expectation {100*2000/len(t):.1f} %)")

print("\n=== TEST 8: cost scaling (numpy+scipy sifting, single core) ===")
for dur in (0.5, 1.0, 2.0):
    n = int(dur * FS)
    x = np.sin(2 * np.pi * 220 * np.arange(n) / FS) + 0.4 * rng.standard_normal(n)
    ts = time.time()
    im, _ = emd(x)
    dt = time.time() - ts
    print(f"  {dur:4.1f} s @44.1k -> {dt:5.2f} s, {len(im)} IMFs ({dur/dt:4.2f}x realtime)")

print("\n=== TEST 9: real musicom render (if the engine is importable) ===")
try:
    import os
    import tempfile
    from workflows.musicom_workflow import compose, produce
    outdir = os.path.join(os.getcwd(), "render")
    os.makedirs(outdir, exist_ok=True)
    r = compose(style="pop", key="C", bpm=120)
    p = produce(r.midi_path, method="SP-001")
    wav = getattr(p, "wav_path", None) or getattr(p, "audio_path", None)
    print("  compose/produce ok:", r.midi_path, "| wav:", wav)
    if wav and os.path.getsize(wav) > 40:
        from scipy.io import wavfile
        sr, data = wavfile.read(wav)
        x = data.astype(float)
        if x.ndim > 1:
            x = x.mean(axis=1)
        x = x / (np.abs(x).max() + 1e-12)
        seg = x[: int(2.0 * sr)]
        ts = time.time()
        im, rr = emd(seg, max_imfs=6)
        dt = time.time() - ts
        er = np.max(np.abs((im.sum(0) if len(im) else 0) + rr - seg)) / np.max(np.abs(seg))
        print(f"  render {sr} Hz, {len(seg)/sr:.1f} s -> {len(im)} IMFs in {dt:.2f} s "
              f"({len(seg)/sr/dt:.2f}x realtime), recon err {er:.2e}")
        print("  IMF centroids on the real mix:", [round(centroid(m), 1) for m in im])
except Exception as e:
    print("  skipped:", type(e).__name__, e)

print("\nDONE")
