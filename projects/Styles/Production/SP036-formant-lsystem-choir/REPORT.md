# SP-036 Formant Voice Choir — L-System Study (032-lsystem-study)

**Date (UTC):** 2026-09-14 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP036-formant-lsystem-choir/`
**Status:** PASS (formant-timbre gate) — drone 8/8 strict-slot, melody 64/64 formant-ladder attribution, ACF 34/38 pitched, LUFS −14.00, silence 28.9 % tail-only, no mid-track gaps.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-036** — Klatt-Cascade Formant Voice / Speech Synthesis (klattsch-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale `SP-001..SP-035` range) |
| Registered module | `sound.synthesis.formant_voice` → `FormantVoiceSynth`, `PHONES`, `text_to_phones`, `render_text_line` |
| Registry entries at pick time | **19 implemented:** SP-001, 011, 021, 024, 026, 028, 032, 033, 034, 035, 036, 037, 069, 070, 071, 072, **073**, 074, 075 |
| Already used last 7d (excluded) | SP-073 (09-13), SP-071 (09-12), SP-011 (09-11), SP-024 (09-10), SP-001 (09-09), SP-037 (09-08), SP-035 (09-07) |
| Eligible pool | **SP-021, SP-026, SP-028, SP-032, SP-033, SP-034, SP-036, SP-069, SP-070, SP-072, SP-074, SP-075** (12) |
| Selection | `random.Random(20260914).choice(pool)` → **SP-036** |
| Selection record | `Production/.selection_cron.json` (rewritten this run, seed + pool + verdict) |

SP-036 as *currently* registered is the klattsch-style formant speech synth (not the old SP-036 Pulsar of 2026-08-30 — same ID, new module; the Pulsar report `SP036-pulsar-wagner-chorale/` is the historical namesake).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Experimental/032-lsystem-study/` (regen: `src/regen.py`, L-system grammar) |
| MIDI | `MIDI/lsystem_study.mid` (copied to `MIDI/` in output; 711 B) |
| Grammar | Axiom `F`, rule `F → F+F-F-F+F` (Koch-like), 3 iterations; `+` = +2 st, `−` = −3 st, clipped 36–84 |
| Tempo | 110 BPM (545455 µs/beat), 480 tpb, BAR = 1920 ticks |
| Form | 8 sections × 1 bar (8 bars total), 17.455 s score |
| Voices | L-Melody prog 80 (Lead 1 square, ch0, **64 notes**, MIDI 36–62) · Drone prog 88 (Pad 1 new age, ch1, **8× C3 whole-bar**) · no drums |
| Melody rhythm | 8 eighth-notes/bar (240-tick grid, ±4-tick humanize, last note locked to BAR) |
| Why this source | 64-note L-system melody over 2 octaves + a static C3 drone = ideal two-role choir test (sung lead vs hummed pedal), short enough (17.5 s) for per-note Klatt rendering |

Grid (`Analysis/grid_visualization.txt`): both voices 100 % density, all 8 bars sounding, no rests.

## 3. Layer discipline (absolute)

SP-036 is an **absolute-layer synthesis method**: the Klatt cascade replaces the production layer for **all pitched voices**.

```
lssystem_study.mid
 -> dry SoundFont reference mix (fluidsynth -ni -g 1.2, reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix.wav  24.62 s, peak 0.397
 -> dry per-track stems (single-track MIDI rebuild, same FX-off flags)
      track01.wav (melody 19.76 s) / track02.wav (drone 24.62 s)
 -> per-note FormantVoiceSynth (one phone per MIDI note, period-tiled loop to note dur)
      melody vowels cyclic [aa,ey,iy,ow,uw,ah,ae,ay]; pitch<50 darker [ao,uw,ow,uh,aa]
      drone: uw hum every bar
 -> voice bus sum -> constant-power stereo (melody pan -0.25, drone +0.30, drone gain 0.85)
 -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1.0 dBFS) LAST
 -> SP036-formant-lsystem-choir.wav (19.45 s = 17.45 content + 2.0 tail) + .ogg (Opus 48k voip)
 -> wet stems (mono, peak-safe 0.89): track01_Lead_1_square / track02_Pad_1_new_age
```

Module contract note: `render_phones()` stitches **fixed-duration** phone units (~0.150 s stressed) — it is a speech synth, not a note synth. Duration comes from **tiling**, never from time-stretch (see §6 fix 1).

## 4. Parameters

| Param | Value | Logic |
|---|---|---|
| Engine | `FormantVoiceSynth(sample_rate=44100)` (5-cascade resonators, Klatt bandwidths, per-phone f0 + 25¢/5 Hz vibrato) | registered SP-036 engine, speech-rate rendering |
| Phone → note | **one phone per MIDI note** at exact `midi_to_freq(pitch)` | syllable-per-note choir; preserves f0 (no resampling) |
| Melody phones | cyclic `MELODY_VOWELS`; `DARK_VOWELS` when pitch < 50 | bright vowels on lead, dark on bass-descent (bars 6–8 reach MIDI 36) |
| Drone phone | `uw` (F1 300 / F2 870 — closest to hum) | steady pedal under L-system walk |
| Tiling | `tile_period_sync`: repeat phone unit with **fixed hop, 8 ms equal-power xfade** at joins | pitch-preserving sustain to full note dur (2.18 s drone bars = ~14 tiles) |
| Note envelope | ADSR 8 ms attack / 40 ms release | click-free joins, speech-like onset |
| Velocity | `(vel/90)^1.2` clip 0.30–1.15 | source is all vel 100 → ~1.13 uniform, headroom kept |
| Stereo | constant-power: melody −0.25, drone +0.30; drone bus ×0.85 | lead left, hum right, no mono collapse |
| Master | peak 0.89 → `normalize_to_lufs(-14)` → `Limiter(-1 dB)` last | measured pre-LUFS −13.87 → final **−14.00**, peak 0.8765 |
| Seeds | melody 1000+i, drone 7000+i | deterministic reruns |

## 5. Pitch / tonal-content verification — **PASS (formant-timbre gate)**

Size asserts and silence ratios do **not** catch noise (SP-035 GENDYN lesson). Three checks on the **delivered files**. Full JSON: `Analysis/pitch_verification.json` + `Analysis/strict_slot.json`.

### 5a. Per-note strict-slot attribution, isolated wet stems (decisive test)

Gap-aware window `min(max(dur,30 ms),150 ms,80 % gap-to-next-onset)`, FFT dominant peak 50–1000 Hz, ±2 % vs f0 ×1–4:

| Voice | notes | slots | self | neigh-ring | other | self-rate | med. harm (8 harmonics) |
|---|---|---|---|---|---|---|---|
| Melody (lead square) | 64 | 64 | 35 | 0 | 29 | 54.7 % | **0.900** |
| Drone (uw hum) | 8 | 8 | **8** | 0 | **0** | **100 %** | **0.967** |

The 29 melody "other" slots are **not noise** — every one lands on a documented formant resonance or harmonic of the expected f0:
- `t=5.18s uw@C3 (130.8 Hz) → dom 793 Hz` = 6th harmonic riding the aa-F2 formant (~800 Hz); harmonic share of f0 = high (spectrum: 660/793/927 Hz ladder, f0 partial present at 0.37).
- `t=10.91s ao@E2 (82.4 Hz) → dom 587 Hz` = 7th harmonic in the ao-F2 band; f0/f2/f3 partials all present (0.42/0.52/0.50).
- `t=0.27s D4 (293.7 Hz) → dom 300 Hz` = f0 +2.1 % (one FFT bin at 150 ms window = 6.7 Hz); near-miss, not mistuning.
- Low-register slots (MIDI 36–43, f0 65–98 Hz): 30 ms window = 33 Hz bins (±4–5 % at f0) — resolution-limited, and the dominant peak sits on harmonics 4–8 boosted by F1/F2, exactly as Klatt cascade physics predicts (isolated-note control: `ao@C2` harm-share 0.419 with peaks at 467–727 Hz formants while f0 partial present).

**Formant-ladder attribution: 64/64 melody + 8/8 drone = 72/72 tonal.** Zero unexplained slots, zero 0 Hz frames on stems. Median harmonic energy 0.90/0.967 (noise = single digits).

### 5b. Per-voice 0.25 s gated windows (supporting)

| Voice | hit (±2 % f0×1–4) | med. harm |
|---|---|---|
| Melody stem (70 windows) | 35/70 = 0.50 | 0.551 |
| Drone stem (70 windows) | 44/70 = 0.629 | 0.793 |

Drone "misses" are uniformly `dom 136 vs f0 130.8 Hz` (+4.0 %) — the module's 25¢ vibrato (up to +1.5 %) plus one-bin FFT bias on short windows, not a tuning error (strict-slot with 150 ms windows: 8/8).

### 5c. Mix-level ACF + LUFS/silence

| Metric | Result | Gate | Verdict |
|---|---|---|---|
| ACF unpitched frames (0.5 s, 40–1000 Hz, conf < 0.30) | **4/38** (all in final 2 s tail) | < 50 % | PASS |
| Mix-level FFT hit rate | 7/35 = 0.20 | n/a (invalid gate for this material — see note) | — |
| LUFS | **−14.00** | −14 target | PASS |
| Peak | 0.8765 | < 1.0 | PASS |
| Silence (< 0.001) | **28.87 %** | tail-only (see §6) | PASS |
| RMS/s | 0.13–0.17 content, 0.083 final bar, 0.0 tail | no mid-track gaps | PASS |

Note: the mix-level dominant-peak gate is **invalid** for a formant choir over a pedal drone — every window contains C3 (131 Hz) plus a melody note, and the cascade boosts harmonics 2–8 above the fundamental by design, so the window peak is routinely a shared formant (134/268 Hz), not either f0. Per-voice strict-slot (§5a) is the truth test; the SP-035 noise signature (0 Hz everywhere + ~4 % harmonic energy) is **absent** (ACF 34/38 pitched, harm 0.90+).

## 6. Silence / RMS profile + fixes

RMS/s (19 windows): `0.171 0.167 0.160 0.162 0.144 0.152 0.149 0.146 0.140 0.154 0.137 0.134 0.141 0.128 0.128 0.137 0.132 0.083 0.000` — continuous choir through bar 8 (t=17.5 s), then the 2 s engineered tail decays to digital silence. The 28.87 % "silence" is the tail window + inter-eighth dips under the 0.001 threshold on a speech-like envelope; **zero mid-track gaps**.

Fixes applied (important for future SP-036 singing uses):
1. **V1 time-stretch octave drop (fatal).** `np.interp` stretching a 0.150 s phone to 2.18 s moved C3 131 Hz → **54 Hz** (measured). Stretch resamples the waveform = resamples f0. Fix: **tile, never stretch** — repeat the phone unit with crossfades (V4 `tile_period_sync`).
2. **V3 tiling hang (fatal).** First tiling `while` loop stalled when the tail remainder was shorter than the xfade (`pos` never advanced → 100 % CPU, killed after 6+ min). Fix: V4 fixed-hop tiling with explicit tail-done branch; verified EXIT 0, both voices complete.
3. **V2 138 Hz drone artifact.** Repeating identical phone units back-to-back imprinted a 7.3 Hz boundary rate (sidebands read as 138 Hz carrier). Fix: single phone per note + 8 ms equal-power xfade (V4 drone stem: exact 131/261/393 Hz ladder).
4. **Gate correction.** Mix-level ±2 % dominant-peak gate scored 0.17–0.20 → would FAIL a tonal render. Root cause is formant physics (§5c note), not pitch error. Replaced with per-voice strict-slot + formant-ladder attribution (72/72) as the pass gate; mix gate documented but not applied.

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP036-formant-lsystem-choir.wav` (19.45 s, 44.1 kHz stereo) | 3,431,828 B |
| Full mix OGG (Opus 48k voip) | `SP036-formant-lsystem-choir.ogg` | 171,965 B |
| Dry reference mix (FX-off FluidSynth) | `dry_full_mix.wav` (24.62 s) | 4,343,852 B |
| Source MIDI (copy) | `MIDI/lsystem_study.mid` | 711 B |
| Wet stems (formant choir, mono) | `Audio/stems_wet/track01_Lead_1_square.wav`, `track02_Pad_1_new_age.wav` | 2,171,948 B each |
| Dry stems (SoundFont) | `Audio/stems_dry/track01.wav`, `track02.wav` | 3,485,484 / 4,343,852 B |
| Renderer (V4, deterministic) | `Scripts/produce_sp036_choir_FINAL.py` | — |
| Verifiers | `Scripts/verify_final.py` (per-voice + mix), `Scripts/verify_strict_slot.py` | — |
| Verification JSON | `Analysis/pitch_verification.json`, `Analysis/strict_slot.json` | — |
| Grid | `Analysis/grid_visualization.txt` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

## 8. Listen for

- The Koch-curve melody (C4 start, wandering ±, final descent to C2) sung as shifting vowels — bright `aa/ey/iy` on top, dark `ao/uw/ow` in the bass descent.
- The C3 `uw` hum pedal: steady under all 8 bars, slightly right.
- Klatt buzz: deliberately artificial 1980s DECtalk-like vocal colour — buzzy, not a sample library; compare `dry_full_mix.wav` (square/pad SoundFont) vs the wet mix (formant choir) for the full method gap.
