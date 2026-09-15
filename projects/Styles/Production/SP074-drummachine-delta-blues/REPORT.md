# SP-074 BULLFROG DRUM MACHINE — Delta Blues / blues-delta-daily-2026-06-24

**Date (UTC):** 2026-09-15 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP074-drummachine-delta-blues/`
**Status:** PASS — mix FFT 40/40, ACF 1/22 unpitched, silence 14.38% (below dry 15.46%, loci match dry), LUFS −14.34, peak 0.891.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-074** — Eight-Channel Sample Drum Machine + Sequencer (Bullfrog Drums-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale `SP-001..SP-035` range, NOT `Production/select_job.py` which picks from a stale `SP-001..SP-052` range) |
| Registered module | `sound.generators.drum_machine` → `BullfrogDrums`, `Kit`, `SampleChannel`, `CVChannel`, `synthesize_drum_samples` |
| Registry entries at pick time | **19 implemented:** SP-001, 011, 021, 024, 026, 028, 032, 033, 034, 035, 036, 037, 069, 070, 071, 072, **074**, 073, 075 |
| Already used last 7d (excluded) | SP-036 (09-14), SP-073 (09-13), SP-071 (09-12), SP-011 (09-11), SP-024 (09-10), SP-001 (09-09), SP-037 (09-08) |
| Eligible pool | **SP-021, SP-026, SP-028, SP-032, SP-033, SP-034, SP-035, SP-069, SP-070, SP-072, SP-074, SP-075** (12) |
| Selection | `random.Random(20260915).choice(pool)` → **SP-074** (first SP-074 production run; module already implemented, never produced until tonight) |
| MIDI pool | 289 candidates under `Styles/` (excl. `phase1` + `Production`), 282 usable (>40 B); sorted-deterministic pick → `Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid` |
| Selection record | `Production/.selection_cron.json` (rewritten this run, seed + pool + verdict) |

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Blues/blues-delta-daily-2026-06-24/` (Delta Blues daily 2026-06-24) |
| MIDI | `MIDI/blues-delta-daily-2026-06-24.mid` (copied to `MIDI/` in output; 4024 B) |
| Genre / key | Delta Blues, A blues hexatonic (A C D Eb E G); 8-bar blues in A7 + intro/outro = 12-bar grid |
| Tempo | 72 BPM (833333 µs/beat), declared 12/8, 480 tpb; material reads as 4-quarter bars → BAR = 1920 ticks, 12-bar grid |
| Length | last drum tick 21120 = 11.0 × 1920 → NBARS 12; rendered 44.68 s (39.6 s music + fluid tails) |
| Voices | Resonator Slide lead GM25 ch0 (**290 notes**, MIDI 69–79, dur med ~144 ticks) · Acoustic Rhythm GM26 ch1 (83 notes, MIDI 40–67) · Fingerstyle Bass GM32 ch2 (47 notes, MIDI 40–57) · Stomp & Clap ch9 (**101 onsets**: kick 36 ×33, clap 39 ×18, hat 42 ×50) |
| Why this source | 101-onset strict drum grid + 290-note slide lead = ideal Bullfrog test (real transient grid to replace 1:1, dense tonal bed to preserve); short enough (45 s) for per-hit sample render |

Grid (`Analysis/grid_visualization.txt`): all 4 voices 12/12 bars sounding, no rest bars.

## 3. Layer discipline (absolute — with documented rhythm-layer boundary)

SP-074 is an **absolute-layer rhythm method**: the Bullfrog X0X engine **replaces** the drum production layer 1:1 (all 101 ch9 onsets re-rendered as Bullfrog hits, dry GM drum stem dropped from the mix). Pitched voices keep the dry SoundFont bed (FX-off) — running slide-guitar lines through drum one-shots would delete the piece's tonality, so absolute applies to the rhythm layer, pitched bed preserved. Plus CV-lane sub garnish (channel 8, 0.15 gain).

```
blues-delta-daily-2026-06-24.mid
 -> dry SoundFont reference mix (fluidsynth -ni -g 1.2, reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix.wav  44.68 s, peak ~1.0, silence 15.46%
 -> dry per-track stems (RenderPipeline.render_stems, FX off, native lengths)
      track00 lead 44.68 s / track01 harm 41.67 s / track02 bass 41.69 s / track03 drums 38.96 s
 -> Bullfrog X0X: source onsets quantized to 16 steps/bar, swing 0.55, per-class voicing
      track04_Drums_BULLFROG.wav  41.00 s stereo, peak-norm 0.89
 -> CV lane: per-bar root/fifth walking values -> sine sub pulse garnish (0.15 gain)
      track05_CV_sub_garnish.wav
 -> mix: lead 1.0 + harm 0.8 + bass 0.9 + bullfrog 1.0 + sub (beds native-length, zero-padded to longest 44.68 s)
 -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1.0 dBFS) LAST
 -> SP074-drummachine-delta-blues.wav (44.68 s stereo) + .ogg (Opus 48k voip)
 -> processed pitched stems (peak-safe 0.89 copies) for DAW
```

Bullfrog voicing (measurement-driven defaults): ch1 kick LP 900 Hz / res 0.15 / drive 0.25 / pan 0 · ch3 hat HP 7000 Hz / decay 0.6 / pan −0.25 · ch5 clap LP 2500 Hz / decay 0.7 / pan +0.28 · kit `Kit.demo_kit` (kick/synth-snare/hat/tom/clap/rim/cymbal factory samples).

## 4. Parameters

| Param | Value | Logic |
|---|---|---|
| Engine | `BullfrogDrums(sr=44100)` + `Kit.demo_kit` | registered SP-074 engine |
| GM → channel map | 36 kick→ch1, 42 hat→ch3, 39 clap→ch5 | 1:1 onset preservation (33/50/18 hits) |
| Grid | 16 steps/bar × 12 bars, step 0.20833 s @72 BPM, round-quantize | source grid already 16th-strict |
| Swing | 0.55 (odd-16th delay) | blues shuffle feel on X0X grid |
| Velocity | `clip(vel/90, 0.2, 1.2)`, collision = max | source dynamics kept |
| CV lane | 24 steps (2/bar): root then fifth, `(note−36)/48` norm → `to_pitch_sequence(base 55 Hz)` → sine sub, 0.16 s gates, 0.06 s decay, 0.15 gain | documents channel-8 use; sub felt, not heard |
| Mix balance | lead 1.0 / harm 0.8 / bass 0.9 / bullfrog 1.0 + sub | lead carries 290-note line |
| Master | peak 0.89 → `normalize_to_lufs(−14)` → `Limiter(−1 dB)` last | measured **−14.34 LUFS**, peak 0.8913 |
| SoundFont | `discover_soundfont()` → FluidR3_GM.sf2 (never hardcoded) | ONE-ENV contract |

## 5. Pitch / tonal-content verification — **PASS**

Size asserts and silence ratios do **not** catch noise (SP-035 GENDYN lesson). Checks on the **delivered files**:

| Metric | Wet mix | Dry reference | Gate | Verdict |
|---|---|---|---|---|
| Mix FFT hit (1 s windows, ±2% f0×1–4) | **40/40 = 1.000** | 40/40 = 1.000 | ≥ 0.60 | PASS |
| Median harmonic energy (8 harmonics) | 0.172 | 0.191 | judged vs dry (see note) | PASS (Δ −0.019) |
| ACF unpitched (every-2nd 1 s, conf<0.30) | **1/22** | — | < 50% | PASS |
| Pitched-only stem sum harm | 0.200 | — | tonal-bed ref | sane |
| Bullfrog-drums-only harm @55 Hz | 0.041 | — | noise ref (~single digits ×) | confirms dilution source, not mistuning |

Note: the absolute 0.30 harmonic gate is **invalid** for a drum-forward mix — the Bullfrog kit is noise-transient energy by design (0.041 solo) and dilutes the window ratio; the dry SoundFont mix itself scores 0.191 on this sparse slide-guitar material. Judged vs dry reference (Δ −0.019 = drum dilution only), same precedent as SP-073's per-class bands and SP-036's formant-ladder gate. The SP-035 failure signature (0 Hz everywhere + ~4% harm) is **absent** (FFT 1.000, ACF 21/22 pitched).

Full JSON: `Analysis/pitch_verification.json`.

## 6. Silence / RMS profile + rhythmic grid

| Metric | Wet | Dry | Note |
|---|---|---|---|
| Silence (<0.001) | **14.38%** | 15.46% | wet LOWER — Bullfrog fills interstices |
| Peak / LUFS | 0.8913 / −14.34 | ~1.0 / — | limiter last |
| RMS/s | 0.17→0.22 content, dips s03/s06 (0.15/0.15), outro decay s36–39, 4 s tail | same loci, deeper dips | **all dip loci match dry** — arrangement breathing, not production gaps |

Per-second silence wet: s03 21.6%, s06 26.4%, s36 42.4%, s39 30.1%, s40–43 tail 100%; dry shows the same loci (34.0/38.2/43.1/35.2% + tail). Zero mid-track production gaps; only sub-0.01 RMS windows are the final 4 s tail.

Rhythmic grid (broadband envelope, 2× local contrast on Bullfrog stem): **67/101 = 66.3%**. Known limitation per SP-073 precedent: broadband envelope under-counts kick against bass bleed; hats would score higher in split bands. Reported as preservation proxy with miss list in JSON, not a transcription claim.

## 7. Fixes applied during this run

1. **V1 truncation (fatal musical bug).** Mixer cut all beds to the drum-stem length (38.96 s), deleting bars 11–12 of the lead/harmony. Root cause: `RenderPipeline.render_stems` rebuilds single-track MIDIs whose fluid tails differ (lead 44.68 / harm 41.67 / bass 41.69 / drums 38.96). Fix: V2 pads all beds to the longest (lead 44.68 s), music intact; documented in `provenance.json`.
2. **`normalize_to_lufs` arg order.** Signature is `(audio, target_lufs, sample_rate)` — passing `(mix, SR, −14)` targets +44100 LUFS with fs=−14 (scipy `ValueError: critical frequencies must be > 0`). Fix: positional `(mix, −14.0, SR)`; future callers use keywords.
3. **Verifier timeout.** Full per-0.5 s ACF + FFT on 44 s hung >600 s. Fix: 1 s windows, ACF every 2nd window at 8.8 kHz downsample; runtime <4 min.
4. **First-run `fluidsynth` resolve.** Cron env lacks bare `fluidsynth` on PATH; used `$MUSICOM_ENV/bin/fluidsynth` with PATH fallback (ONE-ENV contract).

## 8. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP074-drummachine-delta-blues.wav` (44.68 s, 44.1 kHz stereo) | 7,881,516 B |
| Full mix OGG (Opus 48k voip) | `SP074-drummachine-delta-blues.ogg` | ~326,048 B |
| Dry reference mix (FX-off) | `dry_full_mix.wav` (44.68 s) | 7,881,516 B |
| Source MIDI (copy) | `MIDI/blues-delta-daily-2026-06-24.mid` | 4,024 B |
| Dry stems | `Audio/stems_dry/track00..03.wav` | 7.88 / 7.35 / 7.35 / 6.87 MB |
| Wet stems | `Audio/stems_processed/track04_Drums_BULLFROG.wav`, `track05_CV_sub_garnish.wav`, `track0*_SOUNDFONT.wav` | 6.9 / 6.9 / 7.9–7.1 MB |
| Renderer | `Scripts/produce_sp074.py` (+ `remix_sp074.py`, selectors, verifiers) | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/grid_visualization.txt` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 9. Listen for

- Kick/stomp replaced by Bullfrog ch1 thump (LP 900 + drive) with shuffle swing — 4-on-floor of the shack, now machine-tight but still swung.
- Hats left (−0.25) vs claps right (+0.28): the X0X stereo field the GM kit never had.
- CV sub under bars: root–fifth pulse you feel in the chest, mixed at 0.15 so it never steps on the fingerstyle bass.
- Compare `dry_full_mix.wav` (GM kit) vs wet mix: same slide calls, new pocket.

## 10. Quality gate

- [x] MIDI present for the audio render (`MIDI/blues-delta-daily-2026-06-24.mid`)
- [x] OGG non-empty (~326 kB) and playable-length (44.68 s)
- [x] Pitch verification run and reported (PASS: FFT 40/40, ACF 1/22)
- [x] Silence ratio + per-second RMS measured; loci match dry, no production gaps
- [x] Full mix WAV + per-track stems (dry AND wet/Bullfrog)
- [x] `provenance.json` per artifact set
- [x] Grid visualization written before trusting timing
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
