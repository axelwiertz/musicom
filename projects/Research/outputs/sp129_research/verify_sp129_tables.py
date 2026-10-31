"""Final TCC numbers for the SP-129 entry (corrected interaural-axis geometry)."""
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
exec(open('/opt/data/tmp_tcc/tcc_v2.py').read().split('print(f"fs=')[0])

print("[1] beta sweep (band 100 Hz-16 kHz)")
print("  beta      max|C| dB   xtalk L->R dB   total err dB")
for beta in [0.0, 1e-8, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1]:
    H = H_matrix(); C = invert(H, beta)
    r = resid(H, C, (100, 16000)); e = total_err(H, C, B)
    print(f"  {beta:<9.0e} {20*np.log10(np.abs(C).max()):>8.2f}   {r[1,0]:>10.2f}      {e:>7.2f}")

beta = 1e-3
H = H_matrix(); C = invert(H, beta)
print(f"\n[2] per-band suppression (beta={beta:g})")
for lo, hi in [(20,80),(80,200),(200,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000)]:
    r = resid(H, C, (lo, hi))
    print(f"  {lo:>5}-{hi:<5} Hz  {r[1,0]:>8.2f} dB   (max|C| {20*np.log10(np.abs(C[:,:, (f>=lo)&(f<=hi)]).max()):>6.2f} dB)")

print("\n[3] pose sensitivity (C for centred head), band 500 Hz-8 kHz")
for dx, dy, yaw in [(0,0,0),(1,0,0),(2,0,0),(5,0,0),(0,0,2),(0,0,5),(0,0,10),(0,2,0),(0,5,0),(0,-5,0),(2,0,2)]:
    Hd = H_matrix(dx/100, dy/100, np.deg2rad(yaw))
    r = resid(Hd, C, (500, 8000)); e = total_err(Hd, C, B)
    print(f"  dx={dx:>4}cm dy={dy:>4}cm yaw={yaw:>3}deg -> {r[1,0]:>8.2f} dB  err {e:>7.2f} dB")

print("\n[4] difference-filter gain cap (bass management)")
hs, ho = H[0,0], H[1,0]; Cs, Cd = 1/(hs+ho), 1/(hs-ho)
for gmax in [30, 18, 12, 6]:
    Cd2 = Cd.copy(); lim = 10**(gmax/20)
    Cd2 = np.where(np.abs(Cd2) > lim, lim*np.exp(1j*np.angle(Cd2)), Cd2)
    C2 = np.zeros_like(C)
    for k in range(f.size):
        C2[:,:,k] = np.array([[Cs[k]+Cd2[k], Cs[k]-Cd2[k]],[Cs[k]-Cd2[k], Cs[k]+Cd2[k]]])/2
    rl = resid(H, C2, (20,200)); rh = resid(H, C2, (500,8000)); rw = resid(H, C2, (20,16000))
    print(f"  cap +{gmax:>2} dB  20-200Hz {rl[1,0]:>7.2f} dB   500-8k {rh[1,0]:>7.2f} dB   worst {rw[1,0]:>7.2f} dB")

print("\n[5] shuffler vs matrix inverse (beta=0)")
C0 = invert(H, 0.0)
Csh = np.zeros_like(C0)
for k in range(f.size):
    Csh[:,:,k] = np.array([[Cs[k]+Cd[k], Cs[k]-Cd[k]],[Cs[k]-Cd[k], Cs[k]+Cd[k]]])/2
print(f"  xtalk resid {resid(H, Csh, (20,16000))[1,0]:.1f} dB   total err {total_err(H, Csh, B):.1f} dB")

print("\n[6] delays / taps")
ears = np.array([[0.0,-a],[0.0,a]])
for s in range(2):
    for e in range(2):
        rr = np.linalg.norm(spk[s]-ears[e])
        print(f"  spk{s}->ear{e}: r={rr:.4f} m  tau={rr/c*1e3:.3f} ms  ({rr/c*fs:.1f} samples)")
