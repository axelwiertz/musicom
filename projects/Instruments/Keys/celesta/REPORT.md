# Celesta Research & Verification Report

**Date**: 2026-09-21  
**Instrument**: Celesta  
**Family**: Keys  
**GM Program**: 8 (0-indexed GM1/GM2 standard; 1-indexed GM #9)  
**GM Name**: Celesta  
**Stem Label**: `Celesta` (`trackXX_Celesta.wav`) — exact match, no quirk!  

---

## 1. Research Summary

### Identity & Physics
The celesta (or céleste, French for "heavenly") is a keyboard metallophone invented in Paris in 1886 by Auguste Mustel. The instrument resembles a small upright piano in appearance and action, but instead of strings, felt-covered hammers strike a set of tuned steel bars suspended over wooden resonance boxes. The resonators amplify the fundamental frequency of the plates and dampen harsh high-frequency metallic inharmonicity, producing a characteristic bell-chime timbre that is ethereal, delicate, round, and warm. 

Immortalized by Pyotr Ilyich Tchaikovsky in the *Dance of the Sugar Plum Fairy* from *The Nutcracker* (1892), the celesta became an indispensable color in late Romantic, Impressionist, and modern film scores (e.g., John Williams' *Hedwig's Theme*).

### Acoustic & MIDI Ranges
- **Sounding Range**: MIDI 48 to 108 (C3 to C8, ~130.8 Hz to 4186.0 Hz). Modern standard orchestral 5-octave instruments sound C3–C8; older 4-octave models span C4–C8 (60–108).
- **Notation / Transposition**: In traditional orchestral sheet music, the celesta is a transposing instrument written one octave below sounding pitch (sounds *8va alta*). In musicom standard MIDI convention, sounding pitch is used directly (RANGE_MIN=48, RANGE_MAX=108).
- **Sweet Spot**: MIDI 72 to 96 (C5 to C7, ~523.3 Hz to 2093.0 Hz) — singing celestial chime with maximum clarity, warmth, and ethereal carrying power.
- **Solo Range**: MIDI 60 to 96 (C4 to C7).
- **Register Zones**:
  - *Low* (48–59 / C3–B3): Dark, deep bell-hum; wooden resonator cavity resonance is prominent.
  - *Mid-Low* (60–71 / C4–B4): Mellow, warm, round chime; foundation for chordal beds and arpeggios.
  - *Mid-High* (72–83 / C5–B5): Sweet crystalline sparkle (*Sugar Plum Fairy* core melody register).
  - *High* (84–95 / C6–B6): Sparkling, brilliant, ethereal chime; transparent high arabesques.
  - *Altissimo* (96–108 / C7–C8): Delicate pinprick silver droplets; highly effective for top ornamentation.

### Articulations
- **Normale**: Velocity 78, duration 1.0 (standard felt hammer strike with natural plate ring).
- **Staccatissimo**: Velocity 75, duration 0.3 (pointillistic, crisp staccato drop).
- **Legato**: Velocity 70, duration 1.1 (sustained arpeggios, damper pedal engaged).
- **Accent**: Velocity 95, duration 0.9 (bright sforzato bell stroke).
- **Pianissimo**: Velocity 52, duration 1.0 (whisper-quiet mysterious celestial chime).
- **Arpeggio**: Velocity 72, duration 0.85 (cascading rolled chords across octaves).

### Timbre DNA & Synthesis Recommendations
1. **ModalSynth (`modal`) — Primary Recommendation**:
   - Resonator bank physical modeling (`sound/synthesis/modal.py`).
   - Stock preset `'bell'` provides standard inharmonic metallic resonance.
   - Dedicated `CELESTA_MODES` captures felt hammer strike, wooden resonator coupling, and steel plate modes:
     - $1.0\times f_0$ (decay rate 3.2): fundamental amplified by wooden cavity resonator
     - $2.76\times f_0$ (decay rate 4.8): transverse plate inharmonic mode
     - $5.40\times f_0$ (decay rate 6.5): higher flexural mode
     - $8.90\times f_0$ (decay rate 8.5): felt strike attack transient
2. **Karplus-Strong (`karplus`) — Fallback**:
   - High loop gain (`loop_gain: 0.9970`) models natural ~1.5–2.0 s chime decay.
   - Stereo width 0.40 models keyboard metallophone spread.
3. **PhaseModSynth (`phase_mod`) — Secondary Alternative**:
   - FM celestial chime: sine carrier + sine modulator, `mod_freq_ratio: 2.76`, `mod_depth: 1.1`, attack 3 ms, release 1.2 s.

### Production Defaults
- **Reverb Tail**: 2.4 s (concert hall reverberation allows crystalline celesta tones to float above the orchestra).
- **EQ**:
  - Body: +1.5 dB @ 500 Hz (wooden resonator fullness).
  - Presence: +1.8 dB @ 4.0 kHz (felt hammer strike clarity).
  - Air: +2.2 dB @ 11.0 kHz (silver shimmer and sparkle).
- **Pan**: +0.25 (standard orchestral layout: slightly right-of-center near percussion/harp).

---

## 2. Complete Constants (`Keys/celesta/celesta.py`)

```python
# -*- coding: utf-8 -*-
"""Celesta — musicom instrument constants."""

MIDI_PROGRAM = 8
GM_NAME = "Celesta"
STEM_LABEL = "Celesta"

RANGE_MIN = 48       # C3 (sounding)
RANGE_MAX = 108      # C8 (sounding)
SOLO_RANGE = (60, 96)   # C4–C7
SWEET_SPOT = (72, 96)   # C5–C7

ZONES = {
    "low": (48, 59),
    "mid_low": (60, 71),
    "mid_high": (72, 83),
    "high": (84, 95),
    "altissimo": (96, 108),
}

ARTICULATIONS = {
    "normale": (78, 1.0),
    "staccatissimo": (75, 0.3),
    "legato": (70, 1.1),
    "accent": (95, 0.9),
    "pianissimo": (52, 1.0),
    "arpeggio": (72, 0.85),
}

SYNTHESIS = "modal"
MODAL_PRESET = "bell"

CELESTA_MODES = [
    (440.0, 1.00, 3.2),
    (1214.4, 0.40, 4.8),
    (2376.0, 0.18, 6.5),
    (3916.0, 0.08, 8.5),
]

KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,
    "width": 0.40,
    "role": "lead",
}

FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_shape": "sine",
    "mod_freq_ratio": 2.76,
    "mod_depth": 1.1,
    "attack": 0.003,
    "release": 1.2,
}

REVERB_TAIL = 2.4
EQ_BODY = (500, 1.5)
EQ_PRESENCE = (4000, 1.8)
EQ_AIR = (11000, 2.2)
PAN = 0.25


def midi_to_freq(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
```

---

## 3. Registration Discipline Proof

Registered in `/opt/data/projects/Instruments/instrument_registry.py`:
- Dotted module path: `"Keys.celesta.celesta": "celesta"`
- Exported constant: `CELESTA = ALL_INSTRUMENTS["celesta"]`
- Extended `_FIELDS` with `celesta_modes`

### Registry Table & Verification Output:
```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Keys | Celesta | 8 | 48–108 | lead, melody, ornament, arpeggio, countermelody, accent |

Verification:
  CELESTA.midi_program = 8 (should be 8)
  by_name('celesta') = <Instrument Celesta (family=Keys, program=8, range=48-108)>
  by_program(8) = <Instrument Celesta (family=Keys, program=8, range=48-108)>
  CELESTA.in_sweet_spot(84) = True
```

---

## 4. Engine Verification Results (`_test/verify_celesta.py`)

- **Zero-drift validation**: `UnitMatrixComposer.validate()` → `True (OK)`
- **MIDI export**: `/opt/data/projects/Instruments/_test/celesta_test.mid` — **144 bytes** (>40 ✓)
- **Solo FluidSynth WAV**: `/opt/data/projects/Instruments/_test/celesta_test.wav` — **1,061,420 bytes** (>40 ✓)
- **Spectral buzz check**: 4–8 kHz buzz energy = **4.5%** (well within ≤20% gate, clean single voice, no comb-filtering ✓)
- **SoundFont discovery**: `discover_soundfont()` auto-resolved to `FluidR3_GM.sf2` (141 MB)
- **SoundFont pitch sweep**: `celesta_sweep.py` across full sounding compass 48–108:
  - Note 48 (C3): RMS 0.0854
  - Note 60 (C4): RMS 0.0964
  - Note 72 (C5): RMS 0.1127
  - Note 84 (C6): RMS 0.1100
  - Note 96 (C7): RMS 0.1016
  - Note 108 (C8): RMS 0.1015
  - All notes smoothly rendered with full body and zero dropouts.
- **Pipeline Stem Render**:
  - `track00_Celesta.wav` (1,061,420 bytes)
  - `track01_Electric_Bass_finger.wav`
  - Pipeline stem label: `trackXX_Celesta.wav` matches `GM_PROGRAMS[8]` exactly (**no quirk**).
