# Electric Bass (finger) — Nightly Instrument Research Report

**Date**: 2026-10-08
**Cron job**: Nightly Instrument Research — LAYER-ALIGNED
**Instrument**: Electric Bass (finger) — GM33
**Family**: Bass (new family — first entry)

---

## Instrument Identity

- **GM Program**: 33 (0-indexed)
- **GM Name**: "Electric Bass (finger)"
- **Family**: Bass (new family, directory `Bass/electric_bass/`)
- **Pipeline stem label**: GM_PROGRAMS[33] = "Electric Bass (finger)"
  → `trackXX_Electric_Bass_finger.wav`
- **SF2 preset**: FluidR3 preset 33 = "Fingered Bass" (cosmetic name difference
  only — no routing impact; the pipeline labels by GM_PROGRAMS, not SF2
  internal names)
- **Channel**: Melodic channel (0-9) — NOT channel 9 (would trigger drum kit map)

## Constants

| Constant | Value |
|---|---|
| `MIDI_PROGRAM` | 33 |
| `GM_NAME` | "Electric Bass (finger)" |
| `STEM_LABEL` | "Electric_Bass_finger" |
| `RANGE_MIN` | 24 (C1) |
| `RANGE_MAX` | 84 (C5) |
| `SOLO_RANGE` | (31, 55) — G1–G3 |
| `SWEET_SPOT` | (40, 65) — E2–F4 |
| `SYNTHESIS` | "karplus" |
| `KARPLUS_DEFAULTS` | `{"loop_gain": 0.9970, "width": 0.6, "role": "bass"}` |
| `REVERB_TAIL` | 1.4 s |
| `EQ_BODY` | (250 Hz, −3.0 dB) |
| `EQ_PRESENCE` | (800 Hz, +2.5 dB) |
| `EQ_AIR` | (5000 Hz, +1.5 dB) |
| `PAN` | 0.0 (center) |
| `MODAL_PRESET` | "string" (weak fallback) |

## Register Zones

| Zone | MIDI | Pitches | Description |
|---|---|---|---|
| contrabass | 24–35 | C1–E2 | Sub-bass fundamental: chest thump, felt > heard |
| groove | 36–50 | E2–D3 | Primary rhythm register: root-fifth pocket, walking lines |
| mid | 51–65 | D#3–F4 | Melodic fills, fretboard centre, singing tone |
| high | 66–84 | F#4–C5 | Tenor register: bright, aggressive, slap/pop solos |

## Articulations

| Technique | Velocity | Duration Factor | Description |
|---|---|---|---|
| finger | 72 | 1.0 | Fingertip pluck — warm round tone, the default |
| pick | 86 | 0.85 | Plectrum — bright, aggressive, thinner sustain |
| slap | 94 | 0.35 | Thumb slap — percussive thwack |
| pop | 100 | 0.25 | Finger pop/snap — bright harmonic click |
| muted | 42 | 0.20 | Palm mute / ghost note — no pitch |
| legato | 68 | 0.85 | Hammer-on / pull-off |
| slide | 62 | 1.10 | Glissando / fret slide |
| accent | 90 | 0.80 | Emphatic pluck or pick dig |

## Synthesis Engine

**Primary**: Karplus-Strong (`sound/synthesis/karplus_strong.py`, SP-011).
The plucked waveguide is the exact physical model for a wound-steel bass
string with magnetic pickup. `loop_gain` 0.9970 provides moderate damping
(wound steel rings 1–3 s, shorter than harp 0.9985 but longer than
shamisen 0.9955). `width` 0.6 gives subtle stereo ambience in the
harmonic tail.

**Fallback**: ModalSynth 'string' preset — a clean harmonic stack with
moderate decay. Not idiomatic (no magnetic-pickup colour, no fret noise).

**Weak alternative**: PhaseModSynth saw carrier + sub-octave modulation
(ratio 0.5, depth 2.0) for a cheap PWM bass approximation.

## Production Defaults

- **Reverb**: Room 1.4 s — electric bass is typically dry (DI / close-mic
  amp); verb is a mix choice for exposed solos
- **EQ body**: 250 Hz, −3.0 dB — cut the P-Bass / Jazz-Bass box resonance
  (the "mud" zone)
- **EQ presence**: 800 Hz, +2.5 dB — finger attack and fret noise "growl"
- **EQ air**: 5 kHz, +1.5 dB — roundwound string shimmer / pick click
- **Pan**: 0.0 (center, 100% mono) — industry standard for bass

## Registration Proof

Registry verification output:

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
  ...
```

Verification commands:
```python
from instrument_registry import ELECTRIC_BASS, by_name, by_program
assert ELECTRIC_BASS.midi_program == 33
assert by_name("electric bass").midi_program == 33
assert by_program(33).midi_program == 33
```

Convenience constant `ELECTRIC_BASS` added to `instrument_registry.py`.
Module registered in `_INSTRUMENT_MODULES` as `"Bass.electric_bass.electric_bass": "electric_bass"`.

## Engine Verification Results

| Check | Result |
|---|---|
| Zero-drift | ✅ True (OK) |
| MIDI size | ✅ 111 bytes (> 40) |
| WAV size | ✅ 741,676 bytes (> 40) |
| Spectral buzz (4–8 kHz) | ✅ 0.4% (OK, well below 20% gate) |
| Stem label (pipeline) | ✅ GM_PROGRAMS[33] = "Electric Bass (finger)" |
| STEM_LABEL constant | ✅ "Electric_Bass_finger" |
| SF2 preset name | ✅ "Fingered Bass" (cosmetic only) |
| Stem render on disk | ✅ track00_Electric_Bass_finger.wav (741,676 bytes, > 40) |
| Karplus-Strong smoke | ✅ Peak 0.290, audio_len 22050 |

## Pipeline / Quirks

- **No stem label quirk**: GM_PROGRAMS[33] = "Electric Bass (finger)" and
  the STEM_LABEL constant "Electric_Bass_finger" matches the sanitized form.
- **SF2 name difference**: FluidR3 preset 33 is internally named "Fingered
  Bass" vs the pipeline's "Electric Bass (finger)" — this is cosmetic only
  (the pipeline labels by its own GM_PROGRAMS list, not SF2 preset names).
- **Channel quirk**: Must use a melodic channel (0–9) with program 33.
  Channel 9 triggers the GM drum-kit map and the `Acoustic_Grand_Piano`
  program-0 fallback label (same as timpani/taiko rule).
- **Line/rhythm quirk**: Electric bass is a monophonic groove instrument.
  Double-stops on adjacent strings are physically possible but not idiomatic
  in most styles. The bass is NOT a chord/comping voice.

## Files Created

| File | Path |
|---|---|
| Constants | `Bass/electric_bass/electric_bass.py` |
| Research doc | `Bass/electric_bass/instrument.md` |
| Verify script | `Bass/electric_bass/verify_electric_bass.py` |
| Report | `Bass/electric_bass/REPORT.md` |
| Test MIDI | `_test/electric_bass_test.mid` |
| Test WAV | `_test/electric_bass_test.wav` |
| Stems | `_test/stems_electric_bass/track00_Electric_Bass_finger.wav` |

## Registry Files Modified

| File | Change |
|---|---|
| `instrument_registry.py` | Added `"Bass.electric_bass.electric_bass": "electric_bass"` to `_INSTRUMENT_MODULES`, added `ELECTRIC_BASS = ALL_INSTRUMENTS["electric_bass"]`, added role entry for "electric bass (finger)" |
| `registry.md` | Added "Electric Bass added (2026-10-08)" entry documenting GM33, Karplus-Strong, spectral check, quirks |