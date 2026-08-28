# REPORT — 079-minimalism-isorhythm

**Date (UTC):** 2026-08-27 23:16
**Style:** Minimalism (Arvo Pärt holy-minimalism)
**Method:** 032 Isorhythmic Talea-Color Mapping — `generators.tintinnabuli` (`TintinnabuliGenerator` + `isorhythmize` pattern)
**Seed:** 20260827

---

## 1. Form & Key

- **Tempo:** 92 BPM, 4/4, 480 TPB, BAR = 1920 ticks
- **Key:** E natural minor. Scale pcs: {4, 6, 7, 9, 11, 0, 2} (E F# G A B C D)
- **Sections:** Intro, Mvt1, Mvt2, Mvt3, Mvt4, Outro — 4 bars each, 24 bars total
- **Section length:** 7680 ticks each

## 2. Full Progression (24 bars, roots + function)

```
i  VI III iv | i  VI III iv | i  VI III V  | i  VI iv  V  | i  VI III iv | i  III iv i
Em C  G   Am | Em C  G   Am | Em C  G   B  | Em C  Am  B  | Em C  G   Am | Em G  Am  Em
```

Chord tone sets (diatonic triads, root-keyed):
- i (Em): {52, 55, 59} · III (G): {55, 59, 62} · iv (Am): {57, 60, 64}
- V (B): {59, 62, 66} · VI (C): {60, 64, 67}

## 3. Voices + Instruments (from Instruments KB)

| # | Voice | GM | Instrument KB | Role |
|---|-------|----|----------------|------|
| 0 | M-Voice | 41 | Viola | Pärt M-voice: conjunct stepwise melody, mode + chord quantized |
| 1 | T-Voice | 42 | Cello | Tintinnabuli triad (E-G-B) shadow below melody, ∩ bar-chord |
| 2 | Violin | 40 | Violin | Sustained organum pad: bar root + fifth (+24), whole-bar |
| 3 | DblBass | 43 | Double Bass | Root drone, whole-bar sustained (octave 2) |
| 4 | Bells | 9 | Music Box | Chord-tone arpeggio accents on 1, 2&, 3, 4& |
| 5 | Drums | ch9 | Drum Kit | Soft pulse: hat 8ths, kick 1, snare 2&4, ride in dense mvt |

## 4. Two-Phase Architecture

**Phase 1** (`MIDI/079-minimalism-isorhythm-phase1.mid`) — raw generative draft:
- Single voice (Pan Flute 75), NO harmony, NO bass, NO drums
- Pitches: color pattern `[0,2,4,7,5,7,4,2,0,-1,-3,-5]` + seeded Gaussian register wander — **unquantized**
- Rhythm: talea `[1,0.5,0.5,1,0.5,1.5,0.5,1,2,0.5,1,0.5]` beats — fractional, **off-grid** (this is the point of phase 1)
- Per-section event counts: 24 / 32 / 36 / 32 / 36 / 24

**Phase 2** (`MIDI/079-minimalism-isorhythm.mid`) — musicom rules post-process:
1. **Grid-lock FIRST** to 16th grid (120 ticks) — mandatory rhythm-grid sync
2. M-voice: snap each pitch to E-minor mode degrees (`tint.m_voice`)
3. **Chord-tone quantization per bar using GLOBAL bar lookup** (`s*BARS_PER + local_bar`) — see fixes
4. Leap cap <= 9 semitones (drift to nearest chord tone)
5. T-voice: nearest E-G-B triad tone below melody, filtered to bar-chord pcs
6. Organum pad, bass drone, bells, percussion follow bar chords
7. `rules.voice_leading.VoiceLeadingRules(style="classical")` check on M-voice: **0 flags**
8. Zero-drift `validate()` gate on both phases: **OK / OK**
9. `visualization.grid.write_grid_visualization` + `provenance` sidecars + `summary.json`

## 5. Grid Audit (rhythm-grid sync — MANDATORY)

Exported phase-2 MIDI, every track's onsets vs grid (0 off-grid required):

| Track | Voice | ch | n | 16th off (120) | 8th off (240) |
|-------|-------|----|---|---------------|---------------|
| 1 | M-Voice | 0 | 114 | **0** | **0** |
| 2 | T-Voice | 1 | 114 | **0** | **0** |
| 3 | Violin | 2 | 48 | **0** | **0** |
| 4 | DblBass | 3 | 24 | **0** | **0** |
| 5 | Bells | 4 | 96 | **0** | **0** |
| 6 | Drums | 9 | 256 | **0** | **0** |

**Verdict: 0 off-grid on all voices (both grids).** Drums also fully on-grid.

## 6. Harmony Audit (scale + chord-tone — MANDATORY)

Pitch-class membership per voice (drums exempt — percussion sounds, not pitches):

| Track | Voice | out-of-scale | out-of-chord |
|-------|-------|--------------|--------------|
| 1 | M-Voice | **0** | **0** |
| 2 | T-Voice | **0** | **0** |
| 3 | Violin | **0** | **0** |
| 4 | DblBass | **0** | **0** |
| 5 | Bells | **0** | **0** |
| 6 | Drums | n/a | n/a |

**Verdict: 0 out-of-scale, 0 out-of-chord on every pitched voice.**

## 7. Zero-Drift Status

- Phase 1 `validate()`: **OK** — every cell carries terminal landmark `MusicEvent(0,0,7679,7680)`
- Phase 2 `validate()`: **OK** — all 6 rows equal length (6 × 7680 = 46080 ticks), terminal landmark per cell
- MIDI exports via `UnitMatrixComposer.to_midi()` (built-in absolute-alignment + tail pad)

## 8. Audio Render + Silence/RMS Profile

FluidSynth CLI: `fluidsynth -ni -g 1.2 -F <wav> TimGM6mb.sf2 <mid>`, then ffmpeg → opus (voip 48k).

| File | Size | Duration | Silence ratio | FFT tonal frames |
|------|------|----------|---------------|------------------|
| Audio/079-minimalism-isorhythm.wav | 12,756,268 B | 72.31 s | **13.3%** | 144/144 |
| Audio/079-minimalism-isorhythm.ogg | 552,792 B | — | — | — |
| Audio/079-minimalism-isorhythm-phase1.wav | 11,437,612 B | 64.84 s | **3.4%** | 129/128 |
| Audio/079-minimalism-isorhythm-phase1.ogg | 529,169 B | — | — | — |

Per-second RMS (mix, first 20 s): 0.112–0.137 — steady body, no mid-track dead zones.
FFT dominant peaks: 196 Hz (G3), 66 Hz (E2 bass drone), 392 Hz (G4), 248 Hz — all E-minor palette, no noise. **No silent-WAV trap, no noise render.**

## 9. File Paths

```
MIDI/079-minimalism-isorhythm.mid            (7,480 B)
MIDI/079-minimalism-isorhythm.mid.provenance.json
MIDI/079-minimalism-isorhythm-phase1.mid
MIDI/079-minimalism-isorhythm-phase1.mid.provenance.json
Audio/079-minimalism-isorhythm.wav/.ogg (+ provenance sidecars)
Audio/079-minimalism-isorhythm-phase1.wav/.ogg (+ provenance sidecars)
Analysis/grid_visualization.txt
Analysis/summary.json
README.md
compose.py
```

All MIDI/JSON/text artifacts > 40 bytes (size asserts passed). Preflight exit 0 (compliant).

## 10. Fixes Applied This Run

1. **Grid-lock ordering (079 bugfix, extends 078 rule):** grid-lock moved BEFORE chord-tone
   quantization. Quantizing then snapping can push a note across a bar boundary into a bar whose
   chord it doesn't fit. Lock-then-quantize keeps bar lookup consistent with the final rhythm.
2. **GLOBAL bar lookup (079 bugfix):** phase-1 events are section-relative ticks, so `tick // BAR`
   yields a *section-local* bar. Sections 0/1/5 repeat `i VI III iv`, masking the bug; section 2's
   bar 3 is global bar 11 = **V** (B major) but was quantized as *local* bar 3 = **iv** (Am) →
   M-voice landed on E (64) inside V. Fixed: `bar = s*BARS_PER + local_bar` in M-voice, T-voice,
   and bells. (Same latent bug existed in 078, hidden by its section pattern.)
3. **T-voice triad correction:** initial T-voice used a G-B-D triad (wrong tonic). Corrected to the
   E-minor tintinnabuli triad E-G-B, intersected with the bar chord per note (never empty: tonic
   triad shares a pc with every diatonic chord of E minor) → strict in-chord invariant holds.
4. **Violin pad:** was hardcoded to Em root for all sections → now follows each bar's chord
   (root + fifth from that bar's tones), eliminating 48 out-of-chord notes.
5. **Bells:** were playing tonic-triad tones in all bars → now cycle the bar's chord tones
   (+24 octave shift), eliminating 43 out-of-chord notes.
6. **Audit correctness:** chord audit uses pitch-class membership (bass at octave 2 / bells +24
   are in-chord, just shifted), and the percussion channel (ch9) is exempted from scale/chord
   tests (drum sounds are not pitches).

## 11. Method Rationale (why Method 032 + Minimalism)

Method 032 (Isorhythmic Talea-Color Mapping) couples a repeating pitch color to a repeating
duration talea — the Pärt holy-minimalism engine already present in `generators.tintinnabuli`.
The 12-element color and 12-element talea are coprime in effect, so pitch and rhythm never
synchronize into a static loop; the register wander in phase 1 keeps the raw line breathing.
Phase 2 is the musicom rules layer: mode snapping (conjunct M-voice), tintinnabuli triad shadow
(T-voice), strict chord-tone harmony per bar, grid-locked rhythm — turning the stochastic draft
into a coherent, consonant minimalist piece.
