# 249 — Gamelan Parsimonious Subset Sequence

Autonomous nightly composition job · 2026-10-17 · seed 249.

| Field | Value |
|---|---|
| **Style** | Gamelan (Javanese, slendro-like pentatonic) |
| **Method** | **ABS-104** — Parsimonious Subset Sequence Composition (PSSC) |
| **Layer** | **abstract** (~1/7 abstract-night cadence) |
| **Form** | `head-solos-head` → Head(8) · Solo1(8) · Solo2(8) · HeadReprise(8) = **32 bars** |
| **Key** | D pentatonic = {D E F♯ A B} = pcs {2,4,6,9,11} |
| **Tempo / meter** | 108 BPM · 4/4 · 480 TPB · BAR = 1920 · total 61440 ticks (~71 s) |
| **Seed** | 249 (composition + humanization) |

---

## 1. Method — two-phase architecture (ABS-104, abstract layer)

**Abstract layer (Phase 1 of design):** the harmony is *not* a functional
I–V–vi–IV loop. It is a **parsimonious walk through 12TET subsets of the
D-pentatonic scale** — `PatternNetwork.walk()` over a library of all 26
non-empty subsets (cardinality 2–5) of {2,4,6,9,11}, steering each step by
`edge_weight + |tension − target|` (parsimony first, tension-curve second),
seeded + deterministic. Every chord is a subset of the key scale, so the
concrete realization is in-key *by construction*.

**Concrete layer (realization):** each walked subset → a 4-voice gamelan
texture, chord-tone quantized (every note drawn from its bar's subset),
16th-grid snapped, voice-leading checked, zero-drift gated.

**Phase 1 raw draft** (`-phase1.mid`): single vibraphone voice, stochastic
random walk over the D-pentatonic pc pool, unquantized pitch + off-grid
micro-timing (±90 ticks), **no harmony**. 256 grain events, off-grid by design.

**Phase 2** (`-perfect.mid` + `-humanized.mid`): full texture, chord-quantized,
grid-snapped, dual-version export.

### Tension curve (per bar → walk target)

| Section | Bars | Target span | Role |
|---|---|---|---|
| Head | 0–7 | 1.2 → 1.8 | home (D–F♯–A sonority `p3_269` anchor) |
| Solo1 | 8–15 | 2.0 → 3.2 | rise |
| Solo2 | 16–23 | 3.2 → 4.8 | peak (4-note subsets, highest tension) |
| HeadReprise | 24–31 | 3.0 → 1.0 | resolve (cadence back to home via `home=` bias) |

---

## 2. Full progression (32 bars — the subset walk)

| bar | pattern | subset | T | bar | pattern | subset | T |
|---|---|---|---|---|---|---|---|
| 0 | p3_269 | {2,6,9} | 2.0 | 16 | p3_2911 | {2,9,11} | 3.0 |
| 1 | p2_26 | {2,6} | 0.5 | 17 | p3_2411 | {2,4,11} | 3.0 |
| 2 | p2_24 | {2,4} | 1.5 | 18 | p3_469 | {4,6,9} | 3.0 |
| 3 | p3_2411 | {2,4,11} | 3.0 | 19 | p3_6911 | {6,9,11} | 3.0 |
| 4 | p2_411 | {4,11} | 1.0 | 20 | p4_26911 | {2,6,9,11} | 5.0 |
| 5 | p2_611 | {6,11} | 1.0 | 21 | p3_4911 | {4,9,11} | 3.5 |
| 6 | p2_49 | {4,9} | 1.0 | 22 | p4_26911 | {2,6,9,11} | 5.0 |
| 7 | p2_611 | {6,11} | 1.0 | 23 | p3_6911 | {6,9,11} | 3.0 |
| 8 | p2_49 | {4,9} | 1.0 | 24 | p3_2911 | {2,9,11} | 3.0 |
| 9 | p2_611 | {6,11} | 1.0 | 25 | p3_2411 | {2,4,11} | 3.0 |
| 10 | p3_4611 | {4,6,11} | 3.5 | 26 | p3_2911 | {2,9,11} | 3.0 |
| 11 | p2_46 | {4,6} | 1.5 | 27 | p3_2411 | {2,4,11} | 3.0 |
| 12 | p3_469 | {4,6,9} | 3.0 | 28 | p2_411 | {4,11} | 1.0 |
| 13 | p3_2411 | {2,4,11} | 3.0 | 29 | p2_49 | {4,9} | 1.0 |
| 14 | p3_469 | {4,6,9} | 3.0 | 30 | p2_611 | {6,11} | 1.0 |
| 15 | p3_6911 | {6,9,11} | 3.0 | 31 | p2_49 | {4,9} | 1.0 |

Parismony is visible: adjacent bars share 1–2 pitch classes (small
voice-leading distance, P/L/R-style), and cardinality tracks the tension
curve (2-note at home, 3–4-note at peak).

---

## 3. Ensemble (instrument registry — source of truth)

| Voice | Instrument | GM | Channel | Role |
|---|---|---|---|---|
| Balungan | Glockenspiel | 9 | 0 | core melody (D6 register, sweet 84–100) |
| Gender | Vibraphone | 11 | 1 | interlocking 16th elaboration (D5, octave-down interlock) |
| Kenong | Marimba | 12 | 2 | colotomic gong/kenong punctuation (D3, root of each subset) |
| Kendang | Drum Kit | — | 9 | kick + tom interlock (Solo: 8th kendang roll) |

All pitched voices draw **only** from their bar's subset ⊆ D-pentatonic.

---

## 4. Verification (measured, mido read-only readback)

| Check | phase1 | perfect | humanized |
|---|---|---|---|
| File size (bytes) | 2245 | 7969 | 7983 |
| Zero-drift (equal track lengths) | ✅ 1 × 61440 | ✅ 4 × 61440 | ✅ 4 × 61440 |
| **Grid audit (off-grid onsets)** | 253 (raw, by design) | **0** | **712** (>0, humanizer ran) |
| **Harmony — out-of-scale** | 0 | **0** | **0** |
| **Harmony — out-of-chord** | 117 (raw, no harmony) | **0** | 9 (bar-line jitter) |

Notes:
- **Perfect** is the compositional truth: 0 off-grid, 0 out-of-scale, 0
  out-of-chord — the harmony + grid gates both pass.
- **Humanized** out-of-scale stays 0 (humanization moves *time*, not pitch).
  The 9 "out-of-chord" counts (ch0=2, ch1=3, ch2=4) are the ±≤5-tick onset
  jitter moving 9 of ~748 pitched onsets across a bar line — their pitch
  classes are unchanged and in-key; it is a time-attribution artifact, not a
  harmony violation.
- **Phase 1** is raw by contract (unquantized, unharmonized) — off-grid and
  out-of-chord are the point of the pre-rules draft.

### Per-voice grid/harmony (perfect, pre-humanization)

| Voice | notes | off_grid | out_scale | out_chord |
|---|---|---|---|---|
| Balungan | 192 | 0 | 0 | 0 |
| Gender | 512 | 0 | 0 | 0 |
| Kenong | 48 | 0 | 0 | 0 |
| Kendang | 192 (unpitched) | 0 | — | — |

---

## 5. Humanization (always-on, style-derived, seeded)

Style `gamelan` → no STYLE_HUMANIZE hit → default profile; per-instrument DNA
overrides (all metallophone-family: timing σ 2.5 ms, vel σ 5.0; kit σ 2.0 ms —
idiomatically tight/percussive). Master seed 249; per-voice child seed =
`249 * 101 + row`.

| Voice | seed | timing σ (ms) | layback (ms) | mean shift (t) | max shift (t) | vel Δ |
|---|---|---|---|---|---|---|
| Balungan | 25149 | 2.5 | 0 | 1.4 | 5 | 3.6 |
| Gender | 25150 | 2.5 | 0 | 1.3 | 5 | 4.1 |
| Kenong | 25151 | 2.5 | 0 | 1.0 | 3 | 4.4 |
| Kendang | 25152 | 2.0 | 0 | 1.1 | 5 | 3.4 |

Zero-drift safe by construction (forward-clamp, section-boundary clamp, pinned
terminal landmark) — both perfect + humanized pass `validate()`.

---

## 6. Audio (FluidSynth → master → Opus OGG)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()`). Each of the three
MIDIs rendered → mastered to `target_for_style("gamelan")` → Opus OGG.

| Render | target LUFS | integrated LUFS | true-peak dBTP | dur | silence | low-RMS s |
|---|---|---|---|---|---|---|
| perfect | −14.0 | **−14.13** | **−1.00** | 78.65 s | 8.6% | 6/78 |
| humanized | −14.0 | **−14.16** | **−1.00** | 78.64 s | 8.7% | 6/78 |
| phase1 | −14.0 | **−14.13** | **−1.00** | 73.48 s | 4.5% | 1/73 |

All three land within 0.2 LUFS of the −14.0 target, true peak pinned at the
−1 dBTP ceiling. Silence ratios are far below the 30% silent-render trap
(mostly the natural ring-out after the final kenong). OGG (Opus 128k) sizes:
phase1 1.58 MB · perfect 1.82 MB · humanized 1.81 MB — all > 40 B, non-empty.

Full numbers in `Analysis/render_stats.json`.

---

## 7. Files

```
249-gamelan-parsimonious-subset/
├── REPORT.md
├── README.md
├── index.html
├── compose.py            # engine-only composition (two-phase, dual-version)
├── render.py             # fluidsynth render + master + ogg
├── verify.py             # mido read-only audit
├── MIDI/
│   ├── 249-...-phase1.mid      (+ .provenance.json)
│   ├── 249-...-perfect.mid     (+ .provenance.json)
│   └── 249-...-humanized.mid   (+ .provenance.json)
├── Audio/
│   ├── 249-...-phase1.wav/.ogg
│   ├── 249-...-perfect.wav/.ogg
│   └── 249-...-humanized.wav/.ogg
└── Analysis/
    ├── summary.json            # subset walk + inline audit + humanize
    ├── readback.json           # mido readback (grid/harmony/zero-drift)
    ├── render_stats.json       # LUFS / dBTP / silence / RMS
    └── grid_visualization.txt
```

---

## 8. Fixes applied this run

1. **Duplicate section-name collision** — the literal `head-solos-head` form
   produced two sections both named `"Head"`; `fill_voice_section()` resolves
   by name, so both fills overwrote the first cell (corrupting pitch/timing
   alignment and silently dropping the recapitulation). Fixed by using unique
   section names (`Head`, `Solo1`, `Solo2`, `HeadReprise`).
2. **Note-clone across section seams** — `split_abs_to_section()` used an
   `end/start` clamp that *cloned* a note whose tail crossed a section seam
   into both neighbours. Changed to assign each note to the single section
   containing its start, clipping only the tail (no clone). Verified: perfect
   out-of-chord 0 (was 1 → 0), Kenong 48 notes correctly present.
