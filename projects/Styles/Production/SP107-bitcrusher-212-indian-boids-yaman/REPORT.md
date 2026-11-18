# REPORT — SP-107 BitCrusher × 212-indian-boids-yaman

**Job:** random-style production (SP) — layer-aligned (2026-11-18)
**Method:** SP-107 — Bit Crusher / Fidelity Reducer (Modbap Fidelity Theory-style)
**Source composition:** `IndianClassical/212-indian-boids-yaman` (Raga Yaman, Boids flocking)
**Seed:** 20261118

---

## 1. Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (97 implemented entries) |
| Method | **SP-107** → `sound.effects.bit_crusher` |
| Source MIDI | `Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid` |
| Candidates | 466 `.mid` scanned → 361 well-formed → 360 meaningful (≥3 pitch classes) |
| Recent excluded (≤7 d) | SP-069, SP-075, SP-084, SP-100, SP-115, SP-146, SP-154 |
| Already-on-source | SP-091 (this source had an earlier SP pass) |
| Baseline excluded | SP-001 |
| Pool size | 88 |

## 2. Source composition

| Field | Value |
|---|---|
| Style / key | IndianClassical — **Raga Yaman on C** (S R G M̄ P D N = C D E F♯ G A B) |
| BPM / meter / TPB | 90 · 4/4 · 480 TPB (16th = 120, 8th = 240, bar = 1920) |
| Length | 32 bars (8 sections × 4), alap → gat → jhala → alap, ~85.3 s |
| Voices | Drone (Church Organ 19, ch0), LeadSitar (Sitar 104, ch1), Bansuri (Flute 74, ch2), Tabla (ch9) |
| Harmony | Monophonic raga over Sa+Pa tanpura drone; chord-tone vocabulary = full Yaman scale |
| Method of origin | 031 Swarm Intelligence Flocking (Boids), two-phase (phase1 raw → phase2 rules) |

## 3. Pre-flight — RULES ADHERENCE GATE

| Rule | Result |
|---|---|
| 1. Grid sync (16th = 120) | **PASS — 0 off-grid** (960 pitched+perc onsets all on 16th grid) |
| 2. Harmony (in-scale + chord-tone) | **PASS — 0 out-of-scale, 0 out-of-chord** (vs Yaman pcs {0,2,4,6,7,9,11}) |
| 3. Zero-drift | **PASS — all 4 note tracks end at 61440 ticks (32 bars)** |

**Verdict: PASS all three — no rework required.** Source was already rules-clean
(0 / 0 / 0 / zero-drift). Raw boid draft preserved as phase1 sidecar in `MIDI/`.

## 4. SP-107 method — Bit Crusher / Fidelity Reducer

**Layer: ABSOLUTE** — one fidelity-reducer chain applied across the whole dry mix
(per-channel `BitCrusher` instances to avoid cross-channel filter-state leakage).

| Param | Value |
|---|---|
| fidelity | 0.42 → sample rate **23600 Hz**, bit depth **10** |
| mode | **worn** (low-mid emphasis, softened highs, asymmetric saturation + grain) |
| ring | 0.20 (aliasing foldover emphasis) |
| mix | 1.0 (full wet) |

Pipeline: source MIDI → 3-rule pre-flight (PASS) → dry FluidSynth (`-R 0 -C 0 -g 1.2`,
FX off) → SP-107 bit-crusher → `master()` (target −18.0 LUFS, −1 dBTP ceiling) →
WAV + Opus OGG → pitch/silence/RMS verification → provenance + this report.

## 5. Verification (synthesis-pitch mandatory check)

| Metric | Value |
|---|---|
| Pitch hit rate (0.5 s windows vs Yaman pcs) | **1.000** (172/172 valid windows) |
| Mean harmonic energy (8 harmonics of lowest fundamental) | **0.410** (≥ 0.30 threshold) |
| Harmonic-energy retention vs dry | **0.923** (≥ 0.40 threshold) |
| **Pitch verdict** | **PASS** — tonal, not noise |
| Integrated LUFS | −18.00 (target −18.0) |
| True peak | −4.62 dBTP (ceiling −1.0 — legit below ceiling for a −18 LUFS raga) |
| Peak (sample) | 0.587 |
| Silence ratio | **7.72%** (tail padding after final note; no mid-track gaps) |
| RMS | 0.0903 (per-second RMS map continuous 0–85 s, then clean tail decay) |

## 6. Artifacts

| File | Size |
|---|---|
| `SP107-bitcrusher-212-indian-boids-yaman.wav` | 16,321,068 B (92.5 s, 44.1 kHz stereo) |
| `SP107-bitcrusher-212-indian-boids-yaman.ogg` | 626,760 B (Opus 48k voip) |
| `dry_full_mix_sp001_reference.wav` | 16,321,068 B (dry reference) |
| `MIDI/212-indian-boids-yaman.mid` | 7,847 B (rules-processed) |
| `MIDI/212-indian-boids-yaman-phase1.mid` | 3,889 B (raw boid draft) |
| `Analysis/preflight.json`, `Analysis/render_stats.json`, `provenance.json` | — |

## 7. Notes

- No composition fixes were needed — the pre-flight gate passed clean on the first
  audit, so the "rework-first" branch was not triggered.
- `master()` true-peak is a ceiling, not a target: a −18 LUFS raga legitimately
  lands at −4.62 dBTP. Correct behaviour, not fixed.
- Wall clock: dry render ~40 s + bit-crush 86 s + master ~210 s = **343 s** total
  (bit-crusher is pure-Python per-sample; master LUFS metering dominates).
- File sizes all `> 40 B` (no empty-output trap); OGG `> 10 KB`.
