# Rhodes (Electric Piano 1) — Instrument Report
**Date**: 2026-10-06 | **Registry Version**: `instrument_registry.py` (post-RHODES)

## Instrument Identity

| Field | Value |
|---|---|
| Instrument | **Rhodes (Electric Piano 1)** |
| Family | Keys |
| GM Program | 4 |
| GM Name (pipeline) | "Electric Piano 1" |
| GM Name (SF2 phdr) | "Rhodes EP" (FluidR3_GM.sf2 internal name — cosmetic only) |
| Stem label | `Electric_Piano_1` → `trackXX_Electric_Piano_1.wav` |
| MIDI range | 36–96 (E1–C7) |
| Sweet spot | 48–84 (C3–C6) |
| Solo range | 60–79 (C4–G5 — the classic Rhodes "bark" zone) |
| Role | harmony, melody, bass, accent, color |
| Synthesis | ModalSynth primary, Karplus-Strong secondary, PhaseModSynth tertiary |

## Synthesis Details

**ModalSynth** (primary): struck clamped-cantilever tine inharmonic modal bank.
Custom `RHODES_MODES` at compressed ratios **1.0 : 2.3 : 4.1 : 6.8** (the
spring-coil base pushes modes down from harmonic 1:2:3:4), decay rates 1.5–3.0.
Stock `'string'` preset is the fallback.

**Karplus-Strong** (secondary): struck waveguide = exact physical model of the
tine. `loop_gain` **0.9965** between clavi 0.9960 (rubber-muted) and sitar
0.9975 (long sympathetic ring). Steel tine rings 1-3 s with felt damper.
`lowpass_hz` 2000 for the magnetic pickup's limited bandwidth.

**PhaseModSynth** (tertiary): FM bell-like tone, ratio 2.3, depth 1.8, attack
0.004 s, release 1.5 s.

## Production Defaults

| Parameter | Value |
|---|---|
| REVERB_TAIL | 2.2 s (hall) |
| EQ_BODY | 350 Hz, -2.5 dB (tine-mount resonance cut) |
| EQ_PRESENCE | 2500 Hz, +2.5 dB (bell articulation) |
| EQ_AIR | 8000 Hz, +1.5 dB (subtle sparkle) |
| PAN | 0.0 (center) |

## Registration Proof

```
Registry table includes row:
| Keys | Electric Piano 1 | 4 | 36–96 | harmony, melody, bass, accent, color |

by_name('rhodes')              → <Instrument Electric Piano 1 (family=Keys, program=4, range=36-96)>
by_name('electric piano 1')    → <Instrument Electric Piano 1 (family=Keys, program=4, range=36-96)>
by_program(4)                  → <Instrument Electric Piano 1 (family=Keys, program=4, range=36-96)>
RHODES.midi_program            = 4
RHODES.in_sweet_spot(69)       = True
RHODES.in_sweet_spot(30)       = False
RHODES.range_min               = 36
RHODES.range_max               = 96
RHODES.stem_label              = 'Electric_Piano_1'
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift (validate) | **True (OK)** |
| MIDI file size | **82 bytes** (> 40 ✓) |
| WAV file size (solo) | **731,180 bytes** (> 40 ✓) |
| Spectral buzz (4-8 kHz) | **1.4%** (< 20% gate ✓) |
| Stem label match | **GM_PROGRAMS[4] = "Electric Piano 1"** ✓ |
| Pipeline stem file | `track00_Electric_Piano_1.wav` (731,180 bytes) ✓ |
| FluidR3 preset 4 | "Rhodes EP" (cosmetic — SF2 internal name) |
| ModalSynth 'string' | peak=0.900, tail_rms/peak=0.063 ✓ |

## Quirks Found

1. **SF2 internal name**: FluidR3_GM.sf2 stores program 4 as "Rhodes EP" while
   GM_PROGRAMS[4] = "Electric Piano 1". This is cosmetic — the pipeline routes
   by program number, not by name. No routing impact.

2. **Pickup compression quirk**: The Rhodes' electromagnetic pickup compresses
   the dynamic range compared to an acoustic piano. A velocity range of 40–120
   on the Rhodes produces only ~3-4 dB of perceived dynamic change, vs ~15-20
   dB on a piano. Composition jobs should phrase with REGISTRATION (voicing
   density, chord spacing, two-hand spacing) as much as with velocity — use
   open/closed voicings and note count for dynamic contour.

3. **No MidiInstrument enum entry**: GM4 is not in `structures/instrument.py`
   `MidiInstrument` (which only exposes 10 instruments). Use raw `program=4`
   in `add_voice()` calls.

4. **Bass zone limitation**: Below C3 (MIDI 48) the Rhodes gets rumbly/dark;
   for true bass foundation below C2 (MIDI 36), use acoustic bass or piano
   instead.

## Files Created

| Path | Description |
|---|---|
| `Keys/rhodes/instrument.md` | Full research reference (175 lines) |
| `Keys/rhodes/rhodes.py` | Importable constants (131 lines) |
| `Keys/rhodes/verify_rhodes.py` | End-to-end verification script |
| `Keys/rhodes/rhodes_test.mid` | Test MIDI output (82 bytes) |
| `Keys/rhodes/rhodes_test.wav` | Test WAV output (731 KB) |
| `Keys/rhodes/stems/track00_Electric_Piano_1.wav` | Pipeline stem output |
| `Keys/rhodes/REPORT.md` | This report |

## Registry Changes

- `instrument_registry.py`: added `"Keys.rhodes.rhodes": "rhodes"` to
  `_INSTRUMENT_MODULES`, `RHODES = ALL_INSTRUMENTS["rhodes"]` convenience
  constant, role entry in `registry_table()`, and verification lines in
  `__main__`.
- `registry.md`: added registry table row, stem label quirks entry, and
  dated changelog entry (2026-10-06).