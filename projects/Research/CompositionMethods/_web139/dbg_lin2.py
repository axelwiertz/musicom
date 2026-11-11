#!/usr/bin/env python3
"""Stability test: r computed from symmetric K but k1 = 1.5K (the dbg_asym combo)."""
import numpy as np

m = 2.35e-6; K = 450.0; k = K*1.5
ZETA_R = 0.22
r = 2*ZETA_R*np.sqrt(K*m)     # <-- damping from K, not k
w = np.sqrt(k/m)
dt = 1/44100.0
print(f"omega={w:.1f} w*dt={w*dt:.4f} delta*dt={(r/m)*dt:.4f} zeta_eff={r/(2*np.sqrt(k*m)):.3f}")
det = 1 - (r/m)*dt
print(f"|lambda| = sqrt(det) = {np.sqrt(det):.5f}")

x, v = 0.0, 0.0
Spm = 3e-5*2000.0
grow = 1.0
for n in range(1, 7000):
    a = (Spm - k*x - r*v)/m
    x, v = x + dt*v, v + dt*a
    if n in (1, 100, 1000, 2000, 3000, 4000, 5000):
        print(f"n={n:5d} x={x:.6e} v={v:.6e}")
print(f"equilibrium {Spm/k:.6e}")
