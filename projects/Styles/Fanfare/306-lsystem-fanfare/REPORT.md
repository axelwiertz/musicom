# 306-lsystem-fanfare — REPORT

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-15 · Method 019 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Fanfare** (random from 43 style dirs) |
| Method | **019 — L-System Algorithmic Composition** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due — last abstract was 300 on 11-12, three days ago) |
| Form | **cinematic-build** → `Intro·Build·Rise·Peak·Resolve`, bars `[4,8,8,8,4]` = **32 bars** (from `pick_form("fanfare")`; no style hint → full non-loop palette → cinematic-build) |
| Seed | 20261115 · humanize seed 66139 |

Methods excluded (used last 7 days): 001, 007, 012, 015, 023, 032, 041, 053, 075, 120, 132, 134.

## 2. Musical DNA

| Field | Value |
|---|---|
| Key | Bb major (Ionian) = pc {0,2,3,5,7,9,10} |
| Tempo | 120 BPM · 4/4 · 480 TPB · BAR=1920 · 8th=240 |
| Length | 32 bars = 61,440 ticks (~64 s) |

**L-System (method 019)** — D0L grammar, deterministic:
```
axiom  = "C"
rules  = { A -> "ABA",  B -> "BC",  C -> "RA",  R -> "R" }
interp = A=+1 degree (step up), B=-1 (step down), C=+2 (leap up a 4th), R=rest
```
Expanded to **256 symbols** (A=109, B=83, C=36, R=28) = 32 bars of 8th notes.
The rewrite `A → ABA` yields the classic ternary rise–fall–rise fanfare ornament,
self-similarly nested; `C → RA` injects the leap-and-breathe fanfare call.

**Voices (6, from instrument registry):**

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Trumpet | Trumpet | 56 | 0 | L-system lead melody |
| FrenchHorn | French Horn | 60 | 1 | canon (rotated L-system, −12) |
| Brass | Brass Section | 61 | 2 | voice-led triads (pad) |
| Tuba | Tuba | 58 | 3 | bass (roots/fifths) |
| Timpani | Timpani | 47 | 4 | pitched percussion + 16th rolls |
| Drums | GM kit | — | 9 | snare / kick / crash march |

## 3. Progression (Bb major)

| Section | Bars | Degrees (chords) |
|---|---|---|
| Intro | 0-3 | Bb Bb Bb Bb |
| Build | 4-11 | Bb Bb Eb Eb F F Bb Bb |
| Rise | 12-19 | Eb Eb F F Gm Gm F F |
| Peak | 20-27 | Bb Bb Eb F Bb Gm F Bb |
| Resolve | 28-31 | F F Bb Bb (authentic cadence V→I) |

Per-bar degree attribution (floor-bar); section midpoint chord used for the
section root (no bar-0 tonic collapse). Voice-leading on the pad triads:
**0 corrections** needed (parallel-fifths/octaves already clean).

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`, 2027 B): raw L-system walk, single trumpet voice,
  unquantized float pitch (seeded normal jitter) + **off-grid onsets** (±25-tick
  jitter), 228 notes, own composer + validate() gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): tiered quantization
  (`ScaleQuantizer.tiered_quantize` — strong beats → chord tones, weak beats →
  scale tones), 8th-grid snap + dedup, voice-leading on the brass pad, register
  enforcement, 6-voice brass texture. French Horn reads the L-system string
  rotated by register shift (−12) as a self-similar canon.

## 5. Dual-version + humanization (always-on, seeded)

`export_dual` → `-perfect.mid` (grid-locked) + `-humanized.mid` (style fanfare +
per-instrument brass DNA). `hz_seed = 66139`. Per-voice mean/max abs shift
(ticks) + velocity delta:

| Voice | mean shift | max shift | vel Δ | notes |
|---|---|---|---|---|
| Trumpet | 4.19 | 15 | 6.20 | 228 |
| FrenchHorn | 4.45 | 16 | 6.01 | 202 |
| Brass | 4.71 | 13 | 6.84 | 104 |
| Tuba | 4.83 | 18 | 6.39 | 80 |
| Timpani | 4.11 | 17 | 4.44 | 106 |
| Drums | **0.96** | 4 | 2.85 | 84 (anchors) |

Drums anchor the grid (0.96 ticks, tightest); brass voices ~4-5 ticks of timing
slop. Zero-drift safe (forward-clamp + boundary-clamp, terminal landmark pinned).

## 6. Verification (real numbers, read-only mido + `audit_voice`)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| voice tracks | 1 | 6 | 6 |
| track length (ticks) | 61440 | 61440 | 61440 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 228 | 720 | 720 |
| drums (ch9) | 0 | 84 | 84 |
| off-grid (16th=120) | 216 (raw) | **0** | **707** (jitter) |
| off-grid (8th=240) | 216 | 24* | 709 |
| untagged out-of-scale | 89 (raw) | **0** | **0** |
| tagged non-resolving | 0 | 0 | 0 |
| strong-beat violations | 8 (raw) | **0** | **0** |

\* perfect-layer `off-8th = 24` = intentional 16th-note **timpani rolls** at the
Peak/Resolve climax (onsets are multiples of 120, i.e. on the 16th grid — within
the sanctioned 8th/16th grid). All 5 pitched voices pass the tiered pitch
discipline: **0 untagged / 0 non-resolving / 0 strong violations**.

Phase-1 raw violations are expected (unquantized draft, pre-rules). Humanized
off-grid 707/720 proves the humanizer ran; pitch stays 100% in-scale/in-chord.

## 7. Audio (mastered to −14 LUFS, −1 dBTP ceiling)

`target_for_style("fanfare")` = **−14.0** (fanfare not in GENRE_LUFS → fallback;
documented). SoundFont = FluidR3_GM.sf2.

| Version | LUFS | true-peak | silence | OGG |
|---|---|---|---|---|
| phase1 | −14.01 | −1.00 | 4.1% | 642 KB |
| perfect | −14.00 | −1.23 | 4.0% | 513 KB |
| humanized | −14.00 | −1.00 | 4.4% | 510 KB |

Silence < 5% on all three (healthy; no mid-track gaps). True-peaks sit at/below
the −1 ceiling (ceiling, not target). Per-second RMS max 0.17-0.19 (fanfare
brass density).

## 8. Fixes applied during build (audit-driven)

1. Lead chord-tone snap range narrowed to ≤86 — the register clamp was forcing a
   strong-beat Eb-chord snap 87→86 (D, out-of-chord). Removed the upper clamp.
2. French Horn Intro drone: C4 → F4 (open-5th Bb–F, both chord tones).
3. Tuba/Timpani register shift −24 → −12 (was emitting wrong pitch classes and
   clamping to F#=30 outside the key).
4. Timpani pitch = nearest **chord tone** in the 41-55 sweet range (was a
   register shift that broke chord membership).
5. Timpani roll starts at 16th k=1 (removed a k=0 duplicate of the strong hit).
6. Phase-1 onset jitter now stored (was computed then discarded → phase1 came
   out on-grid; restored the raw off-grid character).

## 9. Artifacts

| File | Role |
|---|---|
| `MIDI/306-lsystem-fanfare-phase1.mid` | raw L-system draft |
| `MIDI/306-lsystem-fanfare-perfect.mid` | grid-locked phase 2 |
| `MIDI/306-lsystem-fanfare-humanized.mid` | humanized phase 2 |
| `Audio/*-perfect.ogg` / `*-humanized.ogg` / `*-phase1.ogg` | mastered Opus renders |
| `Analysis/grid_visualization.txt` (+phase1) | rhythm DNA grids |
| `Analysis/compose_summary.json` / `verification.json` / `render_report.json` | metrics |
| provenance sidecars (`.mid.provenance.json`) | per MIDI artifact |
| `index.html` | dashboard (VoltAgent styling) |
| `compose.py` / `render.py` / `verify.py` / `build_dashboard.py` | generators |
