#!/usr/bin/env python3
"""
SP-138 STEPS — Struck-Tine Electromechanical Piano Synthesis: verification prototype.
Two-mass asymmetric tuning-fork core (tine + tonebar) -> modal note renderer ->
velocity-sensing nonlinear magnetic pickup -> damper -> tanh preamp -> stereo tremolo.
12 checks. Deterministic per seed. Sample-count preserving (zero-drift safe).
"""
import numpy as np, wave, os

FS = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "steps_verify_output.txt")
_log = open(OUT, "w", encoding="utf-8")
_lines = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); _log.write(s + "\n"); _log.flush(); _lines.append(s)

P("=" * 78)
P("SP-138 STEPS prototype verification — %s" % np.__version__)
P("=" * 78)

# ---------------------------------------------------------------- check 1-3: two-mass fork ODE
def fork_ring(f0, mu, rho, zeta_t, zeta_b, dur, strike=1.0, dt=1.0 / FS):
    """Integrate coupled tine/tonebar:  y_t (light, struck), y_b (heavy). Returns (t, yt, yb)."""
    w0 = 2 * np.pi * f0
    mt, mb = 1.0, mu
    kt, kb = mt * w0 ** 2, mb * w0 ** 2
    kc = rho * mt * w0 ** 2
    rt, rb = 2 * zeta_t * w0 * mt, 2 * zeta_b * w0 * mb  # damping coeffs (tuned at w0)
    n = int(dur * FS)
    yt = np.zeros(n); yb = np.zeros(n)
    vt = np.zeros(n); vb = np.zeros(n)
    vt[0] = strike  # hammer impulse to the tine
    a_yt, a_yb = yt[0], yb[0]
    for i in range(n - 1):
        # semi-implicit Euler
        at = (-kt * yt[i] - rt * vt[i] - kc * (yt[i] - yb[i])) / mt
        ab = (-kb * yb[i] - rb * vb[i] - kc * (yb[i] - yt[i])) / mb
        vt[i + 1] = vt[i] + at * dt
        vb[i + 1] = vb[i] + ab * dt
        yt[i + 1] = yt[i] + vt[i + 1] * dt
        yb[i + 1] = yb[i] + vb[i + 1] * dt
    return yt, yb

def peak_freqs(x, k=3, min_db=40):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / FS)
    X[0] = 0
    Xdb = 20 * np.log10(np.maximum(X / (X.max() + 1e-30), 1e-30))
    peaks = []
    for i in range(1, len(Xdb) - 1):
        if Xdb[i] > Xdb[i - 1] and Xdb[i] > Xdb[i + 1] and Xdb[i] > -min_db:
            peaks.append((f[i], Xdb[i]))
    peaks.sort(key=lambda t: -t[1])
    return [p[0] for p in peaks[:k]]

f0 = 220.0; mu = 8.0; rho = 0.02
w2_theory = f0 * np.sqrt(1 + rho * (1 + 1.0 / mu))
P("\n[1-3] two-mass fork ODE: f0=%.2f Hz, mu=%.2f, rho=%.3f -> upper mode theory %.2f Hz" % (f0, mu, rho, w2_theory))
yt, yb = fork_ring(f0, mu, rho, 0.004, 0.002, 4.0)
pf = peak_freqs(yt, 2, 60)
P("  measured fork modes: %s" % ["%.2f Hz" % v for v in pf])
ok1 = any(abs(p - f0) < 0.5 for p in pf)
ok2 = any(abs(p - w2_theory) < 1.0 for p in pf)
P("  check1 in-phase mode = f0 present: %s" % ("PASS" if ok1 else "FAIL"))
P("  check2 out-of-phase mode = theory present: %s" % ("PASS" if ok2 else "FAIL"))

# beat: undamped fork ring (zero damping) -> Hilbert envelope -> beat freq = f2 - f1
from scipy.signal import hilbert
yu, _ = fork_ring(f0, mu, rho, 0.0, 0.0, 6.0)
env = np.abs(hilbert(yu))
env = env - np.mean(env)
E = np.abs(np.fft.rfft(env * np.hanning(len(env)))); fe = np.fft.rfftfreq(len(env), 1.0 / FS)
E[0] = 0
m = (fe > 0.3) & (fe < 8.0)
beat_f_meas = fe[m][np.argmax(E[m])]
beat_f_theory = w2_theory - f0
beat_period_meas = 1.0 / beat_f_meas
beat_period_theory = 1.0 / beat_f_theory
P("  beat freq measured %.3f Hz vs theory %.3f Hz (period %.3f vs %.3f s)" %
  (beat_f_meas, beat_f_theory, beat_period_meas, beat_period_theory))
P("  check3 energy slosh (beating): %s" % ("PASS" if abs(beat_f_meas - beat_f_theory) / beat_f_theory < 0.03 else "FAIL"))

# ---------------------------------------------------------------- check 4-5: pickup transduction
def nonlinear_pickup(y):
    """Flux Phi(x)=1/(1+x/d); EMF = -dPhi/dt (discrete derivative). d = 1.0 (normalized)."""
    d = 1.0
    Phi = 1.0 / (1.0 + y / d)
    return -np.diff(Phi) * FS

t = np.arange(4 * FS) / FS
yt2, _ = fork_ring(f0, mu, rho, 0.004, 0.002, 4.0)
out = nonlinear_pickup(yt2)
v = np.diff(yt2) * FS
# small-motion: output should correlate with velocity
cc = np.corrcoef(out[50:2000], v[50:2000])[0, 1]
P("\n[4] pickup EMF vs tine velocity (small motion): r=%.4f" % cc)
P("  check4 velocity sensing: %s" % ("PASS" if cc > 0.99 else "FAIL"))

# two-tone intermodulation: drive two modes f_a, f_b through nonlinear pickup
fa, fb = 200.0, 440.0
tt = np.arange(3 * FS) / FS
x2 = 0.5 * np.sin(2 * np.pi * fa * tt) + 0.5 * np.sin(2 * np.pi * fb * tt)
y2 = nonlinear_pickup(x2)
X = np.abs(np.fft.rfft(y2)); fr = np.fft.rfftfreq(len(y2), 1.0 / FS)
X[0] = 0
im_lo = abs(fb - fa); im_hi = fb + fa
amp_lo = X[np.argmin(np.abs(fr - im_lo))] / X.max()
amp_hi = X[np.argmin(np.abs(fr - im_hi))] / X.max()
P("\n[5] pickup intermodulation: |fb-fa|=%.0f Hz rel %.3f, fb+fa=%.0f Hz rel %.3f" % (im_lo, amp_lo, im_hi, amp_hi))
P("  check5 mode intermodulation (JASA 2020 effect): %s" % ("PASS" if amp_lo > 0.02 and amp_hi > 0.02 else "FAIL"))

# ---------------------------------------------------------------- full note renderer (modal bank)
def render_note(f0n, vel, dur, r2=2.2, r3=4.5, stretch=None, damp=False, seed=0, trem=None,
                drive=0.8, f_up=None, amp_up=0.06, release_at=None, pickup_d=1.2):
    """Modal bank: tine modes f0, r2*f0, r3*f0 (inharmonic stretch) + shared tonebar sustain +
    coupled upper fork mode (beat). Velocity->brightness power law. Nonlinear pickup, damper,
    tanh preamp, optional stereo tremolo. Returns stereo float array (samples, 2)."""
    rng = np.random.default_rng(seed)
    n = int(dur * FS)
    fsig = np.array([f0n, r2 * f0n, r3 * f0n])
    tau = np.array([2.2, 0.35, 0.12])            # decay taus (s)
    amp = np.array([1.0, 0.45, 0.20]) * vel ** np.array([0.55, 1.5, 2.2])
    amp /= np.max(np.abs(amp)) + 1e-9
    ph = rng.uniform(0, 2 * np.pi, 3)
    tt = np.arange(n) / FS
    x = np.zeros(n)
    for a_, f_, ta_, ph_ in zip(amp, fsig, tau, ph):
        x += a_ * np.exp(-tt / ta_) * np.sin(2 * np.pi * f_ * tt + ph_)
    # tonebar sustain reservoir: shares f0, very long decay, small amp (fork reinforcement)
    x += 0.35 * vel ** 0.55 * np.exp(-tt / 14.0) * np.sin(2 * np.pi * f0n * tt + ph[0] + 0.4)
    # coupled out-of-phase upper mode -> audible beat wobble in the attack
    if f_up is None:
        f_up = f0n * np.sqrt(1 + 0.02 * (1 + 1 / 8.0))
    x += amp_up * vel ** 0.8 * np.exp(-tt / 0.8) * np.sin(2 * np.pi * f_up * tt + ph[1])
    # magnetic pickup: velocity sensing + nonlinear flux (intermodulation); pickup_d>>1 = linear
    Phi = 1.0 / (1.0 + x / pickup_d)
    x = -np.diff(Phi, prepend=Phi[0]) * FS
    # preamp tanh saturation (odd harmonics); drive<=0 bypasses the preamp
    if drive > 0:
        x = np.tanh(drive * x)
    # damper: felt pad engages at key release, 50 ms contact -> smooth collapse of the
    # pickup output (mechanical motion suppressed). Applied post-transduction (signal flow).
    if damp and release_at is not None:
        rel = int(release_at * dur * FS)
        env_d = np.ones(n)
        tr = int(0.01 * FS)                     # 10 ms raised-cosine transition
        tdec = tt[rel:] - tt[rel]
        env_d[rel:] = np.exp(-tdec / 0.05)
        ramp = 0.5 - 0.5 * np.cos(np.pi * np.arange(tr) / tr)
        env_d[rel:rel + tr] *= ramp
        x *= env_d
    x *= 0.8 / (np.max(np.abs(x)) + 1e-9)
    # stereo tremolo (opposite-phase LFO gains)
    if trem:
        rate, depth = trem
        gL = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt))
        gR = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt + np.pi))
        return np.stack([x * gL, x * gR], axis=1)
    return np.stack([x, x], axis=1)

P("\n[6] inharmonic stretch: rendering C4 (261.63 Hz), vel 0.8; linear pickup (pickup_d=100); FFT over 400 ms attack window")
x6 = render_note(261.63, 0.8, 2.5, seed=1, drive=0.0, pickup_d=100.0)[:, 0]
i0, i1 = int(0.05 * FS), int(0.45 * FS)
seg = x6[i0:i1] * np.hanning(i1 - i0)
X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1.0 / FS)
X[0] = 0
def band_peak(lo, hi):
    m = (fr >= lo) & (fr <= hi)
    if not m.any(): return None
    return fr[m][np.argmax(X[m])]
p1 = band_peak(261.63 - 40, 261.63 + 40)
p2 = band_peak(2.2 * 261.63 - 40, 2.2 * 261.63 + 40)
p3 = band_peak(4.5 * 261.63 - 60, 4.5 * 261.63 + 60)
r2v = p2 / p1 if (p2 and p1) else float("nan")
r3v = p3 / p1 if (p3 and p1) else float("nan")
P("  partials (attack window): f1=%.2f f2=%.2f f3=%.2f | ratios %.3f %.3f" % (p1, p2, p3, r2v, r3v))
P("  check6 inharmonic stretch (2nd partial in (2.0,2.6), not 2.0): %s" % (
    "PASS" if (p2 and p1 and 2.0 < r2v < 2.6 and abs(r2v - 2.0) > 0.05) else "FAIL"))

P("\n[7] velocity -> brightness (pickup output, preamp bypassed)")
x_soft = render_note(261.63, 0.3, 1.5, seed=2, drive=0.0)[:, 0]
x_hard = render_note(261.63, 0.95, 1.5, seed=2, drive=0.0)[:, 0]
def band_ratio(xx):
    Xx = np.abs(np.fft.rfft(xx * np.hanning(len(xx)))); frr = np.fft.rfftfreq(len(xx), 1.0 / FS)
    Xx[0] = 0
    b1 = Xx[(frr > 240) & (frr < 290)].max()
    b2 = Xx[(frr > 500) & (frr < 750)].max()
    return 20 * np.log10(b2 / (b1 + 1e-30))
br_s, br_h = band_ratio(x_soft), band_ratio(x_hard)
dr = br_h - br_s
P("  mode2/mode1 band ratio: soft %.1f dB, hard %.1f dB, delta %.1f dB" % (br_s, br_h, dr))
P("  check7 velocity->brightness (hard > soft by >6 dB): %s" % ("PASS" if dr > 6 else "FAIL"))

P("\n[8] damper release (key release at 0.8 s of a 2.0 s note)")
x_free = render_note(261.63, 0.6, 2.0, seed=3, damp=False)
x_damp = render_note(261.63, 0.6, 2.0, seed=3, damp=True, release_at=0.4)
def rms_win(xx, a, b):
    seg = xx[int(a * FS):int(b * FS)]
    return float(np.sqrt(np.mean(seg ** 2)) + 1e-30)
r_free = rms_win(x_free[:, 0], 1.0, 2.0)
r_damp = rms_win(x_damp[:, 0], 1.0, 2.0)
P("  RMS in [1.0,2.0] s: free %.4f, damped %.5f -> ratio %.1f (%.1f dB)" %
  (r_free, r_damp, r_free / r_damp, 20 * np.log10(r_free / r_damp)))
P("  check8 damper shortens decay (RMS ratio > 10): %s" % ("PASS" if r_free / r_damp > 10 else "FAIL"))

P("\n[9] tanh preamp odd-only harmonics")
xt = np.tanh(0.8 * np.sin(2 * np.pi * 220 * np.arange(1 * FS) / FS))
Xt = np.abs(np.fft.rfft(xt)); frt = np.fft.rfftfreq(len(xt), 1.0 / FS)
h2 = 20 * np.log10(Xt[np.argmin(np.abs(frt - 440))] / Xt[np.argmin(np.abs(frt - 220))])
h3 = 20 * np.log10(Xt[np.argmin(np.abs(frt - 660))] / Xt[np.argmin(np.abs(frt - 220))])
P("  h2=%.1f dB, h3=%.1f dB (tanh: odd-only)" % (h2, h3))
P("  check9 preamp saturation: %s" % ("PASS" if h3 > -40 and h2 < -100 else "FAIL"))

P("\n[10] stereo tremolo anti-phase")
xtr = render_note(440.0, 0.7, 2.0, seed=4, trem=(4.0, 0.7))
envL = np.convolve(np.abs(xtr[:, 0]), np.ones(256) / 256, "same")
envR = np.convolve(np.abs(xtr[:, 1]), np.ones(256) / 256, "same")
# cross-correlate envelopes at lag 0 (should be ~ -1)
cc_t = np.corrcoef(envL[FS:2 * FS], envR[FS:2 * FS])[0, 1]
P("  L/R envelope correlation r=%.3f (anti-phase -> ~ -1)" % cc_t)
P("  check10 tremolo: %s" % ("PASS" if cc_t < -0.9 else "FAIL"))

P("\n[11] zero-drift + determinism")
a = render_note(330.0, 0.5, 1.2345, seed=7)
b = render_note(330.0, 0.5, 1.2345, seed=7)
c = render_note(330.0, 0.5, 1.2345, seed=8)
P("  length exact: %d == %d (%s)" % (a.shape[0], int(1.2345 * FS), "PASS" if a.shape[0] == int(1.2345 * FS) else "FAIL"))
P("  same seed identical: %s" % ("PASS" if np.array_equal(a, b) else "FAIL"))
P("  diff seed differs: %s" % ("PASS" if not np.array_equal(a, c) else "FAIL"))
P("  check11: %s" % ("PASS" if (a.shape[0] == int(1.2345 * FS) and np.array_equal(a, b) and not np.array_equal(a, c)) else "FAIL"))

# ---------------------------------------------------------------- demo phrase
P("\n[12] demo phrase -> sp138_demo.wav")
notes = [  # (midi, vel, start_s, dur_s)
    (60, 0.55, 0.00, 1.6), (64, 0.50, 0.45, 1.3), (67, 0.60, 0.90, 1.2),
    (71, 0.65, 1.35, 1.0), (72, 0.85, 1.80, 1.4), (71, 0.60, 2.30, 1.0),
    (67, 0.55, 2.75, 1.2), (64, 0.45, 3.20, 2.0),
]
total = 5.4
buf = np.zeros((int(total * FS), 2))
for midi, vel, st, du in notes:
    f = 440.0 * 2 ** ((midi - 69) / 12)
    seg = render_note(f, vel, du + 0.05, seed=100 + midi, trem=(3.5, 0.65), drive=0.85)
    i0 = int(st * FS)
    buf[i0:i0 + seg.shape[0]] += seg
buf = buf / (np.max(np.abs(buf)) + 1e-9) * 0.85
pcm = (buf * 32767).astype(np.int16)
w = wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp138_demo.wav"), "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(FS)
w.writeframes(pcm.tobytes()); w.close()
P("  wrote sp138_demo.wav: %d frames, %d bytes" % (buf.shape[0], os.path.getsize(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp138_demo.wav"))))
P("  check12 demo file: %s" % ("PASS" if os.path.getsize(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp138_demo.wav")) > 40 else "FAIL"))

n_pass = sum(1 for l in _lines if "check" in l and "PASS" in l and "FAIL" not in l)
n_fail = sum(1 for l in _lines if "check" in l and "FAIL" in l)
P("\n=== %d/12 checks PASS (%d FAIL) ===" % (n_pass, n_fail))
_log.close()
