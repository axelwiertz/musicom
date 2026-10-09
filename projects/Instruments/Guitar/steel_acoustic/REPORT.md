# Acoustic Guitar (steel) — Nightly Instrument Research Report

**Date**: 2026-10-09
**Job**: LAYER-ALIGNED Nightly Instrument Research

---

## Instrument

| Field | Value |
|---|---|
| Name | Acoustic Guitar (steel) |
| Family | Guitar |
| MIDI Program | 25 |
| GM | "Steel String Guitar" (GM1) |
| Pipeline label | "Acoustic Guitar (steel)" |
| FluidR3 preset | "Steel String Guitar" |
| Range | 40–86 (E2–C#6) |
| Sweet spot | 50–79 (D3–G5) |
| Solo range | 50–79 |
| Synthesis | Karplus-Strong (primary), ModalSynth (fallback) |

## Program mapping

- FluidR3_GM.sf2 preset 25 = "Steel String Guitar" (verified by phdr chunk)
- Pipeline GM_PROGRAMS[25] = "Acoustic Guitar (steel)" → stem `trackXX_Acoustic_Guitar_steel.wav`
- **No quirk**: pipeline label and stem name match the instrument identity; SF2 internal name "Steel String Guitar" vs pipeline "Acoustic Guitar (steel)" is cosmetic only
- **Fix applied**: existing acoustic_guitar (nylon) was using program 25 (which is actually the steel-string patch in FluidR3). Changed to program 24 (FluidR3 preset 24 = "Nylon String Guitar") so both guitars are now on the correct programs

## Articulations

| Technique | Velocity | Duration |
|---|---|---|
| strum_down | 80 | 0.25 |
| strum_up | 70 | 0.20 |
| fingerpick_thumb | 65 | 1.0 |
| fingerpick_index | 60 | 1.0 |
| flatpick | 85 | 0.20 |
| arpeggio | 65 | 0.15 |
| hammer_on | 75 | 0.50 |
| pull_off | 65 | 0.50 |
| muted_palm | 45 | 0.10 |
| harmonic | 95 | 0.45 |
| slide | 70 | 0.80 |
| accent | 92 | 0.20 |

## Zoning

| Zone | MIDI range | Pitches | Register character |
|---|---|---|---|
| Low | 40–50 | E2–D3 | Bass strings (E A D), open chord roots, bass runs, percussive thump |
| Mid | 51–66 | D#3–G4 | Full fundamental range for chords and fingerpicking |
| High | 67–86 | G#4–C#6 | Melodic lead, harmonics, bright cutting top |

## Synthesis engine

**Karplus-Strong** (primary):
- `loop_gain`: 0.9970 — steel strings ring 1–3 s (between clavi 0.9960 and harp 0.9985)
- `excitation`: "pick" — bright hard attack from plectrum
- `width`: 0.65 — moderate pulse width (stiffer than nylon = brighter)
- `lowpass_hz`: 6000 — steel has energy up to ~8 kHz, lowpass 6k for mix-friendly tone
- `noise_component`: 0.02 — pick scrape noise on wound strings

**ModalSynth** (fallback):
- Preset: "string" — harmonic 1D string modes
- Excitation: impulse — pick/finger transient
- Decay rates: 6, 9, 14, 20, 30

## Production defaults

| Parameter | Value |
|---|---|
| Reverb tail | 1.6 s (room/small hall) |
| EQ body | 300 Hz, -3.0 dB (cut boxiness/honk) |
| EQ presence | 4000 Hz, +2.5 dB (string brightness, pick attack) |
| EQ air | 9000 Hz, +1.5 dB (gentle sparkle) |
| Pan | -0.2 (center solo; ±0.2 stereo) |

## Registration proof

Full registry_table output showing the new row:

```
| Guitar | Acoustic Guitar (nylon) | 24 | 40–84 | lead, harmony, accent |
| Guitar | Acoustic Guitar (steel) | 25 | 40–86 | harmony, rhythm, strum, lead, melody, ornament, countermelody |
```

Verification lines:
```
  STEEL_ACOUSTIC.midi_program = 25 (should be 25)
  by_name('steel acoustic') = <Instrument Acoustic Guitar (steel) (family=Guitar, program=25, range=40-86)>
  by_program(25) = <Instrument Acoustic Guitar (steel) (family=Guitar, program=25, range=40-86)>
  STEEL_ACOUSTIC.in_sweet_spot(65) = True
```

## Engine test results

| Check | Result |
|---|---|
| Zero-drift (validate) | True (OK) |
| MIDI file | 111 bytes (> 40 ✓) |
| WAV file (solo) | 1,525,036 bytes (> 40 ✓) |
| Spectral buzz (4–8 kHz) | 8.8% (< 20% gate ✓) |
| Pipeline label | "Acoustic Guitar (steel)" matches STEEL_ACOUSTIC.stem_label ✓ |
| FluidR3 preset 25 | "Steel String Guitar" ✓ |

## Quirks found

- **None for program 25**. Pipeline GM_PROGRAMS[25] = "Acoustic Guitar (steel)" and FluidR3 preset 25 = "Steel String Guitar" — the internal SF2 name differs from pipeline label but this is cosmetic only, no routing impact. The stem file is `trackXX_Acoustic_Guitar_steel.wav`.
- **Existing instrument fix**: The pre-existing `acoustic_guitar.py` (nylon) was using program 25, which in FluidR3_GM.sf2 is actually the Steel String Guitar patch. Changed to program 24 (FluidR3 preset 24 = "Nylon String Guitar"). Both guitars now on correct programs.

## Files

| Path | Purpose |
|---|---|
| `instrument.md` | Full research reference |
| `steel_acoustic.py` | Importable constants |
| `verify_steel_acoustic.py` | Engine verification script |
| `steel_acoustic_test.mid` | MIDI output (1 bar, G major arpeggio) |
| `steel_acoustic_test.wav` | FluidSynth WAV render (solo) |
| `_check_sf2.py` | FluidR3 preset probe |
| `_check_registry.py` | Registry loading probe |