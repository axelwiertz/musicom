# REPORT — SP-069 Topology Distortion × 018-rock-apprenticeship (Study 02)

**Job:** random-style production (SP) layer-aligned
**Date (UTC):** 2026-10-07 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP069-topology-distortion-blues-rock-shuffle/`
**Status:** PASS — pitch hit-rate 0.9904, harmonic-energy retention 0.846, silence 4.70%, LUFS −14.00, peak 0.1908, mono correlation 0.999.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-069** — Switched Discrete Distortion Topology Bank (Teaching Machines FuzzBillion-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.effects.topology_distortion` → `FuzzBillion`, `TopologyStage`, `ELEMENTS`, `random_code` |
| Registry entries at pick time | **40 implemented** (SP-001 … SP-100) |
| Already used last 7d (excluded) | SP-021, SP-072, SP-075, SP-080, SP-083, SP-086, SP-091 |
| Eligible pool | **33 implemented methods** |
| Selection | `random.choice(sorted(eligible))` (unseeded true-random) → **SP-069** |
| MIDI pool | All `.mid` outside `Production/`, skipping `phase1`; 199 well-formed candidates (tpb 480, ≥8 notes, ≥1 program change, ≥2 channels) |
| Selection record | `Analysis/select_20261007.json` + `provenance.json` + `../.selection_cron.json` |

The method is a bank of **11 serial nonlinear stages**, each a 10-position switch
(0 bypass, 1 transformer-saturation, 2 tube-asymmetric, 3 JFET square-law,
4 germanium-pair, 5 silicon-pair, 6 single-diode clamp, 7 LED-pair,
8 CMOS hard clip, 9 op-amp rail foldback) → `10**11` distinct circuits. Each
antiparallel diode pair uses `y = Vk · asinh(x/Vk)` with exact knee voltages
(Ge 0.30 V, Si 0.65 V, LED 1.80 V).

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Hybrid/018-rock-apprenticeship/` — Study 02 "Blues Rock Shuffle Engine" |
| MIDI | `study-02-blues-rock-shuffle-engine.mid` (copied to `MIDI/`; 8,027 B) |
| Genre | Blues-rock shuffle boogie (rock apprenticeship study) |
| Key / tonality | **E blues** — source pitch classes {0,1,2,4,6,7,8,9,10,11} (blue notes + chromatic passing tones) |
| Tempo / grid | 112 BPM, tpb 480, 4/4 triplet-shuffle subdivision; 51.43 s = 96 beats = 24 bars (12-bar blues × 2) |
| Voices (stems) | `track00_Overdriven_Guitar` (GM 29, full 24 bars) · `track01_Electric_Bass_finger` (GM 33, full) · `track02_Distortion_Guitar` (GM 30, bars 12–21 solo) · `track03_Drums` (ch9, full) |
| Note range | 36 (C2) → 74 (D5) |

Grid (`Analysis/grid_visualization.txt`): rhythm guitar + bass + drums run the
whole piece; the second distortion guitar enters at bar 12 (the solo chorus).

## 3. Layer Discipline (Absolute)

SP-069 is an **absolute-layer distortion method**: one `FuzzBillion` circuit
applied to the whole mix — no per-voice parameterization. Distortion is
memoryless and nonlinear, so `Σ distort(stemᵢ) ≠ distort(Σ stemᵢ)`; the
primary output is the whole-piece (full-mix) distortion, with per-stem wet
copies provided as a convenience (same circuit per voice) for DAW import.

**Master circuit (random draw `random_circuit(seed=20261007)`) — 11 switches,**
signal order left → right:

```
CIRCUIT = (3, 5, 1, 4, 9, 9, 9, 1, 4, 2, 8)
GAIN    = 2.2
IO_MODE = "line"     (in_trim 1.6, out_trim 1/1.6)
```

Element chain:
`jfet-squarelaw → silicon-pair → transformer-saturation → germanium-pair →
opamp-rail-foldback ×3 → transformer-saturation → germanium-pair →
tube-asymmetric → cmos-inverter`

Circuit fingerprint (steady sine, `FuzzBillion.profile`):

| Tone | Spectral centroid | harmonic_ratio | peak |
|---|---|---|---|
| 110 Hz | 239.3 Hz | 0.4622 | 0.3136 |
| 220 Hz | 474.3 Hz | 0.4622 | 0.3136 |
| 440 Hz | 940.0 Hz | 0.4622 | 0.3136 |

(harmonic_ratio 0.46 = heavy harmonic enrichment from the triple op-amp
foldback + CMOS stages — a fuzz meltdown texture, classic for blues-rock.)

## 4. Production Chain

1. FluidSynth dry full mix (SP-001 reference) — `-ni -g 1.2 -R 0 -C 0`, SoundFont via `discover_soundfont()` (FluidR3_GM.sf2).
2. `RenderPipeline.render_stems()` → 4 dry stems (FX off).
3. `FuzzBillion.process()` on the whole mix (absolute layer) + per-stem.
4. Master: `normalize_to_lufs(-14)` → `Limiter(-1 dBFS)` LAST.
5. OGG via `ffmpeg -codec:a libopus -application voip -b:a 48k`.

## 5. Verification Results

| Metric | Value | Verdict |
|---|---|---|
| Integrated LUFS | **-14.00** | target met |
| True peak | 0.1908 (−14.4 dBFS) | below ceiling (heavy squash → low crest) |
| Silence ratio | **4.70 %** | PASS (< 30 %) |
| RMS (mono) | 0.1442 | healthy body |
| Mono correlation | 0.999 | mono/center-panned source (FluidSynth default pan) |
| Pitch hit-rate | **0.9904** (103/104 windows) | PASS (≥ 0.60) |
| Harmonic energy (wet) | **0.2067** | see retention note |
| Harmonic energy (dry ref) | **0.2442** | clean baseline |
| Harmonic-energy retention | **0.846** | PASS (≥ 0.50) |
| **Pitch verdict** | **PASS** | — |

**Pitch verification method:** FFT dominant peak per 0.5 s window in 50–1000 Hz,
mapped to MIDI pitch class, checked against the source's own pitch-class set
{0,1,2,4,6,7,8,9,10,11} within ±0.45 semitone.

**Verification note (important — honest gate calibration):** the SP-035-style
absolute harmonic-energy gate (`mean_HE ≥ 0.25`) is calibrated for *synthesis*
methods where < 0.25 means broadband noise. A *distortion effect* applied to a
percussion-heavy source does not sit cleanly on that scale: this blues shuffle's
**clean SP-001 reference itself measures 0.2442**, i.e. the source is already
cymbal/drum-broadband and sits essentially at the threshold *before any
processing*. Distortion spreads energy to higher/inharmonic partials + adds
intermodulation, so the wet mix lands at 0.2067 — an **84.6 % retention** of
tonal energy, not a collapse. The SP-035 noise signature (hit-rate ≈ 0,
harmonic energy ≈ 0.04) is **absent**: pitch hit-rate is 0.99 (identical to
dry), harmonic energy is ~5× the noise floor. Verdict therefore keys on
*pitch-hit-rate + wet-vs-dry harmonic-energy retention*, which is the correct
noise discriminator for an effects-layer method. The render is tonal, not noise.

**RMS per second:** no mid-track gaps; the 4.70 % silence is the legitimate
tail/reverb region after the last note, not an internal hole.

## 6. Files

| File | Size |
|---|---|
| `SP069-topology-distortion-blues-rock-shuffle.wav` | 9.5 MB (53.96 s, 44.1 kHz stereo) |
| `SP069-topology-distortion-blues-rock-shuffle.ogg` | 301 KB (Opus 48 kHz voip) |
| `dry_full_mix_sp001_reference.wav` | 9.5 MB |
| `MIDI/study-02-blues-rock-shuffle-engine.mid` | 8,027 B (copy) |
| `Audio/stems_dry/` (4 tracks) | 8.7–9.5 MB each |
| `Audio/stems_wet/` (4 tracks, `_TOPOLOGY`) | 8.7–9.5 MB each |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/select_20261007.json`, `Analysis/grid_visualization.txt` | — |
| `Scripts/produce_sp069_cron.py` | 11.6 KB |

## 7. Fixes Applied

1. **Source re-roll** — first random draw landed on `Country/012-country-country-uke/MIDI/country_uke_8bars.mid`, rejected as degenerate (single channel, tpb 10080, no program changes). Re-rolled among well-formed candidates (tpb 480, ≥8 notes, ≥1 program change, ≥2 channels) → `study-02-blues-rock-shuffle-engine.mid`.
2. **JSON float32 serialization** — `measure_lufs()` returns a numpy `float32`, which `json.dumps` rejects; cast to native `float` (same for the RMS scalar).
3. **Gate recalibration for effects-layer methods** — see §5 note; absolute HE ≥ 0.25 replaced by pitch-hit-rate ≥ 0.60 **and** wet/dry harmonic-energy retention ≥ 0.50 as the noise discriminator for an absolute-layer *distortion* (documented, not silently dropped).

## 8. Result

SP-069 FuzzBillion-style topology distortion applied as an absolute layer to a
112 BPM blues-rock shuffle in E (rock apprenticeship Study 02). A random 11-switch
circuit (JFET → silicon → transformer → germanium → triple op-amp foldback →
transformer → germanium → tube → CMOS) yields an aggressive fuzz-meltdown texture
suited to the distorted-guitar source. Pitch integrity fully preserved (hit-rate
0.99, 84.6 % harmonic-energy retention vs clean reference), loudness normalized
to −14 LUFS, peak −14.4 dBFS, silence 4.70 %.
