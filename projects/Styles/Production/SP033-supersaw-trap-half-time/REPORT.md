# SP-033 SUPERSAW SWARM (Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad) — 001-trap-half-time

**Date (UTC):** 2026-09-21 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/`
**Status:** PASS — mix FFT 56/56 (1.0000), harmonic energy 0.3773, ACF 1/14 unpitched, silence 19.23%, LUFS -14.28, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-033** — Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad (Native Instruments SuperStarSaw / A.G. Cook-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.synthesis.supersaw_swarm` → `SupersawSwarm`, `MorphPad`, `SwarmSnapshot`, `SCALES`, `CHORDS` |
| Registry entries at pick time | **32 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–091 |
| Already used last 7d (excluded) | SP-080 (09-20), SP-083 (09-19), SP-084 (09-17), SP-072 (09-16), SP-074 (09-15), SP-036 (09-14), SP-073 (09-13) |
| Eligible pool | **25 implemented methods** |
| Selection | `random.Random(20260921).choice(pool)` → **SP-033** (first SP-033 production run in current cycle) |
| MIDI pool | 228 usable candidates (>500 B, excl. `Production`, `phase1`, `candidates`); deterministic seeded pick → `Trap/001-trap-half-time/MIDI/trap-half-time.mid` |
| Selection record | `Analysis/select_20260921.json` and `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Trap/001-trap-half-time/` (Trap with 808 sub-bass, half-time drums, dark Phrygian pads) |
| MIDI | `trap-half-time.mid` (copied to output `MIDI/`; 1,609 B) |
| Tempo / grid | 140 BPM (428,571 µs/beat), tpb 480; 27.43 s musical duration, 34.63 s render tail, 30,720 ticks (16 bars) |
| Form | 4 sections × 4 bars = 16 bars total, C Phrygian modal progression (`Cm(add b9) -> Eb -> G -> Cm`) |
| Voices | KickSnare (ch9) · Hat (ch9) · 808 Sub (Electric Bass GM33 ch2) · Pad (String Ensemble GM49 ch3) · Lead (Square Lead GM80 ch0) |
| Texture | Half-time trap beat with syncopated 16th hats/rolls, deep sub roots, dark sustained Phrygian chords, and sparse motif lead |
| Why this source | The detuned supersaw swarm and scale/chord quantizer architecture is made for modern electronic trap and hyperpop textures: rich saw stacks replace GM string pads and square leads while 808 sub bass receives tight low-end harmonic reinforcement |

Grid (`Analysis/grid_visualization.txt`): 5 voices × 4 sections, 16 bars total, half-time trap groove.

---

## 3. Layer Discipline (Absolute)

SP-033 is an **absolute-layer synthesis and harmonic quantization method**: `SupersawSwarm` (NI SuperStarSaw architecture with dual 16-oscillator swarms, detune spread ladders, stereo field distribution, amplitude drift, and bilinear MorphPad control) replaces the melodic, chordal, and bass voices across the entire piece.

```
trap-half-time.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (6.11 MB)
 -> dry stems (RenderPipeline extraction, FX off):
      track00_Drums / track01_Drums / track02_Electric_Bass_finger / track03_String_Ensemble_2 / track04_Lead_1_square
 -> SP-033 Supersaw Swarm processing:
      Pad (track03): 16-oscillator dual swarm, 38c spread, Phrygian scale quantize, morph pad blend ->
      Lead (track04): 16-oscillator dual swarm, 24c spread, minor scale quantize, wide stereo pan ->
      808 Sub (track02): 8-oscillator tight swarm, 6c spread, lowpass tilt (0.45 brightness), root quantize ->
      Drums (track00, track01): punch-preserved transients, peak-norm ->
      per-stem peak-norm 0.89 -> trackXX_*_SUPERSAW.wav
 -> master bus sum -> AlgorithmicReverb (room_size 0.6, wet_dry 0.15) -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
 -> SP033-supersaw-trap-half-time.wav + .ogg (Opus 48k voip)
```

### Voice Profiles (Supersaw Swarm & MorphPad Parameter Design)

| Voice Stem | Role | Osc Count | Spread | Drift | Brightness | Harmony Mode | Morph XY | Pan Spread | Attack / Rel |
|---|---|---|---|---|---|---|---|---|---|
| `track02_Electric_Bass_finger` | 808 Sub Bass | 8 | 6.0 cents | 0.10 | 0.45 (LP tilt) | Phrygian | (0.1, 0.1) | 0.20 | 15ms / 100ms |
| `track03_String_Ensemble_2` | Dark Pad | 16 | 38.0 cents | 0.45 | 0.75 | Phrygian | (0.8, 0.4) | 0.95 | 150ms / 350ms |
| `track04_Lead_1_square` | Melodic Lead | 16 | 24.0 cents | 0.35 | 0.90 | Minor | (0.5, 0.8) | 0.75 | 10ms / 150ms |
| `track00_Drums` / `track01_Drums` | Half-Time Beats | — | — | — | — | — | — | — | Punch peak-norm |

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on delivered wet mix audio:

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–1000 Hz, ±4.5% vs fund ×1/×2/×3/×4//2) | **56/56 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.3773** | ≥ 0.30 | PASS |
| ACF unpitched (every-2nd 1 s, conf < 0.25) | **1/14 = 0.071** | < 50% | PASS |
| Expected pitch classes seen | C, Db, Eb, G, Ab, Bb (C Phrygian / Minor) | — | Aligned |
| Median dominant peak | 130.8 Hz (C3) / 196.0 Hz (G3) / 65.4 Hz (C2 sub) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Tonal gravity and pitch integrity of the C Phrygian trap harmony remain 100% intact.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **19.23%** | Natural breathing room between trap half-time bars and lead pauses |
| Peak / LUFS | **0.8913 / -14.28 LUFS** | Limiter(-1 dBFS) applied last |
| RMS profile | ~0.08–0.17 active | Steady energy across all 16 measures |

---

## 6. Fixes & Discoveries During Run

1. **Stem Alignment & Padding**: All stems padded to exact maximal length (1,527,296 samples = 34.63 s) prior to summation to prevent timing drift.
2. **Mastering API Alignment**: Used `AlgorithmicReverb(wet_dry=0.15)` and `normalize_to_lufs(sample_rate=SR)` with `Limiter(sample_rate=SR)` matching current musicom audio API signatures.
3. **Harmonic Quantization Consistency**: The `SupersawSwarm` harmonic quantization engine successfully snapped wide detuned oscillator clusters into C Phrygian scale confines, avoiding microtonal dissonance while preserving rich chorus width.

---

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/SP033-supersaw-trap-half-time.wav` | 6,109,228 B |
| Master OGG | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/SP033-supersaw-trap-half-time.ogg` | 183,173 B |
| Dry Reference | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/dry_full_mix_sp001_reference.wav` | 6,109,228 B |
| Source MIDI | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/MIDI/trap-half-time.mid` | 1,609 B |
| Dry Stems | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/Audio/stems_dry/` (5 stems) | ~30.5 MB total |
| Wet Stems | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/Audio/stems_wet/` (5 stems) | ~30.5 MB total |
| Script | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/Scripts/produce_sp033_cron.py` | 18.5 KB |
| Provenance | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/provenance.json` | 912 B |
| Report | `/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time/REPORT.md` | this file |
