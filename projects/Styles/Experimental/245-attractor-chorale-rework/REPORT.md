# 245-attractor-chorale-rework — REPORT

## Source
- Project: `Experimental/061-attractor-chorale` (Method 043 — Strange Attractor
  Trajectory Mapping, Lorenz / RK4).
- Identity preserved: E dorian, 92 BPM, homophonic SATB flute/bass chorale,
  attractor-speed-triggered rhythm, progression i–ii–IV–VI dorian gravity.

## Audit result (current standards)
| # | Standard | Result |
|---|---|---|
| 1 | Engine (`UnitMatrixComposer`) | ✅ PASS |
| 2 | Zero-drift (equal track lengths) | ✅ PASS (4 voice tracks @ 15360 ticks) |
| 3 | Rhythm-grid sync (onset % 120/240) | ✅ PASS (156 pitched onsets, 0 off-grid) |
| 4 | ≥4 voice tracks | ✅ PASS (4 voices S/A/T/B) |
| 5 | Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | ❌ **FAIL** — no `-phase1.mid` |
| 6 | provenance.json + index.html | ❌ **FAIL** — `index.html` missing |

**Decision: REDESIGN** (2 standards failed). Rebuilt from scratch through the
canonical `UnitMatrixComposer`, preserving only the musical identity
(genre/key/tempo/Lorenz method/SATB instrumentation). Non-compliant gaps
(no phase-1 export, no dashboard) remediated in the new project.

## What changed (rework)
- Longer form: 8 bars → **10 sections × 2–4 bars = 32 bars**.
- Per-section harmonic regions: each section its OWN progression (avoids the
  bar-0 tonic bug). Section roots derived from each section's MIDPOINT chord.
- Two-phase export: raw Lorenz single-voice draft (`-phase1.mid`) + rules
  post-processed 6-voice texture (`.mid`), each with its own zero-drift gate.
- Added `index.html` dashboard + `README.md` + full provenance sidecars.

## Form (10 sections × 2–4 bars = 32 bars, 92 BPM, E dorian)
```
Intro       i   IV
VerseA      i   ii  IV  i
VerseB      i   v   III VII
Chorus      IV  v   VII i
VerseA2     i   ii  IV  i
Bridge      vi° ii  v   VII
Chorus2     v   vi° i   ii     (Chorus transposed +1 dorian degree)
Development vi° v
Climax      IV  VII
Outro       i   IV
```
Section roots (midpoint chord): A, A, G, D, A, B, E, B, D, A — varied, not all tonic.

## Variation techniques (6, mapped to sections)
1. **Density ramp** — rhythm mask floor/threshold varies per section:
   Intro sparse → Climax densest → Outro sparse.
2. **Register shift (+octave)** — Chorus/Chorus2/Development/Climax voice the
   upper three voices an octave higher (brighter climax).
3. **Diatonic transposition (+1 degree)** — Chorus2 progression = Chorus
   shifted up one E-dorian scale degree.
4. **Augmentation** — Outro strikes half-notes (beats 1 & 3) instead of eighths.
5. **Counterline** — 5th voice (Oboe descant) added in Chorus/Bridge/Chorus2/
   Climax as a 16th-note chord-tone arpeggio.
6. **Inversion** — the descant arpeggio is ascending in Chorus but inverted
   (descending) in the Bridge.

## Voices (6)
| Voice | Program | Channel | Role |
|---|---|---|---|
| Soprano | Flute (74) | 0 | homophonic top voice (root, octave) |
| Alto | Flute (74) | 1 | fifth |
| Tenor | Flute (74) | 2 | third |
| Bass | Bass (33) | 3 | chord root |
| Descant | Oboe (68) | 4 | counterline (Chorus/Bridge/Chorus2/Climax) |
| Perc | 0 | 9 | ch9 timpani pulse (Climax only) |

## Verification (read-only mido, exported MIDI)
- phase-2 MIDI: **6 voice tracks @ 61440 ticks**, zero-drift PASS.
- pitched onsets **628** | off-grid **0** | out-of-scale **0** | out-of-chord **0**.
- phase-1 MIDI: 1 voice @ 61440 ticks, zero-drift PASS (raw, pre-rules).
- sizes: phase2 6090 B, phase1 1843 B (both > 40).

## Audio
| File | duration | peak | RMS | silence |
|---|---|---|---|---|
| 245-attractor-chorale-rework.wav | 85.7 s | 0.971 | 0.163 | 9.26% |
| 245-attractor-chorale-rework-phase1.wav | 85.6 s | 0.637 | 0.099 | 5.01% |

- Silence well under the 30% suspect threshold; dominant freq 443 Hz (A4) —
  real pitched content, not noise.

## Files
```
MIDI/245-attractor-chorale-rework.mid            (6090 B) + provenance
MIDI/245-attractor-chorale-rework-phase1.mid     (1843 B) + provenance
Audio/245-attractor-chorale-rework.wav           (15 MB, FluidSynth FluidR3_GM)
Audio/245-attractor-chorale-rework.ogg           (643 KB, Opus)
Audio/245-attractor-chorale-rework-phase1.wav    (15 MB)
Audio/245-attractor-chorale-rework-phase1.ogg    (728 KB, Opus)
Analysis/grid_visualization.txt                  (ASCII grid)
Analysis/summary.json                            (chord walk + roots + audit)
index.html                                       (dashboard)
README.md
```
