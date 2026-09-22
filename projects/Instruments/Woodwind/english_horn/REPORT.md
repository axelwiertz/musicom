# English Horn (Cor Anglais) Research & Verification Report

**Date**: 2026-09-22  
**Instrument**: English Horn (Cor Anglais)  
**Family**: Woodwind  
**GM Program**: 69 (0-indexed GM1/GM2 standard; 1-indexed GM #70)  
**GM Name**: English Horn  
**Stem Label**: `English_Horn` (`trackXX_English_Horn.wav`) — exact match, no quirk!  

---

## 1. Research Summary

### Identity & Physics
The English horn (French: *cor anglais*, Italian: *corno inglese*) is a double-reed woodwind instrument in the oboe family, pitched a perfect fifth lower than the standard soprano oboe (tenor oboe in F). Key acoustic characteristics include:
- A pear-shaped bulbous bell (*liebesfuss*) that acoustically attenuates piercing high partials and enriches warm low-mid resonances.
- A curved metal bocal (crook) carrying a wide double reed.
- A wide conical bore producing a dark, velvety, melancholic, and pastoral timbre.

Famous for its elegiac and nostalgic solo literature, notably Antonín Dvořák's *Symphony No. 9 "From the New World"* (Largo), Jean Sibelius's *The Swan of Tuonela*, and Maurice Ravel's *Piano Concerto in G*.

### Acoustic & MIDI Ranges
- **Sounding Range**: MIDI 50 to 85 (D3 to C#6, ~146.8 Hz to ~1108.7 Hz).
  - Standard orchestral sounding compass: E3 to A5 (MIDI 52 to 81).
  - Extended range in modern instruments and FluidR3_GM.sf2: D3 to C#6 (MIDI 50 to 85).
- **Notation / Transposition**: Traditional orchestral sheet music transposes up a perfect fifth (written C4 sounds F3). In musicom MIDI convention, concert sounding pitch is used directly.
- **Sweet Spot**: MIDI 57 to 72 (A3 to C5, ~220.0 Hz to ~523.3 Hz) — the quintessential pastoral, plaintive, singing solo register.
- **Solo Range**: MIDI 52 to 77 (E3 to F5).
- **Register Zones**:
  - *Low* (50–56 / D3–G#3): Deep, dark, husky, velvety double-reed drone.
  - *Sweet Spot* (57–72 / A3–C5): Haunting, lyrical singing solo voice.
  - *Mid-High* (73–79 / C#5–G5): Intense, expressive, poignant, penetrating melodic lines.
  - *Altissimo* (80–85 / G#5–C#6): Thin, pinched, dramatic top; FluidR3 preset 69 cuts off above 85.

### Articulations
- **Legato**: Velocity 78, duration 1.05 (cantabile, smooth lyrical phrasing — default).
- **Espressivo**: Velocity 85, duration 1.10 (melodic line with prominent vibrato swell).
- **Tenuto**: Velocity 72, duration 0.90 (deliberate held note with gentle separation).
- **Staccato**: Velocity 65, duration 0.30 (short, rounded double-tongued articulation).
- **Accent**: Velocity 94, duration 0.85 (incisive double-reed tonguing, emphatic entry).
- **Pianissimo**: Velocity 52, duration 1.00 (breath-supported whisper, distant pastoral melancholy).

### Timbre DNA & Synthesis Recommendations
1. **PhaseModSynth (`phase_mod`) — Primary Recommendation**:
   - Resonator: sawtooth carrier (conical bore even + odd harmonic series).
   - Modulator: sine wave, fundamental tracking (`mod_freq_ratio: 1.0`).
   - `mod_depth: 2.2` (rounder and warmer than soprano oboe's 2.5).
   - Attack: 0.06 s (reed onset inertia), Release: 0.12 s.
2. **AdditiveSynth (`additive`) — Alternative**:
   - Rich harmonic series boosting partials 2 through 4 for warm body.
   - Formant resonance hump at 1.8–2.2 kHz (liebesfuss cavity resonance).

### Production Defaults
- **Reverb Tail**: 2.2 s (concert hall acoustic space cradles the tone).
- **EQ**:
  - Body: +2.0 dB @ 600 Hz (pear-bell body resonance).
  - Boxiness Cut: -1.5 dB @ 350 Hz (clarity).
  - Presence: +2.0 dB @ 2.2 kHz (reed articulation formant).
  - Air: -1.0 dB high shelf @ 8.0 kHz (preserves intimate pastoral warmth).
- **Pan**: +0.10 (slightly right of center in orchestral woodwind section).

---

## 2. Complete Constants (`Woodwind/english_horn/english_horn.py`)

```python
# -*- coding: utf-8 -*-
"""English Horn (Cor Anglais) — musicom instrument constants."""

MIDI_PROGRAM = 69
GM_NAME = "English Horn"
STEM_LABEL = "English_Horn"

RANGE_MIN = 50        # D3 (sounding, lowest extended range)
RANGE_MAX = 85        # C#6 (sounding, upper boundary of FluidR3 preset 69)
SOLO_RANGE = (52, 77) # E3-F5 (standard orchestral solo compass)
SWEET_SPOT = (57, 72) # A3-C5 (pastoral, plaintive singing register, New World Largo)

ZONES = {
    "low": (50, 56),        # D3-G#3, deep dark husky velvety double-reed drone
    "sweet_spot": (57, 72), # A3-C5, plaintive singing solo voice
    "mid_high": (73, 79),   # C#5-G5, intense expressive penetrating melodic lines
    "altissimo": (80, 85),  # G#5-C#6, thin pinched dramatic top
}

ARTICULATIONS = {
    "legato": (78, 1.05),
    "espressivo": (85, 1.10),
    "tenuto": (72, 0.90),
    "staccato": (65, 0.30),
    "accent": (94, 0.85),
    "pianissimo": (52, 1.00),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.2,
    "attack": 0.06,
    "release": 0.12,
}

REVERB_TAIL = 2.2
EQ_BODY = (600, 2.0)
EQ_PRESENCE = (2200, 2.0)
EQ_AIR = (8000, -1.0)
PAN = 0.10

def midi_to_freq(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

---

## 3. Registration Verification Proof

Output from executing `instrument_registry.py`:
```text
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
...
| Woodwind | Clarinet | 71 | 52–96 | lead, harmony, accent |
| Woodwind | English Horn | 69 | 50–85 | lead, countermelody, melody, harmony, accent |
| Woodwind | Flute | 74 | 60–96 | lead, harmony, accent |
...

Verification:
  ENGLISH_HORN.midi_program = 69 (should be 69)
  by_name('english horn') = <Instrument English Horn (family=Woodwind, program=69, range=50-85)>
  by_program(69) = <Instrument English Horn (family=Woodwind, program=69, range=50-85)>
  ENGLISH_HORN.in_sweet_spot(65) = True
```

---

## 4. Engine & Solo Audio Verification Results

Executed via `_test/verify_english_horn.py`:
- **Registry loading**: Successful (`by_name("english horn")`, `by_program(69)`, `ENGLISH_HORN` constant).
- **UnitMatrixComposer**: 1 bar, 1 section, 120 BPM, 4/4 time.
- **Zero-drift gate**: Passed (`validate()` = `True (OK)`).
- **Solo Voice Stack**: Track 0 is solo English Horn (no unison doubling); Track 1 is bass C1 context note 3 octaves below.
- **Exported MIDI**: `/opt/data/projects/Instruments/_test/english_horn_test.mid` — 144 bytes (> 40 bytes ✓).
- **FluidSynth SoundFont Render**: Using `discover_soundfont()` (`FluidR3_GM.sf2`).
- **Rendered WAV (Solo)**: `/opt/data/projects/Instruments/_test/english_horn_test.wav` — 741,420 bytes (> 40 bytes ✓).
- **Spectral Buzz Gate**: 4–8 kHz buzz energy = 0.8% (passed, well within 20% limit).
- **RenderPipeline Stem Verification**:
  - `RenderPipeline.render_stems` generated: `['track00_English_Horn', 'track01_Electric_Bass_finger']`.
  - Stem file: `/opt/data/projects/Instruments/_test/stems_english_horn/track00_English_Horn.wav`.
  - Exact match with pipeline `GM_PROGRAMS[69]` (`"English Horn"`).

---

## 5. SoundFont & Pitch Sweep Quirks

Full chromatic sweep (`_test/sweep_english_horn.py`):
- FluidR3_GM preset 69 is fully audible across MIDI 48 to 85 (RMS 0.0276 to 0.0482).
- Hard ceiling at note 85 (C#6): note 86 and 87 produce 0.0000 RMS (preset key limit).
- Preserves full standard orchestral compass (52–81 / E3–A5) with head and foot margin.
