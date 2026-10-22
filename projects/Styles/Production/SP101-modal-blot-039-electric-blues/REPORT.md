# SP-101 BLOT-style Geometric Modal Resonator Network — production report

- **Date**: 2026-10-22
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-101 (`sound.synthesis.modal_blot`) — BLOT-style Geometric Modal
  Resonator Network. 8-mode just-intonation resonators per piece, waveguide
  strings, ring modulation, multiband saturation, FDN memory.
- **Layer**: ABSOLUTE (whole-piece timbre replacement; note material preserved).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (55 pickable in
  pool; recent-7-day methods SP-006/032/090/092/099/105/108/111 excluded).
- **Source composition**: `Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-v5.mid`
  (A-minor Am7 16th-note ostinato, 80 BPM, 480 TPB, 12 bars, single voice,
  144 notes, program 30 distortion guitar; pitches A3/C4/E3/G3).

## Pre-flight audit (3 rules) — PASS, no rework needed
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = 0, out-of-chord = 0 (A nat-minor, Am7) |
| Zero-drift (equal track ends) | **PASS** — single note track, end = 23040 ticks |

## Render
- Patch: 3 modal pieces (size 1.0 / 0.5 / 2.0 → fundamental + octave up + octave
  down), brightness 0.7/0.4/0.5, ring_time 0.4/0.25/0.5 s, waveguide pluck tuned
  per note, ring-mod pair (0,1), FDN mix 0.12. Strike velocity 0.6, +0.15 s ring
  tail per note, overlap-add stereo with subtle pan (low-left, high-right).
- Rendered at 48000 Hz (resonator phase math is 48000-native).
- Mastered: `master()` → blues −14 LUFS target, −1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 1.0000 (73 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: 0.4201
- **Silence**: 15.31%
- **RMS**: 0.1404
- **LUFS**: -14.00  **true peak**: 0.8913

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP101-modal-blot-039-electric-blues/SP101-modal-blot-039-electric-blues.wav` (7008044 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP101-modal-blot-039-electric-blues/SP101-modal-blot-039-electric-blues.ogg` (315117 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP101-modal-blot-039-electric-blues/SP101_modal_blot_raw.wav` (pre-master)
- `MIDI/source_original.mid` (reference copy)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- BLOT is an inharmonic (just-intonation) modal timbre by design; harmonic
  energy in strict integer-harmonic bins is naturally lower than a SoundFont
  render. The dominant-peak hit rate confirms every window lands on an in-key
  note class (fundamental = strongest mode, reinforced by octave-doubled pieces).
