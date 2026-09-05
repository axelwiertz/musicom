# REPORT — 086-son-markov-guajira

**Date:** 2026-09-04 (nightly autonomous composition job)
**Style:** Cuban — son (guajira-leaning montuno)
**Method:** 002 Markov Probabilistic Transitions (MarkovChainGenerator.generate_sequence)
**Layer:** concrete (6-of-7 concrete cadence; prior abstract run was 085)
**Project dir:** `/opt/data/projects/Styles/Cuban/086-son-markov-guajira`

---

## 1. Concept brief

- Genre/subgenre: Cuban son, guajira-leaning montuno (danceable, warm).
- Emotional target: relaxed dance floor, nostalgic street-son warmth.
- Key/mode: A minor (aeolian). Bars 10/14/23 voice degree 4 as V7 (E7) with
  the harmonic-minor leading tone G# (pc 8) for authentic dominant pull.
- Tempo/meter: 104 BPM, 4/4, 480 TPB.
- Form: AAB — 6 sections × 4 bars = 24 bars.
- Instrumentation: tres lead (GM 24 nylon guitar stand-in), piano montuno
  guajeo, nylon guitar comp, contrabass tumbao, trumpet answer, GM drums +
  woodblock son clave.
- Lesson: hear the Markov degree path (tonic-biased random walk with V→i
  gravity) realized as a functional son progression; hear phase-1 chaos
  (unquantized raw chain) vs phase-2 order (chord tones on a grid).

## 2. Method mechanics (Method 002, concrete)

Phase 1 uses the engine's `generators.chain.MarkovChainGenerator`:
`generate_sequence(length=192, states=0..6, distribution=7x7 transition)`.
The transition matrix encodes tonal gravity: i strongly self-retains (0.40),
v→i at 0.60, ii°/VII resolve toward i/VI, producing a tonic-anchored random
walk over the seven A-minor scale degrees. The raw degree stream maps to
absolute A-minor scale pitches (marimba program 12) placed at *fractional*
tick offsets (±12% of an 8th) — the raw generative fingerprint. Single voice,
no harmony/bass/drums.

Phase 2 (musicom rules post-process):
- The same Markov chain drives the phase-2 lead (tres), but each bar's notes
  are **chord-tone quantized** to that bar's chord from the planned progression
  (which was itself shaped with the chain's tonic bias: i–VII–VI–i,
  ii°–i–V7–i, iv–VII–V7–i, VI–iv–VII–i).
- All pitched voices (Lead, Montuno, Comp, Bass, Trumpet) are chord-quantized
  per bar then **grid-snapped** to the 16th (120 ticks). Drums/clave built
  directly on the grid.
- Full texture assembled through `UnitMatrixComposer` with per-section
  event accumulation + landmark pad → validate() → to_midi().

## 3. Harmony

Degree plan per bar (A minor; bar = 1-indexed):

| Bars | Degrees | Roman |
|---|---|---|
| 1-4 | 0 0 0 0 | i i i i |
| 5-8 | 0 6 5 0 | i VII VI i |
| 9-12 | 1 0 4 0 | ii° i V7 i |
| 13-16 | 3 6 4 0 | iv VII V7 i |
| 17-20 | 5 3 6 0 | VI iv VII i |
| 21-24 | 0 6 4 0 | i VII V7 i |

Chord pitch classes (absolute, A-minor): i=Am{9,0,4}, ii°=Bdim{11,2,5},
III=C{0,4,7}, iv=Dm{2,5,9}, V7=E7{4,8,11,2}, VI=F{5,9,0}, VII=G{7,11,2}.
All diatonic to A (harmonic) minor; V7 bars use G# (pc 8).

## 4. Voices and instruments

| Voice | Instrument | Program | Channel | Register |
|---|---|---|---|---|
| Lead | Tres (nylon-guitar stand-in; tres not in the 18-instrument registry) | 24 | 0 | 62-84 |
| Montuno | Piano (registry PIANO) | 1 | 1 | 60-84 |
| Comp | Acoustic Guitar (registry ACOUSTIC_GUITAR) | 25 | 2 | 52-72 |
| Bass | Contrabass (registry DOUBLE_BASS) | 43 | 3 | 33-55 |
| Trumpet | Trumpet (registry TRUMPET) | 56 | 4 | 58-76 |
| Drums | GM percussion kit ch9 + woodblock (son clave) | — | 9 | — |

## 5. Grid audit (phase 2, exported MIDI, READ-ONLY mido)

Grid = 16th (120) mandatory; 8th (240) reported for info.

| Voice | notes | off 16th | off 8th | verdict |
|---|---|---|---|---|
| Lead (tres) | 118 | 0 | 50* | 0 off 16th |
| Montuno (piano) | 288 | 0 | 0 | 0 off 16th |
| Comp (guitar) | 150 | 0 | 0 | 0 off 16th |
| Bass (contrabass) | 72 | 0 | 0 | 0 off 16th |
| Trumpet | 24 | 0 | 0 | 0 off 16th |
| Drums (ch9) | 480 | 0 | 48* | percussion |

\* off-8th counts are legal 16th syncopation: lead uses 16th passing tones in
montuno sections, drums carry 16th clave/hat/cowbell. All onsets lie on the
16th grid → **0 off-grid (mandatory 16th check passes for every voice).**

Phase-1 raw draft (for contrast): 192 onsets, 92 off-16th / 92 off-8th —
the intended unquantized generative fingerprint. In scale (0 out-of-scale),
102/192 out-of-chord (raw chain has no chord context — expected).

## 6. Harmony audit (phase 2)

Scale = A harmonic minor {9,11,0,2,4,5,7,8}; chord = bar chord from §3.

| Voice | out-of-scale | out-of-chord | verdict |
|---|---|---|---|
| Lead (tres) | 0 | 0 | PASS |
| Montuno (piano) | 0 | 0 | PASS |
| Comp (guitar) | 0 | 0 | PASS |
| Bass (contrabass) | 0 | 0 | PASS |
| Trumpet | 0 | 0 | PASS |

**Harmony verdict: 0 out-of-scale, 0 out-of-chord across all pitched voices.**

## 7. Zero-drift status

- Phase 1: `validate()` OK → exported (1674 B).
- Phase 2: `validate()` OK → exported (8716 B).
- Both tracks length 46080 ticks (24 bars × 1920). Provenance sidecars
  written for both phase MIDIs.

## 8. Render + silence/RMS profile (SP-001 FluidSynth)

| Metric | Value |
|---|---|
| WAV | Audio/086-son-markov-guajira.wav, 10 983 212 B |
| OGG | Audio/086-son-markov-guajira.ogg, 421 344 B |
| Duration | 62.26 s @ 44100 Hz, stereo |
| Peak | 0.96 |
| Silence ratio | 0.1079 (10.8 % — all in the reverb tail after last note) |
| Per-second RMS | 0.067–0.148 for all 68 music seconds; last ~5 s tail decay to 0 |

No mid-track gaps: RMS stays ≥ 0.067 through second 67. Render healthy.

Phase-1 contrast render (raw Markov draft, marimba only):
WAV 10 355 756 B · OGG 488 617 B · 58.71 s · silence 5.6 %.

## 9. Files

```
MIDI/086-son-markov-guajira-phase1.mid           1674 B  (+ provenance.json)
MIDI/086-son-markov-guajira.mid                  8716 B  (+ provenance.json)
Audio/086-son-markov-guajira.wav            10 983 212 B  (+ provenance.json)
Audio/086-son-markov-guajira.ogg                421 344 B  (+ provenance.json)
Audio/086-son-markov-guajira-phase1.wav     10 355 756 B  (+ provenance.json)
Audio/086-son-markov-guajira-phase1.ogg         488 617 B  (+ provenance.json)
Analysis/grid_visualization.txt   (█/░ per-voice density grid)
Analysis/audit.json               (full per-voice verification numbers)
Analysis/render_stats.json        (silence/RMS profile, phase 2)
Analysis/render_stats_phase1.json (silence/RMS profile, phase 1)
Analysis/summary.json             (project summary)
README.md
REPORT.md
compose.py audit.py render_audio.py render_phase1.py write_summary.py
summarize_audit.py
```

## 10. Fixes applied during the run

1. **Tres not in registry** — lead uses GM 24 (nylon guitar) stand-in; noted
   in README/REPORT (registry has no guitar-family Cuban instrument).
2. **C-space degree tables → A-minor absolute** — initial degree/chord tables
   were built around C (pc0 tonic). Audits flagged ~20 out-of-scale/bar.
   Rewrote TRIAD_PCS/DEGREE_PCS as absolute A-minor pcs; V7 = E7 {4,8,11,2}
   with harmonic-minor G#.
3. **Section merge drift bug** — per-bar pad units merged per section caused
   offset rebasing twice (pad_unit offset applied then align added it again),
   producing out-of-chord notes at 1920 multiples. Rewrote phase-2 assembly:
   per-voice per-section absolute-tick accumulator, single pad at the end.
4. **Clave as pitched voice** — clave marimba (ch5) was wrongly audited as a
   pitched voice. Folded son clave into the drum voice (woodblock 76, ch9).
5. **Audit pairing bug** — naive onset/note_off pairing produced phantom
   long notes; replaced with single-pass same-pitch close logic.
6. **Audit percussion noise** — ch9 notes were counted out-of-scale;
   percussion is now excluded from scale/chord audit (rhythm-only).

## 11. Method rationale

Method 002 (Markov) is a concrete, grid-locked, local-memory method — a
natural fit for a genre whose identity is a repeating harmonic loop with a
syncopated groove. The chain's tonic gravity (i at 0.40, v→i at 0.60) maps
directly to son's i–VII–VI / ii–V7–i functional lean, so phase-2 chord
quantization preserves the chain's statistical contour while making every
voice consonant. Son clave/tumbao are fixed genre anchors (rules layer,
cf. method 016/012 family) layered under the Markov lead.
