# REPORT — Harpsichord (GM6, Keys family) — 2026-09-17

## Summary

| Item | Value |
|---|---|
| Instrument | Harpsichord (quill-plucked Baroque keyboard) |
| Family | Keys (4th entry: piano, organ, dulcimer, **harpsichord**) |
| MIDI program | **6** (0-based GM1 "Harpsichord"; NOT in the 10-member `MidiInstrument` enum — use raw `program=6`) |
| Range | 29–89 (F1–F6, modern 61-note concert double-manual compass; historic Ruckers/Taskin 36–84) |
| Sweet spot | 48–84 (C3–C6, 8' principal register) |
| Role | harmony, continuo, melody, ornament, countermelody, accent |
| Synthesis | Karplus-Strong primary (`loop_gain` 0.9980); ModalSynth 'string' fallback + custom `HARPSICHORD_MODES`; PhaseModSynth cheap alt |
| Stem label | `trackXX_Harpsichord.wav` — GM_PROGRAMS[6] = "Harpsichord" = FluidR3 preset 6, **no quirk** |
| Files | `Keys/harpsichord/instrument.md`, `Keys/harpsichord/harpsichord.py`, `_test/verify_harpsichord.py` |
| Registry | `instrument_registry.py`: `"Keys.harpsichord.harpsichord": "harpsichord"` + `HARPSICHORD = ALL_INSTRUMENTS["harpsichord"]` + role mapping + `__main__` verification block |

## Why harpsichord

World family was complete (sitar/koto/shamisen/kalimba/banjo/fiddle/shenai/
taiko). GM6 was an unused classic slot in the Keys family — and the
harpsichord is the ONLY plucked member of the Keys family, which fits the
KB's Karplus-Strong lineage perfectly (plucked waveguide = exact physical
model). Distinct identity lesson: **no touch dynamics** (fixed quill
displacement), the inverse of the piano lesson.

## Constants (harpsichord.py)

```python
MIDI_PROGRAM = 6
GM_NAME = "Harpsichord"
STEM_LABEL = "Harpsichord"
RANGE_MIN, RANGE_MAX = 29, 89        # F1–F6
SOLO_RANGE = (29, 89)
SWEET_SPOT = (48, 84)                # C3–C6
ZONES = {"low": (29, 47), "mid": (48, 71), "high": (72, 89)}
ARTICULATIONS = {
    "pluck_8ft": (88, 1.0), "full_choir": (96, 1.2), "octave_4ft": (78, 0.9),
    "lute_buff": (70, 0.55), "arpeggio_broken": (74, 0.9),
    "trill": (82, 0.5), "mordent": (86, 0.3), "etouffer": (52, 0.15),
}
SYNTHESIS = "karplus"
MODAL_PRESET = "string"
KARPLUS_DEFAULTS = {"loop_gain": 0.9980, "width": 0.5, "role": "lead"}
HARPSICHORD_MODES = [   # 8' + 4' registration — octave DOUBLED (4' choir)
    (440.0, 1.00, 0.35), (880.0, 0.45, 0.50), (880.0, 0.55, 0.35),
    (1320.0, 0.22, 0.70), (1760.0, 0.25, 0.50), (2640.0, 0.10, 0.90),
]
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 2.0,
               "mod_depth": 2.2, "attack": 0.002, "release": 1.4}
REVERB_TAIL = 1.8     # chamber/baroque hall — shorter than harp 2.4
EQ_BODY = (300, -2.0); EQ_PRESENCE = (3500, 2.0); EQ_AIR = (9500, 1.5)
PAN = 0.0             # center solo; right-of-center continuo seat
def midi_to_freq(m): return 440.0 * 2.0 ** ((m - 69) / 12.0)
```

## Registration proof (instrument_registry.py)

Run: `cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`

New row in `registry_table()` (ALL_INSTRUMENTS count = 42):

```
| Keys | Harpsichord | 6 | 29–89 | harmony, continuo, melody, ornament, countermelody, accent |
```

Verification lines:

```
HARPSICHORD.midi_program = 6 (should be 6)
by_name('harpsichord') = <Instrument Harpsichord (family=Keys, program=6, range=29-89)>
by_program(6) = <Instrument Harpsichord (family=Keys, program=6, range=29-89)>
HARPSICHORD.in_sweet_spot(69) = True
```

## Verification results (_test/verify_harpsichord.py — ALL CHECKS PASSED)

- **Registry import**: `by_name('harpsichord')` → program 6 ✓ (proves registration)
- **Zero-drift**: `validate()` → `True (OK)` — 2 voices (Harpsichord solo ch0 +
  low bass D2 ch1 GM33 context, NOT a melodic doubling), terminal landmark flush at BAR
- **MIDI**: `_test/harpsichord_test.mid` — 144 bytes (>40 ✓)
- **WAV solo render** via `discover_soundfont()` → FluidR3_GM.sf2:
  `_test/harpsichord_test.wav` — 761,132 bytes (>40 ✓)
- **Spectral gate**: 4–8 kHz buzz 9.1% (OK, ≤20%; no comb-filtering — solo render)
- **Stem labels**: GM_PROGRAMS[4..8] = 'Electric Piano 1', 'Electric Piano 2',
  **'Harpsichord'**, 'Clavi', 'Celesta'; RenderPipeline stem render produced
  `track00_Harpsichord.wav` (761,132 B) + `track01_Electric_Bass_finger.wav`
- **SF2 preset**: FluidR3_GM.sf2 phdr → preset 6 = "Harpsichord" (exact match)
- **FluidR3 pitch sweep** (notes 29–89, 10 samples): rms 0.017–0.035,
  **audible 10/10, no gaps** — bottom F1 0.0347, top F6 0.0175 (no harp-style
  treble cliff)
- **Karplus-Strong ring ordering** (1–2 s tail rms/peak, loop_gain):
  harp 0.9985 → 0.0083 > **harpsichord 0.9980 → 0.0063** > sitar 0.9975 →
  0.0050 > dull control 0.990 → 0.0013 ✓ (exactly the placed slot)
- **KS partial signature**: 2nd partial **107.8% of f0** (loudest partial —
  the 4' octave double; unique in the KB), 3rd 86.0% — stack decays upward ✓
- **ModalSynth HARPSICHORD_MODES**: late(1.0–1.5 s) rms/peak **0.345** vs
  marimba preset 0.0001; octave-band amplitude 1.00 vs fundamental 1.00
  (4' choir doubling modeled at 0.55+0.45)

## Quirks found

1. **No touch dynamics** — quill plucks at fixed displacement; velocity
   changes pluck noise/brightness, not loudness. Composition jobs: keep
   velocities in the 84–100 band; phrase with registration (density,
   octave doubling, choir choice) + ornaments. Trills/mordents are the
   sustain mechanism on fast-dying plucked strings.
2. **4' octave double** is the timbre signature — the 2nd partial is the
   loudest (measured 107.8% of f0 in the KS render). FluidR3 preset 6 is a
   single-choir patch; to fake the 4' choir in MIDI, double the melody an
   octave up at ~half velocity — or use `HARPSICHORD_MODES` in ModalSynth.
3. **Clean releases** (cloth dampers) — unlike the harp (no dampers),
   releasing the key stops the string instantly; KS loop_gain 0.9980
   models ring-while-held between harp 0.9985 and sitar 0.9975.
4. Stem label `trackXX_Harpsichord.wav` — exact match, no quirk
   (contrast Flute→"Recorder", Bagpipe→"Bag_pipe").
5. Channel quirk (general): melodic channel (0–9) with program 6 — ch9
   would trigger the drum-kit map and the `Acoustic_Grand_Piano`
   program-0 fallback label.

## Registry discipline checklist

- [x] `_INSTRUMENT_MODULES` entry `"Keys.harpsichord.harpsichord": "harpsichord"`
- [x] Convenience constant `HARPSICHORD`
- [x] `registry_table()` role mapping branch
- [x] `__main__` verification lines (HARPSICHORD block)
- [x] Registry verification run prints the new row + by_name/by_program proof
- [x] `registry.md`: changelog entry + Registry table row + stem-quirk table row
- [x] `_FIELDS` needed no extension (no new field type introduced)
