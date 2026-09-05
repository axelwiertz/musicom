# Kalimba — Instrument Research Report (2026-09-05)

## Instrument

- **Name**: Kalimba (thumb piano, mbira family lamellophone)
- **Family**: World (fourth entry — after sitar, koto, shamisen)
- **GM program**: 108 (GM2 Kalimba) — melodic channel (0-9), NOT channel 9
- **Synthesis engine**: Karplus-Strong (`sound/synthesis/karplus_strong.py`, SP-011),
  fallback ModalSynth `preset('bell')` (inharmonic metal-bar modes)

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full | 48–96 | C3–C7 (extended/treble kalimbas; 17-note core C4–E6) |
| Sweet spot | 62–81 | D4–A6 |
| Low | 48–59 | C3–B3 (extended bass tines, dark box ring) |
| Mid | 60–76 | C4–E6 (classic 17-note body, lead register) |
| High | 77–96 | F6–C7 (bright, plinky, fast decay) |

## Role

- Lead melody, ornament, drone/pulse, harmony (2–4 note chords OK)
- NOT bass, NOT rhythm-section groove

## Constants (kalimba.py)

```python
MIDI_PROGRAM = 108
GM_NAME = "Kalimba"
STEM_LABEL = "Kalimba"
RANGE_MIN = 48
RANGE_MAX = 96
SOLO_RANGE = (60, 84)
SWEET_SPOT = (62, 81)
ZONES = {"low": (48, 59), "mid": (60, 76), "high": (77, 96)}
ARTICULATIONS = {
    "pluck": (76, 1.0), "roll": (66, 0.07), "double": (72, 0.3),
    "damped": (48, 0.12), "accent": (94, 0.9),
}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9940, "width": 0.40, "role": "lead"}
MODAL_PRESET = "bell"
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 3.7,
               "mod_depth": 2.5, "attack": 0.002, "release": 0.5}
REVERB_TAIL = 1.8
EQ_BODY = (450, -2.0)
EQ_PRESENCE = (3500, 2.5)
EQ_AIR = (8000, 1.5)
PAN = 0.0
```

## Registration proof

`instrument_registry.py` updated: `"World.kalimba.kalimba": "kalimba"` in
`_INSTRUMENT_MODULES`, `KALIMBA = ALL_INSTRUMENTS["kalimba"]` constant,
role row in `registry_table()` + `__main__` verification lines.

Registry run (`python instrument_registry.py`) — new row + lookups:

```
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
  KALIMBA.midi_program = 108 (should be 108)
  by_name('kalimba') = <Instrument Kalimba (family=World, program=108, range=48-96)>
  by_program(108) = <Instrument Kalimba (family=World, program=108, range=48-96)>
  KALIMBA.in_sweet_spot(69) = True
```

`verify_kalimba.py` registry-backed import: `ALL_INSTRUMENTS count = 22`
(21 → 22 with kalimba).

## Verification results (verify_kalimba.py — ALL CHECKS PASSED)

- **Zero-drift**: `True (OK)` — UnitMatrixComposer, 1 bar, 1 section,
  Kalimba solo melody (ch0) + ONE low bass C3 context note (ch1, GM33,
  octave below — no unison doubling)
- **MIDI**: `kalimba_test.mid` — 135 bytes (> 40 ✓)
- **WAV (solo render)**: `kalimba_test.wav` — 1,295,148 bytes (> 40 ✓)
  - Rendered via `discover_soundfont()` → **FluidR3_GM.sf2** (141MB proper set)
  - `render_midi(midi_path, wav, solo=0)` — Kalimba track ONLY (no
    clarinet/piano doubling — no comb-filtering)
  - Spectral check: **4–8 kHz buzz energy = 4.3% (OK)** — no buzz
- **Stem label**: `GM_PROGRAMS[108] = 'Kalimba'` → `track00_Kalimba.wav`
  on disk (matches exactly, no quirk)
- **SF2 preset**: FluidR3 preset 108 = `'Kalimba'` (phdr chunk verified)
- **Karplus-Strong smoke test** (loop_gain 0.9940):
  - tail_rms/peak (0.2–0.6 s) = **0.014** vs dull 0.990 control **0.008** → 1.7× ring advantage
  - vs sitar (0.9975) tail **0.023** → kalimba decays faster (metal tine vs
    sympathetic strings) ✓ physics

## Quirks found

1. **Measurement window matters for short-ring instruments**: sitar/koto
   verify scripts measure ring in the 1–2 s window. Kalimba's metal-tine
   ring is gone by then — both the instrument and the dull control sit at
   the noise floor (0.002), so a `>0.01` threshold failed. Use the
   **0.2–0.6 s window** (0.014 vs 0.008, clean 1.7× separation).
2. **loop_gain sensitivity**: the Karplus lowpass is aggressive; 0.9940 is
   the empirical sweet spot (probe: 0.993 → 1.5×, 0.994 → 1.7×, 0.995 → 2.0×,
   0.996 → 2.3×, 0.997 → 2.6× vs control). Above ~0.996 the kalimba starts
   sounding like a sitar — keep 0.9940 for the metal-tine character.
3. **Stem labels / SF2**: NO quirk for GM108 — pipeline label "Kalimba",
   FluidR3 preset "Kalimba", file `track00_Kalimba.wav` all match exactly.
4. **World family convention**: kalimba is a line/ostinato voice, not a
   dense-harmony voice — composition jobs write melodic lines and
   interlocking thumb patterns (mbira style), not thick chords.
5. **Context bass note**: the verify uses GM33 (Electric Bass finger) at C3 —
   a full octave below the lowest kalimba note, so no unison doubling.

## Files

- `/opt/data/projects/Instruments/World/kalimba/instrument.md`
- `/opt/data/projects/Instruments/World/kalimba/kalimba.py`
- `/opt/data/projects/Instruments/World/kalimba/REPORT.md` (this file)
- `/opt/data/projects/Instruments/_test/verify_kalimba.py`
- `/opt/data/projects/Instruments/_test/kalimba_test.mid` (135 B)
- `/opt/data/projects/Instruments/_test/kalimba_test.wav` (1.3 MB)
- `/opt/data/projects/Instruments/_test/stems_kalimba/track00_Kalimba.wav` + `track01_Electric_Bass_finger.wav`
- `/opt/data/projects/Instruments/instrument_registry.py` (registered)
- `/opt/data/projects/Instruments/registry.md` (changelog + table + quirks)
