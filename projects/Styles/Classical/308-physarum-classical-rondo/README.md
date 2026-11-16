# 308-physarum-classical-rondo

Classical rondo composed with **Method 035 — Physarum Polycephalum Transport
Network Optimization** (concrete layer, Nature-Led). Nightly composition job
2026-11-16.

## Concept

A foraging slime-mold model drives the rondo melody. Food sources are the
current bar's chord tones (pitch-coordinate nodes) plus a tonic attractor; a
single agent streams toward the nearest source, depositing protoplasmic "tube
thickness" (flux) on revisited pitches. Peristaltic contraction oscillations
produce the rhythmic density (rests when the contraction dips), and flux maps
to velocity.

The raw Physarum walk (unquantized float pitch + off-grid onsets) is the
**Phase 1** draft. **Phase 2** applies the musicom rules layer: tiered
quantization (strong beats → chord tones, weak beats → scale tones), 8th-grid
snap, voice-leading on the pad triads, and a 5-voice classical texture
(violin lead · flute canon · viola inner harmony · cello bass · piano
broken-chord continuo).

## Key / Form / Tempo

| Field | Value |
|---|---|
| Key | G major (Ionian) |
| Tempo | 100 BPM, 4/4, 480 TPB |
| Form | rondo — A(4) · B(4) · A(4) · C(4) · A(4) = 20 bars |
| Texture | Violin · Flute · Viola · Cello · Piano |

## Files

| Path | Role |
|---|---|
| `MIDI/*-phase1.mid` | raw Physarum draft (unquantized) |
| `MIDI/*-perfect.mid` | grid-locked phase 2 |
| `MIDI/*-humanized.mid` | humanized phase 2 |
| `Audio/*-*.ogg` | mastered Opus renders (3 versions) |
| `Analysis/grid_visualization*.txt` | rhythm DNA grids |
| `Analysis/compose_summary.json` / `verification.json` / `render_report.json` | metrics |
| `REPORT.md` | full record |
| `index.html` | dashboard |
| `compose.py` / `render.py` / `verify.py` / `build_dashboard.py` | generators |

## Status

All hard gates pass — see `REPORT.md` for real numbers.
