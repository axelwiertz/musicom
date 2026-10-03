# 219-japanese-kojo-koto-rework — Rework Report

**Rework of:** `Japanese/103-japanese-kojo-koto` (Nightly Autonomous Rework Job, 2026-10-03)

---

## 1. Source selection & audit

Randomly selected source composition: **Japanese/103-japanese-kojo-koto**
(L-System dragon-curve, A hirajoshi pentatonic, Jo-Ha-Kyu form, 24 bars).

**Audit against current standards** (full JSON in source `Analysis/rework_audit.json`):

| # | Standard | Result |
|---|---|---|
| 1 | Engine-authored (`UnitMatrixComposer`) | ✅ pass |
| 2 | Zero-drift (equal track lengths) | ✅ pass (5×46080) |
| 3 | Rhythm-grid sync (onset % 120/240) | ✅ pass (0/556 off-grid) |
| 4 | ≥4 voice tracks | ✅ pass (5 voices) |
| 5 | Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | ✅ pass |
| 6 | provenance.json + index.html | ❌ **fail** (both missing) |

**Decision: EXTEND** (not full rebuild). The musical core is already fully
engine-compliant — only documentation artifacts were missing. I preserved the
identity (genre, key, tempo, L-system method, 5-voice orchestration) and:
- extended the form 6→8 sections (24→32 bars),
- added 6 variation techniques,
- remediated std6 (root `provenance.json` + `index.html` in the new project).

---

## 2. Identity (preserved from source)

| Item | Value |
|---|---|
| Style | Japanese (koto + shakuhachi + shamisen + taiko) |
| Key | A hirajoshi pentatonic — pc {9,10,2,4,7} (A Bb D E G) |
| BPM / meter | 80 · 4/4 · 480 TPB |
| Method | 019 L-System (dragon-curve, `A→A+B, B→A-B`, +2/−2) |
| Voices | Koto(107,ch0) · Shakuhachi(74,ch1) · Shamisen(106,ch2) · KotoBass(107,ch3) · Taiko(ch9) |
| Harmonic palette | 4-note pentatonic subsets, one per bar, root on the true chord root |

---

## 3. Form (extended)

Source: Jo·Ha1·Ha2·Kyu1·Kyu2·Jo_Coda = 6×4 = 24 bars.
Rework: **8 sections × 4 bars = 32 bars** (N+2 sections, 8 bars beyond source).

| Section | Method | Density | Palette (per bar) | Variation technique |
|---|---|---|---|---|
| Jo | original | quarter | A·A·D·A | **Augmentation** (half-speed lead) |
| Ha1 | original | eighth | A·G·Bb·A | theme statement |
| Ha2 | **invert** | eighth | Bb·D·E·Bb | **Inversion** (negated deltas) |
| Bridge | **arpeggio** | arp | D·G·A·D | **Method change** (pentatonic arpeggio) |
| Kyu1 | **retrograde** | sixteenth | E·A·G·E | **Retrograde + diminution** |
| Kyu2 | original | sixteenth | G·A·Bb·E | **Register shift** (lead 74–90) + diminution |
| Interlude | original | eighth | A·Bb·D·A | **Canon counterline** (shamisen echo) |
| Jo_Coda | original | quarter | A·E·D·A | resolution, theme returns |

Per-section harmonic regions are distinct; bass drone lands on each bar's true
root (A, Bb, D, E, G), so **no all-tonic collapse** (bar-0 tonic bug avoided).
Roots are derived from the per-bar palette, attributed by `t // BAR` (floor).

---

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw L-system draft, single voice, unquantized
  micro-rhythm (~235±25 ticks/note), whole-tone fractal folded into koto window.
  Fingerprint: **254/256 (99.2%) off-grid** — confirms raw unquantized material.
- **Phase 2** (`.mid`): musicom rules — 16th/8th grid snap, per-bar chord-tone
  quantization, register enforcement, 5-voice arrangement, dedup of collided
  `(start_tick, pitch)` keeping longest. `validate()` PASS on both phases.

---

## 5. Verification (real numbers)

| Gate | Phase 1 | Phase 2 |
|---|---|---|
| `validate()` | PASS | PASS |
| MIDI size | 2251 B (>40) | 6694 B (>40) |
| Voice tracks | 1 | 5 |
| Zero-drift (track lengths) | [61440] | all 5 = 61440 |
| Total notes | 256 | 736 |
| Off-grid (pitched onsets) | 254 (raw) | **0** |
| Out-of-scale | — (raw) | **0** |
| Out-of-chord | — (raw) | **0** |

**Per-track (Phase 2):** Koto 288 · Shakuhachi 64 · Shamisen 224 · KotoBass 32 ·
Taiko 128 notes — all off-grid 0, out-of-scale 0, out-of-chord 0.

**Audio (FluidSynth → Opus):** 99.51 s (96 s music + 3.5 s reverb tail),
peak 0.920, silence ratio **4.51%** (well under 30% trap), RMS −21.6 dBFS.

---

## 6. Artifacts

| File | Size |
|---|---|
| `MIDI/219-japanese-kojo-koto-rework.mid` | 6694 B |
| `MIDI/219-japanese-kojo-koto-rework-phase1.mid` | 2251 B |
| `Audio/219-japanese-kojo-koto-rework.wav` | 17,552,940 B |
| `Audio/219-japanese-kojo-koto-rework.ogg` | 821,507 B |
| `Analysis/grid_visualization.txt` | 4677 B |
| `Analysis/rework_verify.json` | — |
| `provenance.json` (root) + 2× `.mid.provenance.json` | — |
| `index.html` dashboard | — |
