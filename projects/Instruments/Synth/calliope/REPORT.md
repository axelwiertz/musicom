# REPORT — Calliope (GM82, "Lead 3 (calliope)") — 2026-11-03 nightly

## Instrument

**Calliope** — Synth family, fourth entry (after synth_pad GM88, synth_brass_1
GM62, synth_voice GM54). GM82 "Lead 3 (calliope)" is the GM Lead-family patch
modelled on the **steam calliope** ("steam piano"): a bank of steam-driven
organ pipes / brass whistles played from a keyboard — circus, carnival,
fairground, Mississippi riverboat. The patch reads as a mellow, slightly
breathy pipe lead: near-sine pipe fundamentals with a whisper of chiff, fast
valve-like attack, sustained while held.

Picked from the remaining candidate set (probed GM 82–87 synth leads +
GM55 Orchestra Hit in `_test/_probe_candidates.py`). Rationale: GM82 was the
mellow, clean member of the probe cluster (C6 spectral centroid ≈ 2230 Hz,
buzz 11.2% vs charang 26.6% / fifths 21.6% / bass+lead 20.3%), has a unique
identity with no overlap in the 83-instrument KB, and passes the 4–8 kHz
spectral gate comfortably.

## Program / GM

- **MIDI program**: 82 (raw GM number — `MidiInstrument` enum exposes only 10
  instruments and has NO calliope constant; registry is the full KB)
- **GM name**: "Lead 3 (calliope)" (GM1 spec)
- **Stem label**: `GM_PROGRAMS[82]` = "Lead 3 (calliope)" → sanitized
  `Lead_3_calliope` (spaces → `_`, parens stripped) — `STEM_LABEL =
  "Lead_3_calliope"` matches the pipeline's real sanitization exactly
- **FluidR3 preset 82** = "Calliope Lead" (verified from phdr chunk) — SF2
  internal name differs from the GM label, **cosmetic only, no routing
  impact** (stems are labelled from GM_PROGRAMS, not the SF2)

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full (writing band) | 60–96 | C4–C7 (real steam rack ~3 octaves) |
| Low | 60–71 | C4–B4 — warm round, chunky |
| Mid | 72–83 | C5–B5 — PRIMARY melody register (carnival tunes) |
| High | 84–96 | C6–C7 — bright top, whistle-y |
| Solo range | 67–89 | G4–A6 |
| Sweet spot | 72–84 | C5–C6 — the classic fairground tune register |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24–108 step 6):
preset 82 audible **15/15 notes, no gaps** (RMS 670–2125; C1 loudest 2125,
gentle treble rolloff to 670 at C8) — full-keyboard patch, no ceiling, SF2
never clips a composition. Range 60–96 is the idiomatic *writing* band, NOT
a physical limit.

## Role

lead, melody, ornament, accent, countermelody — carnival/circus cue lead,
retro/fantasy "toy town" top lines. NOT a bass voice, NOT a pad (pipes are
rhythmic; the pad role is synth_pad GM88). Light 2–3 note pipe chords OK
(calliopes are played two-handed); dense harmony smears. No unison doubling
with another melodic patch on the same pitches (2026-09-01 comb-filter rule).

## Synthesis engine

1. **PhaseModSynth (primary)** — `sound/synthesis/phase_mod.py`. The pipe
   recipe: **sine carrier** (NOT saw — pipes are near-sinusoidal; saw would
   read as synth brass), sine modulator, ratio 1.0, **mod_depth 1.8**
   (between flute 1.5 and shakuhachi 2.0 — brighter than a flute, mellower
   than reeds 2.2–4.5), attack 0.02 s (fast valve opening — steam pressure is
   already up), release 0.12 s (dry pipe cutoff), sustain_level 0.9.
2. **Additive (secondary)** — mellow harmonic pipe stack
   `[1.0, 0.55, 0.30, 0.18, 0.10, 0.05]` (strong fundamental, gentle rolloff,
   no reed brightness).
3. **AirPipe (tertiary, physical model)** — `sound/synthesis/air_pipe.py`: a
   pressure-driven flue pipe IS the calliope physics. `stopped=False` (open
   pipe), `pressure=0.6` (below the 0.75 overblow threshold — stays on the
   fundamental), `length_scale=1.0`.

## Constants (`Synth/calliope/calliope.py`)

- `MIDI_PROGRAM = 82`, `GM_NAME = "Lead 3 (calliope)"`,
  `STEM_LABEL = "Lead_3_calliope"`
- `RANGE_MIN = 60`, `RANGE_MAX = 96`, `SOLO_RANGE = (67, 89)`,
  `SWEET_SPOT = (72, 84)`
- `ZONES = {"low": (60, 71), "mid": (72, 83), "high": (84, 96)}`
- `ARTICULATIONS = {"pipe": (74, 1.0), "chiff": (70, 0.30), "marcato":
  (85, 0.85), "trill": (80, 0.25), "swell": (64, 1.2), "accent": (88, 0.9)}`
- `SYNTHESIS = "phase_mod"`, `FM_DEFAULTS = {carrier_shape: sine, mod_shape:
  sine, mod_freq_ratio: 1.0, mod_depth: 1.8, attack: 0.02, release: 0.12,
  sustain_level: 0.9}`, `SYNTHESIS_DEFAULTS = {instrument: "calliope",
  **FM_DEFAULTS}`
- `ADDITIVE_DEFAULTS = {harmonic_count: 6, harmonic_weights: [1.0, 0.55,
  0.30, 0.18, 0.10, 0.05], attack: 0.02, release: 0.12}`
- `AIRPIPE_DEFAULTS = {stopped: False, pressure: 0.6, length_scale: 1.0}`
- `REVERB_TAIL = 2.0`, `EQ_BODY = (400, -2.5)`, `EQ_PRESENCE = (3000, 2.0)`,
  `EQ_AIR = (9000, 1.5)`, `PAN = 0.0`
- `midi_to_freq(midi)` — standard A440 conversion

## Registration proof

Registered in `instrument_registry.py`:
1. `_INSTRUMENT_MODULES["Synth.calliope.calliope"] = "calliope"`
2. `CALIOPE = ALL_INSTRUMENTS["calliope"]` convenience constant
3. `registry_table()` role row: `"lead 3 (calliope)"` → `lead, melody,
   ornament, accent, countermelody`
4. `__main__` verification block extended

Verification run (`python instrument_registry.py`, exit 0) — the new row in
`registry_table()`:

```
| Synth | Lead 3 (calliope) | 82 | 60–96 | lead, melody, ornament, accent, countermelody |
```

Verification lines:

```
=== Calliope (Lead 3, GM82) ===
  CALIOPE.midi_program = 82 (should be 82)
  by_name('calliope') = <Instrument Lead 3 (calliope) (family=Synth, program=82, range=60-96)>
  by_name('LEAD 3 (CALLIOPE)') = <Instrument Lead 3 (calliope) (family=Synth, program=82, range=60-96)>
  by_program(82) = <Instrument Lead 3 (calliope) (family=Synth, program=82, range=60-96)>
  CALIOPE.in_sweet_spot(72) = True
  CALIOPE.in_sweet_spot(48) = False
  CALIOPE.range_min = 60 CALIOPE.range_max = 96
  CALIOPE.stem_label = 'Lead_3_calliope'
```

Full output: `_test/registry_out_calliope.txt`.

## Verification results (`_test/verify_calliope.py` — ALL CHECKS PASSED)

- **Registry import through the registry**: `from instrument_registry import
  by_name, by_program, CALIOPE` — `CALIOPE is by_name("calliope")` ✓,
  `by_program(82) is CALIOPE` ✓
- **Engine test**: UnitMatrixComposer, 1 bar × 1 section, 2 voices — Calliope
  (ch0) + drum-kit context (ch9). Calliope solo line: C5 E5 G5 C6(acc) G5 E5
  C5 G4, terminal note flush at BAR
- **Zero-drift**: `validate()` → **True (OK)** ✓
- **MIDI**: `_test/calliope_test.mid` — **188 bytes** (> 40 ✓)
- **WAV (SOLO render, voice 0 only — no unison doubling)**: FluidR3 via
  `discover_soundfont()` → `_test/calliope_test.wav` — **1,001,772 bytes**
  (> 40 ✓)
- **Spectral check (4–8 kHz buzz)**: **3.5%** — OK (gate ≤ 20%; single voice,
  no comb-filtering)
- **Stem label**: `GM_PROGRAMS[82] = 'Lead 3 (calliope)'` ✓, `STEM_LABEL ==
  "Lead_3_calliope"` ✓
- **SF2 preset**: preset 82 → `'Calliope Lead'` ✓
- **RenderPipeline stems on disk** (`_test/stems_calliope/`):
  - `track00_Lead_3_calliope.wav` — 1,001,772 B ✓
  - `track01_Drums.wav` — 706,092 B ✓
- **Engine smoke tests**:
  - PhaseModSynth C5 (depth 1.8): peak **0.796**, head_rms 0.3789,
    mid_rms 0.3795, tail_rms 0.2940 (sustain holds, release decays — no
    collapse) ✓
  - AirPipe C5 (pressure 0.6, open pipe): peak **1.704** ✓
  - Additive C5 (normalized pipe stack + ADSR): peak **2753** ✓

## Quirks found

1. **Stem label — sanitization, not a mismatch**: `GM_PROGRAMS[82] = "Lead 3
   (calliope)"` sanitizes to `Lead_3_calliope` (spaces → `_`, parens
   stripped). `STEM_LABEL` matches the pipeline's real output — **no routing
   quirk** (contrast the Bag_pipe/Shanai label quirks at 109/111).
2. **FluidR3 preset name differs**: preset 82 = "Calliope Lead" vs GM label
   "Lead 3 (calliope)" — cosmetic only; stems are labelled from GM_PROGRAMS.
3. **Enum gap**: `MidiInstrument` has no calliope constant (10-instrument
   legacy enum) — raw GM 82 used; registry is the full KB.
4. **Channel quirk**: melodic channel 0–9 required; ch9 would trigger the
   drum-kit map + `Acoustic_Grand_Piano` program-0 fallback label (timpani
   lesson).
5. **Full-keyboard patch**: plays 24–108 with no ceiling — SF2 never clips;
   writing band 60–96 keeps the calliope character (below C4 the patch reads
   as organ bass, not calliope).
6. **No built-in vibrato** (steam pressure is constant) — pitch-bend is the
   only idiomatic wobble.
7. **Fast attack = dry separation**: short chiff notes stay dry and
   separated (no smear — contrast the synth-voice bloom); calliope trills
   are the fairground ornament.

## Files

- `Synth/calliope/instrument.md` — full research reference
- `Synth/calliope/calliope.py` — importable constants
- `Synth/calliope/REPORT.md` — this report
- `_test/verify_calliope.py` + `_test/verify_calliope_out.txt` — verification
- `_test/registry_out_calliope.txt` — registry verification output
- `_test/calliope_test.mid`, `_test/calliope_test.wav`,
  `_test/stems_calliope/` — artifacts
- `instrument_registry.py` + `registry.md` — registered + documented
