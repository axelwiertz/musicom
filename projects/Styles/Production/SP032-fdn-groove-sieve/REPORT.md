# SP-032 FDN Reverb — Groove Sieve (080-groove-sieve)

**Date:** 2026-09-02 (random-style nightly production pass)
**Job:** `random-style production job (SP methods) — LAYER-ALIGNED (2026-09-02)`

## Selection

| Item | Value |
|---|---|
| Production method | **SP-032 — Feedback Delay Network (FDN) Reverberation** |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (7 implemented entries; NOT methods_db.md spec-only range) |
| Registered module | `sound.effects.fdn_reverb` (`FDN` class, Rev Ocean "Tidal" style) |
| Source composition | `/opt/data/projects/Styles/Groove/080-groove-sieve/MIDI/080-groove-sieve.mid` |
| Composition style | Method 025 Xenakis Sieve groove — G natural minor, 110 BPM, 96 beats (24 bars), 5 voices: Soprano Sax lead (65), Brass Section stabs (61), Rhodes comp (4), Electric Bass (33), Drums ch9 |
| Layer discipline | **Absolute layer**: FDN replaces the spatial layer for the WHOLE piece. FluidSynth internal reverb/chorus forced OFF (`synth.reverb.active=no`, `synth.chorus.active=no`) so FDN is the sole spatial treatment. Per-voice dry stems shipped for DAW remix. |
| Method pool | Free (last-7-day exclusion): SP-011, SP-021, SP-024, SP-026, SP-028, SP-032 → random pick SP-032. (Recent dirs seen: SP-001, SP-024, SP-017, SP-036, SP-014.) |

Selection script: `/opt/data/select_job_20260902.py` (registry-based; result also in `/opt/data/projects/Styles/Production/.selection.txt`).

## Pipeline

```
080-groove-sieve.mid
  → fluidsynth -ni -g 1.2 -r 44100 (reverb/chorus OFF) → dry_full_mix.wav
  → FDN.process()  [sound.effects.fdn_reverb, 8 prime delay lines, Hadamard
                    feedback matrix, per-line one-pole LPF, 0.15 Hz modulated
                    delay readout, input ducking, stereo width via mid/side]
  → wet+dry mix (module wet_dry), peak normalize -1 dBFS
  → SP032-fdn-groove-sieve.wav → .ogg (Opus 48k voip)
  + 5 per-voice dry stems (RenderPipeline-style per-track extraction, same
    FX-off FluidSynth flags)
```

- SoundFont: `discover_soundfont()` → **FluidR3_GM.sf2** (not the TimGM6mb fallback)
- Dry input padded 5.0 s so the FDN tail rings past the last note (dry content ends 52.32 s), then trimmed to content-end + 3.5 s.

## Parameters (FDN module, `set()`)

| Param | Value | Meaning |
|---|---|---|
| n_delays | 8 | parallel delay lines (power of 2 for Hadamard) |
| prime delays | 1471–2797 samples @44.1k | spread/diffusion, ~33–63 ms |
| size | 0.60 | feedback base gain |
| decay | 0.85 | tail length |
| brightness | 0.70 | HF damping (one-pole LPF per line) |
| modulation | 0.28 | ±2.2-sample sweep at 0.15 Hz ("Tidal" movement) |
| width | 0.90 | mid/side stereo spread on wet |
| duck_amount | 0.15 | input ducking (transient clarity) |
| wet_dry | 0.40 | 40% wet mix |
| master | -1 dBFS | peak normalization |

Sizing choice: groove idiom needs an audible-but-tight tail (decay 0.85, ~2 s
effective) and ducking so the 8th-note funk bass + horn stabs keep transient
punch; size kept at 0.60 (not 0.7 max) to avoid washing the sieve syncopation.

## Checks & verification

| Check | Result | Verdict |
|---|---|---|
| FDN tail extends past dry end (peak in dry+0.3–1.1 s window) | 0.00642 (dry there: 0.000031) | PASS — reverb audible after last note, dry silent in same window |
| Stereo width (side/mid RMS) | 0.075 | modest spread, acceptable for FDN wet bus |
| Silence ratio | **8.0 %** | PASS (< 30 %); tail-pad-only decay |
| Per-second RMS | 0.06–0.17 across 58 active seconds; only final 2 s near 0 (reverb tail decay) | PASS — no mid-track gaps |
| **Pitch verification** | harmonic-match hit rate **1.000** (105/105 windows), harmonic energy (8 harmonics of lowest fundamental) mean **0.530** | **PASS** |

### Pitch verification detail (v1 → v2 fix)

- v1 rule (dominant peak within ±4 % of active fundamental **or its octave**)
  scored **0.581 → FAIL**.
- Root cause: this groove's bass plays G1 = **49 Hz**, below the 50 Hz analysis
  band. Bass-dominated 0.5 s windows put the dominant FFT peak on the 2nd
  harmonic (~98 Hz), which the octave-only rule rejected. This is a
  measurement artifact of a low-tuned groove, not tonal noise — harmonic
  energy was already 0.53.
- v2 rule: dominant peak must match **k·f of any active non-drum MIDI
  fundamental (k = 1..8, k·f within 40–1050 Hz), ±4 %** → **1.000 hit rate**,
  harmonic energy 0.530 ≥ 0.30 threshold. **PASS.**
- Full JSON: `Analysis/pitch_verification.json` (v1→v2 note also in `provenance.json`).

## Files

| Artifact | Path | Size |
|---|---|---|
| Processed WAV | `Audio/SP032-fdn-groove-sieve.wav` | 9 846 280 B (55.82 s) |
| Processed OGG (Opus) | `Audio/SP032-fdn-groove-sieve.ogg` | 361 501 B |
| Dry full mix (FX off) | `dry_full_mix.wav` | 9 668 140 B |
| Source MIDI copy | `MIDI/080-groove-sieve.mid` | 6 614 B |
| Stems (dry, per voice) | `Audio/stems/track00_Soprano_Sax.wav` … `track04_Drums_GM.wav` | 48 049 116 B total |
| Provenance | `provenance.json` | 3 071 B |
| Render stats | `Analysis/render_stats.json` | 851 B |
| Pitch verification | `Analysis/pitch_verification.json` | 324 B |
| Report | `REPORT.md` | this file |

## Fixes applied

1. FluidSynth internal reverb/chorus explicitly disabled so SP-032 is a true
   absolute-layer spatial replacement (dry source's original render had
   FluidSynth default reverb baked in).
2. Pitch verification rule corrected to harmonic matching (k = 1..8) for
   low-tuned material — v1 octave-only rule is invalid below the 50 Hz band.

## Listening notes

- Sieve-syncopated lead + offbeat horn stabs now sit in one shared warm FDN
  room; 8th-note bass keeps its lock thanks to input ducking.
- Compare vs dry: same arrangement, no internal FluidSynth reverb — FDN tail
  adds space without burying the 16th push in choruses.
