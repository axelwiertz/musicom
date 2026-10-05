# Soprano Saxophone — Nightly Instrument Research Report

**Date**: 2026-10-05
**Job**: Nightly Instrument Research — LAYER-ALIGNED

---

## Instrument

| Field | Value |
|---|---|
| **Name** | Soprano Saxophone |
| **Family** | Woodwind |
| **MIDI Program** | 64 |
| **GM Name** | Soprano Sax |
| **General MIDI** | GM1 Soprano Sax (program 64) |
| **Transposition** | Bb (sounds M2 lower than written; constants are CONCERT/sounding pitch) |

## Range

| Register | MIDI | Pitches | Character |
|---|---|---|---|
| Full range | 54–89 | F#3–F6 (concert) | bright, piercing, most penetrating standard sax |
| Sweet spot | 67–79 | G4–G5 | singing lead — cuts through any ensemble |
| Low (closed) | 54–63 | F#3–D#4 | reedy, crisp, slightly thin — less projection |
| Mid (core) | 64–74 | E4–D5 | bright command — the soprano's money register |
| High (sopranino) | 75–89 | D#5–F6 | piercing scream — altissimo intensity |
| Solo range | 62–84 | D4–C6 | practical solo repertoire compass |

## Zones

```python
ZONES = {
    "low": (54, 63),
    "mid": (64, 74),
    "high": (75, 89),
}
```

## Articulations

```python
ARTICULATIONS = {
    "legato": (82, 1.0),     # smooth vocal, lightest reed
    "tenuto": (74, 0.9),     # slight separation, expressive
    "staccato": (68, 0.22),  # short crisp (fastest tongue in sax family)
    "accent": (94, 0.9),     # sharp reed attack, punchy
    "growl": (80, 1.0),      # reed growl/overblow — dirty altissimo
    "vibrato": (80, 1.0),    # wide deliberate — narrower than alto, faster in classical
}
```

## Synthesis Engine

**Primary**: PhaseModSynth (`sound/synthesis/phase_mod.py`)

```python
FM_DEFAULTS = {
    "carrier_shape": "saw",     # conical bore single reed
    "mod_freq_ratio": 1.0,      # reed-driven oscillator
    "mod_depth": 2.6,           # between clarinet 2.0 and alto 2.8
    "attack": 0.03,             # fastest reed in sax family (thinnest reed)
    "release": 0.08,            # smallest air column stops fastest
}
```

**Fallback**: Additive (6-partial harmonic stack, conical-bore single-reed weighting)

## Production Defaults

| Parameter | Value |
|---|---|
| Reverb tail | 1.4 s (dry — shortest in Woodwind, keep attack clarity) |
| EQ body cut | 800 Hz, -2.0 dB (soprano reed honk higher than alto's 400 Hz) |
| EQ presence boost | 2800 Hz, +2.5 dB (reed core, brighter than alto 2500) |
| EQ air | 6500 Hz, +1.5 dB (shimmer/breath) |
| Pan | 0.0 (center solo; +0.3..+0.45 in sax section) |

## Stem Label

- Pipeline GM_PROGRAMS[64] = `"Soprano Sax"`
- Sanitized filename: `trackXX_Soprano_Sax.wav`
- SF2 preset 64 (FluidR3): `"Soprano Sax"`
- **No quirk**: labels match exactly across pipeline and FluidSynth

## Constants (all values)

```python
MIDI_PROGRAM = 64
GM_NAME = "Soprano Saxophone"
STEM_LABEL = "Soprano_Sax"
RANGE_MIN = 54       # F#3 (lowest note on standard horn)
RANGE_MAX = 89       # F6 (altissimo)
SOLO_RANGE = (62, 84)
SWEET_SPOT = (67, 79)
REVERB_TAIL = 1.4
EQ_BODY = (800, -2.0)
EQ_PRESENCE = (2800, 2.5)
EQ_AIR = (6500, 1.5)
PAN = 0.0
```

## Registration Proof

Registry `_INSTRUMENT_MODULES` entry:
```python
"Woodwind.soprano_sax.soprano_sax": "soprano_sax",
```

Convenience constant: `SOPRANO_SAX = ALL_INSTRUMENTS["soprano_sax"]`

Verification output (from `instrument_registry.py __main__`):

```
| Woodwind | Soprano Saxophone | 64 | 54–89 | lead, countermelody, ornament, accent |

SOPRANO_SAX.midi_program = 64 (should be 64)
by_name('soprano sax') = <Instrument Soprano Saxophone (family=Woodwind, program=64, range=54-89)>
by_program(64) = <Instrument Soprano Saxophone (family=Woodwind, program=64, range=54-89)>
SOPRANO_SAX.in_sweet_spot(72) = True
SOPRANO_SAX.in_sweet_spot(50) = False
```

The new row appears in the registry table between the existing Piccolo and Tenor Saxophone entries (sorted by family then name within the Woodwind section).

## Verification Results

### Component Tests

| Test | Result |
|---|---|
| Constants import | ✓ soprano_sax.py loads with all fields |
| ZONES | ✓ 3 zones (low/mid/high) covering 54-89 |
| ARTICULATIONS | ✓ 6 techniques with velocity+duration |
| SYNTHESIS | ✓ phase_mod with FM_DEFAULTS dict |
| REVERB_TAIL | ✓ 1.4 seconds |
| EQ_BODY / EQ_PRESENCE / EQ_AIR | ✓ all present |
| PAN | ✓ 0.0 |

### Engine Test (UnitMatrixComposer)

| Check | Result | Detail |
|---|---|---|
| Zero-drift | ✓ | `validate()` → True (OK) |
| MIDI export | ✓ | 111 bytes (> 40 ✓) |
| WAV render (solo) | ✓ | 758,316 bytes via FluidSynth + FluidR3_GM.sf2 |
| Spectral buzz check | ✓ | 4-8 kHz energy = 0.3% (well below 20% gate) |
| No comb-filtering | ✓ | solo voice only — no unison doubling present |

### Stem Label Tests

| Check | Result | Detail |
|---|---|---|
| Pipeline GM_PROGRAMS[64] | ✓ | `"Soprano Sax"` |
| STEM_LABEL constant | ✓ | `"Soprano_Sax"` |
| Label match | ✓ | constant matches pipeline label |
| SF2 preset 64 name | ✓ | `"Soprano Sax"` (FluidR3_GM.sf2) |

## Quirks Found

1. **No quirk**: Stem label `Soprano_Sax` matches the pipeline's GM_PROGRAMS[64] = "Soprano Sax" exactly (sanitized). FluidR3 preset 64 is also "Soprano Sax". No cosmetic or routing discrepancies.

2. **Monophonic line voice**: Soprano sax is a single-reed monophonic lead instrument — composition jobs MUST write single-note lines, NOT dense chords. Unison/octave doubling in a sax section is fine but the soprano part itself is one line.

3. **Brightest sax**: The soprano is the highest and most penetrating member of the standard saxophone family — it naturally has the strongest 2-5 kHz energy of any woodwind in the KB. The 0.3% buzz in the 4-8 kHz band confirms this is a clean single voice, NOT comb-filtered distortion.

4. **SATB quartet complete**: With this addition, all four members of the standard saxophone quartet are now registered: Soprano (GM64) + Alto (GM65) + Tenor (GM66) + Baritone (GM67). Composition jobs can now write for the full SATB sax section.

5. **Reed speed ordering**: Soprano reed is the lightest and fastest-responding in the sax family. Attack timing across the sax family: soprano 0.03 < alto 0.04 < tenor 0.05 < baritone 0.07 (confirmed in FM_DEFAULTS).

6. **EQ body cut frequency**: Soprano sax body honk lives at ~800 Hz (higher than alto's 400 Hz) because the instrument is physically smaller — the resonant body frequency scales inversely with instrument size.

7. **Range overlap**: Soprano range (54-89) overlaps with alto (49-88) but the tone character is distinctly different — soprano is brighter, reedier, and sits above the alto in a section context. The sweet spot (67-79) is about a fourth higher than alto's sweet spot (61-79).

## FluidSynth Behavior

- `discover_soundfont()` finds FluidR3_GM.sf2 (141 MB, preferred)
- FluidR3 preset 64: clean, focused patch with fast reed attack, labelled "Soprano Sax"
- TimGM6mb.sf2 fallback: "Sop Sax (TB) v2.3" (TB = TimBrasse — thinner, more aggressive)
- No velocity layers or key-switching; single-layer patch with natural velocity→loudness
- Code MUST use `from sound.render.fluidsynth import discover_soundfont()` — never hardcode TimGM6mb

## File Locations

- Constants: `/opt/data/projects/Instruments/Woodwind/soprano_sax/soprano_sax.py`
- Research: `/opt/data/projects/Instruments/Woodwind/soprano_sax/instrument.md`
- Test script: `/opt/data/projects/Instruments/_test/verify_soprano_sax.py`
- Test MIDI: `/opt/data/projects/Instruments/_test/soprano_sax_test.mid` (111 bytes)
- Test WAV: `/opt/data/projects/Instruments/_test/soprano_sax_test.wav` (758 KB)
- Registry: `/opt/data/projects/Instruments/instrument_registry.py`
- Registry doc: `/opt/data/projects/Instruments/registry.md`