# SP-149 — Minnaert Bubble-Resonance Percussion Synthesis (MBRS)

**Layer:** absolute — sound production (Synthesis Engines)
**Target output:** gas-bubble liquid percussion; drip / rain / brook / glug timbres; tuned sub-bass "bubble" thump
**Candidate code path:** `sound/synthesis/bubble_resonance.py`
**DB section:** `methods_db.md` → "Sound Production Method SP-149 — Minnaert Bubble-Resonance Percussion Synthesis (MBRS)"
**Prototype:** `_web149_mbrs/verify_mbrs.py` (13/13 checks, `verify_mbrs_results.txt`, demo WAV 2,304,044 B)
**Framework:** Musical Elements (PITCH/RHYTHM/HARMONY/STRUCTURE/TEXTURE) + UnitMatrix (Voices=rows, Sections=columns, Cells=MusicUnit)

---

## 1. Idea in one paragraph

A gas bubble in a liquid is a **compliance (the gas) driven by a mass (the surrounding liquid)** — a
one-degree-of-freedom resonator. Minnaert (1933) showed that the sound of running water is not the
impact of droplets but the ringing of millimetre-scale air bubbles entrained by them, at a frequency
fixed by the *radius alone*: `f0·a ≈ 3.26 m/s`. MBRS takes that identity as the scoring rule —
**radius is pitch** — and derives everything else from the same number: decay (Q from the three
fluid loss channels), the "plink" chirp (radius changes while the bubble rings), the collective
resonance of a cloud, and the sub-audio surface wobble of large bubbles. The result is the only
pitched percussion instrument in the catalogue whose *register and articulation are the same axis*
(big bubbles are low **and** long), and the only one whose timbre is a property of a fluid rather
than of a shape, a circuit, or a spectrum.

## 2. Derivation of the pitch law (from Rayleigh–Plesset)

Rayleigh–Plesset for a spherical bubble of radius `a` in an incompressible liquid at rest at infinity:

    ρ (a·ä + (3/2)·ȧ²)  =  p_g(a) − p_∞ − 4μ·ȧ/a − 2σ/a

with `p_g = p_g0 (a0/a)^{3γ}` (polytropic gas) and equilibrium `p_g0 = p_∞ + 2σ/a0`.

Linearise with `a = a0(1+x)`, `|x| ≪ 1`:

    p_g − p_∞ ≈ −[3γ p_∞ + 6γσ/a0] x + (2σ/a0) x
    2σ/a       =  (2σ/a0)(1 − x)
    −2μ·ȧ/a   →  −(4μ/a0)·a0·ẋ

so, to first order,

    ẍ + (4ν/a0²)·ẋ + ω0²·x = 0 ,   ω0² = [ 3γ p_∞ + 2σ(3γ−1)/a0 ] / (ρ a0²)

    ⇒  f0 = (1/2πa0) · sqrt( (3γ p_∞ + 2σ(3γ−1)/a0) / ρ )

At `p_∞ = 100 kPa`, `ρ = 1000 kg/m³`, `γ = 1.4`, `σ = 0`: `f0·a0 = (1/2π)√(3γp/ρ) = 3.262 m/s`.
With `σ = 0` and `γ = 1` the bracket becomes `3p_∞ + 4σ/a0`, i.e. **Leighton's isothermal small-bubble
equation** `f0 = (1/2πR0)√(3p0/ρ + 4σ/(ρR0))` — an exact algebraic identity, checked to 1e-12.

Surface tension matters only at the bottom of the register: the +1 % pitch crossover is at
`a* ≈ 0.054 mm` (because `f ∝ √(bracket)` halves the correction), +0.055 % at 1 mm, +1.1 % at 50 µm.

**Radius ↔ note** (`a = 3.26/f`):

| note | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|
| f (Hz) | 65.4 | 130.8 | 261.6 | 523.3 | 1046.5 | 2093 | 4186 |
| a (mm) | 49.9 | 24.9 | 12.5 | 6.23 | 3.12 | 1.56 | 0.78 |

Audible band = 163 mm (20 Hz) … 0.16 mm (20 kHz): every note is a plausible bubble, so no rescaling
is needed and the physical constraints stay honest across the whole keyboard.

## 3. Damping: Q is a material property

Three loss channels, expressed as damping constants `δ = 1/Q` (energy loss per radian):

    radiation:      δ_rad  = k·a = ωa/c
    viscous:        δ_visc = 4ν / (ω a²)          [from the 4ν/a0² term above: δ = 2β/ω]
    thermal:        δ_th   ≈ 3(κ−1)·δ_t / a ,   δ_t = sqrt(2D/ω)

    δ_tot = δ_rad + δ_visc + δ_th ,   Q = 1/δ_tot ,   τ = Q/(π f0) ,   T60 = 6.91·τ

The thermal term is the asymptotic (thin boundary layer, `a ≫ δ_t`) form; `δ_t ≈ 46 µm` at 1 mm and
3.3 kHz, so it is valid for every radius this method uses musically. Its prefactor is `(κ−1)`, not
`(γ−1)`, which is what makes the model self-consistent as bubbles shrink: the same quantity that
detunes the pitch also removes the loss (an isothermal bubble cannot lose heat to a gradient it does
not have).

Measured with the prototype (`ρ = 998`, `ν = 1e−6`, `c = 1480`, `D = 2.2e−5`):

| a (mm) | f0 (Hz) | δ_rad | δ_visc | δ_th | Q | τ (ms) | T60 (ms) |
|---|---|---|---|---|---|---|---|
| 0.1 | 32 432 | 0.0138 | 0.00196 | 0.1537 | 5.9 | 0.03 | 0.20 |
| 0.5 | 6 522 | 0.0138 | 0.00039 | 0.0738 | 11.4 | 0.56 | 3.85 |
| 1.0 | 3 268 | 0.0139 | 0.00020 | 0.0531 | 14.9 | 1.45 | 10.0 |
| 2.0 | 1 636 | 0.0139 | 0.00010 | 0.0380 | 19.2 | 3.73 | 25.8 |
| 5.0 | 656 | 0.0139 | 0.00004 | 0.0243 | 26.1 | 12.7 | 87.5 |
| 10.0 | 328 | 0.0139 | 0.00002 | 0.0173 | 32.0 | 31.1 | 215 |

Two consequences follow directly and are the method's musical signature:

1. `δ_rad` is **constant** across the table (0.0139) because `ω ∝ 1/a` exactly cancels the `a` in
   `ka` — radiation is a fixed tax of ~1.4 % per radian on every bubble.
2. Thermal conduction dominates below ~10 mm and grows as `1/a`, so **small = short, large = long**.
   A 3.3 kHz drip is a 10 ms tick; a 328 Hz glug rings 215 ms. You cannot have a long high bubble
   without lying about the fluid (`q_override`), which is why the override is flagged in provenance.

## 4. Effective polytropic exponent

Small bubbles equilibrate thermally within a cycle (`κ → 1`, isothermal); large ones do not
(`κ → γ`). Implemented as a smooth interpolation on the thermal penetration depth:

    δ_t(a) = sqrt(2D/ω) ,   κ(a) = 1 + (γ−1)·a/(a + δ_t)

fixed-point iterated (ω depends on κ). Measured: `κ(1 mm) = 1.3823`, `κ(1 µm) = 1.1756` — adiabatic
where physics says adiabatic, isothermal only in the ultrasonic regime. Using `γ = 1.4` for a 5 µm
bubble overestimates pitch by a few percent and overestimates thermal damping; using `γ = 1` for a
1 mm bubble is ≈18 % flat.

## 5. Chirp: radius is integrated, not frequency

    a(t) = a0 · (1 + (g−1)·t/T) ,      g = a(T)/a0
    f(t) = (1/2π a(t))·sqrt((3γp + 2σ(3γ−1)/a(t))/ρ)
    φ(t) = 2π ∫₀ᵗ f(ξ) dξ ,   y = A e^{−t/τ} sin φ(t)

`g < 1` (dissolving / collapsing bubble) → **rising** plink: the tap-drip signature.
`g > 1` (growing / rising, lower pressure) → **falling** glug: the bottle-fill signature.
Verified: `g = 0.70` measures ×1.396 against the ideal ×1.4286 (2.3 %, analysis-window residual).

Phase must be integrated. `sin(2π f(t)·t)` is *not* the same signal: it sweeps at twice the intended
rate near `t = T/2` and jumps phase wherever `a(t)` changes slope — audible crackle plus a wrong chirp.

## 6. Cloud resonance

`N` bubbles within a cloud of radius `a_c` resonate collectively at the cloud's own Minnaert
frequency, not at the individual bubble frequency:

    a_c = a · N^{1/3} ,   f_cloud = 3.26 / a_c

Verified: 1000 × 1 mm bubbles → `a_c = 10 mm` → 328.7 Hz, exactly one decade below the single
bubble's 3288 Hz. This is the "rumble" under a brook or a poured bottle, and it must be rendered
**once per cloud** (amplitude ∝ √N, decay slower than the grains), not once per bubble.

## 7. Surface (Lamb) modes

Non-spherical modes obey `ω_n² = (n−1)(n+1)(n+2)σ/(ρa³)`; for `n = 2`:

    f2 = (1/2π)·sqrt(12σ/(ρ a³))

Always far below `f0` (52.6 Hz at 2 mm; 2.3 Hz at 16 mm) and scaling as `a^{−3/2}` (ratio 22.63 = 8^1.5
between 2 and 16 mm, verified). Musically it is the sub-audio "wobble/burble" of large bubbles and
clouds — worth a small (`≈0.12`) mix only when `f2 > 20 Hz`, otherwise it is DC mud.

## 8. Event = three layers

    y(t) = A·e^{−t/τ}·sin φ(t)                     bubble ring (pitch, decay)
         + g2·e^{−t/1.6τ}·sin(2π f2 t)             Lamb wobble (size cue)
         + s(t)·e^{−t/τs}                          pinch-off splash (impact cue)

`s(t)` is a 2–5 ms band-limited (first-difference-tilted) noise burst, `τs ≈ 0.25·len(s)`. The
**splash : ring ratio is the "wetness" knob** — the single most useful production control, because it
decides whether a gesture reads as *impacts on water* or as *tones made of water*.

## 9. Cost

Per event: one phase accumulator, one exponential envelope, one optional LF oscillator, one short
noise burst → `O(1)` state, ~6 ops/sample. Cheaper than a single Karplus-Strong string (which needs a
delay line). A 200-event rain bed over 10 s at 48 kHz is ~10⁸ ops in NumPy, vectorised per event;
cost is linear in event count, independent of "polyphony".

## 10. Presets

| preset | radius source | splash | glide g | shape mode | Q override |
|---|---|---|---|---|---|
| `drip` | note → a | 0.10 | 0.95–0.99 | off | – |
| `drop` | note → a | 0.35 | 0.78–0.92 | off | – |
| `glug` | note → a | 0.15 | 1.05–1.25 | on | 45 |
| `rain` | log-normal in a, 0.3–1.5 mm | 0.60 | 0.9–1.1 | off | – |
| `brook` | log-normal, 0.5–4 mm + cloud | 0.40 | 0.85–1.15 | on | – |
| `bubble-bass` | note → a, C1–C3 | 0.08 | 1.1–1.3 | on | 60 |

## 11. NumPy implementation sketch

```python
import numpy as np

P_ATM, RHO, GAMMA, SIGMA = 101325.0, 998.0, 1.4, 0.0728
C_W, NU, D_AIR = 1480.0, 1.0e-6, 2.2e-5


def minnaert_f(a, p=P_ATM, rho=RHO, gamma=GAMMA, sigma=SIGMA):
    """Bubble natural frequency (Hz). a in metres."""
    return np.sqrt(3.0 * gamma * p + 2.0 * sigma * (3.0 * gamma - 1.0) / a) \
        / (2.0 * np.pi * a * np.sqrt(rho))


def radius_for_f(f, p=P_ATM, rho=RHO, gamma=GAMMA):
    """Inverse map: f*a = const  ->  radius in metres."""
    return np.sqrt(3.0 * gamma * p / rho) / (2.0 * np.pi * f)


def gamma_eff(a, f=None, gamma=GAMMA, D=D_AIR, p=P_ATM, rho=RHO):
    ge = gamma
    for _ in range(6):
        if f is None:
            f = minnaert_f(a, p=p, rho=rho, gamma=ge)
        dt = np.sqrt(2.0 * D / (2.0 * np.pi * f))
        ge, f = 1.0 + (gamma - 1.0) * (a / (a + dt)), None
    return ge


def damping(a, f, rho=RHO, nu=NU, c=C_W, D=D_AIR):
    w = 2.0 * np.pi * f
    d_rad = w * a / c
    d_visc = 4.0 * nu / (w * a * a)
    d_th = 3.0 * (gamma_eff(a, f) - 1.0) * np.sqrt(2.0 * D / w) / a
    return d_rad + d_visc + d_th          # delta = 1/Q


def shape_f2(a, rho=RHO, sigma=SIGMA):
    return np.sqrt(12.0 * sigma / (rho * a ** 3)) / (2.0 * np.pi)


def render_event(a0, dur, fs=48000, glide=1.0, q=None, splash=0.25,
                 seed=0, shape=True):
    n = int(round(dur * fs))
    t = np.arange(n) / fs
    a_t = a0 * (1.0 + (glide - 1.0) * np.linspace(0.0, 1.0, n))
    f_t = minnaert_f(a_t, gamma=gamma_eff(a0))
    phase = 2.0 * np.pi * np.cumsum(f_t) / fs      # integrate, never modulate
    f0 = float(f_t[0])
    q = 1.0 / damping(a0, f0) if q is None else q
    tau = q / (np.pi * f0)
    y = np.sin(phase) * np.exp(-t / tau)
    f2 = shape_f2(a0)
    if shape and f2 > 20.0:
        y += 0.12 * np.sin(2.0 * np.pi * f2 * t) * np.exp(-t / (1.6 * tau))
    rng = np.random.default_rng(seed)
    na = max(8, int(0.0035 * fs))
    nz = np.diff(rng.standard_normal(na), prepend=0.0)
    nz *= np.exp(-np.arange(na) / (0.25 * na))
    y[:na] += splash * nz / (np.max(np.abs(nz)) + 1e-12)
    y *= np.minimum(1.0, np.arange(n) / 16.0)      # de-click onset
    return y


def render_cell(events, section_samples, fs=48000):
    """Sum events into exactly section_samples (zero-drift safe)."""
    buf = np.zeros(section_samples)
    for ev in events:
        i0 = int(ev["start_tick"] * ev["samples_per_tick"])
        seg = ev["audio"][: max(0, section_samples - i0)]
        buf[i0:i0 + len(seg)] += seg
    return buf
```

## 12. Verification record (13/13)

`_web149_mbrs/verify_mbrs.py` (run with `$MUSICOM_PYTHON`):

1. `f0·a = 3.2617 m/s` at `p = 1e5`, `ρ = 1000`; `f0(1 mm) = 3286.5 Hz`.
2. Exact `f ∝ 1/a`: `f(0.5 mm)/f(2 mm) = 4.000000000` (with surface tension: 4.003281).
3. Depth: 10 m water → ×1.4018 measured vs `√(p/p0) = 1.4022`.
4. Surface-tension +1 % crossover at `a* = 0.054 mm`; +0.055 % at 1 mm, +1.1 % at 50 µm.
5. Helium (`γ = 1.667`) → ×1.0912.
6. Independent Rayleigh–Plesset integration peaks at 1651.2 Hz vs analytic 1643.7 Hz → **0.46 % error**.
7. Renderer `f0` within **0.005 %**, `τ` within **0.5 %** of `Q/(π f0)`.
8. Chirp: `g = 0.70` → ×1.396 measured vs ×1.4286 ideal.
9. Cloud: 1000 × 1 mm → 328.7 Hz, exactly ×0.100 of 3288 Hz (`N^{1/3}` law).
10. Determinism (SHA-256 identical across runs) and exact sample count (`n = 24000` for 0.5 s @ 48 kHz).
11. `γ = 1` limit equals Leighton's isothermal equation to 1e-12 (56082.18 Hz both ways at 50 µm).
12. `κ(1 mm) = 1.3823` (adiabatic), `κ(1 µm) = 1.1756` (isothermal).
13. Lamb `n = 2`: 52.6 Hz @ 2 mm, 2.3 Hz @ 16 mm, ratio 22.627 = 8^1.5.

Demo: 12.0 s stereo WAV, 2,304,044 B (`projects/Research/outputs/sp149_mbrs/sp149_mbrs_demo.wav`).

## 13. UnitMatrix mapping

- **Rows (voices)** = liquid sources with `{gas, depth_m, temp_c, q_override, size_class, splash,
  glide range, shape_mode, cloud{n, spread_cents}, seed}`. A row is *pitched* (radius from the note)
  or *unpitched* (radius from a size distribution) — the latter for rain/fizz beds.
- **Columns (sections)** = water state `{preset tap|rain|brook|underwater|pour, depth_m,
  density_events_s, splash, room_send, cloud_size}`, cross-faded over ≥100 ms. Because parameters are
  evaluated per event at onset, a column change alters the *next* events only — which is what a real
  change of medium does; no click is possible.
- **Cells (MusicUnit)** = one or more events: `start_tick` → onset, `pitch` → radius (or ignored),
  `velocity` → excitation amplitude and splash ratio, optional `radius_scale` for microtonal colour.
  Tails are summed into the row buffer and truncated at the section seam.
- **Stage order**: MBRS (source) → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) →
  space/tail (SP-009/SP-032/SP-140/SP-148) → bus dynamics (SP-008/SP-107) → loudness (SP-126) →
  dither (SP-122).

## 14. Pitfalls (condensed)

1. One mode, no spectrum — layer with a body (SP-003/042/105) for melodic use.
2. Don't "fix" the 1.45 ms decay with `q_override`; lower the register or add space instead.
3. Integrate phase; never modulate frequency instantaneously.
4. Clamp `a ≥ 0.15 mm` and `f0 ≤ 0.45 fs` (surface tension makes `f0 ∝ a^{−1.5}` at the small end).
5. Normalise the splash burst per event; otherwise "wetness" is secretly a level control.
6. Jitter cloud onsets ±10 ms; draw radii log-normally in `a`, never on a grid.
7. Render the collective cloud resonance once per cloud, not once per bubble.
8. Record `depth_m`, not `p_A` (a 10 m ambiguity is ×1.4 in pitch).
9. Use `κ(a)` at both extremes; don't pick a global γ.
10. Seed per (row, cell, event); assert the row buffer length equals the section's sample count.

## 15. References

1. Minnaert, M. (1933). "On musical air-bubbles and the sounds of running water." *Philosophical Magazine* 16(104), 235–248. doi:10.1080/14786443309462277.
2. Leighton, T. G. (1994). *The Acoustic Bubble*. Academic Press. (Damping decomposition; isothermal small-bubble equation, §4.)
3. Prosperetti, A. & Oguz, H. N. (1993). "The impact of drops on liquid surfaces and the underwater noise of rain." *Annu. Rev. Fluid Mech.* 25, 577–602. doi:10.1146/annurev.fl.25.010193.003045.
4. Rayleigh, Lord (1917). "On the pressure developed in a liquid during the collapse of a spherical cavity." *Phil. Mag.* 34, 94–98.
5. Plesset, M. S. (1949). "The dynamics of cavitation bubbles." *J. Appl. Mech.* 16, 277–282.
6. Prosperetti, A. (1974). "Nonlinear oscillations of gas bubbles in liquids: steady-state solutions." *J. Acoust. Soc. Am.* 56, 878–885.
7. Devin, C. (1959). "Survey of thermal, radiation, and viscous damping of pulsating air bubbles in water." *J. Acoust. Soc. Am.* 31, 1654–1667.
8. Lamb, H. (1932). *Hydrodynamics*, 6th ed., §275 (surface modes).
9. Brennen, C. E. (1995). *Cavitation and Bubble Dynamics*. Oxford University Press.
10. Mann, S., Janzen, R., Post, M., & Jackson, T. (2007). "Hydraulophone design considerations: design that evokes feelings of fun and wonder." *Proc. ACM Multimedia* / hydraulophone instrument papers 2005–2011.
11. Waters, R. (1968–2013). Waterphone (ocean harp) — steel bowl + bronze rods + water as added mass.
12. Farnell, A. (2010). *Designing Sound*. MIT Press. (Procedural water/impact layering practice.)
13. Chandran Suja, V. & Barakat, A. I. (2018). "A mathematical model for the sounds produced by knuckle cracking." *Scientific Reports* 8, 4600. (Bubble collapse as the sound source in a biological system — evidence for the mechanism's generality.)
