# 272-indie-pop-sunset-rework

Indie Pop rework of the legacy `indie-pop-sunset` composition. D Dorian, 120 BPM,
26 bars / 8 sections. Rebuilt through the canonical `UnitMatrixComposer` engine
(two-phase architecture) with dual-version humanization.

## Files
- `MIDI/272-indie-pop-sunset-rework-perfect.mid` — grid-locked (compositional truth)
- `MIDI/272-indie-pop-sunset-rework-humanized.mid` — humanized (pop profile + instrument DNA)
- `MIDI/272-indie-pop-sunset-rework-phase1.mid` — raw pre-rules generative draft
- `Audio/272-indie-pop-sunset-rework-perfect.ogg` — mastered listen (Opus)
- `Audio/272-indie-pop-sunset-rework-humanized.ogg` — mastered listen (Opus)
- `index.html` — project dashboard

## Identity
Key D dorian · pitch motif `(2,3,-2,0,5)` · Euclidean 5-in-8 clavé · Lead/Pad/Bass/Counter/Drums.

## Regenerate
```bash
$MUSICOM_PYTHON compose.py   # build + export MIDI (perfect/humanized/phase1)
$MUSICOM_PYTHON verify.py    # read-only audit
$MUSICOM_PYTHON render.py    # FluidSynth -> master -> Opus
```

See `REPORT.md` for the full rework rationale and `Analysis/` for audits + grid viz.