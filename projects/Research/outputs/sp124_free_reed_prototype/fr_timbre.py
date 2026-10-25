"""SP-124: is the naive lumped model a buzz or a sine? measure y swing vs set."""
import numpy as np
import fr_sweep as S

FS = S.FS
RHO, C_AIR, CD = S.RHO, S.C_AIR, S.CD


def run_trace(f0, pm, zeta, Rrad, Vc, y0=4e-5, w=3e-3, af_ratio=1.0, n=24000):
    E, rho_r, h = 200e9, 7850.0, 0.25e-3
    L = np.sqrt(0.16154 * h * np.sqrt(E / rho_r) / f0)
    I = w * h ** 3 / 12.0
    K = 3 * E * I / L ** 3
    M = (33.0 / 140.0) * rho_r * w * h * L
    w0 = 2 * np.pi * f0
    R = 2 * zeta * w0 * M
    Af = af_ratio * K * y0 / pm
    Cc = Vc / (RHO * C_AIR ** 2)
    y, v, pc, Uprev = y0 * 0.5, 0.0, 0.0, 0.0
    ys = np.empty(n)
    out = np.empty(n)
    for i in range(n):
        g = max(y + y0, 0.0)
        dp = pm - pc
        U = CD * w * g * np.sign(dp) * np.sqrt(2 * abs(dp) / RHO)
        acc = (-K * y - R * v + dp * Af) / M
        v += acc / FS
        y += v / FS
        pc += (U - pc / Rrad) / Cc / FS
        out[i] = (U - Uprev) * FS
        Uprev = U
        ys[i] = y
    return out, ys, y0


def harm_report(out, f0):
    seg = out[int(0.2 * FS):int(0.2 * FS) + 16384]
    X = np.abs(np.fft.rfft(seg * np.hanning(seg.size))) * 2 / np.hanning(seg.size).sum()
    f = np.fft.rfftfreq(seg.size, 1 / FS)
    fpk = f[np.argmax(X * (f < 400))]
    amps = np.array([X[np.argmin(np.abs(f - k * fpk))] for k in range(1, 13)])
    amps /= amps[0]
    return fpk, amps


for (zeta, Rrad, Vc, af, pm) in [(0.005, 4e6, 2e-5, 3.0, 3000.0),
                                 (0.02, 4e7, 2e-5, 1.0, 1500.0),
                                 (0.002, 4e6, 2e-5, 10.0, 3000.0)]:
    out, ys, y0 = run_trace(194.0, pm, zeta, Rrad, Vc, af_ratio=af)
    fpk, amps = harm_report(out, 194.0)
    print(f"zeta={zeta} af={af} pm={pm:.0f}  y_swing={ys[-4000:].max()-ys[-4000:].min():.2e} m "
          f"(set y0={y0:.1e}, ratio {(ys[-4000:].max()-ys[-4000:].min())/y0:.1f}x)  "
          f"f={fpk:.1f} Hz  tonal_h2={amps[1]:.3f} h3={amps[2]:.3f} h5={amps[4]:.3f} "
          f"THD={np.sqrt((amps[1:]**2).sum()):.3f}")
