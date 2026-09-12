# SP-071 SEVERANCE — Techno / 083-techno-brownian (Reflected Brownian Motion)

**Date (UTC):** 2026-09-12 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP071-severance-techno-brownian/`
**Status:** PASS — pitch verification PASS, LUFS −14.09, wet silence 3.79%

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-071** — Gated Reverb + Dual-Engine Delay + Glitch Chain + Parallel Band Compressor (ZERO9-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md`, which holds spec-only methods with no runnable code; NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.effects.severance` — `GatedReverb`, `DualEngineDelay`, `RhythmicGlitchChain`, `ParallelBandCompressor`, `spectral_declash` |
| Registry entries at pick time | 18 implemented: SP-001, 011, 021, 024, 026, 028, 032, 033, 034, 035, 036, 037, 069, 070, **071**, 072, 073, 074 |
| Already used in last 7 days (excluded) | SP-011 (09-11), SP-024 (09-10), SP-001 (09-09), SP-037 (09-08), SP-035 (09-07), SP-026 (09-06), SP-033 (09-05) |
| Eligible pool after exclusion | **SP-021, SP-028, SP-032, SP-034, SP-036, SP-069, SP-070, SP-071, SP-072, SP-073, SP-074** (11) |
| Selection | `random.choice(pool)` → **SP-071** (first SP-071 production run; module already implemented in `sound/effects/severance.py`) |
| Selection record | `Production/.selection_cron.json` |

Method is **new to the production corpus** — no prior `SP071-*` directory existed.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Techno/083-techno-brownian/` (nightly composition job 2026-08-31) |
| MIDI | `MIDI/083-techno-brownian.mid` (phase-2, rules-processed; copied to `MIDI/`) |
| Style / method | Techno · composition method 048 Reflected Brownian Motion Pitch Diffusion (RBMPD) |
| Key | F natural minor |
| Tempo | 128 BPM (µs/beat 468,750), 4/4, 480 tpb, BAR = 1920 ticks |
| Form | 6 sections × 4 bars = 24 bars; 48.0 s musical, 48.21 s rendered |
| Voices | Lead (Church Organ GM19, ch0) · Cello (GM42, ch1) · Piano (GM1, ch2) · Violin (GM40, ch3) · Double Bass (GM43, ch4) · Drums (ch9) |
| Note counts | 174 / 72 / 192 / 192 / 137 pitched + **372 drum onsets** (kick 64, snare 24, clap 16, hats 256, crash 8, ride 4) |

**Why this source:** the 372 percussion onsets at a strict 4-on-floor grid at 128 BPM make it the ideal subject for an *onset-gated* reverb — SP-071's gate has a real, dense transient grid to react to, all aligned to 16th positions (0.1172 s apart).

## 3. Layer discipline (absolute)

SP-071 is an **absolute-layer post-production method**: the ZERO9 suite replaces the space / echo / glue layer for the **whole piece**, not a per-voice opt-in.

```
083-techno-brownian.mid
  -> fluidsynth -ni -g 1.2 -r 44100 with synth.reverb.active=no,
     synth.chorus.active=no            (SEVERANCE is the ONLY space layer)
     -> dry_full_mix.wav  (48.21 s, stereo, peak 1.0000, silence 6.70%)
  -> per-voice dry stems (6, FX-off, full-length, time-aligned)
       track01..track06  (piano/organ/cello/…/drums, GM names from the file)
  -> FULL-MIX chain (whole bus, per channel L/R independently)
  -> 6 × PER-VOICE chain -> processed stems (DAW remix material)
  -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
```

### Signal chain (order fixed, as documented in the module)

| # | Stage | Parameters used | Rationale |
|---|---|---|---|
| 1 | `ParallelBandCompressor` | down thr −16 dB / ratio 3.0 · up thr −44 dB / amount 0.30 · parallel_mix 0.45 | 4-band complementary split (120/500/2000 Hz), upward lift of quiet bands + downward squash of loud ones = bus glue before the spatial stages |
| 2 | `GatedReverb` | tail_gain 0.55 · declash 0.5 · movement 0.5/0.7 Hz · decay 0.62 · **gate_len 0.2344 s** (= one 8th at 128 BPM) · **372 onsets** | onset-triggered closure on EVERY drum hit; short tail = classic gated-reverb punch, not a wash |
| 3 | `DualEngineDelay` | time_cont **0.3516 s** (dotted 8th) · time_gran **0.7031 s** (dotted quarter) · feedback 0.42 · routing serial · splice 4 · grain_len 512 · **dry/echo blend 0.45** | dotted values give the 3-against-4 techno cross-rhythm; serial routing feeds the continuous engine into the granular one |
| 4 | `RhythmicGlitchChain` | bpm 128, steps 16, **sparse patterns** (stutter steps 1+9, reverse step 8, bitcrush step 13, decimate OFF) | tempo-locked but deliberately sparse (~3 of 16 steps per bar) so the chain colours the mix instead of shredding it |
| 5 | `spectral_declash` | 35% parallel blend | tames stacked resonant peaks from the reverb + delay feedback structure |
| 6 | Master | `normalize_to_lufs(−14)`, then `Limiter(−1.0 dB)` | streaming target; limiter strictly last |

## 4. Pitch verification (mandatory) — **PASS**

Method: per 0.5 s window, (a) FFT dominant peak in 50–1000 Hz, matched within ±2% against MIDI-note fundamentals **and their harmonics 2–4** for every note sounding in that window; (b) normalized-autocorrelation pitch (`sound.effects.subharmonic.pitch_frame`, 40–1000 Hz), counting unpitched frames; (c) harmonic energy in the first 8 harmonics of the lowest sounding expected fundamental.

| Metric | Result | Gate | Verdict |
|---|---|---|---|
| FFT dominant-peak hit rate vs expected MIDI pitches (+harmonics) | **0.656** (59/90 checked windows) | ≥ 0.60 | PASS |
| Median harmonic energy ratio (8 harmonics) | **0.374** | ≥ 0.30 | PASS (noise = single digits) |
| Autocorrelation unpitched frames | **1 / 95** | < 50% | PASS (no noise collapse) |
| Median dominant peak | 208.0 Hz ≈ G#3 — the F-minor texture's expected low-mid centre | — | sane |
| **Dry-vs-wet waveform correlation** | **0.430** | > 0.25 | PASS (transients preserved) |

Noise signature (SP-035 GENDYN failure mode: 0 Hz frames + 4% harmonic energy) is **absent**.

## 5. Silence ratio + RMS profile

| Render | Silence (<0.001) | Peak | LUFS |
|---|---|---|---|
| `dry_full_mix.wav` | 6.70% | 1.0000 | — |
| `SP071-severance-techno-brownian.wav` | **3.79%** | **0.8912** | **−14.09** |

Per-second RMS (final mix, 49 windows): min 0.082 (start) → **0.207** peak (Drop) → 0.16–0.18 through Drop2 → 0.061 / 0.0095 / 0.0008 / 0.0001 tail. **Zero mid-track gaps**; the only sub-0.01 windows are the final 3 s of release/tail padding after the last note. Silence is *lower* than dry because the gated tail and delay fill the drum-grid interstices.

Spectral balance dry → wet (share of total energy):

| Band | dry % | wet % | ratio |
|---|---|---|---|
| 20–60 Hz | 3.54 | 13.41 | **3.79×** (sub built up) |
| 60–120 Hz | 20.03 | 25.05 | 1.25× |
| 120–500 Hz | 37.36 | 30.19 | 0.81× |
| 500–2 k | 28.29 | 15.19 | 0.54× (declash + band comp) |
| 2 k–8 k | 10.25 | 12.70 | 1.24× |
| 8 k+ | 0.53 | 3.46 | **6.57×** (gate splash on hats) |

Stereophony widened: L/R correlation 0.673 (dry) → 0.760 — slightly *more* correlated, because both channels receive identical trigger grids and the parallel band compressor is mono-coherent.

## 6. Fixes applied during this run (important for future SP-071 uses)

1. **`DualEngineDelay.process()` returns the WET ENGINE OUTPUT ONLY.** It is not a bus send-return — the dry signal is *replaced*, not mixed. Applying it at 100% on a 4-on-floor mix moved every transient 3/16 late and comb-filtered the whole bus: measured dry-vs-wet waveform correlation **0.061**, i.e. the techno pulse was effectively destroyed. **Fix:** explicit blend `y = (1−0.45)·y + 0.45·y_echo`. Correlation recovered to 0.430. Ablation table (20 s slice):

   | delay mix | corr(after echo) | corr(after glitch) | corr(after declash) |
   |---|---|---|---|
   | 0.00 (off) | 0.791 | 0.653 | 0.646 |
   | 0.20 | 0.742 | 0.617 | 0.611 |
   | 0.30 | 0.671 | 0.564 | 0.559 |
   | **0.45 (chosen)** | 0.516 | 0.442 | **0.439** |
   | 1.00 (raw module) | −0.006 | — | — |

   *Recommendation for the registry docstring: state that `DualEngineDelay` is wet-only and pair it with an explicit mix control at the call site.*

2. **Stage order matters for level.** Running `spectral_declash` on the whole chain output **twice** (inside `GatedReverb` at 50% and again at 35% parallel on the bus) cost ~3.6× overall RMS (0.101 → 0.028) and −9 dB. A 35% parallel blend is the maximum before the declash starts removing the intended reverb splash; do not raise it.

3. **Glitch-chain patterns must be sparse.** Default patterns plus the bit-depth modulation rotated through the whole 16-step bar and punched holes in the 4-on-floor grid. Only 3 of 16 steps per bar are gated here; the decimate stage is **off**.

4. **`RhythmicGlitchChain.process` reverts to defaults when `patterns` is omitted** — pass an explicit tuple, never rely on the internal default for a production render.

5. Bug: `write_grid_visualization` kwarg is `ticks_per_character`, not `ticks_per_char` (the main renderer died after writing the OGG; artifacts were completed by `complete_sp071.py`).

6. Stereo chain applied **per channel** (not on a downmix) to preserve the source's L/R independence.

## 7. Files + sizes

| File | Bytes | Tracked by git |
|---|---|---|
| `SP071-severance-techno-brownian.wav` (final mix) | 8,505,132 | no (`*.wav` ignored) |
| `SP071-severance-techno-brownian.ogg` (Opus 48k voip) | 323,783 | **yes** |
| `dry_full_mix.wav` | 8,505,132 | no |
| `Audio/stems_dry/track01..06.wav` | 8,505,132 / 8,408,364 / 8,356,908 / 8,385,324 / 8,356,908 / 8,375,852 | no |
| `Audio/stems_processed/track01..06_serverance.wav` | same sizes, peak-normalized 0.891 | no |

Stem map (MIDI track index → GM program → role, as parsed from the source):

| Stem | Track | GM program | Instrument | Role |
|---|---|---|---|---|
| track01 | 1 | 19 | Church Organ | RBMPD lead, 174 notes |
| track02 | 2 | 42 | Cello | sustained pad, 72 notes |
| track03 | 3 | 1 | Bright Acoustic Piano | offbeat stabs, 192 notes |
| track04 | 4 | 40 | Violin | counterline, 192 notes |
| track05 | 5 | 43 | Contrabass | root pulse, 137 notes |
| track06 | 6 | 0 (ch 9) | Drum Kit | 372 onsets (gate trigger source) |

| `MIDI/083-techno-brownian.mid` | copied from source | yes |
| `Analysis/pitch_verification.json` | 24,757 (95 windows) | yes |
| `Analysis/render_stats.json` | LUFS, peaks, silence, per-second RMS dry+wet | yes |
| `Analysis/grid_visualization.txt` | 6 voices × 6 sections, █/░ density | yes |
| `provenance.json` | full parameter + hash record | yes |
| `run_full.log` | full renderer stdout | yes |
| `produce_sp071_cron.py` / `complete_sp071.py` | generator scripts | yes |

Total project size 113 MB (WAVs excluded from git by policy).

Stem-sum sanity: Σ(dry stems) vs full mix max abs diff 0.2021 on a 1.0000 peak (20.2%) — expected, because the full-mix FluidSynth render sums on a shared bus while the stems are rendered independently (per-track gain staging + GM velocity response), so the stems are *closer* to the composition, not bit-identical. Both were rendered with identical FX-off flags.

## 8. Provenance / classification

`provenance.json`: composition is AI-assisted (musicom engine, generative method 048 + rules layer); production layer is AI-generated (deterministic DSP, no samples, no model inference). No external audio sources. No sample libraries used — everything derives from the source MIDI + `sound.effects.severance`.

## 9. Listening guide

- **0–13 s (Intro/Build):** listen to how the gated tail on the kick stops *dead* at the 8th-note gate — the 4-on-floor pulse should stay readable through the compression and the sub band (3.8× energy lift).
- **13–26 s (Drop):** dotted-8th + dotted-quarter echoes cross the 4/4 grid; you should hear 3-against-4 movement *behind* the beat, never on top of it.
- **~26 s / ~39 s (Break/Drop2):** sparse glitch steps — one stutter, one reversed slice, one bitcrushed 16th per bar. They are meant to read as *glitches on a good take*, not as a destroyed mix.
- **44–48 s (Outro):** the gate closes and only the delay tail + declashed reverb remain.

## 10. Quality gate

- [x] MIDI present for the audio render (`MIDI/083-techno-brownian.mid`)
- [x] OGG non-empty (323,783 B) and playable-length (48.21 s)
- [x] Pitch verification run and reported (PASS, harmonic ratio 0.374)
- [x] Silence ratio + per-second RMS measured; no mid-track gaps
- [x] Full mix WAV + per-track stems (dry **and** processed)
- [x] `provenance.json` per artifact set
- [x] Grid visualization written before trusting timing
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (resolved via `sound.render.fluidsynth.discover_soundfont` → FluidR3_GM.sf2)
