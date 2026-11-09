# 293-steel-guitar-rework

Country steel-slide rework of `038-steel-guitar-demo` through the canonical
`UnitMatrixComposer` engine.

- **Genre**: Country · **Key**: G major · **BPM**: 90 · **Form**: 20 bars / 6 sections
- **Motif**: steel-slide 1→3→5 (G→B→D), ascending with one descending reset
- **Voices**: Steel Guitar (25), Fiddle (40), Rhythm Guitar (24), Bass (32), Drums (ch9)

## Files
| Artifact | Path |
|---|---|
| Phase 1 (raw draft) | `MIDI/293-steel-guitar-rework-phase1.mid` |
| Phase 2 perfect | `MIDI/293-steel-guitar-rework-perfect.mid` |
| Phase 2 humanized | `MIDI/293-steel-guitar-rework-humanized.mid` |
| Audio (perfect) | `Audio/293-steel-guitar-rework-perfect.ogg` |
| Audio (humanized) | `Audio/293-steel-guitar-rework-humanized.ogg` |
| Dashboard | `index.html` |
| Grid viz | `Analysis/grid_visualization.txt` |
| Audit | `Analysis/rework_audit.json` |

## Regenerate
```bash
$MUSICOM_PYTHON Scripts/compose.py     # MIDI + provenance + grid
$MUSICOM_PYTHON Scripts/verify.py      # read-only checks
$MUSICOM_PYTHON Scripts/render.py      # FluidSynth -> master -> OGG
```

## Status
Redesign of a hand-rolled, zero-drift-failing source; all engine standards now pass.
See `REPORT.md` for the full audit and verification numbers.
