"""TCC v2: head pose (lateral dx, front/back dy, yaw) + correct shuffler form."""
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq

fs = 48000; N = 1 << 17; c = 343.0; a = 0.0875; d = 1.0
th = np.deg2rad(30); f_shadow = 700.0
f = rfftfreq(N, 1 / fs)
spk = np.array([[d*np.cos(th), d*np.sin(th)], [d*np.cos(th), -d*np.sin(th)]])

def H_matrix(dx=0.0, dy=0.0, yaw=0.0):
    R = np.array([[np.cos(yaw), -np.sin(yaw)], [np.sin(yaw), np.cos(yaw)]])
    ears = (R @ np.array([[0.0, -a], [0.0, a]]).T).T + np.array([dx, dy])
    H = np.zeros((2, 2, f.size), dtype=complex)
    for e in range(2):
        for s in range(2):
            r = np.linalg.norm(spk[s] - ears[e]); w = 2j*np.pi*f
            m = (1.0/r)*np.exp(-w*r/c)
            if e != s: m = m/(1.0 + w/(2*np.pi*f_shadow))
            H[e, s] = m
    return H

def invert(H, beta):
    C = np.zeros_like(H)
    for k in range(f.size):
        h = H[:, :, k]
        C[:, :, k] = h.conj().T @ np.linalg.inv(h @ h.conj().T + beta*np.eye(2))
    return C

def apply(T, x):
    y = np.zeros_like(x)
    for o in range(2):
        for i in range(2):
            y[o] += irfft(T[o, i]*rfft(x[i], N), N)
    return y

def resid(H, C, band=(100, 16000)):
    m = (f >= band[0]) & (f <= band[1])
    o = np.zeros((2, 2))
    for k in np.where(m)[0]:
        p = H[:, :, k] @ C[:, :, k]
        o = np.maximum(o, np.abs(p - np.eye(2)))
    return 20*np.log10(o + 1e-30)

def total_err(H, C, B):
    E = apply(H, apply(C, B)); return 20*np.log10(np.sqrt(np.mean((E-B)**2))/np.sqrt(np.mean(B**2)) + 1e-30)

t = np.arange(N)/fs
sig = sum(np.sin(2*np.pi*110*2**(n/12)*t)*(0.5**(n % 3)) for n in range(8)); sig /= np.abs(sig).max()
Hv = H_matrix(); B = np.stack([irfft(Hv[e, 0]*rfft(sig, N), N) for e in range(2)])

beta = 1e-3; H = H_matrix(); C = invert(H, beta)
print(f"fs={fs} spk +/-30deg @1m head r={a*100:.2f}cm beta={beta:g}")
print("\n[A] Head pose sensitivity (C built for centred, unrotated head)")
print("   dx(cm) dy(cm) yaw(deg) | xtalk 500-8k | total err | ipsi gain err")
for dx, dy, yaw in [(0,0,0),(2,0,0),(5,0,0),(0,0,2),(0,0,5),(0,0,10),(0,5,0),(0,10,0),(5,0,5),(10,0,10)]:
    Hd = H_matrix(dx/100, dy/100, np.deg2rad(yaw))
    r = resid(Hd, C, (500, 8000)); e = total_err(Hd, C, B)
    ig = 20*np.log10(np.abs(Hd[0,0]@C[:,0] if False else (Hd[:,:, :]*C).sum(axis=1)).max()) if False else np.nan
    p = np.array([abs((Hd[:,:,k]@C[:,:,k])[0,0]) for k in np.where((f>500)&(f<8000))[0]])
    print(f"   {dx:>5} {dy:>6} {yaw:>7} | {r[1,0]:>9.2f} dB | {e:>7.2f} dB | {20*np.log10(p.max()):>6.2f}/{-20*np.log10(p.min()):>5.2f} dB")

print("\n[B] Shuffler (Cooper-Bauck) form: C = 1/(hs+ho) [sum] +- 1/(hs-ho) [diff]")
hs, ho = H[0, 0], H[1, 0]
Cs, Cd = 1/(hs+ho), 1/(hs-ho)
Csh = np.zeros_like(C)
for k in range(f.size):
    Csh[:, :, k] = np.array([[Cs[k]+Cd[k], Cs[k]-Cd[k]], [Cs[k]-Cd[k], Cs[k]+Cd[k]]])/2
d = 20*np.log10(np.abs(Csh - C).max()/np.abs(C).max())
r = resid(H, Csh, (100, 16000))
print(f"   max|Cshuffler - Cinv| = {d:.1f} dB rel. max|C|   xtalk resid L->R {r[1,0]:.1f} dB   total err {total_err(H,Csh,B):.1f} dB")

print("\n[C] Why: |hs - ho| (the cancellation denominator) by band")
for lo, hi in [(20,80),(80,200),(200,500),(500,2000),(2000,8000),(8000,16000)]:
    m = (f >= lo) & (f <= hi)
    print(f"   {lo:>5}-{hi:<5} Hz  |hs|/|ho| max {20*np.log10((np.abs(hs[m])/np.abs(ho[m])).max()):>5.1f} dB   |hs-ho| min {20*np.log10(np.abs(hs[m]-ho[m]).min()):>6.1f} dB   gain 1/(hs-ho) {20*np.log10(np.abs(Cd[m]).max()):>5.1f} dB")
