# REPORT — 263-chanson-frieze-canon

**Project:** 263-chanson-frieze-canon
**Genre:** Chanson (French art song — lyrical, piano/strings, restrained groove)
**Method:** 091 — Coxeter–Conway Frieze Pattern Composition (CCFPC) · **Layer:** concrete · **Paradigm:** Rules-Based
**Form:** `verse-chorus` (Intro 4 | Verse 8 | Chorus 8 | Verse2 8 | Chorus2 8 | Outro 4 = 40 bars) — chosen via `pick_form(style)` (not a loop)
**Key:** D major (ionian: D E F# G A B C#) · **BPM:** 92 · 4/4 · 480 TPB
**Date:** 2026-10-24 (nightly composition job)
**Seed:** 20261024 · humanize seed 20261025

---

## 1. Selection (LAYERED METHODOLOGY)

- **Style:** `Chanson` — random draw from `/opt/data/projects/Styles/` genre
  folders (excluded `_Comparison/_Data_Patterns/Research/Poetry/Production/
  Percussion/Other`).
- **Method:** `091 CCFPC` — random draw from the algorithmic methods table
  (concrete pool, 103 candidates) excluding the last-7-days set
  (004–008 balfolk, 023, 026, 043, 051, 053, 065, 069, 075, 082, 098, 104,
  111, 113, ABS-001/002). **Layer = concrete** (~6/7 concrete night).
- **Form:** `verse-chorus` — `pick_form("Chanson")` (chanson is in the
  verse-chorus style-hint pool; the draw landed on a real 4-part form, not a loop).

## 2. Method — Coxeter–Conway frieze (continuants + Ptolemy flips)

A frieze pattern is an array of positive integers whose adjacent 2×2 diamonds
satisfy the **unimodular relation** `ad − bc = 1`. It is generated from a
triangulation of a convex polygon: the **quiddity sequence** (a_i = triangles
meeting vertex i) is the second row, and every lower row is an **Euler
continuant** `K(x₁,…,xₖ)` of consecutive quiddity entries
(`K()=1, K(x)=x, K(x,y)=xy−1, K(x,y,z)=xyz−x−z, …`).

| param | value |
|---|---|
| period n | 16 (= one 4/4 bar of 16ths) |
| polygon | 16-gon, fan triangulation |
| quiddity (Intro/Outro) | [14,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1] (sum 42 = 3(n−2)) |
| quiddity (Verse) | [13,2,1,3,2,2,2,2,2,2,2,2,2,2,2,1] (1 Ptolemy flip) |
| quiddity (Chorus) | [12,3,1,2,3,2,2,2,2,2,2,2,2,2,2,1] (2 Ptolemy flips) |
| raw events (phase 1) | 213 |

- **Rows = polyphonic strata** (quiddity = voice 1, interior rows = inner
  voices); **columns = metric pulses** (16th slots).
- **Verified invariants** (asserted in compose.py): R₀ = all 1s (top boundary),
  Rₙ₋₂ = all 1s (bottom boundary), Rₙ₋₁ = all 0s (termination), all interior
  entries positive, and the **glide-reflection mirror** R₁ and Rₙ₋₃ share the
  identical value multiset (the canon source).
- **Ptolemy diagonal flips** (quiddity mutation: `q_i−=1, q_j−=1,
  q_{i+1}+=1, q_{j+1}+=1`, sum-preserving) generate section-specific friezes —
  the method's "cluster-algebra mutation across section boundaries".

**Musical translation:** the lead reads the frieze **vertically** (down the
columns of rows R₁…R₇, cycling per bar) — each column is a monotone
ascending/descending contour, so the melody is a chain of rising/falling
phrases with the "14→2" corner giving the registral climax. The clarinet reads
the **glide-reflection mirror row** Rₙ₋₂₋ₖ at the off-16ths — an inverted,
phase-shifted canon. The unimodular determinant (`ad−bc=1`) is the method's
structural guarantee against "parallel collapse" / harmonic drift.

## 3. Two-phase architecture

**Phase 1 (`-phase1.mid`)** — raw frieze draft, single oboe voice, 213 events.
Pitch = `60 + frieze_value` (chromatic — off-scale pcs **{0,3,5,8,10}** by
design, 12 distinct pcs total). Onsets OFF-GRID (jittered +12…+55 ticks).
NO harmony, NO grid.

**Phase 2 (`-perfect.mid` + `-humanized.mid`)** — musicom rules post-process:
1. onset snap to the 8th/16th grid;
2. tiered pitch quantization via `ScaleQuantizer.tiered_quantize` —
   strong beats (1 & 3, grid (0, 960)) → nearest scale degree THEN nearest
   chord tone (in-scale AND in-chord); weak beats → nearest scale degree only
   (in-scale). Zero chromaticism — every chord is diatonic so in-scale ∩
   in-chord is always satisfiable;
3. full 6-voice chanson texture;
4. zero-drift landmark padding + `validate()` gate;
5. dual-version export (`export_dual`: perfect then humanized).

## 4. Form + harmony (40 bars, all diatonic 7th chords in D major)

| Section | Bars | Progression |
|---|---|---|
| Intro | 0–3 | Dmaj7 · Gmaj7 · Em7 · A7 |
| Verse | 4–11 | Dmaj7 · Bm7 · Gmaj7 · A7 · Dmaj7 · Bm7 · Em7 · A7 |
| Chorus | 12–19 | Gmaj7 · A7 · Dmaj7 · Bm7 · Gmaj7 · A7 · Dmaj7 · Dmaj7 |
| Verse2 | 20–27 | Dmaj7 · Bm7 · Gmaj7 · A7 · Dmaj7 · Bm7 · Em7 · A7 |
| Chorus2 | 28–35 | Gmaj7 · A7 · Dmaj7 · Bm7 · Gmaj7 · A7 · Dmaj7 · Dmaj7 |
| Outro | 36–39 | Gmaj7 · A7 · Dmaj7 · Dmaj7 |

Every chord is a four-note 7th chord from scale degrees (d, d+2, d+4, d+6) →
**all chord tones in-scale** → the tiered discipline's in-scale ∩ in-chord
requirement is satisfiable with **zero chromaticism** (bass/pad/harmony/rhythm
zero chromatic; the lead stays fully diatonic — no ornaments needed).

## 5. Voices + instruments (from `instrument_registry.py`)

| Voice | Instrument | GM program | Channel | Role | humanize DNA (timing/vel/layback/dur σ) |
|---|---|---|---|---|---|
| Oboe | Oboe | 68 | 0 | frieze lead | (None, 7.0, None, 0.02) — style governs timing |
| Clarinet | Clarinet | 71 | 1 | glide-reflection canon | (None, 7.0, None, 0.02) |
| Piano | Acoustic Grand | 0 | 2 | off-beat comp | (None, 5.0, None, 0.015) |
| Strings | String Ensemble 1 | 48 | 3 | pad (Intro/Chorus/Outro) | (None, 6.0, None, 0.03) |
| Bass | Double Bass | 43 | 4 | root/5th/approach | (10.0, 6.0, 8.0, 0.03) |
| Drums | Drum Kit | — | 9 | light brush groove | (2.0, 4.0, 0.0, 0.008) |

Roles: Oboe = frieze lead (213 notes); Clarinet = off-16th canon (216);
Piano = off-beat voicings (320); Strings = sustained swell (96, 24 bars);
Bass = root 1&3 + octave syncopation + diatonic approach (160); Drums = soft
kick 1&3 / brush side-stick 2&4 / tick hat (336).

## 6. Grid audit (per voice, pre-humanization)

Read-only mido audit of the exported phase-2 MIDI. All pitched-voice onsets
snap to the 16th grid (120 ticks); drums (ch 9) excluded from the pitch grid
audit by convention.

| artifact | pitched notes | off-grid | verdict |
|---|---|---|---|
| perfect | 1005 | **0** | ✅ grid-locked |
| humanized | 1005 | **936** | ✅ humanizer ran (>0 required) |
| phase1 (raw) | 213 | **213** | ✅ off-grid by design |

## 7. Tiered harmony audit (`workflows.pitch_audit.audit_voice`)

Perfect (strict: strong notes must be in-scale **and** in-chord), per voice:

| ch | voice | audible | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|
| 0 | Oboe | 213 | 51 | 162 | 0 | 0 | 0 | ✅ |
| 1 | Clarinet | 216 | 0 | 216 | 0 | 0 | 0 | ✅ |
| 2 | Piano | 320 | 0 | 320 | 0 | 0 | 0 | ✅ |
| 3 | Strings | 96 | 96 | 0 | 0 | 0 | 0 | ✅ |
| 4 | Bass | 160 | 80 | 80 | 0 | 0 | 0 | ✅ |

Humanized (in-scale audit; jittered onsets fall off the strong grid so notes
re-classify weak) → all voices pass: **0 untagged_out / 0 non_resolving /
0 strong_viol**. No tagged ornaments anywhere (bass/pad/harmony/rhythm zero
chromatic; lead fully diatonic, as required).

## 8. Humanization (always-on, style-derived, seeded)

`export_dual` validated + exported the grid-locked `-perfect.mid` FIRST, then
humanized in place, re-validated, exported `-humanized.mid`. Seed = 20261025
(per-voice child seed = seed·101 + row). Chanson profile = 8.0 ms σ / 2.0 ms
layback / 0.45 phrase-corr (lyrical, moderately loose). All shifts
forward-clamped + boundary-clamped → `validate()` passed on BOTH exports.

| voice | timing σ ms | layback ms | mean abs shift (ticks) | max shift (ticks) | mean vel delta |
|---|---|---|---|---|---|
| Oboe | 8.0 | 2.0 | 4.27 | 16 | 5.54 |
| Clarinet | 8.0 | 2.0 | 4.20 | 18 | 5.67 |
| Piano | 8.0 | 2.0 | 4.74 | 14 | 4.00 |
| Strings | 8.0 | 2.0 | 4.68 | 13 | 5.04 |
| Bass | 10.0 | **8.0** | **6.98** | 27 | 4.96 |
| Drums | **2.0** | 0 | **0.99** | 5 | 3.23 |

Invariants hold: drums tightest (2.0 ms, 0.99-ticks mean), bass lays back
(+8 ms, 6.98-ticks mean), melodic voices ~4.2–4.7-ticks mean. All within
profile bounds.

## 9. Zero-drift

All 6 note tracks = **76800 ticks** (= 40 bars × 1920). `drift_ok = True` on
both phase-2 exports and the phase-1 draft. Terminal landmark
`MusicEvent(0,0,sec_len,sec_len)` pins every cell to its section boundary.

## 10. Render + mastering (FluidSynth → `master()` → Opus OGG)

SoundFont: `FluidR3_GM.sf2` (via `soundfont_path()`). Style target =
`target_for_style("Chanson")` = **−14.0 LUFS**. All three MIDIs rendered
(`fluidsynth -ni -g 1.2 -R no -C no`), mastered
(`master(target_lufs=-14, ceiling_db=-1)`), OGG-encoded (libopus voip 48k).

| artifact | LUFS | true peak | peak | silence | dur | wav | ogg |
|---|---|---|---|---|---|---|---|
| perfect | −14.0 | −1.0 dBTP | 0.776 | 5.2% | 108.53 s | 19.1 MB | 762 KB |
| humanized | −14.0 | −1.0 dBTP | 0.752 | 5.3% | 108.54 s | 19.1 MB | 771 KB |
| phase1 | −14.1 | −1.0 dBTP | 0.748 | 32.7%* | 106.67 s | 18.8 MB | 904 KB |

\* phase-1 silence is **expected** — the raw draft is a sparse monophonic frieze
line (213 short notes, no drums/harmony/bass); the per-second RMS map shows
activity (RMS 0.07–0.21) across all 105 seconds, with only the final tail
(secs 105–106) at zero. The full textures (perfect/humanized) show RMS
0.08–0.18 every second → **no mid-track gaps**; their 5.2–5.3% silence is only
the release tail (secs 105–107).

All measured LUFS ≈ −14.0 target; all true peaks = −1.0 dBTP (≤ ceiling).

## 11. Files

| file | size (bytes) |
|---|---|
| MIDI/263-chanson-frieze-canon-phase1.mid | 2045 |
| MIDI/263-chanson-frieze-canon-perfect.mid | 10858 |
| MIDI/263-chanson-frieze-canon-humanized.mid | 10863 |
| Audio/*-perfect.wav / .ogg | 19145260 / 762065 |
| Audio/*-humanized.wav / .ogg | 19145772 / 771449 |
| Audio/*-phase1.wav / .ogg | 18816556 / 904489 |
| Analysis/verify.json / summary.json / grid_visualization.txt | — |
| provenance.json per MIDI artifact | — |

## 12. Verification summary (all real numbers)

- ✅ phase1 off-grid = 213/213 (raw), chromatic fingerprint (off-scale pcs {0,3,5,8,10}, 12 distinct pcs)
- ✅ perfect off-grid = 0/1005; humanized off-grid = 936/1005 (>0)
- ✅ harmony: 0 untagged out-of-scale / 0 non-resolving / 0 strong violations
  (both perfect and humanized, all 5 pitched voices)
- ✅ zero-drift: all 6 tracks 76800 ticks
- ✅ frieze invariants: R₀=R₁₄=1s boundary, R₁₅=0s, positive interior,
  glide-reflection mirror multiset match
- ✅ sizes > 40 bytes (all MIDI)

No fixes required post-verification (single-pass green).
