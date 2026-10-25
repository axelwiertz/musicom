"""SP-124 parameter sweep: find the self-oscillation regime of the 4-state model.

Physical scaling fixed from cantilever geometry (steel 440 Hz-class reed):
  L=32.4 mm, h=0.25 mm, w=3 mm, E=200 GPa, rho_r=7850  ->  f1~194 Hz scale
  K = 3EI/L^3 = 68.8 N/m,  M = 33/140 rho A L = 4.5e-5 kg
  effective pressure area Af is CALIBRATED so that the static deflection at
  playing pressure equals the set y0 (the reed is a nearly-balanced valve,
  it must not be slammed wide open).
"""
import itertools
import numpy as np

FS = 48000.0
RHO, C_AIR, CD = 1.2, 343.0, 0.62


def run(f0, pm, zeta, Rrad, Vc, y0=4e-5, w=3e-3, l_s=1e-3, Ra=2e5,
        n=24000, af_ratio=1.0):
    w0 = 2 * np.pi * f0
    # geometry from the tuning law: f = 0.16154 (h/L^2) sqrt(E/rho)
    E, rho_r, h = 200e9, 7850.0, 0.25e-3
    L = np.sqrt(0.16154 * h * np.sqrt(E / rho_r) / f0)
    I = w * h ** 3 / 12.0
    K = 3 * E * I / L ** 3
    M = (33.0 / 140.0) * rho_r * w * h * L
    R = 2 * zeta * w0 * M
    Af = af_ratio * K * y0 / pm          # calibrated: y_eq ~ y0 at pm
    Cc = Vc / (RHO * C_AIR ** 2)
    gmin = 1e-6

    y, v, pc, Uprev = y0 * 0.5, 0.0, 0.0, 0.0
    out = np.empty(n)
    for i in range(n):
        g = max(y + y0, 0.0)
        dp = pm - pc
        Uor = CD * w * g * np.sign(dp) * np.sqrt(2 * abs(dp) / RHO)
        F = dp * Af
        acc = (-K * y - R * v + F) / M
        v += acc / FS
        y += v / FS
        pc += (Uor - pc / Rrad) / Cc / FS
        out[i] = (Uor - Uprev) * FS
        Uprev = Uor
    return out


def analyse(x, f0):
    x = x[int(0.15 * FS):]
    rms = float(np.sqrt(np.mean(x ** 2)))
    if rms < 1e-12:
        return rms, 0.0, 0.0
    X = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    f = np.fft.rfftfreq(x.size, 1 / FS)
    band = f < 4000
    k = int(np.argmax(X[band]))
    a, b, c = X[k - 1], X[k], X[k + 1]
    d = 0.5 * (a - c) / (a - 2 * b + c)
    fp = (k + d) * FS / x.size
    tonal = float(X[k] ** 2 / np.sum(X[band] ** 2))
    return rms, fp, tonal


if __name__ == "__main__":
    f0 = 194.0
    print(f"target f0 = {f0} Hz")
    print(f"{'zeta':>6} {'Rrad':>9} {'Vc':>9} {'af':>5} {'pm':>6} "
          f"{'rms':>10} {'fpeak':>8} {'tonal':>7}")
    for zeta, Rrad, Vc, af in itertools.product(
            (0.005, 0.02), (4e6, 4e7), (2e-6, 2e-5), (0.3, 1.0, 3.0)):
        for pm in (500.0, 1500.0, 3000.0):
            x = run(f0, pm, zeta, Rrad, Vc, af_ratio=af)
            rms, fp, tonal = analyse(x, f0)
            flag = "  <== oscillates" if (rms > 1e-6 and abs(
                1200 * np.log2(fp / f0)) < 100 and tonal > 0.3) else ""
            print(f"{zeta:6.3f} {Rrad:9.1e} {Vc:9.1e} {af:5.1f} {pm:6.0f} "
                  f"{rms:10.4e} {fp:8.1f} {tonal:7.3f}{flag}")
