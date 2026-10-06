# 225 — Country Steel Rework

Nightly musicom rework of **038-steel-guitar-demo** (Country, G major, 90 BPM).

## Source identity (preserved)

- **Genre**: Country
- **Key**: G major
- **Tempo**: 90 BPM
- **Core motif**: steel-guitar slide — bend up a third (`1→3→5` = G→B→D), ascending
  slide contour with one descending reset.
- **Progression**: G–C–D (I–IV–V)
- **Instrumentation**: steel guitar (lead) · acoustic guitar (comp) · acoustic bass · drums.

## Audit result — FAIL (6/6 standards) → redesign

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine, not hand-rolled | FAIL — raw `mido.MidiTrack()`/`note_on` |
| 2 | Zero-drift | FAIL — tracks 30480 vs 34330 ticks |
| 3 | Rhythm-grid sync | FAIL — 448/576 onsets off-grid |
| 4 | ≥4 voice tracks | FAIL — only 2 |
| 5 | Two-phase artifacts | FAIL — no phase1.mid |
| 6 | provenance.json + index.html | FAIL — both missing |

Rebuilt **from scratch** through `UnitMatrixComposer`, keeping only the musical
identity above. Discarded all non-compliant code.

## What changed

- 16 bars → **24 bars**, 2 sections → **5 sections**.
- Hand-rolled mido → engine-authored (zero-drift invariant enforced by `validate()`).
- Every pitched note quantized to its bar's chord tone; onsets snapped to 120-tick grid.
- Two-phase: raw jittered draft (phase1) + rules-processed arrangement (phase2).

## Form (24 bars)

| Section | Bars | Chords | Lead variation |
|---------|------|--------|----------------|
| Intro | 0–1 | G · G | sparse 1→3→5 hook |
| Verse | 2–9 | G C D G / C G D G | 8th-note arpeggios, low register |
| Chorus | 10–17 | C G Am D / C G D G | **register shift +octave**, dense |
| Bridge | 18–21 | Em C Am D | **retrograde** descent, minor coloring |
| Outro | 22–23 | C G | **augmentation** (long notes), tonic resolve |

## Variation techniques (6)

1. **Register shift** — chorus lead transposed up an octave (79–88 vs 64–79).
2. **Retrograde** — bridge reverses the hook contour (1→3→5 becomes 5→3→1 descent).
3. **Augmentation** — outro lead + bridge/outro bass in whole/half notes.
4. **Counterline** — fiddle (violin) enters in chorus (sustained chord-tone pads)
   and answers in bridge.
5. **Per-section harmonic regions** — each section own progression (midpoint roots:
   Intro=G, Verse=C, Chorus=C, Bridge=Am, Outro=G).
6. **Density rise** — drums: sparse hats (intro) → backbeat (verse) → 16th hats
   (chorus) → breakdown (bridge).

## Verification (read-only mido)

- phase2: **5 voice tracks, all 46080 ticks** (zero-drift OK)
- off-grid pitched onsets: **0**
- scale violations (out of G major): **0**
- chord violations (non chord-tone of own bar): **0**

## Files

- `MIDI/225-country-steel-rework-phase1.mid` — raw draft (single voice, pre-rules)
- `MIDI/225-country-steel-rework.mid` — rules-processed full arrangement
- `Audio/225-country-steel-rework.ogg` — FluidSynth render
- `Analysis/grid_visualization.txt`, `Analysis/verify.json`
- `Scripts/compose.py` — engine-authored generator
