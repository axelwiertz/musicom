# 237 — Kuramoto Chorale Extended

**Rework of 069-kuramoto-chorale.** Method 038 (KOPS). F dorian. 92 BPM.
18 bars / 8 sections. SATB chorale + drums.

## Concept

Four Kuramoto phase oscillators with incommensurate natural frequencies
(0.85 / 1.0 / 1.15 / 1.35 events-per-beat) are coupled; coupling strength K
rises section-by-section (0.5 → 4.0). The ensemble evolves from desynchronized
polyrhythmic drift into a phase-locked chorale. The soprano (oscillator 0)
carries the melody; alto/tenor/bass are voice-leading-optimized block harmony.

## Files

| File | Role |
|------|------|
| `MIDI/237-kuramoto-chorale-extended.mid` | Phase 2 — rules-processed (5 voices) |
| `MIDI/237-kuramoto-chorale-extended-phase1.mid` | Phase 1 — raw KOPS draft (single voice) |
| `MIDI/*.provenance.json` | Provenance sidecars (both phases) |
| `Audio/237-kuramoto-chorale-extended.ogg` | Opus render (Telegram) |
| `Audio/237-kuramoto-chorale-extended.wav` | FluidSynth WAV |
| `Analysis/grid_visualization.txt` | High-contrast UnitMatrix timeline |
| `Analysis/rework_audit.json` | Audit of source (069) |
| `REPORT.md` | Rework report |
| `index.html` | Dashboard |
| `compose.py` / `verify.py` | Reproducible generator + verifier |

## Variation techniques

1. Rhythm augmentation (Verse A')
2. Register shift +12 (Verse A')
3. Density rise via drums (Chorus)
4. Contour inversion + modal color III (Bridge)
5. Melodic retrograde (Verse B)
6. Octave doubling (Chorus')
7. Diminution / fade (Outro)

## Validation

- Zero-drift: PASS (5 tracks × 34560 ticks)
- Off-grid: 0 | Scale violations: 0 | Chord violations: 0
- Voice-leading violations (classical): 0
- Silence ratio: 10.9% (< 30% threshold)
