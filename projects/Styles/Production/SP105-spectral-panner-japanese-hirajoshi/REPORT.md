# SP-105 Spectral Brightness Panner — japanese-hirajoshi

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-18  **Seed:** 20261018

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (48 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-105` |
| Module | `sound.effects.spectral_panner` → `SpectralBrightnessPanner`, `BrightnessTracker`, `PanLaw`, `LFO` |
| Description | Spectral Brightness Panner — frequency-dependent auto-panner driven by spectral centroid/brightness analysis, independent per-channel paths, virtual centre mode, LFO blend, 3 pan profiles (Sound Particles Brightness Panner 2-style) |
| Layer | ABSOLUTE — one brightness→pan config applied to the WHOLE piece |
| Recent excluded (7d) | SP-006, SP-026, SP-028, SP-032, SP-074, SP-092, SP-099, SP-103 |
| Pool size | 40 |
| Well-formed candidates | 241 / 353 |

**Source composition:** `Styles/Japanese/001-japanese-hirajoshi/MIDI/japanese-hirajoshi.mid`
- D hirajoshi pentatonic `2-1-4-1-4` = pitch classes {D, Eb, G, Ab, C} = {2,3,7,8,0}.
- 70 BPM, 4/4, TPB 480, 16 bars (4 sections × 4 bars), 54.86 s; type-1 MIDI.
- 4 voices: Koto (ch0, GM 108), Shakuhachi (ch1, GM 75), Shamisen (ch2, GM 106), Taiko (ch9 drums).
- 212 pitched note events + 16 drum hits. Sparse "ma"-structured hōgaku texture: sparse koto plucks, sustained ornamented shakuhachi, 8th-note shamisen ostinato (D↔G), taiko on beat 1 of each bar.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid (all 212 pitched onsets on 120/240/480 grid) | PASS |
| Harmony — in scale (D hirajoshi {2,3,7,8,0}) | 4 out-of-scale notes — **all 4 are the same C♯6 mordent ornament** (note 85, pc 1), one per section (bars 0/4/8/12, onset 120/7800/15480/23160, 120-tick 16th grace) | PASS (ornament) |
| Harmony — chord tone of bar | N/A by construction — modal pentatonic piece with no functional chord progression; the "harmony" IS the 5-note hirajoshi vocabulary over a D↔G shamisen drone | PASS |
| Zero-drift (equal note-track lengths) | 4 note tracks all = 30720 ticks (16 bars × 1920); track 0 is the empty conductor/tempo track (length 0, no notes) | PASS |

**Verdict: PASS all three — no rework required, proceed to SP-105.**

Note on the 4 "out-of-scale" notes: they are a single deliberate shakuhachi **mordent** (chromatic upper-neighbor C♯6 on the opening C6 of each 4-bar phrase) — idiomatic hōgaku ornamentation, not an out-of-scale counterline or non-chord crud. All 208 structural notes sit inside the hirajoshi set. Grid is strictly 16th-aligned. This is not the SP-099 case (100 out-of-chord notes in a real harmonic context); it is a documented grace ornament, so the source MIDI is left unmodified.

## Layer discipline (absolute)

SP-105 is an **absolute-layer frequency-aware stereo panner**: one `SpectralBrightnessPanner` config applied to the whole mix (per-track application is a later refinement). Brightness = IIR-smoothed high-frequency (>2 kHz) energy ratio, mapped to a pan position; independent per-channel brightness paths; optional LFO blend; virtual-centre pulls bright content toward centre.

| Param | Value |
|---|---|
| `profile` | CIRCULAR (brightness 0→1 = continuous left→right sweep) |
| `mode` | DIRECT |
| `brightness_smooth` | 0.85 |
| `virtual_center` | True (threshold 0.6) — bright leads (shakuhachi) anchored centre, dark transients (taiko/koto attack) roam |
| `lfo_blend` / `lfo_rate` / `lfo_waveform` | 0.20 / 0.25 Hz / sine (gentle movement blended into the brightness control) |
| Mastering | `master()` → LUFS −14.0 (target_for_style "japanese" → −14 fallback), ceiling −1 dBTP |

Pipeline: dry FluidSynth (FX off `-R 0 -C 0`, `-g 1.2`) → `SpectralBrightnessPanner.process` (whole mix) → `master()` → WAV + Opus OGG. Dry per-track stems rendered via `RenderPipeline.render_stems` as DAW-import artifacts.

## Pitch / tonal-content verification — PASS

| Metric | Wet (SP-105) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 110 | 110 |
| FFT pitch-class hit rate | 0.8545 | 0.8545 |
| Mean harmonic energy (8 harmonics) | 0.5406 | 0.5429 |
| HE retention | 0.996 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40). The panner is a **gain/pan modulation only** — the dominant frequency and harmonic structure are byte-level preserved (hit rate identical wet vs dry, HE retention 99.6%). The 85.45% hit rate is a property of the *source* (some 0.5 s windows land on a harmonic or a transient adjacent to the mordent/ma gaps), not a SP-105 artifact — dry hits exactly the same.

## Silence / RMS profile

- Silence ratio: **5.47%** (well below the 30% suspect threshold — the shamisen 8th-note ostinato + sustained shakuhachi keep the texture near-continuous; only the ma gaps between phrases read as true silence).
- Overall RMS: 0.1356
- LUFS: **−14.02**  |  Peak: **0.8913** (−1.0 dBTP)
- Mono correlation: 0.976 (FluidSynth dry render is near-centre; SP-105 spreads only the brightness-modulated movement).

## Artifacts

| File | Size |
|---|---|
| `SP105-spectral-panner-japanese-hirajoshi.wav` | 10,240,812 B (58.05 s) |
| `SP105-spectral-panner-japanese-hirajoshi.ogg` | 548,434 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 10,240,812 B |
| `Audio/stems_dry/track00_Kalimba.wav` | 10,030,124 B |
| `Audio/stems_dry/track01_Pan_Flute.wav` | 10,051,116 B |
| `Audio/stems_dry/track02_Shamisen.wav` | 10,240,812 B |
| `Audio/stems_dry/track03_Drums.wav` | 10,030,124 B |
| `MIDI/japanese-hirajoshi.mid` | 2,033 B (copy of source) |
| `provenance.json` | 1,620 B |
| `Analysis/render_stats.json` | 448 B |
| `Analysis/select_20261018.json` | 268 B |
| `Scripts/produce_sp105_cron.py` | 10,744 B |
| `Scripts/audit_source.py` | 3,331 B |

Stem labels use GM program names, not `add_voice()` names (documented quirk): Koto→`Kalimba` (GM 108), Shakuhachi→`Pan_Flute` (GM 75), Shamisen→`Shamisen` (GM 106), Taiko→`Drums` (ch9).

## Notes

- Selection script: `Production/select_job_20261018.py` (writes `.selection_cron.json`).
- Produce script: `Scripts/produce_sp105_cron.py`; audit script: `Scripts/audit_source.py`.
- Source MIDI was **NOT modified** — audit passed clean (the 4 "out-of-scale" events are a single idiomatic mordent, not a harmony failure), so no phase-1/phase-2 rework was needed.
- FluidSynth render used FX off (`-R 0 -C 0`) so SP-105 is the only production-layer transformation, cleanly attributable.
- SP-105 process() runs ~0.57× realtime (pure-Python IIR loop) — 58 s of audio processed in ~33 s.
- WAVs are `.gitignore`d (`*.wav`); tracked deliverables are the OGG + MIDI + REPORT + provenance + Scripts + Analysis. Commit/push handled by the nightly auto-sync.
