# REPORT — 084 Soul Voice-Leading Graph

**Project**: 084-soul-voiceleading-graph
**Style**: Soul · **Method**: 011 Voice-Leading Graph Search (TonalNetworkGenerator)
**Key/Tempo**: D minor · 92 BPM · 4/4 · 24 bars (6 sections × 4)
**Date**: 2026-09-02 (daily algorithmic composition job, run 2)

## Status

✅ **AUDIT PASS** — 0 off-grid (16th), 0 out-of-scale, 0 out-of-chord, 0 voice-leading flags.
✅ **Audio rendered** (SP-001 FluidSynth, FluidR3 via discover_soundfont) + analysis pass.

## What changed in this run

1. **Lead dedup post-quantization** (`dedup_by_start_pitch` in compose): off-grid
   random-walk events that collided onto the same (start_tick, pitch) after 8th-grid
   snapping became ONE event (longest duration wins). Lead 147 → 135 notes
   (12 doubled-note artifacts removed — audible as machine-gun repeats).
2. **Audit bar-attribution fixed** (audit_084): harmony check now attributes a note
   to the bar where it STARTS (`t // BAR`, matching compose's floor quantization),
   with an explicit exception for genuine 16th-note anticipations at the bar
   boundary (`t % BAR == BAR - 120`) that play the NEXT bar's root (bass push).
   The old `round(t / BAR)` misattributed notes in the last portion of every bar
   to the next bar's chord → 238 false harmony violations (40 lead + 119 piano +
   54 guitar + 25 bass), ALL boundary mismatches, ZERO real mid-bar violations.

## Verification

| Check | Result |
|---|---|
| Phase-1 validate (zero-drift) | OK |
| Phase-2 validate (zero-drift) | OK |
| Grid audit (16th, all voices) | 0 off-grid |
| Harmony audit (scale/chord) | 0 / 0 |
| Voice-leading flags (classical) | 0 |
| Lead dedup | 147 → 135 notes |

## Audio

| Render | WAV | OGG | Silence | Buzz 4-8k |
|---|---|---|---|---|
| Full mix (66.75 s) | 11.8 MB | 444 KB | 6.3% | 10.0% OK |
| Phase-1 draft (64.61 s) | 11.4 MB | 565 KB | 13.7% | 4.2% OK |

SoundFont: **FluidR3_GM.sf2** via `discover_soundfont()` (TimGM6mb was the thin
fallback — oboe/bassoon/strings buzzed; fixed 2026-09-01 across all test WAVs).

## Files

- `MIDI/084-soul-voiceleading-graph-phase1.mid` — raw tonal-graph walk (1 voice)
- `MIDI/084-soul-voiceleading-graph.mid` — phase-2 full arrangement (6 voices)
- `Audio/*.wav|*.ogg` + provenance sidecars
- `Analysis/audit.json`, `vl_audit.json`, `summary.json`, `render_stats.json`,
  `grid_visualization.txt`
- `compose_084.py`, `audit_084.py`, `render_audio.py`, `audio_stats.py`,
  `audio_provenance.py`

## Voices

Tenor-Sax lead (graph-walk, chord-tone quantized, leap cap 9) · Rhodes offbeat
comp · Violin whole-bar triad pad · Acoustic-Guitar 8th strum · Electric-Bass root
pulse (16th next-bar push in verses/choruses) · Backbeat drums (kick 1&3, snare
2&4, 16th hats + claps in choruses).
