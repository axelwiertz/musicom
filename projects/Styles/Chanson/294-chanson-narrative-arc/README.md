# 294 — Chanson Narrative Arc

A chanson built with **Method 007 — Narrative Arc Register Planning**
(concrete layer, Rules-Based).

## Concept

Method 007 maps a **story arc** to **register**: the melodic register rises
through the piece toward a climax, then falls back. Each strophic verse carries
its own register center — exposition (low, intimate) → rising action → climax
(high) → denouement (falling) — and within each verse the contour rises to a
local climax (~62% through) before falling.

Phase 1 (`-phase1.mid`) is the raw single-voice narrative stream (off-grid
onsets + unquantized pitch drift). Phase 2 grid-locks, tiered-snaps (strong →
chord tone, weak → F-major scale tone), and builds the full chanson texture.

## Key facts

| Field | Value |
|---|---|
| Style | Chanson |
| Method | 007 Narrative Arc Register Planning (concrete) |
| Form | strophic (4 verses × 8 bars = 32 bars) |
| Key | F major — {5,7,9,10,0,2,4} = F G A Bb C D E |
| Tempo | 72 BPM · 4/4 · 480 TPB |
| Verse register centers | V1 67 (G4) · V2 72 (C5) · V3 77 (F5, climax) · V4 69 (A4) |
| Voices | Violin (lead), Clarinet (counterline), Accordion (pad), Double Bass (bass) |

## Files

- `MIDI/` — `-phase1.mid` (raw draft), `-perfect.mid` (grid-locked),
  `-humanized.mid` (style-derived seeded humanization), each with `.provenance.json`
- `Audio/` — mastered WAV + Opus OGG for all three versions
- `Analysis/` — `grid_visualization.txt`, `manifest.json`, `readback.json`
- `REPORT.md` — full audit (grid / harmony / humanization / loudness)
- `compose.py`, `render_audio.py`, `verify.py` — reproducible pipeline

See `REPORT.md` for the complete two-phase breakdown and verification numbers.
