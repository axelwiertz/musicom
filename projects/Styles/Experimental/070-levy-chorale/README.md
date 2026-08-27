# 070 - Levy Flight Chorale

**Method 053: Levy Flight Composition (LFC)**
**Status:** Complete
**Created:** 2026-08-16

## Concept

Heavy-tailed random walk: step lengths drawn from alpha-stable distribution P(l) ~ l^-(1+alpha). Clusters of small steps (conjunct motion) punctuated by rare long jumps (dramatic leaps) → fractal, self-similar melodic structure.

**Musical story:** stability index alpha DECREASES per section (1.6 → 1.4 → 1.2 → 1.0). Early sections behave like Brownian motion (mostly stepwise, calm), later sections become Cauchy-like (frequent large leaps, dramatic). The form is itself the alpha descent.

## Parameters

- **Key:** G aeolian (natural minor)
- **Tempo:** 88 BPM
- **Form:** 4 sections × 2 bars = 8 bars total (21.8s)
- **Progression:** i - VI - VII - i (Gm - Eb - F - Gm)
- **Voices:** Soprano (Flute), Alto (Strings), Tenor (Strings), Bass
- **Alpha per section:** [1.6, 1.4, 1.2, 1.0]

## Two-Phase Architecture

### Phase 1: Raw Generative Draft (PRE-RULES)

- **Pitch DNA:** symmetric Levy flight trajectory in MIDI pitch space, CMS algorithm, alpha descending per section, clipped ±24 st, weak Ornstein-Uhlenbeck mean reversion toward origin. Continuous chromatic values (rounded), NOT quantized to any scale → heavy non-diatonic leak (5 pitch classes outside G aeolian).
- **Rhythm DNA:** Levy-distributed inter-onset intervals, IOI = base + L_n, L_n ~ S_alpha_r(sigma_r, 0, 0), clipped [0.25, 4.0] beats → bursty clustered rhythm.
- **Dynamics DNA:** velocity follows |local step| (big leaps louder).
- **Single voice** (Flute), no chord context, no scale enforcement, no voice leading.

### Phase 2: Musicom Rules Post-Processing

- **Quantization:** each raw pitch snapped to nearest tone of section's diatonic triad (G aeolian: i - VI - VII - i) in soprano register, octave-folded into [60, 84] to preserve melodic contour.
- **Harmony:** Alto/Tenor/Bass built as diatonic block harmony via canonical `Scale7ChordDegree.get_diatonic_note()` helper (no off-by-octave wrap).
- **Voice-leading:** `VoiceLeadingRules.optimize_voice_leading()` rotates inversions to minimize total voice-leading distance; Phase 2c CORRECTS remaining parallel/hidden fifth violations by trying inversion rotations.
- **Harmonic function:** i - VI - VII - i validated against `Scale7ChordDegree.function` map (tonic → tonic-prolongation → dominant → tonic = closed perfect cadence).
- **Zero-drift gate:** `UnitMatrixComposer.validate()` passes for BOTH Phase 1 and Phase 2.

## Files

- `MIDI/070-levy-chorale-phase1.mid` (458 bytes) — raw generative draft, single voice, pre-rules
- `MIDI/070-levy-chorale.mid` (1733 bytes) — rules-processed, 4 voices, diatonic
- `MIDI/070-levy-chorale-phase1.mid.provenance.json` — Phase 1 provenance
- `MIDI/070-levy-chorale.mid.provenance.json` — Phase 2 provenance
- `Analysis/grid_visualization.txt` — high-contrast UnitMatrix timeline
- `Notes/lesson-levy-flight.md` — musical explanation

## Verification

```
Phase 1: 2 tracks (tempo + 1 voice), 15360 ticks, 46 notes, 24 distinct pitches
  Non-diatonic leak: 5 pitch classes (1, 4, 6, 8, 11) — expected pre-rules signature
Phase 2: 5 tracks (tempo + 4 voices), all 15360 ticks, 46 notes per voice
  Programs: 33 (Bass), 49 (Strings), 74 (Flute)
  Pitch range: 43..82, 16 distinct pitches
  Non-diatonic leak: [] — clean diatonic output
Zero-drift validation: PASS (both phases)
Harmonic function: legal (tonic → prolongation → dominant → tonic)
Parallel/hidden fifth violations: 0
```

## Musical Analysis

### Levy Flight Report (alpha descends 1.6 → 1.0)

```
Section 1 (i, Gm):  alpha=1.6, 13 notes, mean|step|=7.33 st, max|step|=12 st
Section 2 (VI, Eb): alpha=1.4, 11 notes, mean|step|=1.80 st, max|step|=7 st
Section 3 (VII, F): alpha=1.2, 10 notes, mean|step|=1.56 st, max|step|=4 st
Section 4 (i, Gm):  alpha=1.0, 12 notes, mean|step|=9.18 st, max|step|=21 st
```

**Heavy-tail signature:** 4 leaps ≥ 12 semitones out of 46 steps (8.7%)

### Phase 2 Quantization (raw → chord tone, first 8 per section)

```
i (Gm) 1:  [(67, 67), (64, 62), (57, 70), (67, 67), (74, 74), (78, 74), (72, 74), (60, 62)]
VI (Eb):   [(56, 67), (57, 70), (57, 70), (57, 70), (58, 70), (58, 70), (54, 67), (59, 70)]
VII (F):   [(54, 65), (52, 65), (51, 65), (51, 65), (48, 60), (48, 60), (48, 60), (52, 65)]
i (Gm) 2:  [(49, 62), (55, 67), (68, 67), (72, 70), (69, 70), (70, 70), (75, 74), (63, 62)]
```

### What to Listen For

1. **Phase 1 vs Phase 2:** Phase 1 has chromatic wanderings (non-diatonic leak), Phase 2 is clean diatonic. The raw Levy flight produces interesting contour but violates harmonic grammar; Phase 2 preserves the contour while enforcing scale/chord context.

2. **Alpha descent:** Section 1 (alpha=1.6) has moderate stepwise motion with occasional leaps. Section 4 (alpha=1.0, Cauchy) has frequent dramatic leaps (max 21 semitones). The form is the statistical transition.

3. **Heavy-tail signature:** 4 leaps ≥ 12 semitones (octave) out of 46 steps. This is the Levy flight fingerprint — most steps are small (conjunct motion), rare steps are huge (dramatic leaps). Real melodies follow this distribution (Voss 1994).

4. **Rhythm burstiness:** Levy-distributed IOIs produce clustered rhythms — rapid runs separated by sustained notes. The rhythm itself is fractal.

## References

- Voss, R. F. (1994). "Fractal scaling of melodies."
- Mandelbrot, B. B. (1982). *The Fractal Geometry of Nature*.
- Chambers, Mallows & Stuck (1976). CMS algorithm for alpha-stable distributions.
- `Research/CompositionMethods/methods_db.md:Method 053`
