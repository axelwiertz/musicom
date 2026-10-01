# REPORT — 216-lsystem-fractal

**Project:** 216-lsystem-fractal
**Style:** Electronic
**Method:** 019 L-System Algorithmic Composition (Lindenmayer rewrite system) — `generators.interval_lsystem.IntervalLSystem`
**Layer:** `concrete`
**Date:** 2026-10-01 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20261001
**Key:** A natural minor = A B C D E F G = pitch classes {9, 11, 0, 2, 4, 5, 7}
**BPM:** 120 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240, section = 7680, total = 61440)

---

## 1. Selection

| Field | Value |
|---|---|
| Style | **Electronic** — random pick from the genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered/`Celtic `). Seed 20261001 first roll = Electronic. No repeat of the last 7 nights (203 Experimental, 204/215 Minimalism, 205 African, 206 Ragtime, 207 Funk, 208 HipHop, 209 Trap, 210 West-African, 211 Disco, 212 IndianClassical, 213 Experimental, 214 Blues), so no re-roll needed. |
| Method | **019 L-System Algorithmic Composition** — `concrete` layer, Rules-Based, Exponential fractal rewrite. Not used in the last 7 days. |
| Layer cadence | `concrete` (6-of-7 cadence). Last abstract composition job was 105 (2026-09-24, method 095 Contour Theory); abstract not yet due. |
| Recent-method exclusion | Excluded methods used in the last 7 days: {001, 010, 016, 018, 020, 025, 026, 031, 032, 040, 041, 048, 069, 075, 082, 095}. Random pick from the remaining concrete methods landed on **019**. |

## 2. Method essence (019 L-System)

A Lindenmayer system rewrites a string of interval symbols into a
self-similar (fractal) interval structure:

```
axiom   = "A"
rules   = { "A": "A+B-A-B+A",  "B": "A-B+A+B-A" }
symbols = { "+": +2 semitones, "-": +1 semitone }   # whole / half step
```

Each iteration expands every non-terminal, so the contour repeats at larger
scales — the classic L-system property. After 3 iterations the system yields
**124 stepwise interval deltas** (`[2,1,1,2,2,1,2,...]`), a balanced
whole/half-step fractal walk. The raw phase-1 lead *is* this walk: a single
square-lead voice stepping through the deltas with added chromatic jitter and
unquantized onset micro-timing. Phase 2 then maps the fractal contour onto
A-minor diatonic triads (chord-tone quantization) so the self-similar shape is
preserved while every note is in-key and in-chord.

| L-system parameter | Value |
|---|---|
| axiom / rules | `"A"` / `{A→A+B-A-B+A, B→A-B+A+B-A}` |
| symbol map | `+`=+2, `-`=+1 (whole/half steps) |
| iterations | 3 |
| resulting deltas | 124 stepwise intervals |
| register | lead 48–88, center A4 (69) |

## 3. Form, Key, Meter

| Field | Value |
|---|---|
| Form | 8 sections × 4 bars = **32 bars**: `Intro / VerseA / VerseB / Chorus / Drop / Bridge / Climax / Outro` |
| Key | **A natural minor** (pcs {9,11,0,2,4,5,7}) |
| Meter | 4/4, 120 BPM, straight 16th grid (16th = 120 ticks) |
| Progression | i–VI–III–VII movement (Am F C G) with Em/Dm color in Drop/Bridge |

Section map (each 4 bars):

| # | Name | Progression | Start degree | Midpoint chord | Variation technique |
|---|---|---|---|---|---|
| 0 | Intro | Am Am Am Am | i | Am | sparse drone, no drums |
| 1 | VerseA | Am F C G | i | C | baseline L-system deltas |
| 2 | VerseB | F Am G C | VI | G | **retrograde** deltas |
| 3 | Chorus | F C G Am | VI | G | full texture |
| 4 | Drop | Am Em F G | i | F | **augmentation** (durations ×2) |
| 5 | Bridge | F G Am Em | VI | Am | **inversion** (negate deltas) |
| 6 | Climax | Am F C G | i | C | **register shift +12**, full drums |
| 7 | Outro | Am Am Am Am | i | Am | **diminution** (durations ×0.5) |

## 4. Voices & Instruments (registry source of truth)

| Voice | Instrument | GM Program | Channel | Role |
|---|---|---|---|---|
| Lead | Lead 1 (square) | 80 | 0 | L-system fractal melody (raw GM — no synth-lead in registry) |
| Pad | Pad 2 (warm) | 90 | 1 | Sustained root+3rd+5th harmony (raw GM) |
| Bass | Synth Bass 1 | 38 | 2 | 8th-note root pulses, octave bounce (raw GM) |
| Arp | Clavi | 7 | 3 | 16th-note chord-tone arpeggio (registry `CLAVI`) |
| Sparkle | Celesta | 8 | 4 | Off-beat high chord-tone accents (registry `CELESTA`) |
| Drums | Drum Kit | 0 (ch9) | 9 | Four-on-floor kick, snare 2&4, 8th hats |

Registry instruments (Clavi 7, Celesta 8) resolved via `instrument_registry.py`.
The three synth voices (square lead, warm pad, synth bass) have no registry
entry — the 18-instrument KB covers acoustic/orchestral timbres only, so those
use standard GM program numbers directly (documented), per the skill's
"raw MIDI program numbers" allowance for non-enum instruments.

## 5. Two-Phase Architecture

### Phase 1 — Raw L-System Draft (`-phase1.mid`)
- Single voice (LeadRaw, square lead program 80).
- **Onsets** unquantized: 16th/8th slot + micro-jitter (±18 ticks) off the 120/240 grid.
- **Pitch** unquantized: raw L-system interval walk + chromatic jitter (±0.9 st) — NO scale/chord snap.
- No harmony, no chord-tone quantization, no texture. `validate()` PASSED.

### Phase 2 — Musicom Rules Post-Processing (`.mid`)
- Same L-system walk re-run with the same seed (no jitter), then:
  1. every onset snapped to the **16th grid** (120 ticks),
  2. every pitch snapped to its bar's **A-minor diatonic chord-tone set**,
  3. voice-leading cap (consecutive leaps ≤ 9 st).
- Full 6-voice electronic texture added. `validate()` PASSED.

## 6. Verification (real numbers)

### Grid audit — **0 OFF-GRID (16th = 120 ticks)** on every voice

| Track | Onsets | off_16th | off_8th | Verdict |
|---|---|---|---|---|
| Lead | 271 | **0** | 31 (16th syncopation) | 0 off-grid |
| Pad | 96 | **0** | 0 | 0 off-grid |
| Bass | 256 | **0** | 0 | 0 off-grid |
| Arp | 512 | **0** | 256 (16th arpeggio) | 0 off-grid |
| Sparkle | 64 | **0** | 32 (16th accents) | 0 off-grid |
| Drums (ch9) | 316 | **0** | 0 | 0 off-grid |

All **1515** onsets snap to the 16th grid (120 ticks). The non-zero `off_8th`
counts on Lead/Arp/Sparkle are intentional 16th-note subdivision — the
mandatory rule is "8th = 240 **or** 16th = 120", and this composition uses the
finer 16th grid, so 0 off-16th = fully on-grid. No onset falls off the 120
grid.

### Harmony audit (pitched voices vs A-minor scale + bar chord) — **0 OUT-OF-KEY**

| Track | Notes | out_of_scale | out_of_chord | Verdict |
|---|---|---|---|---|
| Lead | 271 | **0** | **0** | pass |
| Pad | 96 | **0** | **0** | pass |
| Bass | 256 | **0** | **0** | pass |
| Arp | 512 | **0** | **0** | pass |
| Sparkle | 64 | **0** | **0** | pass |

All **1199** pitched notes are in the A natural minor scale AND in their bar's
chord set. Chord-tone quantization guarantees both, since every diatonic chord
(A C E / B D F / C E G / D F A / E G B / F A C / G B D) is a subset of the
scale.

### Audio profile (FluidSynth + discover_soundfont → WAV → Opus OGG)

| Phase | Duration | Silence | Peak | Tonal ratio | Verdict |
|---|---|---|---|---|---|
| Phase 2 | 68.88 s | 6.59% | 0.7717 | 99.27% | healthy |
| Phase 1 | 66.13 s | 7.38% | 0.3474 | 97.73% | raw sparse lead (expected) |

- Silence < 30% (mid-track gaps only: the Intro's sparse drone and the release
  tail). No dead zones.
- FFT tonal content 50–1000 Hz ≥ 97% both phases → **not noise**.
- Phase 1 vs phase 2 contrast is texture (1 voice vs 6) and harmonicity
  (chromatic wander vs chord-locked), exactly as intended.

## 7. Zero-drift status

`UnitMatrixComposer.validate()` PASSED for **both** phases. All tracks equal
length (61440 ticks = 32 bars × 1920). Terminal landmark
`MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)` per section per voice,
chronological sort enforced by the engine. No raw-mido authoring (mido used
only for read/verify in render_audio.py), no sys.path hack beyond the
sanctioned instrument-registry path.

## 8. Files

| Path | Size | Description |
|---|---|---|
| MIDI/216-lsystem-fractal.mid | 12,629 B | Phase 2 rules composition (DAW-editable) |
| MIDI/216-lsystem-fractal-phase1.mid | 2,256 B | Phase 1 raw L-system draft |
| Audio/216-lsystem-fractal.ogg | 524,052 B | Phase 2 Opus render (Telegram-ready) |
| Audio/216-lsystem-fractal-phase1.ogg | 708,666 B | Phase 1 Opus render |
| Audio/*.wav | ~11–12 MB each | Raw PCM (pre-compression) |
| Analysis/grid_visualization.txt | — | High-contrast timeline |
| Analysis/summary.json | — | Full audit numbers |
| compose.py / render_audio.py | 19,182 / 7,273 B | Generators |
| provenance.json per artifact | — | write_provenance sidecars |

## 9. Fixes / notes

1. **Synth voice programs**: square lead (80), warm pad (90), synth bass (38)
   are standard GM synth timbres with no registry entry — the instrument KB is
   acoustic/orchestral. Used raw GM program numbers (documented) rather than
   forcing an ill-fitting acoustic program. Clavi (7) and Celesta (8) are
   registry-resolved.
2. **Grid choice**: this piece runs on the 16th grid (120), so Lead/Arp/Sparkle
   legitimately show non-zero `off_8th` (16th syncopation/arpeggio). The gate
   that matters — `off_16th` — is **0 for all 1515 onsets**.
3. **L-system register drift**: the raw walk can drift chromatically; Phase 2's
   chord-tone snap + ≤9-st voice-leading cap re-anchors it to the diatonic
   chord field without destroying the fractal contour.

## 10. What to listen for

- **The fractal lead** (square synth): a self-similar stepwise contour that
  repeats its own shape at bigger and bigger scales — the L-system signature.
- **The four-on-floor drive** (kick every beat, snare on 2&4) entering at
  VerseA and peaking at the Climax's open hi-hat.
- **The chord changes**: i → VI → III → VII (Am F C G) pull; the Drop darkens
  to i–v–VI–VII (Am Em F G) and the Bridge inverts the harmonic direction.
- **The 16th-note clavi arpeggio** (root–3rd–5th–octave) gluing the harmonic
  field together.
- **The celesta sparkle** on the off-beats, one per section, tracing the
  high register.
