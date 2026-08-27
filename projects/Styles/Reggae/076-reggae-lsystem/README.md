# 076-reggae-lsystem — Reggae / Method 019 L-System (Fibonacci word)

**Style:** Reggae · **Method:** 019 L-System Algorithmic Composition (Fibonacci word, Rules-Based paradigm)
**Key:** A aeolian · **BPM:** 96 · **Bars:** 24 · **Sections:** Intro / Verse / Chorus / Verse2 / Chorus2 / Outro (4 bars each)

## Concept

Reggae roots one-drop in A aeolian. The **Fibonacci word** L-system
(axiom `A`, rules `{A -> AB, B -> A}`, 6 iterations → 21 symbols
`ABAABABAABAABABAABABA`) is the melodic DNA: strictly self-similar at every
scale, motif fragments recur at nested scales, never identically. The word
re-enters each section at a rotation offset `(0, 5, 3, 8, 5, 3)` so every
re-entry starts at a different phase.

Reggae pillars implemented:
- **One-drop**: kick + rimshot on beat 3 (the anchor); beat 1 carried by the
  bass pickup.
- **Skank (chop)**: staccato guitar chords on the offbeats (the "and" of
  every beat).
- **Bubble**: bass root/fifth bounce with syncopated pushes toward the
  one-drop anchor.
- **Dub cut**: the Outro drops lead AND skank entirely — "space is the
  place" — bass + drums exposed for the last 4 bars.

Harmony: i – bVII – i – bVI (Am – G – Am – F), validated against the
`Scale7ChordDegree` function map (tonic → tonic-prolongation → tonic →
subdominant → ... = legal reggae modal loop, closed by the i anchor).

## Two-Phase Architecture

- **Phase 1 (`MIDI/076-reggae-lsystem-phase1.mid`)**: raw L-system draft.
  Symbol semantics: `A` = pitch +2 st (quarter), `B` = pitch −2 st (eighth).
  Continuous chromatic pitch walk — NOT scale-enforced: **50 of 118 events
  leak non-diatonic tones** (the pre-rules signature). Single voice (organ),
  no harmony, no voice leading.
- **Phase 2 (`MIDI/076-reggae-lsystem.mid`)**: musicom rules post-process.
  Every raw pitch snapped to the nearest section triad tone (lead organ),
  A-aeolian block harmony via canonical `Scale7ChordDegree.get_diatonic_note()`
  (no off-by-octave wrap), voice-leading optimization + Phase 2c inversion
  rotation (0 violations after, 0 corrections needed), then the full one-drop
  texture: skank guitar offbeat chops, bass pickup-anchor bounce, one-drop
  drums with open-hat 4& push, chorus snare ghosts, dub-cut outro.

## Files

- `compose.py` — two-phase generator (engine: `structures` + `workflows.unitmatrix_composer`)
- `MIDI/076-reggae-lsystem-phase1.mid` + `.provenance.json`
- `MIDI/076-reggae-lsystem.mid` + `.provenance.json`
- `Audio/076-reggae-lsystem.wav` / `.ogg` + phase1 versions
- `Analysis/grid_visualization.txt`, `summary.json`, `provenance.json`

## Verification

- `validate()` Phase 1: OK · Phase 2: OK (zero-drift gate passed)
- Full-mix WAV: 66.7s, 10.2% silence (only tail padding), RMS 0.102,
  peak 0.996 — no digital silence
- Phase 1 WAV: 62.1s, 3.7% silence, RMS 0.062
- All artifacts > 40 bytes (asserted)
- Preflight: `preflight_check.py` exit 0 (COMPLIANT)
- Voice-leading violations (classical): 0 · Phase 2c corrections: 0
