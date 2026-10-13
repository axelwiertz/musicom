# 238 — Neo-Riemannian Afro Drop

**Nightly composition job — 2026-10-12**
**Style:** African | **Method:** 011 Voice-Leading Graph Search | **Layer:** concrete

## Selection

| Field | Value |
|---|---|
| seed | 20261012 |
| layer roll | 0.4066 → **concrete** (~6/7 concrete cadence) |
| method | **011 Voice-Leading Graph Search** (Rules-Based, Neo-Riemannian) |
| style | African |
| form | **intro-break-drop-outro** (Intro 4, Break 8, Drop 8, Outro 4) |
| key | G major (tonic G3 = 55), 4/4, 480 TPB, bar = 1920 ticks |
| bpm | 124 |
| 16th grid | 120 ticks |

## Method interpretation (concrete → engine)

Neo-Riemannian graph traversal to find the **shortest voice-leading path**
between chord cells. Implementation:

1. **Graph** — nodes are the 6 diatonic major/minor triads of G major
   (`I G+`, `ii Am`, `iii Bm`, `IV C+`, `V D+`, `vi Em`). Edges are the
   neo-Riemannian transformations that stay diatonic: **R** (relative) and
   **L** (leading-tone exchange); P leaves the key so is excluded. Edge
   weight = semitone distance of the single moving voice.
2. **Search** — a 24-bar tonal plan is walked with **BFS shortest paths**
   from each chord to the next. Every consecutive target is a single R or L
   step, so each bar is one minimal transformation: **two common tones are
   held, one voice moves by a step** (R = whole tone, L = semitone).
3. **Rules layer (Phase 2)** — grid-snap (120 ticks), per-bar chord-tone
   quantization, register enforcement, voice-led string pad, and a
   `VoiceLeadingRules(style="classical")` parallel/hidden-fifths check.

## Chord path (24 bars)

| Section | Bars | Degrees |
|---|---|---|
| Intro | 1–4 | `I  vi  IV  ii` |
| Break | 5–12 | `IV  vi  I  iii  V  iii  I  vi` |
| Drop | 13–20 | `I  iii  V  iii  I  vi  IV  ii` |
| Outro | 21–24 | `IV  vi  I  I` (bar 24 = held tonic, fermata) |

**Voice-leading step census (23 steps):** 14× R (whole tone), 8× L
(semitone), 1× hold (0). No step moves more than one voice; the parallel /
hidden fifth + octave check reports **0 violations**.

## Voices & instruments (from the instrument registry)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Marimba | 12 | 0 | chord-tone contour / balafon lead |
| Harmony | String Ensemble 1 | 48 | 1 | voice-led block-chord pad (1 chord/bar) |
| Kalimba | Kalimba | 108 | 2 | mbira ostinato (8th-note arpeggio) |
| Bass | Double Bass | 43 | 3 | chord roots, ostinato rhythm |
| Drums | (GM percussion) | — | 9 | bell timeline + shaker + kick/snare/toms |

## Arrangement

- **Intro** — half-note marimba, quarter-note kalimba plucks, bass on 1 & 3,
  shaker + sparse cowbell. Sparse, laid back.
- **Break** — call (bars 5,7,9,11) / response (6,8,10,12) between marimba and
  tom fills; kick only on call bars. Breakdown character.
- **Drop** — full groove: four-on-floor kick + backbeat snare + 8th-note
  marimba arpeggio + 8th-note kalimba + cowbell timeline + 16th shaker.
- **Outro** — fade: sparse marimba, quarter kalimba, bass on 1 & 3, sparse
  bell + shaker, held tonic.

## Verification (real numbers)

```
zero-drift        : True  (5 note tracks x 46080 ticks, all equal)
grid audit (16th/8th) per pitched voice:
  Lead            : 116 notes, off16=0, off8=0
  Harmony         :  72 notes, off16=0, off8=0
  Kalimba         : 160 notes, off16=0, off8=0
  Bass            :  64 notes, off16=0, off8=0
  TOTAL off-grid  : 0
harmony audit per pitched voice:
  out-of-scale    : 0   (all notes in G major)
  out-of-chord    : 0   (all notes chord tones of their bar)
voice-leading     : 0 parallel/hidden fifth/octave violations
phase-1 raw draft : 73 events, off-grid by design (pre-rules, single voice)
```

Audio: FluidR3_GM.sf2 → WAV 44.1 kHz (peak 1.000, 2 clipped samples
0.0001%, RMS −18.46 dB, silence 10.1%, 0 mid-track gaps, 52.06 s incl.
reverb tail) → Opus OGG 48k.

## Files

| Path | Size |
|---|---|
| `MIDI/238-neoriemannian-afro-drop.mid` | 6846 B (+ provenance.json) |
| `MIDI/238-neoriemannian-afro-drop-phase1.mid` | 703 B (+ provenance.json) |
| `Audio/238-neoriemannian-afro-drop.wav` | 9183532 B |
| `Audio/238-neoriemannian-afro-drop.ogg` | 396351 B |
| `Audio/238-neoriemannian-afro-drop-phase1.wav` | 8765996 B |
| `Audio/238-neoriemannian-afro-drop-phase1.ogg` | 363353 B |
| `Analysis/grid_visualization.txt` | — |
| `Analysis/summary.json` (chord path + steps) | — |
| `Analysis/audit.json` (mido readback) | — |
| `Analysis/render_stats.json` | — |

## Fixes applied during this run

1. **Style list hygiene** — excluded the misplaced project folder
   `016-genre-pattern-dataset` (and the accidental `Celtic ` with trailing
   space) from the genre pool before re-rolling.
2. **Grid sync (078-class bug)** — Break-section Lead/Bass used odd 16th
   slots (3, …) → `off8 = 8`. Snapped all pitched onsets to the 8th-note
   grid (multiples of 240 ticks) → `off8 = 0` on every voice.
3. **Dropped final bar** — BFS returned an empty route when target == current
   (the outro hold), silently dropping bar 24 for every pitched voice.
   Added an explicit `hold` step so all 24 bars are voiced (harmony note
   count 69 → 72).
4. **Voice-leading distance** — reported mod-12 so L steps read 1 semitone
   (not 11).

## Provenance

Engine-only composition: `structures`, `workflows.unitmatrix_composer`,
`workflows.provenance`, `visualization.grid`, `rules.voice_leading`, and the
instrument registry. No raw `mido` authoring (mido used read-only for the
independent audit). Both phase MIDIs pass `validate()` (zero-drift) and carry
`classification=ai-generated` provenance sidecars.
