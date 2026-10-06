# REPORT — 226-apollonian-packing

Autonomous nightly composition job · 2026-10-06 · job `1fc3fd65d359`

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Experimental** (random from `Styles/` genre folders, excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered dirs + `Celtic ` dup) |
| Method | **094 — Apollonian Circle Packing Composition (ACPC)** (Nature-Led, Pitch/Rhythm/Harmony/Structure/Texture, O(3^D)) |
| Layer | **concrete** |
| Seed | 20261006 (date-seeded RNG) |
| Layer roll | `rng.random()` = **0.4948** ≥ 1/7 → *concrete* (the ~6-of-7 cadence) |
| Excluded (last 7d) | methods used 2026-09-29 → 10-05: **007, 019, 025, 031, 041, 050, 095, 213, 217** |
| Candidate pool | 94 concrete methods after exclusion |

The last abstract-layer job was 2026-10-03 (220-funk, method 095 Contour Theory).
This night the date-seeded roll landed concrete (0.4948), as expected by the
6-of-7 cadence; the abstract slot for this week is already satisfied.

## 2. Method essence (094 Apollonian Circle Packing)

Recursive **integral Apollonian circle packings** under Descartes' kissing-circle
theorem. Root quadruple **v₀ = (−1, 2, 2, 3)** (−1 = the enclosing bounding circle).
Every Descartes quadruple of mutually-tangent curvatures satisfies

```
(k1+k2+k3+k4)² = 2·Σ ki²
```

and Vieta's formula gives the Apollonian reflection `ki' = 2·Σ_{j≠i} kj − ki`,
so every inscribed circle has **exact integer curvature** (Graham–Lagarias–Mallows–
Wilks–Yan 2003). Musical mappings:

- **curvature k → scale degree (k mod 7)** (pitch)
- **radius r = 1/k → fractal duration** (big circle = long tone; micro-circle = 16th figuration)
- **mutually-tangent quadruple = 4-voice consonant chord** (Bass/Tenor/Alto/Soprano)
- **Apollonian reflection = parsimonious voice-leading** (3 voices hold, 1 pivots)

## 3. Musical parameters

| Field | Value |
|---|---|
| Key | **D Dorian** — D E F G A B C → pc `{0,2,4,5,7,9,11}`, tonic D |
| Tempo | 90 BPM |
| Meter | 4/4 · 480 TPB · BAR = 1920 · 16th = 120 · 8th = 240 · total = 46080 ticks |
| Form | 6 sections × 4 bars = **24 bars** (Seed → Growth → Branching → Canopy → Micro → Coda) |
| Arc | 20 bars of monotonically rising fractal density (quads sorted by depth, then max curvature), then 4-bar coda returning to the spacious root region |

## 4. Two-phase architecture

**Phase 1 (raw draft, single voice):** a lead flute walks a *deep* Apollonian
curvature stream — every positive curvature of the packing out to depth 7 — with
unquantized pitch (register drifts up with `5·log₂(k)+3·depth`, ±1.5 semitone
micro-jitter), **off-grid onsets** (±30-tick jitter), and fractal radii durations.
No scale/chord snapping. Exported as `-phase1.mid` with its own `validate()` gate
(PASS).

**Phase 2 (musicom rules):** 16th-grid snap (120-tick) → per-bar chord-tone
quantization to the **Descartes-quadruple chord** → per-voice register clamp →
full 4-voice texture. Exported as `.mid`. `validate()` gate PASS.

## 5. Voices & instruments (from registry)

| Voice | Instrument | Program | Channel | Register (D Dorian ladder) |
|---|---|---|---|---|
| Bass | Double Bass | 43 | 0 | D2 E2 F2 G2 A2 B2 C3 (38–48) |
| Tenor | Cello | 42 | 1 | D3 E3 F3 G3 A3 B3 C4 (50–60) |
| Alto | Violin | 40 | 2 | D4 E4 F4 G4 A4 B4 C5 (62–72) |
| Soprano | Flute | 74 | 3 | D5 E5 F5 G5 A5 B5 C6 (74–84) |

Each voice holds its circle's chord tone on strong subdivision slots and exchanges
into a neighbouring chord tone of the *same* Descartes quadruple on weak slots —
motion stays inside the bar's chord (this is what keeps the harmony audit at 0).

## 6. Progression (24 Descartes quadruples → chords, D Dorian degrees)

| Bar | Section | Depth | Quadruple (k1,k2,k3,k4) | Chord (notes) | Born k |
|---|---|---|---|---|---|
| 0 | Seed | 0 | (−1, 2, 2, 3) | D·F·G | — |
| 1 | Seed | 1 | (−1, 6, 2, 3) | D·F·G·C | 6 |
| 2 | Seed | 1 | (15, 2, 2, 3) | E·F·G | 15 |
| 3 | Seed | 2 | (−1, 6, 2, 11) | D·F·A·C | 11 |
| 4 | Growth | 2 | (−1, 6, 14, 3) | D·G·C | 14 |
| 5 | Growth | 2 | (23, 6, 2, 3) | F·G·C | 23 |
| 6 | Growth | 2 | (15, 2, 2, 35) | D·E·F | 35 |
| 7 | Growth | 2 | (15, 38, 2, 3) | E·F·G | 38 |
| 8 | Branching | 3 | (−1, 18, 2, 11) | D·F·A | 18 |
| 9 | Branching | 3 | (−1, 26, 14, 3) | D·G·B | 26 |
| 10 | Branching | 3 | (−1, 6, 30, 11) | D·F·A·C | 30 |
| 11 | Branching | 3 | (−1, 6, 14, 35) | D·C | 35 |
| 12 | Canopy | 3 | (39, 6, 2, 11) | F·A·C | 39 |
| 13 | Canopy | 3 | (47, 6, 14, 3) | D·G·B·C | 47 |
| 14 | Canopy | 3 | (23, 50, 2, 3) | E·F·G | 50 |
| 15 | Canopy | 3 | (23, 6, 2, 59) | F·G·C | 59 |
| 16 | Micro | 3 | (23, 6, 62, 3) | F·G·C | 62 |
| 17 | Micro | 3 | (63, 2, 2, 35) | D·F | 63 |
| 18 | Micro | 3 | (71, 38, 2, 3) | E·F·G | 71 |
| 19 | Micro | 3 | (15, 102, 2, 35) | D·E·F·A | 102 |
| 20 | Coda | 0 | (−1, 2, 2, 3) | D·F·G | — |
| 21 | Coda | 1 | (−1, 6, 2, 3) | D·F·G·C | 6 |
| 22 | Coda | 1 | (15, 2, 2, 3) | E·F·G | 15 |
| 23 | Coda | 2 | (−1, 6, 2, 11) | D·F·A·C | 11 |

The chord is the *set* of pitch classes the quadruple maps into D Dorian; a `−1`
curvature resolves to the tonic D pedal. Subdivision per voice is radius-derived:
k≤0 → whole-bar pedal, k≤5 → half notes, k≤15 → quarters, k≤40 → eighths, k>40 → 16ths.

## 7. GRID audit (phase-2 MIDI read-back via mido, 16th = 120 ticks)

| Track | Notes | off-16th | off-8th | out-of-key | out-of-chord |
|---|---|---|---|---|---|
| Bass (ch0) | 119 | **0** | 24 | **0** | **0** |
| Tenor (ch1) | 124 | **0** | 16 | **0** | **0** |
| Alto (ch2) | 76 | **0** | 8 | **0** | **0** |
| Soprano (ch3) | 96 | **0** | 8 | **0** | **0** |
| **TOTAL** | **415** | **0** | 56 | **0** | **0** |

**Verdict: PASS.** 0 onsets off the 16th grid (the project-078 drift bug class —
onsets at non-grid ticks like 295 — is absent). The 56 "off-8th" counts are the
*intentional* 16th-note offbeats (120/360/600/…), which sit exactly on the 16th
grid; the method's "micro-circle → 16th-note figuration" mapping requires them.
No voice drifts against the grid.

## 8. HARMONY audit (every pitched note vs key scale and bar chord)

| Track | out-of-key (pc ∉ {0,2,4,5,7,9,11}) | out-of-chord (pc ∉ bar quadruple) |
|---|---|---|
| Bass | 0 | 0 |
| Tenor | 0 | 0 |
| Alto | 0 | 0 |
| Soprano | 0 | 0 |
| **TOTAL** | **0** | **0** |

**Verdict: PASS.** Every one of the 415 pitched notes is a D-Dorian scale tone AND
a chord tone of its bar's Descartes quadruple. (No project-078-style foreign-key
counterline.)

## 9. Voice-leading check (outer voices Bass + Soprano, classical rules)

3 flags out of 23 bar transitions (parallel/hidden perfect intervals). These are
inherent to parsimonious common-tone voice leading (both outer voices occasionally
step by the same interval into an octave/fifth while the inner voices hold). Reported
as-informational; the hard gates are grid + harmony (both 0). No forced correction
applied — altering a voice would break the Descartes-quadruple chord mapping.

## 10. Zero-drift status

| Phase | validate() | Result |
|---|---|---|
| Phase 1 (`-phase1.mid`) | `UnitMatrixComposer.validate()` | **PASS** (equal-length track, terminal pad) |
| Phase 2 (`.mid`) | `UnitMatrixComposer.validate()` | **PASS** (4 tracks, all cells land on section boundary) |

All cells end exactly at the section boundary (terminal landmark
`MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)` when needed).

## 11. Render profile (FluidSynth FluidR3_GM → WAV → Opus OGG)

| Metric | Phase 1 | Phase 2 |
|---|---|---|
| Duration | 66.24 s | 66.59 s |
| Peak | 0.712 | 0.501 |
| Silence ratio | **3.04%** | **4.11%** |
| RMS mean | 0.1237 | 0.0802 |
| RMS max | 0.2022 | 0.1194 |
| Mid-track silent windows (1 s) | 0 | 0 |
| SoundFont | FluidR3_GM.sf2 | FluidR3_GM.sf2 |

Both renders are healthy: no mid-track gaps (silence is only note-release + tail),
no clipping (peak < 0.75), continuous RMS. Pitch fidelity is inherent to
FluidSynth MIDI→soundfont rendering (each MIDI note triggers its pitched sample);
tonal content is additionally guaranteed by the §7–§8 audits. No custom synthesis
engine was used, so no FFT/autocorrelation pitch test is required.

## 12. Files

| Path | Size | Note |
|---|---|---|
| `MIDI/226-apollonian-packing-phase1.mid` | 1154 B | raw draft (single voice, off-grid) |
| `MIDI/226-apollonian-packing.mid` | 3786 B | rules-processed 4-voice |
| `MIDI/*.mid.provenance.json` (×2) | — | provenance sidecars (phase flag) |
| `Audio/226-apollonian-packing-phase1.ogg` | 644054 B | Opus 48k voip |
| `Audio/226-apollonian-packing.ogg` | 461370 B | Opus 48k voip |
| `Audio/*.wav` (×2) | ~11.7 MB | FluidSynth 16-bit stereo |
| `Analysis/grid_visualization.txt` | — | high-contrast timeline |
| `Analysis/summary.json` | — | selection + progression + audits |
| `Analysis/render_stats.json` | — | silence/RMS/pitch profile |

## 13. Fixes applied this run

1. **Phase-1 sparsity (85.6% → 3.0% silence):** the initial raw draft walked only
   the ~22 "born" curvatures of the 24-bar arc, leaving ~60 s of trailing silence.
   Fixed by walking a *deep* Apollonian curvature stream (every positive curvature
   to depth 7) so the raw voice fills the full 46080-tick timeline continuously.
2. **Preflight compliance:** removed a stale `sys.path.insert(..., "…/musicom")`
   from the render script (`sound.render.fluidsynth` is flat-importable from the
   editable install); annotated the mido import as reading-only. `preflight_check.py`
   now exits 0 (COMPLIANT).

## 14. Verification summary

```
grid 16th off-grid : 0 / 415   (PASS)
out-of-key          : 0 / 415   (PASS)
out-of-chord        : 0 / 415   (PASS)
zero-drift (both)   : PASS
silence (phase2)    : 4.11 %    (healthy)
preflight           : COMPLIANT
```
