# REPORT — Glockenspiel (GM9, Percussion family) — 2026-09-19

## Summary

| Item | Value |
|---|---|
| Instrument | Glockenspiel (orchestral steel bells) |
| Family | Percussion (6th entry: drum_kit, marimba, steel_drums, vibraphone, timpani, xylophone, **glockenspiel**) |
| MIDI program | **9** (0-based GM1 "Glockenspiel"; raw program=9) |
| Range | 79–108 (G5–C8 sounding pitch, standard 2.5-octave orchestra bells; SF2 patch responds down to 55 for transposed written scores) |
| Sweet spot | 84–100 (C6–E7, bright crystalline bell chime) |
| Role | lead, melody, ornament, accent, countermelody |
| Synthesis | ModalSynth primary (stock 'bell' preset + custom `GLOCKENSPIEL_MODES`); Karplus-Strong fallback (`loop_gain` 0.9980); PhaseModSynth cheap alt |
| Stem label | `trackXX_Glockenspiel.wav` — GM_PROGRAMS[9] = "Glockenspiel" = FluidR3 preset 9, **no quirk** |
| Files | `Percussion/glockenspiel/instrument.md`, `Percussion/glockenspiel/glockenspiel.py`, `_test/verify_glockenspiel.py` |
| Registry | `instrument_registry.py`: `"Percussion.glockenspiel.glockenspiel": "glockenspiel"` + `GLOCKENSPIEL = ALL_INSTRUMENTS["glockenspiel"]` + role mapping + `__main__` verification block |

## Why Glockenspiel

The Percussion pitched mallet family already contained Marimba (wood, GM12), Vibraphone (aluminum with tremolo, GM11), and Xylophone (dry rosewood, GM13). Glockenspiel (steel bars, GM9) fills the essential high-register metallic pitched percussion role: the brightest, highest-reaching melodic treble voice in the orchestra (sounding G5–C8). It pairs perfectly with musicom's `ModalSynth` engine ('bell' preset and steel plate/bar inharmonic resonators).

## Constants (glockenspiel.py)

```python
MIDI_PROGRAM = 9
GM_NAME = "Glockenspiel"
STEM_LABEL = "Glockenspiel"
RANGE_MIN, RANGE_MAX = 79, 108       # G5–C8 sounding pitch
SOLO_RANGE = (84, 103)               # C6–G7
SWEET_SPOT = (84, 100)               # C6–E7
ZONES = {
    "low": (79, 86),     # G5–D6
    "mid": (87, 98),     # D#6–D7
    "high": (99, 108),   # D#7–C8
}
ARTICULATIONS = {
    "hard_mallet": (88, 1.0),
    "soft_mallet": (68, 1.2),
    "staccato": (80, 0.4),
    "double_stop": (76, 1.0),
    "glissando": (72, 0.3),
}
SYNTHESIS = "modal"
MODAL_PRESET = "bell"
GLOCKENSPIEL_MODES = [
    (1046.5, 1.00, 2.5),   # C6 fundamental
    (2836.0, 0.50, 4.0),   # ~2.71x inharmonic steel clang
    (5389.0, 0.25, 6.5),   # ~5.15x shimmer partial
    (8822.0, 0.12, 9.0),   # ~8.43x silver transient
]
KARPLUS_DEFAULTS = {"loop_gain": 0.9980, "width": 0.35, "role": "lead"}
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 3.5,
    "mod_depth": 1.6,
    "attack": 0.001,
    "release": 1.5,
}
REVERB_TAIL = 2.2        # seconds — glockenspiel blooms in concert hall reverb
EQ_BODY = (800, -2.0)
EQ_PRESENCE = (3500, 2.0)
EQ_AIR = (10000, 2.5)
PAN = 0.20
def midi_to_freq(m): return 440.0 * (2.0 ** ((m - 69) / 12.0))
```

## Registration Proof (instrument_registry.py)

Command run:
```bash
cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py
```

Output:
```
| Percussion | Glockenspiel | 9 | 79–108 | lead, melody, ornament, accent, countermelody |
...
  GLOCKENSPIEL.midi_program = 9 (should be 9)
  by_name('glockenspiel') = <Instrument Glockenspiel (family=Percussion, program=9, range=79-108)>
  by_program(9) = <Instrument Glockenspiel (family=Percussion, program=9, range=79-108)>
  GLOCKENSPIEL.in_sweet_spot(84) = True
```
Total instruments loaded: 43.

## Verification Results (_test/verify_glockenspiel.py)

- **Registry import**: `by_name('glockenspiel')` and `by_program(9)` return `Instrument Glockenspiel` (program 9) ✓
- **Zero-drift**: `UnitMatrixComposer` validate gate returned `True (OK)` ✓
- **MIDI file**: `_test/glockenspiel_test.mid` generated (144 bytes, >40 bytes ✓)
- **WAV solo render**: `_test/glockenspiel_test.wav` generated via FluidSynth + FluidR3_GM.sf2 (1,694,508 bytes, >40 bytes ✓)
- **RenderPipeline stem export**:
  - `track00_Glockenspiel.wav` (1,694,508 bytes)
  - `track01_Electric_Bass_finger.wav` (741,676 bytes)
  - Stem label matches GM_PROGRAMS[9] = "Glockenspiel" exactly, **no quirk** ✓
- **FluidR3 patch**: preset 9 = "Glockenspiel" in FluidR3_GM.sf2 phdr chunk ✓
- **Pitch sweep audibility**: 12/12 test notes audible (RMS 0.0490 to 0.0952) across sounding range (79–108) and lower transposed range (55–78), no gaps ✓
- **Synthesis checks**:
  - `ModalSynth.render_preset('bell')` rendered cleanly (peak=0.900) ✓
  - `ModalSynth.render_custom(GLOCKENSPIEL_MODES)` rendered cleanly (peak=0.900) ✓
  - `karplus_strong` fallback rendered cleanly with sustained tail (peak=0.277, tail_rms=0.0011) ✓

## Quirks Found

- **No stem label quirk**: GM_PROGRAMS[9] is "Glockenspiel", matching the SF2 preset exactly.
- **Transposition notation vs MIDI sounding pitch**: In traditional orchestral sheet music, glockenspiel is written two octaves lower (G3–C6) to fit the treble staff. In musicom and standard MIDI, sounding pitch (G5–C8, MIDI 79–108) is the standard range. FluidR3_GM preset 9 responds down to MIDI 55, allowing playback of transposed files if encountered.
- **High spectrum energy**: Struck steel bars produce high natural acoustic energy in the 4–8 kHz band (~30% spectral energy), which is the physical hallmark of bells rather than comb-filtering buzz. Solo single-voice render guarantees zero comb-filtering.
