# Sound Production Method SP-131 — Two-Mass Vocal Fold Physical Modeling Synthesis (TMVF)

**ID:** SP-131 · **Acronym:** TMVF · **Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines (physical self-oscillating voice source / glottal excitation)
**Candidate code path:** `sound/synthesis/vocal_fold_model.py` (new module) → consumed by `sound/synthesis/kelly_lochbaum.py` (SP-067 tract) or any formant/LPC resonator downstream
**Dispatch:** `workflows/musicom_workflow.py::produce(method="SP-131", params={...})`
**Status:** documented + numerically verified 2026-11-02 (NumPy, 48 kHz, 0.6 s buffers; script `projects/Research/outputs/sp131_research/verify_sp131_tmvf.py`)

---

## 1. One-line definition

A synthesis engine that renders the human voice source as the classic Ishizaka–Flanagan
**two-mass vocal fold model** — two coupled nonlinear masses per fold driven by subglottal
pressure through a Bernoulli glottal flow, self-oscillating with no vibratory input — and
emits the emergent glottal volume velocity $u_g(t)$ (unipolar, skewed, −7.7 dB/oct flow
slope, measured) as the excitation for any tract resonator (SP-067 KLAT, SP-015 formants,
SP-028 LPC).

---

## 2. Why TMVF is not one of the existing methods

| Method | Voice source | Kind |
|---|---|---|
| SP-004 Formant Vocal Synthesis | external neural engines (ACE/DiffSinger) | learned synthesis |
| SP-015 Formant Vowel Filter | **parametric** glottal pulse-train | source-filter, abstract formants |
| SP-025 FOF | cosine wave-packets | time-domain formant |
| SP-028 LPC | impulse/noise excitation | all-pole model |
| SP-038 VOSIM | sin² chirp trains | formant via chirps |
| SP-067 KLAT | **parametric** Rosenberg/LF glottal pulse | physical *tract*, parametric *source* |
| SP-127 STRAIGHT | analysis-derived excitation | analysis-resynthesis |
| **SP-131 TMVF** | **physical self-oscillating two-mass folds** | physical *source* (Ishizaka–Flanagan 1972) |

The DB's voice methods all *assume* a glottal pulse; TMVF *is* the glottis. It is the
missing physical-source stage: SP-067's own doc explicitly notes its glottal source is a
parametric Rosenberg/LF pulse train — TMVF replaces exactly that block with a
self-oscillating laryngeal model, so pitch, skew, closed quotient, registers, and
breathiness *emerge* instead of being drawn by hand.

---

## 3. History and lineage

- **1958 — van den Berg, "Myoelastic-Aerodynamic Theory of Voice Production":** the
  mechanism. No neural drive vibrates the folds; the *aerodynamic* pressure in the glottis
  sustains the oscillation. Bernoulli's law: as air accelerates through the narrowing
  glottis, pressure drops; the drop pattern over the fold surface pushes the folds open
  during the convergent phase and pulls them closed during the divergent phase — energy is
  injected every cycle, and the collision stops the closure. This is why the larynx is a
  *relaxation oscillator with a fluid coupling*, not a driven resonator.
- **1968 — Flanagan & Landgraf, "Self-Oscillating Source for Vocal-Tract Synthesizers":**
  the first usable single-mass self-oscillating source (one mass per fold, one spring) —
  proved the computational feasibility of the aerodynamic drive.
- **1972 — Ishizaka & Flanagan, "Synthesis of Voiced Sounds From a Two-Mass Model of the
  Vocal Cords" (BSTJ 51(6), 1233–1268):** the canonical two-mass model. The single-mass
  model can oscillate but its waveform is too sinusoidal; two coupled masses reproduce the
  *skewed* glottal flow pulse (slow opening, fast closure) that gives voiced sound its
  characteristic spectrum. The 1972 parameter set remains the field default.
- **1985 — Fant, Liljencrants & Lin (LF model):** the *parametric* four-parameter glottal
  flow — the analytic shape that TMVF's emergent flow approximates. LF is the "what",
  TMVF is the "why": the LF pulse shape falls out of the two-mass physics.
- **1988 — Titze:** eigenmode analysis of small-amplitude fold oscillation; threshold
  pressure law for phonation onset; the f0 ≈ √(k/m)/2π relation with aerodynamic loading.
- **1995 — Story & Titze:** the 16-mass body-cover model; the register (chest/falsetto)
  mechanism as parameter regimes.

---

## 4. Technical mechanics (full)

### 4.1 State and equations of motion

Per fold, two lumped masses: lower (mass 1, "body") and upper (mass 2, "cover"),
displacements $\xi_1, \xi_2$ (positive = lateral, opening the glottis):

$$
m_1 \ddot{\xi}_1 + r_1 \dot{\xi}_1 + k_1 \xi_1 + k_c(\xi_1 - \xi_2) + f_{c1} = F_1
$$
$$
m_2 \ddot{\xi}_2 + r_2 \dot{\xi}_2 + k_2 \xi_2 + k_c(\xi_2 - \xi_1) + f_{c2} = F_2
$$

- $r_i = 2\zeta_i\sqrt{m_i k_i}$ — damping from a damping *ratio*: $\zeta_1 = 0.1$ when the
  gap is open, $\zeta_2 = 0.6$ when closed (higher closed-phase damping models tissue
  hysteresis and the collision losses).
- $k_c(\xi_1 - \xi_2)$ — the coupling spring between the two masses (models the
  connective tissue / vocal ligament).
- Collision: when $\xi_i + x_{0i} < 0$ (the medial surface would pass the midline), a
  stiff contact spring engages: $f_{ci} = 3 k_i (\xi_i + x_{0i})$ (contact-ratio 3,
  matching both reference implementations; the IF72 paper used the same factor).

### 4.2 Canonical IF72 parameters (SI)

| Param | Value | Meaning |
|---|---|---|
| $m_1$ | $1.25\times10^{-4}$ kg (0.125 g) | lower mass |
| $m_2$ | $2.5\times10^{-5}$ kg (0.025 g) | upper mass |
| $k_1$ | 80 N/m | lower stiffness |
| $k_2$ | 8 N/m | upper stiffness |
| $k_c$ | 25 N/m | coupling stiffness |
| $x_{01}, x_{02}$ | $2.0\times10^{-4}$ m | rest half-openings |
| $L$ | 0.014 m | fold length (anterior-posterior) |
| $T_1, T_2$ | $2.5\times10^{-3}$, $5.0\times10^{-4}$ m | mass thicknesses |
| $\rho$ | 1.14 kg/m³ | warm lung air density |
| $\zeta_{\text{open}}, \zeta_{\text{close}}$ | 0.1, 0.6 | damping ratios |
| $P_s$ | 800 Pa (typ.) | subglottal pressure |

### 4.3 Glottal geometry and flow

Areas at each mass (both folds: factor 2):

$$
a_{g1} = 2L(\xi_1 + x_{01}), \qquad a_{g2} = 2L(\xi_2 + x_{02}), \qquad a_{\min} = \min(a_{g1}, a_{g2})
$$

Orifice (Bernoulli) flow — the glottal volume velocity:

$$
u_g = a_{\min}\sqrt{\frac{2P_s}{\rho}}
$$

Pressure on each mass (Bernoulli with flow separation at the minimum area):

$$
P_1 = P_s\left(1 - \left(\frac{a_{\min}}{a_{g1}}\right)^2\right), \qquad
P_2 = \begin{cases} 0 & a_{g2} \ge a_{g1} \\ P_s\left(1 - \left(\frac{a_{\min}}{a_{g2}}\right)^2\right) & a_{g2} < a_{g1} \end{cases}
$$

Driving forces: $F_i = P_i\, L\, T_i$ (pressure over the medial surface $L \times T_i$).

**Why this self-oscillates (the physics).** During the opening phase the glottis is
convergent; the Bernoulli drop makes $P_1$ slightly below $P_s$ but still strongly
positive — it pushes the folds apart. As the folds pass through the neutral point the
glottis becomes divergent; the flow separates at the vena contracta (min area) and the
pressure downstream of the throat collapses toward the supraglottal pressure ($P_2 \to 0$,
often *below* the oral pressure in refined models), which *sucks* the folds closed. The
collision stops the closure, the pressure rebuilds, and the cycle repeats. The asymmetric
pressure profile ($P_1$ positive, $P_2 \approx 0$) is what produces the **skewed** glottal
pulse — the Rosenberg/LF shape emerges from physics, not from a lookup table.

### 4.4 Integration

Classic **RK4** at audio rate, $dt = 1/f_s$. At every stage: recompute areas → flow →
pressures → collision state → forces → accelerations. Verified stable at 48 kHz with the
IF72 defaults; explicit Euler is *not* stable once the collision springs engage.

### 4.5 What to emit

- **Glottal flow** $u_g(t)$: unipolar (min = 0), the volume velocity — the *source* for a
  tract model that accepts flow input (SP-067 KLAT is exactly this: it takes $u_g$ at the
  glottal end).
- **Radiated pressure**: $p_{\text{rad}} \propto du_g/dt$ — the differentiated flow, the
  actual acoustic output at the mouth (mouth radiation is a differentiator at low
  frequencies). Use this for formant-filter (SP-015) or LPC (SP-028) chains, or add a DC
  blocker if feeding raw $u_g$.

### 4.6 Measured behaviour (this verification run — 48 kHz, NumPy, 0.6 s)

| # | Check | Result |
|---|---|---|
| 1 | Self-oscillation from rest | limit cycle, amp($\xi_1$) = $4.45\times10^{-4}$ m ✓ |
| 2 | f0 at IF72 defaults, $P_s$ = 800 Pa | **126.2 Hz** (male range) ✓ |
| 3 | Pitch law, kscale = 2 | f0 → 226.5 Hz, ratio 1.79 → **f0 ~ k^0.84** (super-linear; aerodynamic loading super-stiffens vs the linear √(k/m) = 1.414) ✓ |
| 4 | Closed quotient | 0.18 (skewed pulse) ✓ |
| 5 | $u_g$ unipolar | min = 0.0 ✓ |
| 6 | Flow spectral slope (200 Hz–4 kHz, steady-state Welch) | **−7.7 dB/oct** (canonical glottal rolloff −6…−14) ✓ |
| 7 | Radiated $du_g/dt$ slope | −1.7 dB/oct (brighter, differentiated) ✓ |
| 8 | Determinism | two identical runs bit-equal ✓ |
| 9 | Subglottal threshold, $P_s$ = 80 Pa | amplitude decays to $1.4\times10^{-9}$ m — no phonation ✓ |

---

## 5. Python/NumPy implementation sketch

```python
import numpy as np

FS = 48000
DT = 1.0 / FS

P = dict(m1=1.25e-4, m2=2.5e-5, k1=80.0, k2=8.0, kc=25.0, contact_ratio=3.0,
         x01=2.0e-4, x02=2.0e-4, L=0.014, T1=2.5e-3, T2=5.0e-4,
         rho=1.14, zeta_open=0.1, zeta_close=0.6, ps=800.0)

def glottal(x1, x2, P):
    """Areas, Bernoulli flow, pressures at current fold state."""
    a1 = P["x01"] + x1; a2 = P["x02"] + x2
    ag1 = 2*P["L"]*a1 if a1 > 0 else 0.0
    ag2 = 2*P["L"]*a2 if a2 > 0 else 0.0
    if a1 <= 0 or a2 <= 0:                 # closed: no flow
        return 0.0, 0.0, 0.0
    amin = min(ag1, ag2)
    ug = amin * np.sqrt(2*P["ps"]/P["rho"])          # orifice equation
    p1 = P["ps"] * (1 - (amin/ag1)**2)               # Bernoulli drop at lower mass
    p2 = 0.0 if ag2 >= ag1 else P["ps"] * (1 - (amin/ag2)**2)
    return ug, p1, p2

def deriv(state, P):
    x1, v1, x2, v2 = state
    ug, p1, p2 = glottal(x1, x2, P)
    a1 = P["x01"] + x1; a2 = P["x02"] + x2
    c1 = a1 < 0; c2 = a2 < 0                          # collision flags
    z1 = P["zeta_close"] if c1 else P["zeta_open"]
    z2 = P["zeta_close"] if c2 else P["zeta_open"]
    r1 = 2*z1*np.sqrt(P["m1"]*P["k1"])
    r2 = 2*z2*np.sqrt(P["m2"]*P["k2"])
    fc1 = (P["contact_ratio"]*P["k1"]*a1) if c1 else 0.0
    fc2 = (P["contact_ratio"]*P["k2"]*a2) if c2 else 0.0
    fa1 = p1*P["L"]*P["T1"]; fa2 = p2*P["L"]*P["T2"]
    acc1 = (-r1*v1 - P["k1"]*x1 - P["kc"]*(x1-x2) - fc1 + fa1)/P["m1"]
    acc2 = (-r2*v2 - P["k2"]*x2 - P["kc"]*(x2-x1) - fc2 + fa2)/P["m2"]
    return np.array([v1, acc1, v2, acc2]), ug

def rk4(state, P):
    k1, _ = deriv(state, P)
    k2, _ = deriv(state + 0.5*DT*k1, P)
    k3, _ = deriv(state + 0.5*DT*k2, P)
    k4, _ = deriv(state + DT*k3, P)
    return state + (DT/6.0)*(k1 + 2*k2 + 2*k3 + k4), None

def render(seconds, ps=800.0, kscale=1.0, f0_cal=None, out_radiated=True):
    """Render `seconds` of phonation. Returns (t, ug, signal)."""
    P2 = dict(P, ps=ps, k1=P["k1"]*kscale, k2=P["k2"]*kscale, kc=P["kc"]*kscale)
    n = int(seconds*FS)
    t = np.arange(n)*DT
    ug = np.empty(n)
    state = np.array([1.2e-4, 0.0, 1.2e-4, 0.0])   # small perturbation from rest
    for i in range(n):
        ug[i] = glottal(state[0], state[2], P2)[0]
        state, _ = rk4(state, P2)
    sig = np.diff(ug) if out_radiated else ug       # radiate the derivative
    return t, ug, sig

if __name__ == "__main__":
    import sys
    t, ug, sig = render(0.5)
    # write a 16-bit WAV via soundfile/scipy if available
    try:
        from scipy.io import wavfile
        x = np.int16(sig/np.max(np.abs(sig))*0.9*32767)
        wavfile.write("tmvf_voice.wav", FS, x)
        print("wrote tmvf_voice.wav", len(x), "samples")
    except Exception as e:
        print("wav write skipped:", e)
```

**Tuning recipe for a note.** (1) Choose register (chest/falsetto/fry = parameter regime,
see §6). (2) Find the kscale that gives the target f0: the measured law is
$f_0 \approx 126.2 \times \text{kscale}^{0.84}$ Hz at $P_s=800$ Pa — invert it
($\text{kscale} = (f_0/126.2)^{1/0.84}$) for a first guess, then fine-tune by a 0.2 s
calibration render per voice. (3) Map MIDI velocity → $P_s$ (e.g. 500–1200 Pa across the
velocity range; more pressure = louder AND brighter AND slightly sharper — the real
"shout" coupling). (4) Vibrato = ±3–7% kscale LFO at 5–6 Hz.

---

## 6. Musical Elements Framework

| Element | Role |
|---|---|
| **PITCH** | Emergent f0 from (k, m, Ps, collision). Tension (kscale on k1,k2,kc) is the pitch dial — measured law f0 ~ k^0.84, calibrated per voice. Vibrato = tension LFO; glissando = continuous tension ramp (physical in-source counterpart of SP-029); register = parameter regime (chest: strong collision, low ζ2; falsetto: mass-2 dominant, weak collision; fry: low Ps near threshold → period-doubling). |
| **RHYTHM** | Onset = Ps ramp (note-on); offset = Ps release. Physical attack transient (~5–10 ms) — the "voice onset time" is part of the timbre. Breathiness = aspiration noise added to ug; creak/fry = subharmonic rhythmic microstructure. |
| **HARMONY** | Single source per instance; harmony = N instances (choir rows) or downstream tract. Chord voicing = per-voice tension; unison detune = ±0.5% tension offsets → physical beating/chorus. |
| **STRUCTURE** | Per-section parameter states = macro-form: chest→falsetto→fry arcs, Ps risers into collision saturation, drop below oscillation threshold for physical silence. |
| **TEXTURE** | Closed quotient (from ζ2 + contact ratio + Ps) = harmonic richness; breathiness = spectral floor; pressed vs flow phonation = crest factor; fry = granular texture. Fixed −7.7 dB/oct flow tilt; tract shapes it into vowels. |

---

## 7. UnitMatrix Integration

**Voices = rows = independent laryngeal sources.** Row $v$ = one TMVF instance:
`{tension (kscale), ps_pa, breathiness, zeta_close, register, seed}`; child seed
`seed * 101 + row` (same recipe as humanize) for per-voice reproducibility.

**Sections = columns = source-parameter states.** Column $j$ = tension register, Ps
envelope, breathiness, vibrato depth/rate, and downstream tract/vowel (SP-067 KLAT area
function or SP-015 formant set). Parameter crossfades are click-free by construction:
parameters enter the ODE continuously, so a linear ramp over a few ms is smooth — a
physical advantage over table-based sources (no zipper).

**Cells = MusicUnit.** Cell $(v,j)$: pitch → tension (via the calibrated k^0.84 law);
velocity → Ps (louder = brighter + sharper, the shout coupling); duration → Ps gate.
Standard `create_note_unit`/`_unit_from_events` fill; `validate()` gates drift.

**Produce dispatch:**

```python
produce(midi_path, method="SP-131", params={
    "rows": [{"tension": 1.0, "ps_pa": 800, "register": "chest", "seed": 7},
             {"tension": 1.05, "ps_pa": 750, "register": "chest", "seed": 8}],
    "columns": {"A": {"vowel": "a", "ps_pa": 700},
                "B": {"vowel": "i", "tension": 1.4},
                "C": {"register": "falsetto"}},
    "tract": "kelly_lochbaum",   # or "formant" / "lpc"
    "fs": 48000})
```

**Stage order:** TMVF source → tract (SP-067 KLAT / SP-015 formants / SP-028 LPC) →
per-row EQ (SP-007) → spatialization (SP-021/SP-129) → dynamics (SP-008/SP-107) →
loudness (SP-126) → dither (SP-122).

**Chaining convention:** TMVF is the *physical source* replacement for the parametric
glottal pulses in SP-015/028/038/067. Its radiated flow feeds any existing resonator
chain unchanged — swap-in is a drop-in at the excitation block.

---

## 8. Pitfalls

1. **Pitch is not a dial.** f0 emerges from (k, m, Ps, collision); you cannot set 440 Hz
   directly. Calibrate a tension→f0 table per voice by simulation; the measured law is
   f0 ~ k^0.84 (not k^0.5 — aerodynamic loading super-stiffens, a naive √(k/m) guess is
   ~30% off). Pitch via tension, never by resampling the output.
2. **RK4 required; explicit Euler blows up.** Collision springs (3k) push the fastest
   eigenmode up; forward Euler at 48 kHz is unstable at the closed phase (observed during
   development). RK4 is stable at 48 kHz with IF72 defaults; use a stiff solver (LSODA via
   scipy) if you raise collision stiffness.
3. **Zero-area division.** When the glottis closes, a_g → 0 and the orifice equation
   divides; branch to u_g = 0 when a_min ≤ 0 (both reference implementations do this). Do
   not clamp areas to a tiny epsilon and keep dividing — that leaks flow through a "closed"
   glottis.
4. **DC and the unipolar flow.** u_g is unipolar (min = 0) with a large DC component.
   Radiate the *derivative* du_g/dt (the physical mouth radiation) or DC-block before the
   tract; feeding raw u_g into KLAT biases the tube.
5. **The attack transient is physical.** The limit cycle needs ~5–10 ms to build from
   rest; below-threshold Ps (≈ 80–300 Pa with these defaults) never phonates (verified:
   80 Pa decays to 1e-9 m). For instant note starts, pre-sustain the oscillator (keep Ps
   active one cell before onset) or embrace the onset as the voice-onset-time feature.
6. **Closed quotient is a result, not a control.** Default ζ2 = 0.6 / contact-ratio 3
   gives CQ ≈ 0.18 (measured) — a bright, buzzy "IF72 voice". Natural speech CQ is
   0.4–0.6: raise ζ_close or enlarge x0 to darken; lower for fry. Tune (ζ2, contact
   ratio, Ps), not CQ directly.
7. **Two masses ≠ two formants.** m1/m2 are mechanical modes, not acoustic resonances.
   The source still needs the tract (SP-067/SP-015/SP-028) to sound like a voice; TMVF
   alone is a buzzy saw. Document the chain, not the source alone.
8. **Stiff ODEs are expensive.** Per-sample RK4 with per-stage Bernoulli evaluation is
   ~10–30× realtime in NumPy (loop-bound); a C/cython or `solve_ivp`-blocked
   implementation runs realtime. State is only 4 floats — ideal for AudioWorklet (as the
   JS reference implementation shows) or 2×-oversampled block integration.

---

## 9. Relation to other SP methods

| Method | Relation |
|---|---|
| SP-067 KLAT | **primary consumer**: physical tract; TMVF replaces its parametric glottal pulse at the glottal boundary |
| SP-015 Formant Vowel | alternative tract: TMVF radiated flow through formant filters |
| SP-028 LPC | alternative tract: TMVF flow as LPC excitation (whispered/shaped) |
| SP-038 VOSIM / SP-025 FOF | same job (voice source) with different physics — parametric vs physical |
| SP-004 DDSP-style | learned neural voice source — TMVF is the interpretable physical foil |
| SP-027 SMS / SP-061 CLS | analysis-side siblings: TMVF is pure synthesis (no analysis needed) |
| SP-121 Van der Pol | same *self-oscillating nonlinear oscillator* family (relaxation oscillation) — but TMVF's limit cycle is driven by aerodynamics, not a damping sign-flip |
| SP-029 CPPG glide | glissando concept shared: TMVF does it inside the source via tension ramp |

---

## 10. References

- Ishizaka, K., & Flanagan, J. L. (1972). "Synthesis of Voiced Sounds From a Two-Mass
  Model of the Vocal Cords." *Bell System Technical Journal* 51(6), 1233–1268.
- van den Berg, J. (1958). "Myoelastic-Aerodynamic Theory of Voice Production." *Journal
  of Speech and Hearing Research* 1(3), 227–244.
- Flanagan, J. L., & Landgraf, L. L. (1968). "Self-Oscillating Source for Vocal-Tract
  Synthesizers." *IEEE Trans. Audio Electroacoustics* AU-16(1), 57–64.
- Titze, I. R. (1988). "The Physics of Small-Amplitude Oscillation of the Vocal Folds."
  *JASA* 83(4), 1536–1552.
- Story, B. H., & Titze, I. R. (1995). "Voice Simulation With a Body-Cover Model of the
  Vocal Folds." *JASA* 97(2), 1249–1260.
- Pelorson, X., et al. (1994). "Theoretical and Experimental Study of Quasisteady-Flow
  Separation Within the Glottis During Phonation." *JASA* 96(6), 3416–3431.
- Fant, G., Liljencrants, J., & Lin, Q. (1985). "A Four-Parameter Model of Glottal Flow."
  *STL-QPSR* 26(4).
- Rosenberg, A. E. (1971). "Effect of Glottal Pulse Shape on the Quality of Natural
  Vowels." *JASA* 49(2B), 583–590.
- kazm00th. "ishizaka-flanagan-realtime" (JS/AudioWorklet two-mass implementation,
  canonical IF72 values, MIT license). GitHub.
- Yoshinaga, T. (2022). "two_mass.m" — IF72 two-mass model with subglottal/supraglottal
  tract loading and Pelorson flow separation (MATLAB, MIT license). GitHub.
