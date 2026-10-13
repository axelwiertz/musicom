# 238 — Neo-Riemannian Afro Drop

**Style:** African · **Method:** 011 Voice-Leading Graph Search (concrete)
**Form:** intro-break-drop-outro · **Key:** G major · **BPM:** 124

An African groove built from a neo-Riemannian voice-leading graph search:
every bar moves one chord to the next by holding two common tones and moving
the third a semitone (L) or whole tone (R). Marimba balafon lead, voice-led
string pad, kalimba mbira ostinato, double-bass roots, and a ch9 bell-timeline
+ shaker + kick/snare/tom polyrhythm across intro → break → drop → outro.

## Files

- `MIDI/` — phase-2 (rules) + phase-1 (raw draft) MIDI, with provenance
- `Audio/` — FluidR3_GM WAV + Opus OGG (phase-2 and phase-1)
- `Analysis/` — `summary.json` (chord path + voice-leading steps),
  `audit.json` (mido readback), `grid_visualization.txt`,
  `render_stats.json`
- `REPORT.md` — full record (selection, method, verification numbers)
- `index.html` — dashboard

## Status

Complete. Zero-drift True, 0 off-grid, 0 out-of-scale, 0 out-of-chord,
0 voice-leading violations.

## Regenerate

```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py   # MIDI + provenance
/opt/data/micromamba/envs/musicom/bin/python render.py    # FluidSynth -> WAV/OGG
/opt/data/micromamba/envs/musicom/bin/python verify.py    # grid + harmony audit
```
