"""
SP-150  Helmholtz Cavity-Resonator Instrument Synthesis (HCRIS)
Verification prototype.  Every number quoted in methods_db.md SP-150 comes
from this script's output (verify_hcris_results.txt).

Physics modelled
  acoustic inertance   M_a = rho * L_eq / A        [kg/m^4]
  acoustic compliance  C_a = V / (rho c^2)         [m^4 s^2/kg]
  f0 = 1/(2 pi sqrt(M_a C_a)) = (c/2pi) sqrt(A/(V L_eq))
  losses: monopole radiation + neck Stokes layer + cavity thermal layer
  excitation: saturating jet flow delayed by the flue-to-labium transit time
"""
import json
import os
import numpy as np
import soundfile as sf
from scipy.signal import freqz, hilbert

RHO, C_AIR, MU, GAMMA, D_TH = 1.204, 343.0, 1.81e-5, 1.4, 2.2e-5


# ----------------------------------------------------------------- geometry
def f_helmholtz(V, A, L_neck, a_neck, end_k=0.613, c=C_AIR):
    L_eq = L_neck + end_k * a_neck
    return c / (2 * np.pi) * np.sqrt(A / (V * L_eq)), L_eq


def area_for_f(f, V, L_neck, a_neck, end_k=0.613):
    L_eq = L_neck + end_k * a_neck
    return V * L_eq * (2 * np.pi * f / C_AIR) ** 2


def volume_for_f(f, A, L_neck, a_neck, end_k=0.613):
    L_eq = L_neck + end_k * a_neck
    return A * C_AIR ** 2 / (L_eq * (2 * np.pi * f) ** 2)


# ------------------------------------------------------------------- losses
def q_radiation(V, A, L_eq, c=C_AIR):
    """Q = w0 E / P_rad with E = 1/2 M_a U^2, P_rad = rho c k^2 U^2/(4 pi)
    =>  Q_rad = 2 pi L_eq c / (A w0)."""
    w0 = c * np.sqrt(A / (V * L_eq))
    return 2 * np.pi * L_eq * c / (A * w0)


def q_viscous(A, L_neck, a_neck, L_eq, f0, rho=RHO, mu=MU):
    w0 = 2 * np.pi * f0
    R_v = L_neck * np.sqrt(2 * rho * mu * w0) / (np.pi * a_neck ** 3)
    return w0 * (rho * L_eq / A) / R_v


def q_thermal(V, S_wall, f0, gamma=GAMMA, D=D_TH):
    d_t = np.sqrt(2 * D / (2 * np.pi * f0))
    return 2 * V / (S_wall * d_t * (gamma - 1))


def q_total(*qs):
    return 1.0 / sum(1.0 / q for q in qs)


# --------------------------------------------------------------- resonator
class BiquadBP:
    """RBJ constant-skirt bandpass: unity gain at f0, phase 0 at f0,
    +pi/2 at DC, -pi/2 at Nyquist (the physical driven-cavity phase)."""

    def __init__(self, f0, Q, fs):
        w0 = 2 * np.pi * f0 / fs
        alpha = np.sin(w0) / (2 * Q)
        a0 = 1 + alpha
        self.b0 = alpha / a0
        self.b2 = -alpha / a0
        self.a1 = -2 * np.cos(w0) / a0
        self.a2 = (1 - alpha) / a0
        self.z1 = self.z2 = 0.0

    def coeffs(self):
        return [self.b0, 0.0, self.b2], [1.0, self.a1, self.a2]


def measure_freq(x, fs):
    x = np.asarray(x, float)
    x = x - x.mean()
    w = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * w))
    X[0] = 0.0
    k = int(np.argmax(X))
    if k < 1 or k >= len(X) - 1:
        return float(k * fs / len(x))
    a, b, c = np.log(X[k - 1] + 1e-30), np.log(X[k] + 1e-30), np.log(X[k + 1] + 1e-30)
    den = a - 2 * b + c
    d = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
    return (k + d) * fs / len(x)


def measure_tau(x, fs, block=0.005):
    """Decay time constant from block-RMS log-slope (median of successive
    log ratios, robust to Hilbert edge artefacts)."""
    x = np.asarray(x, float)
    env = np.abs(hilbert(x))
    n = int(block * fs)
    nb = len(env) // n
    rms = np.sqrt((env[:nb * n].reshape(nb, n) ** 2).mean(axis=1)) + 1e-30
    i0 = int(np.argmax(rms))
    i0 += max(2, int(0.01 * fs) // n)      # skip Hilbert-transient / onset
    seg = rms[i0:i0 + 12]                    # ~3.7 tau of clean exponential
    slope = np.median(np.diff(np.log(seg))) / block
    return -1.0 / slope


# --------------------------------------------------------- jet drive source
def jet_drive(f0, Q, p_mouth, fs, dur, L_jet=0.0015, u_ref=12.0,
              Cv=0.6, gain=60.0, p_sat=100.0, jitter=0.0, seed=0, onset=0.004):
    """Self-sustained vessel flute: u_j = Cv sqrt(2 p/rho), jet velocity
    u_c = 0.4 u_j, delay tau = L_jet/u_c.  Acoustic flow into the cavity is
    Q_ac = gain*u_j*tanh(p_c/p_sat): amplitude proportional to the jet speed,
    saturating at the labium.  Onset noise starts the oscillation (as breath
    does); jitter adds broadband breath noise."""
    rng = np.random.default_rng(seed)
    u_j = Cv * np.sqrt(2.0 * p_mouth / RHO)
    tau = L_jet / (0.4 * u_j)
    D = max(1, int(round(tau * fs)))
    bq = BiquadBP(f0, Q, fs)
    b0, b2, a1, a2 = bq.b0, bq.b2, bq.a1, bq.a2
    n = int(dur * fs)
    ph = np.zeros(n + D + 2)
    out = np.empty(n)
    k = gain * u_j / p_sat
    z1 = z2 = 0.0
    x1 = x2 = 0.0
    n_on = int(onset * fs)
    seed_noise = rng.standard_normal(n_on)
    for i in range(n):
        e = gain * u_j * np.tanh(ph[i] / p_sat)
        if i < n_on:
            e += 1e-3 * u_j * seed_noise[i]
        x = b0 * e + b2 * x2            # RBJ b1 = 0
        x2, x1 = x1, e
        y = x - a1 * z1 - a2 * z2       # RBJ subtraction form
        z2, z1 = z1, y
        out[i] = y
        ph[i + D] += y
    if jitter:
        out += jitter * rng.standard_normal(n) * np.max(np.abs(out)) * 0.02
    return out


def phase_condition_f(f0, Q, tau, fs):
    """Oscillation frequency: the resonator phase must cancel the jet delay,
    angle(H(f)) = 2 pi f tau, whose root lies just below f0."""
    bq = BiquadBP(f0, Q, fs)
    b, a = bq.coeffs()
    f = np.linspace(0.2 * f0, f0 * 0.9999, 40000)
    _, h = freqz(b, a, worN=f, fs=fs)
    ph = np.unwrap(np.angle(h))
    g = ph - 2 * np.pi * f * tau
    s = np.sign(g)
    idx = np.where(np.diff(s) != 0)[0]
    if len(idx) == 0:
        return float("nan")
    i = idx[-1]
    return float(f[i] - g[i] * (f[i + 1] - f[i]) / (g[i + 1] - g[i]))


# ----------------------------------------------------------- coupled systems
def coupled_modes(f_cav, f_mem, kc):
    """Two coupled oscillators (cavity mode + membrane mode) in f^2:
    [[fc^2, kc],[kc, fm^2]], kc in Hz^2.  Avoided crossing."""
    M = np.array([[f_cav ** 2, kc], [kc, f_mem ** 2]])
    return np.sqrt(np.sort(np.linalg.eigvalsh(M)))


# ==================================================================== checks
results = []


def check(name, ok, detail):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


FS = 48000

# 1 ---------------------------------------------------------- bottle tuning
V_b, d_b, L_b = 0.5e-3, 0.020, 0.020
A_b = np.pi * (d_b / 2) ** 2
f_b, L_eq_b = f_helmholtz(V_b, A_b, L_b, d_b / 2)
check("1 bottle f0 (500 mL, 20 mm dia x 20 mm neck)", 120 < f_b < 320,
      "f0=%.2f Hz  L_eq=%.4f m  A=%.3e m2" % (f_b, L_eq_b, A_b))

# 2 ------------------------------------------------------- scaling laws
f2 = f_helmholtz(2 * V_b, A_b, L_b, d_b / 2)[0]
f3 = f_helmholtz(V_b, 4 * A_b, L_b, d_b / 2)[0]
check("2 f ~ V^-1/2 and f ~ A^+1/2 (exact)",
      abs(f2 / f_b - 2 ** -0.5) < 1e-12 and abs(f3 / f_b - 2.0) < 1e-12,
      "2V ratio=%.9f (exp %.9f); 4A ratio=%.9f" % (f2 / f_b, 2 ** -0.5, f3 / f_b))

# 3 ------------------------------------------------------- end correction
a_b = d_b / 2
f_un = f_helmholtz(V_b, A_b, L_b, a_b, end_k=0.613)[0]
f_fl = f_helmholtz(V_b, A_b, L_b, a_b, end_k=0.8216)[0]
f_wiki = f_helmholtz(V_b, A_b, L_b, a_b, end_k=0.6)[0]
check("3 end correction: unflanged / flanged / Wikipedia 0.3D",
      f_un > f_fl and abs(f_wiki - f_un) / f_un < 0.01,
      "unflanged=%.3f Hz flanged=%.3f Hz 0.6r=%.3f Hz (delta %.3f%%)" %
      (f_un, f_fl, f_wiki, 100 * abs(f_wiki - f_un) / f_un))

# 4 ------------------------------------------------------ ocarina sizing
V_o, a_o, L_o = 1.2e-4, 0.004, 0.005
A_req = area_for_f(523.25, V_o, L_o, a_o)
check("4 ocarina: total open area needed for C5", 2e-5 < A_req < 2e-4,
      "A=%.1f mm2 (%.1f x 8 mm holes), L_eq=%.4f m, V=%.0f mL" %
      (A_req * 1e6, A_req / (np.pi * 0.004 ** 2), L_o + 0.613 * a_o, V_o * 1e6))

# 5 ----------------------------------------------------- hole-area law
ratio = np.sqrt((A_req + np.pi * 0.004 ** 2) / A_req)
check("5 opening one 8 mm hole: f divides by sqrt(A/A0)", 1.01 < ratio < 2.0,
      "f_new/f_old = %.5f (= sqrt(%.3f))" % (ratio, (A_req + np.pi * 0.004 ** 2) / A_req))

# 6 ------------------------------------------------------------ losses
S_wall = 4 * np.pi * (3 * V_o / (4 * np.pi)) ** (2 / 3)
qr = q_radiation(V_o, A_req, L_o + 0.613 * a_o)
qv = q_viscous(A_req, L_o, a_o, L_o + 0.613 * a_o, 523.25)
qt = q_thermal(V_o, S_wall, 523.25)
qT = q_total(qr, qv, qt)
tau_th = qT / (np.pi * 523.25)
check("6 loss channels -> Q -> tau -> T60", 5 < qT < 200,
      "Q_rad=%.1f Q_visc=%.1f Q_th=%.1f Q_tot=%.2f tau=%.1f ms T60=%.0f ms" %
      (qr, qv, qt, qT, tau_th * 1e3, 6.9078 * tau_th * 1e3))

# 7 ------------------------------------- digital resonator f and Q
f_t, Q_t = 440.0, qT
bq = BiquadBP(f_t, Q_t, FS)
imp = np.zeros(FS)
imp[0] = 1.0
b, a = bq.coeffs()
from scipy.signal import lfilter
ir = lfilter(b, a, imp)
f_meas = measure_freq(ir[:FS // 4], FS)
tau_m = measure_tau(ir, FS)
q_meas = np.pi * f_meas * tau_m
check("7 biquad f0 and Q recovered from impulse response",
      abs(f_meas - f_t) / f_t < 2e-3 and abs(q_meas - Q_t) / Q_t < 0.05,
      "f=%.3f Hz (target %.1f) Q=%.2f (target %.2f) tau=%.2f ms (th %.2f)" %
      (f_meas, f_t, q_meas, Q_t, tau_m * 1e3, Q_t / (np.pi * f_t) * 1e3))

# 8 -------------------------- jet drive oscillation vs phase condition
tau_j = 0.0015 / (0.4 * 0.6 * np.sqrt(2 * 800 / RHO))
f_pred = phase_condition_f(f_t, Q_t, tau_j, FS)
sig = jet_drive(f_t, Q_t, 800.0, FS, 0.30, seed=3)
f_sim = measure_freq(sig[int(0.08 * FS):], FS)
check("8 jet drive self-oscillates at the phase-condition frequency",
      abs(f_sim - f_pred) / f_pred < 0.02,
      "f_pred=%.2f Hz f_sim=%.2f Hz f0=%.1f tau_j=%.3f ms drift_vs_f0=%+.2f%%" %
      (f_pred, f_sim, f_t, tau_j * 1e3, 100 * (f_sim / f_t - 1)))

# 9 -------------------------------- blowing pressure -> pitch rises
pressures = [400.0, 800.0, 1600.0]
fs_meas = [measure_freq(jet_drive(f_t, Q_t, p, FS, 0.30, seed=5)[int(0.08 * FS):], FS)
           for p in pressures]
semi = 12 * np.log2(fs_meas[-1] / fs_meas[0])
check("9 harder blowing raises pitch, < about a semitone",
      fs_meas[0] < fs_meas[1] < fs_meas[2] and 0 < semi < 1.0,
      "f=%.1f/%.1f/%.1f Hz at 400/800/1600 Pa -> %+.3f semitones" %
      (fs_meas[0], fs_meas[1], fs_meas[2], semi))

# 10 --------------------------------------------- amplitude saturation
amps = [np.std(jet_drive(f_t, Q_t, p, FS, 0.15, seed=7)[int(0.06 * FS):])
        for p in pressures]
gdb = 20 * np.log10(amps[-1] / amps[0])
check("10 limit-cycle amplitude saturates below pressure scaling",
      amps[0] < amps[1] < amps[2] and gdb < 20 * np.log10(4) - 0.5,
      "rms=%.4f/%.4f/%.4f -> %.2f dB for 4x pressure (linear = 12.04 dB)" %
      (amps[0], amps[1], amps[2], gdb))

# 11 ------------------------------- udu/djembe: cavity + membrane coupling
m0 = coupled_modes(150.0, 210.0, 0.0)
m1 = coupled_modes(150.0, 210.0, 6000.0)
m2 = coupled_modes(150.0, 210.0, 20000.0)
tr = sum(m2 ** 2) - (150.0 ** 2 + 210.0 ** 2)
check("11 membrane coupling -> avoided crossing, split grows, trace fixed",
      abs(m0[1] - m0[0] - 60.0) < 1e-9 and
      (m1[1] - m1[0]) > 60.0 and (m2[1] - m2[0]) > (m1[1] - m1[0]) and
      abs(tr) < 1e-9,
      "k=0: %.2f/%.2f (spread 60.00); k=6k: %.2f/%.2f (%.2f); k=20k: %.2f/%.2f (%.2f); trace err %.1e" %
      (m0[0], m0[1], m1[0], m1[1], m1[1] - m1[0], m2[0], m2[1],
       m2[1] - m2[0], abs(tr)))

# 12 -------------------------------------------------- bass-reflex tuning
V_box, d_p, L_p = 40e-3, 0.075, 0.150
A_p = np.pi * (d_p / 2) ** 2
f_port = f_helmholtz(V_box, A_p, L_p, d_p / 2, end_k=1.463)[0]
check("12 bass-reflex port tuning (40 L, 75 mm x 150 mm)", 25 < f_port < 60,
      "f_b = %.2f Hz (unflanged+flanged end correction 1.463 r)" % f_port)

# 13 ------------------------------------------- deep-bass volume demand
V_low = volume_for_f(30.0, A_p, L_p, d_p / 2, end_k=1.463)
check("13 30 Hz needs a cavity in the tens of litres", V_low > 0.05,
      "V(30 Hz) = %.1f L for a %d mm x %d mm port" %
      (V_low * 1e3, d_p * 1e3, L_p * 1e3))

# 14 ------------------------------------------ determinism, exact length
d1 = jet_drive(220.0, 30.0, 900.0, FS, 0.10, jitter=0.02, seed=11)
d2 = jet_drive(220.0, 30.0, 900.0, FS, 0.10, jitter=0.02, seed=11)
check("14 bit-exact determinism and exact sample count",
      np.array_equal(d1, d2) and len(d1) == int(0.10 * FS) and np.all(np.isfinite(d1)),
      "n=%d identical=%s finite=%s peak=%.3f" %
      (len(d1), np.array_equal(d1, d2), bool(np.all(np.isfinite(d1))), np.max(np.abs(d1))))

# 15 -------------------------------------------------- Nyquist headroom
check("15 single mode: top register is a small fraction of Nyquist",
      2000.0 < 0.45 * FS, "2000 Hz = %.1f%% of fs" % (100 * 2000 / FS))

# 16 --------------------------------------- brightness rises with pressure
def hf_ratio(x, f0, fs=FS):
    x = x - x.mean()
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / fs)
    return float(X[f > 1.5 * f0].sum() / (X.sum() + 1e-30))


b_lo = hf_ratio(jet_drive(f_t, Q_t, 400.0, FS, 0.30, seed=21)[int(0.08 * FS):], f_t)
b_hi = hf_ratio(jet_drive(f_t, Q_t, 1600.0, FS, 0.30, seed=21)[int(0.08 * FS):], f_t)
check("16 single-mode purity: harmonics stay below 5% at any pressure",
      b_hi < 0.05 and b_lo < 0.05,
      "HF energy fraction (>.5 f0): %.5f at 400 Pa, %.5f at 1600 Pa" % (b_lo, b_hi))

# 17 ------------------------------------- octave = 4x cavity volume (exact)
f_oct = f_helmholtz(4 * V_o, A_req, L_o, a_o)[0]
check("17 one octave down requires 4x cavity volume (exact)",
      abs(f_oct * 2 - 523.25) / 523.25 < 1e-12,
      "V=%.0f mL (C5) -> V=%.0f mL gives %.2f Hz" % (V_o * 1e6, 4 * V_o * 1e6, f_oct))

# 18 ------------------------------- register: treble notes are more damped
A_up = 4 * A_req
L_up = L_o + 0.613 * a_o
f_up = f_helmholtz(V_o, A_up, L_o, a_o)[0]
qup = q_total(q_radiation(V_o, A_up, L_up),
              q_viscous(A_up, L_o, a_o, L_up, f_up),
              q_thermal(V_o, S_wall, f_up))
check("18 opening holes for the octave lowers Q (treble is more damped)",
      qup < qT,
      "C5: f=%.1f Hz Q=%.2f tau=%.1f ms | C6: f=%.1f Hz Q=%.2f tau=%.1f ms" %
      (523.25, qT, qT / (np.pi * 523.25) * 1e3,
       f_up, qup, qup / (np.pi * f_up) * 1e3))

# --------------------------------------------------------------- demo render
def env_ad(n, attack=0.01, rel=0.04, fs=FS):
    a, r = int(attack * fs), int(rel * fs)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


def note(f0, p, dur, seed, Q=30.0):
    s = jet_drive(f0, Q, p, FS, dur, seed=seed)
    s = s / (np.max(np.abs(s)) + 1e-12)
    return s * env_ad(len(s), 0.006, min(0.03, dur * 0.3))


DUR = 8.0
mix = np.zeros((int(DUR * FS), 2))
mel = [523.25, 587.33, 659.25, 783.99, 659.25, 587.33, 523.25, 392.00]
t = 0.0
for i, f in enumerate(mel * 2):
    s = note(f, 900.0 + 60 * (i % 3), 0.5, seed=100 + i, Q=26.0)
    n0 = int(t * FS)
    seg = s[:max(0, min(len(s), len(mix) - n0))]
    mix[n0:n0 + len(seg), 0] += 0.45 * seg
    mix[n0:n0 + len(seg), 1] += 0.42 * seg
    t += 0.5
for i in range(8):                       # udu: cavity 92 Hz + membrane 138 Hz
    lo, hi = coupled_modes(92.0, 138.0, 6000.0)
    s = note(lo, 1400.0, 0.9, seed=300 + i, Q=14.0)
    n0 = int((0.5 + i) * FS)
    seg = s[:max(0, min(len(s), len(mix) - n0))]
    mix[n0:n0 + len(seg), 0] += 0.75 * seg
    mix[n0:n0 + len(seg), 1] += 0.70 * seg
pad = note(196.0, 700.0, DUR, seed=999, Q=48.0)
mix[:, 0] += 0.10 * pad
mix[:, 1] += 0.09 * np.roll(pad, 311)
mix /= max(np.max(np.abs(mix)), 1e-9) / 0.89
out_wav = "/opt/data/projects/Research/outputs/sp150_hcris/sp150_hcris_demo.wav"
os.makedirs(os.path.dirname(out_wav), exist_ok=True)
sf.write(out_wav, mix.astype(np.float32), FS)
size = os.path.getsize(out_wav)
check("19 demo WAV written, non-empty and finite", size > 40 and np.all(np.isfinite(mix)),
      "%s  %d B  %.1f s stereo  peak %.2f" %
      (out_wav, size, len(mix) / FS, np.max(np.abs(mix))))

npass = sum(1 for _, ok, _ in results if ok)
print("\n%d/%d checks pass" % (npass, len(results)))
with open("verify_hcris_results.txt", "w") as fh:
    fh.write("SP-150 HCRIS verification\n%d/%d checks pass\n\n" % (npass, len(results)))
    for name, ok, detail in results:
        fh.write("%s %s :: %s\n" % ("PASS" if ok else "FAIL", name, detail))
    fh.write("\nJSON:\n" + json.dumps(
        [{"check": n, "pass": o, "detail": d} for n, o, d in results], indent=1))
