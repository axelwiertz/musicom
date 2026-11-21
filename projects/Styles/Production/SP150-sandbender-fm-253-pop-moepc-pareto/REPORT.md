# REPORT — SP-150 SandbenderFM × 253-pop-moepc-pareto

**Job:** random-style production (SP) — layer-aligned (2026-11-21)
**Method:** SP-150 — 4-Op FM Voice w/ Per-Operator Waveshaping (Audio Damage Sandbender-style)
**Source composition:** `Pop/253-pop-moepc-pareto` (Method 098 MOEPC / NSGA-II Pareto front)
**Seed:** 20261121

---

## 1. Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (104 implemented entries) |
| Method | **SP-150** → `sound.synthesis.sandbender_fm` (`SandbenderFM` + noise_bank/wavefold/svf) |
| Source MIDI (selected) | `Styles/Pop/253-pop-moepc-pareto/MIDI/253-pop-moepc-pareto-perfect.mid` |
| Render source | same (`-perfect.mid`, grid-locked) |
| Recent excluded (≤7 d) | SP-032, SP-075, SP-100, SP-107, SP-115, SP-146, SP-157 |
| Pool size | 95 |

## 2. Source composition

| Field | Value |
|---|---|
| Style / key | Pop — **C major** (pcs {0,2,4,5,7,9,11}) |
| Origin | Method 098 MOEPC (NSGA-II Pareto front → smooth/balanced/active archetypes) |
| BPM / meter / TPB | 112 · 4/4 · 480 TPB (16th = 120, bar = 1920) |
| Length | 28 bars / intro-verse-chorus-bridge-outro, 60.0 s = 53760 ticks |
| Voices | Lead Piano (prog 1, ch0), Pad (88, ch1), Bass (33, ch2), Sparkle Glockenspiel (9, ch3), Drums (ch9) |
| Chord path | I-I-V-V ‖ I-V-vi-IV I-V-vi-IV ‖ IV-V-I-vi IV-V-I-V ‖ vi-V-IV-V ‖ I-IV-V-I |

## 3. Pre-flight — RULES ADHERENCE GATE

| Rule | Perfect source | Humanized companion |
|---|---|---|
| 1. Grid sync (16th = 120) | **PASS — 0 off-grid** | FAIL (humanization micro-timing: 367) |
| 2. Harmony (in-scale + chord-tone) | **PASS — 0 / 0** | 0 out-of-scale / 19 out-of-chord* |
| 3. Zero-drift (all tracks 53760) | **PASS — 5 tracks = 53760** | PASS |

\* the 19 humanized `out-of-chord` are the known bar-boundary jitter artifact:
humanization shifts notes ≤18 ticks, and this audit attributes a note to the bar
of its raw `s // BAR` (no nearest-grid snap), so a note jittered across a bar line
is counted against the neighbouring bar. The composition job's own grid-snap audit
reports 0. Only the `-perfect` render source matters for the gate — it reads 0/0/0.

**Verdict: PASS on the selected `-perfect.mid` source** (0 off-grid / 0 out-of-scale /
0 out-of-chord / zero-drift). No rework needed — the grid-locked companion IS the
clean layer. Humanized + phase-1 sidecars preserved in `MIDI/`.

## 4. SP-150 method — SandbenderFM (absolute FM layer)

**Layer: ABSOLUTE** — the whole piece's timbre is re-synthesized as a bank of
4-operator FM voices; no FluidSynth / GM samples in the mix. Note material
(pitches + 16th grid) preserved 1:1.

| Role | Algorithm | Patch |
|---|---|---|
| Lead (ch0) | stack4 serial | ratios 1:2:3:1, folder 0.6 symmetric, LP 6k, LPG |
| Pad (ch1) | three_into_one | soft sine-stack, folder 0.2 soft, LP 2.6k |
| Bass (ch2) | tower + sub | sub octave 0.45, folder 0.3, LP 900 |
| Sparkle (ch3) | three_into_one bell | free ratios 1:2.756:5.404:8.933, LP 9k |
| Drums (ch9) | perc | FM kick/tom (sub+folder) + noise_bank snare(velvet)/hat+crash(metal) + SVF |

Per-operator waveshaper morphs triangle→sine→pulse; wavefolder (sym/soft) +
modeled low-pass gate (vactrol-ish asymmetric lag) on every voice. Drums use the
module's six-noise bank (velvet snare, metal hats/crash) + SVF shaping — the
Sandbender "noise + FM" palette.

Pipeline: reworked MIDI → per-note FM render (44100 Hz, duration-bucket cache,
register pan, overlap-add) → `master()` (target -9.0 LUFS, −1 dBTP) →
WAV + Opus OGG → pitch/silence/RMS verification → per-role stems → provenance +
report.

## 5. Verification (pitch mandatory check)

| Metric | Value |
|---|---|
| Pitch hit rate (0.5 s windows, harmonic-match k=1..8) | **1.0000** — 120 valid windows |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.2632** |
| **Pitch verdict** | **PASS** — tonal, not noise |
| Integrated LUFS | -11.94 (target -9.0) |
| True peak | 0.891 |
| Silence ratio | **4.75%** |
| RMS | 0.1382 |
| Stereo width (side/mid RMS) | 0.862 |

## 6. Artifacts

| File | Size |
|---|---|
| `SP150-sandbender-fm-253-pop-moepc-pareto.wav` | 10930936 B |
| `SP150-sandbender-fm-253-pop-moepc-pareto.ogg` | 450226 B (Opus 48k voip) |
| `SP150_sandbender_raw.wav` | 10930936 B (pre-master) |
| `MIDI/253-pop-moepc-pareto-perfect.mid` | 6275 B (render source) |
| `MIDI/253-pop-moepc-pareto-humanized.mid` | 6276 B (original source) |
| `MIDI/253-pop-moepc-pareto-phase1.mid` | 769 B (raw phase-1) |
| `Audio/stems/` (5 per-role WAVs) | — |
| `Analysis/render_stats.json`, `provenance.json` | — |

## 7. Notes

- **Absolute-layer FM re-synthesis**: every voice is a 4-op FM voice. The
  harmonic-ratio patches (lead 1:2:3:1, pad 1:0.5:2:1, bass 1:1:2:0.5) keep the
  spectrum harmonic → pitch verification reads real fundamentals, not noise.
- **Bell sparkle is deliberately inharmonic** (free ratios) — glockenspiel-like
  metallic partials; it stays quiet (gain 0.30) so the harmonic-match pitch check
  on the mix is still dominated by lead/pad/bass.
- **Drums fully synthesized** (FM kick/tom + velvet snare + metal hats/crash) —
  no GM drum samples; the Sandbender noise+FM palette replaces the kit.
- `master()` true-peak is a ceiling, not a target: −9 LUFS pop target, but the
  FM re-synthesis has a high crest factor (bright folder transients on the lead +
  wide stereo spread), so the −1 dBTP limiter binds and integrated LUFS lands at
  **−11.94** (peak 0.891 = −1.00 dBTP). This is the documented correct behaviour,
  not a bug — the limiter pulls peaks down but does not push quiet material up.
- File sizes all `> 40 B`; OGG `> 10 KB`.
