#!/usr/bin/env python3
"""Tune CDRB v2: channel inertance + correct modal scaling + realistic oboe geometry."""
import numpy as np

FS = 44100; RHO = 1.2; C = 343.0
# realistic oboe reed: total tip aperture ~1 mm (2H), blade w 5mm, eff area 3e-5, f_r 2200 Hz
M  = 2.35e-6; FR = 2200.0; K  = M*(2*np.pi*FR)**2     # ~450 N/m
ZETA_R = 0.20; R  = 2*ZETA_R*np.sqrt(K*M)
H  = 5.0e-4; S = 3.0e-5; W = 5.0e-3; CD = 0.6
L_CH = 0.012          # blade/channel length
AP_MAX = 1.5*2*H*W

def render(pm, dur=1.2, L_eff=0.58, zpeak=2e7, nmode=14, zeta0=0.008, zeta_slope=0.002,
           seed=1, breath=0.0, y0=None):
    f0 = C/(2*L_eff)
    fn = f0*np.arange(1, nmode+1)
    zn = zeta0 + zeta_slope*np.arange(1, nmode+1)
    wn = 2*np.pi*fn
    mu = 2*zn*wn*zpeak/np.arange(1, nmode+1)          # Z_res = zpeak/n
    m1 = m2 = M; r1 = r2 = R; k1 = k2 = K
    N = int(dur*FS); dt = 1.0/FS
    x1, v1, x2, v2 = (0.0,)*4 if y0 is None else y0
    u = 0.0
    pn = np.zeros(nmode); vpn = np.zeros(nmode)
    p = np.zeros(N); U = np.zeros(N)
    for n in range(N):
        pnow = float(pn.sum())
        a1 = (S*(pm - pnow) - k1*x1 - r1*v1)/m1
        a2 = (S*(pm - pnow) - k2*x2 - r2*v2)/m2
        x1n, v1n = x1 + dt*v1, v1 + dt*a1
        x2n, v2n = x2 + dt*v2, v2 + dt*a2
        ap = min(max(W*(2*H - x1n - x2n), 0.0), AP_MAX)
        # channel inertance flow: L_a du/dt = (pm - p) - R_q(u) u
        La = RHO*L_CH/max(ap, 1e-12)
        Rq = RHO/(2*CD*CD*ap*ap)*abs(u) if ap > 0 else 0.0
        du = (pm - pnow - Rq*u)/La
        un = u + dt*du
        u = un
        # bore modes driven by du/dt
        dudt = du
        for i in range(nmode):
            vpn[i] += dt*(-2*zn[i]*wn[i]*vpn[i] - wn[i]**2*pn[i] + mu[i]*dudt)
            pn[i]  += dt*vpn[i]
        x1, v1, x2, v2 = x1n, v1n, x2n, v2n
        p[n] = pnow; U[n] = un
    return p, U

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

for zr in (0.15, 0.25):
    for zpeak in (5e6, 2e7, 8e7):
        for pm in (2500.0, 4500.0, 6500.0):
            report(pm, zr, zpeak)
