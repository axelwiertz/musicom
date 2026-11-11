#!/usr/bin/env python3
"""Debug runaway in render()."""
import numpy as np, warnings
warnings.filterwarnings('error')

FS = 44100; RHO = 1.2; C = 343.0
M  = 2.0e-6; FR = 2000.0; K  = M*(2*np.pi*FR)**2; ZETA=0.15; R = 2*ZETA*np.sqrt(K*M)
H  = 3.0e-4; S = 1.8e-5; W = 3.0e-3; CD = 0.6

def bore_modes(f0, nmode=14, zeta0=0.008, zeta_slope=0.0015, mu0=1.0):
    if nmode == 0:
        return np.array([]), np.array([]), np.array([])
    fn = f0*np.arange(1, nmode+1)
    zn = zeta0 + zeta_slope*np.arange(1, nmode+1)
    wn = 2*np.pi*fn
    return wn, zn, mu0*wn/wn[0]

def render(pm, dur=0.12, L_eff=0.58, k1=None, k2=None, kc=0.0, seed=1, breath=0.0,
           nmode=14, mu0=1.0, y0=None, trace=False):
    f0 = C/(2*L_eff)
    wn, zn, mu = bore_modes(f0, nmode, mu0=mu0)
    k1 = K if k1 is None else k1; k2 = K if k2 is None else k2
    m1 = m2 = M; r1 = r2 = R
    N = int(dur*FS); dt = 1.0/FS
    x1, v1, x2, v2 = (0.0,)*4 if y0 is None else y0
    pn = np.zeros(nmode); vpn = np.zeros(nmode)
    p = np.zeros(N); u = np.zeros(N)
    for n in range(N):
        pnow = float(pn.sum())
        a1 = (S*(pm - pnow) - k1*x1 - r1*v1 - kc*(x1 - x2))/m1
        a2 = (S*(pm - pnow) - k2*x2 - r2*v2 - kc*(x2 - x1))/m2
        x1n, v1n = x1 + dt*v1, v1 + dt*a1
        x2n, v2n = x2 + dt*v2, v2 + dt*a2
        ap = W*max(2*H - x1n - x2n, 0.0)
        dp = pm - pnow
        un = CD*ap*np.sign(dp)*np.sqrt(2.0*abs(dp)/RHO) if ap > 0 else 0.0
        du = (un - u[n-1])/dt if n > 0 else 0.0
        for i in range(nmode):
            vpn[i] += dt*(-2*zn[i]*wn[i]*vpn[i] - wn[i]**2*pn[i] + mu[i]*du)
            pn[i]  += dt*vpn[i]
        x1, v1, x2, v2 = x1n, v1n, x2n, v2n
        p[n] = pnow; u[n] = un
        if trace and not np.isfinite(pnow):
            print(f"  diverged at n={n}: pnow={pnow}, un={un}, x={x1n:.3e}, v={v1n:.3e}")
            return p, u
    return p, u

for mu0 in (0.01, 0.1, 1.0):
    try:
        p, u = render(2000.0, mu0=mu0, trace=True)
        print(f"mu0={mu0}: max|p|={np.max(np.abs(p)):.3e} max|u|={np.max(np.abs(u)):.3e}")
    except Exception as e:
        print(f"mu0={mu0}: EXC {e}")
