# SP-111 Odd1 Microsonic Granular Engine — bossa-nova-daily

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-20  **Seed:** 20261020

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (54 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-111` |
| Module | `sound.synthesis.odd1_engine` → `Odd1Microsonic`, `Playhead`, `RollingBuffer` |
| Description | Multi-Playhead Microsonic Granular Engine — 2 layers × 4 playheads with TIME PATH (forward/backward/freeze), independent pitch/speed, grain spacing/size morph, per-grain frequency-selective filter; SYNTH/LIVE (60s rolling buffer)/LOOPS (phase-locked independent loops) modes (Oddment ODD-1-style) |
| Layer | ABSOLUTE — the WHOLE dry mix is fed as one granular source buffer; one engine config applied to the whole piece |
| Recent excluded (7d) | SP-006, SP-028, SP-032, SP-092, SP-099, SP-103, SP-105 |
| Already on source | SP-098 (bossa-nova-daily already had a fractal-seq pass) |
| Baseline excluded | SP-001 |
| Pool size | 46 |
| Well-formed candidates | 245 / 357 |

**Source composition:** `Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid`
- A minor, **84 BPM**, 4/4, TPB 480, **2 bars** (3840 ticks = 5.714 s); type-1 MIDI.
- Harmony is a single **Am7** (A–C–E–G, pitch classes {9, 0, 4, 7}) over an **A** bass — the whole piece is one chord, so every instant contains only A/C/E/G.
- 44 pitched notes (8 bass + 36 harmony) + 25 drum hits (16 shaker 8ths + 9 rimshot clave).
- Voices: Bass (ch0, note 33 = A1), Harmony (ch1, Am7 = 57/60/64/67, bossa clave onsets), Percussion (ch9).
- **Quirk:** the original generator assigned **no `program_change`**, so FluidSynth plays channels 0/1 with the default Grand Piano (program 0) — the "bass" and "harmony" both sound as piano. Stem labels reflect this (`track00_Acoustic_Grand_Piano`, `track01_Acoustic_Grand_Piano`). Documented, not fixed (source preserved).

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid (all 44 pitched onsets on 120/240/480 grid) | PASS |
| Harmony — in scale (A natural minor {9,11,0,2,4,5,7}) | 0 out-of-scale | PASS |
| Harmony — chord tone (Am7 {9,0,4,7}) | 0 out-of-chord | PASS |
| Zero-drift (note tracks equal length) | [3840, 3720, 3660] — **NOT equal** | **CHECK → reworked** |

**Zero-drift finding + rework.** The source is a raw-`mido` "daily pattern" file (pre-`UnitMatrixComposer`). Onsets are all correctly placed absolute ticks (no drift/desync — grid + harmony both clean), but the three note tracks end at different ticks because the **final note durations differ by design** (bass rings 240 ticks, harmony 120, percussion 60). The strict "all note tracks equal length" gate reads NOT equal.

**Fix** (`rework_zerodrift_20261020.py`): pad each note track's `end_of_track` delta so every track spans exactly **3840 ticks** (2 bars × 1920) — the musicom terminal-landmark convention. **No note moved, no duration changed, audio byte-identical** to the source render. Written to `MIDI/composition.mid` in the production folder (source is never overwritten; `MIDI/source_original.mid` is a byte copy).

**Re-audit after rework:** note-track lengths `[3840, 3840, 3840]` → **zero-drift PASS**. Off-grid 0, out-of-scale 0, out-of-chord 0.

## Layer discipline (absolute)

SP-111 is an **absolute-layer granular engine**: the dry FluidSynth mix (FX off) is the single source buffer; `Odd1Microsonic` re-granulates the whole mix with 2 layers × 4 playheads. Per-track application is a later refinement.

Pipeline: dry FluidSynth (`-R 0 -C 0`, `-g 1.2`) → **trim 8.81 s → 6.2 s** (release tail) → `Odd1Microsonic.render` (whole mix, forward time path, mono L + R via two seeds) → `master()` → WAV + Opus OGG. Dry per-track stems via `RenderPipeline.render_stems` as DAW-import artifacts.

| Param | Value |
|---|---|
| `mode` / `time_path` | synth / forward |
| `grain_spacing_ms` | 40 (hop = 1764 samples @ 44.1 kHz) |
| playhead `speed` | 1764 (= hop → 1:1 forward read; NOT the default 1.0 which would freeze-read) |
| 8 playheads (layer, head, pitch_st, grain_ms, filter) | L0: (0, 80, 1.0) (0, 80, 0.7) (−12, 50, 0.6) (+12, 100, 0.4) · L1: (0, 40, 0.8) (0, 120, 0.5) (−12, 60, 0.55) (+12, 90, 0.4) |
| pitch_st range | {0, ±12} only → octave shimmer/sub, **pitch class preserved** (see engine quirk below) |
| stereo | two independent seeds (20261020, 20261021) → L and R |
| Mastering | `master()` → LUFS −14.0 (`target_for_style("bossa nova")`), ceiling −1 dBTP |

**Engine quirk (documented, not a bug in this job):** the grain read uses `src = arange(gsz) / 2**(pitch_st/12)`, so **positive `pitch_st` → pitch DOWN an octave** (inverted vs. musical convention). We use only 0 / ±12, which are octave-equivalent, so the pitch-class content is untouched and pitch verification is unaffected.

## Pitch / tonal-content verification — PASS

| Metric | Wet (SP-111) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 12 | 12 |
| FFT pitch-class hit rate | 0.8333 | 1.0000 |
| Mean harmonic energy (8 harmonics) | 0.3745 | 0.2425 |
| HE retention | 1.544 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40). The granular engine **raises** harmonic energy (0.24 → 0.37, retention 1.54) because overlap-add sustaining converts the short piano plucks into a sustained tonal field — the classic granular "bloom". 10/12 windows' dominant pitch is an Am7 chord tone; the 2 misses are transient smeared windows (not noise — harmonic energy stays well above the 30% noise floor). No 0-Hz frames, no noise signature.

## Silence / RMS profile

- Silence ratio: **8.86%** (clean — after trimming the FluidSynth release tail; pre-trim it was 36.9%, confirmed tail-only via per-second RMS: sec 0–5 music, sec 6+ digital silence, **no mid-track gaps**).
- Overall RMS: 0.1060
- LUFS: **−14.04**  |  Peak: **0.8913** (−1.0 dBTP)
- Mono correlation: **0.089** — the two independent-seed L/R renders are essentially uncorrelated granular clouds (the engine's binaural/decorrelated character). Mono-summed pitch content is intact (hit 0.83, HE 0.37).

## Artifacts

| File | Size |
|---|---|
| `SP111-odd1-granular-bossa-nova-daily.wav` | 1,093,724 B (6.2 s) |
| `SP111-odd1-granular-bossa-nova-daily.ogg` | 44,807 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 1,093,724 B (trimmed) |
| `Audio/stems_dry/track00_Acoustic_Grand_Piano.wav` | 1,467,436 B |
| `Audio/stems_dry/track01_Acoustic_Grand_Piano.wav` | 1,418,028 B |
| `Audio/stems_dry/track02_Drums.wav` | 1,554,988 B |
| `MIDI/composition.mid` (zero-drift normalized) | 587 B |
| `MIDI/source_original.mid` (byte copy) | 586 B |
| `provenance.json` | 2,685 B |
| `Analysis/render_stats.json`, `Analysis/select_20261020.json` | — |
| `Scripts/produce_sp111_cron.py` / `audit_source_20261020.py` / `rework_zerodrift_20261020.py` | 12,562 / 3,367 / 2,564 B |

Stem labels use GM program names (not `add_voice()` names) — here both pitched tracks are `Acoustic_Grand_Piano` because the source never set a program change (default program 0).

## Notes

- Selection script: `Production/select_job_20261020.py` (writes `.selection_cron.json`).
- Audit: `Scripts/audit_source_20261020.py`; rework: `Scripts/rework_zerodrift_20261020.py`; produce: `Scripts/produce_sp111_cron.py`.
- **Source MIDI was NOT modified in place** — the only rework was the zero-drift tail padding into the production folder's `MIDI/composition.mid` (no note/duration change).
- `master()` landed at −14.04 LUFS (target −14) with peak at the −1 dBTP ceiling — correct ceiling behaviour.
- FluidSynth raw render ran to 8.81 s (low piano note release tail); trimmed to 6.2 s so the deliverable has no dead air. Stems are intentionally left full-length (time-aligned DAW artifacts).
- WAVs are `.gitignore`d; tracked deliverables = OGG + MIDI + REPORT + provenance + Scripts + Analysis. Commit/push handled by the nightly auto-sync.
