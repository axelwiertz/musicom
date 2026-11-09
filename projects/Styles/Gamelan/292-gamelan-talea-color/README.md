# 292 — Gamelan Isorhythmic Talea-Color

A gamelan-flavored composition built with **Method 032 — Isorhythmic
Talea-Color Mapping (ITCM)** (concrete layer, Rules-Based).

## Concept

The medieval isorhythmic decoupling of **talea** (fixed rhythm) from **color**
(fixed pitch sequence) — lengths chosen **coprime** so the two cycles drift out
of phase and only realign after their least common multiple:

- **Color**: 5-note C-pentatonic pitch sequence `[C E A G D]` (length 5).
- **Talea**: 7-duration rhythm `[2 3 2 2 3 2 2]` sixteenths (length 7, sums to 1 bar).
- LCM(5, 7) = 35 → the pitch/rhythm pairing shifts continuously and realigns
  only every 35 notes.

Mapped onto a **gamelan** texture: the isorhythmic line is the *balungan*
(core melody), over a colotomic *gong* cycle, an interlocking *kotekan*
16th-note figuration, and a sustained *saron* "sléndro trichord" pad.

## Key facts

| Field | Value |
|---|---|
| Style | Gamelan |
| Method | 032 Isorhythmic Talea-Color Mapping (concrete) |
| Form | through-composed (6 sections × 4 bars = 24 bars) |
| Key | C major pentatonic (sléndro) — {0,2,4,7,9} |
| Tempo | 100 BPM · 4/4 · 480 TPB |
| Voices | Marimba (balungan), Steel Drums (kotekan), Celesta (saron), Double Bass (gong) |

## Files

- `MIDI/` — `-phase1.mid` (raw draft), `-perfect.mid` (grid-locked),
  `-humanized.mid` (style-derived seeded humanization), each with `.provenance.json`
- `Audio/` — mastered WAV + Opus OGG for all three versions
- `Analysis/` — `grid_visualization.txt`, `manifest.json`, `readback.json`
- `REPORT.md` — full audit (grid / harmony / humanization / loudness)
- `compose.py`, `render_audio.py`, `verify.py` — reproducible pipeline

See `REPORT.md` for the complete two-phase breakdown and verification numbers.