# 094-african-hierarchical-diffusion

**Style**: African (Mande / djembe drum-ensemble idiom) · **Layer**: `concrete`
**Method**: 010 Hierarchical Diffusion (multi-level Markov base) — `generators.chain.MarkovChainGenerator`
**Key**: A dorian · **BPM**: 112 · **Form**: 6 sections × 4 bars = 24 bars
**Seed**: 20260912 · **Grid**: 16th (120 ticks @ 480 TPB)

Nightly autonomous composition (2026-09-12). Style drawn from the 41 genre folders
(excluding the 6 recently used styles); method drawn from `select_for_cron()` minus the
last-7-day methods (`001, 010, 023, 040, HC-012` eligible → 010 drawn).

## Idea

Method 010 is a **diffusion of Markov chains down a hierarchy**: a macro chain plans the
song's energy per section, each section spawns a bar-level chain, each bar a beat-level
chain, and each beat expands into 1–4 onsets on the 16th grid. The result is one
musical object whose every rhythm came from a single method, at four resolutions.
The African (Mande) idiom supplies the instrumentation — kalimba lead, balafon
interlock, fula flute counterline, kora arpeggio, dundun/root bass, djembe ensemble —
and per-voice rotation of the L1 onset offsets creates the interlocking hocket feel.

## Two-phase

| Phase | Files | What |
|---|---|---|
| 1 (raw) | `MIDI/*-phase1.mid`, `Audio/*-phase1.ogg` | Unquantized single-voice Markov draft: 7-state pitch map including out-of-key C#/G#, fractional 417-tick onset interval → 96/102 onsets off-grid |
| 2 (rules) | `MIDI/*.mid`, `Audio/*.ogg` | 4-level diffusion → 16th grid lock → A-dorian chord-tone quantization → voice-leading repair → 6-voice texture |

## Verified (see `REPORT.md` for full numbers)

- **Grid**: 0/1433 onsets off the 16th grid (all voices)
- **Harmony**: 0 out-of-scale, 0 out-of-chord (all pitched voices, canonical degree helper)
- **Zero-drift**: all tracks end at 46080 ticks
- **Audio**: 62.8 s, peak 0.890, silence 15.76 % (tail decay only, no mid-track gaps)
- **Tonal**: phase-1 102/102 fundamentals present · melodic chroma 90.5 % in-key

## Listen for

1. **Intro → KoraVerse**: the bass is sparse in the intro (L4 state 0) and the L2 beat
   chain fills it in as density rises.
2. **Chorus**: kalimba and balafon interlock — same tempo, offset 16ths (rotations 0 and 2),
   so the two lines trade accents instead of doubling.
3. **Phase-1 vs phase-2**: the raw draft wanders off-key (C#, G#) and drifts against the
   grid — that is the method pre-rules; phase 2 keeps the contour but snaps it into A dorian.

## Layout

```
MIDI/     phase-1 + phase-2 MIDI (+ provenance sidecars)
Audio/    OGG renders (+ provenance sidecars)
Analysis/ grid_visualization.txt, audit.json, tonal_check.json,
          render_stats.json, render_info.json, summary.json, concept.json
Scripts/  compose.py audit.py render_audio.py audio_stats.py tonal_check.py summarize.py
REPORT.md index.html
```
