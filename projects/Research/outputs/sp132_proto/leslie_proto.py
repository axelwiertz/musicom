"""Reference prototype v2: Rotary Speaker (Leslie) Doppler-AM spatialization.

Isolates the Doppler (delay modulation) from the amplitude modulation so the
measured frequency deviation can be compared against theory:
    f_rx(t) = f0 * (1 - v_rad(t)/c),  v_rad = d(d)/dt
"""
import numpy as np
from scipy.signal import hilbert, butter, sosfilt

FS = 48000.0
C = 343.0

def rotor(n, rpm, r, R, phi_mic=0.0, tau_spin=None, rpm_start=None):
    w_t = 2*np.pi*rpm/60.0
    if tau_spin is None:
        w = np.full(n, w_t)
    else:
        w = np.empty(n)
        w[0] = 2*np.pi*(rpm_start or rpm)/60.0
        a = 1.0 - np.exp(-1.0/(FS*tau_spin))
        for i in range(1, n):
            w[i] = w[i-1] + (w_t - w[i-1])*a
    th = np.cumsum(w)/FS
    d = np.sqrt(R*R + r*r - 2*R*r*np.cos(th - phi_mic))
    return th, d, w

def frac_delay(x, D):
    idx = np.arange(len(x)) - D*FS
    i0 = np.floor(idx).astype(int); f = idx - i0
    xp = np.pad(x, (4, 4), mode="edge"); i0 = i0 + 4
    return (xp[i0-1]*(-f*(f-1)*(f-2)/6.0)
            + xp[i0]*(3*(f+1)*(f-1)*(f-2)/6.0)
            + xp[i0+1]*(-3*(f+1)*f*(f-2)/6.0)
            + xp[i0+2]*((f+1)*f*(f-1)/6.0))

def am_curve(th, phi_mic, depth_db):
    return 10.0 ** (-depth_db*(1.0-np.cos(th-phi_mic))/2.0/20.0)

def cents(y, f0):
    sos = butter(4, [f0*0.7/(FS/2), f0*1.4/(FS/2)], btype="band", output="sos")
    z = hilbert(sosfilt(sos, y))
    f = np.gradient(np.unwrap(np.angle(z)))*FS/(2*np.pi)
    m = len(f)//4
    return 1200*np.log2(f[m:-m]/f0)

n = int(3.0*FS); t = np.arange(n)/FS; f0 = 440.0
tone = np.sin(2*np.pi*f0*t)

print("=== A. Doppler only (pure tone, no AM, no 1/d): meas vs theory ===")
print(f"{'rpm':>5} {'vpk m/s':>8} {'theory c':>9} {'meas c':>8} {'err %':>7}")
for rpm in (40, 50, 340, 400, 800):
    th, d, w = rotor(n, rpm, 0.10, 0.50)
    # analytic radial velocity: v = d'(t) computed from the trajectory
    v = np.gradient(d)*FS
    y = frac_delay(tone, d/C)
    meas = cents(y, f0)
    # theory: f = f0(1 - v/c) -> deviation at peak v
    th_c = 1200*np.abs(np.log2(1 - v.min()/C))
    print(f"{rpm:>5} {np.abs(v).max():>8.2f} {th_c:>9.2f} {np.abs(meas).max():>8.2f} "
          f"{100*(np.abs(meas).max()-th_c)/th_c:>7.1f}")

print("\n=== B. AM depth of the gain curve (horn depth param -> measured dB) ===")
for depth in (3, 6, 10, 15):
    th, d, w = rotor(n, 400, 0.10, 0.50)
    g = am_curve(th, 0.0, depth) * (0.5/d)     # directivity x inverse distance
    print(f"  depth_param={depth:>2} dB -> meas AM = {20*np.log10(g.max()/g.min()):5.2f} dB")

print("\n=== C. Inverse-distance term alone (R/d, r=0.10 R=0.50) ===")
th, d, w = rotor(n, 400, 0.10, 0.50)
print(f"  0.5/d range {0.5/d.max():.4f}..{0.5/d.min():.4f} -> "
      f"{20*np.log10(d.max()/d.min()):.2f} dB of pure distance AM")

print("\n=== D. Spin-up chorale->tremolo, tau = 0.2/0.35/0.6 s ===")
for tau in (0.2, 0.35, 0.6):
    _, d, w = rotor(n, 400, 0.10, 0.50, tau_spin=tau, rpm_start=50)
    rp = w*60/(2*np.pi)
    t10 = np.argmax(rp >= 85)/FS; t90 = np.argmax(rp >= 365)/FS
    ts = np.argmax(np.abs(rp-400) <= 4)/FS
    print(f"  tau={tau:.2f}s  t10-90%={t90-t10:.3f}s  settle1%={ts:.2f}s")

print("\n=== E. Two-mic stereo (phi = +/-90 deg), correlation & delay diff ===")
th, dL, w = rotor(n, 400, 0.10, 0.50, phi_mic=np.pi/2)
_, dR, _ = rotor(n, 400, 0.10, 0.50, phi_mic=-np.pi/2)
yL = frac_delay(tone, dL/C)*am_curve(th, np.pi/2, 10.0)
yR = frac_delay(tone, dR/C)*am_curve(th, -np.pi/2, 10.0)
print(f"  correlation={np.sum(yL*yR)/np.sqrt(np.sum(yL**2)*np.sum(yR**2)):+.3f}  "
      f"ITD swing max={(np.abs(dL-dR).max())/C*1e3:.3f} ms")

print("\n=== F. Delay swing & Doppler across hardware presets ===")
for name, rpm, r in (("horn chorale", 50, .10), ("horn tremolo", 400, .10),
                     ("drum chorale", 40, .15), ("drum tremolo", 340, .15)):
    th, d, w = rotor(n, rpm, r, 0.50)
    v = np.abs(np.gradient(d)*FS).max()
    print(f"  {name:<13} rpm={rpm:>4} r={r:.2f}: swing={(d.max()-d.min())/C*1e3:.3f} ms "
          f"v_pk={v:.2f} m/s doppler=+/-{1200*np.log2(1+v/C):.1f} cents")
