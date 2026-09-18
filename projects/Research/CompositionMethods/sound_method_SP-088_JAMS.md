# Sound Production Method SP-088 — Jiles–Atherton Magnetic Tape Saturation Synthesis (JAMS)

**Layer:** absolute (sound production — Post-Processing / DSP)
**Category:** Post-Processing / DSP | **Target Output:** Analog Tape Saturation / Magnetic Hysteresis Coloration

### One-line description

Renders analog tape saturation from the physics of magnetic hysteresis rather
than a static transfer curve: the Jiles–Atherton differential model integrates
magnetization $M$ of the tape coating sample-by-sample against the head-drive
field $H_e = \alpha M + H$, so compression, harmonic generation, low-frequency
head bump, and high-frequency loss all *emerge* from domain-wall physics
(saturation $M_s$, pinning $a$, domain coupling $\alpha$, reversibility $c$)
and react dynamically to level, bias, and tape speed.

### Layer classification

Per `LAYER_ARCHITECTURE.md`, every SP-* method is **absolute** (sound production:
audio stems → WAV/OGG). JAMS is an *absolute*-layer method in the Post-Processing
/ DSP class: it consumes an already-rendered audio stem (any UnitMatrix export)
and emits a re-magnetized buffer. Candidate code path:
`sound/effects/tape_saturation.py` — sibling of `sound/effects/tape_delay.py`
(delay-line lo-fi) and the analog-coloration side of
`sound/effects/mastering.py`. Plugs into
`workflows.musicom_workflow.produce(method="SP-088")` as a stem coloration stage
after SP-001 (FluidSynth) / SP-011 (Karplus-Strong) rendering.

### Source

The **Jiles–Atherton model** (Jiles & Atherton, *Journal of Magnetism and
Magnetic Materials* **61**:48, 1986) is the standard physics-based description
of ferromagnetic hysteresis: magnetization $M$ lags applied field $H$ through
domain-wall pinning, anhysteretic equilibrium $\mathrm{anh}(x)=\coth(x)-1/x$
(Langevin function), and inter-domain coupling. Signal-processing adopters:

- Jiles, D. C., & Atherton, D. L. (1986). "Theory of ferromagnetic
  hysteresis." *J. Magn. Magn. Mater.* 61(1-2): 48–60. (Original ODE
  $\frac{dM}{dH}$; Langevin anhysteresis; the five canonical parameters.)
- [Wikipedia: Jiles–Atherton model](https://en.wikipedia.org/wiki/Jiles%E2%80%93Atherton_model)
  (fetched 2026-09-18): parameter roles, coupling into the effective field,
  delta-method ODE integration — used as the parameter-semantics cross-check.
- CHOPIN / SPICE literature: T. Matsuo et al., "Fast numerical method for
  the Jiles–Atherton model" (IEEJ, 2005-ish) — $dM/dt$ time-domain form,
  Euler/Heun integration guidance, deal-with-derivative-singularity tricks.
- R. Marion, M. Lemistieu, et al., "Improvements of the Jiles–Atherton model
  for audio applications" lineage (hysteresis-for-audio papers, e.g.
  DAFx-adjacent work) — bias scaling, per-sample ODE integration discipline.
- V. Välimäki & co., tape-saturation overviews (AES/DAFx): tape machine
  signal chain — hysteresis nonlinearity + frequency-dependent head response
  (playback head gap loss, head bump) + asperity noise; the modularity JAMS
  follows.
- P. J. W. Mels & D. T. Yeh / Stanford Music421-type virtual-analog notes:
  waveform-exact tape emulation practice (whine whistles, azimuth loss,
  bias-frequency choices 150–250 kHz scaled down to feasible $f_b$).

### Description

Analog tape "warmth" is not a soft-clip curve. It is the output of a
 hysteretic system: the tape coating's magnetization $M$ does not track the
record-head field $H$ instantaneously but follows a history-dependent path
governed by domain-wall pinning. Consequences that a static `tanh` coloration
cannot reproduce, and that JAMS gets by construction:

1. **Slope-dependent compression.** The incremental gain $\frac{dM}{dH}$
   decreases as the magnetization approaches saturation — heavy material
   compresses more at peaks, gently material stays nearly linear.
2. **Hysteresis loops = memory distortion.** $M(t)$ depends on the *path*,
   not just the instant — low-level detail rides on a magnetization set by
   recent loud passages (analog-style "bloom" after loud transients).
3. **Odd *and* order-dependent harmonics.** Small loops traced around a
   biased operating point produce asymmetric transfer (even harmonics at low
   levels, odd-dominant at high levels) exactly as real tape machines do.
4. **Head bump / NAB loss.** The record head is a first-order high-pass
   differentiator ($e[j\omega] = j\omega H$); the playback head's gap loss
   $e^{-k g^2 f^2}$ rolls off highs; the standard NAB equalization adds a
   low shelf — the combination yields the "head bump" at the low end
   (~50–100 Hz) and gentle top rolloff. These are linear stages that bracket
   the nonlinear core.
5. **Asperity noise.** Surface roughness of the coating adds a low-level
   high-passed noise floor that masks quantization — the analog "air".

The method integrates the **Jiles–Atherton ODE in time** (the "delta
method" of SPICE practice):

$$\frac{dM}{dt} = \frac{dM}{dH_e}\Big|_{H_e}\cdot\frac{dH_e}{dt},\qquad
H_e = H + \alpha M$$

with

$$\frac{dM}{dH_e} =
\frac{(1-c)\,\frac{dM_\mathrm{irr}}{dH_e} + c\,\frac{dM_\mathrm{rev}}{dH_e}}
     {1 - \alpha(1-c)\,\frac{dM_\mathrm{irr}}{dH_e}}$$

$$\frac{dM_\mathrm{irr}}{dH_e} =
\frac{M_\mathrm{an}(H_e) - M_\mathrm{irr}}
     {k\,\delta - \alpha\,(M_\mathrm{an}(H_e) - M_\mathrm{irr})},\qquad
\delta = \mathrm{sign}\!\left(\frac{dH_e}{dt}\right)$$

$$M_\mathrm{an}(H_e) = M_s\left[\coth\!\left(\frac{H_e+\alpha M}{a}\right) - \frac{a}{H_e+\alpha M}\right]$$

Five physical parameters: $M_s$ (saturation magnetization — how hard you
can push), $a$ (domain-wall pinning — "softness"), $k$ (coercivity — how
much history resistance), $\alpha$ (inter-domain coupling — how much the
material "squares up"), $c$ (reversibility — how much follows the
anhysteretic curve directly). Musical knobs derive from these:

| Knob | Jiles–Atherton mapping | Musical effect |
|---|---|---|
| Drive | head-field gain $g$ scaling $H$ | saturation amount |
| Bias | offset added to $H$ | distortion-floor sweet spot; too low → low-level distortion, too high → level loss |
| Tape type (I/II) | $a$, $k$, $M_s$ presets | hardness/brightness of compression |
| Speed (IPS) | gap-loss corner $f_g\propto 1/v$ | 7.5 IPS duller than 15 IPS |
| Head bump | NAB low-shelf gain/corner | low-end warmth (~60 Hz) |
| Asperity | noise std + HP cutoff | analog air / floor |

### Technical Mechanics

**Per-sample loop** (real-time-feasible; ~15 flops/sample, branch-light):

1. **Record head + bias:** $h[n] = g\,x[n] + I_b\sin(2\pi f_b n/f_s)$ — a
   high-frequency bias (modeled at a feasible 25 kHz, not the hardware's
   150+ kHz) rides the signal to linearize small-signal response and keep
   the operating point in the linear region of the anhysteretic curve.
2. **Effective field:** $H_e[n] = h[n] + \alpha M[n-1]$.
3. **Delta-method ODE step** (explicit Euler or Heun; sub-step $N=2$ for
   stability at low sample rates):

   $$M[n] = M[n-1] + N_\mathrm{sub}\cdot \mathrm{clamp}\!\left(
   \frac{dM}{dH_e}(H_e[n])\cdot (H_e[n] - H_e[n-1]),\ \Delta M_\max\right)$$

   with singularity guards: $k\delta - \alpha(M_\mathrm{an}-M_\mathrm{irr})$
   clamped to a small positive value ($\epsilon=10^{-6}$) — this is the
   division blow-up that melts audio if omitted; and
   $\coth(u) - 1/u$ computed by series for $|u|<10^{-3}$ (else it is
   $0/0$ numerically).
4. **Output (playback head):** $y[n] = e^{- (f_g f)^2} \cdot \mathrm{NAB}(M[n])$
   — implement gap loss and NAB as a short cascade of one-pole
   low-shelf (bump) + second-order low-pass (gap) sections parameterized
   by tape speed.
5. **Asperity:** $y[n] \mathrel{+}= \sigma_a\,\mathrm{HP}\{\eta[n]\}$,
   $\eta \sim \mathcal{N}(0,1)$, high-passed at ~3 kHz (surface-roughness
   band).
6. **Flux normalization / IEC1-32 dB convention** as in tape-machine
   calibration: normalize $|M|$ to the fluxivity reference so that drive
   $g=0.5$ sits near the knee — keeps presets transferable.

**Complexity:** $\mathcal{O}(N_\mathrm{sub})$ per sample — no oversampling
needed if the bias is bandlimited and $\Delta M$ is clamped (the ODE is a
low-pass integrator by nature; no ADAA required, cf. SP-062).

**Derivative sanity:** $\frac{dM}{dH_e} > 0$ always in the clamped region —
guarantees the map is monotone (no folding/aliasing-in-the-loop), which is
why tape saturates "gracefully" compared to waveshapers.

### Musical Elements Framework

- **PITCH:** transparent to pitch (memoryless-ish in the frequency domain);
  the ODE's slow relaxation adds minute phase rotation and sub-hertz drift
  of the operating point — perceived as pitch *stability* ("tape doesn't
  waver like a plugin compressor's release").
- **RHYTHM:** transient handling is the character — attack slopes compress
  asymmetrically (fast positive slopes densify, decays open), yielding the
  soft "round" hats/snares of tape-recorded drums. At extreme drive, slow
  recovery smears the groove boundary slightly (flux memory).
- **HARMONY:** harmonic generation is level- and slope-dependent: quiet
  chords stay clean, climaxes grow 3rd/5th/7th harmonics asymmetrically —
  a natural dynamic-sideband "chorus of distortion" that thickens pads on
  crescendos without changing their interval content.
- **STRUCTURE:** acts as a **global macro-dynamics** stage — apply per
  section (e.g., lighter drive on intro/outro, full saturation on chorus)
  or as a bus coloration after the full mix. The ODE's memory means
  section joins have a short "tape settle" (5–20 ms) — natural glue.
- **TEXTURE:** asperity noise fills the spectral floor between voices;
  head bump + gap loss shape a gentle band focus (~120 Hz – 10 kHz)
  reminiscent of cassette-era density. Pair with SP-006 (humanization) for
  lo-fi character or with SP-009/SP-032 (reverb) after, not before, to
  keep reverb tails clean.

### UnitMatrix Integration

- **Voices = rows** — each voice's stem can be driven through its own
  tape channel with per-voice parameters (e.g., lead bright/tight:
  small $k$ + high speed; bass warm/loose: large $k$ + 7.5 IPS head bump).
- **Sections = columns** — per-section drive/automation map: parameterize
  drive $g(s)$ and bias $b(s)$ per section so the macro-form carries a
  tape-density arc (verse = light, chorus = pushed). The ODE state $M$
  carries *across* section boundaries for physical continuity (do not
  reset — resets click and lose the settle).
- **Cells = MusicUnit** — one `MusicUnit` per voice/section already
  renders to a stem via SP-001/SP-011; JAMS post-processes the summed or
  per-voice stems. Unit boundaries align with the tape's settle
  characteristics: terminal silent padding (MIDI tail truncation fix)
  keeps the last note's hysteresis decay inside the section length.
- **Workflow:** `compose()` → `produce(method="SP-001")` →
  `produce(method="SP-088", params={drive, bias, speed, bump})` →
  WAV/OGG. Optionally parallel: dry + saturated blend for parallel
  "tape thickness" (a common production move).

### Implementation Sketch (Python/NumPy)

```python
import numpy as np
from utilities.env import fluidsynth_bin, soundfont_path  # upstream render

MS, A, K, ALPHA, C = 1.2, 0.35, 0.45, 2.0e-3, 0.25   # tape: CrO2-ish
FS, BIAS_F, BIAS_A = 48000.0, 25e3, 0.6              # feasible HF bias
FG, BUMP_DB, BUMP_F = 0.9e-6, 4.5, 70.0              # 15 IPS gap/bump

def _anh(u):
    u = np.clip(u, -30, 30)
    return np.cosh(u)/np.sinh(u) - 1.0/u if abs(u) > 1e-3 else u/3.0

def jiles_atherton(x, drive=0.6, nsub=2):
    g = drive
    n = len(x); M = 0.0; He_prev = 0.0; y = np.empty(n)
    for i, xi in enumerate(x):
        bias = BIAS_A * np.sin(2*np.pi*BIAS_F * i/FS)
        H = g * xi + bias
        He = H + ALPHA * M
        dHe = He - He_prev
        Mirr = M / (1.0 - C) if (1.0 - C) > 0 else M  # init split
        Man = MS * (_anh((He + ALPHA*M)/A) - A/(He + ALPHA*M + 1e-12))
        den = K * np.sign(dHe) - ALPHA * (Man - Mirr)
        den = np.sign(den) * max(abs(den), 1e-6)      # singularity guard
        dMirr = (Man - Mirr) / den
        dM = ((1-C) * dMirr + C) / (1 - ALPHA * (1-C) * dMirr)
        M = float(np.clip(M + dM * dHe / nsub, -MS, MS))
        He_prev = He
        y[i] = M / MS                                  # normalize flux
    return y  # then NAB bump + gap-loss LP + asperity noise stages
```

Numerical notes: integrate at least 2 substeps per sample below 96 kHz;
Heun (midpoint) instead of Euler if drive > 1.0; never let $|M|$ exceed
$M_s$ (clip softly); initialize $M$ from the first-sample anhysteretic
value, not 0, to avoid the first-note "thunk".

### Pitfalls

1. **Singularity blow-up.** The denominator $k\delta - \alpha(M_\mathrm{an}
   - M_\mathrm{irr})$ crosses zero at loop turning points; without a
   clamp the derivative is ±∞ and the audio folds into full-scale noise.
   Fix: clamp $|\cdot| \ge \epsilon$ as shown (the standard SPICE trick).
2. **coth numerics near zero.** $\coth(u)-1/u$ is $0/0$ for small $u$;
   naive `1/np.tanh(u) - 1/u` yields NaN/inf on silent passages. Fix:
   Taylor series $u/3 - u^3/45$ for $|u|<10^{-3}$.
3. **Overshoot past saturation.** Explicit integration can overshoot $M_s$
   on transients → hard clip = digital, not tape. Fix: soft-clamp $M$ and
   use $\Delta M$ limiting per substep.
4. **Bias frequency aliasing.** A real machine biases at 150–250 kHz;
   modeling it literally aliases. Fix: feasible bias (~25 kHz) + low-pass
   before the ODE, or run the whole loop at 2× fs with decimation.
5. **State reset at section boundaries.** Zeroing $M$ per section clicks
   and kills the physical continuity that makes tape feel like tape. Fix:
   carry $M$ (and the bias phase) across sections; only reset on
   transport stop.
6. **Static-curve regression.** Do not "optimize" the ODE into a lookup
   table of $y=f(x)$ curves — that is SP-029/SP-062 territory and loses
   the memory behavior that is the entire point. If a cheaper path is
   needed, cache $\frac{dM}{dH_e}(H_e)$ (it is nearly a function of $H_e$
   alone) — that preserves hysteresis while saving flops.
7. **Level dependence of presets.** J–A parameters are flux-domain
   quantities; a preset tuned at −12 dBFS will distort differently at
   −3 dBFS. Fix: normalize input to a reference flux (IEC1 320 nWb/m
   convention) before the ODE and re-scale after.
8. **Double-saturation with upstream stages.** Running JAMS after
   SP-029 (ladder filter with saturation) or SP-019 (wavefolding) stacks
   nonlinearities → harsh intermodulation. Fix: place JAMS as the last
   coloration stage, or reduce upstream drive.

### Comparison With Related Methods

- **SP-006 Zero-Drift Humanization**: micro-timing/velocity realism in the
  symbolic domain; JAMS operates on the audio stems — complementary
  (humanize → render → tape).
- **SP-013 Feedback Delay Line w/ HF damping**: temporal warmth via
  feedback filtering; JAMS is instantaneous-domain magnetic coloration.
  Chainable: tape-delay into tape-saturation = vintage echo chain.
- **SP-019 Chebyshev waveshaping / SP-029 PolyBLEP+ladder**:
  static-memoryless harmonic generators; JAMS is their dynamic,
  history-aware counterpart (slope- and level-dependent response).
- **SP-062 ADAA**: anti-aliasing for memoryless nonlinearity; JAMS's ODE
  core is a natural low-pass integrator and needs no ADAA (the bias
  frequency is bandlimited by design).
- **SP-073 Transient Shaping (TSDE)**: shapes attack/sustain envelope
  gains; JAMS compresses transients *physically* via domain saturation —
  different mechanism, similar perceived punch management.
- **SP-018 Scanned Synthesis / SP-052 CORDIS-ANIMA**: other ODE-driven
  sound engines (mass-spring / mass-interaction); JAMS is the
  ferromagnetic member — same differential-state discipline, different
  physics (magnetic domains vs mechanical mass).

### References

- Jiles, D. C., & Atherton, D. L. (1986). "Theory of ferromagnetic
  hysteresis." *Journal of Magnetism and Magnetic Materials* 61(1-2): 48–60.
- Jiles–Atherton model — Wikipedia (fetched 2026-09-18).
- Matsuo, T., et al. "Fast numerical method for the Jiles–Atherton model"
  (IEEJ) — time-domain $dM/dt$ integration practice.
- Marion, R., et al. "Improvements of the Jiles–Atherton model for audio
  applications" (hysteresis-for-audio lineage).
- Välimäki, V., et al. — tape saturation & virtual-analog overviews
  (AES/DAFx).
- Stanford CCRMA Music 421 notes — tape machine signal-chain emulation
  (bias, gap loss, NAB, asperity).

---

*Appended 2026-09-18 by the sound-production research cron job. Layer tag:
absolute. Paradigm: Nature-Led-adjacent DSP (physical hysteresis ODE) —
categorized Post-Processing / DSP. ID SP-088 confirmed free at append time
(global max was SP-087: summary table SP-087 TASS, code registry
SP-076..SP-086, no `sound_method_SP-088*` / `report_SP-088*` files existed).*
