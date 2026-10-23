# REPORT — 258-groove-rbn-critical

**Project:** 258-groove-rbn-critical
**Genre:** Groove (funk-style 16th groove)
**Method:** 082 — Random Boolean Network Criticality Composition (RBNCC) · **Layer:** concrete · **Paradigm:** Nature-Led
**Form:** `aba` (A1 8 | B 8 | A2 8 = 24 bars) — chosen via `pick_form(style)` (not verse-chorus)
**Key:** A natural minor (A B C D E F G) · **BPM:** 104 · 4/4 · 480 TPB
**Date:** 2026-10-22 (nightly composition job)
**Seed:** 20261022 · humanize seed 20261023

---

## 1. Selection (LAYERED METHODOLOGY)

- **Style:** `Groove` — random draw from `/opt/data/projects/Styles/` genre
  folders (excluded `_Comparison/_Data_Patterns/Research/Poetry/Production/
  Percussion/Other`).
- **Method:** `082 RBNCC` — random draw from the algorithmic methods table,
  excluding methods used in the last 7 days (043, 051, 065, 069, 098, 104,
  111, 113, ABS-001/002, and the balfolk 004–008 set). **Layer = concrete**.
- **Form:** `aba` — `pick_form("Groove")` (loop_prob = 1/7 default; the draw
  landed on a real 3-part form, not a loop).

## 2. Method — RBN criticality (Kauffman Boolean network)

A random Boolean network is a triple (N, K, {f_i}): N binary nodes, K incoming
edges each, synchronous update x_i(t+1) = f_i(inputs). Critical connectivity
K_c = 1/[2p(1-p)] = **2** at bias p = 0.5. The deterministic trajectory has a
**transient** (length μ) then an **attractor cycle** (length λ).

| param | value |
|---|---|
| N (nodes) | 24 |
| K (connectivity) | 2 (= critical) |
| p (output bias) | 0.5 |
| **μ (transient)** | **6** |
| **λ (attractor cycle)** | **22** |
| slots (16th grid) | 384 (24 bars × 16) |
| raw events | 138 |

- **Transient (μ=6)** = connective/tension material at the very start.
- **Attractor cycle (λ=22)** = the repeating groove.
- **Frozen core** → harmonic scaffold (mapped in phase 2 to the A-minor 7th
  chords); **unstable periphery** → the figuration (the clavi lead line).
- Decode: bits[0:12] = pitch-class mask, bits[12:24] = rhythm/velocity mask.
  Onset presence = rhythm bit; pitch = parsimonious pick among active pcs
  (nearest to the previous sounding pc — the symmetric-difference/voice-leading
  flavor of the method).

## 3. Two-phase architecture

**Phase 1 (`-phase1.mid`)** — raw RBN draft, single clavi voice, 138 events.
Pitches are the literal chromatic pitch classes (48 + pc) — **off-scale by
design** (chromatic fingerprint: off-scale pcs = {1, 3, 6, 8}, 7 distinct pcs
total). Onsets OFF-GRID (jittered +12…+55 ticks). NO harmony, NO grid.

**Phase 2 (`-perfect.mid` + `-humanized.mid`)** — musicom rules post-process:
1. onset snap to the 16th grid (120 ticks);
2. tiered pitch quantization via `ScaleQuantizer.tiered_quantize` —
   strong beats (1 & 3, grid (0, 960)) → nearest scale degree THEN nearest
   chord tone (in-scale AND in-chord); weak beats → nearest scale degree only
   (in-scale). Zero chromaticism — every chord is diatonic so in-scale ∩
   in-chord is always satisfiable;
3. full 5-voice groove texture;
4. zero-drift landmark padding + `validate()` gate.

## 4. Form + harmony (24 bars, all diatonic 7th chords in A natural minor)

| Section | Bars | Progression | Symbols |
|---|---|---|---|
| A1 | 0–7 | i7 i7 VI7 VII7 i7 i7 VI7 VII7 | Am7 Am7 Fmaj7 G7 Am7 Am7 Fmaj7 G7 |
| B | 8–15 | III7 VI7 iv7 v7 III7 VI7 iv7 v7 | Cmaj7 Fmaj7 Dm7 Em7 Cmaj7 Fmaj7 Dm7 Em7 |
| A2 | 16–23 | i7 i7 VI7 VII7 i7 i7 VI7 VII7 | Am7 Am7 Fmaj7 G7 Am7 Am7 Fmaj7 G7 |

Every chord is a four-note 7th chord built from scale degrees (d, d+2, d+4,
d+6) of A natural minor → **all chord tones are in-scale**, so the tiered
discipline's in-scale ∩ in-chord requirement is satisfiable with **zero
chromaticism** (bass/pad/harmony/rhythm carry zero chromatic; the lead carries
zero chromatic too — no ornaments were needed).

## 5. Voices + instruments (from `instrument_registry.py`)

| Voice | Instrument | GM program | Channel | humanize DNA (timing/vel/layback/dur σ) |
|---|---|---|---|---|
| Clavi | Clavinet | 7 | 0 | (6.0, 5.0, 0.0, 0.015) |
| Rhodes | Electric Piano 1 | 4 | 1 | (6.0, 5.0, 0.0, 0.015) |
| Bass | Electric Bass (finger) | 33 | 2 | (5.0, 4.0, 8.0, 0.01) |
| Pad | Pad 1 (new age) | 88 | 3 | (3.0, 4.0, 0.0, 0.01) |
| Drums | Drum Kit | — | 9 | (2.0, 4.0, 0.0, 0.008) |

Roles: Clavi = RBN-derived lead (138 notes); Rhodes = off-beat comp (192
notes, "and of 2" / "and of 4"); Bass = groove (root on 1&3 strong, octave
syncopation + diatonic approach on weak, 96 notes); Pad = B-section-only
sustain lift (32 notes); Drums = funk groove (syncopated kick 1·and-2·3,
backbeat snare 2&4, 16th hats, 512 hits).

## 6. Grid audit (per voice, pre-humanization)

Read-only mido audit of the exported phase-2 MIDI. All pitched-voice onsets
snap to the 16th grid (120 ticks); drums (ch 9) are excluded from the pitch
grid audit by convention.

| artifact | pitched notes | off-grid | verdict |
|---|---|---|---|
| perfect | 458 | **0** | ✅ grid-locked |
| humanized | 458 | **421** | ✅ humanizer ran (>0 required) |
| phase1 (raw) | 138 | **138** | ✅ off-grid by design |

## 7. Tiered harmony audit (`workflows.pitch_audit.audit_voice`)

Perfect (strict: strong notes must be in-scale **and** in-chord), per voice:

| ch | voice | audible | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|
| 0 | Clavi | 138 | 10 | 128 | 0 | 0 | 0 | ✅ |
| 1 | Rhodes | 192 | 0 | 192 | 0 | 0 | 0 | ✅ |
| 2 | Bass | 96 | 48 | 48 | 0 | 0 | 0 | ✅ |
| 3 | Pad | 32 | 32 | 0 | 0 | 0 | 0 | ✅ |

Humanized (in-scale audit; jittered onsets fall off the strong grid so notes
are re-classified weak) → all voices pass: **0 untagged_out / 0 non_resolving
/ 0 strong_viol**. No tagged ornaments were used anywhere (bass/pad/harmony/
rhythm = zero chromatic, as required; lead stays fully diatonic).

## 8. Humanization (always-on, style-derived, seeded)

`export_dual` validated + exported the grid-locked `-perfect.mid` FIRST, then
humanized in place, re-validated, exported `-humanized.mid`. Seed = 20261023
(per-voice child seed = seed·101 + row). All shifts forward-clamped and
boundary-clamped → `validate()` passed on BOTH exports (zero-drift safe).

| voice | timing σ ms | layback ms | mean abs shift (ticks) | max shift (ticks) | mean vel delta |
|---|---|---|---|---|---|
| Clavi | 3.0 | 0 | 1.64 | 8 | 3.86 |
| Rhodes | 6.0 | 0 | 3.88 | 12 | 3.84 |
| Bass | 5.0 | **8.0** | **6.51** | 15 | 3.01 |
| Pad | 3.0 | 0 | 2.00 | 4 | 3.31 |
| Drums | **2.0** | 0 | **1.05** | 4 | 3.05 |

Invariants hold: drums tightest (2.0 ms, 1.05-ticks mean), bass lays back
(+8 ms, 6.51-ticks mean), lead (clavi) locked tight at 3.0 ms / 1.64-ticks
mean. All within profile bounds.

## 9. Zero-drift

All 5 note tracks = **46080 ticks** (= 24 bars × 1920). `drift_ok = True` on
both phase-2 exports and the phase-1 draft. Terminal landmark
`MusicEvent(0,0,sec_len,sec_len)` pins every cell to its section boundary.

## 10. Render + mastering (FluidSynth → `master()` → Opus OGG)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()`). Style target =
`target_for_style("Groove")` = **−14.0 LUFS** (fallback, balanced). All three
MIDIs rendered (`fluidsynth -ni -g 1.2 -R no -C no`), mastered
(`master(target_lufs=-14, ceiling_db=-1)`), OGG-encoded (libopus voip 48k).

| artifact | LUFS | true peak | peak | silence | dur | wav | ogg |
|---|---|---|---|---|---|---|---|
| perfect | −14.04 | −1.0 dBTP | 0.884 | 6.6% | 57.96 s | 10.22 MB | 366 KB |
| humanized | −14.05 | −1.0 dBTP | 0.891 | 6.8% | 57.96 s | 10.22 MB | 358 KB |
| phase1 | −14.19 | −1.0 dBTP | 0.891 | 60.9%* | 57.39 s | 10.12 MB | 278 KB |

\* phase-1 silence is **expected** — the raw draft is a sparse monophonic RBN
line (138 short notes, no drums/harmony); the per-second RMS map shows activity
(RMS 0.06–0.21) across all 55 seconds with the only zeros in the final tail
(secs 55–56). The full textures (perfect/humanized) show RMS 0.12–0.19 every
second → **no mid-track gaps**; their 6.6–6.8% silence is only the release tail.

All measured LUFS ≈ −14.0 target; all true peaks ≤ −1.0 dBTP.

## 11. Files

| file | size (bytes) |
|---|---|
| MIDI/258-groove-rbn-critical-phase1.mid | 1198 |
| MIDI/258-groove-rbn-critical-perfect.mid | 7557 |
| MIDI/258-groove-rbn-critical-humanized.mid | 7350 |
| Audio/*-perfect.wav / .ogg | 10223404 / 366075 |
| Audio/*-humanized.wav / .ogg | 10223404 / 357665 |
| Audio/*-phase1.wav / .ogg | 10123052 / 277763 |
| Analysis/verify.json / summary.json / grid_visualization.txt | — |
| provenance.json per MIDI artifact | — |

## 12. Verification summary (all real numbers)

- ✅ phase1 off-grid = 138/138 (raw), chromatic fingerprint (off-scale pcs {1,3,6,8})
- ✅ perfect off-grid = 0/458; humanized off-grid = 421/458 (>0)
- ✅ harmony: 0 untagged out-of-scale / 0 non-resolving / 0 strong violations
  (both perfect and humanized, all 4 pitched voices)
- ✅ zero-drift: all tracks 46080 ticks
- ✅ mastering: −14.04 / −14.05 / −14.19 LUFS, −1.0 dBTP ceiling
- ✅ sizes > 40 bytes (all MIDI + OGG)
- ✅ phase1 fingerprint: 7 distinct pcs, 4 off-scale (chromatic by design)

No fixes were required post-verification (single-pass green).

## 13. Lead-timing fix (2026-10-23 rebuild)

The jazz swing bug (straight lead vs swung ride) does **not** apply here — this
is a straight-16th groove, so the lead is already on the correct grid. The real
lead-timing issue was humanization looseness: the clavi lead carried the Keys
family default (6.0 ms σ, 16-tick max shift) while the drums anchor at 2.0 ms.
For a tight groove the lead must lock, so `hz_instruments["Clavi"]` is overridden
to `(3.0, 5.0, 0.0, 0.015)` → lead mean |dev| 1.64 ticks (was 3.28), max 8
(was 16), now within ~1.6× of the drum anchor instead of ~3×. Re-composed +
re-verified + re-rendered.
