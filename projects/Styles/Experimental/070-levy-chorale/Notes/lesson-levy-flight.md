# Lesson: Levy Flight Composition (Method 053)

## What is a Levy Flight?

A Levy flight is a random walk where step lengths follow a heavy-tailed power-law distribution P(l) ~ l^-(1+alpha). Unlike Gaussian random walks (Brownian motion, alpha=2), Levy flights produce trajectories characterized by **clusters of short steps** interspersed with **rare but very long jumps**.

**Musical insight:** Voss (1994) showed that pitch intervals in real melodies (folk songs, classical themes, jazz solos) follow power laws with alpha ~ 1.0-1.5. Levy flights don't impose an artificial model — they capture the statistical structure that already exists in human-composed music.

## The Alpha Parameter

The stability index alpha controls the balance between conjunct motion (small steps) and leaping motion (large jumps):

- **alpha = 2.0:** Gaussian Brownian motion (all steps moderate, no extreme leaps)
- **alpha = 1.5:** Typical melody (mostly stepwise, occasional leaps of 3rds-5ths)
- **alpha = 1.0:** Cauchy distribution (frequent large leaps, highly dramatic contour)
- **alpha = 0.5:** Extremely heavy-tailed (rare but massive jumps, mostly static)

## This Composition

**Form as alpha descent:** alpha decreases per section (1.6 → 1.4 → 1.2 → 1.0). The piece evolves from Brownian stepwise motion (calm, conjunct) to Cauchy-like leaping (dramatic, wide intervals). The statistical transition IS the form.

**Heavy-tail signature:** 4 leaps ≥ 12 semitones (octave) out of 46 steps (8.7%). Most steps are small (mean 1.5-9 st), rare steps are huge (max 21 st). This is the Levy flight fingerprint.

## Two-Phase Architecture

### Phase 1: Raw Generative Draft (PRE-RULES)

- Pitch = continuous chromatic accumulation (alpha-stable steps) → heavy non-diatonic leak (5 pitch classes outside G aeolian)
- Rhythm = Levy-distributed inter-onset intervals (bursty clusters)
- Velocity = follows |local step| (big leaps louder)
- Single voice, no scale enforcement, no chord context, no voice leading

**What to listen for:** chromatic wanderings, non-diatonic tones, interesting contour but violates harmonic grammar.

### Phase 2: Musicom Rules Post-Processing

- Quantize raw pitches to nearest chord tone (octave-folded to preserve contour)
- Build diatonic block harmony (Alto/Tenor/Bass via `Scale7ChordDegree.get_diatonic_note()`)
- Apply voice-leading rules (optimize inversions, correct parallel/hidden fifths)
- Validate harmonic function (i → VI → VII → i = tonic → prolongation → dominant → tonic)

**What to listen for:** clean diatonic output, preserved melodic contour, proper voice leading, harmonic coherence.

## Comparison: Phase 1 vs Phase 2

| Aspect | Phase 1 (Raw) | Phase 2 (Rules) |
|--------|---------------|-----------------|
| Pitch set | Chromatic (24 distinct) | Diatonic (16 distinct) |
| Non-diatonic leak | 5 pitch classes | 0 |
| Voices | 1 (Flute) | 4 (Soprano/Alto/Tenor/Bass) |
| Harmonic context | None | Section triads (Gm-Eb-F-Gm) |
| Voice leading | None | Classical rules applied |
| Musical effect | Interesting contour, harmonic violations | Coherent, listenable, grammatical |

## CMS Algorithm (Chambers-Mallows-Stuck)

The CMS algorithm generates samples from the symmetric alpha-stable distribution:

```python
def levy_stable_sample(alpha, sigma, size=1):
    if alpha == 2.0:  # Gaussian
        return sigma * np.random.randn(size)
    if alpha == 1.0:  # Cauchy
        return sigma * np.tan(np.pi * (np.random.rand(size) - 0.5))
    # General CMS (Nolan form, guaranteed-positive bases)
    U = np.random.uniform(-pi/2, pi/2, size)
    W = np.random.exponential(1.0, size)
    S = np.sign(np.random.randn(size))  # Rademacher
    X = S * sigma * (sin(alpha*U) / cos(U)^(1/alpha)) * ((cos(U*(1-alpha)) / W)^((1-alpha)/alpha))
    return X
```

**Key:** Nolan form uses `cos(U)` and `cos(U*(1-alpha))` as bases, which are guaranteed positive for |U| < pi/2 and alpha in (0, 2], avoiding complex number leakage.

## Pitfalls

1. **Infinite variance:** For alpha < 2, variance is infinite → extreme values occur more frequently than Gaussian. Clip step sizes to ±24 semitones to prevent unplayable leaps.

2. **Undefined mean:** For alpha ≤ 1, mean is undefined → flight can drift arbitrarily far. Add weak Ornstein-Uhlenbeck mean reversion (pull toward origin) to prevent wandering off.

3. **Complex number leakage:** Original CMS formula can produce negative bases raised to fractional powers → complex numbers. Use Nolan form (guaranteed-positive bases).

4. **Scale quantization bias:** Levy flights produce continuous pitch values; quantizing to discrete scale degrees can introduce bias. Octave-fold raw pitch into soprano register first to preserve contour.

5. **Monotone collapse:** If raw pitches all fall below the chord tone range, quantization collapses to one repeated note. Octave-fold + widen candidate range (lo=60, hi=84) to spread pitches.

## References

- Voss, R. F. (1994). "Fractal scaling of melodies."
- Mandelbrot, B. B. (1982). *The Fractal Geometry of Nature*. W. H. Freeman.
- Shlesinger, West & Klafter (1987). "Lévy dynamics of enhanced diffusion." *Physical Review Letters*, 58(11), 1100–1107.
- Chambers, Mallows & Stuck (1976). CMS algorithm for alpha-stable distributions.
- `Research/CompositionMethods/methods_db.md:Method 053`
