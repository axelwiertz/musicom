# 267 — Blues Interval Exchange (Method 121 IETC)

**Nightly composition job — autonomous two-phase composition. 2026-10-25.**

## 1. Selection (LAYERED METHODOLOGY)

| axis | pick |
|---|---|
| style | **Blues** (random from `/opt/data/projects/Styles/` genre folders) |
| method | **121 — Interval Exchange Transformation Composition (IETC)** |
| layer | **concrete** (Rules-Based / deterministic-ergodic) |
| form | **`blues-12`** — `pick_form("Blues")` (style hint `"blues"` → `blues-12`), sections `['Blues']`, `[12]` bars |
| key | **Ab natural minor (aeolian)**, tonic pc 8, scale `[8,10,11,1,3,4,6]` |
| tempo | 100 BPM, 4/4, 480 ticks/beat, BAR = 1920 |

Method was **not** in the last-7-days set (002, 023, 028, 043, 051, 053, 065,
069, 075, 082, 091, 098, 104/ABS-002, 107, 111, 113) — exercised a fresh
concrete method this night.

## 2. Method — Interval Exchange Transformation (IETC)

A 7-block interval exchange partitions the unit circle `[0,1)` into 7 blocks,
one per scale degree of Ab natural minor, whose **widths encode tonal
gravity** (tonic widest, then 5th, 4th, b3, b7, b6, 2nd):

| degree | pc | width (tonal gravity) |
|---|---|---|
| 1 (tonic) | 8 (Ab) | 0.279112 |
| 2 | 10 (Bb) | 0.049841 |
| b3 | 11 (Cb) | 0.139556 |
| 4 | 1 (Db) | 0.149524 |
| 5 | 3 (Eb) | 0.201035 |
| b6 | 4 (Fb) | 0.060310 |
| b7 | 6 (Gb) | 0.120621 |

- permutation `π = [3,4,5,6,0,1,2]` (rotation-type IET, S₃,₄).
- **rotation number α = Σ(widths of blocks 4–6) = 1/φ² = 0.38196601125** — the
  golden-ratio² inverse, chosen IRRATIONAL so the orbit is aperiodic and
  uniquely ergodic.
- **Unique ergodicity ⇒ width IS tonal gravity**: the time-average of the orbit
  visits each block with frequency exactly equal to its width, from every seed.

**Ergodic verification (real number):** `max |freq − width| = 5.42e-06` over
400,000 iterates (compose.py). The raw draft's pitch-class histogram already
trends toward the widths (tonic modal: 12/57, 5th 13/57, …).

## 3. Harmony — 12-bar minor blues (diatonic m7 in Ab natural minor)

```
bar:  0    1    2    3    4    5    6    7    8    9    10   11
      i7   i7   i7   i7   iv7  iv7  i7   i7   v7   iv7  i7   i7
```

- i7 = Ab–Cb–Eb–Gb (pcs {8,11,3,6})
- iv7 = Db–Fb–Ab–Cb (pcs {1,4,8,11})
- v7 = Eb–Gb–Bb–Db (pcs {3,6,10,1})

All chord tones are diatonic to Ab natural minor (no borrowed/dominant-7th
alteration → clean tiered harmony audit).

## 4. Voices (instrument registry — source of truth)

| voice | instrument | GM prog | channel | role |
|---|---|---|---|---|
| Harmonica | Harmonica | 22 | 0 | lead (IET degree stream) |
| Organ | Drawbar Organ | 16 | 1 | comp (sustained m7 pad) |
| Bass | Double Bass | 43 | 2 | shuffle bass (dotted-8th+16th lilt) |
| Drums | Drum Kit | 0 | 9 | backbeat (kick 1&3, snare 2&4, swung hats) |

## 5. Two-phase architecture

**Phase 1 — raw IET draft** (single harmonica, NO harmony): the IET orbit is
mapped degree → pitch class → pitch with register drift, onsets placed on 8th
slots with ±40-tick jitter (off-grid), durations 0.85–1.25×eighth. Result:
**57 notes, 56/57 off-grid, 57/57 in-scale** — the raw degree stream, pre-rules.

**Phase 2 — rules post-process**: grid-lock every onset to the 16th grid (120),
then **tiered weight-aware snap** via `ScaleQuantizer.tiered_quantize` +
`classify_weight` (STRONG_GRID = beats 1&3 = (0,960)):

- **strong** onset → snap to nearest scale degree THEN nearest chord tone
  (hard in-scale AND in-chord);
- **weak** onset → snap to nearest scale degree only (in-scale).

plus full blues texture: organ pads the root-position m7, bass runs a
dotted-8th+16th shuffle (all 16th-aligned, so the grid audit stays 0), drums
lock the backbeat. Lead is chromatic-free (the tiered discipline is exercised
as strong→chord / weak→scale; no ornament tags were needed).

## 6. Verification (real numbers)

### Grid audit (onset % 120 or % 240)

| artifact | off-grid | verdict |
|---|---|---|
| phase1 | 56/57 | raw (expected) |
| **perfect** | **0** | grid-locked ✓ |
| **humanized** | **187** | humanizer ran (off-grid > 0) ✓ |

### Tiered harmony audit (`workflows.pitch_audit.audit_voice`, strict chord for BOTH)

Every pitched voice (ch 0/1/2; ch 9 drums excluded by role):

| artifact | ch0 (57) | ch1 (48) | ch2 (96) | verdict |
|---|---|---|---|---|
| perfect | 0/0/0 | 0/0/0 | 0/0/0 | **all pass** ✓ |
| humanized | 0/0/0 | 0/0/0 | 0/0/0 | **all pass** ✓ |

`untagged_out_of_scale` / `tagged_non_resolving` / `strong_violations` = 0
everywhere. (Humanization jitters timing/velocity only — never pitch — so the
humanized twin passes the same strict chord audit.)

### Zero-drift

`validate()` passed for phase1 + both phase-2 exports; MIDI readback: all 4
voice tracks = **23040 ticks** (12 bars) exactly. ✓

### Humanization DNA (blues profile: timing 10 ms, vel 7, layback 3 ms, phrase_corr 0.55; per-role DNA overrides)

master seed `hz_seed = 20261026`, per-voice child seed `seed*101+row`:

| voice | seed | mean |abs shift| max shift | vel Δ | profile |
|---|---|---|---|---|---|
| Harmonica | 2046363626 | 4.79 ticks | 18 | 5.79 | blues 10 ms (style) |
| Organ | 2046363627 | 6.48 ticks | 16 | 4.48 | blues 10 ms (style) |
| Bass | 2046363628 | 7.32 ticks | 20 | 4.82 | blues 10 ms + layback 8 ms |
| Drums | 2046363629 | 1.10 ticks | 4 | 3.21 | 2 ms anchor, 0 layback |

Role order holds: drums tightest (1.1), bass lays back (7.3), lead mid (4.8).

### Render + master (FluidSynth `-R no -C no` → `master()` → Opus)

Style target **−14.0 LUFS** (`target_for_style("blues")`), ceiling −1 dBTP:

| artifact | integrated LUFS | true peak | peak | silence | dur |
|---|---|---|---|---|---|
| perfect | −14.08 | −1.0 dBTP | 0.8899 | 12.9% | 33.82 s |
| humanized | −14.08 | −1.0 dBTP | 0.8848 | 12.64% | 33.82 s |
| phase1 | −14.00 | −2.4 dBTP | 0.7585 | 34.83% | 30.97 s |

phase1's 34.8% silence is the expected sparseness of a solo harmonica raw
draft (57 notes, no accompaniment) — not a mid-track dropout bug (per-second
RMS map in `Audio/render_stats.json` shows continuous note activity, no
abrupt gaps). Perfect/humanized sit at ~13% silence (natural note gaps +
tail), well under the 30% suspicion threshold.

## 7. Files

```
MIDI/267-blues-interval-exchange-phase1.mid          (580 B)  + provenance
MIDI/267-blues-interval-exchange-perfect.mid         (2799 B) + provenance
MIDI/267-blues-interval-exchange-humanized.mid       (2820 B) + provenance
Audio/267-blues-interval-exchange-{perfect,humanized,phase1}.wav (5.5–6 MB, mastered)
Audio/267-blues-interval-exchange-{perfect,humanized,phase1}.ogg (249–258 KB, Opus)
Audio/render_stats.json
Analysis/summary.json
Analysis/verify.json
Analysis/grid_visualization.txt
compose.py  verify.py  render.py  grid_viz.py
```

## 8. What to listen for

- The **lead** is a single deterministic orbit — no RNG after the seed; the
  same seed reproduces it exactly. Its pitch-class mix IS the tonal-gravity
  widths (tonic + 5th dominate), which is why it "wants" to resolve to Ab even
  while wandering.
- **Bars 0–3** (i7) vs **4–5** (iv7) vs **8** (v7): the strong beats snap into
  the current chord, so the harmony shift is audible as the lead's strong-note
  set changes (Ab/Cb/Eb/Gb → Db/Fb/Ab/Cb → Eb/Gb/Bb/Db).
- **Shuffle lilt**: bass + hats use a dotted-8th+16th swing (grid-clean
  approximation of triplet swing) — the "chunka-chunka" is in the 16th-aligned
  lilt, not true 320-tick triplets (which would break the grid audit).
- **A/B humanized vs perfect**: the humanized twin has 187 off-grid onsets and
  looser timing (drums still tight, bass lagging behind the beat) — the
  "human feel" layer.

## 9. Fixes / decisions applied

- Rational widths would have made the IET **periodic** (finite permutation) and
  broken exact ergodicity; switched to φ²-based irrational widths
  (rotation number α = 1/φ²) → error 5.4e-6 instead of 0.01.
- True triplet swing (320-tick "and") is off the 8th/16th grid; used the
  dotted-8th+16th lilt (onsets 0/360) instead so the grid audit stays 0.
- Lead register pinned to Harmonica sweet spot (64–79); bass roots in Double
  Bass sweet spot (40–55); organ voicing 55–72.
