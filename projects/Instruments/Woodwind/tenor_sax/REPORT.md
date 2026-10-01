# Tenor Saxophone — Instrument Report (2026-10-01)

## Instrument

- **Name**: Tenor Saxophone (B♭ tenor sax)
- **Family**: Woodwind
- **GM Program**: 66 (GM #67 "Tenor Sax")
- **Pipeline label**: GM_PROGRAMS[66] = "Tenor Sax"
- **Stem label**: `trackXX_Tenor_Sax.wav` ✓ (labels match exactly, **no quirk**)
- **FluidR3 preset**: 66 = "Tenor Sax" (labels match exactly)

## Range

| Parameter | Value |
|---|---|
| `range_min` | 44 (A♭2 concert; written B♭2) |
| `range_max` | 88 (E6 concert; written F♯6 with altissimo) |
| `solo_range` | (48, 82) — D3–A♭5 |
| `sweet_spot` | (53, 78) — F3–F5 warm singing register |

### Register zones

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Low | 44–53 | A♭2–F3 | dark, breathy, husky bottom |
| Mid | 54–68 | F♯3–C5 | warm vocal core — the money register |
| High | 69–88 | C♯5–E6 | bright cutting altissimo |

## Articulations (velocity, duration_factor)

| Technique | Velocity | Duration | Description |
|---|---|---|---|
| legato | 80 | 1.0 | smooth vocal tenor — the default |
| tenuto | 72 | 0.9 | slight separation, expressive |
| staccato | 65 | 0.25 | short crisp articulation |
| accent | 92 | 0.9 | sharp reed attack, punchy |
| growl | 78 | 1.0 | reed overblow, dirty blues/rock |
| vibrato | 78 | 1.0 | wide deliberate vibrato — the hallmark |
| subtoned | 55 | 1.2 | breathy whisper — classic jazz ballad |

## Synthesis Engine

- **Primary**: PhaseModSynth (`sound/synthesis/phase_mod.py`)
  - `carrier_shape`: "saw" (conical single reed — even+odd harmonics)
  - `mod_freq_ratio`: 1.0
  - `mod_depth`: 3.0 (deeper than alto 2.8 — huskier tenor core)
  - `attack`: 0.05 s (heavier reed than alto 0.04)
  - `release`: 0.10 s
- **Fallback**: Additive (explicit even+odd partials with stronger fundamental)

## Production Defaults

| Parameter | Value |
|---|---|
| `reverb_tail` | 1.6 s |
| `eq_body` | (400 Hz, -2.5 dB) cut boxiness |
| `eq_presence` | (2200 Hz, +2.5 dB) reed core (lower than alto 2500 — warmer/darker) |
| `eq_air` | (5500 Hz, +1.5 dB) breathy air (lower than alto 6000) |
| `pan` | 0.0 (center solo; +0.25..0.35 in section) |

## Registration Proof

```
| Woodwind | Tenor Saxophone | 66 | 44–88 | lead, countermelody, accent, harmony |

Verification:
  TENOR_SAX.midi_program = 66 (should be 66)
  by_name('tenor sax') = <Instrument Tenor Saxophone (family=Woodwind, program=66, range=44-88)>
  by_program(66) = <Instrument Tenor Saxophone (family=Woodwind, program=66, range=44-88)>
  TENOR_SAX.in_sweet_spot(64) = True
  TENOR_SAX.in_sweet_spot(30) = False
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift (validate) | True (OK) |
| MIDI file | tenor_sax_test.mid (117 bytes) > 40 ✓ |
| WAV file (solo FluidSynth) | tenor_sax_test.wav (758,316 bytes) > 40 ✓ |
| Spectral buzz (4–8 kHz) | 0.4% (< 20% gate ✓) |
| Stem label | `track00_Tenor_Sax.wav` ✓ (matches GM_PROGRAMS[66] = "Tenor Sax") |
| PhaseModSynth smoke test | C5=523.3 Hz peak=0.781, tail_rms/peak=0.175 (sustained ✓) |

## Quirks Found

- **None.** GM_PROGRAMS[66] = "Tenor Sax" → stem file `trackXX_Tenor_Sax.wav`. FluidR3 preset 66 = "Tenor Sax". Labels match exactly. STEM_LABEL = "Tenor_Sax" matches the pipeline's sanitized label. No quirk.
- **Note**: the stem label is "Tenor_Sax", NOT "Saxophone" and NOT "Alto_Sax" — match on the actual pipeline label "Tenor Sax" → "Tenor_Sax" in any stem-aware code.
- **API quirk**: MidiInstrument enum does not include program 66 (enum only exposes 10 instruments). Use raw `program=66` in composition jobs.

## Files Created

- `Woodwind/tenor_sax/instrument.md` — full research reference
- `Woodwind/tenor_sax/tenor_sax.py` — importable constants
- `Woodwind/tenor_sax/verify_tenor_sax.py` — verification script
- `Woodwind/tenor_sax/REPORT.md` — this report
- `instrument_registry.py` — updated with module entry + TENOR_SAX constant + role + verification
- `registry.md` — updated with table row + changelog + stem label quirk entry