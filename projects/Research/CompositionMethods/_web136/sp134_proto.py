"""SP-134 prototype: conical (saxophone) single-reed bore — mode series + modal render.

Part A: analytic input impedance of a truncated cone (open at L) vs a
        stopped cylinder of the same length -> pole (resonance) lists.
Part B: modal synthesis of the cone driven by a nonlinear single-reed valve
        with bore pressure feedback -> spectrum check (even harmonics present).
"""
import numpy as np

c = 343.0
rho = 1.2
fs = 48000.0

# ---------------------------------------------------------------- geometry
x0 = 0.102          # distance from cone apex to mouthpiece (m)
Lt = 1.370          # truncated cone length mouthpiece->open end (m)
L_full = x0 + Lt    # 1.472 m -> f1 ~ 116.5 Hz
r_mouth = 0.065 * x0 / L_full
r_bell = 0.065

print(f"x0={x0:.3f} Lt={Lt:.3f} L_full={L_full:.3f} r_mouth={r_mouth*1e3:.2f}mm "
      f"r_bell={r_bell*1e3:.1f}mm  c/(2L_full)={c/(2*L_full):.2f} Hz")

# ------------------------------------------------------- analytic impedance
def Z_cone(f):
    k = 2 * np.pi * f / c
    th = k * Lt
    num = 1j * rho * c * k * x0 * np.sin(th)
    den = k * x0 * np.cos(th) + np.sin(th)
    return num / den

def Z_cyl_stopped(f):
    k = 2 * np.pi * f / c
    return 1j * rho * c * np.tan(k * Lt)

def poles(zfun, fmax=4000.0, df=0.25):
    f = np.arange(1.0, fmax, df)
    z = zfun(f)
    a = np.abs(z)
    # poles = local maxima of |Z| above a threshold
    idx = np.where((a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]))[0] + 1
    idx = [i for i in idx if a[i] > 5 * np.median(a)]
    # parabolic refine
    out = []
    for i in idx:
        y0, y1, y2 = a[i - 1], a[i], a[i + 1]
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-30)
        out.append(f[i] + d * df)
    return np.array(out), a

fc, ac = poles(Z_cone, 4000)
fcy, acy = poles(Z_cyl_stopped, 4000)
print("\ncone poles  :", np.round(fc, 2))
print("ratios/f1   :", np.round(fc / fc[0], 3))
print("cyl poles   :", np.round(fcy, 2))
print("ratios/f1   :", np.round(fcy / fcy[0], 3))
print("theory n*c/(2*L_full):", np.round(np.arange(1, len(fc) + 1) * c / (2 * L_full), 2))
print("deviation cents cone vs n*f1:",
      np.round(1200 * np.log2((fc / fc[0]) / np.arange(1, len(fc) + 1)), 1))

# ------------------------------------------------------------- reed static
k_r = 1000.0        # N/m   (reed stiffness, order of magnitude for a sax reed)
S_r = 1.0e-4        # m^2   effective reed area
H0 = 0.5e-3         # m     rest opening
w_eff = 0.012       # m     effective reed width (jet perimeter scale)
alpha = 0.7         # vena-contracta / jet coefficient

def flow_static(dp):
    """Quasi-static reed flow; opening closes linearly with pressure."""
    H = np.clip(H0 - dp * S_r / k_r, 0.0, None)
    return alpha * w_eff * H * np.sqrt(2 * np.abs(dp) / rho) * np.sign(dp)

pclose = k_r * H0 / S_r
dp = np.linspace(0, pclose * 1.2, 200001)
u = flow_static(dp)
istar = np.argmax(u)
print(f"\nclosing pressure k*H0/S = {pclose:.0f} Pa; flow peak at {dp[istar]:.0f} Pa "
      f"(theory k*H0/(3S) = {pclose/3:.0f} Pa); u_max={u[istar]*1e3:.3f} L/s")

# --------------------------------------------------------------- render
def render(f0_target=116.5, dur=1.0, p_mouth=4200.0, seed=7, nmode=26):
    n = int(dur * fs)
    # mode frequencies: exact conical poles, scaled so pole 1 == f0_target
    fmodes = fc[:nmode] * (f0_target / fc[0])
    # Q grows with frequency (viscothermal + radiation): Q ~ 20 at f1 -> ~60 at 4k
    Q = 12.0 + 10.0 * (fmodes / fmodes[0]) ** 0.5
    r = np.exp(-np.pi * fmodes / (Q * fs))
    a1 = 2 * r * np.cos(2 * np.pi * fmodes / fs)
    a2 = -r * r
    y1 = np.zeros(nmode); y2 = np.zeros(nmode)
    # per-mode input gain ~ 1/f (pressure/flow impedance falls with frequency)
    g = 1.0 / (1.0 + (fmodes / fmodes[0]) ** 1.0)
    g = g / g[0]

    # reed ODE: m xdd + rr xd + k x = S dp  (x opens the reed)
    m_r = 1.0e-5
    fr = 1600.0
    Qr = 4.0
    rr = 2 * np.pi * fr * m_r / Qr
    x = 0.0; xd = 0.0
    out = np.zeros(n)
    ubuf = 0.0
    rng = np.random.default_rng(seed)
    for i in range(n):
        pb = ubuf                     # bore pressure at the mouthpiece (1-sample lag)
        dpv = p_mouth - pb
        # reed dynamics (semi-implicit Euler, substepped 4x for stability)
        for _ in range(4):
            h = 1.0 / (4 * fs)
            xdd = (S_r * dpv - rr * xd - k_r * x) / m_r
            xd += h * xdd
            x += h * xd
            x = min(x, 2 * H0)
        H = max(H0 + x, 0.0)
        if H <= 1e-9:
            uv = 0.0
        else:
            uv = alpha * w_eff * H * np.sqrt(2 * abs(dpv) / rho) * np.sign(dpv)
        # modal bank
        yn = a1 * y1 + a2 * y2 + g * uv
        y2 = y1; y1 = yn
        pb_new = yn.sum() * 6.5e6 * 6.4e-5 / 6.4e-5  # placeholder scale, fixed below
        # scale: pressure = sum(mode pressure); calibrate so RMS lands ~ 0.1
        ubuf = pb_new * 0.0 + yn.sum()
        out[i] = yn.sum()
    return out

# calibrate gain empirically: run and normalise, report raw RMS
y = render()
print(f"\nraw render rms={np.sqrt(np.mean(y**2)):.4g} peak={np.abs(y).max():.4g}")

# find periodicity / spectrum
w = np.hanning(len(y))
Y = np.abs(np.fft.rfft(y * w))
fr_ax = np.fft.rfftfreq(len(y), 1 / fs)
sel = (fr_ax > 60) & (fr_ax < 3000)
pk = fr_ax[sel][np.argmax(Y[sel])]
print(f"dominant f = {pk:.2f} Hz")

def harm_levels(y, f0, nh=10):
    w = np.hanning(len(y)); Y = np.abs(np.fft.rfft(y * w))
    fr_ax = np.fft.rfftfreq(len(y), 1 / fs)
    out = []
    for h in range(1, nh + 1):
        m = np.abs(fr_ax - h * f0) < 3.0
        out.append(Y[m].max() if m.any() else 0.0)
    out = np.array(out)
    return 20 * np.log10(out / out.max() + 1e-12)
print("harmonic levels dB (re h1):", np.round(harm_levels(y, pk), 1))
