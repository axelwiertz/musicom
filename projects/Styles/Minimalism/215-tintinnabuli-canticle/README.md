# 215-tintinnabuli-canticle

Arvo Pärt-style holy-minimalism. Isorhythmic talea-color melody (Method 032,
`generators.tintinnabuli`) over an E-natural-minor tintinnabuli shadow.

- **Key:** E natural minor · **Tempo:** 92 BPM · **Meter:** 4/4
- **Form:** 8 sections × 4 bars = 32 bars (rework of `079-minimalism-isorhythm`, extended + varied)
- **Voices:** Viola (M-voice), Cello (T-voice), Violin (pad), Double Bass (drone), Glockenspiel, Canon Violin, Drums (ch9)

## Files

| Path | Purpose |
|---|---|
| `MIDI/215-tintinnabuli-canticle.mid` | Phase 2 — rules-processed full texture |
| `MIDI/215-tintinnabuli-canticle-phase1.mid` | Phase 1 — raw isorhythmic draft |
| `Audio/215-tintinnabuli-canticle.ogg` | Opus render (Telegram) |
| `Audio/215-tintinnabuli-canticle.wav` | Full-mix WAV |
| `Analysis/grid_visualization.txt` | █/░ rhythm grid |
| `Analysis/summary.json` | Machine-readable composition summary |
| `REPORT.md` | Full concept, audit, variation techniques, verification |
| `index.html` | Dashboard (VoltAgent styling) |

## Regenerate

```bash
cd /opt/data/projects/Styles/Minimalism/215-tintinnabuli-canticle
$MUSICOM_PYTHON compose.py
```