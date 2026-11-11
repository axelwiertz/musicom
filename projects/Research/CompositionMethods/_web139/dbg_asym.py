#!/usr/bin/env python3
"""Reproduce check-2 (asymmetric blades) divergence."""
import numpy as np

FS = 44100; RHO = 1.2; C = 343.0
M  = 2.35e-6; FR = 2200.0; K  = M*(2*np.pi*FR)**2
ZETA_R = 0.22; R  = 2*ZETA_R*np.sqrt(K*M)
H  = 5.0e-4; S = 3.0e-5; W = 5.0e-3; CD = 0.6
L_CH = 0.012

def render(pm, dur=0.15, k1=K*1.5, k2=K*0.5, trace=False):
    m1 = m2 = M; r1 = r2 = R
    N = int(dur*FS); dt = 1.0/FS
    x1, v1, x2, v2 = 0.0, 0.0, 0.0, 0.0
    u = 0.0
    for n in range(N):
        a1 = (S*pm - k1*x1 - r1*v1)/m1
        a2 = (S*pm - k2*x2 - r2*v2)/m2
        x1n, v1n = x1 + dt*v1, v1 + dt*a1
        x2n, v2n = x2 + dt*v2, v2 + dt*a2
        x1, v1, x2, v2 = x1n, v1n, x2n, v2n
        if trace and n % 5000 == 0:
            print(f"n={n}: x1={x1:.4e} v1={v1:.4e} x2={x2:.4e} v2={v2:.4e}")
    print(f"final: x1={x1:.6e} x2={x2:.6e} | analytic {S*pm/k1:.6e}, {S*pm/k2:.6e}")
    print(f"opening {2*H - x1 - x2:.6e} vs analytic {2*H - S*pm*(1/k1+1/k2):.6e}")

render(2000.0, trace=True)
