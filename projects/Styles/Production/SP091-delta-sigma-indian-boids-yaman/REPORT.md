# SP-091 DELTA-SIGMA CONVERTER SATURATION — 212-indian-boids-yaman

**Date (UTC):** 2026-10-06 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP091-delta-sigma-indian-boids-yaman/`
**Status:** PASS — pitch hit-rate 0.9676, harmonic energy 0.3888, silence 0.17%, LUFS -14.00, peak 0.1951, mono correlation 0.979.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-091** — Physics-Based Delta-Sigma Converter Saturation & Circuit Strain (Mixland Grey Matter-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.effects.delta_sigma_saturator` → `DeltaSigmaSaturator`, `DeltaSigmaStage`, `SlewLimiter`, `ReconstructionFilter` |
| Registry entries at pick time | **40 implemented** (SP-001 … SP-100) |
| Already used last 7d (excluded) | SP-021, SP-072, SP-075, SP-079, SP-080, SP-081, SP-083, SP-086 |
| Eligible pool | **32 implemented methods** |
| Selection | `random` (unseeded, true-random this run) → **SP-091** (first SP-091 production run in current cycle) |
| MIDI pool | All `.mid` outside `Production/`, preferring non-`phase1`; random pick → `Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid` |
| Selection record | `Analysis/select_20261006.json` + `provenance.json` + `../.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/IndianClassical/212-indian-boids-yaman/` — Yaman raga melody driven by a boids flocking algorithm |
| MIDI | `212-indian-boids-yaman.mid` (copied to output `MIDI/`; 7,847 B) |
| Tempo / grid | 90 BPM (666,667 µs/beat), tpb 480; 85.33 s, 128 beats = 32 bars (4/4) |
| Tonality | **Yaman raga in C = C Lydian** — pitch classes {0,2,4,6,7,9,11}; raised 4th (F♯) is the Yaman signature |
| Voices (stems) | `track00_Church_Organ` (GM 19, drone C–G, all 32 bars) · `track01_Sitar` (GM 104, melody, all 32 bars) · `track02_Recorder` (GM 74, counterline, bars 4–23) · `track03_Drums` (ch9 tabla/perc, bars 4–31) |
| Texture | Meditative Hindustani drone + sitar/reed melody + tabla entering after the 4-bar alaap |

Grid (`Analysis/grid_visualization.txt`): 4 voices × 32 bars. Organ drone + sitar run the whole piece; recorder and tabla enter at bar 4.

---

## 3. Layer Discipline (Absolute)

SP-091 is an **absolute-layer saturation method**: one `DeltaSigmaSaturator` applied to the whole mix — no per-voice parameterization. It emulates a 1990s console DAC pushed past nominal spec: 2nd-order delta-sigma loop with integrator leak and soft-clip, thermal DC drift + component strain, slew-rate limiting, analog reconstruction lowpass, and asymmetric DAC-ladder soft clipping.

```
212-indian-boids-yaman.mid
 -> dry reference: fluidsynth -ni -g 1.2 -R 0 -C 0 -F (FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (16.32 MB)
 -> dry stems (RenderPipeline.render_stems, FX off):
      track00_Church_Organ / track01_Sitar / track02_Recorder / track03_Drums
 -> SP-091 DeltaSigmaSaturator(mode=console, drive_db=4.0, strain=0.28, mix=1.0)
      applied to the full mix (absolute layer, single pass)
 -> normalize_to_lufs(-14.0) -> Limiter(-1.0 dBFS) LAST
 -> SP091-delta-sigma-indian-boids-yaman.wav + .ogg (Opus 48k voip)
```

**Parameters:**

| Param | Value | Rationale |
|---|---|---|
| mode | `console` | Warm vintage-DAC compression; `broken` would shatter the meditative drone |
| drive_db | 4.0 | Gentle input gain push into the delta-sigma loop |
| strain | 0.28 | Mild component strain — audible warm compression, no chaotic foldback |
| mix | 1.0 | Fully-wet saturation (the effect IS the method) |
| fs | 44100 | Matches FluidSynth render |

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on delivered wet mix (Yaman in C = Lydian, PCS {0,2,4,6,7,9,11}):

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| FFT hit rate (0.5 s windows, 50–1000 Hz, ±0.45 semitone, in-scale) | **179/185 = 0.9676** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fundamental) | **0.3888** | ≥ 0.25 | PASS |
| Valid pitched windows | **185 / 190 (97.4%)** | > 50% | PASS |
| Dominant pitch range | 50–1000 Hz (C2 drone ~65 Hz to sitar/flute upper register) | — | Aligned |
| Median dominant freq | 492 Hz region | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Delta-sigma saturation preserves pitch integrity fully — Yaman's raised 4th (F♯) survives the nonlinear loop intact.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **0.17%** | Near-continuous — organ drone + tabla keep energy flowing; no mid-track gaps |
| Peak / LUFS | **0.1951 / -14.00 LUFS** | Limiter(-1 dBFS) ceiling enforced; low peak = high crest-factor compression (delta-sigma hallmark) |
| RMS (mono) | **0.1464** | Continuous dense signal, ~2.5 dB crest factor — consistent with heavy saturation |
| Mono correlation | **0.979** | Effectively mono (GM source); no stereo artifacts introduced |

Low peak + sustained RMS is the expected signature of a delta-sigma saturation pass over a drone-heavy source: the loop compresses dynamics toward a dense, warm wall while keeping the drone's tonal center locked.

---

## 6. Fixes & Discoveries During Run

1. **numpy float32 JSON crash**: first run wrote WAV/OGG/stems successfully but crashed writing `render_stats.json` — `json.dumps` rejects `np.float32`. Fixed with explicit `float()`/`int()` casts in a follow-up `finish_sp091_cron.py` that recomputes stats from the already-written WAV (no re-render needed).
2. **Stem label quirk confirmed**: `RenderPipeline.render_stems` labels GM 74 as `track02_Recorder` (not "Flute") and GM 19 as `track00_Church_Organ` — matched to the known per-voice label table; no wrong DSP routing.
3. **Track-index vs channel mismatch in grid**: first grid pass keyed tracks by `mido` track index (track 0 = conductor/tempo meta) and showed the organ as empty; corrected to key by `program_change`, revealing the correct 4-voice structure.

---

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `SP091-delta-sigma-indian-boids-yaman.wav` | 16,321,068 B |
| Master OGG | `SP091-delta-sigma-indian-boids-yaman.ogg` | 524,266 B |
| Dry Reference | `dry_full_mix_sp001_reference.wav` | 16,321,068 B |
| Source MIDI | `MIDI/212-indian-boids-yaman.mid` | 7,847 B |
| Dry Stems | `Audio/stems_dry/` (4 stems: Church_Organ, Sitar, Recorder, Drums) | ~16 MB total |
| Script | `Scripts/produce_sp091_cron.py` + `finish_sp091_cron.py` + `gen_grid_sp091.py` | — |
| Grid | `Analysis/grid_visualization.txt` | — |
| Stats | `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/select_20261006.json` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

---

## Verdict

**PASS.** SP-091 delta-sigma converter saturation applied as an absolute layer to the 212-indian-boids-yaman Yaman-rage composition. Tonal content fully preserved (pitch hit-rate 0.9676, harmonic energy 0.3888), continuous musical flow (0.17% silence), loudness normalized to -14 LUFS with -1 dBFS limiter ceiling. The warm DAC-stage compression suits the meditative drone; `broken` mode would be the next variable if a harsher, foldback-laden treatment is desired.
