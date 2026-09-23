# 102 — Perlin × D Dorian (Extended Rework of 056-perlin-lpc)

## Concept

Nightly rework: selected **056-perlin-lpc** (Experimental, D Dorian, 80 BPM,
Perlin-fBm driven). Audit **failed** (3 standards) → full **redesign**,
preserving musical identity, then extended to a longer, more varied piece.

## Source identity (preserved)

| Element | Value |
|---|---|
| Genre | Experimental |
| Key | **D Dorian** (corrected: C natural, pc 0 — source mislabeled C#) |
| Tempo | 80 BPM |
| Method | Perlin noise fBm (seed 42) → pitch contour / rhythm density / velocity |
| Instruments | Lead=Flute(74), Pad=StringEnsemble(49), Bass=Bass(33), Drums=ch9 |

## Audit result (056-perlin-lpc)

- **PASS** standard 1 (engine: UnitMatrixComposer), 2 (zero-drift: 4 tracks = 23040), 4 (4 voice tracks).
- **FAIL** standard 3 (14 pitched onsets off-grid), 5 (no `-phase1.mid`), 6 (no `provenance.json`).
- Bonus discovery: source emitted 14 off-key notes and mislabeled the scale (declared C#, played C natural in chords).

`redesign_required = true`. Audit JSON: `056-perlin-lpc/Analysis/rework_audit.json`.

## What changed (redesign)

1. **Correct key** — D Dorian pcs `{0,2,4,5,7,9,11}` (C natural).
2. **Degree-space transforms** — all variation operates on scale-degree index,
   so output never leaves the key (source's chromatic transposition broke diatonicism).
3. **Two-phase export** — raw `-phase1.mid` (single lead, diatonic, pre-rules) +
   rules-processed full `.mid`.
4. **Per-section harmonic regions** — each section has its own 4-chord progression;
   section root taken from midpoint chord (never the bar-0 tonic trap).
5. **Rhythm-grid snap** — every pitched onset on 480/240/120/960 grid; dedup collided `(tick,pitch)`.
6. **provenance.json + grid_visualization.txt + index.html** sidecars present.

## Variation techniques (6 applied)

| Section | Bars | Harmonic plan | Transform | Technique |
|---|---|---|---|---|
| A Intro | 1–4 | i · VII · i · IV | none | motif exposed, sparse (quarter grid) |
| B Verse | 5–8 | i · IV · v · i | transpose (+3 deg) | **transposition** up a 4th |
| C Chorus | 9–12 | IV · i · VII · IV | octave_up | **register shift** +8ve + **density rise** (16th grid) |
| D Bridge | 13–16 | vi° · III · v · VII | retrograde | **retrograde** (pitch sequence reversed) |
| E Development | 17–20 | i · i · IV · IV | invert | **inversion** (contour mirrored) + density |
| F Outro | 21–24 | IV · VII · i · i | augment | **augmentation** + register down |

Section roots (midpoint): D · A · C · A · G · D — never barred to degree i.

## Verification (read-only mido audit)

- Phase-2 MIDI: **5 tracks** (1 conductor + **4 voice**), all len **46080** → zero-drift ✓
- Pitched onsets: **321**, off-grid **0** ✓
- Key violations: **0**, chord violations: **0** ✓
- Phase-1 MIDI: single lead, zero-drift ✓ (chord violations expected — it is pre-rules by design)
- Audio render: **79.6 s**, silence **8.1%**, peak **0.631** (not a silent-render trap)

## Files

- `MIDI/102-perlin-dorian-bridge-mirror.mid` — phase 2 (full, rules)
- `MIDI/102-perlin-dorian-bridge-mirror-phase1.mid` — phase 1 (raw draft)
- `Audio/102-perlin-dorian-bridge-mirror.ogg` — Opus render
- `Analysis/grid_visualization.txt`, `provenance.json` sidecars, `index.html`