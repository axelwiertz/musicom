# 087-tango-abstract-dorian

Nightly autonomous algorithmic composition — 2026-09-05.

- **Style:** Tango
- **Method:** ABS-002 Subset Walker (ABSTRACT layer) + ABS-001 tension curve + method-006 cadence close
- **Key:** D dorian · **BPM:** 112 · 4/4
- **Form:** Intro | TangoA | TangoB | Lift | TangoA2 | Outro (6 × 4 bars = 24 bars)
- **Texture:** Alto Sax lead · Violin counterline · Cello pad · Piano marcato comp · Double-Bass tango roots · Drum Kit

## Two-phase artifacts

| Phase | MIDI | Audio |
|---|---|---|
| 1 — raw subset-walk draft (off-grid, single sax voice) | `MIDI/087-tango-abstract-dorian-phase1.mid` | `Audio/087-tango-abstract-dorian-phase1.ogg` |
| 2 — rules (16th grid + chord tones + full texture) | `MIDI/087-tango-abstract-dorian.mid` | `Audio/087-tango-abstract-dorian.ogg` |

## Verification summary

| Check | Result |
|---|---|
| Zero-drift validate() | OK both phases |
| Grid audit (16th) | **0 off-grid** on all 6 voices |
| Harmony audit | **0 out-of-scale / 0 out-of-chord** (5 pitched voices) |
| Silence ratio | 4.7% (phase 2, tail-only), 8.6% (phase 1) |
| Provenance | sidecars on all 6 artifacts |

Full record: `REPORT.md`. Analysis: `Analysis/audit.json`,
`Analysis/render_stats.json`, `Analysis/grid_visualization.txt`,
`Analysis/summary.json`.

## The walked progression (D dorian)

```
VII i  III VII | i  IV  i  III | IV VII i  IV | VII v7 ii7 i7 | i  VII i  VII | III i  VII VII
C  Dm F   C    | Dm Gm  Dm F    | Gm C   Dm Gm  | C  Am7 Edim7 Dm7 | Dm C  Dm C    | F  Dm C   C
```
