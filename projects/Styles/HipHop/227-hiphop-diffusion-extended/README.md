# 227-hiphop-diffusion-extended

**HipHop × Method 010 Hierarchical Diffusion** — nightly rework (2026-10-07).

Extended rework of `208-hiphop-hierarchical-diffusion` (source passed all six engine
standards → extension, not redesign).

- **Style:** HipHop (boom-bap backbeat, sub bass, chord stabs, swung 16ths)
- **Key:** A natural minor · **BPM:** 90 · **Form:** 10 sections × 4 bars = **40 bars**
- **Voices:** LeadHook (Piano), KeysPad (Organ), SubBass (Double Bass),
  SparkleStab (Celesta), CounterLine (Flute, bridge counter-melody), Drums (ch9)

## Variation techniques (8)

Inversion (Verse2) · Augmentation (Bridge) · Counterline (Bridge flute) ·
Register shift (Chorus3 +1 octave) · Mode shift (Lift → relative major C) ·
Transposition (Chorus4 +4th) · Retrograde (Outro) · Density rise (global arc).

## Verification (all green)

- **0 off-grid** · **0 out-of-scale** · **0 out-of-chord** across 468 pitched onsets
- Zero-drift: `validate()` PASSED both phases (6 tracks × 76800 ticks)
- Audio: −15.9 LUFS, 4.5% silence (healthy), not a silent render

## Files

- `MIDI/` — phase1 + phase2 MIDI (+ provenance sidecars)
- `Audio/` — Opus OGG + WAV renders (phase1 + phase2)
- `Analysis/` — `grid_visualization.txt`, `rework_audit.json`
- `compose.py`, `verify.py` — generator + verification
- `REPORT.md` — full record
- `index.html` — dashboard
