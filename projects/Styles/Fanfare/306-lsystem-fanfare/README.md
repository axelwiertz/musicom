# 306-lsystem-fanfare

Fanfare composed with **Method 019 — L-System Algorithmic Composition** (concrete
layer, Rules-Based). Nightly composition job 2026-11-15.

## Concept

A self-similar L-system (D0L grammar) drives the fanfare melody. The grammar
`A -> ABA, B -> BC, C -> RA, R -> R` with axiom `C` expands to a 256-symbol
string (32 bars of 8th notes) whose rewrite structure produces the classic
ternary "rise–fall–rise" fanfare contour, recursively nested. Interpretation:
`A` = step up, `B` = step down, `C` = leap up (a 4th), `R` = rest.

The raw L-system walk (unquantized float pitch + off-grid onsets) is the
**Phase 1** draft. **Phase 2** applies the musicom rules layer: tiered
quantization (strong beats → chord tones, weak beats → scale tones), 8th-grid
snap, voice-leading on the brass pad, and a 6-voice brass texture.

## Key / Form / Tempo

| Field | Value |
|---|---|
| Key | Bb major (Ionian) |
| Tempo | 120 BPM, 4/4 |
| Form | cinematic-build — Intro(4) · Build(8) · Rise(8) · Peak(8) · Resolve(4) = 32 bars |
| Texture | Trumpet lead · French Horn canon · Brass Section pad · Tuba bass · Timpani · Drums |

## Files

| Path | Role |
|---|---|
| `MIDI/*-phase1.mid` | raw L-system draft (unquantized) |
| `MIDI/*-perfect.mid` | grid-locked phase 2 |
| `MIDI/*-humanized.mid` | humanized phase 2 |
| `Audio/*-*.ogg` | mastered Opus renders (3 versions) |
| `Analysis/grid_visualization*.txt` | rhythm DNA grids |
| `Analysis/compose_summary.json` / `verification.json` / `render_report.json` | metrics |
| `REPORT.md` | full record |
| `index.html` | dashboard |
| `compose.py` / `render.py` / `verify.py` | generators |

## Status

All hard gates pass — see `REPORT.md` for real numbers.
