# 311-knight-tour-soul — REPORT

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-18 · Method 126 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Soul** (random from 44 genre dirs, seeded 20261118) |
| Method | **126 — Knight's Tour Composition (KTC)** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due — last abstract was 134 on 11-12) |
| Form | **verse-chorus** → `Intro·Verse·Chorus·Verse2·Chorus2·Outro`, bars `[4,8,8,8,8,4]` = **40 bars** (from `pick_form("soul")`) |
| Key | **F major** (ionian), pc `{5,7,9,0,2,4,6}`, tonic F |
| Tempo | 96 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120 |

Methods excluded (used last 7 days): 001, 007, 012, 015, 019, 023, 025, 032,
035, 041, 053, 069, 075, 120, 132, 134.

## 2. Method 126 — Knight's Tour Composition (self-contained model)

A knight's tour is a **Hamiltonian path** on the knight graph of an m×n board
(rows = pitch, columns = time-slot classes): every cell is visited exactly
once, so the 2D aggregate holds — each of the 8 scale-degree rows appears
exactly n times, no literal pitch-slot repeat. Solved with **Warnsdorff's rule
(min-onward-moves) + seeded Pohl tie-break + backtracking fallback** (~O(N),
instant for 8×8 and 8×4).

Musical mapping:
- **Row → pitch**: 8 rows = one octave of F major, F4…F5 (lead register).
- **Tour order → time**: step k → onset `k·8th` (monotonic; the board's
  column coordinate is the *time-slot class*).
- **Knight signature |Δr|·|Δc| = 2** anti-correlates melodic motion with
  duration: a **leap** (|Δr|=2) pairs with |Δc|=1 → *short* note; a **step**
  (|Δr|=1) pairs with |Δc|=2 → *long* note. Encoded as ±1 sixteenth duration
  in the raw draft.
- **Board-transpose = dual voice**: transposing a tour (swap row↔column) is
  itself a valid tour — invertible counterpoint. The **Vox** backing line maps
  the tour's *column* (time-slot class) into pitch space, a distinct
  counter-melody in Chorus/Chorus2.
- Per-section tours: Intro 8×4, Verse 8×8, Chorus 8×8, Verse2 8×8 (inverted
  contour), Chorus2 8×8, Outro 8×4 (inverted). Seeds 1–6.

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single Tenor-Sax voice, the raw knight-tour
  stream — float pitch (scale-degree row + σ=0.35 jitter), off-grid onsets
  (uniform ±25 ticks), duration from the knight signature. 320 raw notes.
  Own `validate()` gate; pre-rules by design.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): musicom rules —
  `ScaleQuantizer.tiered_quantize` (strong → scale *then* chord tone; weak →
  scale only), 8th-grid snap, `(start_tick, pitch)` dedup keeping longest,
  register enforcement, voice-leading on the comp triads
  (`optimize_voice_leading` + parallel/hidden-fifth correction), 5-voice Soul
  texture.

## 4. Voices + instruments (instrument_registry)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Tenor Sax | 66 | 0 | Knight's-tour melody |
| Rhodes | Electric Piano 1 | 4 | 1 | Comp triads (voice-led) |
| Bass | Electric Bass (finger) | 33 | 2 | Root (beat 1) + fifth (beat 3) |
| Vox | Choir Aahs | 53 | 3 | Transpose-tour counter (chorus) / pad (elsewhere) |
| Drums | Drum Kit | 0 | 9 | Backbeat: kick 1&3, snare 2&4, 8th hats (open on 4-&) |

Voice-leading corrections: **0** (I–vi–IV–V is already smooth in F).

## 5. Harmony (F major, per-section regions)

| Section | Bars | Progression |
|---|---|---|
| Intro | 4 | F · Bb · F · C |
| Verse | 8 | F · Dm · Bb · C · F · Dm · Gm · C |
| Chorus | 8 | F · Dm · Bb · C · F · Bb · C · F |
| Verse2 | 8 | F · Dm · Bb · C · F · Dm · Gm · C |
| Chorus2 | 8 | F · Dm · Bb · C · F · Bb · C · F |
| Outro | 4 | F · Bb · C · F |

## 6. Verification (read-only mido audit, `verify.py` → VERIFY_OK)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| tracks | 1 | 5 | 5 |
| zero-drift (equal track length) | ✅ 76800 | ✅ 76800 | ✅ 76800 |
| pitched notes | 320 | 694 | 694 |
| drum notes | 0 | 480 | 480 |
| **off-16th (120)** | 306 (raw) | **0** | **983** (jitter ran) |
| untagged out-of-scale | 34 (raw) | **0** | **0** |
| non-resolving ornaments | 0 | **0** | **0** |
| strong violations | 2 (raw) | **0** | **0** |

Grid audit (perfect layer, pre-humanization): **0 / 1174** pitched onsets
off-grid (16th). Harmony audit per voice: `untagged_out_of_scale = 0`,
`tagged_non_resolving = 0`, `strong_violations = 0` — **all pass**. The
phase-1 draft is intentionally off-grid/off-scale (raw by construction).

## 7. Humanization (always-on, style-derived, seeded)

- `hz_seed = 63699` (md5 of style+key+bpm+bars+project).
- Style profile `soul` → melodic voices timing σ = 8 ms (6.144 ticks @96 BPM).

| Voice | mean |Δshift| ticks | max |Δshift| | mean |Δvel| | timing σ ticks |
|---|---|---|---|---|---|
| Lead | 4.975 | 19 | 5.34 | 6.144 |
| Rhodes | 5.667 | 15 | 3.90 | 6.144 |
| Bass | 6.112 | 14 | 3.28 | 3.84 (5 ms + 8 ms layback) |
| Vox | 4.256 | 19 | 6.23 | 6.144 |
| Drums | 0.921 | 3 | 3.27 | 1.536 (2 ms anchor) |

Drums anchor the grid (tightest); bass lays back (largest mean shift, 8 ms
layback); lead is loose-but-bound. Zero-drift preserved after humanization
(forward-clamp, boundary-clamp, terminal landmark pinned).

## 8. Render + master (background, `render.py`)

Soundfont: `FluidR3_GM.sf2` (via `discover_soundfont()`), fluidsynth CLI
`-ni -g 1.2 -R no -C no`. Each WAV mastered to `target_for_style("soul")`
(**−13.0 LUFS** — `soul` IS in `GENRE_LUFS`, between jazz/blues −14 and
funk −13) at −1 dBTP ceiling, then ffmpeg → Opus OGG (`-b:a 48k`).

| Version | LUFS | dBTP | silence | RMS mean | wav bytes | ogg bytes |
|---|---|---|---|---|---|---|
| phase1 | −13.08 | −1.0 | 7.9% | 0.1667 | 18.0 MB | 950 KB |
| perfect | −13.03 | −1.0 | 4.4% | 0.1581 | 18.5 MB | 813 KB |
| humanized | −13.04 | −1.0 | 4.4% | 0.1579 | 18.5 MB | 809 KB |

All three ≈ target (−13.0) within ±0.1 LUFS, true peak −1.0 dBTP (≤ ceiling),
silence 4.4% (phase1 7.9% — the raw draft's short leap-notes leave more air;
both far below the 30% suspect threshold). Mid-track RMS profile healthy (no
gaps): RMS mean ~0.16, max ~0.21–0.24.

## 9. Files

```
Styles/Soul/311-knight-tour-soul/
├── compose.py  verify.py  render.py
├── README.md  REPORT.md  index.html
├── MIDI/  311-knight-tour-soul-{phase1,perfect,humanized}.mid (+ .provenance.json)
├── Audio/ 311-knight-tour-soul-{phase1,perfect,humanized}.ogg (+ .wav)
└── Analysis/ compose_summary.json  verification.json  render_report.json
              grid_visualization.txt  grid_visualization_phase1.txt
```

MIDI sizes: phase1 2632 B · perfect 9884 B · humanized 9885 B.

## 10. Fixes / notes

- None required on first run — grid, harmony, zero-drift, and humanization
  gates all passed. `voice_leading_corrections = 0` (progression already
  smooth).
- `target_for_style("soul")` = **−13.0 LUFS** (soul is in `GENRE_LUFS`);
  all three renders landed within ±0.1 of target, true peak −1.0 dBTP.
- Phase-1 raw draft intentionally off-grid (306/320) and off-scale (34) —
  that is the pre-rules character the two-phase contract preserves.
