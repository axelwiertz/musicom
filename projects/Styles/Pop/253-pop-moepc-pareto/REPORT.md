# 253-pop-moepc-pareto — REPORT

Pop × Method **098 Multi-Objective Evolutionary Pareto Composition (MOEPC)**

| Field | Value |
|---|---|
| Project | 253-pop-moepc-pareto |
| Style | Pop |
| Method | 098 — Multi-Objective Evolutionary Pareto Composition (MOEPC) |
| Layer | **concrete** |
| Paradigm | Stochastic · Grid-Locked / Continuous · Macro / Pareto Front · O(I·P·N·M) |
| Key | C major (ionian): C D E F G A B |
| Tempo | 112 BPM · 4/4 · 480 TPB · BAR=1920 |
| Form | intro-verse-chorus-bridge-outro: Intro(4) Verse(8) Chorus(8) Bridge(4) Outro(4) = **28 bars** |
| Date | 2026-10-20 (nightly two-phase job) |

## 1. Method mechanics (Method 098, concrete)

MOEPC evolves a population of candidate melodic genomes with **NSGA-II**
(Deb et al. 2002): SBX crossover + polynomial mutation, fast non-dominated
sorting + crowding distance. Genome = 84 notes × (pitch, onset, duration) =
252 continuous genes.

Four conflicting objectives (all minimized):

1. **harmonic quality** — mean distance (semitones) from each note to the
   nearest C-major scale tone (biases toward key, does NOT force it — raw
   pitch stays unquantized).
2. **melodic quality** — mean absolute interval (conjunctness).
3. **rhythmic coherence** — coefficient of variation of inter-onset gaps.
4. **voice independence** — `1 − contour_interest` (minimizing it maximizes
   melodic independence).

Population 64 × 70 generations → rank-0 Pareto front of **47** non-dominated
melodies. Three archetypes drawn from the front; **the front itself defines
the macro-form**:

| Archetype | f1 harmonic | f2 melodic | f3 rhythmic | f4 (1−interest) | Form role |
|---|---|---|---|---|---|
| smooth | 0.0712 | 0.7755 | 0.4106 | 0.2510 | Intro / Bridge / Outro |
| balanced | 0.0673 | 0.8537 | 0.3622 | 0.1840 | Verse (phase-1 raw) |
| active | 0.0702 | 1.0374 | 0.4762 | 0.1177 | Chorus |

`smooth` is most conjunct (lowest f2) — it books the piece. `active` is most
contour-driven (lowest f4) — it drives the chorus. `balanced` is the central
trade-off and serves as the single-voice phase-1 raw draft.

## 2. Two-phase architecture

**Phase 1 — raw generative draft** (`-phase1.mid`): the *balanced*
Pareto-front melody, single piano voice, unquantized onsets + unquantized
float pitch, no harmony, no chord-tone snapping. 84 notes across 28 bars.

**Phase 2 — musicom rules**:
- front archetypes mapped to sections (smooth → Intro/Bridge/Outro, balanced
  → Verse, active → Chorus; Intro/Outro register −12);
- **chord-tone quantization per bar** against the C-major pop progression;
- **240-tick (8th) grid snap** on every melodic onset;
- full pop texture: Piano lead + Synth Pad + Electric Bass + Glockenspiel
  sparkle + Drum Kit (ch9 backbeat);
- voice-leading optimization (NSGA-II triads → `optimize_voice_leading` →
  greedy rotation/octave correction, 0 parallel/hidden-fifth violations).

## 3. Harmony (C major, I-V-vi-IV pop bestseller)

Per-bar degrees (0=I, 3=IV, 4=V, 5=vi):

```
Intro  (4)   I I V V
Verse  (8)   I V vi IV I V vi IV
Chorus (8)   IV V I vi IV V I V
Bridge (4)   vi V IV V
Outro  (4)   I IV V I
```

Section start roots: `[I, I, IV, vi, I]` — four distinct section openings
(no bar-0 "always tonic" collapse).

## 4. Instrumentation (registry — source of truth)

| Voice | Instrument | Program | Channel | Pitched |
|---|---|---|---|---|
| Lead | Piano | 1 | 0 | ✓ |
| Pad | Synth Pad | 88 | 1 | ✓ |
| Bass | Electric Bass | 33 | 2 | ✓ |
| Sparkle | Glockenspiel | 9 | 3 | ✓ |
| Drums | Drum Kit | 0 | 9 | — |

## 5. Grid audit (perfect == 0 off-grid, humanized > 0)

| Voice | notes | perfect off16/off8 | humanized off16/off8 |
|---|---|---|---|
| Lead | 76 | 0 / 0 | 67 / 67 |
| Pad | 100 | 0 / 0 | 79 / 79 |
| Bass | 84 | 0 / 0 | 84 / 84 |
| Sparkle | 168 | 0 / 0 | 137 / 137 |
| Drums | 297 | 0 / 0 | 224 / 224 |

**Perfect = 0 off-grid on every voice.** Humanized > 0 on every voice — proves
the humanizer ran (off-grid > 0 is the expected signature).

## 6. Harmony audit (scale + chord-tone, must be 0)

| Voice | out-of-scale (perfect/humanized) | out-of-chord (perfect/humanized) |
|---|---|---|
| Lead | 0 / 0 | 0 / 0 |
| Pad | 0 / 0 | 0 / 0 |
| Bass | 0 / 0 | 0 / 0 |
| Sparkle | 0 / 0 | 0 / 0 |

**0 out-of-scale and 0 out-of-chord on every pitched voice, both versions.**
(Chord check snaps the onset to the nearest 8th grid before bar attribution —
humanization never changes pitch, and its ≤18-tick jitter is always < half an
8th, so a boundary note jittered across a bar line is correctly attributed to
its authored bar.)

## 7. Humanization (always-on, style-derived, seeded)

Master seed `HZ_SEED = 25554` (deterministic: `253*101 + 1`), style `pop`
(4.0 ms timing σ, 5.0 velocity σ, 2.0 ms layback, phrase_corr 0.25), per-voice
instrument DNA overrides.

| Voice | seed | n | mean shift (t) | max shift (t) | vel Δ |
|---|---|---|---|---|---|
| Lead (Piano) | 2580954 | 76 | 3.29 | 11 | 4.41 |
| Pad (Synth Pad) | 2580955 | 100 | 1.81 | 6 | 3.33 |
| Bass (Electric Bass) | 2580956 | 84 | **7.89** | 18 | 3.08 |
| Sparkle (Glockenspiel) | 2580957 | 168 | 1.50 | 5 | 4.05 |
| Drums (Drum Kit) | 2580958 | 297 | **1.31** | 4 | 3.26 |

Drums tightest (1.31 t — anchors the groove), bass lays back (+7.89 t — the
+8 ms electric-bass DNA layback), lead loosest relative to accompaniment. All
within profile bounds.

## 8. Zero-drift

Both phase-2 MIDIs: **5 note tracks, all length 53760 ticks** (equal). Phase-1
single-voice gate passed separately. `validate()` passed for both phase-1 and
both phase-2 exports.

## 9. Render + master (real numbers)

Target LUFS for `pop` = **−9.0** (−1 dBTP ceiling). FluidSynth (FluidR3_GM)
→ `master()` → Opus OGG for all three versions (phase-1 unmastered by design).

| Render | target LUFS | integrated LUFS | true peak dBTP | silence | OGG bytes |
|---|---|---|---|---|---|
| phase1 (raw, unmastered) | — | — | — | 0.2694 | 556909 |
| perfect | −9.0 | **−10.37** | **−1.0** | 0.0883 | 538786 |
| humanized | −9.0 | **−10.36** | **−1.0** | 0.0888 | 542491 |

Measured LUFS lands at −10.37 (not −9.0) because the true-peak limiter
(−1 dBTP ceiling) is **binding**: after LUFS normalization the dense pop
texture (drum kit + glockenspiel transients) exceeds −1 dBTP, so the limiter
pulls it back. True-peak is a ceiling, not a target — this is correct
behaviour, not a bug (see `musicom-engine-maintenance` note 2026-10-11).
Silence ratio 8.8% is tail padding after the final note — well under the
30% mid-track-gap suspicion threshold. Phase-1 silence 26.9% is expected for
a sparse single-voice unquantized draft.

## 10. Files

| Artifact | Path | Size (B) |
|---|---|---|
| phase1 MIDI | `MIDI/253-pop-moepc-pareto-phase1.mid` | 769 |
| perfect MIDI | `MIDI/253-pop-moepc-pareto-perfect.mid` | 6275 |
| humanized MIDI | `MIDI/253-pop-moepc-pareto-humanized.mid` | 6276 |
| provenance | `MIDI/*.provenance.json` × 3 | — |
| grid viz | `Analysis/grid_visualization.txt` | — |
| summary | `Analysis/summary.json` | — |
| render stats | `Analysis/render_stats.json` | — |
| audio | `Audio/*.ogg` + `Audio/*.wav` | see §9 |

## 11. Fixes applied during the run

1. **Drum humanization blow-up (451.98 t mean shift)**: drum events were built
   out of grid order within each bar, so the humanizer's forward-clamp
   (`ns = max(prev_start, …)`) collapsed later-but-earlier onsets onto the
   previous one. Fixed by sorting every cell's events by onset in `seal()`
   before packing. Drums now humanize at 1.31 t mean (tightest, correct).
2. **Humanized `out_chord` false positives**: boundary notes jittered ≤18 t
   across a bar line were attributed to the wrong bar by a naive `tt // BAR`.
   Fixed by snapping the onset to the nearest 8th grid (≤18 t is always
   < half an 8th = 120 t, so attribution is lossless). out-of-chord now 0 in
   both versions without masking real violations.

## 12. Verification summary

| Check | Result |
|---|---|
| File sizes > 40 B (6 MIDI/OGG/WAV) | PASS |
| Grid audit — perfect | 0 off-grid (all 5 voices) |
| Grid audit — humanized | > 0 off-grid (humanizer ran) |
| Harmony — out-of-scale | 0 (both versions) |
| Harmony — out-of-chord | 0 (both versions) |
| Zero-drift (equal track lengths) | PASS (5 × 53760 t) |
| Humanization within profile bounds | PASS (drums tightest, bass lays back) |
| Post-master loudness | see render_stats.json (target −9 LUFS) |
| Project numbering | 253 (verified next ID) |
