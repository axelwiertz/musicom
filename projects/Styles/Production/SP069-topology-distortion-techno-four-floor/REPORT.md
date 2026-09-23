# REPORT — SP-069 Topology Distortion × 001-techno-four-floor

**Job:** random-style production (SP) layer-aligned
**Date:** 2026-09-23
**Seed:** 20260923

---

## 1. Method + selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (the implemented method registry) — **not** methods_db.md (spec-only) |
| Chosen method | **SP-069** — `sound.effects.topology_distortion` |
| Description | Switched Discrete Distortion Topology Bank (Teaching Machines FuzzBillion-style) |
| Layer | **ABSOLUTE layer** — single master circuit applied uniformly across the whole piece |
| Pool size | 32 registered methods (SP-001 … SP-091) |
| Recent exclusions (last 7 days) | SP-090, SP-033, SP-080, SP-083, SP-084, SP-072 |
| RNG | `random.Random(20260923)` |

The method is a bank of **11 serial nonlinear stages**, each a 10-position switch
(0 bypass, 1 transformer-saturation, 2 tube-asymmetric, 3 JFET square-law,
4 germanium-pair, 5 silicon-pair, 6 single-diode clamp, 7 LED-pair,
8 CMOS hard clip, 9 op-amp rail foldback). Total `10**11` distinct circuits.
Each antiparallel diode pair uses `y = Vk * asinh(x/Vk)` with exact knee
voltages (Ge 0.30 V, Si 0.65 V, LED 1.80 V).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Techno/001-techno-four-floor` |
| MIDI | `MIDI/techno-four-floor.mid` |
| Genre | Techno four-on-the-floor |
| Tempo | 132 BPM |
| Length | 29.1 s (7 tracks, 168 notes, tpb 480) |
| Voices | Drums (ch9, ×3 tracks), Electric Bass finger (33), String Ensemble 2 (49), Lead 1 square (80) |
| Pitch classes | Bb(10) dominant bass pedal, C(0), A(9), plus D(2)/Eb(3)/E(4) passing tones |
| Lowest/highest note | 33 (A1) / 76 (E5) |

**Note (fix 1):** first random source draw landed on
`Country/012-country-country-uke/MIDI/country_uke_8bars.mid` — rejected as
degenerate (single track, 128 notes, tpb 10080, no program changes). Re-rolled
among the 57 projects carrying a `compose.py` + a `MIDI/*.mid` main file, taking
the first well-formed candidate (≥8 notes, sane tpb).

## 3. Circuit + parameters

**Master circuit ("vintage console overdrive")** — 11 switches, signal order
left → right:

```
CIRCUIT = (1, 2, 4, 5, 3, 1, 4, 5, 8, 1, 4)
GAIN    = 2.4
IO_MODE = "line"     (in_trim 1.6, out_trim 1/1.6)
```

Element chain:
`transformer-saturation → tube-asymmetric → germanium-pair → silicon-pair →
jfet-squarelaw → transformer-saturation → germanium-pair → silicon-pair →
cmos-inverter → transformer-saturation → germanium-pair`

Profile on steady sine (harmonic fingerprint):

| Tone | Spectral centroid | harmonic_ratio | peak |
|---|---|---|---|
| 110 Hz | 367.7 Hz | 0.822 | 0.180 |
| 220 Hz | 735.4 Hz | 0.822 | 0.180 |

(harmonic_ratio 0.82 = heavy harmonic enrichment, exactly the expected
signature of a distortion bank.)

**Same circuit applied per-stem** (6 dry stems → 6 wet stems) with the
identical code/gain/io-mode for DAW import. Note: distortion is nonlinear, so
`Σ distort(stem_i) ≠ distort(Σ stem_i)` — the primary output is the
whole-piece (full-mix) distortion per the absolute-layer discipline; the wet
stems are a convenience copy of the same circuit per voice.

## 4. Production chain

1. FluidSynth dry full mix (SP-001 reference) — `-ni -g 1.2 -R 0 -C 0`, SoundFont via `discover_soundfont()` (FluidR3_GM.sf2).
2. `RenderPipeline.render_stems()` → 6 dry stems.
3. `FuzzBillion.process()` (whole mix) + per-stem.
4. Master: `normalize_to_lufs(-14)` → `Limiter(-1 dBFS)`.
5. OGG via `ffmpeg -codec:a libopus -application voip -b:a 48k`.

## 5. Verification results

| Metric | Value | Verdict |
|---|---|---|
| Integrated LUFS | **-14.00** | target met |
| True peak | 0.236 (-12.5 dBFS) | below ceiling (heavy squash → low crest) |
| Silence ratio | **14.58 %** | OK (< 30 %), tail padding |
| Mono correlation | 0.111 | very wide stereo image (synth pans) |
| Pitch hit-rate | **1.000** (63/63 windows) | PASS |
| Mean harmonic energy | **0.331** | PASS (≥ 0.25) |
| **Pitch verdict** | **PASS** | — |

**Pitch verification method:** FFT dominant peak per 0.5 s window in 50–1000 Hz,
mapped to MIDI pitch class, checked against source pitch classes
{0, 2, 3, 4, 9, 10} within ±0.5 semitone. Harmonic energy = energy in first 8
harmonics of the dominant fundamental ÷ total energy (high = tonal
concentration, low = broadband noise). Both metrics far above the FAIL floor,
so the render is tonal — not noise.

**RMS per second (body, first 29 s):** steady 0.092–0.141, no mid-track gaps.
Tail decays cleanly at ~29 s (0.069 → 0.013 → ~0) — the 14.58 % silence is the
legitimate reverb tail after the last note, not an internal hole.

## 6. Files

| File | Size |
|---|---|
| `SP069-topology-distortion-techno-four-floor.wav` | 6.4 MB (36.29 s, 44.1 kHz stereo) |
| `SP069-topology-distortion-techno-four-floor.ogg` | 214 KB (36.30 s, Opus 48 kHz stereo) |
| `dry_full_mix_sp001_reference.wav` | 6.2 MB |
| `MIDI/techno-four-floor.mid` | 1.6 KB (copy) |
| `Audio/stems_dry/` (6 tracks) | 5.3–6.2 MB each |
| `Audio/stems_wet/` (6 tracks, `_TOPOLOGY`) | 5.3–6.2 MB each |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/select_20260923.json` | — |
| `Scripts/produce_sp069_cron.py` | 12 KB |

## 7. Fixes applied

1. **Source re-roll** — `country_uke_8bars.mid` degenerate (single track, tpb 10080, no programs) → re-rolled to `techno-four-floor.mid`.
2. **Script self-copy guard** — `shutil.copy2(__file__, …)` raised `SameFileError` (script already authored in-place under `Scripts/`); wrapped in a same-file guard.

## 8. Result

SP-069 FuzzBillion-style topology distortion applied as an absolute layer to a
132 BPM techno four-on-the-floor track. Warm transformer/tube/germanium
saturation with a mid-chain silicon and CMOS hard-clip stage produces an
overdriven, wide, squashed techno texture. Pitch integrity verified (hit-rate
100 %, harmonic energy 0.33), loudness normalized to −14 LUFS.
