"""SP-133 reference prototype — Theremin Heterodyne Synthesis (THS) v2.

Verifies the Skeldon-1998 physics model + phase-continuous digital render:
  1. Heterodyne identity:  sin(w1 t) * sin(w2 t)  --LP-->  (1/2) cos((w1-w2) t)
     (RF chosen BELOW Nyquist so the sum is removable; real 170 kHz RF aliases — pitfall)
  2. Antenna self-capacitance  C_A(inf) ~ 7 pF  (h=0.5 m rod, d=0.01 m, k=0.4)
  3. Hand proximity capacitance  dC_A(x=10 cm) ~ 0.4 pF  (image-antenna /10 model)
  4. Beat-vs-distance curve f_T(x) with raw Colpitts law — range + mid linearity
  5. 0.01 pF -> one beat octave at 1 MHz RF / C2 = 10 pF (end-to-end)
  6. Phase-accumulator render: exact constant-tone frequency, gliss + vibrato, no clicks
  7. Aliasing demonstration: RF 170 kHz product sampled at 48 kHz contaminates LP output
"""
import numpy as np

FS = 48000
EPS0 = 8.854e-12
PI = np.pi

# ---------------- 1. heterodyne identity (RF below Nyquist) ----------------
N = FS  # 1 s
t = np.arange(N) / FS
f1, f2 = 8000.0, 9000.0            # both < 24 kHz: no aliasing
sig = np.sin(2 * PI * f1 * t) * np.sin(2 * PI * f2 * t)
spec = np.fft.rfft(sig)
freqs = np.fft.rfftfreq(N, 1 / FS)
spec[freqs > 5000] = 0             # keep only the difference band
lp = np.fft.irfft(spec, N)
seg = lp[FS // 4: 3 * FS // 4]     # steady 0.5 s
zc = np.where(np.diff(np.signbit(seg)))[0].size
f_meas = zc / (2 * 0.5)
print(f"[1] heterodyne LP beat = {f_meas:.0f} Hz (theory |f2-f1| = 1000 Hz)")

# ---------------- 2. antenna self-capacitance ----------------
def C_antenna(h, d, k=0.4):
    return 2 * PI * EPS0 * h / (np.log(2 * h / d) - k)

CA_inf = C_antenna(0.5, 0.01)
print(f"[2] C_A(inf) = {CA_inf*1e12:.2f} pF (Skeldon eq.6 -> ~7 pF)")

# ---------------- 3. hand proximity capacitance ----------------
def dC_hand(x, h=0.5, d=0.01):
    return PI * EPS0 * h / (10 * np.log(4 * x / d))

print(f"[3] dC_A(0.10 m) = {dC_hand(0.10)*1e12:.2f} pF (Skeldon eq.7 -> 0.4 pF)")

# ---------------- 4. beat vs distance (raw Colpitts law) ----------------
# oscillator: f = 1/(2 pi sqrt(L C_eq)),  C_eq = C1*C2/(C1+C2), C2 = C_fix + C_A(x)
# tune so f_pitch ~ 1 MHz with C2 ~ 40 pF at x=1 m (playing band keeps beat < ~9 kHz)
L = 280e-6
C1 = 220e-12
C_fix = 33e-12

def f_pitch(x):
    C2 = C_fix + C_antenna(0.5, 0.01) + dC_hand(x)
    C_eq = C1 * C2 / (C1 + C2)
    return 1.0 / (2 * PI * np.sqrt(L * C_eq))

F_REF = f_pitch(1.0)
xs = np.linspace(0.06, 1.0, 300)
fT = F_REF - f_pitch(xs)
lo, hi = 0.15, 0.80                       # mid band for linearity fit
m = (xs >= lo) & (xs <= hi)
lin = np.polyfit(xs[m], fT[m], 1)
resid = np.abs(fT[m] - np.polyval(lin, xs[m]))
print(f"[4] f_pitch@1m = {F_REF/1e3:.0f} kHz; beat x=1 m -> {fT[-1]:.0f} Hz, "
      f"x=0.06 m -> {fT[0]:.0f} Hz; beat at 10 cm = {np.interp(0.10, xs, fT):.0f} Hz")
print(f"    mid-range [{lo},{hi}] m: linear fit slope {lin[0]:.0f} Hz/m, "
      f"max|resid| {resid.max():.0f} Hz over {fT[m].min():.0f}-{fT[m].max():.0f} Hz")
print(f"    steepening near antenna: d(fT)/dx at 0.08 m vs 0.6 m = "
      f"{np.gradient(fT, xs)[np.argmin(abs(xs-0.08))]/np.gradient(fT, xs)[np.argmin(abs(xs-0.6))]:.1f}x")

# ---------------- 5. 0.01 pF -> one beat octave (end-to-end) ----------------
# operating point: choose x0 so beat = 500 Hz; add 0.01 pF of C -> beat should ~ 1000 Hz
x0 = float(np.interp(500.0, fT[::-1], xs[::-1]))   # invert fT(x)
C2a = C_fix + C_antenna(0.5, 0.01) + dC_hand(x0)
C2b = C2a + 0.01e-12
Ceq_a = C1 * C2a / (C1 + C2a); Ceq_b = C1 * C2b / (C1 + C2b)
fa = 1.0 / (2 * PI * np.sqrt(L * Ceq_a)); fb = 1.0 / (2 * PI * np.sqrt(L * Ceq_b))
print(f"[5] op point x0={x0:.3f} m: beat 500.0 -> {F_REF-fb:.0f} Hz after +0.01 pF "
      f"(ratio {(F_REF-fb)/500:.2f} ~ octave)")

# ---------------- 6. phase-continuous render ----------------
def render(f_nom, dur, gliss_to=None, vib_rate=5.5, vib_depth=0.012, vol=None, seed=0):
    n = int(dur * FS)
    tt = np.arange(n) / FS
    f_car = f_nom * np.ones(n) if gliss_to is None else f_nom * (gliss_to / f_nom) ** (tt / dur)
    f_car *= 1 + vib_depth * np.sin(2 * PI * vib_rate * tt + seed)
    y = np.sin(2 * PI * np.cumsum(f_car) / FS)
    if vol is None:
        vol = np.ones(n); a = int(0.02 * FS)
        vol[:a] = np.linspace(0, 1, a); vol[-a:] = np.linspace(1, 0, a)
    return (y * vol).astype(np.float32)

def freq_of(yy, t0, win):
    a = int((t0 - win / 2) * FS); b = int((t0 + win / 2) * FS)
    assert a >= 0 and b <= len(yy), "window out of range"
    z = np.where(np.diff(np.signbit(yy[a:b])))[0].size
    return z / 2 / win

yA = render(440.0, 1.0)
print(f"[6] const 440 Hz tone: meas {freq_of(yA, 0.5, 0.5):.1f} Hz; "
      f"max step {np.abs(np.diff(yA)).max():.4f} (bound {2*PI*440/FS:.4f})")
yG = render(220.0, 2.0, gliss_to=440.0, vib_rate=5.5, vib_depth=0.012)
print(f"    gliss 220->440+vib: meas@0.3s {freq_of(yG, 0.3, 0.2):.0f} Hz (want ~{220*2**(0.3/2):.0f}), "
      f"meas@1.7s {freq_of(yG, 1.7, 0.2):.0f} Hz (want ~{220*2**(1.7/2):.0f}); len {len(yG)} == {int(2.0*FS)}")

# ---------------- 7. aliasing pitfall with real RF (170 kHz @ 48 kHz) ----------------
sig2 = np.sin(2 * PI * 170000 * t) * np.sin(2 * PI * 171000 * t)
spec2 = np.fft.rfft(sig2)
spec2[freqs > 5000] = 0
lp2 = np.fft.irfft(spec2, N)
seg2 = lp2[FS // 4: 3 * FS // 4]
zc2 = np.where(np.diff(np.signbit(seg2)))[0].size
print(f"[7] RF 170/171 kHz product LP'd at 48 kHz: measured {zc2/(2*0.5):.0f} Hz "
      f"(theory 1000 Hz; alias of sum 341 kHz -> 5 kHz contaminates)")

np.save('/opt/data/repos/musicom/projects/Research/outputs/sp133_proto/sp133_gliss.npy', yG)
print("ALL CHECKS DONE")
