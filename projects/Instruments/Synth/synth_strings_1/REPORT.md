# REPORT — Synth Strings 1 (GM50)

**Date**: 2026-11-23
**Family**: Synth (seventh entry)
**Files**: `Synth/synth_strings_1/instrument.md`, `Synth/synth_strings_1/synth_strings_1.py`
**Registry key**: `synth_strings_1` → constant `SYNTH_STRINGS_1`

## 1. Instrument identity

GM50 "Synth Strings 1" = the **divide-down string machine** (1972–1982):
Eminent 310 Unique, ARP Solina String Ensemble, ARP Omni, Roland RS-202, Korg
Poly-Ensemble, Elka Rhapsody, Logan String Melody, Crumar Performer.

Architecture that defines every constant:

- divide-down oscillator bank (all 12 pitches per octave, borrowed across octaves)
  → bright square/saw hybrid tone, band-limited by the divider chain;
- **one shared filter + one shared LFO** for the whole keyboard → paraphonic:
  all held notes share the same chorus/vibrato phase;
- **triple BBD ensemble chorus** (three phase-shifted LFO-delayed taps,
  ~0.3–1.5 Hz, ±8–15 cents) → the slow wide swirl;
- no velocity sensing, no bow/rosin noise, **infinite sustain while held**,
  20–40 ms capacitor attack, 100–300 ms release.

The synthetic sibling of the sampled sections: GM48 String Ensemble 1 / GM49
String Ensemble 2 are acoustic and realistic; GM50 is brighter, wider, obviously
processed (Pink Floyd "Shine On You Crazy Diamond", Jarre *Oxygène*, Air "Sexy
Boy", disco string pads).

## 2. MIDI / program

| Field | Value |
|---|---|
| MIDI program | **50** (raw GM; `MidiInstrument` enum has no synth-strings member) |
| GM name | "Synth Strings 1" |
| FluidR3 preset 50 | "Synth Strings 1" (verified from `phdr` chunk) |
| RenderPipeline `GM_PROGRAMS[50]` | "Synth Strings 1" → `trackXX_Synth_Strings_1.wav` — **no quirk** |
| Channel | melodic (0); polyphonic |

## 3. Range

| Field | MIDI | Pitches |
|---|---|---|
| RANGE_MIN | 36 | C2 |
| RANGE_MAX | 96 | C7 |
| SOLO_RANGE | 52–88 | E3–E6 |
| SWEET_SPOT | 60–84 | C4–C6 |

Zones: low 36–55 (C2–G3, cello-ish pad body), mid 56–79 (G#3–G5, workhorse),
high 80–96 (G#5–C7, band-limited violin-top sheen). Original machines were
4-octave/49-key; the GM patch extends the span.

## 4. Role

pad, harmony, texture, drone, lead (unison chorus lines), countermelody,
accent (swell hit). **NOT** a bass foundation (thin chorused bottom), **NOT** a
realistic orchestral section (GM48/49).

## 5. Synthesis engine

- **Primary: PolySynth** (`sound/synthesis/polysynth.py`) — the subtractive
  divide-down + shared low-pass + unison detune IS the physical model.
  `POLYSYNTH_DEFAULTS`: saw + square osc pair, ±9-cent osc2/osc3 detune,
  osc3 level 0.8, filter cutoff 3000 Hz, resonance 0.2, attack 0.03 s,
  decay 0.05 s, **sustain 1.0**, release 0.25 s, unison 3.
- **Secondary: Additive** — `string_machine` harmonic stack
  `[1.0, 0.85, 0.70, 0.55, 0.40, 0.28, 0.18, 0.10]`, detune ±1.0%, stack 3,
  attack 0.03 s, release 0.25 s, `decay_S = 1e-4` (hold chord).
- **Tertiary: PhaseModSynth** — saw carrier, ratio 1.0, depth 1.2 (gentle,
  NOT brassy), attack 0.03 s, release 0.3 s.
- `MODAL_PRESET = "string"` (generic fallback only; least faithful).

## 6. All constants (synth_strings_1.py)

```
MIDI_PROGRAM = 50
GM_NAME = "Synth Strings 1"
STEM_LABEL = "Synth_Strings_1"
RANGE_MIN = 36 ; RANGE_MAX = 96
SOLO_RANGE = (52, 88) ; SWEET_SPOT = (60, 84)
ZONES = {low:(36,55), mid:(56,79), high:(80,96)}
ARTICULATIONS = {sustain:(70,1.0), legato:(68,1.0), swell:(82,1.0),
                 staccato:(66,0.25), marcato:(86,0.85), drone:(58,1.0),
                 accent:(90,0.9)}
SYNTHESIS = "polysynth"
SYNTHESIS_DEFAULTS = {instrument:"synth_strings_1", attack:0.03,
                      detune:0.010, stack:3, release:0.25,
                      sustain_level:1.0, decay_S:1e-4}
POLYSYNTH_DEFAULTS = {... see §5 ...}
FM_DEFAULTS = {carrier:"saw", mod:"sine", ratio:1.0, depth:1.2,
               attack:0.03, release:0.3, sustain:1.0}
REVERB_TAIL = 2.8
EQ_BODY = (250, -2.5) ; EQ_PRESENCE = (3200, 2.0) ; EQ_AIR = (8000, 1.5)
PAN = 0.0
midi_to_freq(69) = 440.0 Hz
```

## 7. Registration proof

Registered in `_INSTRUMENT_MODULES` as
`"Synth.synth_strings_1.synth_strings_1": "synth_strings_1"`, constant
`SYNTH_STRINGS_1 = ALL_INSTRUMENTS["synth_strings_1"]`, registry-table role
branch added, and `_FIELDS` extended with `polysynth_defaults` (also makes
`warm_pad.POLYSYNTH_DEFAULTS` registry-visible).

`instrument_registry.py` output (excerpt — table row + verification block):

```
| Synth | Synth Strings 1 | 50 | 36–96 | pad, harmony, texture, drone, lead, countermelody, accent |

=== Synth Strings 1 (Divide-down String Machine, GM50) ===
  SYNTH_STRINGS_1.midi_program = 50 (should be 50)
  by_name('synth strings 1') = <Instrument Synth Strings 1 (family=Synth, program=50, range=36-96)>
  by_name('Synth Strings 1') = <Instrument Synth Strings 1 (family=Synth, program=50, range=36-96)>
  by_program(50) = <Instrument Synth Strings 1 (family=Synth, program=50, range=36-96)>
  by_program(49) = <Instrument String Ensemble 2 (family=Strings, program=49, range=28-96)> (distinct: sampled string ensemble 2)
  SYNTH_STRINGS_1.in_sweet_spot(72) = True
  SYNTH_STRINGS_1.in_sweet_spot(24) = False
  SYNTH_STRINGS_1.range_min = 36 SYNTH_STRINGS_1.range_max = 96
  SYNTH_STRINGS_1.solo_range = (52, 88)
  SYNTH_STRINGS_1.stem_label = 'Synth_Strings_1'
  SYNTH_STRINGS_1.synthesis = 'polysynth'
  SYNTH_STRINGS_1.polysynth_defaults = {'osc1_waveform': 'saw', 'osc2_waveform': 'square', 'osc2_detune_cents': 9.0, 'osc3_waveform': 'saw', 'osc3_detune_cents': -9.0, 'osc3_level': 0.8, 'filter_cutoff': 3000.0, 'filter_resonance': 0.2, 'env_attack': 0.03, 'env_decay': 0.05, 'env_sustain': 1.0, 'env_release': 0.25, 'unison_voices': 3}
  SYNTH_STRINGS_1.reverb_tail = 2.8 SYNTH_STRINGS_1.pan = 0.0
  SYNTH_STRINGS_1.articulations = ['sustain', 'legato', 'swell', 'staccato', 'marcato', 'drone', 'accent']
```

Registry table now has 100 instrument rows (99 before this entry + the new
one); `len(ALL_INSTRUMENTS)` = 100.

## 8. Verification results

Script: `_test/verify_synth_strings_1.py` (constants imported via
`from instrument_registry import by_name, SYNTH_STRINGS_1`; WAV via
`discover_soundfont()`; SOLO render).

Composition: 1 bar / 1 section, bpm 104 — voice 0 = Synth Strings 1 (ch0,
sustained Cmaj7 pad C4-E4-G4-B4 held the whole bar), voice 1 = drum kit (ch9,
kick/snare/hats, terminal landmark). **No second melodic patch** — the
2026-09-01 comb-filter rule.

```
Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/synth_strings_1_test.mid (134 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
WAV (solo): /opt/data/projects/Instruments/_test/synth_strings_1_test.wav (1290028 bytes)
Spectral check: 4-8kHz buzz energy = 1.5% (OK)

Stem label: GM_PROGRAMS[50] = 'Synth Strings 1'

Stems rendered (2 files):
  track00_Synth_Strings_1.wav (1290028 bytes)
  track01_Drums.wav (784428 bytes)

PolySynth: peak=0.980 tail_rms/peak=0.581

ALL CHECKS PASSED
```

| Gate | Result |
|---|---|
| Zero-drift `validate()` | ✓ True (OK) |
| MIDI size | 134 bytes (> 40) ✓ |
| WAV solo size | 1,290,028 bytes (> 40) ✓ |
| 4–8 kHz buzz (solo) | 1.5% (≤ 20%) ✓ |
| Stem label on disk | `track00_Synth_Strings_1.wav` ✓ |
| PolySynth sustain behaviour | tail_rms/peak 0.581 — sustained (no natural decay) ✓ |
| `tests/test_voice_hybrid.py` | 24 passed (registry `_FIELDS` change safe) ✓ |

## 9. Quirks found

1. **No stem-label quirk**: `GM_PROGRAMS[50]` = "Synth Strings 1" and FluidR3
   preset 50 = "Synth Strings 1" — exact match. Sanitized stem is
   `Synth_Strings_1` (spaces → underscore only).
2. **Enum gap**: `MidiInstrument` exposes only 10 programs and has no synth
   strings constant — raw GM 50 must be used. Registry is the full KB.
3. **Paraphonic truth**: a real string machine cannot give one note vibrato and
   leave another still, and has no velocity response. Model the chorus with
   static per-voice detune; never add per-note vibrato; write dynamics via
   register/density, not velocity.
4. **Sustain, not decay**: the patch holds indefinitely while the key is down —
   unlike sampled GM48/49 with their loop/decay. PolySynth smoke test confirms
   flat sustain (tail 0.581 of peak, release only at gate-off).
5. **Band-limited top**: BBD top rolls off ~6–8 kHz; the 8 kHz air shelf is a
   gentle restoration, not a request for sampled-string sparkle.
6. **`_FIELDS` extension**: added `polysynth_defaults` so the subtractive
   preset is registry-visible (same pattern as `electric_grand_modes`); it is
   additive and backward-compatible (getattr default None for all others).

## 10. Remaining sibling candidates

GM51 Synth Strings 2, GM112 Tinkle Bell, GM118 Synth Drum, GM63 Synth Brass 2,
GM37 Slap Bass 2.
