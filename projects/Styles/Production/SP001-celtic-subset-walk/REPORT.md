# SP-001 FluidSynth SoundFont — Celtic Subset Walk (090-celtic-subset-walk)

**Date:** 2026-09-09 (random-style nightly production pass)
**Job:** `random-style production job (SP methods) — LAYER-ALIGNED (2026-09-02 spec)`

## Selection

| Item | Value |
|---|---|
| Production method | **SP-001 — Multi-timbral SoundFont (FluidSynth)** |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (12 implemented entries, 2026-09-09; NOT methods_db.md spec-only range) |
| Registered module | `sound.render.fluidsynth` (`FluidSynthRenderer` + `RenderPipeline`) |
| Source composition | `/opt/data/projects/Styles/Celtic/090-celtic-subset-walk/MIDI/090-celtic-subset-walk.mid` |
| Composition style | Celtic texture, ABS-002 subset-walk + tension-curve steering, **D minor**, **108 BPM** (tempo 555556), 24 bars / 6 sections, 6 voices: Violin lead (40, ch0), Flute→Recorder counterline (74, ch1), Cello pad (42, ch2), Piano harp rolls (1, ch3), Double Bass→Contrabass roots (43, ch4), Drum kit (ch9) |
| Layer discipline | **Absolute layer**: FluidSynth GM SoundFont rendering is the production/timbre layer for the WHOLE piece — full mix + per-voice stems. GM internal reverb/chorus ON (default production sound). |
| Method pool | Registry = SP-001/011/021/024/026/028/032/033/034/035/036/037. Last-7-day exclusion (dir mtimes ≥ 2026-09-02): SP-032, SP-034, SP-011, SP-033, SP-026, SP-035, SP-037 → available **SP-001, SP-021, SP-024, SP-028, SP-036** → random pick (seed = YYYYMMDD of run date) **SP-001**. |
| Source pick | Seeded random (seed 20260909) over 261 candidate main `.mid` files under `Styles/` (Production/_Data_Patterns/_Comparison excluded, `-phase1` and VoiceAudio intermediates excluded). |

## Pipeline

```
090-celtic-subset-walk.mid
  → RenderPipeline.render_to_wav  (fluidsynth CLI -ni -g 1.2 -r 44100, reverb/chorus ON)
  → peak normalize -1 dBFS, tail trim (content-end + reverb budget)
  → SP001-celtic-subset-walk.wav → .ogg (Opus 48k voip)
  + 6 per-voice stems via RenderPipeline.render_stems (WAV + OGG each)
```

- SoundFont: `discover_soundfont()` → **FluidR3_GM.sf2** (not the TimGM6mb fallback)
- Full mix renders 56.02 s raw (53 s score + GM release tails); pitched content ends 54.29 s; MIDI last note ~55.33 s; trimmed to 56.02 s with natural reverb tail decay (last 2–3 s RMS 0.0004 → 0).

## Parameters

| Param | Value | Meaning |
|---|---|---|
| method | SP-001 | FluidSynth GM SoundFont render |
| soundfont | FluidR3_GM.sf2 (141 MB) | full GM patch set (strings/woodwind/bass/drums) |
| sample_rate | 44100 | output WAV rate |
| gain | 1.2 | fluidsynth `-g` (prevents tail truncation) |
| synth.reverb | ON (GM default) | production space |
| synth.chorus | ON (GM default) | production width |
| normalization | -1 dBFS peak | master ceiling |
| delivery | Opus 48k `-application voip` | Telegram playback |

## Checks & verification

| Check | Result | Verdict |
|---|---|---|
| Pitch (FFT dominant peak, 0.5 s windows, 50–1000 Hz, ±4% vs active MIDI fundamentals) | **107 windows checked, hit rate 0.991** | **PASS** |
| Harmonic energy (first 8 harmonics of lowest active fundamental) | **mean 0.434 (43.4%)** — tonal, not noise | **PASS** |
| Silence ratio (< 0.001 threshold) | **0.0488 (4.9%)** — healthy; tail decay only | **PASS** |
| Per-second RMS | steady 0.06–0.10 across content; decay 0.0416 → 0.0004 → 0 at final reverb tail | PASS |
| WAV size | 9.88 MB full mix (< 100 MB guard) | PASS |
| Stems | 6 × ~9.8 MB WAV + OGG, all > 40 KB | PASS |
| OGG | 366,632 bytes full mix, non-empty | PASS |

Pitch verification details: dominant spectral peak per 0.5 s window was matched
against every MIDI fundamental active in that window (f, f/2, f*2 tolerance
4%). 106/107 windows hit → dense, correctly-pitched texture (violin lead + flute
counterline + piano rolls + contrabass over drum kit). Harmonic-energy mean
43.4% confirms real pitched content (pure noise registers single digits).

## Files

```
SP001-celtic-subset-walk/
├── produce_sp001_cron.py            # this run's generator (reproducible)
├── provenance.json                  # selection, params, checks, artifact map, sha256
├── REPORT.md                        # this file (primary record)
├── MIDI/090-celtic-subset-walk.mid  # source MIDI copy
├── Audio/
│   ├── SP001-celtic-subset-walk.wav  (9,881,644 B, 56.02 s)
│   ├── SP001-celtic-subset-walk.ogg  (366,632 B)
│   └── stems/
│       ├── track00_Violin.wav/.ogg                 (40, ch0)
│       ├── track01_Recorder.wav/.ogg               (74, ch1 — GM label, Flute program)
│       ├── track02_Cello.wav/.ogg                  (42, ch2)
│       ├── track03_Bright_Acoustic_Piano.wav/.ogg  (1, ch3)
│       ├── track04_Contrabass.wav/.ogg             (43, ch4 — GM label, Double Bass program)
│       └── track05_Drums.wav/.ogg                  (ch9)
└── Analysis/
    ├── render_stats.json            # duration, silence, RMS/s, sizes
    └── pitch_verification.json      # hit rate + harmonic energy + verdict
```

Note on stem labels: `RenderPipeline.render_stems` names stems by GM program
name — the source Flute program (74) yields `track01_Recorder` and the Double
Bass program (43) yields `track04_Contrabass` (FluidR3 GM naming). This is the
known, documented labeling quirk — the underlying voice identities are Flute
counterline and Double Bass roots.

## Fixes / notes

- No fixes required this run: single-pass PASS on all gates (pitch 0.991,
  harmonic energy 0.434, silence 4.9%). SP-001 is the always-available baseline
  method; this run documents a clean GM SoundFont production of the 090 Celtic
  subset-walk composition with full stem set for DAW remix.
- Composition `sha256`: see `provenance.json`.
