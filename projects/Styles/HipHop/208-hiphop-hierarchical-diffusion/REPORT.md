# REPORT — 208-hiphop-hierarchical-diffusion

**Project:** 208-hiphop-hierarchical-diffusion
**Style:** HipHop (boom-bap backbeat, sub bass, chord stabs, swung 16ths)
**Method:** 010 Hierarchical Diffusion (Stochastic, Structure/Texture)
**Layer:** `concrete`
**Date:** 2026-09-27 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20260927
**Key:** A natural minor = A B C D E F G = pitch classes {9, 11, 0, 2, 4, 5, 7}
**BPM:** 90 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240)

---

## 1. Selection

| Field | Value |
|---|---|
| Style | **HipHop** — random pick from `/opt/data/repos/musicom/projects/Styles/` genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `), seed 20260927. |
| Method | **010 Hierarchical Diffusion** — `concrete` layer. Multi-level top-down step-wise expansion from macro plans to MIDI events. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, method 095 Contour Theory). |
| Recent-method exclusion | Excluded methods used in the last 7 days: {001, 016, 019, 025, 040, 048, 069, 075}. Random pick from the remaining 89 concrete methods landed on **010**. |

## 2. Method essence (010 Hierarchical Diffusion)

Multi-level top-down step-wise expansion, diffused from macro plan down to MIDI
events. Four explicit levels:

| Level | Macro -> micro | This composition |
|---|---|---|
| L0 | Macro form plan | 8 sections, each a density target + harmonic region (per-section density) |
| L1 | Section -> bars | 4 bars per section, each bar one chord from the progression |
| L2 | Bar -> onset slots | Recursive binary split (Galton-Watson branching): a bar-span token splits into two children with probability `p = density * 0.9^level`, else becomes a leaf onset at a jittered position |
| L3 | Onset -> pitch | Ornstein-Uhlenbeck drift-diffusion: `p += 0.30*(root_target - p) + N(0, 2.5)` — a pitch random walk with a restoring drift toward the current chord root |

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | Intro → Verse → Chorus → Verse2 → Chorus2 → Bridge → Chorus3 → Outro (8 sections × 4 bars = **32 bars**) |
| Key | **A natural minor** |
| Meter | 4/4, 90 BPM |
| Grid | 480 TPB → 16th = 120, 8th = 240, bar = 1920, section = 7680, total = 61440 ticks (~85.3 s) |
| Progression | **i–VI–III–VII** (Am–F–C–G); Bridge = VI–III–VII–i (F–C–G–Am, darker turn); Intro/Outro pedal Am |

Per-section density (L0 macro plan, drives onset branching):
Intro 0.35 · Verse 0.55 · Chorus 0.78 · Verse2 0.55 · Chorus2 0.82 · Bridge 0.48 · Chorus3 0.78 · Outro 0.30.

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| LeadHook | Piano | 1 | 0 | Diffused chord-tone hook (Ornstein-Uhlenbeck pitch walk) |
| KeysPad | Church Organ | 19 | 1 | Sustained chord pad (whole-bar voicing) |
| SubBass | Double Bass | 43 | 2 | Deep root bass on beats 1/3 + upbeat push |
| SparkleStab | Celesta | 8 | 3 | High chord stabs on off-beats (16th steps 6/14) |
| Drums | Drum Kit | 0 (ch9) | 9 | Boom-bap backbeat: kick 1/3, snare 2/4, 8th hats, open hat on 4& |

All instrument programs resolved via `instrument_registry.py` (source of truth),
not the 10-entry `MidiInstrument` enum.

## 5. Two-Phase Architecture

### Phase 1 — Raw Diffusion Draft (`-phase1.mid`)
- Single voice (Raw_Lead, Piano).
- **Onsets** unquantized: hierarchical-diffused bar positions + micro-jitter
  (±25 ticks) OFF the 120/240 grid.
- **Pitch** unquantized: raw Ornstein-Uhlenbeck drift-diffusion (chromatic),
  NOT snapped to key/chord.
- No harmony, no chord-tone quantization, no texture. This is the raw method
  output. Zero-drift terminal landmark per section; `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- **Same diffusion** re-run with the same seed → identical raw material, then:
  1. every onset snapped to the **16th grid** (120 ticks),
  2. every pitch snapped to its **bar's chord tones** (A natural minor).
- Full 5-voice hip-hop texture added. Zero-drift landmarks; `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit (every voice vs 16th/8th grid) — **0 OFF-GRID**

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| LeadHook | 103 | **0** | 54 | 0 off-grid (54 are legit 16th syncopation) |
| KeysPad | 96 | **0** | 0 | 0 off-grid |
| SubBass | 96 | **0** | 0 | 0 off-grid |
| SparkleStab | 64 | **0** | 0 | 0 off-grid |
| Drums (ch9) | 416 | **0** | 0 | 0 off-grid |

All 775 onsets snap to the 16th grid. The 54 "off-8th" lead onsets are
deliberate 16th-note syncopations (off-beat stabs), on-grid at 16th resolution.

### Harmony audit (pitched voices vs key + bar chord) — **0 OUT-OF-KEY**

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| LeadHook | 103 | **0** | **0** | pass |
| KeysPad | 96 | **0** | **0** | pass |
| SubBass | 96 | **0** | **0** | pass |
| SparkleStab | 64 | **0** | **0** | pass |

Every pitched note is a chord tone of its bar (hence in A natural minor).

### Audio profile (FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 90.17 s | 5.43% | 0.638 | 99.4% | healthy (silence = tail only) |
| Phase 1 | 87.33 s | 62.1% | 0.241 | 100% | raw sparse single voice (expected) |

- Phase 2: 5.43% silence is the ~5 s FluidSynth reverb/release tail after the
  last note (near-silent seconds are indices 86–90 of 91; content ends ~85 s).
  No mid-track gaps.
- Phase 1: 62.1% silence is expected for a raw single-voice diffusion draft
  (sparse diffused onsets, no texture). Longest contiguous near-silent run is
  3 s — no pathological dead zones; notes are spread across the whole piece.
- FFT tonal content 50–1000 Hz ≥ 99% in both phases → **not noise**.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All 5 tracks equal
length (61440 ticks), terminal landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`
per section, chronological sort (note-offs before note-ons at duplicate ticks)
enforced by the engine.

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/208-hiphop-hierarchical-diffusion.mid | 6,502 B | Phase 2 rules composition (DAW-editable) |
| MIDI/208-hiphop-hierarchical-diffusion-phase1.mid | 951 B | Phase 1 raw diffusion draft |
| Audio/208-hiphop-hierarchical-diffusion.ogg | 1,747,269 B | Phase 2 Opus render |
| Audio/208-hiphop-hierarchical-diffusion-phase1.ogg | 1,636,718 B | Phase 1 Opus render |
| Audio/*.wav | ~15 MB | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | 4,678 B | High-contrast timeline |
| Analysis/summary.json | 4,134 B | Full audit numbers |
| compose.py / render_audio.py | — | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes applied

None required — first-pass validation, grid audit, and harmony audit all green.
No rhythm-grid drift (078-class bug avoided by construction: all phase-2 onsets
computed as `round(raw_tick / GRID16) * GRID16`, never `SECTION_TICKS // n_events`).
Diatonic pitch routing uses chord-tone snapping against the explicit
`CHORD_PCS` dict (no custom `% 7` wrappers).

## 10. What to listen for

- **Diffused hook**: the LeadHook density breathes with the form — sparse in the
  Intro, densest in the Choruses, thinning in the Bridge/Outro. The pitch line
  drifts toward each bar's chord root (audible pull to A, F, C, G).
- **Bridge turn**: progression reverses to F–C–G–Am for a darker lift before
  the final chorus.
- **Boom-bap**: kick on 1/3, snare on 2/4, 8th hats — the steady 90 BPM pocket
  under the diffused lead.
- Tension/release lives in the i→VI→III→VII cycle resolving to Am at each bar 1.
