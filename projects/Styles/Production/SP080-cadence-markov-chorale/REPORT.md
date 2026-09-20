# SP-080 CADENCE (Cadence Engine Rhythmic Variator w/ Flux Randomizer) — 064-markov-constraint-chorale

**Date (UTC):** 2026-09-20 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP080-cadence-markov-chorale/`
**Status:** PASS — mix FFT 45/45 (1.0000), harmonic energy 0.4629, ACF 0/12 unpitched, silence 18.16%, LUFS -14.06, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-080** — Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.generators.cadence_variator` → `CadenceEngine`, `CadenceLayer`, `CadenceBlock`, `FluxRandomizer` |
| Registry entries at pick time | **30 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086 |
| Already used last 7d (excluded) | SP-083 (09-19), SP-084 (09-17), SP-072 (09-16), SP-074 (09-15), SP-036 (09-14), SP-073 (09-13), SP-071 (09-12) |
| Eligible pool | **23 implemented methods** |
| Selection | `random.Random(20260920).choice(pool)` → **SP-080** (first SP-080 production run; module registered 2026-09-17 scan, never produced until tonight) |
| MIDI pool | 293 candidates under `Styles/` (excl. `phase1` + `Production`), 286 usable (>40 B); deterministic seeded pick → `Experimental/064-markov-constraint-chorale/MIDI/064-markov-constraint-chorale.mid` |
| Selection record | `Analysis/select_20260920.json` and `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Experimental/064-markov-constraint-chorale/` (Markov-Constraint Wavefront Chorale, UnitMatrix structure) |
| MIDI | `064-markov-constraint-chorale.mid` (copied to output `MIDI/`; 3,137 B) |
| Tempo / grid | 84 BPM (714,285 µs/beat), tpb 480; 22.86 s musical duration, 29.63 s render tail, 15,360 ticks (8 bars) |
| Form | 4 sections × 2 bars = 8 bars total, G minor (aeolian) `i -> VII -> III -> VI` (Gm - F - Bb - Eb) |
| Voices | Soprano (Flute GM74 ch0) · Alto (String Ensemble GM49 ch1) · Tenor (String Ensemble GM49 ch2) · Bass (Acoustic Bass GM33 ch3) |
| Texture | Diatonic 4-part polyphonic chorale driven by an order-1 Markov pitch-walk soprano with stochastic 16th density buildup |
| Why this source | Perfect test bed for Emergence Audio Envoy's Cadence Engine: 4-part counterpoint provides clear vertical voice boundaries to exercise multi-rate rhythmic variation, block modulation, and flux randomizer across independent vocal registers |

Grid (`Analysis/grid_visualization.txt`): 4 voices × 4 sections, 71% average onset density across all 8 bars.

---

## 3. Layer Discipline (Absolute)

SP-080 is an **absolute-layer rhythmic variation and modulation method**: `CadenceEngine` (Emergence Audio Envoy architecture) replaces the micro-rhythm, filter trajectory, dynamic accentuation, and spatial panning across all stems for the entire piece.

```
064-markov-constraint-chorale.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (5.22 MB)
 -> dry stems (RenderPipeline extraction, FX off):
      track00_Recorder / track01_String_Ensemble_2 / track02_String_Ensemble_2 / track03_Electric_Bass_finger
 -> SP-080 Cadence Engine (4 independent blocks per layer, multi-rate, independent feels):
      StepLanes (velocity / pitch / length / pan / combi LP-HP filter) ->
      FluxRandomizer (depth-scaled parameter jitter per block) ->
      Master LFO + Per-Layer LFO integration ->
      Dynamic SVF (StateVariableFilter) time-varying filter sweep ->
      Constant-power stereo panning & gain modulation ->
      per-stem peak-norm 0.89 -> trackXX_*_CADENCE.wav
 -> master bus sum -> AlgorithmicReverb (space diffusion) -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP080-cadence-markov-chorale.wav + .ogg (Opus 48k voip)
```

### Voice Profiles (Cadence Engine & Envoy Parameter Design)

| Voice Stem | Role | Block Steps | Rate | Feel | Direction | Flux Depth | Blocks Targeted | Filter Range (HP/LP) |
|---|---|---|---|---|---|---|---|---|
| `track00_Recorder` | Soprano Lead | `[8, 6, 8, 7]` | 2.0 (16ths) | straight | forward | 0.22 | `[0, 2]` | 250 Hz – 4,500 Hz |
| `track01_String_Ensemble_2` | Alto Counterline | `[7, 8, 6, 8]` | 1.5 (dotted) | swing | pingpong | 0.28 | `[1, 3]` | 180 Hz – 3,800 Hz |
| `track02_String_Ensemble_2` | Tenor Harmony | `[6, 8, 7, 5]` | 1.0 (8ths) | lurch (3-3-2) | forward | 0.25 | `[0, 1, 2]` | 120 Hz – 3,200 Hz |
| `track03_Electric_Bass_finger` | Bass Foundation | `[8, 8, 4, 8]` | 1.0 (8ths) | straight | forward | 0.12 | `[0]` | 40 Hz – 2,200 Hz |

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on delivered wet mix audio:

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–2000 Hz, ±4% vs fund ×1/×2/×3/×4//2) | **45/45 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.4629** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.30) | **0/12 = 0.000** | < 50% | PASS |
| Lowest MIDI notes seen | 38 (D2), 43 (G2), 46 (Bb2), 50 (D3) — chorale bass roots | — | Sane |
| Median dominant peak | 196.0 Hz (G3 chorale tonic) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Tonal gravity and pitch integrity of the G minor chorale remain 100% intact.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **18.16%** | Natural breathing room between chorale phrases and section cadences |
| Peak / LUFS | **0.8913 / -14.06 LUFS** | Limiter(-1 dBFS) applied last |
| RMS profile | ~0.08–0.18 active | Dynamic swell matching Cadence variator envelope curves |

---

## 6. Fixes & Discoveries During Run

1. **Multi-Rate Polyrhythmic Block Alignment**: When layers run at different rates (e.g. rate 2.0 vs 1.5 vs 1.0) with non-uniform block lengths (e.g. `[8,6,8,7]`), total cycle lengths vary between 27 and 29 steps. Rendered enough loop repetitions (`loops=np.ceil(...) + 1`) to ensure zero-dropout envelope coverage across the entire 29.63 s stem timeline.
2. **State Variable Filter Stability**: Dynamically mapped step `lp` and `hp` lanes to continuous cutoffs across 256-sample audio blocks, preventing filter zipper noise while faithfully reproducing Envoy's step-filter motion.
3. **Chorale Stereo Staging**: Balanced soprano (+0.35) and alto (-0.45) on opposite sides with tenor counter-panned (+0.45) and bass anchored dead center (0.0), preserving vocal separation.

---

## 7. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP080-cadence-markov-chorale.wav` | 5,227,564 B |
| Full mix OGG (Opus 48k voip) | `SP080-cadence-markov-chorale.ogg` | 204,222 B |
| Dry reference mix (SP-001) | `dry_full_mix_sp001_reference.wav` | 5,227,564 B |
| Source MIDI (copy) | `MIDI/064-markov-constraint-chorale.mid` | 3,137 B |
| Dry stems | `Audio/stems_dry/track00..03.wav` | 5,227,564 B each |
| Wet stems (peak 0.89) | `Audio/stems_wet/track00..03_CADENCE.wav` | 5,227,564 B each |
| Renderer script | `Scripts/produce_sp080_cron.py` | 16,932 B |
| Verification JSON + grid | `Analysis/pitch_verification.json`, `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
