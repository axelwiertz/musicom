# SP-146 Feedback-Loop Echo + Codec Loss — 076-reggae-lsystem

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date (UTC):** 2026-11-17  **Seed:** 20261117
**Status:** PASS — FFT hit 0.9587, harmonic energy 0.5824 (≥ 0.30), silence 7.27%
(all in tail), LUFS −14.00, true peak −1.00 dBTP. PRE-FLIGHT harmony gate
**failed on the source** (115 out-of-chord notes) → per-bar chord rework applied
→ re-audit clean (0/0/0) → effect applied to the reworked composition.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-146** — Feedback-Loop Echo + Codec Loss: fractional delay whose wobble (wow/flutter/drift), tanh drive, tone band-limiting, all-pass smear and bitrate-derived bit-depth/bandwidth reduction run **inside the feedback path**, plus offline spectral codec (log-magnitude quantisation + band limit) (XLN Audio RC-20 V2 Echo/Loss-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.effects.feedback_loop_fx` → `FeedbackLoopFX` (`process(x)`), `spectral_codec` |
| Registry entries at pick time | 97 |
| Recent excluded (7d) | SP-069, SP-075, SP-084, SP-100, SP-115, SP-138, SP-154 |
| Already on this source | SP-026 |
| Baseline excluded | SP-001 |
| Eligible pool | 88 methods |

Selection record: `Production/.selection_cron.json`,
`Production/select_job_20261117.py`. Well-formed filter: **357 / 462** candidate
MIDIs passed (normal tpb, sane note lengths, ≥2 note tracks or a program change,
2–600 s length); 356 with ≥3 pitch classes.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Reggae/076-reggae-lsystem/` (Method 019 L-System, Fibonacci word) |
| MIDI | `MIDI/076-reggae-lsystem.mid` (Phase-2, rules-processed) |
| Genre / key | Reggae one-drop; **A aeolian** (A B C D E F G) |
| Tempo | 96 BPM, 480 tpb, 4/4, type-1 |
| Length | 60.00 s = 24 bars = 46080 ticks (6 sections × 4 bars) |
| Harmony | i – bVII – i – bVI (Am – G – Am – F), one chord per bar |
| Voices | Lead organ (prog 17, ch0), Skank guitar (prog 27, ch1), Bass (prog 33, ch2), one-drop drums (ch9) |

## 3. PRE-FLIGHT AUDIT (3-rule gate) — FAILED on source, then reworked

### Source MIDI (before rework)

| Rule | Count | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | **0** off-grid | PASS |
| Harmony — in scale (A aeolian) | **0** out-of-scale | PASS |
| Harmony — chord tone of its bar | **115** out-of-chord | **FAIL** |
| Zero-drift (all tracks = 46080) | [46080 ×4] | PASS |

Root cause: the Phase-2 build quantized the **Lead organ** (35 notes) and
**Skank guitar** (80 notes) to the *section's first-bar* triad (one chord per
4-bar section), while the bass and the harmonic bed move **per bar**
(i–bVII–i–bVI). In bars whose chord differs from the section chord, the lead and
skank play the previous chord's tones (e.g. E4 over a G-major bar) → out-of-chord.
Bass is already per-bar correct (0 out-of-chord); drums are percussion (exempt).

### Rework (per-bar chord-tone quantization, canonical engine)

`Scripts/rework_076_perbar.py` re-runs the source `compose.py` logic (reused as a
module) with one change: Lead and Skank are quantized to the **per-bar**
voice-leading-corrected triad (`corrected_triads[bar]`) instead of the section
triad. Triads are computed through `Scale7ChordDegree.get_diatonic_note()` (no
off-by-octave wrap). Rebuilt via `UnitMatrixComposer` → `validate()` PASS →
`to_midi`. Source project MIDI is **NOT** modified.

### Reworked MIDI (after rework — gate MUST be clean)

| Rule | Count (source) | Count (reworked) | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | 0 | **0** | PASS |
| Harmony — in scale (A aeolian) | 0 | **0** | PASS |
| Harmony — chord tone (bar chord) | 115 | **0** | PASS |
| Zero-drift (all tracks = 46080) | equal | **equal [46080 ×4]** | PASS |

Final reworked MIDI: 504 pitched notes (120 lead / 240 skank / 144 bass), all
in A aeolian, all onsets on the 16th grid, all chord tones of their bar, all
four tracks exactly 46080 ticks.

## 4. SP-146 parameters (absolute layer, applied to the whole piece)

| Param | Value | Logic |
|---|---|---|
| delay_ms | **312.5** | eighth-note echo locked to 96 BPM (60/BPM/2) |
| feedback | 0.55 | moderate dub tail (clamped < 1.0, decaying) |
| mix | 0.35 | wet blend |
| wobble_cents / wobble_rate | 6.0 / 0.5 Hz | tape wow |
| flutter_rate | 6.3 Hz | tape flutter |
| drive | 0.12 | subtle tanh saturation (in-loop, per repeat) |
| tone_hz | 6000 | loop band-limiting ("Space" tonal stage) |
| smear | 0.15 | short all-pass diffuser per repeat |
| codec | **True** | in-loop bit-depth/bandwidth reduction |
| codec_bitrate | 96 kbps | generation-loss character per repeat |
| reverse | False | forward echo |

The offline `spectral_codec()` (whole-track codec mode) was **not** applied
separately — the in-loop `codec=True` path already exercises the RC-20
"Echo+Loss" generation-loss character; a whole-track codec pass would only
add blanket band-limiting. `FeedbackLoopFX.process()` runs per-channel (stereo),
sample-accurate, with gain compensation and final peak clamp.

## 5. Render + master

| Stage | Value |
|---|---|
| Carrier | FluidSynth CLI `-ni -g 1.2 -R 0 -C 0 -F`, **FluidR3_GM.sf2** (dry, FX off — clean carrier for the echo) |
| Effect | `FeedbackLoopFX(44100, **params).process(dry)` — stereo, peak 0.975 → 0.634 |
| Master | `master(target_lufs=-14.0, ceiling_db=-1.0, sample_rate=44100)` |
| Target LUFS | `target_for_style("Reggae")` → **−14.0** |
| Integrated LUFS | **−14.00** |
| True peak | **−1.00 dBTP** (at ceiling) |
| Peak / RMS | 0.8913 / 0.1445 |

Master stages (input → final): −17.94 (effected) → −17.95 highpass → −18.13 glue
→ −18.13 stereo → −14.00 lufs_norm → −14.00 true-peak limit.

## 6. Verification (pitch + silence + RMS)

| Metric | Dry carrier | Final (mastered) | Verdict |
|---|---|---|---|
| FFT dominant-pc hit rate (0.5 s windows, 50–1000 Hz, vs A-aeolian pcs) | 0.9587 (121) | **0.9587** (121) | PASS |
| Mean harmonic energy (first 8 harmonics of lowest fundamental) | 0.5816 | **0.5824** | PASS (≥ 0.30) |
| Silence ratio (`|mono| < 0.001`) | 7.30 % | **7.27 %** | tail/decay only |
| Zero-drift | [46080 ×4] | — | PASS |

Harmonic energy 0.5824 ≫ 0.30 confirms the render is **tonal, not noise** (the
2026-08-24 GENDYN failure mode: broadband noise = single-digit harmonic energy).
Per-second RMS profile: music 0–60 s at 0.13–0.18 RMS (continuous, no gaps), a
release tail at 61 s (0.009) → 62 s (0.0004), then digital silence 63–65 s.
**No mid-track silence** — the only zero-RMS seconds are the tail after the last
note.

## 7. Fixes applied

1. **Per-bar chord-tone quantization (Lead + Skank)** — the source quantized
   these voices to the section's first-bar chord; re-quantized to the per-bar
   voice-leading-corrected triad. 115 out-of-chord → **0**. No out-of-scale
   change (all chord tones ⊂ A aeolian). Grid and zero-drift untouched (were
   already clean). Bass and drums unchanged.

## 8. Artifacts

| File | Size | Role |
|---|---|---|
| `Audio/SP146-feedback-loop-fx-076-reggae-lsystem.ogg` | 522 447 B | Opus 48k voip (Telegram) |
| `Audio/SP146-feedback-loop-fx-076-reggae-lsystem.wav` | 11 468 844 B | mastered full mix (post-FX) |
| `Audio/076-reggae-lsystem-reworked-dry.wav` | 11 468 844 B | dry FluidSynth carrier (pre-FX reference) |
| `MIDI/076-reggae-lsystem-reworked.mid` | 6 422 B | reworked (per-bar chord-quantized), validate() PASS |
| `MIDI/076-reggae-lsystem-reworked.mid.provenance.json` | — | rework provenance |
| `Analysis/render_stats.json` | 3 515 B | LUFS/peak/silence/RMS/pitch + master stages |
| `Scripts/rework_076_perbar.py` | — | reproducible rework |
| `Scripts/produce_sp146.py` | — | reproducible producer (render → FX → master → OGG → verify) |
| `Scripts/audit.py` | — | 3-rule audit (source + reworked) |
| `provenance.json` | — | full production provenance sidecar |

Source reference (unmodified): `Styles/Reggae/076-reggae-lsystem/MIDI/076-reggae-lsystem.mid`.

---

*Report is the primary record. Chat summary is a short caveman digest.*
