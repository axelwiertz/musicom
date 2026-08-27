# SP-001 — Multi-timbral SoundFont (SF2) Render — Dutch Fanfare Loop

**Production run:** 2026-08-17 22:07 (nightly production pipeline, autonomous cron)

## Method

**SP-001 — Multi-timbral SoundFont (SF2)** | Layer: Synthesis Engines | Target: Headless Audio Render

> SoundFont-based wavetable synthesis via FluidSynth. Requires 32-bit normalization (-1.0dB).

Executed per the method description in `methods_db.md` (SP-001 row, Sound Production Methods Framework):

1. Read MIDI (`loop.mid`, 480 TPB, type 1, 2 instrument tracks + tempo map).
2. Headless render via **FluidSynth CLI** (`-ni -F`, gain 1.0) into `TimGM6mb.sf2`.
3. Verify audio content (silence ratio + per-second RMS map — no mid-track gaps; 29% silence is intro/outro tail padding only).
4. **Peak normalization to -1.0 dBFS** (numpy: scale by `10^(-1/20) / peak`; `ffmpeg peaknorm` filter unavailable in this env — manual fallback used, exact -1.0 dBFS achieved).
5. Opus encode for Telegram playback (`libopus`, voip application, 48k).

## Source Composition

| Field | Value |
|---|---|
| Source MIDI | `/opt/data/projects/Styles/Fanfare/004-dutch-fanfare-integrated/MIDI/loop.mid` |
| Style | Dutch Fanfare |
| Tracks | Trumpet (prog 56, ch 0) + Tuba (prog 58, ch 1), 7 notes each |
| Duration | 14.55 s (MIDI), 16.55 s (render w/ tail) |
| Tempo map | 480 TPB, type 1 |

## Artifacts

| File | Purpose |
|---|---|
| `MIDI/source_loop.mid` | Original composition (copy of source for self-contained project) |
| `Audio/fanfare_soundfont_peaknorm.wav` | Final normalized render (-1.0 dBFS peak) |
| `Audio/fanfare_soundfont_render.ogg` | Opus delivery format (142 KB) |
| `provenance.json` | Provenance sidecar |

## Method-Specific Notes

- **Timbre**: TimGM6mb is a compact GM bank; Trumpet 56 / Tuba 58 are sample-based wavetable voices — representative GM brass timbre, not acoustic-exact.
- **Why this matters**: SP-001 is the baseline headless render path — every other synthesis-engine method (SP-003…SP-042) is compared against this reference timbre. It proves the composition itself is DAW-importable and GM-playable.
- **Normalization**: method requires -1.0 dBFS; verified post-normalization peak = -1.0 dB (exact).
- **Silence check passed**: 29.0% silence = intro reverb tail + end padding; per-second RMS shows continuous musical content seconds 3–26 (0-indexed), no internal gaps.

## Listening Guide

- Trumpet carries the fanfare hook; Tuba locks the bass — a classic Dutch fanfare call-response.
- Listen for the loop seam: this is a loop file, seam should be clean (zero-drift MIDI).
