#!/usr/bin/env python3
"""Tune CDRB loop gain: find (mu0, reed zeta) where fundamental wins."""
import numpy as np

FS = 44100; RHO = 1.2; C = 343.0
M  = 2.0e-6; FR = 2000.0; K  = M*(2*np.pi*FR)**2; ZETA_R = 0.25
R  = 2*ZETA_R*np.sqrt(K*M)
H  = 3.0e-4; S = 1.8e-5; W = 3.0e-3; CD = 0.6
AP_MAX = 1.5*2*H*W   # blade-travel limit (physical aperture bound)

def render(pm, dur=1.2, L_eff=0.58, zpeak=5e7, nmode=14, zeta0=0.008, zeta_slope=0.002,
           seed=1, breath=0.0, y0=None):
    # modal peak pressure gain: p/u at resonance n = zpeak/n  (1/n participation)
    f0 = C/(2*L_eff)
    fn = f0*np.arange(1, nmode+1)
    zn = zeta0 + zeta_slope*np.arange(1, nmode+1)
    wn = 2*np.pi*fn
    mu = 2*zn*zpeak/np.arange(1, nmode+1)
    m1 = m2 = M; r1 = r2 = R; k1 = k2 = K
    N = int(dur*FS); dt = 1.0/FS
    x1, v1, x2, v2 = (0.0,)*4 if y0 is None else y0
    pn = np.zeros(nmode); vpn = np.zeros(nmode)
    p = np.zeros(N); u = np.zeros(N)
    for n in range(N):
        pnow = float(pn.sum())
        a1 = (S*(pm - pnow) - k1*x1 - r1*v1)/m1
        a2 = (S*(pm - pnow) - k2*x2 - r2*v2)/m2
        x1n, v1n = x1 + dt*v1, v1 + dt*a1
        x2n, v2n = x2 + dt*v2, v2 + dt*a2
        ap = W*max(2*H - x1n - x2n, 0.0)
        ap = min(ap, AP_MAX)          # physical travel clamp
        dp = pm - pnow
        un = CD*ap*np.sign(dp)*np.sqrt(2.0*abs(dp)/RHO) if ap > 0 else 0.0
        du = (un - u[n-1])/dt if n > 0 else 0.0
        for i in range(nmode):
            vpn[i] += dt*(-2*zn[i]*wn[i]*vpn[i] - wn[i]**2*pn[i] + mu[i]*du)
            pn[i]  += dt*vpn[i]
        x1, v1, x2, v2 = x1n, v1n, x2n, v2n
        p[n] = pnow; u[n] = un
    return p, u

def report(pm, zr, zpeak):
    global R, ZETA_R
    ZETA_R = zr; R = 2*zr*np.sqrt(K*M)
    p, u = render(pm, zpeak=zpeak)
    seg = p[int(0.4*FS):int(1.15*FS)]
    r = np.sqrt(np.mean(seg**2))
    X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1/FS)
    m = (fr > 60) & (fr < 4000)
    pk = fr[m][np.argmax(X[m])]
    f0 = C/(2*0.58)
    hs = []
    for k in range(1, 7):
        mm = (fr > pk*k*0.98) & (fr < pk*k*1.02)
        hs.append(float(X[mm].max()) if mm.any() else 1e-12)
    hs = np.array(hs)
    hdb = 20*np.log10(hs/np.max(hs))
    print(f"pm={pm:5.0f} zr={zr:.2f} zpeak={zpeak:.0e} | rms={r:.3e} pk={pk:6.1f} (f0={f0:.1f}) | hdb={[f'{d:.1f}' for d in hdb]}")

for zr in (0.15, 0.20, 0.30):
    for zpeak in (2e7, 5e7, 1.2e8):
        for pm in (2500.0, 4500.0, 6500.0):
            report(pm, zr, zpeak)
