# 289 — Bossa Nova Motivic Transforms

**Nightly composition job · 2026-11-06 · Method 013 (concrete)**

A Bossa Nova piece built with **Method 013 — Inversion / Retrograde Transform**:
one 8-note pitch motif is subjected to the classic geometric permutations
(prime → retrograde → inversion → prime-return) across an
`intro-a-a-b-a` form, then realized through the two-phase musicom pipeline.

| | |
|---|---|
| Style | Bossa Nova |
| Method | 013 — Inversion / Retrograde Transform (concrete) |
| Form | intro-a-a-b-a (5 sections, 36 bars) |
| Key | F major |
| Tempo | 120 BPM, 4/4 |
| Seed | 20261106 |

## Voices

| Voice | Instrument | GM program | channel |
|---|---|---|---|
| Flute | flute (lead melody) | 73 | 0 |
| Guitar | acoustic_guitar (nylon comp) | 24 | 1 |
| Rhodes | rhodes (chord pad) | 4 | 2 |
| Bass | acoustic_bass (double bass) | 32 | 3 |
| Drums | drum_kit (bossa kit) | 0 | 9 |

## Core motif (scale degrees in F major)

```
Prime      P  = [0, 1, 3, 2, 4, 2, 1, 0]   (F G Bb A C A G F)
Retrograde R  = [0, 1, 2, 4, 2, 3, 1, 0]
Inversion  I  = [4, 3, 1, 2, 0, 2, 3, 4]   (axis = 2.0)
Retro-Inv. RI = [4, 3, 2, 0, 2, 1, 3, 4]
```

Section transform map: **Intro=P · A1=P · A2=R · B=I · A3=P**.

## Files

- `MIDI/` — `-phase1.mid` (raw draft), `-perfect.mid`, `-humanized.mid` + provenance sidecars
- `Audio/` — mastered `-phase1.ogg`, `-perfect.ogg`, `-humanized.ogg`
- `Analysis/` — `grid_visualization.txt`, `summary.json`, `render_stats.json`
- `REPORT.md` — full record · `index.html` — dashboard · `compose.py` / `render.py`

See `REPORT.md` for the complete verification numbers.
