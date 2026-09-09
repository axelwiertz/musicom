# REPORT — Steel Drums (GM114) added 2026-09-09

## Instrument

- **Name**: Steel Drums (Trinidadian steelpan / pan — lead/tenor pan character)
- **Family**: Percussion (melodic) — third entry after Drum Kit, Marimba
- **MIDI program**: 114 (GM1 "Steel Drums", bank 0)
- **GM name**: "Steel Drums" (matches GM spec, pipeline, and SoundFont)
- **Stem label**: `trackXX_Steel_Drums.wav` (GM_PROGRAMS[114] = "Steel Drums"
  — matches exactly, **no quirk**)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | lead-pan practical register (some extend to E7=100) |
| Sweet spot | 65–86 | F4–D6 | brightest, roundest tone, best projection |
| Solo range | 62–88 | D4–E6 | solo repertoire focus (lead pan) |
| Low | 55–64 | G3–E4 | dark, warm, calypso bass-note/strum zone |
| Mid | 65–76 | F4–E5 | bright round melody zone — lead pan core |
| High | 77–96 | F5–C7 | pingy, cutting, fast decay (double-tenor top) |

Empirical FluidR3 pitch sweep (RMS, notes 24–96): preset 114 audible across
the WHOLE span (24–96, 73/73 notes, no gaps). Range 55–96 is the lead-pan
register; the sweep proves the patch plays the full GM span (bagpipe
precedent: GM-patch span kept, real-register documented).

## Role

- Lead melody, accent/ornament, countermelody, harmony (2–4 note chords
  idiomatic — calypso strums/rolled chords), rhythm (chank patterns)
- NOT a bass voice (bass pans are a separate low sub-family; GM114 patch is
  bright/small); NOT a pad (no sustain — rolls substitute)

## Synthesis engine (musicom)

- **Primary**: ModalSynth (`sound/synthesis/modal.py`) — impulse-excited
  struck-membrane resonator bank. Exact-pan custom modes in `PAN_MODES`:
  f0, 2.0×, 2.7×, 3.6× at decays 12–28 (the 2.7× "pan fifth" is the
  signature overtone). Closest stock preset: `'marimba'` (MODAL_PRESET);
  metallic alt: `'bell'`. Pitch-shift mode frequencies by played note.
- **Fallback**: Karplus-Strong (`sound/synthesis/karplus_strong.py`, SP-011),
  loop_gain 0.9950 — bright metallic ping, between kalimba (0.9940) and
  banjo (0.9960).
- **Alt**: PhaseModSynth cheap patch (sine carrier, mod ratio 2.7).
- **Avoid**: BowedString (no sustain, no bow).

## Constants (steel_drums.py)

```python
MIDI_PROGRAM = 114
GM_NAME = "Steel Drums"
STEM_LABEL = "Steel Drums"
RANGE_MIN = 55; RANGE_MAX = 96
SOLO_RANGE = (62, 88); SWEET_SPOT = (65, 86)
ZONES = {"low": (55,64), "mid": (65,76), "high": (77,96)}
ARTICULATIONS = {"strike": (82,1.0), "roll": (70,0.08), "staccato": (66,0.18),
                 "accent": (96,0.9), "muted": (48,0.12)}
SYNTHESIS = "modal"; MODAL_PRESET = "marimba"
PAN_MODES = [(440,1.0,12), (880,0.55,14), (1188,0.35,17), (1584,0.20,22), (2200,0.10,28)]
KARPLUS_DEFAULTS = {"loop_gain": 0.9950, "width": 0.35, "role": "lead"}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 2.7, "mod_depth": 3.0,
               "attack": 0.001, "release": 0.25}
REVERB_TAIL = 1.4
EQ_BODY = (500, -2.0); EQ_PRESENCE = (3500, 2.5); EQ_AIR = (9000, 1.0)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## Registration proof (registry)

`instrument_registry.py` updated: module
`"Percussion.steel_drums.steel_drums": "steel_drums"` added to
`_INSTRUMENT_MODULES`; `STEEL_DRUMS = ALL_INSTRUMENTS["steel_drums"]`
constant added; role mapping `"steel drums"` → `lead, melody, accent,
countermelody, harmony, rhythm`; `__main__` verification lines added.
Run output (`/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`):

```
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
...
  STEEL_DRUMS.midi_program = 114 (should be 114)
  by_name('steel drums') = <Instrument Steel Drums (family=Percussion, program=114, range=55-96)>
  by_program(114) = <Instrument Steel Drums (family=Percussion, program=114, range=55-96)>
  STEEL_DRUMS.in_sweet_spot(69) = True
```

`ALL_INSTRUMENTS` count: **26** (was 25).

## Verification results (verify_steel_drums.py)

- Registry import through `by_name('steel drums')` ✓
- Constants load through registry (all `_FIELDS`) ✓
- **Zero-drift**: `True (OK)` — 2 voices × 1 section, 1 bar, terminal
  landmark at BAR
- Voice stack: **Steel Drums solo melody (ch0)** + context low bass G2 (43,
  GM33) an octave+ below — NO second melodic patch on the same pitches
- **MIDI**: `steel_drums_test.mid` — 135 bytes (> 40 ✓)
- **WAV (solo, FluidR3 via discover_soundfont())**: `steel_drums_test.wav` —
  706,092 bytes (> 40 ✓)
- **Spectral check**: 4–8 kHz buzz energy = **0.6%** (OK — no comb-filtering)
- **Stem label**: pipeline GM_PROGRAMS[114] = `'Steel Drums'` ✓
  (STEM_LABEL matches); stem file on disk `track00_Steel_Drums.wav`
  (706,092 bytes) ✓
- **SF2 preset**: FluidR3 preset 114 = `'Steel Drums'` ✓ (phdr chunk)
- **ModalSynth**: custom PAN_MODES render peak 0.900, tail_rms/peak = 0.002
  (fast exponential decay, no sustain plateau) ✓; `'marimba'` preset peak
  0.900 ✓
- **Karplus-Strong**: loop_gain 0.9950 → tail_rms/peak(0.2–0.6 s) = 0.016 vs
  0.008 dull control (2.0× ring advantage) ✓

## Stem-label quirks found

- **None for GM114.** `GM_PROGRAMS[114]` = "Steel Drums" (two words) →
  stem file `trackXX_Steel_Drums.wav`; FluidR3 preset 114 also "Steel Drums"
  — labels match exactly.
- Related quirks confirmed unchanged in the same neighborhood: GM109
  "Bag pipe" → `Bag_pipe` (known quirk), ch9/pgm0 → "Acoustic_Grand_Piano"
  fallback (known quirk — steel drums must use a melodic channel 0–9, NOT
  channel 9).

## Files

- `Percussion/steel_drums/instrument.md` — full research reference
- `Percussion/steel_drums/steel_drums.py` — importable constants
- `instrument_registry.py` — registered (26 instruments)
- `registry.md` / `docs/instruments.md` — changelog + table + quirks updated
- `README.md` — structure + count updated
- `_test/verify_steel_drums.py` — end-to-end verification (ALL CHECKS PASSED)
- `_test/sweep_steel_drums.py` — FluidR3 pitch sweep (24–96 audible, no gaps)
- `_test/steel_drums_test.mid/.wav`, `_test/steel_drums_sweep.mid/.wav`,
  `_test/stems_steel_drums/` — artifacts
