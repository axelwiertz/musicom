# Tubular Bells (Orchestral Chimes) — Instrument Research Report

**Date**: 2026-09-26
**Author**: Nightly Instrument Research Job
**Instrument**: Tubular Bells (GM14)

## Summary

| Attribute | Value |
|---|---|
| Family | Percussion |
| GM Program | 14 |
| GM Name | "Tubular Bells" |
| Stem Label | Tubular_Bells |
| Range | 60–78 (C4–F5, standard 1.5-octave 18-tube orchestral chimes) |
| Sweet Spot | 60–72 (C4–C5 fundamental octave) |
| Role | accent, color, drone, lead, ornament |
| Synthesis Engine | modal (ModalSynth) with custom TUBULAR_BELLS_MODES |
| Modal Preset | 'bell' (stock), custom bank for exact brass-tube partials |
| Reverb Tail | 2.5 s (hall/church — idiomatic) |
| Pan | 0.0 (center) |

## Constants (tubular_bells.py)

```python
MIDI_PROGRAM = 14
GM_NAME = "Tubular Bells"
STEM_LABEL = "Tubular_Bells"
RANGE_MIN = 60        # C4
RANGE_MAX = 78        # F5
SOLO_RANGE = (60, 78)
SWEET_SPOT = (60, 72)

ZONES = {
    "low": (60, 66),     # C4–C#5
    "mid": (67, 72),     # D5–C5
    "high": (73, 78),    # C#5–F5
}

ARTICULATIONS = {
    "stroke": (84, 1.0),
    "hard": (96, 0.8),
    "soft": (60, 1.0),
    "roll": (70, 0.06),
    "muted": (72, 0.2),
    "accent": (94, 0.9),
}

SYNTHESIS = "modal"
MODAL_PRESET = "bell"
TUBULAR_BELLS_MODES = [
    (440.0, 1.00, 0.50),   # f0
    (1214.4, 0.55, 0.80),  # 2.76x
    (2376.0, 0.25, 1.20),  # 5.40x
    (3929.2, 0.10, 2.00),  # 8.93x
]

KARPLUS_DEFAULTS = {
    "loop_gain": 0.9970,
    "width": 0.25,
    "role": "accent",
}

FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.76,
    "mod_depth": 1.8,
    "attack": 0.001,
    "release": 2.0,
}

REVERB_TAIL = 2.5
EQ_BODY = (300, -2.0)
EQ_PRESENCE = (2500, 2.5)
EQ_AIR = (7000, 1.5)
PAN = 0.0
```

## Synthesis Details

**Primary: ModalSynth** — The struck brass tube is modelled as a 4-mode inharmonic resonator bank. The tube's free-free bending-mode ratios (1 : 2.76 : 5.40 : 8.93) produce a warm, fundamental-rich "church bell" character. Decay rates 0.50/0.80/1.20/2.00 (slow — brass tube rings for 1.5–3 s, comparable to vibraphone). The stock 'bell' preset is a metallic-bar approximation only; the custom TUBULAR_BELLS_MODES bank is the exact voice.

**Karplus-Strong** — Demoted fallback (tube is struck, not plucked). Loop_gain 0.9970 gives long metallic ring (~1.5–2.5 s, comparable to glockenspiel 0.9980).

**PhaseModSynth** — FM bell alternative: sine carrier, mod ratio 2.76 (dominant bell overtone), depth 1.8, attack 0.001, release 2.0.

## Identity

GM14 = Tubular Bells (orchestral chimes) — struck brass tubes suspended in a frame. The iconic tintinnabuli colour: church-bell sonorities (Tchaikovsky 1812 Overture C4 chimes, Berlioz Symphonie Fantastique "Dies Irae", Mahler Symphony 2 "Resurrection"), ceremonial accents, and the Mike Oldfield "Tubular Bells" theme. NOT a melodic keyboard percussion (marimba, vibraphone, glockenspiel) — the range is only 1.5 octaves, so it is a **colour/effect instrument** for spare, resonant punctuation.

## Registration Proof

Registry table output (from `instrument_registry.py`):

```
| Percussion | Tubular Bells | 14 | 60–78 | accent, color, drone, lead, ornament |
```

Verification:

```
TUBULAR_BELLS.midi_program = 14 (should be 14)
by_name('tubular bells') = <Instrument Tubular Bells (family=Percussion, program=14, range=60-78)>
by_program(14) = <Instrument Tubular Bells (family=Percussion, program=14, range=60-78)>
TUBULAR_BELLS.in_sweet_spot(67) = True
TUBULAR_BELLS.in_sweet_spot(40) = False (should be False)
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift | True (OK) |
| MIDI file | 91 bytes (> 40 ✓) |
| WAV file (solo) | 4,119,084 bytes (> 40 ✓) |
| Spectral check | 4–8 kHz buzz = 3.1% (< 20% ✓) |
| Stem label | `track00_Tubular_Bells.wav` (matches GM_PROGRAMS[14]) |
| STEM_LABEL constant | "Tubular_Bells" |
| Registry import | TUBULAR_BELLS accessible, by_name/by_program work |

## Quirks

1. **Colour instrument**: GM14 has only 1.5 octaves (C4–F5). Used for accent/ceremonial punctuation, NOT melodic passagework. One stroke at a time is the idiom.

2. **Channel quirk**: MUST use a melodic channel (0–9) with program 14. Channel 9 triggers the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback label (timpani lesson).

3. **Stem label**: GM_PROGRAMS[14] = "Tubular Bells" → `trackXX_Tubular_Bells.wav`. Labels match exactly, **no quirk**.

4. **FluidR3 preset**: 14 = "Tubular Bells" (verified from the SF2 preset name). Matches exactly, no quirk.

5. **Karplus-Strong demoted**: The tube is struck, not plucked — KS is a poor physical model for this instrument.

## Files Created

- `Percussion/tubular_bells/instrument.md` — full research reference
- `Percussion/tubular_bells/tubular_bells.py` — importable constants
- `_test/verify_tubular_bells.py` — full verification script
- `instrument_registry.py` — registered as `Percussion.tubular_bells.tubular_bells` → key `tubular_bells`, constant `TUBULAR_BELLS`
- `registry.md` — updated with new entry and changelog