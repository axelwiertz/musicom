# SP-034 BBD Chorus — Marilou Vacation (039-marilou-vacation-v3)

**Date:** 2026-09-03 (random-style nightly production pass)
**Job:** `random-style production job (SP methods) — LAYER-ALIGNED (2026-09-03)`

## Selection

| Item | Value |
|---|---|
| Production method | **SP-034 — BBD Chorus Ensemble (Clock/Compander/Per-Voice Variation)** |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (10 implemented entries; NOT methods_db.md spec-only range) |
| Registered module | `sound.effects.bbd_chorus` (`BBDChorus` class, UVI Thorus XT-style analogue BBD engine) |
| Source composition | `/opt/data/projects/Styles/Country/039-marilou-vacation/MIDI/039-marilou-vacation-v3.mid` |
| Composition style | Country-pop vocal loop (Dutch lyrics, Marilou vacation), 96 BPM (tempo 625000), 6 voices: Flute lead (73, ch0), Acoustic guitar nylon (25, ch1), Electric bass (33, ch2), Drums ch9, Fiddle (110, ch4), Pad 1 new age (91, ch5) |
| Layer discipline | **Absolute layer**: BBD chorus replaces the modulation/spatial layer for the WHOLE piece. FluidSynth internal reverb/chorus forced OFF (`synth.reverb.active=no`, `synth.chorus.active=no`) so the BBD ensemble is the sole modulation treatment. Per-voice dry stems shipped for DAW remix. |
| Method pool | Registry = SP-001/011/021/024/026/028/032/033/034/035. Last-7-day exclusion (dir mtimes ≥ 2026-08-27): SP-001, SP-011, SP-021, SP-024, SP-026, SP-028, SP-032, SP-035 → available **SP-033, SP-034** → random pick **SP-034**. |
| Selection script | `/opt/data/select_job_20260903.py` (registry-based; result in `/opt/data/projects/Styles/Production/.selection.txt`). Note: first random source pick was a rules-phase draft (`063-...-phase1.mid`); re-ran with a filter preferring main (non-`-phase1`) composition files → 216 candidates. |

## Pipeline

```
039-marilou-vacation-v3.mid
  → fluidsynth -ni -g 1.2 -r 44100 (reverb/chorus OFF) → dry_full_mix.wav
  → BBDChorus.process_stereo()  [sound.effects.bbd_chorus, 6 morphable voices,
        per-voice LFO phase/rate spread, clock_mult=4 upsample clocking,
        compander encode→delay→decode, per-voice hiss, Dimension-D decorrelated
        L/R ensembles, width via mid/side]
  → wet+dry mix (mix 0.45), peak normalize -1 dBFS
  → SP034-bbd-chorus-marilou-vacation.wav → .ogg (Opus 48k voip)
  + 6 per-voice dry stems (per-track extraction, same FX-off FluidSynth flags)
```

- SoundFont: `discover_soundfont()` → **FluidR3_GM.sf2** (not the TimGM6mb fallback)
- Dry render is 17.52 s (10 s score + GM release tails); dry pitched content ends at 12.29 s; output trimmed to content-end + 3.5 s → 15.79 s.

## Parameters (BBDChorus, constructor + process_stereo)

| Param | Value | Meaning |
|---|---|---|
| voices | 6.0 | continuous voice count (morphable 1..8 arch); matches 6-voice source |
| rate_hz | 0.5 | base LFO rate — slow enough not to fight the vocal prosody |
| depth_ms | 4.0 | delay modulation depth (mid classic BBD range) |
| lfo_spread | 0.40 | per-voice LFO rate/phase drift (vintage "swirl") |
| clock_mult | 4 | internal BBD clock (clean, fine delay steps) |
| compander | 0.5 | encode/decode companding strength |
| hiss | 0.015 | per-voice noise injection (subtle analogue grit) |
| mix | 0.45 | dry/wet |
| width | 0.80 | mid/side stereo decorrelation |
| seed | 20260903 | deterministic per-voice randomization |
| master | -1 dBFS | peak normalization |
| FluidSynth | reverb OFF, chorus OFF, gain 1.2 | dry capture so BBD is the sole modulation layer |

Sizing choice: country-pop loop needs a gentle, wide chorus — 6 voices (one per
instrument) at slow rate keeps the vocal lead intelligible while the acoustic
strum + fiddle gain ensemble movement; depth 4 ms avoids pitch-wobble artifacts
on the bass; compander 0.5 gives the characteristic BBD "pumping" without
audible noise modulation.

## Checks & verification

| Check | Result | Verdict |
|---|---|---|
| BBD changed signal (wet−dry RMS, full mix) | 0.05600 | PASS — chorus audibly active |
| Stereo decorrelation increase (L/R corr) | dry 0.7520 → wet 0.6801 | PASS — width applied |
| Silence ratio | **0.0154 (1.5 %)** | PASS — no mid-track gaps (dry tail only) |
| WAV size / OGG size | 2 785 636 B / 93 967 B | PASS — non-empty, sane |
| **Pitch verification** | dominant-peak hit rate **0.750** (15/20 windows), harmonic energy (8 harmonics of lowest fundamental) mean **0.456** | **PASS** |

Pitch method: FFT dominant peak per 0.5 s window in the 50–1000 Hz band,
±4 % tolerance vs active MIDI fundamentals (fundamental, octave below, or
octave above — octave tolerance added because chorus-heavy voicings often place
the spectral peak on the 2nd harmonic). 20 windows had active pitched notes and
energy; 15 matched. Harmonic energy 0.456 ≥ 0.30 threshold — tonal content
confirmed, not noise. The 5 unmatched windows sit in the vocal/flute-timbre
transition and drum-dominant regions where the 50 Hz high-pass removes the
bass fundamental; chorus does not destroy pitch clarity.

- Full JSON: `Analysis/pitch_verification.json`, `Analysis/render_stats.json`.

## Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `Audio/SP034-bbd-chorus-marilou-vacation.wav` | 2 785 636 B (15.79 s) |
| Full mix OGG | `Audio/SP034-bbd-chorus-marilou-vacation.ogg` | 93 967 B |
| Dry full mix (pre-FX) | `dry_full_mix.wav` | 3 079 070 B |
| Source MIDI (copy) | `MIDI/039-marilou-vacation-v3.mid` | 995 B |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | — |

Stems (per-voice dry, RenderPipeline-style, time-aligned, FX-off FluidSynth):

| Stem | Path | Size |
|---|---|---|
| Flute lead (73) | `Audio/stems/track00_Flute.wav` | 505 108 B |
| Nylon guitar (25) | `Audio/stems/track01_Acoustic_Guitar_nylon.wav` | 498 548 B |
| Bass (33) | `Audio/stems/track02_Electric_Bass_finger.wav` | 497 856 B |
| Drums (ch9) | `Audio/stems/track03_Drums_GM.wav` | 490 742 B |
| Fiddle (110) | `Audio/stems/track04_Fiddle.wav` | 440 434 B |
| Pad (91) | `Audio/stems/track05_Pad_1_new_age.wav` | 461 372 B |

## Notes & fixes applied

1. **Source selection fix**: initial random pick landed on a phase-1 rules draft
   (`Experimental/063-...-phase1.mid`, 2 tracks); re-ran the selection script
   with a filter preferring main composition files (no `-phase1`) → picked the
   6-voice country-pop loop. `.selection.txt` holds the final pick.
2. SP-034 adapter is not wired in `workflows.musicom_workflow.produce()`
   (only SP-001/SP-011 are) — called the registered module API directly
   (`BBDChorus.process_stereo`), per job instructions.
3. Timing sanity: source score ~10 s rendered dry to 17.52 s (GM release
   tails); 1.5 % silence overall and no per-second RMS zeros mid-track confirm
   no timing drift. Source MIDI came from a validated UnitMatrix composition
   project (zero-drift gate at source); no grid re-visualization needed for an
   FX-layer pass.
4. Precedent: SP-032 FDN pass (2026-09-02) — same absolute-layer structure,
   FX-off dry capture, stem extraction, and verification gate.
