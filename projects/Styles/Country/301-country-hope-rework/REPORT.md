# 301-country-hope-rework — Nightly Rework Report

## Source
`/opt/data/projects/Styles/Country/001-country-hope-loop` — legacy 8-bar Country
loop (`country-hope-loop-v7.mid`), hand-rolled with raw `mido.MidiTrack()`.

## Audit result (6 standards) — ALL FAILED → redesign required

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (UnitMatrixComposer) | FAIL — raw mido note_on/.save() |
| 2 | Zero-drift | FAIL — 1 meta + 1 merged mono voice track (delta-time bug, 63328 ticks) |
| 3 | Rhythm-grid sync | FAIL — onsets stacked at time=0 |
| 4 | ≥4 voice tracks | FAIL — 5 roles collapsed into 1 channel |
| 5 | Two-phase (phase1 present) | FAIL — no phase1.mid |
| 6 | provenance.json + index.html | FAIL — both missing |

## Decision
**REDESIGN** — rebuild from scratch through `UnitMatrixComposer`, preserving only
the musical identity (genre Country, G-major I-IV-V backbone, 96 BPM, boom-chick
groove, hopeful rising G-B-D arpeggio, acoustic-guitar lead + steel pad + piano +
bass + drums).

## Source identity preserved
- Genre: Country
- Key: G (source labelled "G mixolydian"; its realized I-IV-V uses a D-major V with
  F#, i.e. G major pitch content {G A B C D E F#})
- Tempo: 96 BPM, 4/4
- Backbone: I-IV-V (G-C-D) + vi (Em) + ii (Am)
- Groove: boom-chick (kick 1&3, snare 2&4), bass root→fifth
- Core motif: hopeful ascending major arpeggio G-B-D (1-3-5)
- Instruments: Lead Acoustic Guitar (GM 25), Steel Pad (GM 26), Piano (GM 0),
  Electric Bass (GM 33), Drums (ch 9)

## New piece
- Project: `/opt/data/projects/Styles/Country/301-country-hope-rework/`
- Form: 6 sections, 20 bars (source 8 bars → 2.5× longer, N+3 sections)
- Form map: Intro(2) → Verse(4) → Chorus(4) → Verse2(4) → Bridge(4) → Outro(2)

## Per-section harmonic regions (midpoint roots)
| Section | Bars | Chords | Midpoint root | Quality |
|---------|------|--------|---------------|---------|
| Intro   | 2 | G C | C (IV) | major |
| Verse   | 4 | G C G D | C (IV) | major |
| Chorus  | 4 | C G D G | G (I) | major |
| Verse2  | 4 | Em Em C D | Em (vi) | minor |
| Bridge  | 4 | C Am D G | Am (ii) | minor |
| Outro   | 2 | D G | G (I) | major |

Section roots are drawn from each section's midpoint chord (2nd bar), never
collapsing to bar-0 tonic.

## Variation techniques (8 applied; ≥3 required)
1. **Augmentation** — Intro + Outro: sparse, half-speed long notes, register drop.
2. **Baseline contour** — Verse: I-IV-I-V generative contour walk (arpeggio + neighbor tone).
3. **Diminution + register shift up** — Chorus: denser 16th feel, lead center G5 (79).
4. **Inversion + vi shade** — Verse2: mirrored contour over the Em relative-minor region.
5. **Retrograde + counterline** — Bridge: reversed contour over ii-V-I, piano descending line.
6. **Density rise** — Chorus: full steel pad + piano off-beat comp + crash cymbal.
7. **Counterline** — Bridge: piano descending chord-tone counterline.
8. **Authentic cadence + augmentation** — Outro: V→I resolution at half speed.

## Two-phase architecture
- **Phase 1** (`-phase1.mid`): raw single-voice contour walk, unquantized pitch +
  jittered off-grid rhythm, out-of-key by construction. 1 voice, zero-drift gate pass.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): musicom rules post-process —
  blanket chord-tone quantization per bar (floor t//BAR), 16th-grid snap, voice-leading
  cap (leap ≤ 9), register clamp, dedup — then full 5-voice Country texture.

## Dual-version render (always-on humanization)
- `-perfect` = grid-locked truth (off-grid == 0).
- `-humanized` = country style profile (timing σ 9 ms, velocity σ 6.5, phrase corr 0.5,
  layback 2 ms) + per-instrument DNA (bass lays back 8 ms, drums anchor 2 ms).
- Humanize seed: `20261113`.

## Verification (real numbers)
See `Analysis/verification.json` + `Analysis/summary.json`.

| Metric | phase1 | perfect | humanized |
|--------|--------|---------|-----------|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 38400 | 38400 | 38400 |
| zero-drift | true | true | true |
| off-grid (not mult of 120) | 86 (raw) | **0** | 253 (>0, jitter ran) |
| scale violations | 33 (raw) | **0** | 0 |
| chord violations | 71 (raw) | **0** | 5 (bar-seam jitter only) |
| strong-beat violations | 4 (raw) | 0 | 0 |

## Files
- `MIDI/301-country-hope-rework-phase1.mid`
- `MIDI/301-country-hope-rework-perfect.mid`
- `MIDI/301-country-hope-rework-humanized.mid`
- `Audio/301-country-hope-rework-perfect.ogg`
- `Audio/301-country-hope-rework-humanized.ogg`
- `Analysis/grid_visualization.txt`, `Analysis/verification.json`, `Analysis/summary.json`
- `provenance.json`, `index.html`, `compose.py`, `verify.py`, `render.py`
