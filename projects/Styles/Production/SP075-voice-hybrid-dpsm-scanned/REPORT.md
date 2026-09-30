# SP-075 Voice-Like Instrument Hybrid Render — 049-dpsm-scanned

## Job
- **Type**: random-style production (SP) layer-aligned (nightly cron)
- **Date**: 2026-09-30
- **Seed**: 20260930
- **Registry source**: `SP_METHODS` in `workflows/musicom_workflow.py` (single source of truth)
- **Registry size**: 35 implemented methods
- **Recent (7-day) excluded**: SP-011, SP-024, SP-032, SP-069, SP-070, SP-079, SP-081

## Selection
- **Method**: SP-075 — `sound.render.hybrid`
- **Description**: Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)
- **Source composition**: `Styles/Experimental/049-dpsm-scanned/MIDI/049-dpsm-scanned.mid`
  - Deconstructive Phase-Shift Minimalism (Method 026) + Scanned Synthesis (SP-018)
  - 110 BPM, C Dorian, 8 bars, 3 voices, 17.45 s

## Method application (absolute layer)
SP-075 is an absolute-layer production method: the whole piece is re-realized
through it. Voice-like instruments have **no GM soundfont equivalent**, so the
hybrid maps the melodic lead voices onto synthesized voice-like instruments and
keeps the harmonic foundation on the FluidSynth soundfont.

Note-bearing tracks (tempo track 0 skipped by `parse_tracks()`):
| track | voice | program/ch | engine | instrument |
|-------|-------|-----------|--------|-----------|
| 0 | Piano1 (static loop)  | 0/0 | voice_like | `singing_saw` |
| 1 | Piano2 (phase-shift)  | 0/1 | voice_like | `talkbox` |
| 2 | Bass (roots)         | 32/2 | fluidsynth | soundfont |

`voice_instruments = ["singing_saw", "talkbox", None]` — the two DPSM pianos
(an identical 16th-note loop, one static, one phase-shifting) become a
"singing saw" + "talkbox" duet whose phase drift is now audible as two
different voices sliding out of phase; the bass stays a real bass.

## Parameters
- bpm = 110.0 (read from MIDI tempo 545455 us/qn), sr = 44100
- vowels = aoeauo (6-vowel "singing" cycle, per-note articulation)
- voice_gain = 1.0, backing_gain = 1.0
- seed = 20260930 (per-track voice seed = seed + idx*7919)
- available voice-like instruments: ['didgeridoo', 'jaw_harp', 'kazoo', 'singing_saw', 'talkbox', 'vox_humana']

## Verification
Pitch verification is against the **expected MIDI note frequencies** (not the
dry piano render): SP-075 replaces timbre, so a dry-vs-wet spectral-dominant
match is meaningless. Each 0.5s window's FFT dominant peak (50-1000 Hz) is
compared to the notes the source MIDI sounds in that window.
- **Pitch verdict**: PASS
- MIDI-note hit rate: 1.0000 (>= 0.60 required)
- harmonic energy (at expected notes' harmonics, 1..8): 0.9671 (>= 0.25 required)
- ACF unpitched windows: 0/9 (< 0.50 required)
- LUFS: -14.24, peak: 0.8913, silence: 4.95%
- RMS per second: [0.1698, 0.2163, 0.206, 0.2353, 0.2174, 0.2032, 0.2138, 0.2056, 0.2083, 0.2054, 0.1997, 0.2082, 0.2057, 0.2003, 0.21, 0.2388, 0.211, 0.1282]

## Files
- final WAV: `/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-dpsm-scanned/SP075-voice-hybrid-dpsm-scanned.wav` (3220144 bytes)
- final OGG: `/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-dpsm-scanned/SP075-voice-hybrid-dpsm-scanned.ogg` (149853 bytes)
- dry reference: `/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-dpsm-scanned/dry_full_mix_sp001_reference.wav`
- dry stems: `Audio/stems_dry/` (3 files)
- wet stems: `Audio/stems_wet/` (3 files)
- provenance: `provenance.json`, render stats: `Analysis/render_stats.json`
- pitch verification: `Analysis/pitch_verification.json`, grid: `Analysis/grid_visualization.txt`

## Fixes applied
1. **`sound/synthesis/voice_like.py` release-envelope bug**: `render_note()` set
   `env[-r_n:] *= linspace(1,0,r_n)` with `r_n` = release_samples unclamped.
   For short notes (DPSM 16th notes are ~0.114 s = 5011 samples) shorter than
   the release (singing_saw release = 0.30 s = 13230 samples), this produced a
   broadcast error (`(5011,)` vs `(13230,)`) and crashed every note. Fixed by
   clamping `r_n = min(r_n, n)` (and `a_n = min(a_n, n)` for the attack) so the
   envelope never exceeds the note length. Correct and minimal.
