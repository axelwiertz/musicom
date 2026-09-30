# 212-indian-boids-yaman

**Raga Yaman (Hindustani classical) composed via Swarm Intelligence Flocking (Boids).**

- **Style:** IndianClassical — Raga Yaman (Kalyan thaat), alap → gat → jhala → alap form
- **Method:** 031 Swarm Intelligence Flocking (Boids), Nature-Led, `concrete` layer
- **Key:** Raga Yaman on C (Sa = C) — S R G M̄ P D N = C D E F♯ G A B
- **BPM:** 90 · 4/4 · 480 TPB · 32 bars · 8 sections × 4 bars

## Voices (instrument registry)

| Voice | Instrument | GM | Channel |
|---|---|---|---|
| Drone (tanpura) | Church Organ | 19 | 0 |
| LeadSitar | Sitar | 104 | 1 |
| Bansuri | Flute | 74 | 2 |
| Tabla (teental) | Drum Kit | — | 9 |

## Two-phase architecture

1. **Phase 1** (`MIDI/212-indian-boids-yaman-phase1.mid`) — raw boid draft: single
   voice, unquantized onsets (off-grid jitter), raw chromatic centroid pitch,
   no harmony.
2. **Phase 2** (`MIDI/212-indian-boids-yaman.mid`) — musicom rules post-process:
   16th-grid onset snap + raga-harmonic snap, full 4-voice texture.

## Verification (all green)

- Zero-drift `validate()` PASSED both phases.
- Grid audit: **0 off-grid** (every onset on the 16th grid).
- Harmony audit: **0 out-of-scale, 0 out-of-chord** (full Yaman).
- Audio: phase-2 silence 7.6%, tonal 98.4% (not noise).

See `REPORT.md` for the full method write-up, boid parameters, and audit numbers.
