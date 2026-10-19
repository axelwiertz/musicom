# 251 — Japanese Christoffel Word

**Genre**: Japanese (traditional ensemble) · **Method**: 069 Christoffel Word
Combinatorial Composition (CWCC) · **Layer**: concrete · **Form**: rondo
(A-B-A-C-A) · **Key**: E yo pentatonic (major pentatonic) · **Tempo**: 88 BPM.

## Concept

Christoffel words are *balanced binary words* — the combinatorial backbone of
both musical scales and Euclidean rhythms. This piece drives three dimensions
from one word family:

| Dimension | Christoffel object | Musical realization |
|-----------|--------------------|---------------------|
| Scale (height) | step word C(3,2) = `aabab` over {2,3} semitones | steps (2,2,3,2,3) → E yo pentatonic {E F# G# B C#} |
| Rhythm (time) | C(5,3) & C(3,5) as onset/rest words | koto E(5,8) mask `11011010`, shamisen E(3,8) tresillo |
| Form (Sturmian) | Fibonacci substitution A→AB | rondo A-B-A-C-A recurrence |
| Harmony (duality) | dual word C(2,3) = `babaa` (a↔b swap) | episode chords schedule (C#m / B / F#sus2) |

## Instrumentation

| Voice | GM program | Channel | Role |
|-------|-----------|---------|------|
| Koto | 107 | 0 | lead melody (Christoffel contour arpeggio) |
| Shakuhachi | 77 | 1 | sustained counterline (root + upper chord tone) |
| Shamisen | 106 | 2 | rhythmic tresillo plucks |
| Taiko | 116 | 3 | percussion anchor (climax 8th interlock) |

## Files

- `MIDI/251-japanese-christoffel-phase1.mid` — raw stochastic draft (single voice, off-grid)
- `MIDI/251-japanese-christoffel-perfect.mid` — grid-locked concrete layer
- `MIDI/251-japanese-christoffel-humanized.mid` — seeded style humanization
- `Audio/*.ogg` — mastered Opus renders (perfect + humanized + phase1)
- `Analysis/grid_visualization.txt` — high-contrast timeline
- `Analysis/summary.json` / `readback.json` / `render_stats.json`
- `REPORT.md` — full record

## Status

Composed + verified 2026-10-18 (nightly autonomous job).
