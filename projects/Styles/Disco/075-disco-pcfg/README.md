# 075-disco-pcfg — Disco / Method 034 PCFG Recursion

**Style:** Disco · **Method:** 034 Probabilistic Context-Free Grammar Recursion (PCFG), Rules-Based paradigm
**Key:** D natural minor · **BPM:** 118 · **Bars:** 24 · **Sections:** Intro / Verse / Chorus / Verse2 / Chorus2 / Outro (4 bars each)

## Concept

Disco four-on-the-floor in D minor. Chords: i – VI – III – VII (Dm – Bb – F – C)
circle-of-fifths flavored disco harmonic bed. Full texture: square-lead melody,
string octave stabs, 16th-note guitar chank, octave-pulse bass, four-on-the-floor
drums with backbeat + ride + claps in choruses.

## Two-Phase Architecture

- **Phase 1 (`MIDI/075-disco-pcfg-phase1.mid`)**: raw PCFG recursion draft.
  A probabilistic context-free grammar rewrites a start symbol into interval
  and rhythm cells. Pitch indices are raw floats (unquantized, may sit off
  chord), single voice, NO harmony. Sparse and wandering by design.
- **Phase 2 (`MIDI/075-disco-pcfg.mid`)**: musicom rules post-process.
  Every phase-1 pitch is snapped to the nearest chord tone per bar,
  voice-leading caps leaps at 9 semitones, then the full disco texture is
  arranged (strings stabs, guitar chank, bass octave pulse, drums).

## Files

- `compose.py` — two-phase generator (engine: `structures` + `workflows.unitmatrix_composer`)
- `MIDI/075-disco-pcfg-phase1.mid` + `.provenance.json`
- `MIDI/075-disco-pcfg.mid` + `.provenance.json`
- `Audio/075-disco-pcfg.wav` / `.ogg` + phase1 versions
- `Analysis/grid_visualization.txt`, `summary.json`, `silence_check.py`

## Verification

- `validate()` Phase 1: OK · Phase 2: OK (zero-drift gate passed)
- Full-mix WAV: 53.7s, 10.6% silence (only reverb tail), RMS 0.117 — no digital silence
- All artifacts > 40 bytes (asserted)
- Preflight: `preflight_check.py` exit 0
