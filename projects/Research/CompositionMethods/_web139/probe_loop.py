#!/usr/bin/env python3
"""Open-loop transfer function of the reed-bore loop at equilibrium."""
import numpy as np

FS = 44100; RHO = 1.2; C = 343.0
M  = 2.0e-6; FR = 2000.0; K  = M*(2*np.pi*FR)**2; ZETA_R = 0.20
R  = 2*ZETA_R*np.sqrt(K*M)
H  = 3.0e-4; S = 1.8e-5; W = 3.0e-3; CD = 0.6

def modal_z(omega, f0, nmode=14, zeta0=0.008, zeta_slope=0.002, zpeak=5e7):
    fn = f0*np.arange(1, nmode+1)
    zn = zeta0 + zeta_slope*np.arange(1, nmode+1)
    wn = 2*np.pi*fn
    mu = 2*zn*zpeak/np.arange(1, nmode+1)     # p/u at resonance n = zpeak/n
    jw = 1j*omega
    Z = np.sum(mu*jw/( (jw)**2 + 2*zn*wn*(jw) + wn**2 ))
    return Z

def loop_gain(f, pm, f0):
    w = 2*np.pi*f
    # equilibrium reed displacement per blade (p=0 at eq)
    xeq = S*pm/K
    A0 = W*(2*H - 2*xeq)
    sq = np.sqrt(2*pm/RHO)
    # flow sensitivity du/dp (total derivative incl. mechanical response at w)
    # mechanical: x(w) = S*p/(K - m w^2 + j r w)   [force = S*(pm - p); dx/dp = -S/(K-mw2+jrw)]
    mech = -S/(K - M*w*w + 1j*R*w)
    dAdp = -2*W*mech
    # du/dp = Cd*[ sqrt*dAdp*sgn + A0 * d(sqrt)/dp ], d(sqrt(2(pm-p)/rho))/dp = -1/(rho*sq)
    dudp = CD*(sq*dAdp + A0*(-1.0/(RHO*sq)))
    Z = modal_z(w, f0)
    return dudp*Z, dudp, Z

f0 = C/(2*0.58)
for pm in (1500.0, 2000.0, 2500.0, 3000.0, 4500.0):
    print(f"--- pm={pm:.0f} Pa (collapse={K*H/S:.0f})")
    for f in (296.0, 591.0, 886.0, 1999.0):
        L, dudp, Z = loop_gain(f, pm, f0)
        print(f"   f={f:6.1f}: |L|={abs(L):8.4f} phase={np.degrees(np.angle(L)):7.1f}  (dudp={dudp:+.3e}, Z={abs(Z):.3e})")
