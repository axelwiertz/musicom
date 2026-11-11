#!/usr/bin/env python3
"""
SP-139 CDRB — Conical Double-Reed Bore Synthesis verification prototype (final).

Physics:
  * Two cantilever blades (double reed) clamped at the staple, tips facing;
    mouth pressure pushes BOTH blades inward (closing the channel between them):
        m x_i'' + r x_i' + k x_i = S (pm - p) - kc (x_i - x_j)
    (no rigid lay — the aperture is the gap between the two moving blades)
  * Reed channel aperture:  A = W (2H - x1 - x2),  clamped to [0, 2WH]
  * Flow with channel INERTANCE (aerodynamic negative damping, the
    sustaining mechanism at operating pressures):
        L_a du/dt = (pm - p) - R_q(u) u,   R_q = rho/(2 Cd^2 A^2) |u|,
        L_a = rho L_ch / A
  * Conical bore = modal bank at the exact cone pole locations
        f_n = n c / (2 L_eff)  (COMPLETE harmonic series — the conical signature),
    p_n'' + 2 zeta_n w_n p_n' + w_n^2 p_n = mu_n du/dt,  mu_n = 2 zeta_n w_n Z/n,
    reed-end pressure p = sum_n p_n feeds back into reed force + flow.
  * RK2 for the reed, explicit Euler for modes, 44100 Hz, deterministic per seed.

Checks (12):
  1  static opening vs pm matches  A = W(2H - S pm (1/k1 + 1/k2))    (symmetric)
  2  asymmetric blades (k1 != k2) match the two-spring series formula
  3  collapse pressure pm_coll = k H / S (measured vs analytic)
  4  reed free resonance at f_r = (1/2pi) sqrt(k/m)
  5  self-oscillation onset: sustained RMS jumps at a threshold ~3-4 kPa
  6  pitch: dominant peak at f0 = c/2L_eff
  7  COMPLETE harmonic series + conical-vs-stopped-cylinder contrast
  8  brightness: spectral centroid rises with blowing pressure
  9  nonlinear valve: sinusoidal pressure drive -> even+odd harmonics in flow
  10 determinism: same seed -> bit-identical buffer
  11 chanter variant: L_eff -> f0 ~ 466 Hz
  12 WAV artifacts + sample-count preservation
"""
import numpy as np, wave, hashlib, os

FS = 44100; RHO = 1.2; C = 343.0
M  = 2.35e-6; FR = 2200.0; K  = M*(2*np.pi*FR)**2     # ~450 N/m
ZETA_R = 0.22; R  = 2*ZETA_R*np.sqrt(K*M)
H  = 5.0e-4; S = 3.0e-5; W = 5.0e-3; CD = 0.6
L_CH = 0.012
X_OPEN = -1.2*H; X_CLOS = H
ZPEAK = 4e7; NMODE = 14; ZETA0 = 0.008; ZETA_SLOPE = 0.004

def render(pm, dur=1.2, L_eff=0.58, zpeak=ZPEAK, nmode=NMODE, k1=None, k2=None, kc=0.0,
           seed=1, breath=0.0, y0=None, odd_only=False, p_ext=None, out_wav=None):
    """Render one note; return (p, u, x1, x2)."""
    rng = np.random.default_rng(seed)
    f0 = C/(2*L_eff)
    nn = np.arange(1, nmode+1)
    fn = f0*nn
    if odd_only:                                    # stopped-cylinder series (clarinet-like)
        fn = f0*(2*nn - 1)
    zn = ZETA0 + ZETA_SLOPE*nn
    wn = 2*np.pi*fn
    mu = 2*zn*wn*zpeak/nn
    k1 = K if k1 is None else k1; k2 = K if k2 is None else k2
    m1 = m2 = M; r1 = r2 = R
    N = int(dur*FS); dt = 1.0/FS
    x1, v1, x2, v2 = (0.0,)*4 if y0 is None else y0
    u = 0.0
    pn = np.zeros(nmode); vpn = np.zeros(nmode)
    p = np.zeros(N); U = np.zeros(N); X1 = np.zeros(N); X2 = np.zeros(N)
    umax = CD*(2*W*H)*np.sqrt(2*pm/RHO)*2.0
    for n in range(N):
        pnow = float(pn.sum())
        if p_ext is not None:
            pnow += p_ext(n*dt)
        a1 = (S*(pm - pnow) - k1*x1 - r1*v1 - kc*(x1 - x2))/m1
        a2 = (S*(pm - pnow) - k2*x2 - r2*v2 - kc*(x2 - x1))/m2
        # velocity-first semi-implicit (symplectic) Euler: stable for stiff blades
        v1n = v1 + dt*a1; x1n = x1 + dt*v1n
        v2n = v2 + dt*a2; x2n = x2 + dt*v2n
        # collision / travel limits (dead-stop, no bounce)
        if x1n > X_CLOS: x1n, v1n = X_CLOS, 0.0
        elif x1n < X_OPEN: x1n, v1n = X_OPEN, 0.0
        if x2n > X_CLOS: x2n, v2n = X_CLOS, 0.0
        elif x2n < X_OPEN: x2n, v2n = X_OPEN, 0.0
        ap = min(max(W*(2*H - x1n - x2n), 0.0), 2*W*H)
        La = RHO*L_CH/max(ap, 1e-12)
        Rq = RHO/(2*CD*CD*ap*ap)*abs(u) if ap > 0 else 0.0
        du = (pm - pnow - Rq*u)/La
        un = u + dt*du
        if breath > 0:
            un += breath*rng.standard_normal()*np.sqrt(max(ap, 0.0))
        if un > umax: un = umax
        elif un < -umax: un = -umax
        dudt = (un - u)/dt
        u = un
        for i in range(nmode):
            vpn[i] += dt*(-2*zn[i]*wn[i]*vpn[i] - wn[i]**2*pn[i] + mu[i]*dudt)
            pn[i]  += dt*vpn[i]
        x1, v1, x2, v2 = x1n, v1n, x2n, v2n
        p[n] = pnow; U[n] = un; X1[n] = x1; X2[n] = x2
    if out_wav:
        y = p/np.max(np.abs(p)) if np.max(np.abs(p)) > 0 else p
        w = wave.open(out_wav, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS)
        w.writeframes((np.clip(y*0.9, -1, 1)*32767).astype('<i2').tobytes()); w.close()
    return p, U, X1, X2

def rms(x, lo, hi): return float(np.sqrt(np.mean(x[lo:hi]**2)))
def centroid(x, fmax=8000.0):
    X = np.abs(np.fft.rfft(x)); fr = np.fft.rfftfreq(len(x), 1/FS)
    m = fr <= fmax
    return float(np.sum(fr[m]*X[m])/np.sum(X[m]))
def peak_harmonics(seg, pk, kk=range(1, 7)):
    X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1/FS)
    hs = []
    for k in kk:
        m = (fr > pk*k*0.98) & (fr < pk*k*1.02)
        hs.append(float(X[m].max()) if m.any() else 1e-12)
    return np.array(hs)

# ===== 1. static opening vs pm (symmetric blades, no bore) =====
pm = 2000.0
p, u, x1, x2 = render(pm, dur=0.15, nmode=0, y0=(0,0,0,0))
open_meas = 2*H - x1[-1] - x2[-1]
open_anl  = 2*H - S*pm*(1/K + 1/K)
c1 = abs(open_meas - open_anl)/open_anl < 0.02

# ===== 2. asymmetric blades =====
kA, kB = K*1.5, K*0.5
p, u, x1, x2 = render(pm, dur=0.15, nmode=0, k1=kA, k2=kB, y0=(0,0,0,0))
open2 = 2*H - x1[-1] - x2[-1]
open2a = 2*H - S*pm*(1/kA + 1/kB)
c2 = abs(open2 - open2a)/open2a < 0.02

# ===== 3. collapse pressure =====
opens = []
for pp in np.linspace(1000.0, 9000.0, 9):
    _, _, x1, x2 = render(pp, dur=0.15, nmode=0, y0=(0,0,0,0))
    opens.append(2*H - x1[-1] - x2[-1])
opens = np.array(opens)
pms = np.linspace(1000.0, 9000.0, 9)
idx = np.argmax(opens <= 0.02*(2*H))
pm_coll_meas = float(pms[idx]) if opens[-1] <= 0.02*(2*H) else float('nan')
c3 = abs(pm_coll_meas - K*H/S)/(K*H/S) < 0.08

# ===== 4. reed free resonance =====
p, u, x1, x2 = render(0.0, dur=0.4, nmode=0, y0=(1e-4, 0.0, 1e-4, 0.0))
seg = x1[:int(0.05*FS)]
X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1/FS)
pk_r = fr[np.argmax(X)]
c4 = abs(pk_r - FR)/FR < 0.05

# ===== 5. self-oscillation onset =====
def sustained(pm):
    p, *_ = render(pm, dur=1.2)
    return rms(p, int(0.5*FS), int(1.1*FS))
floor = sustained(2500.0)
r3000 = sustained(3000.0); r3500 = sustained(3500.0); r5000 = sustained(5000.0)
thresh = 3000.0 if r3000 > 20*floor else (3500.0 if r3500 > 20*floor else None)
c5 = (thresh is not None) and (r5000 > 50*floor) and (thresh <= 3500)

# ===== 6. pitch =====
pA, *_ = render(5000.0, dur=1.2)
segA = pA[int(0.4*FS):int(1.15*FS)]
X = np.abs(np.fft.rfft(segA)); fr = np.fft.rfftfreq(len(segA), 1/FS)
f0 = C/(2*0.58)
m = (fr > 60) & (fr < 4000)
pk = fr[m][np.argmax(X[m])]
c6 = abs(pk - f0)/f0 < 0.01

# ===== 7. complete harmonic series + conical vs stopped-cylinder =====
pB, *_ = render(6500.0, dur=1.2)
segB = pB[int(0.4*FS):int(1.15*FS)]
hB = peak_harmonics(segB, pk)
hBdb = 20*np.log10(hB/np.max(hB))
pCy, *_ = render(6500.0, dur=1.2, odd_only=True)
segCy = pCy[int(0.4*FS):int(1.15*FS)]
X = np.abs(np.fft.rfft(segCy)); fr = np.fft.rfftfreq(len(segCy), 1/FS)
m = (fr > 60) & (fr < 4000)
pkcy = fr[m][np.argmax(X[m])]
hCy = peak_harmonics(segCy, pkcy)
hCy2db = 20*np.log10(hCy[1]/np.max(hCy))
c7 = (hBdb[1] > -30.0) and all(hBdb[k] > -45.0 for k in range(1, 6)) and (hBdb[1] - hCy2db > 20.0)

# ===== 8. brightness rises with pressure =====
pC, *_ = render(4000.0, dur=1.2)
segC = pC[int(0.4*FS):int(1.15*FS)]
cA, cB = centroid(segC), centroid(segB)
c8 = cB > cA*1.3

# ===== 9. nonlinear valve harmonic generation =====
def bern_harm():
    fdrive, A0, pm = 300.0, 1400.0, 4000.0
    p, u, *_ = render(pm, dur=0.6, nmode=0, p_ext=lambda t: A0*np.sin(2*np.pi*fdrive*t))
    seg = u[int(0.2*FS):]
    X = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1/FS)
    def amp(f):
        m = (fr > f*0.97) & (fr < f*1.03); return float(X[m].max()) if m.any() else 1e-12
    h1, h2, h3 = amp(fdrive), amp(2*fdrive), amp(3*fdrive)
    return 20*np.log10(h2/h1), 20*np.log10(h3/h1)
bh2, bh3 = bern_harm()
c9 = bh2 > -30.0 and bh3 > -45.0

# ===== 10. determinism =====
p1, *_ = render(5000.0, dur=0.8, seed=7, breath=1e-6)
p2, *_ = render(5000.0, dur=0.8, seed=7, breath=1e-6)
p3, *_ = render(5000.0, dur=0.8, seed=8, breath=1e-6)
c10 = hashlib.sha256(p1.tobytes()).digest() == hashlib.sha256(p2.tobytes()).digest() \
      and hashlib.sha256(p1.tobytes()).digest() != hashlib.sha256(p3.tobytes()).digest()

# ===== 11. chanter variant =====
Lc = C/(2*466.0)
pc, *_ = render(5200.0, dur=1.0, L_eff=Lc)
segc = pc[int(0.4*FS):int(0.95*FS)]
Xc = np.abs(np.fft.rfft(segc)); frc = np.fft.rfftfreq(len(segc), 1/FS)
mc = (frc > 60) & (frc < 3000)
pkc = frc[mc][np.argmax(Xc[mc])]
c11 = abs(pkc - 466.0)/466.0 < 0.02 and rms(pc, int(0.5*FS), int(0.9*FS)) > 20*rms(pc, 0, int(0.1*FS))

# ===== 12. WAV artifacts + sample-count =====
w1 = 'sp139_demo_oboe.wav'
w2 = 'sp139_demo_chanter.wav'
render(5000.0, dur=1.6, breath=1e-6, seed=11, out_wav=w1)
render(5200.0, dur=1.2, breath=1e-6, seed=12, L_eff=Lc, out_wav=w2)
s1, s2 = os.path.getsize(w1), os.path.getsize(w2)
c12 = s1 > 40 and s2 > 40 and s1 == 1.6*FS*2 + 44 and s2 == 1.2*FS*2 + 44

results = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
names = ['static-opening', 'asym-blades', 'collapse', 'reed-res', 'onset',
         'pitch', 'complete-series+contrast', 'brightness', 'valve-harms',
         'determinism', 'chanter-pitch', 'wav-artifacts']
print(f"PM_COLL analytic {K*H/S:.0f} Pa, measured {pm_coll_meas:.0f} Pa")
print(f"opening@2kPa: meas {open_meas*1e3:.3f} mm vs anl {open_anl*1e3:.3f} mm")
print(f"asym opening: meas {open2*1e3:.3f} mm vs anl {open2a*1e3:.3f} mm")
print(f"reed resonance: meas {pk_r:.0f} Hz vs {FR} Hz")
print(f"onset: floor(2.5k) {floor:.2e}, 3.0k {r3000:.2e}, 3.5k {r3500:.2e}, 5.0k {r5000:.2e} -> threshold {thresh} Pa")
print(f"pitch: {pk:.1f} Hz vs f0 {f0:.1f} Hz ({1200*np.log2(pk/f0):+.1f} cents)")
print(f"conical hdB: {[f'{d:.1f}' for d in hBdb]}")
print(f"cylinder h2: {hCy2db:.1f} dB | h2 contrast {hBdb[1]-hCy2db:.1f} dB")
print(f"centroid @4kPa {cA:.0f} Hz, @6.5kPa {cB:.0f} Hz (ratio {cB/max(cA,1):.2f})")
print(f"valve harmonics: h2 {bh2:.1f} dB, h3 {bh3:.1f} dB")
print(f"chanter: {pkc:.1f} Hz vs 466 Hz ({1200*np.log2(pkc/466):+.1f} cents)")
print(f"WAV sizes {s1} / {s2} B")
print()
for n, r in zip(names, results):
    print(f"  [{'PASS' if r else 'FAIL'}] {n}")
print(f"\n{sum(results)}/{len(results)} checks pass")
raise SystemExit(0 if all(results) else 1)
