# SP-132 — Rotary Speaker Doppler–Amplitude-Modulation Spatialization (RSDA)

**Layer:** absolute (sound production)
**Family:** Post-Processing / DSP — spatialization with intrinsic pitch modulation
**Candidate code path:** `sound/effects/rotary_speaker.py`
**Status:** documented + reference prototype verified (`projects/Research/outputs/sp132_proto/`)

---

## 1. What the method is

A rotary (Leslie) cabinet is not a modulation effect bolted onto a mix — it is a
*mechanical spatializer*. A compression driver feeds a horn that physically
rotates above an acoustic crossover; a woofer fires into a rotating drum below
it. A microphone at distance `R` therefore receives a **moving source**:

```
y(t) = g(t) · x(t − τp(t)),        τp(t) = d(t)/c
```

Everything characteristic of the sound is a consequence of `d(t)`:

| Observable | Cause |
|---|---|
| pitch warble ("tremolo" at 6.67 Hz) | Doppler: `frx = f0 (1 − vr/c)` |
| level pumping | inverse distance `R/d` + horn directivity lobe |
| "wooden/scooped" colour | louvre reflection comb, path length varying |
| stereo width | two mics at different bearings see different `d(t)` |
| gear-change gesture | motor inertia `dω/dt = (ωt − ω)/τm` |
| bass/treble split behaviour | 800 Hz LR4 crossover, two independent rotors |

The method is **absolute**: buffers in, buffers out, no events, no symbolic
state. Output length equals input length (only a read pointer moves), so
zero-drift and loop-seam invariants are preserved; the delay line adds a fixed
latency that must be pre-rolled.

---

## 2. Extended mechanics

### 2.1 Rotor kinematics

```
ω_target = 2π·rpm/60
dω/dt    = (ω_target − ω)/τm          (first-order servo, motor + belt inertia)
θ(t)     = θ0 + ∫ ω ds
```

Hardware set points (Leslie 122 class):

| rotor | chorale | tremolo | radius (model) |
|---|---|---|---|
| treble horn | 50 rpm | 400 rpm | 0.10 m |
| bass drum | 40 rpm | 340 rpm | 0.15 m |

Measured 10–90 % rise, 48 kHz, 50 → 400 rpm:

| τm (s) | t10–90 % (s) | settle 1 % (s) |
|---|---|---|
| 0.20 | 0.439 | 0.89 |
| 0.35 | 0.769 | 1.57 |
| 0.60 | 1.318 | 2.68 |

A hardware-authentic chorale↔tremolo change therefore takes ≈0.8–1.5 s and is
audible as an *accelerando*, not a switch.

### 2.2 Geometry

Source position `p(t) = r(cos θ, sin θ)`; mic at distance `R`, bearing `φ`:

```
d(t)   = sqrt(R² + r² − 2Rr cos(θ(t) − φ))
τp(t)  = d(t)/c,      c = 343 m/s
```

Measured path swing, `R = 0.50 m`:

| rotor | r | d range | swing |
|---|---|---|---|
| horn | 0.10 | 0.400–0.600 m | 0.583 ms |
| drum | 0.15 | 0.350–0.650 m | 0.875 ms |

### 2.3 Doppler

Differentiate the received phase `φ(t) = 2π f0 (t − τp(t))`:

```
frx(t) = f0 (1 − τp'(t)) = f0 (1 − vr(t)/c)
vr(t)  = R r ω sin(θ − φ) / d(t)          (peak ≈ rω for R ≫ r)
```

Peak deviation in cents, independent of `f0`:

```
Δcents = 1200 log2(1 + rω/c)
```

Measured (pure 440 Hz tone, AM and 1/d disabled, 4-point Lagrange delay):

| rpm | v_peak (m/s) | theory (¢) | measured (¢) | error |
|---|---|---|---|---|
| 40 | 0.42 | 2.11 | 2.19 | +3.7 % |
| 50 | 0.52 | 2.64 | 2.68 | +1.6 % |
| 340 | 3.56 | 17.88 | 18.23 | +2.0 % |
| 400 | 4.19 | 21.01 | 21.45 | +2.1 % |
| 800 | 8.38 | 41.78 | 42.97 | +2.9 % |

Consequences:

- deviation is **constant in cents** ⇒ in Hz it is proportional to `f`. At
  1 kHz and 400 rpm, `Δf = 12.2 Hz` at `fm = 6.67 Hz` ⇒ FM index `β ≈ 1.83`
  (≈3 significant sidebands). Emulating with an f0 LFO in Hz is wrong.
- the modulation rate *is* the rotation rate: 0.83 Hz (chorale) or 6.67 Hz
  (tremolo).

### 2.4 Amplitude

```
g(t) = (R / d(t)) · D(θ),     D(θ) = 10^(−(A/20)·(1 − cos(θ − φ))/2)
```

`D` is exactly `A` dB deep over one revolution; the inverse-distance term adds
more:

| A (dB) | measured total AM |
|---|---|
| 3 | 6.52 |
| 6 | 9.52 |
| 10 | 13.52 |
| 15 | 18.52 |

Pure distance term at `R = 0.5`, `r = 0.10`: **3.52 dB**. Practical values:
horn 8–12 dB, drum 4–7 dB.

The 122's horn pair is mechanically symmetric with **one throat blocked**, so
the lobe is single-sided and AM occurs at `1×` rotation. Two open throats give
`2×` and an octave-high tremolo — a classic emulation error.

### 2.5 Crossover

Linkwitz-Riley 4th order = two cascaded Butterworth-2 sections per band at
`fc = 800 Hz`. Verified: `|Hlp + Hhp| = 1.000000` from 20 Hz to 20 kHz
(max deviation 0.0000 dB), each band −6.02 dB at `fc`. Apply **before** the
rotors; delay-match the bands or the crossover point wanders with rotor angle.

### 2.6 Cabinet reflection

A louvre/box reflection at 2.5 ms with gain 0.8:

```
H(ω) = 1 + 0.8 e^(−jωτ),   τ = 2.5 ms
nulls at odd multiples of 1/(2τ) = 200 Hz
depth 20 log10((1−0.8)/(1+0.8)) = −19.1 dB
```

Measured deepest null 199 Hz, depth −19.1 dB. In the real cabinet this tap
*sweeps* with rotor angle — model as a second time-varying tap, never static.

### 2.7 Two-mic capture

Mics at `φ = ±90°`, `R = 0.5 m`: measured ITD swing **0.583 ms**, inter-mic
correlation **+0.334**. That decorrelation is the width; mono fold-down keeps
the warble and loses the comb.

---

## 3. Reference implementation (NumPy / SciPy sketch)

```python
import numpy as np
from scipy.signal import butter, sosfilt

C = 343.0

def rotor(n, fs, rpm, r, R, phi=0.0, tau=0.35, rpm0=None, theta0=0.0):
    """Angular position, distance-to-mic and delay (s) for one rotor."""
    w_t = 2*np.pi*rpm/60.0
    w = np.empty(n)
    w[0] = 2*np.pi*(rpm0 if rpm0 is not None else rpm)/60.0
    a = 1.0 - np.exp(-1.0/(fs*tau))
    for i in range(1, n):                 # motor inertia (vectorise via lfilter)
        w[i] = w[i-1] + (w_t - w[i-1])*a
    th = theta0 + np.cumsum(w)/fs
    d = np.sqrt(R*R + r*r - 2*R*r*np.cos(th - phi))
    return th, d, d/C, w

def frac_delay(x, D):
    """4-point Lagrange fractional delay, D in samples."""
    idx = np.arange(len(x)) - D
    i0 = np.floor(idx).astype(int); f = idx - i0
    xp = np.pad(x, (4, 4), mode="edge"); i0 += 4
    return (xp[i0-1]*(-f*(f-1)*(f-2)/6.0)
            + xp[i0]*(3*(f+1)*(f-1)*(f-2)/6.0)
            + xp[i0+1]*(-3*(f+1)*f*(f-2)/6.0)
            + xp[i0+2]*((f+1)*f*(f-1)/6.0))

def lr4(fc, fs, kind):
    sos = butter(2, fc/(fs/2), btype=kind, output="sos")
    return np.concatenate([sos, sos])

def rotary(x, fs=48000, fc=800.0, r_horn=0.10, r_drum=0.15, R=0.5,
           rpm_horn=400, rpm_drum=340, am_horn=10.0, am_drum=6.0,
           phi=0.0, tau=0.35, refl=(0.0025, 0.8)):
    lp, hp = lr4(fc, fs, "low"), lr4(fc, fs, "high")
    out = np.zeros_like(x)
    for band, r, rpm, am in ((sosfilt(lp, x), r_drum, rpm_drum, am_drum),
                             (sosfilt(hp, x), r_horn, rpm_horn, am_horn)):
        th, d, dl, _ = rotor(len(x), fs, rpm, r, R, phi=phi, tau=tau)
        g = (R/d) * 10.0**(-am*(1-np.cos(th-phi))/2.0/20.0)
        out += frac_delay(band, dl*fs) * g
    dr, gr = refl                              # sweeping reflection tap
    th, d, dl, _ = rotor(len(x), fs, rpm_horn, r_horn, R, phi=phi, tau=tau)
    tap = dl*fs + dr*fs*(1.0 + 0.05*np.cos(th))
    out += gr*0.5*frac_delay(out, tap)
    return out

# automation: 2 rotors x N mics, stereo
L = rotary(x, phi=+np.pi/2)
R_ = rotary(x, phi=-np.pi/2)
stereo = np.stack([L, R_], axis=1)
```

Numerical notes:

- `ω` can be generated with `scipy.signal.lfilter([a], [1, a-1], ones)` —
  the Python loop above is only for clarity (`a = 1 − e^(−1/(fs·τ))`).
- Delay modulation rate `Ḋ ≈ 0.012 samples/sample` at 400 rpm, so
  interpolation error appears as slow gain ripple, not aliasing.
- Nonzero latency `≈ (R + r)/c ≈ 1.75 ms`; pre-roll that much and do not
  sample-align dry/wet by zero.

---

## 4. Musical behaviour

| Element | Effect |
|---|---|
| PITCH | ±2.6 ¢ @ 0.83 Hz (chorale) → ±21 ¢ @ 6.67 Hz (tremolo), constant in cents, `∝ f` in Hz; twin rotors detuned by a few rpm beat into a physical chorus |
| RHYTHM | rotation period 1.20 s / 0.15 s; speed change = 0.77 s accelerando usable as fill/lift/section marker; tempo-lock via `rpm = 60·BPM·k/n_rev` |
| HARMONY | no new partials; per-partial phase/level divergence thickens chords without adding voices; splitting a chord across 800 Hz makes only one register warble |
| STRUCTURE | rotor state machine (stop/chorale/tremolo + τm) is the form: reprise = return to chorale, drop = coast-down, build = speed ramp outrunning the arrangement |
| TEXTURE | two bands × two rotors × two AM depths, plus a moving comb; `R/r` trades AM against Doppler |

---

## 5. UnitMatrix integration

- **Rows = feeds.** Per row `{routing: horn|drum|full, rpm_horn, rpm_drum, am_db, r, R, mic_deg, phase0, seed}`. Per-row cabinets give N independent warbles; a shared bus reproduces the real single-cabinet coherence.
- **Columns = rotor state.** `{state, transition_tau, target_rpm}`; `ω` integrates across the seam so speed changes are continuous (no click, no phase reset).
- **Cells = MusicUnit.** No event writes. Velocity → AM depth; note length vs rotation period decides whether a note contains 0, 1 or many warbles.
- **Dispatch:** `produce(midi_path, method="SP-132", params={...})`; chain: source → EQ (SP-007) → **RSDA** → room (SP-009/032/075) → dynamics (SP-008/107) → loudness (SP-126) → dither (SP-122).

---

## 6. Pitfalls (short list)

1. AM biases Hilbert-based Doppler measurement (6.41 ¢ vs 2.11 ¢ at 40 rpm) — verify with AM off.
2. Doppler ≠ vibrato: modulate delay, never f0.
3. FM and AM are one geometric gesture; only `r/R` sets their ratio.
4. Blocked second horn throat ⇒ AM at 1× rotation, not 2×.
5. Crossover before rotors, bands delay-matched (flat sum verified).
6. Reflection tap must sweep with rotor angle.
7. Cubic (or better) interpolation; per-block delay updates = zipper.
8. Fixed latency ≈ 1.75 ms; pre-roll; length unchanged.
9. Measured AM = `A + 3.5 dB`; `A` is not the final depth.
10. ±90° mic pair only +0.33 correlated — audition mono.
11. Not a pan law (SP-119) and not a phaser (SP-106): it changes arrival time.
12. Horn and drum have separate motors; do not drive both from one rpm knob.

---

## 7. References

1. Doppler, C. (1842). Über das farbige Licht der Doppelsterne. *Abh. königl. böhm. Ges. Wiss.* II(2), 465–482.
2. Leslie, D. J. US Patents 2,489,653 (1949); 3,036,153; 3,157,246 — rotary tremolo device / dual-rotor cabinet.
3. Wikipedia, "Leslie speaker", rev. 2026-10-30 — 122 architecture, dual horn with one blocked throat, 50/400 rpm horn and 40/340 rpm drum, chorale/tremolo switching.
4. Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley — fractional-delay interpolation, Doppler simulation, modulation effects.
5. Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K/CCRMA — variable delay lines, group-delay error.
6. Linkwitz, S. H., & Riley, S. (1976). Active crossover networks for noncoincident drivers. *JAES* 24(1), 2–8.
7. Morse, P. M., & Ingard, K. U. (1968). *Theoretical Acoustics*. McGraw-Hill — moving-source radiation, directivity, near/far field.
8. Moorer, J. A. (1983). Signal processing approach to simulating horn responses. *JAES*.
9. Prototype + measurements: `projects/Research/outputs/sp132_proto/leslie_proto.py`, `crossover_check.py`.
