# 313-latin-square-chanson

**Chanson via Latin Square & Orthogonal-Array Composition (ABS-139, abstract layer)**

Nightly algorithmic composition job · 2026-11-19

- **Style**: Chanson · **Key**: G major · **Tempo**: 112 BPM · 4/4
- **Form**: verse-chorus (Intro·Verse·Chorus·Verse2·Chorus2·Outro, 40 bars)
- **Method**: ABS-139 LSAC — the piece is a 7×7 Latin square over the 7
  diatonic degrees; an orthogonal second square (MOLS pair) carries the
  rhythm/duration dimension. Every row/column is a complete degree aggregate;
  every `(degree, duration-class)` pair occurs exactly once (complete
  factorial design).
- **Texture**: Trumpet lead · Accordion musette comp · Steel-string guitar
  strum · Double bass · March-like drums.

## Files

- `MIDI/` — phase1 (raw), perfect (grid-locked), humanized (style+DNA jitter)
- `Audio/` — mastered OGG/WAV renders of all three
- `Analysis/` — grid visualization, verification, render report
- `REPORT.md` — full record

## Verify

```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python projects/Styles/Chanson/313-latin-square-chanson/verify.py
```
