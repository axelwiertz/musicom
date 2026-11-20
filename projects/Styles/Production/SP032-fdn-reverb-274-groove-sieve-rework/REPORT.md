# REPORT — SP-032 FDN Reverb × 274-groove-sieve-rework

**Job:** random-style production (SP) — layer-aligned (2026-11-20)
**Method:** SP-032 — Feedback Delay Network Reverb (Rev Ocean "Tidal"-style)
**Source composition:** `Groove/274-groove-sieve-rework` (Method 025 Xenakis Sieve rework)
**Seed:** 20261120

---

## 1. Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (104 implemented entries) |
| Method | **SP-032** → `sound.effects.fdn_reverb` (`FDN` class) |
| Source MIDI (selected) | `Styles/Groove/274-groove-sieve-rework/MIDI/274-groove-sieve-rework-humanized.mid` |
| Render source | `Styles/Groove/274-groove-sieve-rework/MIDI/274-groove-sieve-rework-perfect.mid` (de-humanized rework) |
| Recent excluded (≤7 d) | SP-075, SP-084, SP-100, SP-107, SP-115, SP-146, SP-157 |
| Baseline excluded | SP-001 |
| Pool size | 96 |

## 2. Source composition

| Field | Value |
|---|---|
| Style / key | Groove — **G natural minor** (pcs {7,9,10,0,2,3,5}) |
| Origin | Method 025 Xenakis Sieve rework (from 080-groove-sieve) |
| BPM / meter / TPB | 110 · 4/4 · 480 TPB (16th = 120, bar = 1920) |
| Length | 32 bars / 8 sections (Intro·VerseA·VerseB·Chorus·Bridge·VerseC·Chorus2·Outro), ~69.8 s |
| Voices | Lead (Soprano Sax 65, ch0), Horns (Brass 61, ch1), Rhodes (EP 4, ch2), Bass (EB 33, ch3), Counter (Strings 48, ch4), Drums (ch9) |
| Chord path | i·VII·i·VII ‖ i·III·iv·v ‖ i·iv·v·VI ‖ III·VII·i·iv ‖ VI·III·VII·v ‖ i·III·iv·v ‖ III·VII·i·iv ‖ i·VI·VII·i |

## 3. Pre-flight — RULES ADHERENCE GATE

| Rule | Humanized source (.mid) | Perfect companion (rework) |
|---|---|---|
| 1. Grid sync (16th = 120) | **FAIL — 570 off-grid** (humanization micro-timing) | **PASS — 0 off-grid** |
| 2. Harmony (in-scale + chord-tone) | 0 out-of-scale, 18 out-of-chord (bar-boundary jitter) | **PASS — 0 / 0** |
| 3. Zero-drift (all tracks 61440) | PASS | **PASS — 6 tracks = 61440** |

**Verdict: FAIL (rule 1) on the selected humanized source.** The selection landed
on the composition job's always-on humanized export, whose micro-timing puts
570/652 pitched onsets off-grid. The composition job already ships
the de-humanized companion (`-perfect.mid`) — this IS the grid-snap rework, so no
re-snapping was needed: the perfect layer reads 0 off-grid / 0 out-of-scale /
0 out-of-chord / zero-drift. **Render source = `-perfect.mid`.** Humanized + phase-1
sidecars preserved in `MIDI/`.

## 4. SP-032 method — FDN Reverb

**Layer: ABSOLUTE** — one 8-line feedback delay network replaces the spatial
layer for the whole mix. FluidSynth internal reverb/chorus forced OFF
(`-R 0 -C 0`) so the FDN is the sole spatial treatment.

| Param | Value |
|---|---|
| n_delays / matrix | 8 · normalized Hadamard feedback |
| prime delays | 1471–2797 samples @44.1 kHz (~33–63 ms) |
| size / decay | 0.6 / 0.85 |
| brightness / modulation | 0.7 / 0.28 (0.15 Hz LFO) |
| width / duck_amount | 0.9 / 0.15 |
| wet_dry | 0.4 |

Pipeline: reworked MIDI → dry FluidSynth (`-R 0 -C 0 -g 1.2`, FX off) → +4.0 s
silence pad → FDN reverb → `master()` (target -14.0 LUFS, −1 dBTP) →
WAV + Opus OGG → pitch/silence/RMS verification → dry stems → provenance + report.

## 5. Verification (pitch mandatory check)

| Metric | Value |
|---|---|
| Pitch hit rate (0.5 s windows, harmonic-match k=1..8) | **0.9929** — 141 valid windows |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.5024** |
| **Pitch verdict** | **PASS** — tonal, not noise |
| Integrated LUFS | -14.06 (target -14.0) |
| True peak (dBTP) | -1.00 (ceiling −1.0) |
| Peak (sample, linear) | 0.891 |
| Silence ratio | **8.42%** (reverb tail decay; no mid-track gaps) |
| RMS | 0.1490 |
| Stereo width (side/mid RMS) | 0.123 |

## 6. Artifacts

| File | Size |
|---|---|
| `SP032-fdn-reverb-274-groove-sieve-rework.wav` | 13452396 B |
| `SP032-fdn-reverb-274-groove-sieve-rework.ogg` | 538031 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 12746796 B (dry reference) |
| `SP032_fdn_raw.wav` | 13452396 B (pre-master) |
| `MIDI/274-groove-sieve-rework.mid` | 8971 B (reworked — grid-locked) |
| `MIDI/274-groove-sieve-rework-humanized.mid` | 8969 B (original source) |
| `MIDI/274-groove-sieve-rework-phase1.mid` | 2316 B (raw phase-1) |
| `Audio/stems/` (dry per-voice, 6 files) | — |
| `Analysis/render_stats.json`, `provenance.json` | — |

## 7. Notes

- **Pre-flight caught the same rule-1 pattern as prior jobs**: the composition
  job ships a humanized MIDI, so the production gate's grid-sync rule fails on
  it by construction. The grid-locked `-perfect.mid` companion is the exact
  de-humanization rework — 0 off-grid without touching harmony or zero-drift.
- **Low-tuned groove**: bass plays G1 = 49 Hz, below the 50 Hz analysis band,
  so the pitch check uses harmonic matching (dominant peak may land on the 2nd
  harmonic ~98 Hz). This mirrors the SP-032-on-080 fix (2026-09-02).
- FDN wet_dry 0.4 + ducking keeps the 8th-note funk bass and horn stabs
  punchy while a warm shared room tail glues the sieve syncopation.
- `master()` true-peak is a ceiling, not a target: −14 LUFS groove legitimately
  lands near/below −1 dBTP.
- File sizes all `> 40 B`; OGG `> 10 KB`.
