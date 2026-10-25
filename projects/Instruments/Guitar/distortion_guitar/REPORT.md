# REPORT — Distortion Guitar (GM30)

**Date**: 2026-10-25 · **Job**: nightly instrument research (layer-aligned)
**Status**: REGISTERED + VERIFIED END-TO-END

## Instrument

| Field | Value |
|---|---|
| Name | Distortion Guitar |
| Family | Guitar |
| GM program | 30 (GM1 Distortion Guitar; 0-indexed — matches FluidR3 preset 30 and RenderPipeline `GM_PROGRAMS[30]`) |
| GM name | "Distortion Guitar" |
| Stem label | `Distortion_Guitar` (pipeline + SF2 match exactly — **no quirk**) |
| Range | 28–84 (E1–C6 GM patch span; real 22-fret guitar = E2–E6 = 40–76) |
| Solo range | 45–76 (A2–E6) |
| Sweet spot | 52–72 (E3–C5) |
| Role | lead, melody, accent, rhythm, power-chord strum, countermelody |
| Synthesis engine | karplus_strong (primary), phase_mod (secondary), additive (tertiary), modal 'string' (weak fallback) |

Identity: the high-gain rock/metal guitar — the HEAVIER sibling of
Overdriven Guitar (GM29). Same physical instrument (solidbody, humbuckers,
high-gain tube amp) driven harder: harder clipping (saturation 0.85 vs
0.60), more compression sustain (loop_gain 0.9992 vs 0.9990), darker
speaker roll-off (3.8 kHz vs 4.0 kHz), tighter palm-muted chug.

Why this pick: GM80 Lead 1 (square) was considered first, but the
voice_like **talkbox** member already claims program 80 / stem
`Lead_1_square` as its FluidSynth stand-in — a real registration there
would collide. GM30 has ZERO collisions and completes the Guitar family
(nylon 24, steel 25, jazz 26, clean 27, overdriven 29, distortion 30).

## Constants (Guitar/distortion_guitar/distortion_guitar.py)

```python
MIDI_PROGRAM = 30
GM_NAME = "Distortion Guitar"
STEM_LABEL = "Distortion_Guitar"
RANGE_MIN = 28
RANGE_MAX = 84
SOLO_RANGE = (45, 76)
SWEET_SPOT = (52, 72)
ZONES = {
    "low_strings": (28, 47),   # E1–B2 palm-muted chug roots
    "mid": (48, 64),           # C3–E4 power-chord pocket, riff centre
    "high": (65, 84),          # F4–C6 screaming leads, squeal territory
}
ARTICULATIONS = {
    "sustained_lead": (86, 1.0), "power_chord": (90, 0.40),
    "palm_mute": (58, 0.10), "open_chord": (78, 0.45),
    "staccato": (68, 0.12), "bend": (96, 1.30),
    "hammer_on": (80, 0.60), "pull_off": (70, 0.60),
    "slide": (74, 0.90), "vibrato": (82, 1.0),
    "harmonic": (93, 0.40), "grace": (72, 0.10),
    "accent": (100, 0.30), "feedback": (66, 1.50),
    "tremolo_pick": (84, 0.25),
}
SYNTHESIS = "karplus_strong"
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9992, "excitation": "pick", "width": 0.50,
    "lowpass_hz": 3800, "noise_component": 0.080, "saturation": 0.85,
}
MODAL_PRESET = "string"
FM_DEFAULTS = {
    "carrier_shape": "saw", "mod_freq_ratio": 1.0, "mod_depth": 4.5,
    "attack": 0.005, "release": 0.60,
}
ADDITIVE_DEFAULTS = {
    "harmonic_count": 9,
    "harmonic_weights": [0.9, 0.7, 0.85, 0.55, 0.75, 0.45, 0.55, 0.35, 0.3],
    "attack": 0.005, "release": 0.60,
}
REVERB_TAIL = 2.4
EQ_BODY = (400, -4.5)
EQ_PRESENCE = (2500, 3.0)
EQ_AIR = (5500, 0.5)
PAN = -0.15
```

## Registration proof

`instrument_registry.py` updated:
- `_INSTRUMENT_MODULES`: `"Guitar.distortion_guitar.distortion_guitar": "distortion_guitar"`
- Convenience constant: `DISTORTION_GUITAR = ALL_INSTRUMENTS["distortion_guitar"]`
- `registry_table()` role row added
- `__main__` verification block added

Registry verification run output (full `registry_table()` includes the new
row; verification lines):

```
| Guitar | Distortion Guitar | 30 | 28–84 | lead, melody, accent, rhythm, power-chord strum, countermelody |
=== Distortion Guitar (GM30) ===
  DISTORTION_GUITAR.midi_program = 30 (should be 30)
  by_name('distortion guitar') = <Instrument Distortion Guitar (family=Guitar, program=30, range=28-84)>
  by_name('DISTORTION GUITAR') = <Instrument Distortion Guitar (family=Guitar, program=30, range=28-84)>
  by_program(30) = <Instrument Distortion Guitar (family=Guitar, program=30, range=28-84)>
  DISTORTION_GUITAR.in_sweet_spot(64) = True
  DISTORTION_GUITAR.in_sweet_spot(24) = False
  DISTORTION_GUITAR.range_min = 28 DISTORTION_GUITAR.range_max = 84
  DISTORTION_GUITAR.stem_label = 'Distortion_Guitar'
```

## Verification results (verify_distortion_guitar.py — ALL CHECKS PASSED)

| Check | Result |
|---|---|
| Registry by_name / by_program | ✓ (both return the Distortion Guitar instrument) |
| Zero-drift (UnitMatrixComposer, 1 bar, SOLO voice) | **True (OK)** |
| MIDI export | `distortion_guitar_test.mid` — **93 bytes** (> 40 ✓) |
| WAV solo render (FluidSynth, `discover_soundfont()` → FluidR3_GM.sf2) | `distortion_guitar_test.wav` — **743,724 bytes** (> 40 ✓) |
| Spectral 4–8 kHz buzz | **1.6%** (gate 20% — no comb-filtering; clean single voice) |
| Stem label | `GM_PROGRAMS[30] = 'Distortion Guitar'`; STEM_LABEL `'Distortion_Guitar'` matches sanitized pipeline label ✓ |
| FluidR3 preset 30 phdr | `'Distortion Guitar'` — labels match exactly, **no quirk** |
| RenderPipeline stem render | `track00_Distortion_Guitar.wav` (743,724 bytes) ✓ |
| Karplus-Strong smoke | loop_gain 0.9992 → late(1–2 s) rms/peak **0.0069** vs 0.990 dull control **0.0013** = **5.4×** — hard-clip compression sustain confirmed |
| FluidR3 pitch sweep (28, 40, 52, 64, 76, 84) | 6/6 notes audible (rms 0.060–0.115), no gaps — SF2 never clips a composition |

## Quirks found

- **No stem-label quirk**: `GM_PROGRAMS[30] = "Distortion Guitar"` and
  FluidR3 preset 30 = "Distortion Guitar" — labels match exactly.
- **Collision avoided**: GM80 "Lead 1 (square)" was the first candidate but
  the voice_like **talkbox** member already claims program 80 / stem
  `Lead_1_square` as its FluidSynth MIDI-export stand-in — registering a
  real Lead 1 (square) there would collide on `by_program(80)` and on the
  stem filename. Picked GM30 instead (zero collisions).
- **Distortion dynamics quirk**: hard clipping compresses dynamic range to
  ~10 dB — write crescendos with note density, not velocity; velocities
  ≤ 50 trigger the clean/crunch sample layer, 60–100 the classic distortion
  tone, ≥ 110 the highest gain layer (sustain up, separation down).
- **Writing quirks**: single-note leads + root-fifth power chords are
  idiomatic; dense full-position chords intermodulate into a washy smear.
  Palm-muted 16th chugs (vel 55–70, short durations) are the metal rhythm
  engine. Low E (41 Hz) is weak on distortion (speaker roll-off) — keep
  lines above MIDI 40.
- **MidiInstrument enum**: GM30 NOT in `structures/instrument.py`
  (10-instrument enum) — use raw `program=30` in `add_voice`.

## Files

- `Guitar/distortion_guitar/instrument.md` — full research reference
- `Guitar/distortion_guitar/distortion_guitar.py` — importable constants
- `Guitar/distortion_guitar/verify_distortion_guitar.py` — verify script
- `Guitar/distortion_guitar/distortion_guitar_test.mid` (93 B)
- `Guitar/distortion_guitar/distortion_guitar_test.wav` (743,724 B)
- `Guitar/distortion_guitar/stems_distortion_guitar/track00_Distortion_Guitar.wav` (743,724 B)
- `instrument_registry.py` — registered (module, constant, table role row, verification)
- `registry.md` — changelog + table + stem-quirk entries updated
