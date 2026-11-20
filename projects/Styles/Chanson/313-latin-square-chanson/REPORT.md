# 313-latin-square-chanson — REPORT

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-19 · Method ABS-139 (abstract layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Chanson** (random from 48 genre dirs, seeded 20261119) |
| Method | **ABS-139 — Latin Square & Orthogonal-Array Composition (LSAC)** (Rules-Based) |
| Layer | **abstract** (weekly abstract cadence DUE — last abstract was 134/CSCC on 11-12, seven nights ago) |
| Form | **verse-chorus** → `Intro·Verse·Chorus·Verse2·Chorus2·Outro`, bars `[4,8,8,8,8,4]` = **40 bars** (from `pick_form("chanson")`) |
| Key | **G major** (ionian), pc `{0,2,4,5,7,9,11}`, tonic G |
| Tempo | 112 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120 |

Methods excluded (used last 7 days): 001, 007, 012, 015, 019, 023, 025, 032,
035, 041, 053, 069, 075, 120, 126, 132, 134. Last abstract was ABS-134 on
11-12 → abstract cadence due tonight; ABS-139 (LSAC) selected.

## 2. Method ABS-139 — Latin Square & Orthogonal-Array Composition (abstract)

The piece is laid out as a **Latin square over the UnitMatrix**: rows = voice/
register layers, columns = time-slot classes, symbols = the **7 diatonic scale
degrees** of G major. Two mutually-orthogonal order-7 squares (cyclic, prime
order → MOLS pair via finite-field construction):

```
L[i][j] = (i + j)  mod 7     (pitch-degree square)
M[i][j] = (i + 2j) mod 7     (duration-class square — the orthogonal mate)
```

- **Latin property**: every row and every column of L (and M) is a complete
  aggregate — a permutation of the 7 degrees (verified `_is_latin` both).
- **Orthogonality**: every ordered pair `(degree, duration-class)` occurs
  exactly once across the 7×7 design — a **complete factorial design**
  (verified `_orthogonal`: 49 distinct pairs).
- **Transversal** (Ryser 1967 — odd orders always carry one): the main
  diagonal `L[i][i] = (2i) mod 7 = [0,2,4,6,1,3,5]` is the through-line.

Musical mapping (abstract → concrete):
- **Lead melody** walks L row-major: bar `b` → cell `(b//7, b%7)`; the anchor
  degree = `L[row][col]`, the duration class = `M[row][col]`. Each 7-bar window
  is a complete degree aggregate.
- **Orthogonal square = rhythm**: the duration class drives melodic DENSITY —
  long cells (whole/dotted-half/half → classes 0,1,2) are a single held anchor;
  short cells (classes 3–6) become a 4-note figure (anchor + chord-tone
  response + two in-scale passing notes). 17 long / 23 short cells.
- The 40 bars cover 40 of the 49 design cells; all 40 `(degree, durclass)`
  pairs are distinct (complete factorial over the used window).

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single trumpet voice, the raw Latin-square
  anchor stream — scale-degree note + σ=0.35 pitch jitter, off-grid onsets
  (±25 ticks), orthogonal duration class. 40 raw notes. Own `validate()` gate;
  pre-rules by design.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): musicom rules —
  `ScaleQuantizer.tiered_quantize` (strong → scale *then* chord tone; weak →
  scale only), 8th-grid snap, `(start_tick, pitch)` dedup keeping longest,
  register enforcement, voice-leading on the comp triads
  (`optimize_voice_leading` + parallel/hidden-fifth correction), 5-voice
  Chanson texture.

## 4. Voices + instruments (instrument_registry)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Trumpet | 56 | 0 | Latin-square melody (anchor + density figure) |
| Accordion | Accordion | 21 | 1 | Musette comp: sustained voice-led triads |
| Guitar | Steel Acoustic Guitar | 25 | 2 | 8th-note strum (down/up accents) |
| Bass | Double Bass (contrabass) | 43 | 3 | Root (beat 1) + fifth (beat 3) |
| Drums | Drum Kit | 0 | 9 | March-like 4/4: kick 1&3, snare 2&4, 8th hats |

Voice-leading corrections: **0** (G-major progression already smooth).

## 5. Harmony (G major, per-section regions)

| Section | Bars | Progression |
|---|---|---|
| Intro | 4 | G · C · D · G |
| Verse | 8 | G · Em · C · D · G · Em · Am · D |
| Chorus | 8 | G · C · D · G · Em · Am · D · G |
| Verse2 | 8 | G · Em · C · D · G · Em · Am · D |
| Chorus2 | 8 | G · C · D · G · Em · Am · D · G |
| Outro | 4 | G · C · D · G |

## 6. Verification (read-only mido audit, `verify.py` → VERIFY_OK)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| tracks | 1 | 5 | 5 |
| zero-drift (equal track length) | ✅ 76800 | ✅ 76800 | ✅ 76800 |
| pitched notes | 40 | 1099 | 1099 |
| drum notes | 0 | 480 | 480 |
| **off-16th (120)** | 35 (raw) | **0** | **1361** (jitter ran) |
| untagged out-of-scale | 4 (raw) | **0** | **0** |
| non-resolving ornaments | 0 | **0** | **0** |
| strong violations | 2 (raw) | **0** | **0** |

Grid audit (perfect layer, pre-humanization): **0 / 1579** pitched onsets
off-grid (16th). Harmony audit per voice: `untagged_out_of_scale = 0`,
`tagged_non_resolving = 0`, `strong_violations = 0` — **all pass**. The
phase-1 draft is intentionally off-grid/off-scale (raw by construction).

## 7. Humanization (always-on, style-derived, seeded)

- `hz_seed = 24702` (md5 of style+key+bpm+bars+project).
- Style profile `chanson` → melodic timing σ = 8 ms (7.168 ticks @112 BPM).

| Voice | mean |Δshift| ticks | max |Δshift| | mean |Δvel| | timing σ ticks |
|---|---|---|---|---|---|---|---|
| Lead | 4.242 | 12 | 6.32 | 7.168 |
| Accordion | 5.242 | 17 | 4.76 | 7.168 |
| Guitar | 5.389 | 20 | 4.91 | 7.168 |
| Bass | 8.125 | 19 | 4.79 | 8.96 (8 ms layback) |
| Drums | 1.110 | 4 | 3.39 | 1.792 (2 ms anchor) |

Drums anchor the grid (tightest); bass lays back (largest mean shift, 8 ms);
lead/accordion/guitar are loose-but-bound. Zero-drift preserved after
humanization (forward-clamp, boundary-clamp, terminal landmark pinned).

## 8. Render + master (background, `render.py`)

Soundfont: `FluidR3_GM.sf2` (via `discover_soundfont()`), fluidsynth CLI
`-ni -g 1.2 -R no -C no`. Each WAV mastered to `target_for_style("chanson")`
(**−14.0 LUFS**, chanson → the −14 fallback) at −1 dBTP ceiling, then
ffmpeg → Opus OGG (`-b:a 48k`).

| Version | LUFS | dBTP | silence | RMS mean | wav bytes | ogg bytes |
|---|---|---|---|---|---|---|
| phase1 | −14.15 | −1.0 | 52.1% | 0.1057 | 15.5 MB | 537 KB |
| perfect | −14.08 | −1.0 | 5.3% | 0.1361 | 16.0 MB | 688 KB |
| humanized | −14.05 | −1.0 | 5.4% | 0.1370 | 16.0 MB | 692 KB |

All three ≈ target (−14.0) within ±0.15 LUFS, true peak −1.0 dBTP (≤ ceiling).
Perfect/humanized silence 5.3% (healthy — full 5-voice texture). Phase1 silence
52.1% is EXPECTED and by-design: the raw draft is a single monophonic trumpet
carrying 40 Latin-square anchor notes whose orthogonal duration classes total
≈45% of the timeline (the concrete layer fills the rest). RMS profile healthy
(mean 0.11–0.14, max 0.20–0.25 — no dead mid-track gaps).

## 9. Files

```
Styles/Chanson/313-latin-square-chanson/
├── compose.py  verify.py  render.py
├── README.md  REPORT.md  index.html
├── MIDI/  313-latin-square-chanson-{phase1,perfect,humanized}.mid (+ .provenance.json)
├── Audio/ 313-latin-square-chanson-{phase1,perfect,humanized}.ogg (+ .wav)
└── Analysis/ compose_summary.json  verification.json  render_report.json
              grid_visualization.txt  grid_visualization_phase1.txt
```

MIDI sizes: phase1 444 B · perfect 12253 B · humanized 12286 B.

## 10. Fixes / notes

- None required on first run — grid, harmony, zero-drift, and humanization
  gates all passed. `voice_leading_corrections = 0`.
- The Latin-square construction was verified in-script (Latin rows/cols,
  MOLS orthogonality, diagonal transversal) before any note was written.
- Phase-1 raw draft intentionally off-grid (35/40) and off-scale (4) — the
  pre-rules character the two-phase contract preserves.
