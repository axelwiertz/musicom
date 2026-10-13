# 240 — Ragtime Glide

**Nightly composition job — 2026-10-13**
**Style:** Ragtime | **Method:** 029 Continuous Polyphonic Portamento Glide (CPPG) | **Layer:** concrete

## Selection

| Field | Value |
|---|---|
| seed | 20261013 |
| layer roll | 0.6103 → **concrete** (~6/7 concrete cadence) |
| method | **029 Continuous Polyphonic Portamento Glide** (Rules-Based, CPPG) |
| style | Ragtime |
| form | **rondo** (A B A C A — 5 × 4 bars = 20 bars) |
| key | F major (tonic F3 = 53), 4/4, 480 TPB, bar = 1920 ticks |
| bpm | 100 |
| 16th grid | 120 ticks |

## Method interpretation (concrete → engine)

Method 029 ("Smoothly interpolates pitch and voicings of polyphonic chords
between successive sections instead of jump-cutting, creating a
theremin-style continuous choral warp"). MIDI is discrete (no continuous
pitch-bend in the engine path), so "portamento" is expressed three ways:

1. **Min-motion voice-leading** — a 4-voice string-ensemble choir (diatonic
   7th chords) re-voices every bar with the *smallest* total motion; voices
   frequently move by a semitone/tone. Census: **76 voice-moves, max = 2,
   mean = 0.87 semitones** — i.e. the "slide" is genuinely stepwise.
2. **Continuous re-voicing** — each bar's chord is re-articulated as four
   quarter-note inversions, so the top line "warps" through the chord
   instead of sitting as a static block.
3. **Glissando transitions** — at every rondo section boundary (bars 3, 7,
   11, 15, 19) the lead piano runs a fast ascending (final bar: descending)
   two-octave chord-tone arpeggio that "glides" into the next section.

Every note is a chord tone of its own bar **and** in the F-major scale.

## Chord path (20 bars) — all diatonic 7th chords in F major

| Section | Bars | Degrees |
|---|---|---|
| A1 | 1–4 | Fmaj7 (I)  Dm7 (vi)  Gm7 (ii)  C7 (V7) |
| B | 5–8 | Bbmaj7 (IV)  Fmaj7 (I)  Gm7 (ii)  C7 (V7) |
| A2 | 9–12 | Fmaj7 (I)  Dm7 (vi)  Gm7 (ii)  C7 (V7) |
| C | 13–16 | Dm7 (vi)  Bbmaj7 (IV)  Gm7 (ii)  C7 (V7) |
| A3 | 17–20 | Fmaj7 (I)  Dm7 (vi)  Gm7 (ii)  Fmaj7 (I, tonic close) |

Chord-tone pitch classes: Fmaj7 = {5,9,0,4}, Dm7 = {2,5,9,0},
Gm7 = {7,10,2,5}, C7 = {0,4,7,10}, Bbmaj7 = {10,2,5,9}. All ⊂ F major
{5,7,9,10,0,2,4}.

## Voices & instruments (from the instrument registry)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Acoustic Grand Piano | 1 | 0 | syncopated ragtime melody + glissando transitions |
| Glide | String Ensemble 1 | 48 | 1 | CPPG core — min-motion 4-voice glide choir |
| Stride | Acoustic Grand Piano | 1 | 2 | left-hand stride (bass 1&3, offbeat chord 2&4) |
| Drums | (GM percussion) | — | 9 | light brushed kit (hi-hat / kick / snare) |

## Arrangement

- **A1/A2** — main theme: syncopated piano lead (offbeat 8ths), stride
  "oom-pah" left hand, glide choir quarter-note inversions, quarter-note
  hi-hat. End of each A = ascending glissando into the next section.
- **B** — subdominant lift (starts on Bbmaj7): fuller hi-hat 8ths + soft
  kick on 1&3, lead syncopates a different contour.
- **C (trio)** — relative-minor region (starts on Dm7): brushed snare
  backbeat on 2&4 joins the kick/hat, the "dance" peak of the rondo.
- **A3 (coda)** — returns to the theme and closes on a held Fmaj7 with a
  descending glissando.

## Verification (real numbers)

```
zero-drift        : True  (4 note tracks x 38400 ticks, all equal)
grid audit (16th=120 / 8th=240) per pitched voice:
  Lead            : 127 notes, off16=0, off8=0
  Glide           : 320 notes, off16=0, off8=0
  Stride          : 160 notes, off16=0, off8=0
  TOTAL off-grid  : 0
harmony audit per pitched voice:
  out-of-scale    : 0   (all notes in F major)
  out-of-chord    : 0   (all notes chord tones of their bar)
voice-leading     : 3 parallel/hidden-fifth/octave flags (inherent to
                    parallel 7th-chord min-motion voice-leading — reported,
                    not gating)
portamento census : 76 voice-moves, max=2, mean=0.87 semitones
phase-1 raw draft : 160 events, off-grid by design (single theremin-style
                    glide, no harmony)
```

Audio (FluidR3_GM.sf2 → WAV 44.1 kHz):

| Render | Duration | Peak | RMS | Silence | <-40 dB windows |
|---|---|---|---|---|---|
| phase-2 mix | 52.19 s | 0.473 | −20.78 dB | 7.3% | 3 (sparse intro / transitions) |
| phase-1 raw | 50.70 s | 0.165 | −32.35 dB | 14.7% | 5 (single-voice draft) |

Silence well under the 30% suspicion threshold; no mid-track dropout.

## Files

| Path | Size |
|---|---|
| `MIDI/240-ragtime-glide.mid` | 5747 B (+ provenance.json) |
| `MIDI/240-ragtime-glide-phase1.mid` | 1490 B (+ provenance.json) |
| `Audio/240-ragtime-glide.wav` | 9205804 B |
| `Audio/240-ragtime-glide.ogg` | 346501 B |
| `Audio/240-ragtime-glide-phase1.wav` | 8944172 B |
| `Audio/240-ragtime-glide-phase1.ogg` | 452648 B |
| `Analysis/grid_visualization.txt` | — |
| `Analysis/summary.json` (chord path + voicings + steps) | — |
| `Analysis/audit.json` (mido readback) | — |
| `Analysis/render_stats.json` | — |

## Fixes applied during this run

1. **Duplicate rondo section names (engine collision)** — the composer's
   `fill_voice_section` looks up sections *by name*, so three sections named
   "A" collided and only the first "A" column got filled; A2/A3 defaulted to
   1 bar each (section durations `[7680,7680,1920,7680,1920]`, tracks 12 bars
   instead of 20). Fixed by using unique names **A1/B/A2/C/A3** with a
   `SECTION_ROLE` map → durations all 7680, tracks 38400 ticks.
2. **Grid sync (078-class bug)** — the original lead templates and glissando
   transitions used odd 16th slots (off8 = 42). Snapped every pitched onset to
   the 8th-note grid (multiples of 240 ticks) → **off8 = 0 on every voice**.

## Provenance

Engine-only composition: `structures`, `workflows.unitmatrix_composer`,
`workflows.provenance`, `visualization.grid`, `rules.voice_leading`, and the
instrument registry. No raw `mido` authoring (mido used read-only for the
independent audit). Both phase MIDIs pass `validate()` (zero-drift) and carry
`classification=ai-generated` provenance sidecars.
