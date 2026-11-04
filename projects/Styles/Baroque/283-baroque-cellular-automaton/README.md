# 283 — Baroque Cellular Automaton

**Nightly composition job · 2026-11-03**

A ternary (aba / da capo) Baroque movement in D minor, composed through
**Method 021 Cellular Automata Grid Evolution** — a 1D elementary cellular
automaton (Rule 30) drives melodic contour, note density, and continuo
figuration; the musicom rules layer post-processes it into a full Baroque
texture.

## At a glance

| Field | Value |
|---|---|
| Style | Baroque (classical LUFS/humanize profile) |
| Method | 021 Cellular Automata Grid Evolution (CAGE) — concrete, Rules-Based, Grid-Locked |
| Form | aba (da capo ternary): A1 (8) · B (8) · A2 (8) = 24 bars |
| Key | D minor — harmonic/melodic-mixture (b7 **and** leading tone C# in the key) |
| Meter / tempo | 4/4 · 96 BPM · 480 TPB (BAR = 1920) |
| Voices | Violin (lead) · Oboe (imitative counter) · Harpsichord (continuo) · Viola (inner pedal) · Cello (ground bass) |
| Length | 46080 ticks ≈ 60 s |

## Files

- `MIDI/` — `-phase1.mid` (raw CA draft) · `-perfect.mid` (grid-locked) · `-humanized.mid`
- `Audio/` — matched `.wav` + `.ogg` renders (mastered to −18 LUFS)
- `Analysis/` — `grid_visualization.txt`, `verify.json`, `render_stats.json`, `summary.json`
- `REPORT.md` — full composition + verification report
- `compose.py` / `render_audio.py` / `verify.py` — reproducible generators

## Listening guide

- The **cello ground bass** walks root→fifth on the quarter pulse — the harmonic floor.
- The **violin** runs a flowing 8th-note line whose contour arcs track the CA's
  live/dead cell runs (ascending while a cell lives, descending when it dies).
- The **oboe** echoes the lead in inversion a half-bar behind — imitative counterpoint.
- The **harpsichord** realizes the chords as block + broken-chord figuration,
  thinning out where the CA row is sparse.
- Cadences land V→i (A major → D minor) with the raised leading tone C#.

Compare `-perfect` vs `-humanized`: the humanized twin drifts micro-timing off
the grid (≈ 4 ticks mean, bass lays back ~8 ms) while staying note-identical in pitch.
