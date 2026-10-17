# Electric Piano 2 (DX7 FM Piano) — Research Report

**Date**: 2026-10-17
**Instrument**: Electric Piano 2 (Yamaha DX7 FM Electric Piano)
**MIDI Program**: 5
**GM Name**: "Electric Piano 2"
**Family**: Keys (ninth entry)
**Pipeline Stem Label**: `Electric_Piano_2` → `trackXX_Electric_Piano_2.wav`
**FluidR3 Preset 5**: "Legend EP 2" (internal SF2 name differs cosmetically from GM label — no routing impact)

## Instrument Details

### Identity
GM5 = Electric Piano 2 is historically the **Yamaha DX7** digital synthesizer's iconic "E. Piano 1" preset — a 2-operator FM algorithm with fast percussive attack and bright bell-like tone. Unlike the Rhodes (GM4, electromechanical tine piano), the DX7 is a purely digital **FM synthesis** instrument.

### Range
| Zone | MIDI Range |
|---|---|
| Full range | 36–96 (E1–C7) |
| Sweet spot | 53–79 (F3–G5) — the iconic bright bell zone |
| Low | 36–47 (E1–B2) — dark, thuddy fundamental |
| Mid | 60–79 (C4–G5) — bright bell register, signature DX7 |
| High | 80–96 (G#5–C7) — thin tinkly top, metallic sheen |

### Role
Harmony, melody, bass, accent, color — fully polyphonic chord/strum/arpeggio instrument. The bright/cold FM counterpart to the warm/tine Rhodes.

### Articulations
| Technique | Velocity | Duration |
|---|---|---|
| Legato (pedal) | 45 | 1.0 |
| Touch | 65 | 1.0 |
| Accent | 88 | 0.95 |
| Hard accent | 105 | 0.95 |
| Staccato | 70 | 0.20 |
| Bell | 95 | 0.9 |
| Tremolo | 55 | 1.0 |
| Comping chop | 75 | 0.45 |

### Synthesis
**Primary**: PhaseModSynth (FM synthesis — the exact DX7 model)
  - carrier_shape: sine, mod_freq_ratio: 3.1, mod_depth: 2.8
  - attack: 0.003 s, release: 1.2 s
  - PhaseModSynth smoke test: A4 0.5 s peak=0.799 ✓

**Secondary**: Karplus-Strong (metallic struck waveguide)
  - loop_gain: 0.9960, lowpass_hz: 4000, noise_component: 0.01

**Fallback**: ModalSynth 'bell' preset

### Production Defaults
| Parameter | Value |
|---|---|
| REVERB_TAIL | 2.0 s (80s Lexicon hall shimmer) |
| EQ_BODY | 400 Hz, -2.0 dB (cut mud) |
| EQ_PRESENCE | 3200 Hz, +3.0 dB (bright bell articulation) |
| EQ_AIR | 9000 Hz, +2.0 dB (shimmer) |
| PAN | 0.0 (center) |

## Quirks Found

1. **FM bell quirk**: The DX7 signature has prominent 4-8 kHz energy at the onset BY DESIGN (not comb-filtering). The spectral-buzz gate (4-8 kHz) should NOT be used in the first ~100 ms as a rejection criterion — the natural FM bell has high-frequency content at onset by design.

2. **FluidR3 SF2 name**: FluidR3 preset 5 is internally named "Legend EP 2" while the GM_PROGRAMS list has "Electric Piano 2" at index 5. Cosmetic difference only — no routing impact; the preset index (5) is what matters.

3. **No damper pedal**: Unlike the Rhodes or acoustic piano, the DX7 has no physical damper response — notes ring for their programmed envelope duration regardless of pedal state. Composition jobs should use duration explicitly rather than relying on sustain pedal.

4. **PhaseModSynth smoke test**: The `PhaseModSynth` class uses `render_note(freq, duration, ...)` not `render_preset()`. Verified: FM EP2 note A4 peak=0.799.

## Registration Proof

Registry command output:
```
| Keys | Electric Piano 2 | 5 | 36–96 | harmony, melody, bass, accent, color |
```

Verification:
```
  ELECTRIC_PIANO_2.midi_program = 5 (should be 5)
  by_name('electric piano 2') = <Instrument Electric Piano 2 (family=Keys, program=5, range=36-96)>
  by_program(5) = <Instrument Electric Piano 2 (family=Keys, program=5, range=36-96)>
  ELECTRIC_PIANO_2.in_sweet_spot(69) = True
  ELECTRIC_PIANO_2.in_sweet_spot(30) = False
  ELECTRIC_PIANO_2.range_min = 36 ELECTRIC_PIANO_2.range_max = 96
  ELECTRIC_PIANO_2.stem_label = 'Electric_Piano_2'
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift | True (OK) |
| MIDI size | 111 bytes (> 40 ✓) |
| WAV size | 812332 bytes (> 40 ✓) |
| 4-8 kHz buzz | 1.0% (OK, < 20% gate) |
| Stem label | `Electric Piano 2` → `trackXX_Electric_Piano_2.wav` ✓ |
| SF2 preset 5 | "Legend EP 2" (cosmetic difference from "Electric Piano 2") |
| PhaseModSynth FM note | A4 0.5 s peak=0.799 ✓ |
| Registry load | 64 instruments loaded without error |

## Files Created

| File | Path |
|---|---|
| instrument.md | `/opt/data/projects/Instruments/Keys/electric_piano_2/instrument.md` |
| electric_piano_2.py | `/opt/data/projects/Instruments/Keys/electric_piano_2/electric_piano_2.py` |
| verify_ep2.py | `/opt/data/projects/Instruments/_test/verify_ep2.py` |
| REPORT.md | `/opt/data/projects/Instruments/Keys/electric_piano_2/REPORT.md` |

## Registry Modified

- `instrument_registry.py`: Added `"Keys.electric_piano_2.electric_piano_2": "electric_piano_2"` to `_INSTRUMENT_MODULES`, `ELECTRIC_PIANO_2` convenience constant, `registry_table()` role entry, verification block in `__main__`.
- `registry.md`: Added Electric Piano 2 changelog entry, registry table row, and stem label quirks entry.