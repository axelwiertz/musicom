# SP-070 Morphing Five-Character Resonant Filter — 091-baroque-genetic-allemande

**Date (UTC):** 2026-09-27 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP070-morph-filter-baroque-genetic-allemande/`
**Status:** PASS — pitch hit-rate 0.9127, harmonic energy 0.3884, silence 4.31%, LUFS -14.01, peak 0.8913.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-070** — Morphing Five-Character Resonant Filter (ZERO9 Fusion Filter-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.effects.morph_filter` → `FusionFilter`, `CHARACTERS`, `filter_character` |
| Registry entries at pick time | **34 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–092 |
| Already used last 7d (excluded) | SP-024 (09-26), SP-032 (09-25), SP-011 (09-24), SP-069 (09-23), SP-090 (09-22), SP-033 (09-21), SP-080 (09-20) |
| Eligible pool | **26 implemented methods** |
| Selection | `random.choice(sorted(pool))` → **SP-070** (first SP-070 run in current cycle) |
| MIDI pool | 203 usable candidates (excl. `Production`, `phase1`); seeded pick → `Styles/Baroque/091-baroque-genetic-allemande/MIDI/091-baroque-genetic-allemande.mid` |

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Baroque/091-baroque-genetic-allemande/` (genetic genome selection + tonal-network walk, musicom rules post-processing) |
| MIDI | `091-baroque-genetic-allemande.mid` (copied to output `MIDI/`; 11,058 B) |
| Key / mode | **D aeolian (Dm)** with harmonic-minor raised 7th (C#) on the dominant |
| Tempo / grid | 92 BPM, tpb 480; 62.61 s musical (65.28 s incl. tail), 46,080 ticks (24 bars: 6 sections × 4 bars) |
| Form | Intro / AllemandeA / AllemandeB / Lift / AllemandeA2 / Outro |
| Voices | Violin (lead) · Oboe (counterline) · Cello (pad) · Bright Acoustic Piano (continuo 16ths) · Viola (inner) · Contrabass (walking) · Drums (ch9) |
| Texture | 7-voice baroque allemande, 1,349 note-ons, 0 off-grid / 0 out-of-scale (per source audit) |
| Why this source | A dense, harmonically clean court-dance texture is ideal for a resonant-filter character pass: the morph filter adds warm even-harmonic saturation + 2-pole clarity without disturbing the continuo pulse or walking bass. |

## 3. Layer Discipline (Absolute)

SP-070 is an **absolute-layer** morphing resonant filter. A single `FusionFilter`
character is applied across the WHOLE mix (per-track application is a later
refinement). Five engine topologies — `ladder` (4-pole tanh), `diode`
(asymmetric even-harmonic saturator), `svf` (ZDF 2-pole), `comb` (resonant
comb), `scream` (driven ladder + wavefolder) — share one cutoff / resonance /
drive / mix control; a continuous `position` 0..4 equal-power-crossfades the
two adjacent characters.

```
091-baroque-genetic-allemande.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (11.52 MB)
 -> dry stems (RenderPipeline, FX off): 7 stems (Violin/Oboe/Cello/Piano/Viola/Contrabass/Drums)
 -> SP-070 absolute morph filter (same params on full mix + each stem):
      cutoff=3600 Hz, resonance=0.5, position=1.5, drive=1.4, mix=0.6
      position 1.5 -> equal-power blend {diode: 0.7071, svf: 0.7071}
 -> AlgorithmicReverb (baroque hall, room 0.55, wet 0.14)
 -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
 -> SP070-morph-filter-baroque-genetic-allemande.wav + .ogg (Opus 48k voip)
```

### Why position=1.5 (diode ⊗ svf)

- **diode** asymmetric saturator (`x - 0.35·x²` before tanh) → warm even-order
  harmonic colour, tube-like, ideal for strings/continuo.
- **svf** clean 2-pole → preserves the high baroque woodwind/string clarity.
- The 50/50 equal-power morph is the method's signature: one continuous
  character knob, not a hard filter-switch. cutoff 3600 Hz keeps the upper
  partials while shaving edginess; drive 1.4 adds gentle saturation; mix 0.6
  keeps 40% of the dry attack for articulation clarity.

## 4. Pitch / Tonal-Content Verification — **PASS**

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| FFT hit-rate (0.5 s windows, 50–1000 Hz, ±0.45 semitone, Dm pcs {0,1,2,4,5,7,9,10}) | **0.9127** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.3884** | ≥ 0.25 | PASS |
| Valid pitched windows | **126 / 126 (100%)** | > 50% | PASS |
| Median dominant peak | 170.0 Hz | — | Low-mid (walking bass / cello region) |
| LUFS / peak | -14.01 / 0.8913 | — | Limiter ceiling enforced |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**.
Resonant-filter character pass preserves the D aeolian tonal gravity fully
(harmonic ratio 0.3884 well above the noise floor of single digits).

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **4.31%** | Tail padding only; no mid-track gaps |
| Peak / LUFS | **0.8913 / -14.01 LUFS** | Limiter(-1 dBFS) ceiling enforced |
| RMS map | 0.07–0.18 active, ~0.0003 at final tail | Continuous baroque flow across all 6 sections |
| Duration | 65.28 s | 62.61 s musical + reverb tail |

## 6. Fixes & Discoveries During Run

1. **Final self-copy no-op**: the script lives in `Scripts/` already, so the
   trailing `shutil.copy2(__file__, ...)` raised `SameFileError` — cosmetic,
   after all artifacts + provenance were written; no data loss. Noted for
   future cron scripts (skip self-copy when `__file__` already under Scripts/).
2. **Per-sample Python loop cost**: the ladder/diode engines are per-sample
   Python loops; the full-mix morph (2.76 M samples/ch × 2 engines) took
   ~34.6 s. Acceptable for a 65 s piece; would matter for longer sources.
3. **Stereo discipline**: `FusionFilter.process()` is mono — processed each
   channel independently (same params) to preserve the dry stereo field.

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `SP070-morph-filter-baroque-genetic-allemande.wav` | 11,515,692 B |
| Master OGG | `SP070-morph-filter-baroque-genetic-allemande.ogg` | 442,279 B |
| Dry Reference | `dry_full_mix_sp001_reference.wav` | 11,515,692 B |
| Source MIDI | `MIDI/091-baroque-genetic-allemande.mid` | 11,058 B |
| Dry Stems | `Audio/stems_dry/` (7 stems) | ~80.6 MB total |
| Wet Stems | `Audio/stems_wet/` (7 × `*_MORPH.wav`) | ~80.6 MB total |
| Script | `Scripts/produce_sp070_cron.py` | 12.3 KB |
| Provenance | `provenance.json` | 1.1 KB |
| Stats | `Analysis/render_stats.json`, `Analysis/pitch_verification.json`, `Analysis/grid_visualization.txt` | — |
| Report | `REPORT.md` | this file |
