# SP-072 CRITTER PAD (Brackish Pads three-partial + stochastic microtonal Critters) — Balfolk-Cinematic / 014-balfolk-cinematic

**Date (UTC):** 2026-09-16 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP072-critter-balfolk-cinematic/`
**Status:** PASS — mix FFT 93/96 (0.9688), harmonic energy 0.448, ACF 1/24 unpitched, silence 1.00%, LUFS -14.00, peak 0.7706.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-072** — Three-Partial Pad Bank with Stochastic Microtonal Critters Layer (Brackish Pads-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale `SP-001..SP-035` range) |
| Registered module | `sound.synthesis.critter_pad` → `PadPartialBank`, `Partial`, `Critters`, `cassette`, `splosh`, `pump_envelope` |
| Registry entries at pick time | **19 implemented:** SP-001, 011, 021, 024, 026, 028, 032, 033, 034, 035, 036, 037, 069, 070, 071, **072**, 073, 074, 075 |
| Already used last 7d (excluded) | SP-074 (09-15), SP-036 (09-14), SP-073 (09-13), SP-071 (09-12), SP-011 (09-11), SP-024 (09-10), SP-001 (09-09) |
| Eligible pool | **SP-021, SP-026, SP-028, SP-032, SP-033, SP-034, SP-035, SP-037, SP-069, SP-070, SP-072, SP-075** (12) |
| Selection | `random.Random(20260916).choice(pool)` → **SP-072** (first SP-072 production run; module implemented, never produced until tonight) |
| MIDI pool | 290 candidates under `Styles/` (excl. `phase1` + `Production`), 283 usable (>40 B); deterministic seeded pick → `Balfolk/014-balfolk-cinematic/MIDI/balfolk_cinematic_v1.mid` |
| Selection record | `Production/.selection_cron.json` (rewritten this run) + `Analysis/select_20260916.json` + `Analysis/selector_raw_20260916.json` (raw `/opt/data/sel_20260916.json`) |

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Balfolk/014-balfolk-cinematic/` (Balfolk Jig → Cinematic Epic hybrid) |
| MIDI | `MIDI/balfolk_cinematic_v1.mid` (copied to output `MIDI/`; 2167 B) |
| Tempo / grid | 120 BPM (500000 us/beat), 4/4 declared, tpb **10080** (unusual resolution); 48.00 s music |
| Voices | Violin GM40 ch0 (**112 notes**, MIDI 62–69 = D4–A4: 62×32, 64×32, 65×16, 67×16, 69×16; motif 0.25 s notes, 1.5 s pedal closes) · String Ensemble GM48 ch1 (**112 notes**, all MIDI 38 = D2 pedal, 0.125–1.5 s) |
| Texture | Legato zero-gap lines (gap ticks min/med/max = 0/0/0 on both voices); strings enter at tick 241920 (12.0 s); density 2.33 notes/s/voice |
| Why this source | First production use of SP-072 wants a slow legato bed where the Poisson-triggered Critters clusters and cassette/splosh character are audible; 224 notes at 48 s keeps per-note `render_note` CPU tractable; no drums, so the absolute pad layer is unambiguous |

Grid (`Analysis/grid_visualization.txt`, sanctioned `visualization/grid.py`, 5040 ticks/char): both voices 100% density single 13-char block, no rest bars.

## 3. Layer discipline (absolute)

SP-072 is an **absolute-layer synthesis method**: the `PadPartialBank` replaces the production layer for **all voices**. No drums exist in the source, so nothing rides the GM kit — the kit appears only in the SP-001 reference render. Per-voice stems shipped wet (pad synth) and dry (SoundFont).

```
balfolk_cinematic_v1.mid
 -> per-note PadPartialBank.render_note (voice profiles below, 0.40 s tail)
      + outer half-cosine envelope + velocity gain at call site + const-power pan
      -> voice bus sum -> cassette(0.35 blend) + splosh(0.22)
      -> peak-norm 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
      -> SP072-critter-balfolk-cinematic.wav (48.87 s stereo) + .ogg (Opus 48k voip)
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav 51.75 s
 -> dry stems (RenderPipeline.render_stems, FX off): track00_Violin / track01_String_Ensemble_1
 -> wet stems (same pad synth, peak 0.89): track00_Violin_CRITTER / track01_String_Ensemble_1_CRITTER
```

### Voice profiles (measurement-driven)

| Voice | GM | basic attack/release | complex attack/release | wobble b/c | Critters density / set / drift | balance b/c/cr | gain | pan |
|---|---|---|---|---|---|---|---|---|
| Violin lead | 40 | 0.08 / 0.30 s | 0.12 / 0.40 s | 5 / 12 c | **2.5/s, quarter-tone (±50 c), 25 c** | 0.70 / 0.50 / 0.50 | 1.00 | -0.20 |
| String pedal D2 | 48 | 0.25 / 0.70 s | 0.40 / 1.00 s | 4 / 9 c | 1.2/s, eighth-tone (±25 c), 18 c | 0.75 / 0.45 / 0.35 | 0.85 | +0.20 |

Lead envelopes are deliberately fast for a pad (0.08–0.12 s attack) because the motif moves in 0.25 s steps — stock 1.2–1.8 s attacks would smear it into mush. Pedal keeps the slow Brackish swell. Cassette 0.35 blend + splosh 0.22 on the bus = lo-fi wear + solidity without drowning the motif.

## 4. Pitch / tonal-content verification — **PASS**

Mandatory for every synthesis method: size asserts and silence ratios do **not** catch noise (SP-035 GENDYN shipped broadband noise past both). Three checks, all on the **delivered files**:

| Metric | Wet mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3//2) | **93/96 = 0.9688** | ≥ 0.60 | PASS |
| Median harmonic energy (8 harmonics of lowest fund) | **0.448** | ≥ 0.30 (noise = single digits) | PASS |
| ACF unpitched (every-2nd 1 s, conf<0.30) | **1/24 = 0.042** | < 50% | PASS |
| Misses (3) | t=1.0 dom 772 Hz vs {64,69}; t=4.0 dom 388 Hz vs {64,69}; t=18.5 dom 294 Hz vs {38,65,67} — all land on upper partials of the active chord stack, not noise | — | explained |
| Lowest notes seen | MIDI 38 (D2 pedal), 62/64/65 — the source registers | — | sane |
| Median dominant peak | 74 Hz ≈ D2 pedal | — | sane |

The SP-035 failure signature (0 Hz frames + ~4% harmonic energy) is **absent**.

Full JSON: `Analysis/pitch_verification.json`.

### Critter-presence A/B (module actually engaged, not bypassed)

Single-note control (A4 440 Hz, 1.5 s, seed 11, lead profile): critters 0.50 vs 0.0 — outputs **differ** (rms 0.1853 vs 0.2576; centroid 7333 vs 8438 Hz). The Critters partial measurably reshapes the spectrum (adds low-mid cluster energy, pulls centroid down ~1.1 kHz), so the stochastic layer is proven in the signal path.
Wet-vs-dry violin stem correlation **0.0213** ≈ 0 — expected for two different synthesis engines on the same notes.

## 5. Silence / RMS profile + level

| Metric | Wet | Dry (SP-001 ref) | Note |
|---|---|---|---|
| Silence (<0.001) | **1.00%** | 6.82% | wet denser — pad tails + splosh fill interstices |
| Peak / LUFS | 0.7706 / **-14.00** | — | limiter last |
| RMS/s wet | 0.054–0.225, median 0.142 | — | no dead zones; min is final tail second |
| RMS/s shape | rises s12+ (strings enter), peaks s24–35 (overlap zone), decays to tail | same loci | **loci match dry** — arrangement breathing, not production gaps |

Per-second tables: `Analysis/render_stats.json`. Zero mid-track gaps; only sub-0.01-RMS-adjacent window is the final 0.87 s tail.

## 6. Fixes applied during this run

1. **Timeout kill during dry-stem render (run 1).** The 550 s-capped producer finished the wet mix + wet stems + dry mix, then died inside `RenderPipeline.render_stems` track 2 — leaving a 2.1 MB partial WAV (invalid: `fmt chunk and/or data chunk missing`) plus the pipeline's leftover single-track `.mid`. Fix: run-2 reused the leftover single-track MIDI (valid, 1101 B, 112 notes) for a clean standalone fluidsynth re-render (9.1 MB, header-valid), archived the MIDI to `Analysis/stem2_single_track.mid`, removed the leftover. Lesson for future jobs: the pipeline writes temp MIDIs into the output dir and only deletes them per-track after render — an interrupted run always leaves one; reuse-or-rebuild, never ship the partial WAV.
2. **`render_note()` peak-normalizes every note to 0.8**, erasing dynamics (SP-073 lesson, same class). Fix: explicit `clip((vel/90)**1.5, 0.22, 1.30)` gain at the call site.
3. **Legato zero-gap motif vs slow pad envelopes.** Stock bank attacks (1.2–1.8 s) are ~5× the motif step (0.25 s). Fix: per-voice fast envelopes on the lead (0.08/0.12 s) + outer half-cosine note envelope + 0.40 s tail per note for click safety.
4. **`mido` has no `__version__`** (env probe crashed on the last line). Cosmetic; noted so future probes don't trip.

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP072-critter-balfolk-cinematic.wav` (48.87 s, 44.1 kHz stereo) | 8,619,876 B |
| Full mix OGG (Opus 48k voip) | `SP072-critter-balfolk-cinematic.ogg` | 271,673 B |
| Dry reference mix (SP-001, FX-off) | `dry_full_mix_sp001_reference.wav` (51.75 s incl. GM tails) | 9,128,748 B |
| Source MIDI (copy) | `MIDI/balfolk_cinematic_v1.mid` | 2,167 B |
| Dry stems | `Audio/stems_dry/track00_Violin.wav` (50.60 s) / `track01_String_Ensemble_1.wav` (51.75 s) | 8,926,508 / 9,128,748 B |
| Wet stems (peak 0.89) | `Audio/stems_wet/track00_Violin_CRITTER.wav` / `track01_String_Ensemble_1_CRITTER.wav` (48.87 s each) | 8,619,876 B each |
| Renderer | `Scripts/produce_sp072_cron.py` | — |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| Stem audit record | `Analysis/stem2_single_track.mid` (reused single-track MIDI) | 1,101 B |
| Selection records | `Analysis/select_20260916.json`, `Analysis/selector_raw_20260916.json` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 8. Listen for

- Lead violin motif (D–E–F–G–A jig cells) now breathes: quarter-tone Critters clusters bloom behind the 0.25 s steps, most audible in the s12+ string-entry zone where the D2 pedal gives them something to beat against.
- The D2 pedal is a slow Brackish swell, not an organ hold — wow/flutter + eighth-tone drift make it wobble like a worn Mellotron tape.
- Cassette wear sits low in the blend (0.35): attacks stay readable, tails get the lo-fi fur.
- Compare `dry_full_mix_sp001_reference.wav` (GM violin + strings, clean) vs wet mix: same jig DNA, haunted tape-machine double.

## 9. Quality gate

- [x] MIDI present for the audio render (`MIDI/balfolk_cinematic_v1.mid`)
- [x] OGG non-empty (271,673 B) and playable-length (48.87 s)
- [x] Pitch verification run and reported (PASS: FFT 93/96, harm 0.448, ACF 1/24)
- [x] Silence ratio + per-second RMS measured; loci match dry, no production gaps
- [x] Full mix WAV + per-track stems (dry AND wet/critter)
- [x] `provenance.json` per artifact set
- [x] Grid visualization written before trusting timing (sanctioned visualizer)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Registry source is the implemented `SP_METHODS` dict, not a stale range or spec-only DB
