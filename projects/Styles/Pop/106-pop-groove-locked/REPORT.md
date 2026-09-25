# 106-pop-groove-locked — Pop × Method 016 (Groove-Locked Pattern Writing)

**Style:** Pop (catchy, verse/chorus, backbeat-driven)
**Method:** 016 Groove-Locked Pattern Writing (Rules-Based, Rhythm/Texture)
**Layer:** `concrete`
**Date:** 2026-09-25
**Seed:** 20260925

## 1. Selection

| Field | Value |
|---|---|
| Style | **Pop** — random pick from `/opt/data/repos/musicom/projects/Styles/` genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `), seed 20260925. |
| Method | **016 Groove-Locked Pattern Writing** — `concrete` layer. Strict groove anchors matching a genre tempo; pitches written on top of a locked rhythmic pattern. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, Method 095). |

## 2. Method essence (016)

A fixed 16th-note **groove anchor** locks the whole piece. The groove is the
DNA; melodic pitch material is written *on top of* the repeating onset pattern
and never fights it. Three locked grooves drive the arrangement:

- **Lead groove** (16th steps): `[0, 3, 4, 6, 8, 11, 12, 14]` — syncopated pop
  hook with off-beat pushes (steps 3/11) and strong downbeat.
- **Bass groove**: `[0, 8, 14]` — locks to kick beats 1/3 + an upbeat push.
- **Guitar groove**: `[0, 2, 4, 6, 8, 10, 12, 14]` — straight 8th-note backbeat strum.

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | Intro → Verse → PreChorus → Chorus → Verse2 → Chorus2 → Bridge → Outro (8 sections × 4 bars = **32 bars**) |
| Key | **C Major** |
| Meter | 4/4, 120 BPM |
| Grid | 480 TPB → 16th = 120 ticks, 8th = 240 ticks, bar = 1920 ticks, section = 7680 ticks |
| Progression | **I–V–vi–IV** (C–G–Am–F) cycle, with PreChorus lift (F–G–Am–G) and Bridge (Am–F–C–G) |

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| LeadPiano | Piano | 1 | 0 | Groove-locked chord-tone hook (chorus +1 octave) |
| RhythmGuitar | Acoustic Guitar | 25 | 1 | 8th-note backbeat strum |
| PopBass | Double Bass | 43 | 2 | Groove-locked root/fifth |
| SparkleArp | Celesta | 8 | 3 | 16th-note chord arpeggio shimmer |
| Drums | Drum Kit | 0 (ch9) | 9 | Pop backbeat: kick 1/3, snare 2/4, 8th hats, open hat on 4& |

## 5. Two-Phase Architecture

### Phase 1 — Raw Groove-Locked Draft (`-phase1.mid`)
- Single voice (Raw_Lead, Piano).
- **Onsets locked** to the lead groove, but carry **off-grid micro-jitter**
  (±20 ticks) and **chromatic random-walk pitch** (unquantized to key/chord).
- No harmony, no chord-tone quantization. This is the raw method output.
- Zero-drift terminal landmark per section; `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- Strict **16th-grid quantization** (120 ticks) of every onset.
- **Diatonic C-major** + **per-bar chord-tone** snapping (quantize_to_chord).
- Full pop texture (5 voices), zero-drift landmarks, `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit (every pitched voice vs 16th/8th grid) — 0 OFF-GRID

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| LeadPiano | 256 | **0** | 64 | 0 off-grid (64 are legit 16th syncopation at steps 3/11) |
| RhythmGuitar | 768 | **0** | 0 | 0 off-grid |
| PopBass | 96 | **0** | 0 | 0 off-grid |
| SparkleArp | 192 | **0** | 0 | 0 off-grid |
| Drums (ch9) | 416 | **0** | 0 | 0 off-grid |

All onsets snap to the 16th grid (120 ticks). The 64 "off-8th" lead onsets are
deliberate 16th-note syncopations (steps 3 and 11 = 360/1320 ticks), which are
on-grid at 16th resolution — not drift.

### Harmony audit (pitched voices vs key + bar chord) — 0 OUT-OF-KEY

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| LeadPiano | 256 | **0** | **0** | pass |
| RhythmGuitar | 768 | **0** | **0** | pass |
| PopBass | 96 | **0** | **0** | pass |
| SparkleArp | 192 | **0** | **0** | pass |

### Audio profile (FluidSynth + FluidR3_GM.sf2 → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 71.13 s | 9.14% | 0.7397 | 97.9% | healthy (tail padding only) |
| Phase 1 | 66.63 s | 9.78% | 0.2335 | 97.7% | healthy (raw sparse single voice) |

Silence < 10% in both phases (tail-only), per-second RMS continuous with no
mid-track gaps, FFT tonal content ~98% in the 50–1000 Hz band → **not noise**.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All 5 tracks equal
length (61440 ticks), terminal landmark `MusicEvent(0,0,section-1,section)` per
section, chronological sort enforced.

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/106-pop-groove-locked.mid | 13,684 B | Phase 2 rules composition (DAW-editable) |
| MIDI/106-pop-groove-locked-phase1.mid | 2,220 B | Phase 1 raw groove-locked draft |
| Audio/106-pop-groove-locked.ogg | 1,266,301 B | Phase 2 Opus render |
| Audio/106-pop-groove-locked-phase1.ogg | 1,399,175 B | Phase 1 Opus render |
| Audio/*.wav | ~11-12 MB | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | 4,681 B | High-contrast timeline |
| Analysis/summary.json | 3,523 B | Full audit numbers |
| compose.py / render_audio.py | — | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes applied

None required — first-pass validation, grid audit, and harmony audit all green.
No rhythm-grid drift (078-class bug avoided by construction: all phase-2 onsets
computed as `step * GRID16`, never `SECTION_TICKS // n_events`).

## 10. What to listen for

- The **locked groove** is the through-line: every section rides the same 16th
  syncopation; the lead hook (`0,3,4,6,8,11,12,14`) repeats unchanged.
- **Chorus lift**: lead jumps an octave, doubling the hook for the "big" feel.
- **Bridge contrast**: progression reverses to Am–F–C–G for a darker turn.
- Tension/release lives in the **I→V→vi→IV** cycle resolving to C each bar 1.
