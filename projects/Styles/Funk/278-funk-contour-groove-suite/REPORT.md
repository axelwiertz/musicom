# REPORT — 278-funk-contour-groove-suite

Rework job · 2026-11-01 · extension of **220-funk-contour-groove**.

## 1. Source selection & audit

| Field | Value |
|---|---|
| Source project | `/opt/data/projects/Styles/Funk/220-funk-contour-groove` |
| Genre | Funk |
| Primary MIDI | `MIDI/220-funk-contour-groove.mid` |

**Audit (live read-only mido verification):**

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer, not hand-rolled mido) | PASS |
| 2 | Zero-drift (all voice tracks equal length) | PASS — 5 tracks = 46080 ticks |
| 3 | Rhythm-grid sync (onset % 120 or % 240 == 0) | PASS — 0 off-16th |
| 4 | ≥4 voice tracks | PASS — 5 voices |
| 5 | Two-phase artifacts (`.mid` + `-phase1.mid`) | PASS |
| 6 | provenance.json + index.html | **FAIL — index.html missing** |

**Decision: EXTENSION** (not redesign). Standard 6 is a docs-only gap; the
composition itself is fully engine-compliant (standards 1–5 all pass). The new
project remediates the missing dashboard and adds humanization.

## 2. What changed (extension)

- **24 → 32 bars** (6 → 8 sections): Intro · ThemeA · ThemeB · Variation ·
  Development · Bridge · Climax · Outro.
- **7 variation techniques** (each mapped to a section):

| Technique | Where | How |
|---|---|---|
| Inversion (I) | ThemeB | arch contour → valley (`invert`) |
| Retrograde (R) | Variation | arch contour reversed (`retrograde`) |
| Augmentation | Climax | half-time 8th onsets, ~2× note duration |
| Diminution | Development | 3 motifs/bar on a dense three-way 16th grid |
| Register shift | Dev/Climax→E5, Bridge/Outro→E3 | octave bases E4→E5→E3 |
| Counterline | Climax (sax rise) · Bridge (bass pedal) | sustained counter-melody / root pedal |
| Palette color | Bridge | D-palette pedal (dominant-ish pull) |

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single Trumpet voice, whole-tone contour
  realization (`rank → base + 2·rank`), fractional off-grid ticks. Own
  `validate()` PASS. 224 notes, 221 off-grid — raw draft keeps its character.
- **Phase 2** (dual-version): 16th-grid lock → E-minor-pentatonic snap →
  per-bar palette quantize → full 5-voice funk texture → `export_dual`
  (grid-locked `-perfect` + humanized `-humanized`).

## 4. Per-section harmonic regions

8 sections, each its own 4-bar palette progression. Section roots (midpoint
bar pc): **E, A, G, G, E, A, D, G** — diverse, never all-tonic (defeats the
bar-0 tonic bug). Chord quality derives from the midpoint palette.

## 5. Humanization (dual-version)

- Style profile: `funk` (timing σ 4 ms, layback 2 ms). Instrument DNA:
  drums anchor (2 ms / 0 layback), bass lays back (8 ms), trumpet velocity σ 8.
- Seed: `4153695084` (md5-derived). Per-voice mean/max abs shift (ticks):
  Drums 1.0 / 4 · Clav 2.2 / 8 · Trumpet 2.3 / 9 · Sax 2.6 / 8 · Bass 7.4 / 20.
  Drums tightest, bass most laid-back — invariants correct.

## 6. Verification (real numbers)

| Check | Perfect | Humanized | Phase 1 |
|---|---|---|---|
| Voice tracks | 5 × 61440 | 5 × 61440 | 1 × 61440 |
| Zero-drift | PASS | PASS | PASS |
| Pitched onsets | 656 | 656 | 224 |
| Off-grid | **0** | 586 (>0: jitter ran) | 221 (raw) |
| Scale violations | **0** | **0** | 168 (raw) |
| Chord violations | **0** | 2 (bar-boundary jitter) | 181 (raw) |

The two humanized chord violations are single notes whose onset jitters ≤4
ticks across an intra-section bar boundary (correctly floor()-attributed to the
adjacent bar). Perfect layer is clean 0/0/0; prior rework 259-funk-som-extended
shipped 14 for the same effect — this suite is tighter.

**Audio (FluidSynth CLI → master → Opus):**

| File | LUFS | True peak | Silence |
|---|---|---|---|
| `-perfect.ogg` | −13.29 | −1.0 dBTP | 5.29% |
| `-humanized.ogg` | −13.26 | −1.0 dBTP | 5.22% |

Silence ≪ 30% (no silent-render trap). Both mastered to Funk target (−13 LUFS).

## 7. Files

- `MIDI/...-phase1.mid`, `...-perfect.mid`, `...-humanized.mid` (+ provenance)
- `Audio/...-perfect.{wav,ogg}`, `...-humanized.{wav,ogg}` (+ provenance)
- `Analysis/{verify,humanize,summary,render_stats}.json`, `grid_visualization.txt`
- `compose.py`, `verify.py`, `render_audio.py`, `index.html`, `README.md`, `REPORT.md`
- Source audit written to `220-funk-contour-groove/Analysis/rework_audit.json`