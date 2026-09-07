# REPORT — Dulcimer added to musicom Instruments (2026-09-07)

Nightly instrument-research job (f5be3c580639), layer-aligned run.

## Instrument

| Field | Value |
|---|---|
| Name | **Dulcimer** |
| Family | Keys (3rd entry: piano, organ, dulcimer) |
| GM program | **15** (GM1 Dulcimer) — raw 0-indexed number, NOT in MidiInstrument enum |
| GM name | "Dulcimer" |
| Stem label | `Dulcimer` → `trackXX_Dulcimer.wav` (no quirk) |
| Identity | GM15 "Dulcimer" = **hammered** dulcimer (cimbalom/santur/yangqin struck-string zither), NOT the Appalachian lap dulcimer |
| Files | `Keys/dulcimer/instrument.md`, `Keys/dulcimer/dulcimer.py`, `_test/verify_dulcimer.py` |

**Why this pick**: remaining non-ethnic GM candidates were already covered by
the registry's 18 legacy instruments; the World-family run (sitar→koto→shamisen
→kalimba→banjo, GM104-108) completed 2026-09-06. Dulcimer = GM15, the first
Keys-family melodic addition beyond piano/organ and the instrument the genre
KB references for Klezmer cimbalom lines. FluidR3 has a proper `Dulcimer`
preset 15.

## Range / Role

- Full range 48–96 (C3–C7); sweet spot 62–86 (D4–D6); solo range 60–89 (C4–A6)
- Zones: low 48–59 (dark body ring) / mid 60–77 (melody courses) / high 78–96 (bright treble)
- Role: lead, melody, ornament, rhythm, harmony — chordal voice OK (folk styles
  play 2–4 note rolled chords); NOT bass, NOT kit

## Synthesis

- **SYNTHESIS = "modal"** (ModalSynth, `sound/synthesis/modal.py`) — impulse
  excitation, struck-string physics; `MODAL_PRESET = "string"` stock preset +
  custom struck-string modes documented in instrument.md:
  `(1.0,1.0,3.0),(2.0,0.55,5.0),(3.0,0.30,7.0),(4.0,0.18,9.0),(5.0,0.12,11.0),(6.0,0.08,13.0)`
- Karplus-Strong alt: `loop_gain=0.9975` (bright ring; verified below)
- Phase-mod cheap patch fallback (triangle carrier, 2.0× ratio)

## Constants (dulcimer.py, loaded through registry)

```
MIDI_PROGRAM=15  GM_NAME="Dulcimer"  STEM_LABEL="Dulcimer"
RANGE_MIN=48  RANGE_MAX=96  SOLO_RANGE=(60,89)  SWEET_SPOT=(62,86)
ZONES      = low(48-59) mid(60-77) high(78-96)
ARTICULATIONS = hammer(80,1.0) roll(70,0.10) double(74,0.25) damped(46,0.10) accent(96,0.85)
SYNTHESIS  = "modal"  MODAL_PRESET="string"
KARPLUS_DEFAULTS = {loop_gain 0.9975, width 0.45, role lead}
FM_DEFAULTS  = {triangle carrier, ratio 2.0, depth 2.0, attack 0.002, release 0.35}
REVERB_TAIL=1.2s  EQ_BODY=(350,-2.0)  EQ_PRESENCE=(3200,2.5)  EQ_AIR=(8000,1.5)  PAN=0.0
```

## Registration proof (instrument_registry.py run)

Registry count 23→**24**; new row in `registry_table()`:

```
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
```

Verification lines (real run):

```
DULCIMER.midi_program = 15 (should be 15)
by_name('dulcimer') = <Instrument Dulcimer (family=Keys, program=15, range=48-96)>
by_program(15) = <Instrument Dulcimer (family=Keys, program=15, range=48-96)>
DULCIMER.in_sweet_spot(69) = True
```

`instrument_registry.py` edits: `_INSTRUMENT_MODULES["Keys.dulcimer.dulcimer"]`,
`DULCIMER` convenience constant, role mapping + verification prints.

## Verification results (real run, `_test/verify_dulcimer.py`)

| Check | Result |
|---|---|
| UnitMatrixComposer 1 bar / 1 section, voice = Dulcimer solo (ch0) + low C2 bass context (ch1) | built |
| Zero-drift validate() | **True (OK)** |
| MIDI | `dulcimer_test.mid` **135 bytes** (> 40 ✓) |
| Solo WAV render (FluidR3 via `discover_soundfont()`, solo track 0 — NO unison doubling) | `dulcimer_test.wav` **953,644 bytes** |
| Spectral buzz check (4–8 kHz) | **4.1%** (OK, no comb-filtering) |
| RenderPipeline stem label | `track00_Dulcimer.wav` (953,644 B) — GM_PROGRAMS[15] = "Dulcimer" ✓ |
| SF2 preset (phdr) | FluidR3 preset 15 = `Dulcimer` ✓ (labels match exactly) |
| ModalSynth 'string' smoke | peak 0.900, tail 0.098 @0.2–0.6 s ✓ |
| Custom struck-string modes smoke | peak 0.900 ✓ |
| Karplus-Strong 0.9975 vs 0.990 dull | tail 0.023 vs 0.008 (2.9×) ✓ |
| ALL CHECKS PASSED | ✓ |

## Quirks found

- **Identity quirk (documented, not a label quirk)**: GM15 "Dulcimer" is the
  hammered dulcimer / cimbalom family. Composition jobs referencing Klezmer
  "Cimbalom" or santur/yangqin idioms should use this instrument.
- Stem label: NO quirk — GM_PROGRAMS[15], FluidR3 preset 15 and SF2 preset
  name are all exactly `Dulcimer`.
- Not in MidiInstrument enum (only 10 exposed) — used raw 15, registry is the
  full KB.
- Channel: melodic channel 0-9; ch9 would hit the program-0 fallback
  "Acoustic_Grand_Piano" stem label trap.

## Files written

- `/opt/data/projects/Instruments/Keys/dulcimer/instrument.md`
- `/opt/data/projects/Instruments/Keys/dulcimer/dulcimer.py`
- `/opt/data/projects/Instruments/_test/verify_dulcimer.py`
- `/opt/data/projects/Instruments/_test/dulcimer_test.mid`
- `/opt/data/projects/Instruments/_test/dulcimer_test.wav`
- `/opt/data/projects/Instruments/_test/stems_dulcimer/` (track00_Dulcimer.wav, track01_Electric_Bass_finger.wav)
- `/opt/data/projects/Instruments/registry.md` (changelog + Registry table + stem quirks table)
- `/opt/data/projects/Instruments/instrument_registry.py` (registered)
