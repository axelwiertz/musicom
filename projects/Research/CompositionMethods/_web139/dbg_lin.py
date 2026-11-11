#!/usr/bin/env python3
"""Linear stability test of semi-implicit Euler for the stiff blade."""
import numpy as np

m = 2.35e-6; k = 450.0*1.5; zeta = 0.22
w = np.sqrt(k/m); r = 2*zeta*np.sqrt(k*m)
dt = 1/44100.0
print(f"omega={w:.1f} rad/s  w*dt={w*dt:.4f}  delta*dt={(r/m)*dt:.4f}")
print(f"analytic |lambda| = {np.sqrt(1-(r/m)*dt):.5f}")

x, v = 0.0, 0.0
Spm = 3e-5*2000.0
for n in range(1, 7000):
    a = (Spm - k*x - r*v)/m
    xn, vn = x + dt*v, v + dt*a
    x, v = xn, vn
    if n in (1, 100, 1000, 3000, 5000, 6615):
        print(f"n={n:5d} x={x:.6e} v={v:.6e}")
print(f"equilibrium {Spm/k:.6e}")
