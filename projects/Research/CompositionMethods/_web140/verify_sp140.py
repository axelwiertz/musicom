"""SP-140 Schroeder Reverberator (SRB) — verified prototype.

Renders the classic 1962 comb+allpass network and measures:
  comb IR spacing/decay, allpass flatness, RT60 (Schroeder 1965 backward
  integration), echo-density growth, comb-vs-network ripple, quasi-stereo
  decorrelation, determinism, stability, damping, WAV artifact.

Run: /opt/data/micromamba/envs/musicom/bin/python verify_sp140.py
"""
import numpy as np
import wave

FS = 44100
COMB_MS = [29.7, 37.1, 41.1, 43.7]      # Moorer/Schroeder canonical combs
COMB_G = 0.77
AP_MS_L = [5.0, 1.7]                     # left allpass chain
AP_MS_R = [4.7, 1.3]                     # right chain (quasi-stereo)
AP_G = 0.7
RHO = 1.2  # placeholder (not used; kept for symmetry with physical entries)

def ms2s(ms):
    return int(round(ms * FS / 1000.0))

def comb(x, m, g, damp=0.0):
    """Feedback comb filter; optional in-loop one-pole HF damping (Jot/Freeverb).

    damp = one-pole coefficient on the history: lp = (1-damp)*out + damp*lp.
    damp=0 -> lp = out -> classic Schroeder comb y[n] = x[n] + g*y[n-m].
    damp->1 -> feedback frozen dark (strong HF cut)."""
    n = len(x); y = np.zeros(n); dly = np.zeros(m)
    lp = 0.0; idx = 0
    for i in range(n):
        out = dly[idx]
        lp = (1.0 - damp) * out + damp * lp
        dly[idx] = x[i] + g * lp
        y[i] = out
        idx = (idx + 1) % m
    return y

def allpass(x, m, g):
    """Schroeder allpass: y[n] = -g x[n] + x[n-m] + g y[n-m]; single delay line."""
    n = len(x); y = np.zeros(n); dly = np.zeros(m); idx = 0
    for i in range(n):
        v = dly[idx]                     # stores x[n-m] + g*y[n-m]
        y[i] = v - g * x[i]
        dly[idx] = x[i] + g * y[i]
        idx = (idx + 1) % m
    return y

def network_ir(dur_s, damp=0.0, chain="L"):
    """Full wet-path impulse response: 4 parallel combs -> 2 series allpasses."""
    n = int(dur_s * FS)
    x = np.zeros(n); x[0] = 1.0
    wet = sum(comb(x, ms2s(m), COMB_G, damp) for m in COMB_MS) / 4.0
    ap = AP_MS_L if chain == "L" else AP_MS_R
    out = allpass(allpass(wet, ms2s(ap[0]), AP_G), ms2s(ap[1]), AP_G)
    return out

def rt60(ir, fs=FS, rng=(-5.0, -35.0)):
    """Schroeder backward-integration RT60 on squared IR."""
    e = np.cumsum(ir[::-1] ** 2)[::-1]
    e = np.maximum(e, 1e-30)
    db = 10.0 * np.log10(e / e[0])
    lo, hi = rng
    idx = np.where((db <= lo) & (db >= hi))[0]
    if len(idx) < 10:
        return float("nan")
    k = np.polyfit(idx, db[idx], 1)
    return -60.0 / k[0] / fs

def density(ir, w0_ms, w1_ms, thr=1e-3):
    """Echo count per second in window (echo = |h| > thr*max|h|)."""
    a, b = int(w0_ms * FS / 1000), int(w1_ms * FS / 1000)
    seg = ir[a:b]
    cnt = int(np.sum(np.abs(seg) > thr * np.max(np.abs(ir))))
    return cnt / ((b - a) / FS)

def mag_spec_db(h, fs=FS):
    H = np.abs(np.fft.rfft(h, n=1 << 18))
    H = np.maximum(H, 1e-12)
    return 20.0 * np.log10(H)

CHECKS = []

def check(no, name, ok, detail):
    CHECKS.append((no, name, ok, detail))
    print("CHECK %02d %-46s %s  %s" % (no, name, "PASS" if ok else "FAIL", detail))

# --- 1. Comb IR: echo spacing + geometric decay ---------------------------
m1 = ms2s(COMB_MS[0])
ir_c = comb(np.r_[1.0, np.zeros(6 * m1)], m1, COMB_G)
pos = np.where(np.abs(ir_c) > 1e-9)[0]
spacing = np.diff(pos)
ratios = ir_c[pos[1:]] / ir_c[pos[:-1]]
check(1, "comb echo spacing = m", np.all(spacing == m1),
      "spacing %d samples (m=%d)" % (spacing[0], m1))
check(2, "comb geometric decay g", np.allclose(ratios, COMB_G, atol=1e-6),
      "ratio %.6f (g=%.2f)" % (ratios[0], COMB_G))

# --- 2. Allpass flat magnitude (colorless) --------------------------------
ma = ms2s(AP_MS_L[1])  # 75
h_ap = allpass(np.r_[1.0, np.zeros(200 * ma)], ma, AP_G)   # full decay (g^200 ~ 1e-31)
H = np.abs(np.fft.rfft(h_ap, n=1 << 16)); H = np.maximum(H, 1e-12)
freqs = np.fft.rfftfreq(1 << 16, 1.0 / FS)
band = (freqs >= 20) & (freqs <= 20000)
dev = np.max(np.abs(20.0 * np.log10(H[band])))
check(3, "allpass |H| flat (colorless)", dev < 0.1,
      "max |H| deviation %.4f dB over 20 Hz-20 kHz" % dev)

# --- 3. Full-network RT60 vs design ---------------------------------------
ir_net = network_ir(3.0, damp=0.0)
t60 = rt60(ir_net)
t60_design = 3.0 * ms2s(max(COMB_MS)) / (FS * abs(np.log10(COMB_G)))
ok = abs(t60 - t60_design) / t60_design < 0.25
check(4, "network RT60 vs design (longest comb)", ok,
      "RT60 %.3f s vs design %.3f s (%+.1f %%)" % (t60, t60_design, 100 * (t60 - t60_design) / t60_design))

# --- 4. Echo-density growth (Schroeder >= ~1000 echos/s criterion) --------
d0 = density(ir_net, 0, 50); d1 = density(ir_net, 100, 150); d2 = density(ir_net, 150, 200)
check(5, "echo density grows with time", d1 > 4 * d0 and d2 > 4 * d0,
      "%.0f -> %.0f -> %.0f echos/s ([0,50) [100,150) [150,200) ms)" % (d0, d1, d2))
check(6, "late echo density >= 500/s", d2 >= 500,
      "%.0f echos/s at 150-200 ms (Schroeder target ~1000/s)" % d2)

# --- 5. Periodic-ripple correlation: comb vs network (colorless discriminator)
# A single comb's magnitude ripples periodically at its own spacing f_s/m.
# The incommensurate 4-comb network must show no dominant periodic ripple:
# autocorrelation of the dB spectrum at lag f_s/m1 is strong for the comb,
# weak for the network.
def db_auto_corr(h, lag_hz, fs=FS, nfft=1 << 18):
    H = np.abs(np.fft.rfft(h, n=nfft)); H = np.maximum(H, 1e-12)
    db = 20.0 * np.log10(H)
    f = np.fft.rfftfreq(nfft, 1.0 / fs)
    lag = int(round(lag_hz * nfft / fs))
    sel = (f >= 100) & (f <= 15000) & (np.arange(len(f)) + lag < len(f))
    a = db[sel]; b = db[np.where(sel)[0] + lag]
    a = a - a.mean(); b = b - b.mean()
    return float(np.mean(a * b) / np.sqrt(np.mean(a * a) * np.mean(b * b)))

lag1 = FS / m1  # 33.66 Hz comb-1 spacing
r_comb = db_auto_corr(ir_c, lag1)
r_net = db_auto_corr(ir_net, lag1)
check(7, "no dominant periodic comb ripple (network)", r_net < 0.35 * r_comb,
      "dB-spectrum autocorr @%.1f Hz: comb %.2f -> network %.2f" % (lag1, r_comb, r_net))

# --- 6. Quasi-stereo decorrelation ----------------------------------------
rng = np.random.default_rng(42)
xw = rng.standard_normal(FS)
wet = sum(comb(xw, ms2s(m), COMB_G, 0.0) for m in COMB_MS) / 4.0
L = allpass(allpass(wet, ms2s(AP_MS_L[0]), AP_G), ms2s(AP_MS_L[1]), AP_G)
R = allpass(allpass(wet, ms2s(AP_MS_R[0]), AP_G), ms2s(AP_MS_R[1]), AP_G)
corr = float(np.corrcoef(L, R)[0, 1])
rms_ratio = float(np.sqrt(np.mean(L ** 2) / np.mean(R ** 2)))
check(8, "quasi-stereo L/R decorrelated", 0.2 < corr < 0.8,
      "corr(L,R) = %.2f (rms ratio %.3f)" % (corr, rms_ratio))

# --- 7. Determinism -------------------------------------------------------
L2 = allpass(allpass(wet, ms2s(AP_MS_L[0]), AP_G), ms2s(AP_MS_L[1]), AP_G)
check(9, "deterministic (bit-identical)", np.array_equal(L, L2), "two renders identical")

# --- 8. Stability + frequency/time consistency ----------------------------
peak_in = np.max(np.abs(xw)); peak_out = max(np.max(np.abs(L)), np.max(np.abs(R)))
check(10, "bounded output (g<1)", peak_out < 6.0 * peak_in,
      "noise peak out/in = %.2f (comb resonance 1/(1-g)=%.2f)" % (peak_out / peak_in, 1 / (1 - COMB_G)))
# steady-state sine gain at a comb-1 resonance must equal |H_net(f)| from the
# network IR's FFT (time domain == frequency domain), and stay bounded.
fk = 300 * FS / m1  # 300th comb-1 peak ~= 10099 Hz
tt = np.arange(int(2.0 * FS)) / FS
xs = np.sin(2 * np.pi * fk * tt)
wet = sum(comb(xs, ms2s(m), COMB_G, 0.0) for m in COMB_MS) / 4.0
ys = allpass(allpass(wet, ms2s(AP_MS_L[0]), AP_G), ms2s(AP_MS_L[1]), AP_G)
gain = float(np.max(np.abs(ys[int(1.0 * FS):])) / np.max(np.abs(xs[int(1.0 * FS):])))
nfft = 1 << 18
Hnet = np.abs(np.fft.rfft(ir_net, n=nfft)); Hnet = np.maximum(Hnet, 1e-12)
fn = np.fft.rfftfreq(nfft, 1.0 / FS)
h_at_fk = float(Hnet[np.argmin(np.abs(fn - fk))])
check(11, "sine gain == |H_net(f)| (t/f consistency)", abs(gain - h_at_fk) / h_at_fk < 0.1 and gain < 6.0,
      "sine gain %.3f vs |H(fk)| %.3f @ %.0f Hz" % (gain, h_at_fk, fk))
# --- 9. HF damping --------------------------------------------------------
ir_d = network_ir(3.0, damp=0.5)
seg0 = ir_net[int(0.05 * FS):int(0.3 * FS)]; segd = ir_d[int(0.05 * FS):int(0.3 * FS)]
F0 = np.fft.rfftfreq(len(seg0), 1.0 / FS)
S0 = np.abs(np.fft.rfft(seg0)); Sd = np.abs(np.fft.rfft(segd))
c0 = np.sum(S0 * F0) / (np.sum(S0) + 1e-12)
cd = np.sum(Sd * F0) / (np.sum(Sd) + 1e-12)
check(12, "in-loop damping darkens tail", cd < 0.9 * c0,
      "tail centroid %.0f Hz (damp=0) -> %.0f Hz (damp=0.5)" % (c0, cd))

# --- 10. WAV demo artifact ------------------------------------------------
def render_demo(dur_s=2.2, seed=7):
    r = np.random.default_rng(seed)
    n = int(dur_s * FS)
    t = np.arange(n) / FS
    x = np.zeros(n)
    notes = [(261.6, 0.00, 0.7), (329.6, 0.55, 0.6), (392.0, 1.10, 0.6), (523.3, 1.55, 0.5)]
    for f0, t0, a in notes:
        i0 = int(t0 * FS)
        nn = n - i0
        env = np.exp(-3.0 * np.arange(nn) / FS)
        x[i0:] += a * env * (np.sin(2 * np.pi * f0 * t[:nn]) + 0.4 * np.sin(4 * np.pi * f0 * t[:nn]))
    wet = sum(comb(x, ms2s(m), COMB_G, 0.25) for m in COMB_MS) / 4.0
    L = allpass(allpass(wet, ms2s(AP_MS_L[0]), AP_G), ms2s(AP_MS_L[1]), AP_G)
    R = allpass(allpass(wet, ms2s(AP_MS_R[0]), AP_G), ms2s(AP_MS_R[1]), AP_G)
    return x, L, R

xd, Ld, Rd = render_demo()
mix = 0.45
Lm = (1 - mix) * xd + mix * Ld
Rm = (1 - mix) * xd + mix * Rd
stereo = np.stack([Lm, Rm], axis=1)
stereo = np.clip(stereo, -1, 1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open("/opt/data/projects/Research/CompositionMethods/_web140/sp140_demo.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(FS)
    w.writeframes(pcm.tobytes())
import os
size = os.path.getsize("/opt/data/projects/Research/CompositionMethods/_web140/sp140_demo.wav")
expect = 44 + 2 * 2 * len(pcm)
check(13, "WAV artifact + frame count", size == expect and len(pcm) == len(xd),
      "%d B = 44 + 4*%d frames (%.2f s)" % (size, len(pcm), len(pcm) / FS))

print()
print("SUMMARY: %d/%d checks pass" % (sum(1 for _, _, ok, _ in CHECKS if ok), len(CHECKS)))
print("RT60=%.3fs  autocorr_comb=%.2f autocorr_net=%.2f corr=%.2f gain=%.3f" % (t60, r_comb, r_net, corr, gain))
