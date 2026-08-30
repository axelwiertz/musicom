# REPORT — Alto Saxophone

**Date**: 2026-08-30 (nightly instrument research job)
**Instrument**: Alto Saxophone (GM 65)
**Family**: Woodwind
**Status**: ✅ VERIFIED end-to-end

---

## Instrument

| Field | Value |
|---|---|
| Family | Woodwind |
| Name | Alto Saxophone |
| MIDI program | 65 |
| GM name | "Alto Sax" |
| SF2 preset | `AltoSax (TB) v2.3` (preset 65, verified from phdr chunk) |
| RenderPipeline stem label | `Alto_Sax` → `trackXX_Alto_Sax.wav` |

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 49–88 | Db3–E6 | concert alto sax + altissimo |
| Solo range | 54–82 | F#3–Ab5 | practical solo repertoire |
| Sweet spot | 61–79 | C4–G5 | singing solo register, round full tone |
| Low | 49–60 | Db3–C4 | dark, husky, breathy |
| Mid | 61–70 | C4–B4 | warm, vocal, ballad territory |
| High | 71–88 | C5–E6 | bright, cutting, altissimo scream |

## Role

- Lead melody (C4-G5 sweet spot — pop/jazz/funk/soul default "sexy sax")
- Countermelody (fills behind vocals)
- Accent/ornament (falls, bends, horn-section hits)
- Harmony (sax section, horn stabs)
- NOT bass, NOT rhythm (sustained melodic voice)

## Synthesis Engine

- **Primary**: `phase_mod` — PhaseModSynth (`sound/synthesis/phase_mod.py`)
  - `carrier_shape: saw` (conical single-reed: even+odd harmonics)
  - `mod_freq_ratio: 1.0`, `mod_depth: 2.8` (brighter/reedier than clarinet's 2.0)
  - `attack: 0.04` (breathy reed onset), `release: 0.10`
- **Alt**: `additive` — explicit even+odd partials, boost 1–3 kHz honk, breath-noise floor
- **Avoid**: ModalSynth (better for strings/percussion)
- Wide sax vibrato (4–6 Hz, ±0.3–0.6 st) NOT in the FM engine — add as post LFO / pitch bend

## Constants (saxophone.py)

```python
MIDI_PROGRAM = 65
GM_NAME = "Alto Saxophone"
STEM_LABEL = "Alto_Sax"          # pipeline GM_PROGRAMS[65] = "Alto Sax" -> Alto_Sax
RANGE_MIN = 49      # Db3
RANGE_MAX = 88      # E6
SOLO_RANGE = (54, 82)
SWEET_SPOT = (61, 79)
ZONES = {"low": (49, 60), "mid": (61, 70), "high": (71, 88)}
ARTICULATIONS = {
    "legato": (80, 1.0), "tenuto": (72, 0.9), "staccato": (66, 0.25),
    "accent": (92, 0.9), "growl": (76, 1.0), "vibrato": (78, 1.0),
}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 1.0, "mod_depth": 2.8,
               "attack": 0.04, "release": 0.10}
REVERB_TAIL = 1.6
EQ_BODY = (400, -2.0)
EQ_PRESENCE = (2000, 2.5)
EQ_AIR = (6000, 1.5)
PAN = 0.0
```

## Verification (engine test, 2026-08-30)

Full UnitMatrixComposer test (1 bar, 3 voices: Sax + Clarinet + Piano):

- **Zero-drift validate**: ✅ `True (OK)`
- **MIDI export**: `/opt/data/projects/Instruments/_test/saxophone_test.mid` — **183 bytes** (> 40 ✓)
- **FluidSynth render** (`-ni -g 1.2`, TimGM6mb.sf2): exit 0
- **WAV**: `/opt/data/projects/Instruments/_test/saxophone_test.wav` — **880,428 bytes** (> 40 ✓)
- **RenderPipeline stems**: 3 files, incl. `track00_Alto_Sax.wav` (783,404 bytes > 40 ✓)
- SF2 preset 65 = `AltoSax (TB) v2.3` ✓ (phdr check)
- Stem label `GM_PROGRAMS[65]` = `"Alto Sax"` ✓

Verify script: `_test/verify_saxophone.py` — **ALL CHECKS PASSED**

## Quirks Found

1. **Stem label is "Alto_Sax", NOT "Saxophone"** — pipeline `GM_PROGRAMS[65] =
   "Alto Sax"` (sanitized `Alto_Sax`). `orchestrator.py` already maps
   "Saxophone"→65 correctly (program), but any stem-aware code must match the
   ACTUAL disk label `Alto_Sax`, not the family name. (Same class of quirk as
   GM43→"Contrabass".)
2. **SF2 preset "AltoSax (TB) v2.3"** — TimBrasse-derived bright reedy sax;
   suffix/underscore cosmetic, no routing impact. The "(TB)" suffix marks the
   well-known TimGM6mb sax timbre.
3. **MidiInstrument enum has NO sax** — only 10 instruments exposed (PIANO=1,
   CHURCH_ORGAN=20, ACOUSTIC_GUITAR=25, VIOLIN=41, STRING_ENSEMBLE=49,
   TRUMPET=57, FLUTE=74, SYNTH_PAD=88, BASS=33). Use raw `program=65`.
4. **Sax program family**: GM 64=Soprano, 65=Alto, 66=Tenor, 67=Baritone. This
   entry covers 65 (Alto, the default pop/jazz sax). All four are distinct
   pipeline labels (`Soprano Sax`/`Alto Sax`/`Tenor Sax`/`Baritone Sax`).
