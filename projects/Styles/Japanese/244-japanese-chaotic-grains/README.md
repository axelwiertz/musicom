# 244-japanese-chaotic-grains

Japanese × Method 028 **Chaotically Modulated Cellular Grains (CMCG)** — nightly two-phase composition (2026-10-15).

## Concept

A Japanese koto/shakuhachi/shamisen/taiko ensemble where the **koto grain lead**
is driven by a **Henon chaotic map**: the map's `x`-coordinate selects which
chord tone each grain lands on, and its `y`-coordinate selects which 8th-grid
slot each grain occupies. The four strophic verses sweep the chaotic character
from stable/periodic → bifurcation → full chaos → return, so the piece's
texture "breathes" from sparse grains to a dense grain cloud and back.

| Field | Value |
|---|---|
| Project | 244-japanese-chaotic-grains |
| Style | Japanese |
| Method | 028 — Chaotically Modulated Cellular Grains (CMCG) |
| Layer | concrete (Nature-Led) |
| Key | D Hirajoshi (D E F A Bb) |
| Tempo | 80 BPM · 4/4 · 480 TPB |
| Form | strophic — 4 × Verse × 8 bars = 32 bars |
| Voices | Koto (lead), Shakuhachi (counterline), Shamisen (arpeggio), Taiko + Drums |

## Files

- `MIDI/244-japanese-chaotic-grains.mid` — phase-2 (rules-processed) full texture
- `MIDI/244-japanese-chaotic-grains-phase1.mid` — phase-1 raw Henon grain cloud
- `Audio/*.wav` — FluidSynth render (mastered to −14 LUFS)
- `Audio/*.ogg` — Opus (Telegram-ready)
- `Analysis/summary.json` — chord path, regime schedule, inline audit
- `Analysis/grid_visualization.txt` — ASCII grid
- `REPORT.md` — full report

## Method 028 mechanics

Henon map `x_{n+1} = 1 − a·x_n² + y_n`, `y_{n+1} = b·x_n` (a=1.4, b=0.3):

- **PITCH** ← `x`: grain pitch = chord-tone index derived from chaotic `x`.
- **RHYTHM** ← `y`: grain onset slot = 8th-grid position derived from chaotic `y`.
- **STRUCTURE** ← regime sweep across verses (stable → chaos → return).
