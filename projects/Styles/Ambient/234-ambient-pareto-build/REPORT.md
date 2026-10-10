# 234-ambient-pareto-build — REPORT

Ambient × Method **098 Multi-Objective Evolutionary Pareto Composition (MOEPC)**

| Field | Value |
|---|---|
| Project | 234-ambient-pareto-build |
| Style | Ambient |
| Method | 098 — Multi-Objective Evolutionary Pareto Composition (MOEPC) |
| Layer | **concrete** |
| Paradigm | Stochastic · Grid-Locked · Macro/Form · O(N) |
| Key | D Aeolian (D E F G A B♭ C) |
| Tempo | 70 BPM · 4/4 · 480 TPB |
| Form | cinematic-build: Intro(4) Build(8) Rise(8) Peak(8) Resolve(4) = 32 bars |
| Date | 2026-10-10 (nightly two-phase job) |

## 1. Method mechanics (Method 098, concrete)

MOEPC is a multi-objective evolutionary algorithm. A population of candidate
melodic genomes is evolved with **NSGA-II** (Deb et al. 2002): SBX crossover +
polynomial mutation, fast non-dominated sorting + crowding distance. Each
genome = 96 notes × (pitch, onset, duration) = 288 continuous genes.

Four conflicting objectives (all minimized):

1. **harmonic quality** — mean distance (semitones) from each note to the
   nearest D-Aeolian scale tone (biases toward key, but does NOT force it —
   raw pitch stays unquantized).
2. **melodic quality** — mean absolute interval (conjunctness).
3. **rhythmic coherence** — coefficient of variation of inter-onset gaps
   (regularity).
4. **voice independence** — `1 − contour_interest` (interest = direction-change
   rate + register spread), so *minimizing* it *maximizes* melodic independence.

Population 64 × 70 generations → rank-0 Pareto front of **58** non-dominated
melodies (many-objective fronts are broad by construction). Three archetypes
are drawn from the front and **the front itself defines the macro-form**:

| Archetype | f1 harmonic | f2 melodic | f3 rhythmic | f4 (1−interest) | Form role |
|---|---|---|---|---|---|
| smooth | 0.0704 | 0.8594 | 0.4791 | 0.1952 | Intro / Resolve |
| balanced | 0.0654 | 1.1585 | 0.4346 | 0.1238 | Build (phase-1 raw) |
| active | 0.0731 | 1.1837 | 0.4376 | 0.1117 | Rise / Peak |

`smooth` is the most conjunct (lowest f2) and least active (highest f4) —
it books the piece. `active` is the most interval/contour driven (lowest f4) —
it drives the climax. `balanced` is the central trade-off and serves as the
single-voice phase-1 raw draft.

## 2. Two-phase architecture

**Phase 1 — raw generative draft** (`-phase1.mid`, 857 B): the *balanced*
Pareto-front melody, single celesta voice, unquantized onsets + unquantized
float pitch, no harmony, no chord-tone snapping. 96 notes across 32 bars.

**Phase 2 — musicom rules** (`234-ambient-pareto-build.mid`, 4468 B):
- front archetypes mapped to sections (smooth → Intro/Resolve, balanced →
  Build, active → Rise/Peak, Peak/Resolve register ±12);
- **chord-tone quantization per bar** against the D-Aeolian modal progression;
- **240-tick (8th) grid snap** on every melodic onset;
- sustained organ pad + cello bass + harp sparkle + sparse cinematic percussion;
- voice-leading optimization + correction, zero-drift gate.

## 3. Form & harmonic progression

D Aeolian modal progression, one degree per bar (0-based: i=0 ii°=1 III=2
iv=3 v=4 VI=5 VII=6). Per-bar roots (no bar-0-tonic bug — each bar carries its
own triad).

| Section | Bars | Degrees | Lead archetype (oct) |
|---|---|---|---|
| Intro | 0-3 | i i VI VI | smooth (−12) |
| Build | 4-11 | i VI VII VI iv i VI VII | balanced (0) |
| Rise | 12-19 | iv v VI VII iv v i VII | active (0) |
| Peak | 20-27 | i VI iv v VI VII i i | active (+12) |
| Resolve | 28-31 | i i VI i | smooth (−12) |

Full bar-degree list: `[0,0,5,5, 0,5,6,5,3,0,5,6, 3,4,5,6,3,4,0,6, 0,5,3,4,5,6,0,0, 0,0,5,0]`

The VI→VII→i is the signature Aeolian cadence; the arc i → (VI VII …) → iv →
v → VI → VII → i → drone traces a cinematic build.

## 4. Voices & instruments (from instrument registry)

| Voice | Registry | Program | Channel | Role |
|---|---|---|---|---|
| Lead | `CELESTA` | 8 | 0 | evolved NSGA-II melody (chord-quantized) |
| Pad | `ORGAN` (Church Organ) | 19 | 1 | sustained triad per bar |
| Bass | `CELLO` | 42 | 2 | root + fifth drone |
| Sparkle | `HARP` (Orchestral Harp) | 46 | 3 | high 8th-note arpeggio |
| Drums | GM kit | 0 | 9 | sparse kick/tom/crash (unpitched) |

## 5. Verification (real numbers)

**Zero-drift**: `validate()` = True for BOTH phases (1×5 and 5×5 matrices);
readback track lengths all equal 61440 ticks.

**Rhythm-grid audit** (120-tick 16th AND 240-tick 8th, all voices):

| Voice | Notes | off16 | off8 | Verdict |
|---|---|---|---|---|
| Lead (Celesta) | 89 | 0 | 0 | PASS |
| Pad (Organ) | 112 | 0 | 0 | PASS |
| Bass (Cello) | 64 | 0 | 0 | PASS |
| Sparkle (Harp) | 192 | 0 | 0 | PASS |
| Drums | 52 | 0 | 0 | PASS |
| **Total** | **509** | **0** | **0** | **PASS** |

**Harmony audit** (pitched voices: Lead, Pad, Bass, Sparkle):

| Voice | Out-of-scale | Out-of-chord | Verdict |
|---|---|---|---|
| Lead | 0 | 0 | PASS |
| Pad | 0 | 0 | PASS |
| Bass | 0 | 0 | PASS |
| Sparkle | 0 | 0 | PASS |
| **Total** | **0** | **0** | **PASS** |

**Voice-leading**: 0 corrections, 0 parallel/hidden-fifth violations.

**Render profile** (SP-001 FluidSynth, `discover_soundfont()` → FluidR3_GM.sf2):

| Artifact | Silence | Peak | RMS mean | Notes |
|---|---|---|---|---|
| phase2 | 9.02 % | 0.5787 | 0.0981 | silence is reverb tail (last ~10 s) |
| phase1 | 30.49 % | 0.4012 | 0.0401 | sparse single-voice raw draft (by design) |

Phase 2 has no mid-track gaps — the 0.08–0.13 RMS body runs continuously; the
9.02 % silence is the FluidSynth reverb tail after the final note. Phase 1's
30.49 % is the expected sparsity of an unquantized single-voice generative
draft (3 notes/bar), not a rendering defect.

## 6. Artifacts

| File | Size |
|---|---|
| MIDI/234-ambient-pareto-build.mid | 4468 B |
| MIDI/234-ambient-pareto-build-phase1.mid | 857 B |
| Audio/234-ambient-pareto-build.ogg | 1052184 B |
| Audio/234-ambient-pareto-build-phase1.ogg | 940796 B |
| Analysis/grid_visualization.txt | — |
| Analysis/summary.json | — |
| Analysis/verification.json | — |
| Analysis/render_stats.json | — |
| provenance sidecars (per MIDI artifact) | — |

WAV intermediates removed per cleanup rule (OGG Opus + MIDI are the deliverables).

## 7. Fixes applied

Two fixes during the grid/harmony audit pass:
1. **Harp off-grid**: original sparkle arpeggio used `k*320`-tick offsets
   (320 not a multiple of 120/240) → 128 off-grid. Replaced with 8th-note
   offsets `[0,240,480,960,1200,1440]`.
2. **Lead boundary chord bug**: chord-tone quantization originally used the
   *pre-snap* onset's bar, so notes near a bar boundary snapped into the next
   bar but kept the old bar's chord → 2 out-of-chord. Fixed by recomputing the
   bar from the *snapped* onset before quantizing; also tightened lead snap
   from 16th (120) to 8th (240) so every onset is on-grid for both audits.

After fixes: grid 0 off-grid, harmony 0 out-of-scale / 0 out-of-chord,
zero-drift both phases.
