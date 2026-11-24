#!/usr/bin/env python
"""MBRS — Minnaert Bubble-Resonance Synthesis. Prototype verification (SP-149).

Model: gas bubble in liquid pulsates at its natural (Minnaert) frequency.
    f0 = 1/(2*pi*a) * sqrt( (3*gamma*p + 2*sigma*(3*gamma-1)/a) / rho )
Damping (three channels): radiation, viscous, thermal boundary layer.
Renderer: glided exponentially-decaying sinusoid + cavity-collapse attack.
Run with $MUSICOM_PYTHON.
"""
import hashlib
import numpy as np
from scipy.io import wavfile

FS = 48000.0
P_ATM = 101325.0
RHO_W = 998.0
GAMMA_AIR = 1.40
SIGMA_W = 0.0728
C_W = 1480.0
NU_W = 1.0e-6
D_AIR = 2.2e-5


# ---------- core model ----------
def minnaert_f(a, p=P_ATM, rho=RHO_W, gamma=GAMMA_AIR, sigma=SIGMA_W):
    """Natural frequency (Hz) of a gas bubble of radius a (m)."""
    return np.sqrt(3.0 * gamma * p + 2.0 * sigma * (3.0 * gamma - 1.0) / a) / (
        2.0 * np.pi * a * np.sqrt(rho)
    )


def damping_parts(a, f, rho=RHO_W, nu=NU_W, c=C_W, D=D_AIR, gamma=GAMMA_AIR):
    w = 2.0 * np.pi * f
    d_rad = w * a / c                                   # ka  (acoustic radiation)
    d_visc = 4.0 * nu / (w * a * a)                     # Stokes boundary layer
    ge = gamma_eff(a, f, D=D, gamma=gamma)
    d_th = 3.0 * (ge - 1.0) * np.sqrt(2.0 * D / w) / a  # thin thermal BL
    return d_rad + d_visc + d_th, (d_rad, d_visc, d_th)


def gamma_eff(a, f=None, D=D_AIR, gamma=GAMMA_AIR, rho=RHO_W, p=P_ATM, sigma=SIGMA_W):
    """Effective polytropic exponent: isothermal (1) when the thermal boundary
    layer fills the bubble, adiabatic (gamma) when a >> delta_thermal.
    Fixed-point iteration because f0 depends on the exponent itself."""
    ge = gamma
    for _ in range(6):
        if f is None:
            f = minnaert_f(a, p=p, rho=rho, gamma=ge, sigma=sigma)
        w = 2.0 * np.pi * f
        dt = np.sqrt(2.0 * D / w)              # thermal penetration depth (m)
        ge_new = 1.0 + (gamma - 1.0) * (a / (a + dt))
        ge, f = ge_new, None
    return ge


def shape_mode_f2(a, rho=RHO_W, sigma=SIGMA_W):
    """Lamb n=2 surface (wobble) mode: w2^2 = (n-1)(n+1)(n+2) sigma/(rho a^3)."""
    return np.sqrt(12.0 * sigma / (rho * a ** 3)) / (2.0 * np.pi)


def radius_for_note(midi, p=P_ATM, rho=RHO_W, gamma=GAMMA_AIR):
    """Inverse mapping: MIDI note -> bubble radius (m)."""
    f = 440.0 * 2.0 ** ((midi - 69) / 12.0)
    c = np.sqrt(3.0 * gamma * p / rho) / (2.0 * np.pi)   # f*a constant
    return c / f


# ---------- Rayleigh-Plesset (frequency ground truth) ----------
def rp_ring(a0, n, fs_in=384000.0, gamma=GAMMA_AIR, rho=RHO_W, p=P_ATM,
            sigma=SIGMA_W, rad=True, nu=NU_W):
    """Integrate linearised Rayleigh-Plesset, return downsampled radius trace."""
    dt = 1.0 / fs_in
    pg0 = p + 2.0 * sigma / a0
    a, v = a0 * 1.001, 0.0          # small displacement off equilibrium to excite
    out = np.empty(n)
    for i in range(n):
        pg = pg0 * (a0 / a) ** (3.0 * gamma)
        acc = ((pg - p) / rho - 1.5 * v * v - 4.0 * nu * v / a
               - 2.0 * sigma / (rho * a)) / a          # R-P: LHS is a*addot
        v += acc * dt
        a += v * dt
        out[i] = a - a0
    return out


# ---------- renderer ----------
def render_bubble(a0, dur, fs=FS, glide=1.0, q=25.0, amp=1.0, seed=0,
                  p=P_ATM, rho=RHO_W, gamma=GAMMA_AIR, attack=0.0035,
                  splash=0.25, shape=True):
    """One bubble event. glide = a_end/a_start (>1 grows -> pitch falls)."""
    n = int(round(dur * fs))
    t = np.arange(n) / fs
    frac = np.linspace(0.0, 1.0, n)
    a_t = a0 * (1.0 + (glide - 1.0) * frac)
    ge0 = gamma_eff(a0[()] if np.ndim(a0) else float(a0), gamma=gamma)
    f_t = minnaert_f(a_t, p=p, rho=rho, gamma=ge0)
    phase = 2.0 * np.pi * np.cumsum(f_t) / fs
    f0 = float(f_t[0])
    tau = q / (np.pi * f0)
    env = np.exp(-t / tau)
    y = np.sin(phase) * env
    # Lamb n=2 surface ("jellyfish") wobble: sub-audio burble on big bubbles
    f2 = shape_mode_f2(float(a0))
    if shape and f2 > 20.0:
        y += 0.12 * np.sin(2.0 * np.pi * f2 * t) * np.exp(-t / (1.6 * tau))
    # cavity-collapse attack: short band-limited noise splash
    rng = np.random.default_rng(seed)
    na = max(8, int(attack * fs))
    nz = rng.standard_normal(na)
    nz = np.diff(nz, prepend=0.0)                        # crude HF tilt
    nz *= np.exp(-np.arange(na) / (0.25 * na))
    y[:na] += splash * nz / (np.max(np.abs(nz)) + 1e-12)
    # onset click-free
    y *= np.minimum(1.0, np.arange(n) / 16.0)
    return amp * y


def demo_wav(path, seed=7):
    fs = int(FS)
    total = 12.0
    y = np.zeros(int(total * fs))
    rng = np.random.default_rng(seed)
    scale = [0, 2, 3, 7, 9]                              # minor pentatonic degrees
    tcur = 0.0
    while tcur < total - 0.6:
        midi = 72 + scale[rng.integers(0, len(scale))] + 12 * rng.integers(-1, 2)
        a0 = radius_for_note(midi)
        dur = min(total - tcur, 1.8)
        glide = float(rng.uniform(0.72, 1.35))            # shrink/grow -> chirp
        ev = render_bubble(a0, dur, fs=fs, glide=glide, q=float(rng.uniform(18, 40)),
                           amp=float(rng.uniform(0.35, 1.0)), seed=int(rng.integers(0, 9999)))
        i0 = int(tcur * fs)
        seg = ev[: max(0, len(y) - i0)]
        y[i0:i0 + len(seg)] += seg
        tcur += float(rng.uniform(0.18, 0.55))
    y /= (np.max(np.abs(y)) + 1e-12)
    y *= 0.89
    st = np.stack([y, np.roll(y, 37) * 0.9], axis=1)
    wavfile.write(path, fs, (st * 32767).astype(np.int16))
    return path


# ---------- checks ----------
def main():
    res = []
    ok = lambda tag, cond, info: res.append((tag, bool(cond), info))

    # 1 Minnaert constant + 1 mm frequency
    fa = minnaert_f(1e-3, p=1e5, rho=1000.0, sigma=0.0) * 1e-3
    f1 = minnaert_f(1e-3, sigma=0.0)
    ok("1 fa constant = 3.26 m/s (p=1e5, rho=1000)", abs(fa - 3.262) < 0.01,
       f"fa={fa:.4f} m/s, f(1mm)={f1:.1f} Hz")

    # 2 inverse-radius law (exact with ST off; ST introduces a 0.08 % deviation)
    r_ratio = minnaert_f(0.5e-3, sigma=0.0) / minnaert_f(2e-3, sigma=0.0)
    r_st = minnaert_f(0.5e-3) / minnaert_f(2e-3)
    ok("2 f ~ 1/a (0.5 mm / 2 mm = 4.0)", abs(r_ratio - 4.0) < 1e-12,
       f"ratio={r_ratio:.9f} (with ST: {r_st:.6f})")

    # 3 hydrostatic pressure (depth)
    p10 = P_ATM + RHO_W * 9.81 * 10.0
    r_d = minnaert_f(1e-3, p=p10) / minnaert_f(1e-3)
    pred = np.sqrt(p10 / P_ATM)
    ok("3 depth 10 m -> f x sqrt(p/p0)", abs(r_d - pred) / pred < 1e-3,
       f"measured x{r_d:.4f} vs sqrt(p/p0)={pred:.4f}")

    # 4 surface-tension crossover (where correction = +1 %)
    def corr_pct(a):
        return 100.0 * (minnaert_f(a) / minnaert_f(a, sigma=0.0) - 1.0)
    a_lo, a_hi = 1e-5, 2e-3
    for _ in range(80):
        am = 0.5 * (a_lo + a_hi)
        if corr_pct(am) > 1.0:
            a_lo = am
        else:
            a_hi = am
    ok("4 +1% ST correction at a* ~ 0.055 mm", 0.050e-3 < a_lo < 0.062e-3,
       f"a*={a_lo*1e3:.3f} mm (corr@1mm={corr_pct(1e-3):.3f}%, corr@50um={corr_pct(5e-5):.1f}%)")

    # 5 gas identity (helium)
    r_he = minnaert_f(1e-3, gamma=1.667, sigma=0.0) / minnaert_f(1e-3, sigma=0.0)
    ok("5 helium gamma=1.667 -> x1.091", abs(r_he - np.sqrt(1.667 / 1.4)) < 1e-12,
       f"x{r_he:.4f}")

    # 6 Rayleigh-Plesset numeric vs analytic
    a0 = 2.0e-3
    tr = rp_ring(a0, 20000, fs_in=384000.0)              # 52 ms
    tr = (tr - tr.mean()) * np.hanning(len(tr))
    sp = np.abs(np.fft.rfft(tr))
    fr = np.fft.rfftfreq(len(tr), 1 / 384000.0)
    pk = fr[np.argmax(sp)]
    fa_an = minnaert_f(a0)
    ok("6 R-P ring peak vs analytic (<1%)", abs(pk - fa_an) / fa_an < 0.01,
       f"rp={pk:.1f} Hz analytic={fa_an:.1f} Hz err={100*(pk-fa_an)/fa_an:.2f}%")

    # 7 renderer pitch + decay fidelity
    a0 = 1.5e-3
    q = 30.0
    y = render_bubble(a0, 0.8, glide=1.0, q=q, splash=0.0, attack=0.0005)
    seg = y[: int(0.25 * FS)]
    win = seg * np.hanning(len(seg))
    sp = np.abs(np.fft.rfft(win, 8 * len(win)))
    fr = np.fft.rfftfreq(8 * len(win), 1 / FS)
    pk = fr[np.argmax(sp)]
    f0 = minnaert_f(a0, gamma=gamma_eff(a0))
    tau_pred = q / (np.pi * f0)
    from scipy.signal import hilbert
    env = np.abs(hilbert(y))
    tt = np.arange(len(env)) / FS
    m = (tt > 0.004) & (tt < 4.5 * tau_pred) & (env > 1e-3)
    slope = np.polyfit(tt[m], np.log(env[m]), 1)[0]
    tau_meas = -1.0 / slope
    ok("7 renderer f0 + tau = Q/(pi f0) (<5%)",
       abs(pk - f0) / f0 < 0.002 and abs(tau_meas - tau_pred) / tau_pred < 0.05,
       f"f0 {pk:.1f}/{f0:.1f} Hz ({100*(pk-f0)/f0:+.3f}%), tau {tau_meas*1e3:.2f} vs {tau_pred*1e3:.2f} ms")

    # 8 upward chirp from shrinking bubble
    # high Q is a test vector only: it keeps the event alive for the full glide
    a0, gl = 1.0e-3, 0.70
    y = render_bubble(a0, 0.25, glide=gl, q=1500.0, splash=0.0, attack=0.0005,
                      shape=False)
    ph = np.unwrap(np.angle(hilbert(y)))
    f_inst = np.gradient(ph) * FS / (2.0 * np.pi)
    env8 = np.abs(hilbert(y))
    idx = np.where((np.arange(len(y)) > 0.004 * FS) & (env8 > 0.05 * env8.max()))[0]
    k5 = max(20, len(idx) // 20)
    r_meas = float(np.median(f_inst[idx[-k5:]]) / np.median(f_inst[idx[:k5]]))
    r_pred = 1.0 / gl
    ok("8 shrink to 0.70a -> pitch x1.4286 (<3%)", abs(r_meas - r_pred) / r_pred < 0.03,
       f"measured x{r_meas:.4f} vs 1/glide={r_pred:.4f}")

    # 9 collective (cloud) resonance, lower than a single bubble
    n_b = 1000
    a_single = 1e-3
    a_cloud = a_single * n_b ** (1.0 / 3.0)
    r_c = minnaert_f(a_single, sigma=0.0) / minnaert_f(a_cloud, sigma=0.0)
    ok("9 cloud of 1000 bubbles -> f/10 (N^(1/3))", abs(r_c - 10.0) < 1e-12,
       f"f_cloud={minnaert_f(a_cloud):.1f} Hz vs single {minnaert_f(a_single):.1f} Hz, ratio {r_c:.3f}")

    # 10 determinism + exact sample count
    y1 = render_bubble(2e-3, 0.5, seed=11)
    y2 = render_bubble(2e-3, 0.5, seed=11)
    h = hashlib.sha256(y1.tobytes()).hexdigest()[:16]
    ok("10 deterministic + exact length",
       h == hashlib.sha256(y2.tobytes()).hexdigest()[:16] and len(y1) == int(round(0.5 * FS)),
       f"sha={h} n={len(y1)} expected={int(round(0.5*FS))}")

    # damping table (informational)
    # 11 isothermal limit == Leighton's small-bubble equation
    aa = 5e-5
    lhs = minnaert_f(aa, gamma=1.0)
    rhs = np.sqrt(3.0 * P_ATM / RHO_W + 4.0 * SIGMA_W / (RHO_W * aa)) / (2.0 * np.pi * aa)
    ok("11 gamma=1 limit == Leighton isothermal (4*sigma/rho*a)",
       abs(lhs - rhs) / rhs < 1e-12, f"{lhs:.2f} Hz vs {rhs:.2f} Hz")

    # 12 effective polytropic exponent transition
    g1 = gamma_eff(1e-3)
    g2 = gamma_eff(1e-6)
    ok("12 gamma_eff: 1 mm ~ adiabatic (>1.37), 1 um -> isothermal (<1.20)",
       g1 > 1.37 and g2 < 1.20, f"gamma_eff(1mm)={g1:.4f}, gamma_eff(1um)={g2:.4f}")

    # 13 Lamb n=2 surface mode: f2 < f0, and f2 ~ a^-1.5
    f2a, f2b = shape_mode_f2(2e-3), shape_mode_f2(16e-3)
    ok("13 shape mode f2 ~ a^-1.5 and below f0",
       abs(f2a / f2b - (16.0 / 2.0) ** 1.5) < 1e-9 and f2a < minnaert_f(2e-3),
       f"f2(2mm)={f2a:.1f} Hz f2(16mm)={f2b:.1f} Hz ratio={f2a/f2b:.3f} (expect 8.000)")

    print("\n  a(mm)    f0(Hz)    Q     delta_rad  delta_visc  delta_th")
    for amm in (0.1, 0.5, 1.0, 2.0, 5.0, 10.0):
        aa = amm * 1e-3
        ff = minnaert_f(aa, gamma=gamma_eff(aa))
        dt, parts = damping_parts(aa, ff)
        print(f"  {amm:5.2f} {ff:9.1f} {1/dt:6.1f}   {parts[0]:.5f}   {parts[1]:.6f}   {parts[2]:.5f}")

    print()
    npass = sum(1 for _, c, _ in res if c)
    for tag, c, info in res:
        print(f"[{'PASS' if c else 'FAIL'}] {tag}  -- {info}")
    print(f"\n{npass}/{len(res)} checks pass")

    out = demo_wav("/opt/data/projects/Research/outputs/sp149_mbrs/sp149_mbrs_demo.wav")
    import os
    print(f"demo WAV: {out}  {os.path.getsize(out)} bytes")
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
