# REPORT — Harp (Orchestral Harp, GM46) — nightly instrument job 2026-09-14

## Instrument

- **Name**: Harp (GM name "Orchestral Harp") — 47-string double-action pedal
  harp, the only plucked member of the classical strings block (GM 40–47).
- **Family**: Strings (new folder `Strings/harp/`)
- **Program**: 46 (GM1, 0-based; pipeline `GM_PROGRAMS[46]` = "Orchestral
  Harp"). NOT in the `MidiInstrument` enum — raw `program=46`.
- **Files**: `Strings/harp/instrument.md`, `Strings/harp/harp.py`,
  `_test/verify_harp.py`, `_test/sweep_harp.py`
- **Date**: 2026-09-14

## Range / zones

| Field | Value |
|---|---|
| RANGE_MIN / RANGE_MAX | 24 / 103 (C1–G7, full 47-string concert grand — widest in the KB after the piano) |
| SOLO_RANGE | (24, 103) — full span playable solo |
| SWEET_SPOT | (55, 88) — G3–E6, richest gut/nylon register |
| Zones | low 24–47 (wire bass, rings 6–10 s), mid 48–71 (gut, melody+arpeggio), high 72–103 (nylon treble, gliss sparkle) |
| midi_to_freq | A4=440 standard; C1=32.7 Hz, G7=3136.0 Hz |

## Role

harmony, arpeggio, glissando, melody, countermelody, accent —
arpeggio pads + gliss transitions are the idiomatic texture; NOT a bass
voice (wire strings muddy in a mix), NOT a rhythmic strum voice.

## Synthesis

- **Primary: Karplus-Strong** (`SYNTHESIS = "karplus"`) — plucked waveguide
  = the exact physical model. `KARPLUS_DEFAULTS = {loop_gain: 0.9985,
  width: 0.55, role: "lead"}` — loop_gain is the HIGHEST of the plucked
  set (sitar 0.9975, koto 0.9970, banjo 0.9960): harp strings are the
  longest and least-damped (no dampers exist; harpist damps by hand).
  Measured tail_rms/peak (1–2 s window): **0.0083** vs 0.0050 sitar-class
  (0.9975) and 0.0013 dull control (0.990) — out-rings every plucked KB
  instrument.
- **Fallback: ModalSynth 'string'** preset; custom `HARP_MODES` bank
  (near-harmonic 1 : 2 : 3 : 4 : 5 stack, LOW decay rates 0.22–1.20 —
  the `decay` arg is a rate, so like vibraphone/timpani these sit at the
  slow-decay end of the axis): measured late(1.0–1.5 s) rms/peak **0.497**
  vs marimba preset 0.0001 — second-longest modal ring after vibraphone
  (0.445).
- **Alt: PhaseModSynth** cheap harp — sine carrier, ratio 2.0, depth 1.3,
  attack 0.003, release 1.8.

## Articulations (velocity, duration_factor)

pluck (84, 1.0), nail_attack (96, 0.9), arpeggio (72, 0.9), glissando
(78, 1.2), bisbigliando (62, 1.0), harmonic (60, 0.6), damp/étouffée
(50, 0.12), près_de_la_table (58, 0.8), flat_fermata (66, 1.0).

## Production defaults

| Field | Value | Rationale |
|---|---|---|
| REVERB_TAIL | 2.4 s | the concert-hall instrument; longest of the plucked set |
| EQ_BODY | (250, −2.5) dB | tame soundboard boom (largest body in KB) |
| EQ_PRESENCE | (3500, +1.5) dB | fingertip pluck attack |
| EQ_AIR | (10000, +2.0) dB | treble shimmer + gliss sparkle |
| PAN | 0.0 solo / ~+0.3 orchestra | classical seating (audience view) |

## Registration proof

`instrument_registry.py`:
- `_INSTRUMENT_MODULES["Strings.harp.harp"] = "harp"`
- `HARP = ALL_INSTRUMENTS["harp"]`
- `registry_table()` role row: "orchestral harp" → harmony, arpeggio,
  glissando, melody, countermelody, accent
- `__main__` verification extended: `HARP.midi_program`, `by_name('harp')`,
  `by_name('orchestral harp')`, `by_program(46)`, `HARP.in_sweet_spot(69)`

Registry run output (2026-09-14, `/opt/data/micromamba/envs/musicom/bin/python
instrument_registry.py`):

```
| Strings | Orchestral Harp | 46 | 24–103 | harmony, arpeggio, glissando, melody, countermelody, accent |
...
  HARP.midi_program = 46 (should be 46)
  by_name('harp') = <Instrument Orchestral Harp (family=Strings, program=46, range=24-103)>
  by_name('orchestral harp') = <Instrument Orchestral Harp (family=Strings, program=46, range=24-103)>
  by_program(46) = <Instrument Orchestral Harp (family=Strings, program=46, range=24-103)>
  HARP.in_sweet_spot(69) = True
```

ALL_INSTRUMENTS count after registration: **39** (was 38).

## Verification results (`_test/verify_harp.py`, all passed)

| Check | Result |
|---|---|
| Registry import | `by_name('harp')` → Orchestral Harp, program 46 ✓; row in `registry_table()` ✓ |
| Zero-drift | `True (OK)` — harp arpeggio unit ends flush at BAR (terminal landmark) |
| MIDI export | `_test/harp_test.mid` — **144 bytes** (>40 ✓) |
| WAV solo render | `_test/harp_test.wav` — **2,335,788 bytes** (>40 ✓), rendered via `discover_soundfont()` → FluidR3_GM.sf2, FluidSynth `-g 1.2` |
| Solo voice rule | Harp arpeggio SOLO (ch0) + one low bass note C2 an octave+ below (ch1, GM33) — NO second melodic patch on the same pitches |
| Spectral gate | 4–8 kHz buzz energy **2.4%** — OK, no comb-filtering |
| Stem label | `GM_PROGRAMS[46]` = "Orchestral Harp" → stem `track00_Orchestral_Harp.wav` (2,335,788 bytes) ✓ matches STEM_LABEL; bass stem `track01_Electric_Bass_finger.wav` (741,676 bytes) |
| SF2 preset (phdr) | preset 46 = **"Harp"** (FluidR3 spells it one-word; pipeline label is "Orchestral Harp" — cosmetic only, no routing impact) |
| KS ring | loop_gain 0.9985: tail 0.0083 vs sitar-class 0.0050 (×1.7) and dull 0.990 0.0013 (×6.4) |
| KS partials | f0=136.7, 2×=147.1 (107.6% of f0), 3×=116.8 (85.5%) — octave-rich near-harmonic gut-string stack, decaying upward |
| Modal ring | HARP_MODES late(1.0–1.5 s) rms/peak 0.497 vs marimba 0.0001 (~5000× longer ring) |
| Pitch sweep | FluidR3 preset 46, notes 12–108, **12/12 audible, no gaps** (`_test/sweep_harp.py`) |

## Quirks found

1. **SF2 label**: FluidR3 preset 46 is "Harp" (one word), pipeline
   GM_PROGRAMS[46] is "Orchestral Harp" — cosmetic spelling difference
   only, stem files use the pipeline label `Orchestral_Harp`.
2. **Treble rolloff** (measured): the patch rolls off smoothly toward the
   treble with no cliff — bass strings ~0.024 rms, top octave (≥ C6=84)
   ~0.0024–0.0037 (≈10× quieter, like real nylon trebles). Composition
   jobs should use higher velocities (or doubled octaves) for melody
   above C6.
3. **Diatonic instrument**: 7 double-action pedals retune one pitch class
   across all 47 strings (flat/natural/sharp) — single strings cannot
   play chromatics; accidentals need pedal moves or enharmonic
   re-spelling (the source of bisbigliando). No dampers — everything
   rings until hand-damped; glissando/arpeggio are the idiomatic texture.
4. **Not a bass voice**: wire bass strings (C1–B2) ring huge but muddy
   fast in a mix — cello/double bass own the low register.
5. Harmonics gliss, harmonics, près de la table and flat fermata are
   standard orchestral harp techniques that map cleanly to
   velocity/duration pairs in ARTICULATIONS.

## Registry discipline checklist

- [x] `instrument_registry.py` `_INSTRUMENT_MODULES` entry added
- [x] `HARP` convenience constant added
- [x] `registry_table()` role mapping added
- [x] `__main__` verification lines added
- [x] Registry run prints full table INCLUDING the new row + verification
- [x] `registry.md`: changelog section (2026-09-14), Registry table row,
      stem-label quirks table row
- [x] `instrument.md` + `harp.py` + REPORT.md written
- [x] Engine test through UnitMatrixComposer, zero-drift ✓, MIDI+WAV>40B ✓
- [x] Solo render (no unison doubling) + spectral gate ✓
- [x] Soundfont resolved via `discover_soundfont()` (FluidR3_GM.sf2)
