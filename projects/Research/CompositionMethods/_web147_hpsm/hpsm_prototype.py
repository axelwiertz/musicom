#!/usr/bin/env python3
"""SP-147 HPSM prototype — Handpan/Steelpan Spherical-Shell Modal Synthesis.

Verification checks (each prints PASS/FAIL + measured value):
  1.  MIDI->Hz conversion exactness (69->440, 81->880, 57->220, 60->261.6256)
  2.  Partial ratio synthesis: f0=196 Hz with r=[1,2,3,4], FFT peak detect -> ratios ~1:2:3:4
  3.  Modal decay: specified T60=2.5 s reproduced within 5%
  4.  Helmholtz port formula: f_H for handpan geometry + end correction; 50% port cover -> x0.7071
  5.  Duo-note beating: 8-cent detune at 196 Hz -> measured beat ~ f0*(2^(8/1200)-1) = 0.906 Hz
  6.  Velocity -> brightness: partial-amplitude centroid rises with strike velocity
  7.  Sizing law: clamped-plate f ~ 1/a^2 (double dimple radius -> quarter frequency)
  8.  Zero drift: output sample count exactly matches request
  9.  Determinism: same seed -> byte-identical render
 10.  Demo render: D-Kurd handpan melody + port drone -> hpsm_out.wav
"""
import json, hashlib, numpy as np
from scipy.signal import hilbert

FS = 44100
C = 343.0          # speed of sound, m/s
RHO_STEEL = 7800.0
E_STEEL = 200e9
NU = 0.3
DEN = np.sqrt(E_STEEL / (12.0 * RHO_STEEL * (1.0 - NU**2)))   # ~1532 m/s
K_CLAMP = 10.2158 / (2.0 * np.pi)                             # clamped circular plate lambda_01^2/(2pi)

def midi_to_hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)

def helmholtz(A, V, L, a, flanged=True):
    """f_H = (c/2pi) sqrt(A/(V*L_eff)); L_eff = L + 1.7a (flanged) or L + 1.22a (unflanged)."""
    corr = 1.7 if flanged else 1.22
    L_eff = L + corr * a
    return (C / (2.0 * np.pi)) * np.sqrt(A / (V * L_eff)), L_eff

def render_note(f0, ratios, amps, t60s, dur, seed=0, phase=None):
    """Modal sum: y(t)=sum_k A_k exp(-t/tau_k) sin(2pi f_k t + phi_k); tau=T60/ln(1000)."""
    n = int(round(dur * FS))
    t = np.arange(n) / FS
    rng = np.random.default_rng(seed)
    if phase is None:
        phase = rng.uniform(0, 2 * np.pi, len(ratios))
    tau = np.array(t60s) / np.log(1000.0)
    y = np.zeros(n)
    for k, (r, A, tt) in enumerate(zip(ratios, amps, tau)):
        env = np.exp(-t / tt)
        y += A * env * np.sin(2 * np.pi * r * f0 * t + phase[k])
    return y

def fft_peaks(x, fmin=30, fmax=20000, npeaks=8):
    """Dominant frequency peaks via zero-padded FFT + parabolic interp."""
    X = np.fft.rfft(x * np.hanning(len(x)), n=4 * len(x))
    freqs = np.fft.rfftfreq(4 * len(x), 1 / FS)
    mag = np.abs(X)
    idx = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    m = mag[idx]
    peaks = []
    while len(peaks) < npeaks:
        i = int(np.argmax(m))
        f = freqs[idx[i]]
        if i > 0 and i < len(m) - 1:
            # parabolic interpolation
            denom = m[i-1] - 2*m[i] + m[i+1]
            if abs(denom) > 1e-12:
                d = 0.5 * (m[i-1] - m[i+1]) / denom
                f += d * (freqs[idx[i+1]] - freqs[idx[i]])
        peaks.append(f)
        # zero out a small window around the found peak
        w = int(round(150.0 / (freqs[1]-freqs[0])))
        lo, hi = max(0, i-w), min(len(m), i+w)
        m[lo:hi] = 0
    return np.array(sorted(peaks))

def centroid(ratios, amps):
    return float(np.sum(np.array(ratios) * np.array(amps)) / np.sum(amps))

results = {}

# --- 1. MIDI -> Hz ---
checks = [(69, 440.0), (81, 880.0), (57, 220.0), (60, 261.6255653)]
ok = all(abs(midi_to_hz(m) - f) / f < 1e-9 for m, f in checks)
results["midi_hz"] = {"ok": bool(ok), "detail": [round(midi_to_hz(m), 6) for m, _ in checks]}

# --- 2. Partial ratios 1:2:3:4 ---
f0 = 196.0  # G3
dur = 2.0
y = render_note(f0, [1, 2, 3, 4], [1.0, 0.6, 0.4, 0.25], [2.5, 1.5, 1.0, 0.8], dur, seed=1)
peaks = fft_peaks(y, fmin=50, npeaks=4)
ratios_meas = peaks / peaks[0]
ratio_err = np.max(np.abs(ratios_meas - np.array([1, 2, 3, 4])) / np.array([1, 2, 3, 4]))
results["partial_ratios"] = {"ok": bool(ratio_err < 0.002), "peaks": [round(p, 2) for p in peaks],
                             "ratios": [round(r, 4) for r in ratios_meas], "max_rel_err": round(float(ratio_err), 5)}

# --- 3. T60 decay ---
# Square-law detector: LPF(y^2) = (1/2) e^{-2t/tau}; envelope = sqrt(2*LPF) = e^{-t/tau} exactly.
# Window = 2 periods at 196 Hz (= 450 samples exactly, 44100/196 = 225).
T60 = 2.5
y3 = render_note(f0, [1], [1.0], [T60], 6.0, seed=2)
w = 450
S3 = np.convolve(y3**2, np.ones(w) / w, mode="same")
env3 = np.sqrt(2.0 * S3)
ref3 = np.max(env3)
cross = int(np.argmax(env3[w:] < ref3 * 1e-3)) + w
t60_meas = cross / FS
results["t60"] = {"ok": bool(abs(t60_meas - T60) / T60 < 0.05), "spec": T60, "measured": round(t60_meas, 3)}

# --- 4. Helmholtz port ---
V = 0.020      # 20 L cavity (two shallow domes)
a = 0.05       # Gu radius 5 cm
L = 0.0012     # sheet thickness 1.2 mm
A = np.pi * a**2
fH, L_eff = helmholtz(A, V, L, a)
fH2, L_eff2 = helmholtz(A, V, L, a, flanged=False)
# 50% cover -> A halves -> f x sqrt(0.5)
fH_half, _ = helmholtz(A / 2, V, L, a)
results["helmholtz"] = {"ok": bool(80 < fH < 140 and abs(fH_half / fH - np.sqrt(0.5)) < 1e-9),
                        "V_L": V, "a_cm": a*100, "L_mm": L*1000,
                        "fH_flanged": round(float(fH), 2), "fH_unflanged": round(float(fH2), 2),
                        "L_eff_m": round(L_eff, 4),
                        "cover50_ratio": round(float(fH_half / fH), 5), "sqrt_half": round(float(np.sqrt(0.5)), 5)}

# --- 5. Duo-note beating (8 cents detune at 196 Hz) ---
# y = 2 cos(pi df t) sin(wc t); square-law + LPF -> 1 + cos(2 pi df t): peak at df.
delta_c = 8.0
f_b = f0 * (2.0 ** (delta_c / 1200.0) - 1.0)      # predicted beat
y5 = render_note(f0, [1], [1.0], [2.0], 4.0, seed=3) + render_note(f0 * 2.0**(delta_c/1200), [1], [1.0], [2.0], 4.0, seed=4)
t5 = np.arange(len(y5)) / FS
tau5 = 2.0 / np.log(1000.0)
y5n = y5 / np.exp(-t5 / tau5)          # remove the known modal decay
S5 = np.convolve(y5n**2, np.ones(w) / w, mode="same")
S5 -= np.mean(S5)
seg = S5[int(0.2*FS):int(3.8*FS)] * np.hanning(int(3.6*FS))
E = np.abs(np.fft.rfft(seg, n=8*len(seg)))
fr = np.fft.rfftfreq(8*len(seg), 1/FS)
beat_meas = fr[int(np.argmax(E[1:])) + 1]
results["beating"] = {"ok": bool(abs(beat_meas - f_b) < 0.05), "predicted": round(f_b, 4), "measured": round(float(beat_meas), 4)}

# --- 6. Velocity -> brightness ---
cents = []
for v in [0.2, 0.5, 1.0]:
    amps = [v, v**1.4 * 0.6, v**1.8 * 0.4, v**2.2 * 0.25]   # higher partials steeper in v
    cents.append(centroid([1, 2, 3, 4], amps))
results["velocity_brightness"] = {"ok": bool(cents[0] < cents[1] < cents[2]),
                                  "centroid": [round(c, 3) for c in cents]}

# --- 7. Sizing law f ~ 1/a^2 (clamped circular plate) ---
h = 0.0012
f_a5 = K_CLAMP * h * DEN / (0.05**2)
f_a10 = K_CLAMP * h * DEN / (0.10**2)
results["sizing_law"] = {"ok": bool(abs(f_a5 / f_a10 - 4.0) < 1e-9),
                         "f(a=5cm)": round(float(f_a5), 1), "f(a=10cm)": round(float(f_a10), 1),
                         "ratio": round(float(f_a5 / f_a10), 4)}

# --- 8. Zero drift ---
n_req = 5 * FS + 1234
y8 = render_note(196.0, [1, 2, 3], [1, .5, .3], [2, 1, .7], n_req / FS, seed=5)
results["zero_drift"] = {"ok": bool(len(y8) == n_req), "requested": n_req, "got": len(y8)}

# --- 9. Determinism ---
a1 = render_note(196.0, [1, 2, 3, 4], [1, .6, .4, .25], [2.5, 1.5, 1, .8], 1.0, seed=42)
a2 = render_note(196.0, [1, 2, 3, 4], [1, .6, .4, .25], [2.5, 1.5, 1, .8], 1.0, seed=42)
results["determinism"] = {"ok": bool(np.array_equal(a1, a2) and hashlib.sha256(a1.tobytes()).hexdigest() == hashlib.sha256(a2.tobytes()).hexdigest())}

# --- 10. Demo: D-Kurd handpan + port drone ---
# D Kurd layout (Ding D4, tone circle A3 Bb3 C4 E4 F4 G4 A4); ding + duos
scale = {62: "D4 ding", 57: "A3", 58: "Bb3", 60: "C4", 64: "E4", 65: "F4", 67: "G4", 69: "A4"}
melody = [62, 57, 60, 62, 64, 62, 60, 57, 58, 60, 62, 65, 67, 69, 67, 65, 62]  # 17 notes, 0.55 s apart
spb = 0.55
total = spb * len(melody) + 4.5
mix = np.zeros(int(total * FS))
rng = np.random.default_rng(7)
for i, m in enumerate(melody):
    f = midi_to_hz(m)
    v = 0.55 + 0.35 * rng.random()
    ratios = [1, 2, 3, 4]
    amps = [v, v**1.5*0.55, v**1.9*0.35, v**2.3*0.22]
    t60s = [3.2 if m == 62 else 2.4, 1.6, 1.1, 0.8]
    y = render_note(f, ratios, amps, t60s, spb + 4.0, seed=100 + i)
    onset = int(i * spb * FS)
    mix[onset:onset+len(y)] += y
# duo shimmer on the ding: second ding note detuned +4 cents
for i in [0, 3, 9]:
    f = midi_to_hz(62) * 2.0**(4/1200)
    y = render_note(f, [1, 2, 3, 4], [0.5, 0.28, 0.17, 0.1], [3.2, 1.6, 1.1, 0.8], spb + 4.0, seed=200 + i)
    onset = int(i * spb * FS)
    mix[onset:onset+len(y)] += y
# Helmholtz port drone (A2, 110 Hz) under everything, open then half-covered 2/3 in
drone = np.zeros(len(mix))
fH_d = helmholtz(np.pi*0.05**2, 0.02, 0.0012, 0.05)[0]
n_drone = len(mix)
tt = np.arange(n_drone) / FS
t60p = 6.0
envp = np.exp(-tt / (t60p / np.log(1000.0)))
drone = 0.18 * envp * np.sin(2*np.pi*fH_d*tt)
# cover after 6 s -> pitch drops by sqrt(0.6) ~ -4.4 semitones (talking-drum bend)
cover_t = 6.0
mask = tt > cover_t
fH_cov = helmholtz(np.pi*0.05**2*0.6, 0.02, 0.0012, 0.05)[0]
ph = 2*np.pi*fH_d*cover_t
drone[mask] = 0.18 * envp[mask] * np.sin(2*np.pi*fH_cov*(tt[mask]-cover_t) + ph)
mix += drone
mix = mix / np.max(np.abs(mix)) * 0.85
pcm = (mix * 32767).astype(np.int16)
import wave
with wave.open("hpsm_out.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS)
    w.writeframes(pcm.tobytes())
import os
results["demo"] = {"ok": bool(os.path.getsize("hpsm_out.wav") > 40000),
                   "bytes": os.path.getsize("hpsm_out.wav"), "sec": round(len(mix)/FS, 2),
                   "port_drone_open": round(float(fH_d), 2),
                   "port_drone_covered": round(float(fH_cov), 2),
                   "bend_semitones": round(12*np.log2(fH_cov/fH_d), 2),
                   "sha256": hashlib.sha256(pcm.tobytes()).hexdigest()[:16]}

all_ok = all(v["ok"] for v in results.values())
print(json.dumps(results, indent=1))
print("\nALL CHECKS:", "PASS" if all_ok else "FAIL")
raise SystemExit(0 if all_ok else 1)
