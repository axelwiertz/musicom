# 256-tango-dorian-rework

Tango study in **D dorian** — longer, more varied rework of
`087-tango-abstract-dorian`.

- **Key:** D dorian (D E F G A B C) · **Tempo:** 112 BPM · 4/4 · 480 TPB
- **Form:** 8 sections × 4 bars = **32 bars** (Intro · TangoA · TangoB · Lift ·
  TangoA2 · Bridge · Finale · Coda)
- **Method:** two-phase — Phase 1 raw pitch-index random walk (off-grid draft),
  Phase 2 musicom rules (grid snap + chord-tone quantization + voice-leading)
  with 8 per-section variation techniques.
- **Voices:** alto sax lead · violin counterline · cello pad · piano marcato ·
  double-bass roots · drum kit (ch9)

## Listen

- `Audio/256-tango-dorian-rework-perfect.ogg` — grid-locked compositional truth
- `Audio/256-tango-dorian-rework-humanized.ogg` — style + instrument humanized
- `MIDI/*.mid` — DAW-importable (phase1 raw, perfect, humanized)

## Verify (real numbers)

Perfect layer: 1217 notes, **0 off-grid / 0 out-of-scale / 0 out-of-chord**,
zero-drift (6 tracks × 61440 ticks). Humanized: off-grid 702 (jitter proof),
scale violations 0.

See `REPORT.md` for the full audit, variation map, and humanization stats.
