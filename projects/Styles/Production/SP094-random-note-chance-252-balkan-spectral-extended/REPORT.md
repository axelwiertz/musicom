# SP-094 Random Note Generator + Note Chance Sequencer — production report

- **Date**: 2026-10-26
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-094 (`sound.generators.random_note_gen`) — Random Note Generator
  + Note Chance Sequencer (Maschine 3.7 Random Note Gen / Note Event
  Chance-style). Phase 1: `RandomNoteGenerator` fills each voice's grid "from
  nothing" from configurable odds (density), a scale-quantised pitch pool, and
  a velocity range. `NoteChanceSequencer` wraps that note stream, assigns a
  per-note chance, locks the strong metrical positions, and re-rolls a
  "breathing" realisation each loop. Phase 2 (musicom rules): per-bar G Dorian
  chord-tone quantisation, grid snap, zero-drift pad.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material re-generated
  as per-bar chord-tone random-note-chance texture).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  61 in pool after excluding recent-7-day SP-078, SP-090, SP-095, SP-101, SP-108, SP-111, SP-119 and
  baseline SP-001).
- **Source composition**: `Styles/Balkan/252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid`
  (G Dorian dajcovo 7/8, 132 BPM, 480 TPB, 32 bars = 53760 ticks, 4 voices —
  double bass 43 / accordion 21 / clarinet 71 / violin 40; grid-locked
  "perfect" variant used as the compositional truth).

## Pre-flight audit (3 rules) — PASS on source (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (G Dorian scale + chord tones) | **PASS** — out-of-scale = 0, out-of-chord = 0 |
| Zero-drift (equal track ends) | **PASS** — 4 note tracks, end = 53760 ticks |

The source is grid-locked (0 off-grid; the 24 off-8th onsets are idiomatic
16th-note diminutions in the Dance section, still 16th-grid-locked), fully in
G Dorian and chord-tone clean against the 32-bar progression, and all 4 tracks
end at 53760 ticks — no rework, straight to the SP method.

## SP-094 absolute layer (random-note-chance texture)
Per-bar G Dorian triad (from the source `PROG_DEG` 32-bar progression) is
re-voiced as four random-note-chance voices, one per source instrument:

| Voice | program | register | density | step | chance | chord tones | lock |
|---|---|---|---|---|---|---|---|
| Bass | 43 Double Bass | 43-55 | 0.80 | 8th | 0.92 | root + fifth | dajcovo 2+2+3 accents |
| Accordion | 21 Accordion | 55-67 | 0.45 | 16th | 0.80 | root/3rd/5th | bar downbeat |
| Clarinet | 71 Clarinet | 67-86 | 0.38 | 16th | 0.72 | root/3rd/5th (sequential) | bar downbeat |
| Violin | 40 Violin | 79-91 | 0.28 | 16th | 0.62 | root/3rd/5th (sequential) | bar downbeat |

- **RandomNoteGenerator** scale pool: `scale="minor"` at root D3 == the
  D natural-minor pitch set `{2,4,5,7,9,10,0}` == the **G Dorian** pitch-class
  set (both are modes of F major), so the generator's built-in scale quantisation
  stays in-key for G Dorian. Every generated pitch is then snapped to the bar's
  chord tones (Phase 2).
- **NoteChanceSequencer**: default chance per voice above; the bass also locks
  the dajcovo 2+2+3 accents (8th positions 0/2/4 = ticks 0/480/960) so the 7/8
  lilt stays anchored while interior notes "breathe".
- **Chance re-roll dropped** 127 notes total (per-voice {'Bass': 6, 'Accordion': 37, 'Clarinet': 41, 'Violin': 43}).
- 533 generated notes, pitch classes [0, 2, 4, 5, 7, 9, 10] (all in G Dorian).
- Rendered through FluidSynth (FluidR3_GM) carrier at 44100 Hz, mastered to
  folk −16 LUFS target, −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (G Dorian) | **PASS** — out-of-scale = 0, out-of-chord = 0 |
| Zero-drift (equal track ends) | **PASS** — 4 note tracks, end = 53760 ticks |

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 0.9902 (102 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: 0.5428 (dry reference 0.5097, retention 1.065)
- **Silence**: 7.49%
- **RMS**: 0.1231
- **LUFS**: -16.01  **true peak**: 0.8913

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP094-random-note-chance-252-balkan-spectral-extended/SP094-random-note-chance-252-balkan-spectral-extended.wav` (9440044 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP094-random-note-chance-252-balkan-spectral-extended/SP094-random-note-chance-252-balkan-spectral-extended.ogg` (416551 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP094-random-note-chance-252-balkan-spectral-extended/SP094_random_note_chance_raw.wav` (pre-master)
- `/opt/data/repos/musicom/projects/Styles/Production/SP094-random-note-chance-252-balkan-spectral-extended/dry_full_mix_source_reference.wav` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `MIDI/SP094-random-note-chance.mid` (generated random-note-chance groove)
- `Audio/stems/` (4 per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-094's two headline tools are both exercised: (1) RandomNoteGenerator fills
  the grid "from nothing" from odds + scale + register (its `density`,
  `scale`, `pitch_range`, `velocity_range` params), and (2) NoteChanceSequencer
  applies per-note chance with lockable strong positions and a re-rolled
  "breathing" realisation. The absolute-layer application re-voices the Balkan
  source's 4-instrument texture with the same programs but note material
  regenerated through the chance engine, with Phase-2 chord-tone quantisation
  keeping the harmony exactly on the source's G Dorian progression.
