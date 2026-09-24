# Accordion — Nightly Instrument Research Report (2026-09-24)

## Instrument

| Field | Value |
|---|---|
| **Name** | Accordion |
| **Family** | Keys |
| **GM Program** | 21 |
| **GM Name** | Accordion |
| **Stem Label** | `Accordion` (GM_PROGRAMS[21] = "Accordion" — **no quirk**) |
| **SF2 Preset** | "Accordian" (FluidR3 archaic spelling — cosmetic only, no routing impact) |
| **MidiInstrument enum** | Not exposed (only 10 instruments in enum); use raw `program=21` |

## Range

| Parameter | MIDI | Pitches |
|---|---|---|
| Range min | 36 | C2 (lowest 8' bass reed) |
| Range max | 96 | C7 (extended treble) |
| Solo range | 53–89 | F3–F6 (full right-hand keyboard) |
| Sweet spot | 60–84 | C4–C6 (richest treble register) |

### Register zones

| Zone | MIDI | Pitches | Description |
|---|---|---|---|
| Bass (left hand) | 36–52 | C2–E3 | Stradella fundamental + counter bass rows |
| Low treble | 53–59 | F3–B3 | Bottom of right-hand keyboard — dark, mellow |
| Mid treble | 60–76 | C4–E5 | Primary melodic register — richest reed tone |
| High treble | 77–89 | F5–F6 | Bright, cutting — piccolo/violin register |
| Extended | 90–96 | G6–C7 | Extended top keys — thin, piercing |

## Role

`harmony, melody, bass, rhythm, ornament`

The accordion is the only fully polyphonic instrument in the Keys family that plays melody, harmony, AND bass simultaneously (a one-person band). Right hand plays melody + chords, left hand provides bass + chord accompaniment via the Stradella system.

## Synthesis Engine

**Primary: PhaseModSynth** (`sound/synthesis/phase_mod.py`)

A free-reed aerophone = self-sustained symmetric oscillator. Saw carrier (even+odd harmonics) with phase modulation at moderate depth (3.2) reproduces the reedy buzz. The multi-rank chorus (musette effect) requires layering 2-3 PhaseModSynth voices at ±2-5 cents.

| Parameter | Value | Notes |
|---|---|---|
| carrier_shape | saw | Free reed = symmetric tongue: even+odd harmonics |
| mod_freq_ratio | 1.0 | Fundamental locked |
| mod_depth | 3.2 | Between oboe (2.5) and bagpipe (4.5) |
| attack | 0.015 s | Reed speaks instantly on airflow |
| release | 0.05 s | Reed stops on bellows reversal |

**Alternative: Additive** — harmonic stack with strong even partials + LFO amplitude wobble (5-7 Hz) for musette.

**Fallback: ModalSynth** `'string'` preset — generic sustained tone, loses reed buzz.

## Production Defaults

| Parameter | Value | Purpose |
|---|---|---|
| Reverb tail | 1.4 s | Room/hall — keep reed detail clear, avoid washout |
| EQ body | 300 Hz, -2.5 dB | Cut bellows boxiness |
| EQ presence | 2500 Hz, +2.5 dB | Reed clarity + cut |
| EQ air | 8000 Hz, +1.0 dB | Subtle key-click sparkle |
| Pan | 0.0 | Center solo; ±0.15-0.25 spread for stereo LH/RH |

## Articulations

| Technique | Velocity | Duration factor | Description |
|---|---|---|---|
| Sustain | 74 | 1.0 | Steady bellows, held note — default |
| Staccato | 78 | 0.2 | Short bellows pulse |
| Bellows shake | 82 | 0.5 | Rapid bellows vibrato (AM) |
| Marcato | 86 | 0.9 | Hard bellows accent |
| Legato | 65 | 1.0 | Smooth connected notes |
| Sforzando | 92 | 0.8 | Sudden forceful bellows push |

## Registration Proof

```
| Keys | Accordion | 21 | 36–96 | harmony, melody, bass, rhythm, ornament |
```

```
  ACCORDION.midi_program = 21 (should be 21)
  by_name('accordion') = <Instrument Accordion (family=Keys, program=21, range=36-96)>
  by_program(21) = <Instrument Accordion (family=Keys, program=21, range=36-96)>
  ACCORDION.in_sweet_spot(69) = True
```

## Verification Results

| Check | Result | Detail |
|---|---|---|
| Zero-drift | ✅ True (OK) | UnitMatrixComposer validate() |
| MIDI size | ✅ 111 bytes | > 40 byte gate |
| WAV size (solo) | ✅ 777,004 bytes | > 40 byte gate |
| Spectral buzz (4-8 kHz) | ✅ 2.8% | Below 20% gate — no comb-filtering |
| Stem label | ✅ `track00_Accordion.wav` | Matches GM_PROGRAMS[21] = "Accordion" |
| SF2 preset | ✅ "Accordian" | Cosmetic quirk — archaic spelling, no routing impact |
| PhaseModSynth smoke | ✅ peak=0.780, late_rms/peak=0.264 | Free reed sustains correctly |

## Quirks Found

1. **SF2 preset spelling**: FluidR3_GM.sf2 preset 21 is labeled "Accordian" (archaic spelling) instead of "Accordion". This is cosmetic only — the pipeline uses GM_PROGRAMS[21] = "Accordion" for the stem label, which matches perfectly. No routing impact.
2. **Multi-rank simulation**: A realistic accordion sound requires layering 2-3 PhaseModSynth voices at slight pitch offsets (±2-5 cents) to simulate the musette/chorus effect of multiple reed ranks. A single-voice PM patch sounds thin.
3. **Bellows expression**: MIDI velocity alone cannot capture the accordion's primary expressive mechanism — bellows pressure changes during a note. Composition jobs should use CC7 (volume) or CC11 (expression) ramps for realistic phrasing.
4. **Channel**: Must use a melodic channel (0-9) with program 21. Channel 9 would trigger the drum-kit map.

## Report File

`/opt/data/projects/Instruments/Keys/accordion/REPORT.md`
