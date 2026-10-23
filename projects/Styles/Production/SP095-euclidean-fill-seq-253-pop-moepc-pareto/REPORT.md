# SP-095 Euclidean Fill Sequencer — production report

- **Date**: 2026-10-23
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-095 (`sound.generators.euclidean_fill_seq`) — Euclidean Fill
  Sequencer w/ Live Rotation (Maschine 3.7-style). Bjorklund Euclidean primary
  pulses + probabilistic lower-velocity fills + live per-bar rotation.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material preserved
  as per-bar chord-tone re-grooving).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (55 pickable in
  pool; recent-7-day SP-090/092/099/101/105/108/111 excluded).
- **Source composition**: `Styles/Pop/253-pop-moepc-pareto/MIDI/253-pop-moepc-pareto-perfect.mid`
  (C-major I-V-vi-IV pop, 112 BPM, 480 TPB, 28 bars, 5 voices — Piano lead /
  Synth Pad / Electric Bass / Glockenspiel / Drum Kit; grid-locked "perfect"
  variant used as the compositional truth).
- **Selection note**: the first seeded shuffle pick (single-pitch C5 ostinato,
  `Other/unknown-daily-2026-06-05`) was rejected as degenerate (<3 pitch
  classes — musically meaningless, cannot carry a production pass). A
  "musically meaningful" gate (>=3 distinct pitch classes) was added to the
  selector and the re-roll landed on 253-pop-moepc-pareto. Documented in
  `.selection_cron.json` under `rejected_degenerate`.

## Pre-flight audit (3 rules) — PASS, no rework needed
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = 0, out-of-chord = 0 (C major, per-bar triads) |
| Zero-drift (equal track ends) | **PASS** — 5 note tracks, end = 53760 ticks |

## SP-095 absolute layer (euclidean-fill groove)
Per-bar C-major triad (from the source `BAR_DEGREES` I-V-vi-IV progression) is
re-voiced as three `EuclideanFillSequencer` voices:

| Voice | pulses/steps | fill_density | rotation | register | program |
|---|---|---|---|---|---|
| Bass | 4/16 | 0.00 | fixed 0 | chord root/fifth −24 | 33 Electric Bass |
| Chord | 5/16 | 0.25 | +1/bar | triad root/3rd/5th | 88 Synth Pad |
| Sparkle | 7/16 | 0.40 | +3/bar | chord tones +12 | 9 Glockenspiel |

- Primary velocity 88-118, fill velocity factor 0.6, swing 0.0 (grid-locked).
- **Live rotation**: chord layer advances 1 step/bar, sparkle 3 steps/bar →
  the groove morphs through the 28 bars while the bass stays anchored.
- 627 generated notes, pitch classes [0, 2, 4, 5, 7, 9, 11] (all in C major).
- Rendered through FluidSynth (FluidR3_GM) carrier at 44100 Hz, mastered to
  pop −9 LUFS target, −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync | **PASS** — off-grid = 0 |
| Harmony | **PASS** — out-of-scale = 0, out-of-chord = 0 |
| Zero-drift | **PASS** — 3 note tracks, end = 53760 ticks |

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 1.0000 (125 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: 0.4007 (dry reference 0.3704, retention 1.082)
- **Silence**: 9.55%
- **RMS**: 0.2190
- **LUFS**: -10.13  **true peak**: 0.8913

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP095-euclidean-fill-seq-253-pop-moepc-pareto/SP095-euclidean-fill-seq-253-pop-moepc-pareto.wav` (12130860 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP095-euclidean-fill-seq-253-pop-moepc-pareto/SP095-euclidean-fill-seq-253-pop-moepc-pareto.ogg` (597637 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP095-euclidean-fill-seq-253-pop-moepc-pareto/SP095_euclidean_fill_raw.wav` (pre-master)
- `/opt/data/repos/musicom/projects/Styles/Production/SP095-euclidean-fill-seq-253-pop-moepc-pareto/dry_full_mix_source_reference.wav` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `MIDI/SP095-euclidean-groove.mid` (generated euclidean-fill groove)
- `Audio/stems/` (3 per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-095 is a rhythm/groove generator (drum-machine-style). Its absolute-layer
  application re-voices the source harmony as a euclidean-fill arpeggio
  groove; the Bjorklund pulses carry the primary hits and the probabilistic
  fills add the lower-velocity connective tissue, exactly the method's two
  headline features (fills + live rotation).
