# 232-japanese-isorhythmic — REPORT

Japanese × Method 032 **Isorhythmic Talea-Color Mapping** (ITCM)

| Field | Value |
|---|---|
| Project | 232-japanese-isorhythmic |
| Style | Japanese |
| Method | 032 — Isorhythmic Talea-Color Mapping (ITCM) |
| Layer | **concrete** |
| Paradigm | Rules-Based · Grid-Locked · Macro/Cycle · O(N) |
| Key | D Phrygian (D Eb F G A Bb C) |
| Tempo | 76 BPM · 4/4 · 480 TPB |
| Form | 8 sections × 2 bars = 16 bars |
| Date | 2026-10-09 (nightly two-phase job) |

## 1. Method mechanics (Method 032, concrete)

Isorhythm is the medieval motet technique (Machaut, ca. 1360) of **decoupling a
fixed pitch sequence (COLOR) from a fixed rhythm sequence (TALEA)** and letting
their coprime lengths slide against each other.

- **COLOR** = fixed 7-note pitch sequence, expressed as Phrygian scale degrees
  (0-based): `[0, 1, 3, 4, 6, 4, 3]` → D Eb G A C A G. This is exactly the
  Japanese *in-sen* pentatonic (D Eb G A C = degrees 0,1,3,4,6) with an A→G
  descent — the koto/honkyoku color DNA.
- **TALEA** = fixed 5-duration rhythm in ticks: `[480, 240, 480, 240, 480]`
  (quarter, eighth, quarter, eighth, quarter), summing to exactly 1 bar (1920).
- **gcd(7, 5) = 1** (coprime) → the combined pattern re-aligns only after
  **lcm(7,5) = 35 notes = 7 bars**. Every color statement lands on a different
  metric position than the last, so the melody perpetually "shifts" against the
  bar grid — the audible isorhythmic signature.

Because Method 032 is Grid-Locked and diatonic by construction, Phase 1's
"rawness" is the *absence of harmonic context and chord-tone snapping*, not
microtonal pitch — the raw draft is the pure color×talea stream (80 notes,
single koto voice).

## 2. Two-phase architecture

**Phase 1 — raw generative draft** (`-phase1.mid`, 768 B):
single koto voice running the pure color×talea stream, identity color, octave 0,
no harmony, no chord-tone quantization. 80 events across 16 bars.

**Phase 2 — musicom rules** (`232-japanese-isorhythmic.mid`, 2756 B):
- the TALEA rhythm is preserved **exactly** (isorhythmic identity survives);
- the color contour is **chord-tone-quantized per bar** against the D Phrygian
  modal progression;
- added shakuhachi sustained counterline (1 chord tone/bar), shamisen 8th-note
  arpeggio (1 octave down), taiko DON + GM percussion pulse;
- rhythm-grid snap (120-tick), diatonic block harmony, voice-leading
  optimization + correction, zero-drift gate.

## 3. Form & harmonic progression

D Phrygian modal progression, one degree per bar (0-based: i=0 ♭II=1 ♭III=2
iv=3 v°=4 ♭VI=5 ♭vii=6). Section midpoint degree drives each section root
(no bar-0-tonic bug).

| Section | Bars | Degrees | Midpoint | Color transform |
|---|---|---|---|---|
| Intro | 0-1 | i ♭II | ♭II | identity, oct −12, ×2.0 |
| TaleaA | 2-3 | ♭II ♭vii | ♭vii | identity, oct 0 |
| TaleaB | 4-5 | ♭vii ♭VI | ♭VI | **retrograde**, oct 0 |
| Dev | 6-7 | ♭VI iv | iv | **inversion**, oct 0 |
| TaleaA2 | 8-9 | iv ♭II | ♭II | identity, oct **+12** |
| Climax | 10-11 | ♭II i | i | identity, oct +12, **×0.5** |
| Coda1 | 12-13 | i i | i | retrograde, oct −12, ×2.0 |
| Coda2 | 14-15 | i i | i | identity, oct 0, resolve |

Full bar-degree list: `[0,1, 1,6, 6,5, 5,3, 3,1, 1,0, 0,0, 0,0]`

The ♭II → i (Neapolitan) is the signature Phrygian/Japanese cadence; the
progression arcs i → ♭II → ♭vii → ♭VI → iv → ♭II → i → drone.

Variation techniques applied (≥3): retrograde color, inversion color,
augmentation ×2.0, diminution ×0.5, transposition/register shift (±12),
density rise (Climax 8th hi-hat + taiko off-beat).

## 4. Voices & instruments (from instrument registry)

| Voice | Registry | Program | Channel | Role |
|---|---|---|---|---|
| Koto | `KOTO` | 107 | 0 | isorhythmic lead (color × talea) |
| Shakuhachi | `SHAKUCHACHI` | 77 | 1 | sustained chord-tone counterline |
| Shamisen | `SHAMISEN` | 106 | 2 | 8th-note arpeggio texture |
| Taiko | `TAIKO` | 116 | 3 | deep DON hits (unpitched) |
| Drums | GM kit | 0 | 9 | sparse pulse (unpitched) |

## 5. Verification (real numbers)

**Zero-drift**: `validate()` = True for BOTH phases (5×8 and 1×8 matrices).

**Rhythm-grid audit** (120-tick grid, every pitched + unpitched voice):

| Voice | Notes | Off-grid | Verdict |
|---|---|---|---|
| Koto | 80 | 0 | PASS |
| Shakuhachi | 16 | 0 | PASS |
| Shamisen | 128 | 0 | PASS |
| Taiko | 18 | 0 | PASS |
| Drums | 48 | 0 | PASS |
| **Total** | **290** | **0** | **PASS** |

**Harmony audit** (pitched voices: Koto, Shakuhachi, Shamisen):

| Voice | Out-of-scale | Out-of-chord | Verdict |
|---|---|---|---|
| Koto | 0 | 0 | PASS |
| Shakuhachi | 0 | 0 | PASS |
| Shamisen | 0 | 0 | PASS |
| **Total** | **0** | **0** | **PASS** |

**Voice-leading**: 0 corrections, 0 parallel/hidden-fifth violations.

**Render profile** (SP-001 FluidSynth, discover_soundfont):

| Artifact | Silence | Peak | RMS mean |
|---|---|---|---|
| phase2 WAV | 7.79 % | 0.7378 | 0.0810 |
| phase1 WAV | 9.31 % | 0.3446 | 0.0378 |

Silence well under the 30 % suspect threshold; no mid-track gaps (tail padding
only). Peak < 1.0 (no clipping).

## 6. Artifacts

| File | Size |
|---|---|
| MIDI/232-japanese-isorhythmic.mid | 2756 B |
| MIDI/232-japanese-isorhythmic-phase1.mid | 768 B |
| Audio/232-japanese-isorhythmic.ogg | 430852 B |
| Audio/232-japanese-isorhythmic-phase1.ogg | 494832 B |
| Audio/232-japanese-isorhythmic.wav | 9651500 B (gitignored) |
| Audio/232-japanese-isorhythmic-phase1.wav | 9542956 B (gitignored) |
| Analysis/grid_visualization.txt | — |
| Analysis/summary.json | — |
| Analysis/render_stats.json | — |
| provenance sidecars (per MIDI/WAV artifact) | — |

## 7. Fixes applied

None. Clean first pass — all gates passed on the first run (grid 0 off-grid,
harmony 0 out-of-scale / 0 out-of-chord, zero-drift both phases).
