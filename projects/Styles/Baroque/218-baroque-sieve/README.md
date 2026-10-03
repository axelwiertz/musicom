# 218 — Baroque × Xenakis Sieve Theory

Autonomous nightly composition (2026-10-02). **Baroque** genre, D minor chamber
suite, composed with **Method 025 — Xenakis Sieve Theory** (Layer: concrete).

## Files

| Path | Purpose |
|---|---|
| `MIDI/218-baroque-sieve.mid` | Phase-2 (rules-processed) 5-voice MIDI |
| `MIDI/218-baroque-sieve-phase1.mid` | Phase-1 raw sieve draft (single voice) |
| `Audio/218-baroque-sieve.ogg` | Opus render (FluidSynth) |
| `Audio/218-baroque-sieve.wav` | PCM render |
| `Analysis/audit.json` | grid + harmony audit numbers |
| `Analysis/grid_visualization.txt` | high-contrast voice density timeline |
| `Analysis/summary.json` | machine-readable summary |
| `REPORT.md` | full compositional record |
| `compose.py` / `audit.py` / `render_audio.py` | generator + verifier + renderer |

## One-line DNA

Xenakis sieve `n%3∈{0,2} & n%4∈{0,2,3}` (pitch) × `s%4∈{0,2,3} & s%8∈{0,1,3,4,6}`
(rhythm) drives a raw violin walk; musicom rules discipline it into D-minor
chord tones on a 16th grid, arranged for Violin/Violin2/Recorder/Harpsichord/Cello.

## Verification

- 0 off-grid (16th) · 0 out-of-scale · 0 out-of-chord (531 pitched notes)
- zero-drift: 5 tracks × 46080 ticks
- audio: 62.75 s, 4.16 % silence, peak 0.56
