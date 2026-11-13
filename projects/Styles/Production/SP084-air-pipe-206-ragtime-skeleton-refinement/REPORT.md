# SP-084 AirPipe flue-pipe physical model — production report

- **Date**: 2026-11-13
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-084 (`sound.synthesis.air_pipe`) — physical-modelled flue-pipe
  bank with air-supply modulation (Modartt Airteq-style). Open/stopped
  cylindrical resonators, saturating flue-jet drive, turbulence breath,
  overblow migration, DAM air modulation.
- **Layer**: ABSOLUTE (whole-piece timbre replacement; note material preserved).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (93 registered,
  85 in pool; recent-7-day methods SP-069/097/113/119/138/146/154 excluded,
  SP-138 already used on this source).
- **Source composition**: `Styles/Ragtime/206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid`
  (C major, 120 BPM, 480 TPB, 40 bars = 80 s, Introduction|A|B|A2|Trio|Coda,
  3 piano voices — Melody 60-77, stride Bass 48-57, Comp stabs 55-65, 600 notes).

## Pre-flight audit (3 rules) — PASS (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = 0 |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = 0, out-of-chord = 0 (C major, per-bar diatonic progression) |
| Zero-drift (equal track ends) | **PASS** — track_ends = [76800] |

## Render
- Per-note AirPipe at 44100 Hz. Melody + comp = OPEN pipes (flute/organ, even +
  odd harmonics); bass = STOPPED pipes (odd-harmonic reed/organ). Air pressure
  = 0.32 + 0.4 * vel/127 (never exceeds the 0.75
  overblow threshold -> clean pitch, brighter accents).
- Global "air" LFO (DAM) breathes the whole instrument bank: 0.10 sin(0.15 Hz)
  + 0.06 sin(0.37 Hz).
- Register-based stereo pan (low-left, high-right, ±0.35), overlap-add with
  +0.12s breath tail per note.
- Mastered: `master()` → -14.0 LUFS target, -1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 1.0000 (160 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: 0.3411
- **Silence**: 1.55%
- **RMS**: 0.1192
- **LUFS**: -14.14  **true peak**: 0.8913

## Files
- `/opt/data/repos/musicom/projects/Styles/Production/SP084-air-pipe-206-ragtime-skeleton-refinement/SP084-air-pipe-206-ragtime-skeleton-refinement.wav` (14178192 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP084-air-pipe-206-ragtime-skeleton-refinement/SP084-air-pipe-206-ragtime-skeleton-refinement.ogg` (461202 bytes)
- `/opt/data/repos/musicom/projects/Styles/Production/SP084-air-pipe-206-ragtime-skeleton-refinement/SP084_air_pipe_raw.wav` (pre-master)
- `MIDI/source_original.mid` (reference copy)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- AirPipe is a physical model: the low mode-count means harmonic energy is
  naturally concentrated in the first few integer harmonics of the fundamental,
  giving a clean flute/organ tonal signature (high HE, unlike inharmonic
  synthesis). Stopped bass pipes add odd-harmonic richness for a reed-organ low
  end. Overblow deliberately avoided to keep pitch-verification exact.
