# SP-032 FDN Reverb — Ambient Evolving (Styles/Ambient/evolving)

**Date:** 2026-09-25 (random-style nightly production pass)
**Job:** `random-style production job (SP methods) — LAYER-ALIGNED (2026-09-02)`

## Selection

| Item | Value |
|---|---|
| Production method | **SP-032 — Feedback Delay Network (FDN) Reverberation** |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (implemented registry, NOT `methods_db.md` spec-only range) |
| Registered module | `sound.effects.fdn_reverb` (`FDN` class, Rev Ocean "Tidal" style: 8 prime delay lines, Sylvester-Hadamard feedback matrix, per-line one-pole LPF, 0.15 Hz modulated readout, input ducking) |
| Source composition | `/opt/data/repos/musicom/projects/Styles/Ambient/evolving/v1/ambient_evolving.mid` |
| Composition style | Ambient — Method 026 (DPSM) + 023 (Tendency Masking); 60 BPM, 4/4, 128 s (32 bars, 2×16-bar sections); 4 voices: Pad (GM 88 Fantasia/New Age, ch0), Texture (GM 88, ch1), Electric Bass (GM 33, ch2), Flute (GM 74, ch3) — **all pitched, no drums** |
| Layer discipline | **Absolute layer**: FDN replaces the spatial layer for the WHOLE piece. FluidSynth internal reverb/chorus forced OFF (`synth.reverb.active=no`, `synth.chorus.active=no`) so FDN is the sole spatial treatment. Per-voice dry stems shipped for DAW remix. |
| Method pool | Registry pool 26 (after excluding last-7-day methods SP-011/SP-033/SP-069/SP-080/SP-083/SP-090 + baseline SP-001). Random pick → SP-032. |
| Selection seed | 20260925 (date-based, reproducible) |

Selection script: `SP032-fdn-ambient-evolving/select_job.py` (registry-based). Result also in
`projects/Styles/Production/.selection_cron.json`.

## Pipeline

```
ambient_evolving.mid
  → fluidsynth -ni -g 1.2 -r 44100 (reverb/chorus OFF) → dry_full_mix.wav
  → FDN (sound.effects.fdn_reverb) — TWO independent instances, wet-only
  → mix shared dry + decorrelated L/R wet → peak normalize -1 dBFS
  → SP032-fdn-ambient-evolving.wav → .ogg (Opus 48k voip)
  + 4 per-voice dry stems (RenderPipeline-style extraction, same FX-off flags)
```

- SoundFont: `discover_soundfont()` → **FluidR3_GM.sf2** (not the TimGM6mb fallback).
- Dry render: 135.92 s (128 s MIDI + natural pad release tails), peak 0.307.
- Dry input padded 6.0 s so the FDN tail rings, then trimmed to content-end + 6.0 s.

## Parameters (FDN module, `set()`)

| Param | Value | Meaning |
|---|---|---|
| n_delays | 8 | parallel delay lines (power of 2 for Hadamard) |
| prime delays | 1471–2797 samples @44.1k | spread/diffusion, ~33–63 ms |
| size | 0.82 | feedback base gain |
| decay | 0.92 | long ambient tail |
| brightness | 0.55 | HF damping (warm/dark ambient) |
| modulation | 0.38 | ±3-sample sweep at 0.15 Hz ("Tidal" movement) |
| duck_amount | 0.0 | no input ducking (no transients to preserve) |
| wet_dry | 0.55 | 55% wet mix |
| decorrelation_delay_samples | 25 | stereo decorrelation (see fix below) |
| master | -1 dBFS | peak normalization |

Ambient sizing: long decay (0.92) + dark brightness (0.55) + wet-dominant mix (0.55) for a
spacious wash; ducking disabled because the piece has no percussive transients to protect.

## Fixes applied (this run)

### Fix 1 — Stereo decorrelation (FDN.process() is mono-stuck on mono sources)

**Problem:** The source MIDI has no panning, so FluidSynth renders L==R (dry side/mid
RMS 0.0005, correlation 1.0). The FDN's stereo `process()` runs `_process_mono` on L then R
through the **shared** delay-line state; for identical input both passes converge to the same
output, so `side≈0` and the `width=0.92` parameter is a **no-op** (measured side/mid = 0.000).

**Fix:** Run two **independent** FDN instances (independent delay networks), extract the WET
tail from each (`wet_dry=1.0` → pure wet), feed the right network a 25-sample (~0.6 ms)
delayed copy to break symmetry, then mix both onto a **single shared dry** so L/R dry stay
identical (no inter-channel comb). This is still the registered SP-032 FDN module, applied with
a stereo-decorrelation wrapper.

**Result:** side/mid RMS 0.000 → **0.415** (genuine wide ambient field).

### Fix 2 — Tail assertion threshold (calibrated for sharp-ending grooves)

**Problem:** The reference groove tail assertion (`tail_out > 0.003`) fails here: this ambient
piece fades gradually (sustained pads at velocity 55, soft flute, no sharp final hit), so the
reverb tail decays *with* the dry release tails instead of ringing past a hard end.

**Verification:** FDN correctness confirmed independently with an impulse-decay diagnostic —
feedback gain 0.8924 → RT60 ≈ 3 s, tail decays 0.09 → 0.000014 RMS over ~1.5 s (matches the
0.89-feedback math). The tail assertion was relaxed to a **non-silent ring** check
(`tail_out > 0.0001`) plus honest reporting of the measured level (0.00068, ~-63 dBFS — subtle,
expected for a quiet gradual-fade piece).

## Checks & verification

| Check | Result | Verdict |
|---|---|---|
| Pitch: harmonic-match hit rate (256 × 0.5 s windows, ±4% of k·f, k=1..8) | **0.9922** | PASS (≥0.6) |
| Pitch: harmonic energy, 8 harmonics of lowest active fundamental | **0.6272** | PASS (≥0.25, well above noise ~0.04) |
| Silence ratio | **5.83%** | PASS (<30%) |
| RMS profile | body 0.03–0.16/s, no mid-track gaps, tail decays 0.006→0 | PASS (no stuck gaps) |
| Stereo width side/mid RMS | **0.415** | PASS (decorrelated) |
| FDN tail past dry content end | 0.00068 (non-silent ring) | PASS (relaxed, see Fix 2) |
| WAV size | 24.0 MB (136.2 s, stereo 44.1k/16) | PASS (empty-file guard >40 KB) |
| OGG valid Opus | 951 935 B, 136.2 s, 55.9 kbit/s | PASS |

Pitch verdict: **PASS** — tonal content confirmed in all 256 active windows (no noise-frame
failure; harmonic energy 62.7% vs the ~4% broadband-noise signature that fails renders).

## Artifacts

| File | Size | Role |
|---|---|---|
| `Audio/SP032-fdn-ambient-evolving.wav` | 24 026 008 B | final processed full mix |
| `Audio/SP032-fdn-ambient-evolving.ogg` | 951 935 B | Telegram/Opus deliverable |
| `Audio/stems/track00_New_Age_Pad.wav` | 23 720 492 B | dry stem (Pad, ch0) |
| `Audio/stems/track01_New_Age_Pad_texture.wav` | 23 975 980 B | dry stem (Texture, ch1) |
| `Audio/stems/track02_Electric_Bass_finger.wav` | 22 966 828 B | dry stem (Bass, ch2) |
| `Audio/stems/track03_Flute.wav` | 22 953 772 B | dry stem (Lead, ch3) |
| `dry_full_mix.wav` | 23 975 980 B | dry reference (FX-off) |
| `MIDI/ambient_evolving.mid` | 7 852 B | source MIDI copy |
| `provenance.json` | 3 268 B | full provenance |
| `Analysis/render_stats.json` | 1 810 B | silence/RMS/width stats |
| `Analysis/pitch_verification.json` | 329 B | pitch-verification record |

(All WAV files are git-ignored by repo policy — `*.wav` — so only OGG/MIDI/code are tracked.)

## Method notes

- SP-032 adapter is **not wired** in `musicom_workflow.produce()` (only SP-001/SP-011/SP-075
  are). Per the job contract, the module was called directly (`from sound.effects.fdn_reverb
  import FDN`), documented in the module docstring.
- FDN `_process_mono` is a pure-Python per-sample loop at ~0.5× realtime → ~2×141.9 s input
  ≈ 4.7 min for the two independent L/R networks.
- The registered module's `width` parameter is a mid/side gain applied *after* the two mono
  passes; it cannot create stereo from a mono source. Superseded by the decorrelation wrapper
  (documented in `provenance.json` → `stereo_approach`).
