# SP-084 AIRPIPE (Flue-Pipe Physical Model w/ Air-Supply Modulation) — 099-classical-7sec

**Date (UTC):** 2026-09-17 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP084-airpipe-classical-7sec/`
**Status:** PASS — mix FFT 259/259 (1.0000), harmonic energy 0.3305, ACF 4/65 unpitched, silence 1.97%, LUFS -14.00, peak 0.8913.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-084** — Flue-Pipe Physical Model w/ Air-Supply Modulation (Modartt Airteq-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale `SP-001..SP-052` range) |
| Registered module | `sound.synthesis.air_pipe` → `AirPipe`, `AirPipePatch`, `midi_to_freq` |
| Registry entries at pick time | **30 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086 (full list in `Analysis/select_20260917.json`) |
| Already used last 7d (excluded) | SP-072 (09-16), SP-074 (09-15), SP-036 (09-14), SP-021 (09-14), SP-073 (09-13), SP-071 (09-12), SP-011 (09-11) |
| Eligible pool | **23:** SP-001, 024, 026, 028, 032, 033, 034, 035, 037, 069, 070, 075–086 |
| Selection | `random.Random(20260917).choice(pool)` → **SP-084** (first SP-084 production run; module registered 2026-09-17 scan, never produced until tonight) |
| MIDI pool | 291 candidates under `Styles/` (excl. `phase1` + `Production`), 284 usable (>40 B); deterministic seeded pick → `Classical/099-classical-crossover-pathA-7sec/MIDI/099-classical-7sec.mid` |
| Selection record | `Analysis/select_20260917.json` (copy of `/opt/data/sel_20260917.json`) |

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Classical/099-classical-crossover-pathA-7sec/` (Classical Crossover, Path A top-down, 7 sections) |
| MIDI | `MIDI/099-classical-7sec.mid` (copied to output `MIDI/`; 8401 B) |
| Tempo / grid | 96 BPM (625000 us/beat), tpb 480; 130.00 s music, 99840 ticks |
| Form | Intro 4 \| A 8 \| B 8 \| Dev 8 \| A' 8 \| B' 8 \| Coda 8 = 52 bars, C major |
| Voices | Lead Violin GM41 ch0 (**243 notes**, MIDI 60–88: C4–E6, dom 72/76/77) · Counter Flute/Recorder GM74 ch1 (**76 notes**, 60–76, joins A2/B/B' only) · Piano GM0 ch2 (**315 notes**, 36–52 chord pads) · Pad StringEns GM49 ch3 (**315 notes**, same pad stack, wide pan) · Bass GM33 ch4 (**98 notes**, roots 36/38/41/43/45, beats 1&3) — **1047 notes total** |
| Texture | Intro solo corridor → A diatonic theme → B tintinnabuli M+T → Dev tremolo peak → A' denser +12 → B' shifted shadow → Coda dropout (Lead/Counter exit bar 4, pads/bass bar 6) |
| Why this source | First production use of SP-084 wants a long polyphonic bed where per-note air pressure and the open-pipe mode stack are audible across registers (C2 pads → E6 lead); 1047 notes at 34 ms/note keeps per-note `AirPipe.render` CPU tractable (~34 s total); no drums, so the absolute pipe layer is unambiguous |

Grid (`Analysis/grid_visualization.txt`, sanctioned `visualization/grid.py`, 5040 ticks/char): all voices ~100% density single block; Counter 83% (joins late, drops in Coda). Matches the 099 project's own 7-section grid (Lead 97%, Counter 37%, Piano/Pad 75%, Bass 47% at 480 ticks/char) — same DNA, coarser cell here.

## 3. Layer discipline (absolute)

SP-084 is an **absolute-layer synthesis method**: one `AirPipe` per note replaces the production layer for **all voices**. No drums exist in the source, so nothing rides the GM kit — the kit appears only in the SP-001 reference render. Per-voice stems shipped wet (pipe synth) and dry (SoundFont).

```
099-classical-7sec.mid
 -> per-note AirPipe(midi, pressure, open) + velocity gain at call site
      + outer half-cosine envelope + 0.25 s tail + const-power pan
      -> voice bus sum -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
      -> SP084-airpipe-classical-7sec.wav (130.74 s stereo) + .ogg (Opus 48k voip)
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav 133.?? s incl. GM tails
 -> dry stems (RenderPipeline.render_stems, FX off): track00_Viola / track01_Recorder /
      track02_Acoustic_Grand_Piano / track03_String_Ensemble_2 / track04_Electric_Bass_finger
 -> wet stems (same pipe synth, peak 0.89): trackXX_*_AIRPIPE (full padded length, time-aligned)
```

### Voice profiles (air-supply design)

| Voice | GM | pressure | pan | gain | Role |
|---|---|---|---|---|---|
| Lead | 41 Viola | 0.62 | -0.20 | 1.00 | principal rank, full wind |
| Counter | 74 Recorder | 0.50 | +0.20 | 0.90 | softer flute rank |
| Piano | 0 Grand | 0.52 | -0.35 | 0.75 | open-pipe choir L |
| Pad | 49 StrEns2 | 0.52 | +0.35 | 0.75 | open-pipe choir R (doubles Piano stack) |
| Bass | 33 E.Bass finger | 0.66 | 0.00 | 0.95 | 16'-feel via deep wind, centre |

All pressures stay under the module `OVERBLOW_PRESSURE = 0.75` (verified: `mode_amps(0.95)` collapses f0 1.000→0.263 and boosts 2f0 0.406→1.000 — none of tonight's notes overblow). Piano/Pad double the same chord stack panned wide so the two choirs read as a divided rank, not mono doubling. Bass at 0.66 is the hardest-blown rank — depth without octave flip.

## 4. Pitch / tonal-content verification — **PASS**

Mandatory for every synthesis method: size asserts and silence ratios do **not** catch noise (SP-035 GENDYN shipped broadband noise past both). Three checks, all on the **delivered files**:

| Metric | Wet mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **259/259 = 1.0000** | ≥ 0.60 | PASS |
| Median harmonic energy (8 harmonics of lowest fund) | **0.3305** | ≥ 0.30 (noise = single digits) | PASS |
| ACF unpitched (every-2nd 1 s, conf<0.30) | **4/65 = 0.062** | < 50% | PASS |
| Misses | **none** — zero miss windows | — | clean |
| Lowest notes seen | MIDI 36 (C2), 38, 41, 43, 45 — the source bass roots | — | sane |
| Median dominant peak | 98 Hz ≈ G2 (bass-region blend) | — | sane |

The SP-035 failure signature (0 Hz frames + ~4% harmonic energy) is **absent**.

Full JSON: `Analysis/pitch_verification.json`.

### Module actually engaged (not bypassed)

Single-note probe (seed 7): C4 dom 262.0 Hz vs 261.6 target (0.14%), D2 65.0 vs 65.4 (0.62%), E6 1319.0 vs 1318.5 (0.04%) — the resonator lands on MIDI pitch in every register. Per-note render 14–115 ms (bass cheapest: fewer modes above 22 kHz cap... actually n_modes clips at 24 for lows, 16 for E6).

Wind-sweep (same phrase C–E–G–C at static pressures): rms 0.3215 → 0.4174 → 0.4556 and centroid 10783.7 → 10786.4 → 10798.8 Hz across 0.35/0.55/0.66 — air supply measurably moves level and brightness, so the per-voice pressure design is in the signal path, not decorative.

DAM A/B (4-note phrase, static vs 0.8 Hz global-air swell): outputs **differ** (rms-diff 0.01694, correlation 0.9964, peaks 0.8750 vs 0.9110, centroid 10793.9 vs 10809.6 Hz). The modulation hook is live in the module; tonight's render uses static per-voice wind (deterministic, Dev tremolo already in the notes) — the swell path is proven available for a follow-up pass.

## 5. Silence / RMS profile + level

| Metric | Wet | Dry (SP-001 ref) | Note |
|---|---|---|---|
| Silence (<0.001) | **1.97%** | 2.56% | wet denser — pipe tails fill interstices |
| Peak / LUFS | 0.8913 / **-14.00** | — | limiter last |
| RMS/s wet | 0.032–0.225, median ~0.15 | — | no dead zones; min is final tail second |
| RMS/s shape | dips s9, s119–123 (Coda dropout zone), peaks s20/s50/s68 (A/Dev/A' overlap) | same loci | **loci match dry** — arrangement breathing, not production gaps |

Per-second tables: `Analysis/render_stats.json`. Zero mid-track gaps; the only low windows are the composed Coda dropout and the final tail.

## 6. Fixes applied during this run

1. **`stopped=True` renders one octave HIGH (module physics bug, documented not patched).** `AirPipe.mode_freqs` computes f0 with the open-pipe formula `c/(2L'+...)` for both cases and only thins the spectrum to odd harmonics for stopped pipes — probe: stopped C4 dom = 524.0 Hz vs 261.6 target. True stopped f0 needs half that (f0 = c/4L'). Fix for tonight: **open pipes only** on all five voices; the Bass D2–A2 region is conveyed by open-pipe depth at 0.66 wind instead of a stopped 16' rank. Recommendation: fix `mode_freqs` to halve f0 when `stopped=True`, then re-render Bass stopped for the proper octave-down colour.
2. **No velocity path in the module** (same class as SP-072/SP-073: `render()` has no velocity/dynamics input). Fix: explicit `clip((vel/90)**1.5, 0.22, 1.30)` gain at the call site — Dev accents and Coda taper survive.
3. **Per-mode `decay = exp(-t*(0.4+0.25k))` fades long pads** (2.47 s Coda holds lose ~60% by end). Fix: outer half-cosine note envelope + 0.25 s tail per note for click safety; the decay reads as pipe chiff, not dropout — verified by RMS loci matching dry.
4. **Stem labels are GM program names, not composer voice names** (`track00_Viola`, `track01_Recorder`, `track03_String_Ensemble_2`, `track04_Electric_Bass_finger` — composer called them Lead/Counter/Pad/Bass). Route per-voice DSP by the stem-label string, never the voice name. Cross-checked against `sound/render/pipeline.py` GM table + ch9-drums rule (no drums here).

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP084-airpipe-classical-7sec.wav` (130.74 s, 44.1 kHz stereo) | 23,062,960 B |
| Full mix OGG (Opus 48k voip) | `SP084-airpipe-classical-7sec.ogg` | 659,040 B |
| Dry reference mix (SP-001, FX-off) | `dry_full_mix_sp001_reference.wav` | 23,386,924 B |
| Source MIDI (copy) | `MIDI/099-classical-7sec.mid` | 8,401 B |
| Dry stems | `Audio/stems_dry/track00_Viola.wav` / `track01_Recorder.wav` / `track02_Acoustic_Grand_Piano.wav` / `track03_String_Ensemble_2.wav` / `track04_Electric_Bass_finger.wav` | ~23.3 MB each |
| Wet stems (peak 0.89) | `Audio/stems_wet/trackXX_*_AIRPIPE.wav` (130.74 s each, time-aligned) | 23,062,960 B each |
| Renderer | `Scripts/produce_sp084_cron.py` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Selection records | `Analysis/select_20260917.json` (+ `/opt/data/sel_20260917.json`) | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 8. Listen for

- Lead violin line (C–D–E–G cells, Dev peak E6) now speaks with pipe chiff: breathy attacks at 0.62 wind, most exposed in the Intro corridor (bars 0–3, near-solo).
- Counter flute answers (A2/B/B' only) as the softer 0.50-wind rank right — A/B test against the dry Recorder stem to hear the jet breath the SoundFont lacks.
- Piano/Pad chord stacks (C–F–G–Am regions) as a divided open-pipe choir L/R — Dev tremolo bars shimmer instead of hammering.
- Bass roots (C2–A2, beats 1&3) with 16'-feel depth at hard wind — compare `track04_Electric_Bass_finger.wav` (dry) vs `track04_Electric_Bass_finger_AIRPIPE.wav` (wet) for the stopped-rank that got away: tonight open, octave-down colour reserved for the post-fix re-render.
- Coda dropout (s119+): Lead/Counter gone by bar 4, pads/bass by bar 6 — the pipe tails make the emptying audible as thinning ranks, not a fader move.

## 9. Quality gate

- [x] MIDI present for the audio render (`MIDI/099-classical-7sec.mid`)
- [x] OGG non-empty (659,040 B) and playable-length (130.74 s)
- [x] Pitch verification run and reported (PASS: FFT 259/259, harm 0.3305, ACF 4/65)
- [x] Silence ratio + per-second RMS measured; loci match dry, no production gaps
- [x] Full mix WAV + per-track stems (dry AND wet/airpipe)
- [x] `provenance.json` per artifact set
- [x] Grid visualization written before trusting timing (sanctioned visualizer)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Registry source is the implemented `SP_METHODS` dict, not a stale range or spec-only DB
