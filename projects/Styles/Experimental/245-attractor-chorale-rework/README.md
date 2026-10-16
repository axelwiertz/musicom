# 245-attractor-chorale-rework

Experimental chorale — **Method 043** (Strange Attractor Trajectory Mapping,
Lorenz system / RK4) + musicom rules. Rework of `061-attractor-chorale`.

- **Key:** E dorian (E F# G A B C# D)
- **Tempo:** 92 BPM · 4/4 · 480 TPB
- **Form:** 10 sections × 2–4 bars = **32 bars**, homophonic SATB chorale
- **Voices:** Soprano/Alto/Tenor (Flute) + Bass + Descant (Oboe) + Perc (ch9)

## Two-phase
- **Phase 1** (`-phase1.mid`): raw Lorenz trajectory, single flute voice —
  unquantized pitch, off-grid onsets (pre-rules).
- **Phase 2** (`.mid`): chord-tone quantization per bar (floor `t//BAR`),
  voice-leading continuity, 8th-grid snap, register enforcement.

## Listen
- `Audio/245-attractor-chorale-rework.ogg` (full mix)
- `Audio/245-attractor-chorale-rework-phase1.ogg` (raw draft)

## Edit
- `MIDI/245-attractor-chorale-rework.mid`
- `MIDI/245-attractor-chorale-rework-phase1.mid`

See `REPORT.md` for audit, variation techniques, and verification numbers.
