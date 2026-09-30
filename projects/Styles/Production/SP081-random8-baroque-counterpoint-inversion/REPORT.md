# SP-081 RANDOM8 (8-channel quantized random CV) — 004-baroque-counterpoint-inversion

**Date (UTC):** 2026-09-28 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP081-random8-baroque-counterpoint-inversion/`
**Status:** PASS — dry-wet pitch fidelity 8/9 (0.889), harmonic energy 0.7028, ACF unpitched 0/3, silence 37.16% (tail), LUFS -14.38, peak 0.8913.
**Post-run fix (2026-09-30):** `write_wav` int16 truncation bug — delivered WAV/OGG were
silently zeroed (float→int16 cast without ×32767). Patched + re-rendered + verified from disk.
See §6 item 4. All metrics below are unchanged (deterministic seed) and now backed by an audible file.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-081** — 8-Channel Quantized Random CV Source (Befaco/Mylar Melodies RANDOM8-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.modular.random8` → `Random8`, `RandomChannel`, `SCALES_15`, `STYLES`, `quantize_cv` |
| Registry entries at pick time | **35 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092, 094, 095 |
| Already used last 7d (excluded) | SP-070 (09-27), SP-024 (09-26), SP-032 (09-25), SP-011 (09-24), SP-069 (09-23), SP-090 (09-22), SP-033 (09-21) |
| Baseline excluded | SP-001 (FluidSynth reference, always available) |
| Eligible pool | **27 implemented methods** |
| Selection | `random.seed(20260928); random.choice(sorted(pool))` → **SP-081** (first SP-081 production run in current cycle) |
| MIDI pool | 307 candidates under `Styles/` (excl. `Production/` + `phase1`); deterministic seeded pick → `Styles/Baroque/004-baroque-counterpoint-inversion/midi/004_counterpoint_study.mid` |

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Baroque/004-baroque-counterpoint-inversion/` (Bach-inspired subject + mirror inversion, `src/counterpoint_gen.py`) |
| MIDI | `004_counterpoint_study.mid` (228 B; copied to output `MIDI/`) |
| Content | C-minor subject (C4 D4 Eb4 B3 C4 G3 Ab3 G3) + interval inversion around C4 (C4 Bb3 B3 C#4 C4 F4 E4 F4) |
| Tempo / grid | 120 BPM (500000 µs/beat), tpb 10080; 80640 ticks = 8 beats = **4.0 s musical** (6.91 s incl. FluidSynth tail) |
| Voices | 2 × Acoustic Grand Piano (GM program 0, channel 0 — no program_change in the legacy export) |
| Texture | 2-voice baroque counterpoint study, 16 note-ons |

**Source discovery (legacy export bug):** the pre-reorg music21 writer
(`counterpoint_gen.py`, `unit_to_music21` with `part.insert(event.start_tick, n)`)
misplaces note-offs — the first subject note (C4, tick 0) is never released until
~4 beats in, so it reads as a sustained C4 drone under the moving counterpoint.
This is a property of the *source* MIDI, not the production pass; the SP-081
modulation layer is applied faithfully to whatever the source renders.

## 3. Layer Discipline (Absolute)

SP-081 is a **control-voltage SOURCE, not an audio renderer**. Its musical
identity is eight channels of *controllable, quantised-after-attenuation* random
voltage. As an **absolute-layer** production method, ONE `Random8` instance's
8 CV channels drive a single global modulation matrix across the WHOLE mix
(per-voice/per-track application is a later refinement).

```
004_counterpoint_study.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (1.22 MB)
 -> dry stems (2 voices, same reverb/chorus-off settings):
      track00_Acoustic_Grand_Piano / track01_Acoustic_Grand_Piano
 -> Random8 (seed 20260928, n_trigs=16 = eighth-note grid over 4.0 s) -> 8 CV streams
 -> absolute-layer modulation matrix (see table):
      LPF(ch0/ch6) -> HPF(ch4) -> pan/width(ch1/ch5) -> gain(ch2)
      -> reverb-wet crossfade(ch3) -> trim(ch7)
 -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
 -> SP081-random8-baroque-counterpoint-inversion.wav + .ogg (Opus 48k voip)
```

### Random8 channel matrix

| ch | style | scale | extra | → destination | mapping |
|---|---|---|---|---|---|
| 0 | drift | dorian | slide 0.35 | LPF cutoff | 500→9000 Hz (log) |
| 1 | uniform | major | dividr 2 | stereo pan | −1→+1 (constant power) |
| 2 | steps | unquantised | prob 0.8 | gain tremolo | 0.70→1.0 |
| 3 | bell | natural_minor | slide 0.3 | reverb wet | 0.06→0.36 (dry/wet crossfade) |
| 4 | drift | mixolydian | slide 0.5 | HPF cutoff | 20→80 Hz |
| 5 | burst | whole_tone | slide 0.3 | stereo width | 0.6→1.4 (mid/side) |
| 6 | steps | hirajoshi | atten 0.6 | LPF resonance | 0.15→0.70 |
| 7 | triangle | unquantised | dividr 4 | master trim | 0.92→1.0 |

The filter cutoff is the method's signature: `quantize_cv` snaps the drift CV to
**dorian** scale degrees (quantise-after-attenuation), so the low-pass cutoff
sweeps through a small set of *quantised* musical steps rather than a continuous
curve — the RANDOM8 stepped-voltage character.

## 4. Pitch / Tonal-Content Verification — **PASS**

SP-081 is a modulation layer (filter/pan/gain/reverb), so the correct gate is
**pitch fidelity vs. the dry reference** plus the SP-035 anti-noise signature.

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Dry-vs-wet dominant-peak hit-rate (0.5 s windows, 50–2000 Hz, ±4% vs ×1/×2/×3/×4/×½/×⅓) | **8/9 = 0.8889** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.7028** | ≥ 0.25 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **0/3 = 0.000** | < 50% | PASS |
| Median dominant peak | 220.0 Hz | — | Low-mid (counterpoint register) |
| LUFS / peak | -14.38 / 0.8913 | — | Limiter ceiling enforced |

The single miss (t=0.5 s: dry 294 Hz → wet 234 Hz) is a **filter-induced spectral
centroid shift**, not a pitch change — the LPF cutoff swept low at that instant and
re-weighted the harmonic partials; pitch-class content is preserved. The SP-035
failure signature (0 Hz frames, single-digit harmonic energy) is **absent**
(harmonic ratio 0.7028, far above the noise floor).

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **37.16%** | Tail padding only — no mid-track gaps |
| Peak / LUFS | **0.8913 / -14.38 LUFS** | Limiter(-1 dBFS) ceiling enforced |
| RMS per second | [0.094, 0.131, 0.102, 0.090, 0.011, 0.000] | 4.0 s active music, then reverb tail (s4) + digital silence (s5+) |
| Duration | 6.91 s | 4.0 s musical + FluidSynth tail + reverb decay |

The 37% silence is the legitimate tail after the last note (4.0 s music in a
6.91 s buffer); the four active seconds are continuous (RMS 0.09–0.13) with no
mid-track gaps.

## 6. Fixes & Discoveries During Run

1. **`SCALES_15` has no `minor_pentatonic`** — the `random8.py` module docstring
   usage example (`r8.channel(0).scale = "minor_pentatonic"`) names a scale that
   is not in `SCALES_15`. First run raised `ValueError: unknown scale
   'minor_pentatonic'`. Fixed by using `natural_minor` (a real member of the
   15-scale set). The 15 scales are: major, natural_minor, dorian, mixolydian,
   maqam_rast, maqam_bayati, maqam_hijaz, mayamalavagowla, mecakalyani,
   hanumatodi, hirajoshi, in_sen, yo, whole_tone, quarter_tone. (Doc bug in the
   module — worth a one-line fix upstream.)
2. **Random8 is CV-only, no `demo()`-driven audio** — unlike SP-070/SP-083 the
   module produces no audio directly; the absolute-layer realization had to map
   the 8 CV streams onto the global effect matrix. This is the intended,
   documented interpretation of a CV source as a production layer.
3. **Legacy source has broken note-offs** — see §2; documented, not fixed
   (production jobs process the existing MIDI as-is).
4. **`write_wav` int16 truncation bug (silent output — critical).** The
   `write_wav` helper cast float audio to `np.int16` **without** scaling:
   `clipped.astype(np.int16)` truncates every sample in (-1, 1) to 0, producing a
   byte-identical-size but **all-zero** WAV (and a near-empty OGG). This run's
   §4/§5 metrics were computed from the in-memory `final_master` array, never
   re-read from disk, so the delivered WAV/OGG on 09-28 were silently zeroed.
   Discovered during the SP-079 run (09-29) and fixed 09-30:
   `(clipped * 32767.0).astype(np.int16)`. Re-rendered and verified from disk —
   WAV read-back peak 0.8912, RMS 0.119, 395,110/609,024 nonzero samples; OGG
   decode peak 0.989, RMS 0.119. (The shared `sound/utils/io.py` `write_wav` was
   already correct — it scales ×32767; only these per-project cron scripts carried
   the local unscaled helper.)

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `SP081-random8-baroque-counterpoint-inversion.wav` | 1,218,092 B |
| Master OGG | `SP081-random8-baroque-counterpoint-inversion.ogg` | 39,131 B |
| Dry Reference | `dry_full_mix_sp001_reference.wav` | 1,218,092 B |
| Source MIDI | `MIDI/004_counterpoint_study.mid` | 228 B |
| Dry Stems | `Audio/stems_dry/` (2 × Acoustic_Grand_Piano) | 1,218,092 B each |
| Wet Stems | `Audio/stems_wet/` (2 × `*_RANDOM8.wav`) | 1,218,092 B each |
| Script | `Scripts/produce_sp081_cron.py` | 18.5 KB |
| Provenance | `provenance.json` | 0.9 KB |
| Stats | `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/grid_visualization.txt` | — |
| Selection | `.selection_cron.json` (Production root) | — |
| Report | `REPORT.md` | this file |
