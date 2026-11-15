# REPORT — Woodblock (Percussion, GM115)

Nightly instrument research job · 2026-09-02 slot (written 2026-11-15)
Paths: `/opt/data/projects/Instruments/Percussion/woodblock/{instrument.md, woodblock.py, REPORT.md}`

| Field | Value |
|---|---|
| Instrument | **Woodblock** (hardwood slit block, orchestral/studio) |
| Family | Percussion (9th entry) |
| MIDI program | **115** (GM1 "Woodblock", 0-based) |
| Channel | melodic 0–9 (NOT ch9; ch9 = Hi 76 / Low 77 alternative) |
| Range | 60–96 (C4–C7) — a *window*, not a scale |
| Solo range | 65–84 (F4–C6), home/ostinato note **72** (C5) |
| Sweet spot | 67–74 — the patch's natural, unresampled centre (natural note ≈68, 410 Hz) |
| Role | rhythm, accent, ornament, color |
| Synthesis | **ModalSynth** (`WOODBLOCK_MODES`), PhaseMod alternative |
| Stem label | `trackXX_Woodblock.wav` (`GM_PROGRAMS[115] = "Woodblock"`) — no quirk |
| SF2 preset | FluidR3_GM.sf2 bank 0 / program 115 = **"Woodblock"** (phdr verified) |
| Registry key / constant | `woodblock` / `WOODBLOCK` (`Percussion.woodblock.woodblock`) |

## 1. Why this instrument

The registry covers 88 of the 128 GM programs. The percussion tail (112–119)
held the obvious next gaps: Tinkle Bell 112, Steel Drums 114 (taken), Woodblock
115, Taiko 116 (taken), Melodic Tom 117, Synth Drum 118. **GM115 Woodblock** is
the one with real acoustic identity, a genuine performance practice, and a
unique niche in the KB: it is the only *wooden, unpitched, ultra-short* voice.
The KB already documents Agogo (GM113) as "bright metal timeline"; the agogo
entry itself names 115 Woodblock as "its dry wooden counterpart" — a documented
hole in the family.

## 2. Constants (`woodblock.py`)

```python
MIDI_PROGRAM = 115
GM_NAME = "Woodblock"
STEM_LABEL = "Woodblock"

RANGE_MIN = 60          # C4
RANGE_MAX = 96          # C7
SOLO_RANGE = (65, 84)   # F4–C6
SWEET_SPOT = (67, 74)   # natural, unresampled centre

ZONES = {"low": (60, 70), "mid": (71, 79), "high": (80, 96)}   # timbre zones

ARTICULATIONS = {                       # (velocity, duration_factor)
    "open": (92, 0.25), "accent": (106, 0.30), "muted": (68, 0.12),
    "rim": (86, 0.10), "stick_click": (60, 0.08), "double": (90, 0.18),
    "ghost": (36, 0.10), "roll": (60, 0.06),
}

SYNTHESIS = "modal"
MODAL_PRESET = "drum"                   # closest stock bank, membrane-shaped
WOODBLOCK_MODES = [                     # (freq, amp, decay-rate)
    (430.0, 1.00, 80.0),   # 1.00x block body (measured 430 Hz)
    (843.0, 0.48, 110.0),  # 1.96x near-octave "tock"
    (937.0, 0.30, 140.0),  # 2.18x INHARMONIC wooden clack
    (1480.0, 0.16, 190.0), # 3.44x slit/edge crack
    (2365.0, 0.10, 260.0), # 5.50x hard-stick tick
]
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 3.4,
               "mod_depth": 1.8, "attack": 0.0005, "release": 0.06}
CH9_WOODBLOCK = {"hi": 76, "low": 77, "peak_at_vel_100": 0.55}

REVERB_TAIL = 0.75
EQ_BODY = (600, -2.0)
EQ_PRESENCE = (3600, 2.5)
EQ_AIR = (10000, 1.5)
PAN = 0.15

def midi_to_freq(midi): return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

YAML frontmatter in `instrument.md`:
`type: instrument`, `family: Percussion`, `name: Woodblock`, `midi_program: 115`,
`gms: "Woodblock"`, `range_min: 60`, `range_max: 96`, `solo_range: [65, 84]`,
`role: [rhythm, accent, ornament, color]`, `synthesis: [modal, phase_mod]`.

## 3. Empirical research (all numbers measured, FluidR3_GM.sf2)

### 3.1 Pitch sweep, GM115, vel 100 — the pitch-tracking quirk

| MIDI | expected f | measured peak | ratio |
|---|---|---|---|
| 50 | 146.8 | 330 | 2.25 |
| 56 | 207.7 | 360 | 1.73 |
| 62 | 293.7 | 380 | 1.29 |
| 68 | 415.3 | 410 | 0.99 |
| 72 | 523.3 | 430 | 0.82 |
| 78 | 740.0 | 460 | 0.62 |
| 84 | 1046.5 | 500 | 0.48 |
| 90 | 1480.0 | 530 | 0.36 |
| 96 | 2093.0 | 570 | 0.27 |
| 98 | 2349.3 | 580 | 0.25 |

**FluidR3 GM115 moves its spectral peak only 330 → 580 Hz across 48 semitones
(1.76×) where true transposition would be 16×.** The patch is one woodblock
sample spread over the keyboard with ~10 Hz/octave of tracking. Note number is
a *timbre* control, not a pitch control; the native pitch is note ≈68 (G#4,
410 Hz). Consequence: no melodies, no bass lines, and no hi/lo pair from GM115.

Level is flat: peak 0.34 (note 48) → 0.32 (note 96), RMS 0.0075 → 0.0057
(−2.4 dB across four octaves). Nothing must be avoided dynamically.

### 3.2 Decay (note 72, vel 100)

| time | RMS | % of peak |
|---|---|---|
| 0.00 s | 0.0867 | 25.6 % |
| 0.05 s | 0.0083 | 2.5 % |
| 0.10 s | 0.0104 | 3.1 % |
| 0.20 s | 0.0061 | 1.8 % |
| 0.40 s | 0.0033 | 1.0 % |
| 0.80 s | 0.0012 | 0.4 % |
| 1.60 s | 0.0002 | 0.1 % |

−90 % inside **50 ms**; the residual to ~1.5 s is patch room tone, not block
resonance. Hence all articulation durations are short — note-off length is
inaudible and articulation is velocity/stroke only.

### 3.3 Velocity response (note 72)

| vel | RMS | peak | centroid |
|---|---|---|---|
| 20 | 0.0003 | 0.014 | 5142 Hz |
| 40 | 0.0010 | 0.054 | 5055 Hz |
| 60 | 0.0024 | 0.123 | 5046 Hz |
| 80 | 0.0042 | 0.219 | 5044 Hz |
| 100 | 0.0065 | 0.339 | 5044 Hz |
| 120 | 0.0094 | 0.490 | 5044 Hz |

Near-linear over ~35× peak range, centroid constant → velocity is pure
loudness, no timbre shift. Ghost notes work down to vel 20; nothing is gained
above 110.

### 3.4 Partials (note 72, first 120 ms, relative to 433 Hz peak)

367 Hz (0.27), 383 Hz (0.67), **433 Hz (1.00)**, **850 Hz (0.44 = 1.96×)**,
**942 Hz (0.53 = 2.18×)**, 2392 Hz (0.14 = 5.5×). These MEASURED ratios (not
textbook bar modes) are what `WOODBLOCK_MODES` encodes.

### 3.5 Brightness context (note 72, first 120 ms centroid)

| patch | centroid |
|---|---|
| Marimba (12) | 3034 Hz |
| Xylophone (13) | 3416 Hz |
| **Woodblock (115)** | **4704 Hz** |
| Steel Drums (114) | 5297 Hz |
| Agogo (113) | 7393 Hz |

### 3.6 Channel-9 GM woodblocks (the hi/lo workaround)

| ch9 note | name | f0 | peak @vel100 | centroid |
|---|---|---|---|---|
| 76 | Hi Wood Block | 380 Hz | 0.549 | 4448 Hz |
| 77 | Low Wood Block | 280 Hz | 0.526 | 3733 Hz |
| 75 | Claves | 1080 Hz | 0.550 | 4200 Hz |
| 37 | Side Stick | 600 Hz | 0.356 | 5210 Hz |

The ch9 pair is only a fifth apart and the "Hi" block is low-ish in FluidR3;
ch9 hits are **+4.5 dB hotter** than melodic GM115 at the same velocity.

### 3.7 ModalSynth calibration (`WOODBLOCK_MODES`)

Decay-rate scaling test (mode bank × 1/2/4/6/8/12) established the rate scale:
rate 100 → 66 ms visible length, rate 50 → 132 ms. Rates 80/110/140/190/260 were
chosen to land between the FluidR3 decay (2.5 % at 50 ms) and the marimba bank
(8–20 = ~1 s).

Rendered check (`render_custom`, sr 22050, 0.5 s, impulse):
`peak=0.900 head_rms=0.2769 mid_rms(30–60 ms)=0.0184 late_rms(250–500 ms)=0.0000`
→ `mid/head = 6.6 %`, `late/peak = 0.00000`. Partials vs f0:
1.96× = 35.9 %, 2.18× = 19.8 %, 3.44× = 7.2 %, 5.50× = 3.2 % — the wooden
2.18× clack is present and dominant enough to read as WOOD, not a bar.

## 4. Registration (registry discipline)

`instrument_registry.py` edits:
1. `_INSTRUMENT_MODULES`: `"Percussion.woodblock.woodblock": "woodblock"`
2. `_FIELDS`: added `"woodblock_modes"` (so the mode bank is exposed on the
   `Instrument` object, like `agogo_modes` / `xylophone_modes`)
3. `registry_table()` role branch: `elif low == "woodblock": role = "rhythm,
   accent, ornament, color"`
4. Convenience constant: `WOODBLOCK = ALL_INSTRUMENTS["woodblock"]`
5. `__main__` verification block: `=== Woodblock (Percussion, GM115) ===`

### 4.1 Verification run — `python instrument_registry.py`

```
=== Woodblock (Percussion, GM115) ===
  WOODBLOCK.midi_program = 115 (should be 115)
  by_name('woodblock') = <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
  by_name('Woodblock') = <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
  by_program(115) = <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
  by_program(114) = <Instrument Steel Drums (family=Percussion, program=114, range=55-96)> (distinct: steel drums)
  WOODBLOCK.in_sweet_spot(72) = True
  WOODBLOCK.in_sweet_spot(48) = False
  WOODBLOCK.range_min = 60 WOODBLOCK.range_max = 96
  WOODBLOCK.stem_label = 'Woodblock'
  WOODBLOCK.synthesis = 'modal'
  WOODBLOCK.reverb_tail = 0.75 WOODBLOCK.pan = 0.15
  WOODBLOCK.woodblock_modes = [(430.0, 1.0, 80.0), (843.0, 0.48, 110.0), (937.0, 0.3, 140.0), (1480.0, 0.16, 190.0), (2365.0, 0.1, 260.0)]
```

`registry_table()` row (present in the printed 96-row table, Percussion group):

```
| Percussion | Woodblock | 115 | 60–96 | rhythm, accent, ornament, color |
```

Exit code 0. Full captured output: `_test/registry_out_woodblock.txt`.

## 5. End-to-end verification (`_test/verify_woodblock.py`)

Structure from `verify_marimba.py`/`verify_agogo.py` with the 2026-09-01 fixes:
constants imported **through the registry**, audio rendered **SOLO**, soundfont
via `discover_soundfont()`.

Composition: bpm 104, 1 bar, 2 voices — voice 1 = Woodblock SOLO part (16
strokes, all on note 72: accents 106, ghosts 36, doubles, a 2-stroke pickup);
voice 2 = drum-kit context (kick 36 + hat 42, ch9) — no second melodic patch,
no unison doubling.

```
registry: by_name('woodblock') -> <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
registry: by_name('Woodblock') -> <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
registry: by_program(115) -> <Instrument Woodblock (family=Percussion, program=115, range=60-96)>
registry: WOODBLOCK is ALL_INSTRUMENTS['woodblock'] -> True
registry: family=Percussion program=115 range=60-96 solo=(65, 84) sweet=(67, 74)
registry: stem_label='Woodblock' reverb=0.75 pan=0.15
registry: synthesis=modal modal_preset=drum
registry: woodblock_modes=[(430.0, 1.0, 80.0), (843.0, 0.48, 110.0), (937.0, 0.3, 140.0), (1480.0, 0.16, 190.0), (2365.0, 0.1, 260.0)]
registry: in_sweet_spot(72)=True in_sweet_spot(48)=False in_range(60)=True
Woodblock: program=115 gm='Woodblock' stem='Woodblock' sweet=(65, 84) A4=440.0Hz
Woodblock: zones={'low': (60, 70), 'mid': (71, 79), 'high': (80, 96)}
Woodblock: art=['open', 'accent', 'muted', 'rim', 'stick_click', 'double', 'ghost', 'roll'] synth=modal modal_preset=drum reverb=0.75s pan=0.15
Woodblock: C5=523.3Hz C6=1046.5Hz

Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/woodblock_test.mid (263 bytes)
WAV (solo): /opt/data/projects/Instruments/_test/woodblock_test.wav (794412 bytes)
Spectral check: 4-8kHz buzz energy = 7.6% (OK)

Stem labels (pipeline GM_PROGRAMS, 0-indexed):
  [113] = 'Agogo'
  [114] = 'Steel Drums'
  [115] = 'Woodblock'
  [116] = 'Taiko Drum'
  Woodblock -> 'Woodblock'
SF2: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
SF2 preset 115 -> 'Woodblock'

Stems rendered (2 files):
  track00_Woodblock.wav (794412 bytes)
  track01_Drums.wav (835628 bytes)

ModalSynth WOODBLOCK_MODES: peak=0.900 head_rms=0.2769 mid_rms=0.0184 late_rms=0.0000 late/peak=0.00000
  partials vs f0 (430 Hz):
    1.96x (   843 Hz) =  35.9% of f0
    2.18x (   937 Hz) =  19.8% of f0
    3.44x (  1480 Hz) =   7.2% of f0
    5.50x (  2365 Hz) =   3.2% of f0

ALL CHECKS PASSED
```

Artifact sizes: MIDI **263 B** (>40 ✓), solo WAV **794,412 B** (>40 ✓), stems
794,412 B / 835,628 B. Zero-drift ✓. Spectral buzz in the 4–8 kHz band **7.6 %**
(limit 20 %) — high because the instrument's tick band *is* 4–8 kHz, and there
is no second patch to beat against.

## 6. Quirks found (summary)

1. **GM115 barely pitch-tracks** (measured): 330 → 580 Hz over notes 50–98.
   Note number = timbre. Native note ≈68. Never write melodies on it.
2. **No hi/lo pair from GM115.** Use ch9 note 76 (Hi, 380 Hz) / 77 (Low,
   280 Hz); only a fifth apart, and ch9 is +4.5 dB hotter than the melodic
   patch, plus it loses the `Woodblock` stem label (falls back to
   `Acoustic_Grand_Piano`, the ch9 program-0 quirk).
3. **Durations are meaningless past ~1/16** — the block is over in 50 ms.
   Articulation = velocity + stroke, never note length.
4. **Reverb must stay short** (0.75 s, the KB's driest): longer tails turn the
   tick into a wood "clop" and destroy its marker function.
5. **GM112 naming mismatch** spotted while probing the tail: FluidR3 preset 112
   is spelled **"Tinker Bell"**, RenderPipeline `GM_PROGRAMS[112]` says
   **"Tinkle Bell"** — cosmetic only (stem labels come from the pipeline list),
   but a future Tinkle Bell entry must expect the SF2 spelling.
6. **Claves trap**: claves are ch9 note 75 (1080 Hz), *not* GM115. Writing
   claves on GM115 gives a block, not a rod.

## 7. Reproduction

```bash
cd /opt/data/projects/Instruments
$MUSICOM_PYTHON instrument_registry.py                 # prints table + Woodblock checks
$MUSICOM_PYTHON _test/verify_woodblock.py              # zero-drift, MIDI, solo WAV, stems, modal
$MUSICOM_PYTHON _test/_probe_woodblock.py              # sweep / decay / velocity
$MUSICOM_PYTHON _test/_probe_wb_zones.py               # pitch-tracking map
$MUSICOM_PYTHON _test/_probe_wb_context.py             # centroid + ch9 pair
$MUSICOM_PYTHON _test/_calib_woodblock_modes.py        # modal decay-rate calibration
```

## 8. KB updates

- `registry.md` — Registry table row added (Percussion group, after Xylophone);
  changelog entry "Woodblock added (2026-09-02 nightly slot, written
  2026-11-15)" appended with full constants, quirk and registration proof.
- `instrument_registry.py` — module map, `_FIELDS`, role branch, `WOODBLOCK`
  constant, `__main__` verification block.
- Registry now loads **89 distinct programs** (was 88).

Sibling GM candidates still open: 112 Tinkle Bell, 117 Melodic Tom, 118 Synth
Drum, 76 Blown Bottle, 17/18 Percussive/Rock Organ, 50/51 Synth Strings 1/2,
63 Synth Brass 2, 37 Slap Bass 2.
