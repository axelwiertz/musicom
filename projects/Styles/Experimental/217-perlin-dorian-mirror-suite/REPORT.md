# 217 — Perlin × D Dorian — Mirror Suite (Extension of 102)

## Concept

Nightly rework: selected **102-perlin-dorian-bridge-mirror** (Experimental,
D Dorian, 80 BPM, Perlin-fBm driven). Audit **passed all 6 standards** →
**extension** (no redesign): keep the musical identity, use 102 as the DNA
seed, and compose a NEW LONGER + MORE VARIED piece.

## Source identity (preserved)

| Element | Value |
|---|---|
| Genre | Experimental |
| Key | **D Dorian** — pcs `{0,2,4,5,7,9,11}` (D E F G A B C) |
| Tempo | 80 BPM |
| Method | Perlin noise fBm (seed 42) → pitch contour / rhythm density / velocity |
| Instruments | Lead=Flute(74), Pad=StringEnsemble(49), Bass=Bass(33), Drums=ch9 |

## Audit result (102-perlin-dorian-bridge-mirror)

All **6 standards PASS**:

1. Engine — `compose.py` uses `UnitMatrixComposer` ✓
2. Zero-drift — 4 voice tracks, all len 46080 ✓
3. Rhythm-grid sync — 321 pitched onsets, **0 off-grid** ✓
4. Voice tracks — 4 (Lead/Pad/Bass/Drums) ✓
5. Two-phase — both `.mid` and `-phase1.mid` present ✓
6. Sidecars — `provenance.json` + `index.html` present ✓

`redesign_required = false`. Audit JSON written to
`102-perlin-dorian-bridge-mirror/Analysis/rework_audit.json`.

## What changed (extension)

1. **Form** — 6 sections × 4 bars (24 bars) → **8 sections × 4 bars (32 bars)**.
2. **+1 voice** — added a **Counter** line (Trumpet, ch3) that plays an
   imitative **canon** of the lead in the Development + Climax sections.
3. **+3 variation techniques** — added **diminution** (C), **canon/counterline**
   (F/G), and split **register shift** vs **density rise** into separate
   sections. 8 distinct techniques total (was 5).

## Variation techniques (8 applied)

| Section | Bars | Harmonic plan | Transform | Technique |
|---|---|---|---|---|
| A Intro | 1–4 | i · VII · i · IV | none | motif exposed, sparse (quarter grid) |
| B Verse | 5–8 | i · IV · v · i | transpose (+3 deg) | **transposition** up a 4th |
| C Verse2 | 9–12 | v · i · IV · i | diminution | **diminution** (rhythm compressed) |
| D Chorus | 13–16 | IV · i · VII · IV | octave_up | **register shift** +8ve + **density rise** (16ths) |
| E Bridge | 17–20 | vi° · III · v · VII | retrograde | **retrograde** (pitch sequence reversed) |
| F Development | 21–24 | i · i · IV · IV | invert | **inversion** + **canon** counterline |
| G Climax | 25–28 | IV · VII · i · i | octave_up | register + **density** + **canon** |
| H Outro | 29–32 | i · VII · IV · i | augment | **augmentation** + register down |

Each section has its own 4-chord harmonic region; no section is barred to
degree i (the bar-0 tonic bug is avoided — every bar within a section uses
its own chord degree). Section roots taken from the midpoint chord.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw Perlin-fBm draft, single lead voice,
  diatonic-only, unquantized to chord tones. Pre-rules.
- **Phase 2** (`.mid`): musicom rules — per-bar chord-tone quantization
  (`t // BAR` floor), rhythm-grid snap (120/240), key discipline, register
  clamp, dedup collided `(tick,pitch)`.

## Verification (read-only mido audit)

- Phase-2 MIDI: **6 tracks** (1 conductor + **5 voice**), all len **61440**
  (32 bars × 1920) → zero-drift ✓
- Pitched onsets: **560**, off-grid **0** ✓
- Scale violations: **0**, chord violations: **0** ✓
- Phase-1 MIDI: single lead, zero-drift ✓ (245 raw onsets, diatonic)
- Audio render: **103.6 s**, silence **6.4%**, peak **0.759**, RMS **−18.0 dBFS**
  (not a silent-render trap)

## Files

- `MIDI/217-perlin-dorian-mirror-suite.mid` — phase 2 (full, 5 voices, rules)
- `MIDI/217-perlin-dorian-mirror-suite-phase1.mid` — phase 1 (raw draft)
- `Audio/217-perlin-dorian-mirror-suite.ogg` — Opus render
- `Audio/217-perlin-dorian-mirror-suite.wav` — FluidSynth PCM
- `Analysis/grid_visualization.txt`, `provenance.json` sidecars, `index.html`
