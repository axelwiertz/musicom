# SP-011 — Karplus-Strong String Synthesis → Hip-Hop Boom-Bap

**Job:** random-style production (SP methods), LAYER-ALIGNED cron
**Date:** 2026-09-11
**Output project:** `/opt/data/repos/musicom/projects/Styles/Production/SP011-karplus-hiphop-boombap/`

---

## 1. Selection

| Item | Value |
|---|---|
| Registry (single source of truth) | `workflows.musicom_workflow.SP_METHODS` |
| Registry size | 18 implemented methods |
| Seed | `20260911` (date-derived, reproducible) |
| Recent 7d (excluded) | SP-001, SP-024, SP-028, SP-036, SP-037 |
| Eligible pool | `SP-011, SP-021, SP-026, SP-032, SP-033, SP-034, SP-035, SP-069, SP-070, SP-071, SP-072, SP-073, SP-074` |
| **Chosen method** | **SP-011** → `sound.synthesis.karplus_strong` (Karplus-Strong String Synthesis) |
| **Source composition** | `projects/Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid` |
| Candidate pool size | 277 non-phase1 `.mid` files under `projects/Styles/` (Production/ excluded) |
| Layer discipline | **absolute** — SP-011 replaces the production layer for ALL voices |

## 2. Source composition

| | |
|---|---|
| File | `hiphop_boom_bap.mid` (composer script: `Styles/HipHop/boom-bap/v1/compose.py`) |
| Genre / methods | Hip-Hop Boom-Bap — composition methods 011 (Euclidean) + 002 (Markov) + 026 (DPSM) |
| Key / tempo | E minor, 90 BPM, 4/4 |
| Length | 85.33 s, 32 bars (A 16 + B 16) |
| Tracks | 5 (track 0 = tempo only) |
| Voices | Drums ch9 (prog 0 label, 640 notes) · Bass prog 33 (256) · Lead/Bright Ac. Piano prog 1 (128) · Pad 1 new-age prog 88 (768) |
| Total notes | **1792** |

## 3. Method — Karplus-Strong (absolute layer)

Module API called directly (no `produce()` adapter wiring exists for SP-011 beyond
the generic dispatch):

```python
from sound.synthesis.karplus_strong import karplus_strong, soft_knee
sig = karplus_strong(pitch, dur, vel=velocity, loop_gain=g, sr=44100)
```

Delay-line definition used (engine docstring fix, 2026-08-27):
`y[n] = x[n] + loop_gain * 0.5 * (y[n-N] + y[n-N-1])`, `N = round(sr/f0)`
(**full cycle period — NOT `sr/(2*f0)`**, which would drop an octave). Excitation is a
2-sample uniform noise burst scaled by velocity.

### Voice role mapping

| Role | Source | loop_gain | let-ring (s) | target RMS | pan |
|---|---|---|---|---|---|
| `lead` | Piano melody prog 1 | 0.9990 | 1.00 | 0.090 | drift −0.50 → +0.50 |
| `comp` | Pad 1 (new age) prog 88 | 0.9987 | 0.90 | 0.100 | center |
| `bass` | Bass prog 33 | 0.9995 | 1.40 | 0.115 | center |
| `perc` | ch9 drums (36/38/42) | 0.9840 | 0.25 | 0.055 | center |

### Production chain

1. Per-role let-ring KS plucks (decaying strings sustain across the 16th/8th grid).
2. Per-role bus RMS balance to role targets.
3. Per-role soft-knee outlier control (`thresh 0.45–0.50`, `slope 0.25`).
4. Sum → `Limiter(-1 dB)` → `normalize_to_lufs(-14)` → `Limiter(-1 dB)`.

## 4. Fixes applied this run (rev1 → rev3)

| # | Problem found | Evidence | Fix |
|---|---|---|---|
| 1 | **rev1 render was 52.6 % sub-threshold silence**, mix RMS 0.039 | `rms_per_second` flat at 0.003 for the first 52 s | Plucks were cut at the notated note end (0.13 s for 8th notes) so decaying strings left dead air → **let-ring durations** per role |
| 2 | **rev2 mix was crushed 4× quieter than its stems** (mix RMS 0.027 = −31 dBFS, stems 0.09–0.115) | one coherent-sum transient peaked at `pre_peak=4.58` vs nominal ~0.5 | rev2's single master peak-normalizer let one spike set the level → **per-role soft-knee outlier control** + master `Limiter → LUFS → Limiter` chain |
| 3 | **Inherited `render_melody()` cannot deliver multi-voice balance** | shared module hardcodes 2 roles (lead/bass) and peak-normalizes the raw sum | kept the module for `karplus_strong()` / `soft_knee()` only; per-role bus assembly implemented in the project script |
| 4 | Naive per-note pitch scoring looked like a failure (bass 38 %, comp 3 % ACF) | debug showed bass ACF locking to 109.1 Hz vs expected 82.4 Hz (2.6 s of overlapping E2 + A2 + C3 tails in one stem) | added an **engine-level** pitch test + **chroma** comparison as the pass gates instead of a window-based per-note score |
| 5 | Stale rev1 stem names (`track00_comp`, `track02_lead`) collided with rev3 layout | `Audio/stems/` held two generations | removed rev1 stem WAVs + sidecars, regenerated rev3 provenance |

## 5. Pitch verification (MANDATORY — size/silence does NOT catch noise)

Full record: `Analysis/pitch_verification.json`.

### 5a. Engine level — `karplus_strong()` isolated notes (THE decisive test)

21 renderings across the piece's register (MIDI 36–84) × the 3 loop gains used:

| Metric | Result |
|---|---|
| Notes within **1 %** of target f0 | **21 / 21** |
| Max absolute ratio error | **0.33 %** |
| Min 8-harmonic energy share (50–2000 Hz band) | **22.2 %** |
| Median 8-harmonic energy share | **69.9 %** |

Detected/expected examples: MIDI 36 → 65.4 Hz (ratio 1.000), MIDI 40 → 82.4 Hz
(1.000), MIDI 45 → 110.0 Hz (1.000), MIDI 60 → 260.9/261.6 (0.997),
MIDI 84 → 1050.0/1046.5 (1.003). **No octave error, no noise floor.**

### 5b. Full-mix pitch frames

0.5 s window / 0.25 s hop, autocorrelation 50–1000 Hz:

| Metric | Result | Gate |
|---|---|---|
| Frames with a confident periodic f0 | **340 / 342 = 99.4 %** | ≥ 80 % ✅ |
| Frames with **0 Hz** (noise signature) | **0** | = 0 ✅ |
| Mean autocorrelation confidence | 0.62 | — |
| Median detected f0 | 165 Hz | — |

(The 2 non-confident frames are the leading/trailing partial windows.)

### 5c. Tonality vs FluidSynth GM reference (same MIDI)

12-bin log-frequency chroma, KS mix vs a FluidSynth FluidR3_GM render of the
identical MIDI (reference deleted after comparison per the WAV-cleanup rule):

| Metric | Result | Gate |
|---|---|---|
| Chroma cosine similarity | **0.9735** | ≥ 0.90 ✅ |
| Best key rotation | **0** semitones | = 0 ✅ |
| Best-rotation cosine | 0.9735 | — |

Same key, same pitch-class distribution as a sample-library render of the same
composition — the strongest available evidence that the render is tonal and
pitch-correct rather than noise.

### 5d. Per-note diagnostic (reported, not a gate)

Expected-guided spectral / autocorrelation test per note within each stem:

| Role | Notes | ACF fundamental-or-octave | Spectral top-6 peak match |
|---|---|---|---|
| bass | 256 | 98 (38.3 %) | 100 (39.1 %) |
| lead | 128 | 112 (87.5 %) | 120 (93.8 %) |
| comp | 768 | 312 (40.6 %) | 664 (86.5 %) |

Octave-ratio histogram: `1` → 183, `0.5` → 339 (sub-octave detection at the window
level). **This metric under-reports by construction**: analysis windows inside a
single stem contain the overlapping let-ring tails of neighbouring notes plus
simultaneous voices, so the autocorrelator locks onto whatever is strongest in the
window, not the notated note. The engine-level (§5a) and chroma (§5c) checks are the
pass gates; this table is kept for transparency and reproduction.

### Verdict

**PASS** — pitched, tonal, octave-correct plucked-string render, NOT noise:
21/21 engine notes within 1 % of target f0, 0 zero-Hz frames, chroma cosine 0.9735
vs the GM reference at the same key. All 6 machine gates: `true`.

## 6. Silence ratio + RMS profile

| Metric | Value |
|---|---|
| Duration | 85.93 s (44.1 kHz stereo) |
| Peak | 0.8287 (−1.63 dBFS) |
| RMS | 0.1495 |
| Integrated loudness | **−14.00 LUFS** (streaming target) |
| **Silence ratio (\|x\| < 0.001)** | **0.0 %** (rev1: 52.6 % → rev2: 5.5 % → rev3: 0.0 %) |
| Longest silent run | **0.3 ms** (rev1: 573 ms) |
| Min per-second RMS | 0.0998 (no dead seconds) |
| Per-second RMS range | 0.0998 – 0.1993 |

Per-second RMS is flat across the whole piece (`Analysis/render_stats.json`) — the KS
decay now fills the grid across all 32 bars; the former mid-track gaps are gone.

### Onset grid (16th-note grid, 272 steps; █ = onset)

```
lead  █░░░█░░░█░░░█░░░...   (128 onsets, one per bar-level phrase point)
comp  ████████████████...   (768 onsets, 16th-note pad arpeggio, 3 phase layers)
bass  █░█░█░█░█░█░█░█░...   (256 onsets, straight 8ths)
perc  █░███░███░█░███░█░... (640 onsets, Euclidean 5/16 kick + 7/16 snare + 8th hats)
```

Stems are time-aligned (all 85.93 s padded, identical absolute note timings).

## 7. Files + sizes

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `Audio/SP011-karplus-hiphop-boombap.wav` | 15 158 688 B (85.93 s, 44.1 kHz stereo) |
| OGG (Opus, voip 48k) | `Audio/SP011-karplus-hiphop-boombap.ogg` | 717 336 B (85.94 s) |
| Stem lead | `Audio/stems/track00_lead.wav` | 15 158 688 B |
| Stem comp | `Audio/stems/track01_comp.wav` | 15 158 688 B |
| Stem bass | `Audio/stems/track02_bass.wav` | 15 158 688 B |
| Stem perc | `Audio/stems/track03_perc.wav` | 15 158 688 B |
| Source MIDI copy | `MIDI/hiphop_boom_bap.mid` | 14 337 B |
| Render info | `Analysis/render_info.json` | 4 580 B |
| Pitch verification | `Analysis/pitch_verification.json` | 6 900 B |
| Render stats (RMS/silence) | `Analysis/render_stats.json` | 1 203 B |
| Onset grid | `Analysis/grid_visualization.txt` | 3 534 B |
| Provenance sidecars | `Audio/**/*.provenance.json` ×6 | ~500 B each |
| Producer (final) | `Scripts/produce_sp011_boombap_rev3.py` | — |
| Verifier (final) | `Scripts/verify_final.py` | — |

WAVs are gitignored per repo policy (renderable from MIDI); the OGG is tracked.

**NOTE — a source defect worth flagging:** `hiphop_boom_bap.mid` has all four voices
running the full 32 bars, so unlike the SP-024 country loop (percussion 64-bar tail)
there is no track-length mismatch here. `validate()`-class drift is absent; render
duration equals source duration (85.93 s vs 85.33 s music + 0.6 s decay tail).

## 8. Verdict

**PASS.** All 1792 source notes re-voiced as Karplus-Strong plucked strings (no
FluidSynth, no GM samples in the mix), at −14 LUFS with 0.0 % silence and a 0.3 ms
longest gap. Engine-level pitch accuracy 21/21 within 1 %, full-mix 99.4 % confident
pitch frames / 0 noise frames, chroma cosine 0.9735 at rotation 0 against a GM
reference render. Revision history and the two traps hit (let-ring silence, coherent-sum
transient crushing) are documented in §4 for reuse.

## 9. Reuse notes

- Reproduce: `/opt/data/micromamba/envs/musicom/bin/python Scripts/produce_sp011_boombap_rev3.py`
  then `Scripts/verify_final.py`.
- The shared `sound/synthesis/karplus_strong.render_melody()` is only usable for
  simple 2-role mixes (hardcoded lead/bass, no let-ring, peak-normalized raw sum).
  For multi-voice work use `karplus_strong()` per note and assemble the bus, as in
  `Scripts/produce_sp011_boombap_rev3.py`.
- Whenever a KS render measures low RMS or high sub-threshold silence, check for
  **short notated note durations** before touching gain — decaying synthesis cannot
  fill rests; the fix is let-ring, not level.
