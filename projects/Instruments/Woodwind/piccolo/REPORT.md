# Piccolo Research & Verification Report

**Date**: 2026-09-20  
**Instrument**: Piccolo  
**Family**: Woodwind  
**GM Program**: 72 (0-indexed GM1/GM2 standard)  
**GM Name**: Piccolo  
**Stem Label**: `Piccolo` (`trackXX_Piccolo.wav`) — exact match, no quirk!

---

## 1. Research Summary

### Identity & Physics
The piccolo (Italian for "small", formally *ottavino* or *flauto piccolo*) is the soprano member of the transverse flute family. Built at half the acoustic pipe length of the concert Western C flute (~32 cm vs ~67 cm), it oscillates an octave higher (C5–C8 sounding pitch). Because of its narrower bore and short tube length, acoustic inertia is significantly lower, giving near-instantaneous speech response, intense chiff attack transients, and the ability to pierce through full orchestral tuttis even at *piano* and *mezzo-forte* dynamics.

### Acoustic & MIDI Ranges
- **Sounding Range**: MIDI 72 to 108 (C5 to C8, ~523.3 Hz to 4186.0 Hz). Standard acoustic orchestra models bottom out at D5 (74), while professional models and GM soundfont patches extend down to C5 (72).
- **Sweet Spot**: MIDI 84 to 96 (C6 to C7, ~1046.5 Hz to 2093.0 Hz) — clear, brilliant, singing tone with sparkling carrying power without harsh shrillness.
- **Solo Range**: MIDI 79 to 101 (G5 to F7).
- **Register Zones**:
  - *Low* (72–79 / C5–G5): Soft, breathy, quiet, easily masked by thick orchestration; effective for mysterious and pastoral solos.
  - *Mid* (80–91 / Ab5–G6): Lyrical, expressive, singing, agile woodwind melodic core.
  - *High* (92–101 / Ab6–F7): Brilliant, penetrating, bright; cuts over brass and full percussion.
  - *Altissimo* (102–108 / F#7–C8): Shrill, shrieking, military marches, storm effects, high dramatic climaxes.

### Articulations
- **Legato**: Velocity 70, duration 1.0 (smooth singing lines).
- **Staccato**: Velocity 65, duration 0.25 (crisp, pointed double and triple tonguing).
- **Accent**: Velocity 95, duration 0.85 (piercing sforzando attack).
- **Flutter tongue**: Velocity 72, duration 1.0 (frullato rolling throat/tongue effect).
- **Breath tone**: Velocity 50, duration 0.9 (airy whisper).
- **Trill**: Velocity 70, duration 0.5 (avian ornamentation).

### Recommended Synthesis Engines
1. **PhaseModSynth (`phase_mod`)**:
   - Sine carrier modulated by sine modulator at 1:1 frequency ratio (`mod_freq_ratio: 1.0`).
   - Shallow modulation depth (`mod_depth: 1.2`) adds just enough upper harmonic energy to recreate the acoustic embouchure jet without harsh FM distortion.
   - Attack 0.04 s, release 0.10 s.
2. **AirPipe (`air_pipe`)**:
   - Physical aerophone physical modeling: cylindrical open pipe resonator (`stopped=False`).
   - Scaled length (`length_scale: 0.5`) matching half the C flute length.
   - Jet pressure `0.65` reproducing the narrow-bore overblow behavior.
3. **AdditiveSynth (`additive`)**:
   - Strong fundamental (1.0), weaker 2nd harmonic (0.35), subtle 3rd harmonic (0.12), and high-frequency breath noise floor (>8 kHz).

### Production Defaults
- **Reverb Tail**: 2.2 s (room/hall reverb allows sparkling high transients to float smoothly).
- **EQ**:
  - Body: +2.0 dB @ 1.2 kHz
  - Presence: +3.0 dB @ 3.5 kHz
  - Air: +2.0 dB @ 10 kHz
- **Pan**: +0.15 (standard woodwind placement slightly right of first flute).

---

## 2. Complete Constants (`Woodwind/piccolo/piccolo.py`)

```python
# -*- coding: utf-8 -*-
"""Piccolo — musicom instrument constants."""

MIDI_PROGRAM = 72
GM_NAME = "Piccolo"
STEM_LABEL = "Piccolo"

RANGE_MIN = 72       # C5
RANGE_MAX = 108      # C8
SOLO_RANGE = (79, 101)  # G5 to F7
SWEET_SPOT = (84, 96)   # C6 to C7

ZONES = {
    "low": (72, 79),
    "mid": (80, 91),
    "high": (92, 101),
    "altissimo": (102, 108),
}

ARTICULATIONS = {
    "legato": (70, 1.0),
    "staccato": (65, 0.25),
    "accent": (95, 0.85),
    "flutter": (72, 1.0),
    "breath": (50, 0.9),
    "trill": (70, 0.5),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 1.2,
    "attack": 0.04,
    "release": 0.10,
}

AIR_PIPE_DEFAULTS = {
    "pressure": 0.65,
    "stopped": False,
    "length_scale": 0.5,
}

REVERB_TAIL = 2.2
EQ_BODY = (1200, 2.0)
EQ_PRESENCE = (3500, 3.0)
EQ_AIR = (10000, 2.0)
PAN = 0.15


def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

---

## 3. Registration Discipline Proof

Registered in `/opt/data/projects/Instruments/instrument_registry.py`:
- Dotted module path: `"Woodwind.piccolo.piccolo": "piccolo"`
- Convenience constant: `PICCOLO = ALL_INSTRUMENTS["piccolo"]`
- Added to role mapping and verification assertions.

### Execution Output of `instrument_registry.py`:

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Brass | French Horn | 60 | 41–84 | lead, harmony, accent |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | Trumpet | 56 | 54–86 | lead, harmony, accent |
| Brass | Tuba | 58 | 26–72 | bass, counter, accent, harmony |
| Guitar | Acoustic Guitar (nylon) | 25 | 40–84 | lead, harmony, accent |
| Keys | Acoustic Grand Piano | 1 | 21–108 | lead, harmony, accent |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Keys | Harpsichord | 6 | 29–89 | harmony, continuo, melody, ornament, countermelody, accent |
| Percussion | Drum Kit | 0 | - | rhythm, groove, accent |
| Percussion | Glockenspiel | 9 | 79–108 | lead, melody, ornament, accent, countermelody |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
| Percussion | Xylophone | 13 | 53–89 | lead, melody, ornament, accent, countermelody |
| Strings | Cello | 42 | 36–84 | bass, counter, accent, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, counter, accent, harmony |
| Strings | Orchestral Harp | 46 | 24–103 | harmony, arpeggio, glissando, melody, countermelody, accent |
| Strings | Viola | 41 | 48–91 | lead, harmony, accent |
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Vocal | Didgeridoo | 20 | 24–55 | lead, harmony, accent |
| Vocal | Human Voice | 53 | 48–84 | lead, melody, countermelody |
| Vocal | Jaw Harp | 106 | 36–74 | lead, harmony, accent |
| Vocal | Kazoo | 59 | 50–86 | lead, harmony, accent |
| Vocal | Singing Saw | 81 | 55–91 | lead, harmony, accent |
| Vocal | Talkbox | 80 | 45–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, harmony, accent |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
| Woodwind | Bassoon | 70 | 34–88 | lead, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, harmony, accent |
| Woodwind | Flute | 74 | 60–96 | lead, harmony, accent |
| Woodwind | Oboe | 68 | 52–92 | lead, harmony, accent |
| Woodwind | Piccolo | 72 | 72–108 | lead, melody, ornament, accent, countermelody |
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
| World | Taiko Drum | 116 | 36–67 | accent, rhythm, drone, ornament |

Verification:
  ...
  PICCOLO.midi_program = 72 (should be 72)
  by_name('piccolo') = <Instrument Piccolo (family=Woodwind, program=72, range=72-108)>
  by_program(72) = <Instrument Piccolo (family=Woodwind, program=72, range=72-108)>
  PICCOLO.in_sweet_spot(88) = True
```

---

## 4. Verification Suite Results (`_test/verify_piccolo.py`)

- **Zero-drift validation**: `True (OK)` (exact tick parity across all voices and sections).
- **MIDI size**: 144 bytes (`/opt/data/projects/Instruments/_test/piccolo_test.mid`).
- **WAV solo render**: 768,300 bytes (`/opt/data/projects/Instruments/_test/piccolo_test.wav`).
- **Spectral Buzz Gate**: 4–8 kHz band energy = **3.3%** (threshold <= 20%, clean solo voice, zero comb-filtering/beating).
- **Pipeline Stem Match**:
  - `RenderPipeline.render_stems` generated `track00_Piccolo.wav` (768,300 bytes) and `track01_Electric_Bass_finger.wav` (741,676 bytes).
  - GM program 72 maps directly to `"Piccolo"`.
- **SoundFont Check**:
  - `discover_soundfont()` resolved to `/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2`.
  - Preset (bank 0, preset 72) confirmed as `'Piccolo'`.
- **Pitch Sweep Check (FluidR3)**:
  - Tested MIDI 72 to 108 across 11 pitch points.
  - All notes audible: RMS values range from 0.0482 to 0.1032. No gaps, dead zones, or truncation.
- **Synthesis Engine Checks**:
  - `PhaseModSynth`: rendered C6 peak = 0.799.
  - `AirPipe`: calculated physical length = 7.9 cm, radius = 4.9 mm, fundamental = 2093.0 Hz, 21 resonance modes.

---

## 5. Quirks Found & Noted
- **No Stem Mismatch**: Unlike GM74 (Flute) which is mislabeled `"Recorder"` in the pipeline's GM list, GM72 is accurately labeled `"Piccolo"`, matching both the GM2 specification and FluidR3 preset name exactly.
- **Transposition**: Piccolo is a sounding octave transposing instrument in standard sheet music, but in GM standard and musicom, pitches are always written at concert sounding pitch (72–108).
