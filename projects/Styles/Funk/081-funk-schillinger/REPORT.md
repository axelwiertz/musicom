# REPORT — 081-funk-schillinger

**Date (UTC):** 2026-08-29 23:09
**Style:** Funk
**Method:** 018 Schillinger System of Musical Design — `generators.schillinger` (`SchillingerGenerator`, resultant interference a=5, b=3)
**Seed:** 20260829

---

## 1. Form & Key

- **Tempo:** 100 BPM, 4/4, 480 TPB, BAR = 1920 ticks
- **Key:** Bb major. Scale pcs: {10, 0, 2, 3, 5, 7, 9} (Bb C D Eb F G A)
- **Sections:** Intro, Verse, Chorus, Verse2, Chorus2, Outro — 4 bars each, 24 bars total
- **Section length:** 7680 ticks each

## 2. Full Progression (24 bars, roots + function)

```
I  ii iii V  | I  ii iii V  | I  IV V  I  | I  V  I  ii | I  ii iii V  | I  IV ii I
Bb Cm Dm  F  | Bb Cm Dm  F  | Bb Eb F  Bb | Bb F  Bb Cm | Bb Cm Dm  F  | Bb Eb Cm Bb
```

Chord tone sets (diatonic triads, root-keyed):
- I (Bb): {58, 62, 65} · ii (Cm): {60, 63, 67} · iii (Dm): {62, 65, 69}
- IV (Eb): {63, 67, 70} · V (F): {65, 69, 72}

## 3. Voices + Instruments (from Instruments KB)

| # | Voice | GM | Instrument KB | Role |
|---|-------|----|----------------|------|
| 0 | Lead | 56 | Trumpet (Brass/trumpet) | Schillinger resultant lead, scale+chord quantized |
| 1 | Rhodes | 4 | — | Comp: 3rd/5th, 8th rhythm, sustained |
| 2 | Guitar | 27 | — | Offbeat wah stabs (2&, 3&, 4&), 1& push in choruses |
| 3 | Bass | 33 | — | Root/fifth octave pulse, 16th push in choruses |
| 4 | Clav | 7 | — | Horn stabs in choruses (chord tones +24) |
| 5 | Drums | ch9 | Drum Kit (Percussion/drum_kit) | Kick 1&3, snare 2&4, hats 8ths, claps + ride in choruses |

## 4. Two-Phase Architecture

**Phase 1** (`MIDI/081-funk-schillinger-phase1.mid`) — raw generative draft:
- Single voice (Trumpet 56), NO harmony, NO bass, NO drums
- Rhythm: Schillinger resultant of a=5, b=3 → durations [3,2,1,3,1,2,3] pulses,
  scaled by a jittered factor → **fractional, off-grid** tick durations (this is the point of phase 1)
- Pitches: coordinate-axis sine projection around a drifting center + Gaussian wander — **unquantized**
- Per-section event counts: 26 / 34 / 42 / 34 / 42 / 26

**Phase 2** (`MIDI/081-funk-schillinger.mid`) — musicom rules post-process:
1. **Grid-lock FIRST** to 16th grid (120 ticks) — mandatory rhythm-grid sync (078 rule)
2. Lead: snap to nearest Bb-major scale degree, then **chord-tone quantization per bar
   using GLOBAL bar lookup** (`s*BARS_PER + local_bar`) — 079 bugfix pattern
3. Leap cap ≤ 9 semitones (drift to nearest chord tone of that bar)
4. Rhodes / guitar / bass / clav / drums follow bar chords (bass root + fifth in-chord)
5. `rules.voice_leading.VoiceLeadingRules(style="classical")` check on bass+lead outer
   voices per bar pair — 13 flags (idiomatic parallel fifths between bass root and
   lead chord tone; see section 10)
6. Zero-drift `validate()` gate on both phases: **OK / OK**
7. `visualization.grid.write_grid_visualization` + `provenance` sidecars + `summary.json` + `audit.json`

## 5. Grid Audit (rhythm-grid sync — MANDATORY)

Exported phase-2 MIDI, every track's onsets vs grid (0 off-grid required):

| Track | Voice | ch | n | 16th off (120) | 8th off (240) |
|-------|-------|----|---|---------------|---------------|
| 1 | Lead | 0 | 203 | **0** | 98* |
| 2 | Rhodes | 1 | 96 | **0** | **0** |
| 3 | Guitar | 2 | 80 | **0** | 8* |
| 4 | Bass | 3 | 104 | **0** | 8* |
| 5 | Clav | 4 | 32 | **0** | **0** |
| 6 | Drums | 9 | 296 | **0** | **0** |

\* 8th-off entries are *intentional 16th placements* (16th push / anticipation / 16th
comp rhythm) — they are 16th-grid multiples (120) but not 8th-grid multiples (240).
The MANDATORY requirement is **0 off-grid on the 16th grid** (the working grid of the
piece, matching percussion). 8th-grid is a coarser reporting grid: all those notes are
16th-aligned, i.e. rhythmically locked to the drum grid.

**Verdict: 0 off-grid (16th) on all voices. 8th-grid anomalies are 16th-aligned pushes, not drift.**

## 6. Harmony Audit (scale + chord-tone — MANDATORY)

Pitch-class membership per voice (drums exempt — percussion sounds, not pitches):

| Track | Voice | out-of-scale | out-of-chord |
|-------|-------|--------------|--------------|
| 1 | Lead | **0** | **0** |
| 2 | Rhodes | **0** | **0** |
| 3 | Guitar | **0** | **0** |
| 4 | Bass | **0** | **0** |
| 5 | Clav | **0** | **0** |
| 6 | Drums | n/a | n/a |

**Verdict: 0 out-of-scale, 0 out-of-chord on every pitched voice.**

## 7. Zero-Drift Status

- Phase 1 `validate()`: **OK** — every cell carries terminal landmark `MusicEvent(0,0,7679,7680)`
- Phase 2 `validate()`: **OK** — all 6 rows equal length (6 × 7680 = 46080 ticks), terminal landmark per cell
- MIDI exports via `UnitMatrixComposer.to_midi()` (built-in absolute-alignment + tail pad)

## 8. Audio Render + Silence/RMS Profile

FluidSynth CLI: `fluidsynth -ni -g 1.2 -F <wav> TimGM6mb.sf2 <mid>`, then ffmpeg → opus (voip 48k).

| File | Size | Duration | Silence ratio | FFT tonal windows |
|------|------|----------|---------------|-------------------|
| Audio/081-funk-schillinger.wav | 11,327,516 B | 60.16 s | **5.5%** | 120/120 |
| Audio/081-funk-schillinger.ogg | 443,381 B | — | — | — |
| Audio/081-funk-schillinger-phase1.wav | 11,158,172 B | 60.15 s | **5.3%** | 120/120 |
| Audio/081-funk-schillinger-phase1.ogg | 653,062 B | — | — | — |

Per-second RMS (mix, first 20 s): 0.075–0.115 — steady body, no mid-track dead zones
(global min 0.0 only at the final tail boundary). FFT dominant peaks 50–1000 Hz present
in all windows — tonal content confirmed, **no silent-WAV trap, no noise render.**

## 9. File Paths

```
MIDI/081-funk-schillinger.mid              (8,600 B)
MIDI/081-funk-schillinger.mid.provenance.json
MIDI/081-funk-schillinger-phase1.mid       (8,024 B)
MIDI/081-funk-schillinger-phase1.mid.provenance.json
Audio/081-funk-schillinger.wav/.ogg (+ provenance sidecars)
Audio/081-funk-schillinger-phase1.wav/.ogg (+ provenance sidecars)
Analysis/grid_visualization.txt
Analysis/audit.json
Analysis/summary.json
Analysis/render_stats.json
README.md
compose.py / audit.py / audio_stats.py / audio_provenance.py
```

All MIDI/JSON/text artifacts > 40 bytes (size asserts passed).

## 10. Fixes / Notes Applied This Run

1. **Grid-lock ordering (078/079 rule):** grid-lock BEFORE chord-tone quantization.
   Quantizing then snapping can push a note across a bar boundary into a bar whose
   chord it doesn't fit. Lock-then-quantize keeps bar lookup consistent.
2. **GLOBAL bar lookup (079 bugfix):** phase-1 events are section-relative ticks, so
   `tick // BAR` yields a *section-local* bar. Used `bar = s*BARS_PER + local_bar` for
   lead quantization and leap-cap corrections. Verified by audit: 0 out-of-chord.
3. **Voice-leading flags (13):** all are parallel fifths / hidden fifths between the
   *bass root* (fifth above root is the bass's own fifth) and the *lead chord tone* —
   a root-position funk texture where bass root + lead fifth is idiomatic and stable.
   They were flagged by the strict `classical` style on cross-voice pairs; the
   single-voice melodic line itself is leap-capped. Documented, not "fixed": forcing
   voice-leading corrections here would strip the funk character (the flags arise from
   the root-position triad voicing, not from melodic errors). The mandatory harmony
   invariant (all pitches in-scale + in-chord) holds with 0 violations.
4. **Bass fifth note:** `fifth = root + 7` is always in-chord (root's fifth is the
   chord's fifth for every diatonic triad in this progression) — verified by audit.
5. **16th push / anticipation** in choruses (bass, guitar) is 16th-aligned (t0+1800,
   t0+120) — matches the drum 16th grid, no drift.
6. **Provenance:** `write_provenance` with `AI_GENERATED` classification, Schillinger
   params (a, b, resultant) recorded in the parameters dict, per artifact (MIDI ×2,
   audio ×4). `policy_warnings` satisfied (sources present).

## 11. Method Rationale (why Method 018 + Funk)

Schillinger's interference resultants ARE rhythm — exactly what funk needs. The
resultant of generators 5 and 3 ([3,2,1,3,1,2,3] pulses) produces the syncopated,
asymmetric attack pattern that reads as "funk" once locked to the 16th grid and voiced
with offbeat guitar stabs, octave bass pulse, and backbeat drums. Phase 1 preserves the
raw mathematical rhythm (off-grid, fractional); Phase 2 is the musicom rules layer:
grid lock, scale/chord quantization, leap capping, and a full groove texture — turning
the abstract interference pattern into a danceable Bb-major funk piece.
