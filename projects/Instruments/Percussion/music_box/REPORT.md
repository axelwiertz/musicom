# Music Box — Instrument Research Report

**Date**: 2026-09-29
**Author**: Nightly Instrument Research Job
**Instrument**: Music Box (GM10)

## Summary

| Attribute | Value |
|---|---|
| Family | Percussion |
| GM Program | 10 |
| GM Name | "Music Box" |
| Stem Label | Music_Box |
| Range | 60–96 (C4–C7, full mechanical movement compass) |
| Sweet Spot | 72–84 (C5–C6 — the classic tinkle octave) |
| Role | lead, melody, ornament, accent, color |
| Synthesis Engine | modal (ModalSynth) with stock 'bell' preset + custom MUSIC_BOX_MODES |
| Modal Preset | 'bell' (stock), custom bank for exact steel-tine partials |
| Reverb Tail | 1.5 s (intimate room — NOT cathedral) |
| Pan | 0.0 (center) |

## Constants (music_box.py)

```python
MIDI_PROGRAM = 10
GM_NAME = "Music Box"
STEM_LABEL = "Music_Box"
RANGE_MIN = 60        # C4
RANGE_MAX = 96        # C7
SOLO_RANGE = (60, 84)
SWEET_SPOT = (72, 84)

ZONES = {
    "low": (60, 71),     # C4–B4
    "mid": (72, 84),     # C5–C6
    "high": (85, 96),    # C#6–C7
}

ARTICULATIONS = {
    "pluck": (82, 1.0),
    "soft": (60, 1.0),
    "accent": (100, 0.9),
    "staccato": (70, 0.2),
    "roll": (74, 0.06),
}

SYNTHESIS = "modal"
MODAL_PRESET = "bell"

MUSIC_BOX_MODES = [
    (440.0, 1.00, 4.0),    # f0 fundamental
    (880.0, 0.50, 6.0),    # 2x octave
    (1320.0, 0.20, 9.0),   # 3x twelfth
    (1760.0, 0.08, 12.0),  # 4x double octave
]

KARPLUS_DEFAULTS = {
    "loop_gain": 0.9950,
    "width": 0.15,
    "role": "melody",
}

FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 2.0,
    "mod_depth": 1.2,
    "attack": 0.002,
    "release": 0.3,
}

REVERB_TAIL = 1.5
EQ_BODY = (500, -2.0)
EQ_PRESENCE = (4000, 2.0)
EQ_AIR = (8000, 1.5)
PAN = 0.0
```

### Synthetic mode rationale

The steel tine of a music box is a CANTILEVER (clamped at the comb block, free at the tip) — not a free-free beam like a glockenspiel bar. An ideal rectangular cantilever has mode ratios ~1 : 6.27 : 17.5 : 34.4, but the short, thick, tuned tine of a music box is deliberately designed to suppress inharmonicity. The near-harmonic 1:2:3:4 stack with fast decay rates (4.0–12.0) is the best approximation — much faster than tubular bells' 0.5–2.0, reflecting the steel tine's short ring (~0.3–1.2 s).

## Registration Proof

```
$ /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py

| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Percussion | Music Box | 10 | 60–96 | lead, harmony, accent |

Verification:
  MUSIC_BOX.midi_program = 10 (should be 10)
  by_name('music box') = <Instrument Music Box (family=Percussion, program=10, range=60-96)>
  by_program(10) = <Instrument Music Box (family=Percussion, program=10, range=60-96)>
  MUSIC_BOX.in_sweet_spot(74) = True
```

Registry entries added to `instrument_registry.py`:
- `_INSTRUMENT_MODULES["Percussion.music_box.music_box"] = "music_box"`
- `MUSIC_BOX = ALL_INSTRUMENTS["music_box"]` convenience constant
- Verification lines in `__main__` block

## Verification Results

### UnitMatrixComposer
- **Zero-drift**: True (OK) — MusicUnit ends flush at BAR=1920 with terminal landmark
- **MIDI size**: 120 bytes (> 40 ✓)

### FluidSynth SOLO Render (`discover_soundfont()` → FluidR3_GM.sf2)
- **WAV size**: 854,828 bytes (> 40 ✓)
- **Spectral buzz check**: 4–8 kHz buzz = 9.6% (OK — below 20% gate, no comb-filtering)
- **Render**: solo track only — no unison doubling, no comb-filtering artefacts

### Stem Label Check
- GM_PROGRAMS[10] = "Music Box" → stem file `trackXX_Music_Box.wav`
- STEM_LABEL = "Music_Box" matches the pipeline's sanitised label
- **No quirk**: pipeline label = FluidR3 preset name = GM_NAME — all agree

### SF2 Preset Check
- FluidR3_GM.sf2 preset 10 = "Music Box" (verified from phdr chunk)

### ModalSynth Smoke Test
- `ModalSynth.render_preset('bell', duration=0.5, excitation='impulse')`
- peak = 0.900, tail_rms/peak = 0.095 (fast decay — below 0.3 gate ✓)

## Quirks Found

### Stem-label quirks
- **None**: GM_PROGRAMS[10] = "Music Box" — matches exactly. Stem file: `trackXX_Music_Box.wav`.

### Identity quirks
1. **MONOPHONIC mechanical instrument**: a real music box physically cannot play two notes simultaneously — the cylinder has one pin per note at a given position. Composition jobs MUST write single-note melody lines, NOT chords. Two notes at MIDI pitch 72 + 76 on the same beat = physically impossible on a real movement.
2. **No velocity dynamics**: the pin always plucks at fixed displacement (the spring-wound motor drives it at constant force). Velocity mapping (60–108) is a creative affordance for composition dynamics, not a physical reality on the instrument.
3. **Fixed tempo**: the governor-regulated spring escapement means tempo is locked to the movement's designed speed. A music box cannot speed up or slow down — the MIDI tempo should be fixed.
4. **Real range varies by movement size**: 18-note toy movements = C5–A6 (72–93). 30/50/72-note movements = C4–C7 (60–96). The large Reuge/Sankyo 72-note movements are chromatic throughout; 18-note boxes play a single diatonic tune.

### Channel quirk
- Must use a melodic channel (0–9) with program 10 — channel 9 triggers the drum-kit map and `Acoustic_Grand_Piano` program-0 fallback label (standard percussion channel pitfall).

## RenderPipeline GM_PROGRAMS Quirks Table

| Program | Pipeline Label | Quirk |
|---|---|---|
| 10 | Music Box | **No quirk** ✓ (pipeline + FluidR3 + our entry all agree) |

## Files Created

| File | Path |
|---|---|
| `instrument.md` | `Percussion/music_box/instrument.md` |
| Constants | `Percussion/music_box/music_box.py` |
| Report | `Percussion/music_box/REPORT.md` |
| Verify script | `_test/verify_music_box.py` |
| MIDI output | `_test/music_box_test.mid` |
| WAV output | `_test/music_box_test.wav` |

## Registry Updated

- `instrument_registry.py` — module path, convenience constant, verification lines
- `registry.md` — "Music Box added (2026-09-29)" changelog + quirks table entry