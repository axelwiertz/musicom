# SP-111 Odd1 Microsonic Granular Engine — studio-grand-extended

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-11-01  **Seed:** 20261101

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (72 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-111` |
| Module | `sound.synthesis.odd1_engine` → `Odd1Microsonic`, `Playhead`, `RollingBuffer` |
| Description | Multi-Playhead Microsonic Granular Engine — 2 layers × 4 playheads with TIME PATH (forward/backward/freeze), independent pitch/speed, grain spacing/size morph, per-grain frequency-selective filter; SYNTH/LIVE (60s rolling buffer)/LOOPS (phase-locked independent loops) modes (Oddment ODD-1-style) |
| Layer | ABSOLUTE — the WHOLE dry mix is fed as one granular source buffer; one engine config applied to the whole piece |
| Recent excluded (7d) | SP-092, SP-094, SP-109, SP-115, SP-119, SP-127 (from Production/ dirs modified ≤ 7 days) |
| Pool size | 66 |
| Well-formed candidates | 257 (175 with `compose.py`; preferred pool = 175) |

**Source composition:** `Styles/Classical/studio_grand_extended/v1/studio_grand_extended.mid`
- **C major**, 110 BPM, 4/4, TPB 480, **32 bars** (61440 ticks = 69.82 s); type-1 MIDI, 7 tracks.
- 6 voices: Piano (ch0, GM 0), Strings (ch1, GM 49 → "String_Ensemble_2"), Bass (ch2, GM 33), Drums (ch9), Lead Flute (ch3, GM 74 → "Recorder"), Countermelody Flute (ch4, GM 74).
- Intended harmony: I–IV–V–vi progression (C / G / F / Am) across Intro(4) + V1(8) + Chorus(8) + V2(8) + Outro(4).

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid, 0 off-8th (all pitched onsets on 120/240 grid) | PASS |
| Harmony — in scale (C major {0,2,4,5,7,9,11}) | **18 out-of-scale** | **FAIL** |
| Harmony — chord tone (per-bar C/G/F/Am) | **422 out-of-chord** | **FAIL** |
| Zero-drift (note tracks equal length) | all 61440 ticks | PASS |

**Harmony finding + rework.** Two root causes, both in the source `compose.py`:

1. **Per-section chord collapse** — every `build_*(chords[0], …)` call used the FIRST chord of each 4-bar section for all 4 bars, so the intended I–IV–V–vi progression was never played (only C and F sounded). Fixed: pass `chords[bar]` per bar.
2. **Fixed-semitone lead melody** — the lead used `root + {0,+4,+2,+7,+5,+2,0,−2}` offsets, producing out-of-scale notes (root+10 → **B♭**, root+19 → **C♯**) and many non-chord tones. The countermelody colour cycle used scale tones (not chord tones). Fixed: lead + countermelody rebuilt as **chord-tone arpeggios only** (`LEAD_ARP`, `COLORS` — every note is a chord tone of its bar, all diatonic to C major).

**Fix** (`Scripts/rework_compose.py`): rewritten composer — per-bar chords + chord-tone lead/countermelody — re-exported `studio_grand_extended.mid` with a passing `validate()` gate + new provenance. Original raw MIDI preserved as `studio_grand_extended-phase1.mid` (byte copy of the pre-fix file). Also fixed the stale `ai.utils.visualizer` import → `visualization.grid`.

**Re-audit after rework:** off-grid 0, off-8th 0, out-of-scale **0**, out-of-chord **0**, zero-drift PASS (all tracks 61440). All three rules clean.

## Layer discipline (absolute)

SP-111 is an **absolute-layer granular engine**: the dry FluidSynth mix (FX off) is the single source buffer; `Odd1Microsonic` re-granulates the whole mix with 2 layers × 4 playheads. Per-track application is a later refinement.

Pipeline: dry FluidSynth (`-R 0 -C 0`, `-g 1.2`) → trim release tail (72.0 s → 69.5 s) → `Odd1Microsonic.render` (whole mix, forward time path, mono L + R via two seeds) → `master()` (LUFS −18, −1 dBTP) → WAV + Opus OGG. Dry per-track stems via `RenderPipeline.render_stems` as DAW-import artifacts.

| Param | Value |
|---|---|
| `mode` / `time_path` | synth / forward |
| `grain_spacing_ms` | 40 (hop = 1764 samples @ 44.1 kHz) |
| playhead `speed` | 1764 (= hop → 1:1 forward read) |
| 8 playheads (layer, head, pitch_st, grain_ms, filter) | L0: (0, 80, 1.0) (0, 80, 0.7) (−12, 50, 0.6) (+12, 100, 0.4) · L1: (0, 40, 0.8) (0, 120, 0.5) (−12, 60, 0.55) (+12, 90, 0.4) |
| pitch_st range | {0, ±12} only → octave shimmer/sub, **pitch class preserved** |
| stereo | two independent seeds (20261101, 20261102) → L and R |
| Mastering | `master()` → LUFS −18.0 (`target_for_style("classical")`), ceiling −1 dBTP |
| Trim | 69.50 s (last music second = 68; RMS map shows sec 0–68 music, sec 69+ digital silence → tail-only, no mid-track gaps) |

## Pitch / tonal-content verification — PASS

| Metric | Wet (SP-111) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 138 | 138 |
| FFT pitch-class hit rate | 1.0000 | 1.0000 |
| Mean harmonic energy (8 harmonics) | 0.3215 | 0.4645 |
| HE retention | 0.692 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 AND HE retention ≥ 0.40). Every valid window's dominant pitch is a C-major diatonic class (1.0 hit rate on both wet and dry). The granular engine lowers mean harmonic energy (0.46 → 0.32, retention 0.69) because the classical source is already sustained (piano + string pad), and granular overlap-add smears some harmonic structure — but 0.32 stays well above the 30% noise floor, no 0-Hz frames, no noise signature.

## Silence / RMS profile

- Silence ratio: **2.03%** (clean — after trimming the 3.5 s FluidSynth release tail; RMS map confirms tail-only, **no mid-track gaps**).
- Overall RMS: 0.0764
- LUFS: **−18.00**  |  Peak: **0.7064** (−3.02 dBTP)
- Mono correlation: **0.061** — the two independent-seed L/R renders are essentially uncorrelated granular clouds (the engine's decorrelated character). Mono-summed pitch content intact (hit 1.0, HE 0.32).

Note: −18 LUFS lands at −3.02 dBTP — correct ceiling behaviour (true-peak limit is a ceiling, not a target; a dynamic classical piece legitimately sits below −1 dBTP).

## Artifacts

| File | Size |
|---|---|
| `SP111-odd1-studio-grand-extended.wav` | 12,259,844 B (69.5 s) |
| `SP111-odd1-studio-grand-extended.ogg` | 430,463 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 12,259,844 B (trimmed) |
| `Audio/stems_dry/track00_Acoustic_Grand_Piano.wav` | 12,740,140 B |
| `Audio/stems_dry/track01_String_Ensemble_2.wav` | 13,272,876 B |
| `Audio/stems_dry/track02_Electric_Bass_finger.wav` | 12,669,228 B |
| `Audio/stems_dry/track03_Drums.wav` | 12,669,228 B |
| `Audio/stems_dry/track04_Recorder.wav` | 12,669,228 B |
| `Audio/stems_dry/track05_Recorder.wav` | 12,669,228 B |
| `MIDI/composition.mid` (reworked, rules-clean) | 9,670 B |
| `MIDI/source_original.mid` (byte copy of pre-fix) | 9,510 B |
| `provenance.json` | 2,611 B |
| `Analysis/render_stats.json`, `Analysis/grid_visualization.txt` | — |
| `Scripts/rework_compose.py` / `produce_sp111_cron.py` / `audit_source_20261101.py` / `compose_original.py` | — |

Source project (re-exported in place): `Styles/Classical/studio_grand_extended/v1/studio_grand_extended.mid` (9,670 B, rules-clean) + `studio_grand_extended-phase1.mid` (9,510 B, original raw draft).

Stem labels use GM program names (not `add_voice()` names): Piano→`Acoustic_Grand_Piano`, Strings(49)→`String_Ensemble_2`, Bass(33)→`Electric_Bass_finger`, Drums→`Drums`, Flute(74)→`Recorder` (both lead + countermelody).

## Notes

- Selection script: `Production/_cron_tmp/pick.py` (writes `selection.json`); audit: `Scripts/audit_source_20261101.py`.
- **Source MIDI was re-exported in place** (harmony gate FAIL required a real rework, not just tail padding); the original raw draft is preserved as `-phase1.mid`.
- `master()` landed at −18.00 LUFS (target −18) with peak −3.02 dBTP — correct ceiling behaviour (dynamic classical content below the −1 ceiling).
- FluidSynth raw render ran to ~72 s (piano release tail); trimmed to 69.5 s. Stems intentionally left full-length (time-aligned DAW artifacts).
- WAVs are `.gitignore`d; tracked deliverables = OGG + MIDI + REPORT + provenance + Scripts + Analysis. Commit/push handled by the nightly auto-sync.
