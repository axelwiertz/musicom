# REPORT — Pad 3 (polysynth) (GM90)

**Date**: 2026-11-24
**Family**: Synth (ninth entry)
**Files**: `Synth/polysynth_pad/instrument.md`, `Synth/polysynth_pad/polysynth_pad.py`
**Registry key**: `polysynth_pad` → constant `POLYSYNTH_PAD`

## 1. Instrument identity

GM90 "Pad 3 (polysynth)" = the classic **analog polysynth pad** (1979–1984):
Roland Juno-106 / JX-8P, Oberheim OB-X, Sequential Prophet-5, Korg Poly-61.

Architecture that defines every constant:

- stack of detuned saw/triangle oscillators (3+ voices per note) → the fat
  analog "ensemble" blur;
- one resonant low-pass filter per voice (the classic polysynth signal path);
- slow attack (200–450 ms) — pads ENTER, they don't stab;
- wide chorus / unison detune (±7 cents × 4 voices) → the analog width;
- infinite sustain while held, 400–600 ms release.

The THIRD member of the KB's synth-pad block, the MIDDLE sibling:
GM88 "Pad 1 (new age)" (bright/digital glass — D-50 Fantasia), GM89 "Pad 2
(warm)" (dark/round analog — Juno/OB-X warmth), and **GM90** — rounder and
slower than the new-age shimmer, MORE mid presence and faster attack than
the warm pad (80s pop-ballad pads, synthwave chords, Detroit techno beds).

## 2. MIDI / program

| Field | Value |
|---|---|
| MIDI program | **90** (raw GM; `MidiInstrument` enum has no polysynth member) |
| GM name | "Pad 3 (polysynth)" |
| FluidR3 preset 90 | "Polysynth" (verified from `phdr` chunk — the ONE synth pad whose SF2 name IS the engine name; 88 = "Fantasia", 89 = "Warm Pad") |
| RenderPipeline `GM_PROGRAMS[90]` | "Pad 3 (polysynth)" → sanitized `trackXX_Pad_3_polysynth.wav` — **no quirk** |
| Channel | melodic (0); polyphonic |

## 3. Range

| Field | MIDI | Pitches |
|---|---|---|
| RANGE_MIN | 36 | C2 |
| RANGE_MAX | 96 | C7 |
| SOLO_RANGE | 55–84 | G3–C6 |
| SWEET_SPOT | 60–84 | C4–C6 |

Zones: low 36–55 (C2–G3, pad bottom/drone roots), mid 56–79 (G#3–G5,
workhorse chord body), high 80–96 (G#5–C7, analog top, filter-rolled).

## 4. Role

pad, harmony, texture, drone, accent (soft marcato entrances). **NOT** a lead
voice (slow attack smears melodic runs), **NOT** a rhythm/comp voice, **NOT**
a bass foundation (thin chorused bottom).

## 5. Synthesis engine

- **Primary: PolySynth** (`sound/synthesis/polysynth.py` PolyVoice) — the
  polyBLEP subtractive architecture (3 osc + multimode filter + ADSR +
  unison) IS the physical model of the analog polysynth pad; this is the ONE
  KB instrument whose GM name IS the engine. `POLYSYNTH_DEFAULTS`: saw +
  ±7-cent detuned saw + triangle body (osc3_level 0.7), filter cutoff
  **1800 Hz** (between warm_pad 1400 and synth_brass_1 2800), resonance 0.3,
  attack 0.35 s, decay 0.2 s, sustain 0.85, release 0.6 s, **unison 4**
  (widest chorus in the Synth family).
- **Secondary: Additive** — `pad_polysynth` harmonic stack
  `[1.0, 0.75, 0.55, 0.38, 0.25, 0.15, 0.09]`, detune ±0.012, stack 4,
  attack 0.35 s, release 0.6 s, `decay_S = 1e-4` (hold chord — the 2026-10-12
  additive quirk).
- **Tertiary: PhaseModSynth** — saw carrier, ratio 1.0, depth 1.8 (between
  warm 1.5 and synth_brass_1 3.2; fattens, never honks), attack 0.4 s,
  release 0.6 s.
- `MODAL_PRESET = "string"` (generic fallback only; least faithful — for
  short plucked "blip" effects, not the sustained pad).

## 6. All constants (polysynth_pad.py)

```
MIDI_PROGRAM = 90
GM_NAME = "Pad 3 (polysynth)"
STEM_LABEL = "Pad_3_polysynth"
RANGE_MIN = 36 ; RANGE_MAX = 96
SOLO_RANGE = (55, 84) ; SWEET_SPOT = (60, 84)
ZONES = {low:(36,55), mid:(56,79), high:(80,96)}
ARTICULATIONS = {sustain:(70,1.0), legato:(68,1.0), swell:(82,1.0),
                 staccato:(64,0.25), marcato:(85,0.85), drone:(60,1.0),
                 accent:(88,0.9), bloom:(66,1.25)}
SYNTHESIS = "polysynth"
POLYSYNTH_DEFAULTS = {osc1_waveform:"saw", osc2_waveform:"saw",
                      osc2_detune_cents:7.0, osc3_waveform:"triangle",
                      osc3_detune_cents:-7.0, osc3_level:0.7,
                      filter_cutoff:1800.0, filter_resonance:0.3,
                      env_attack:0.35, env_decay:0.2, env_sustain:0.85,
                      env_release:0.6, unison_voices:4}
SYNTHESIS_DEFAULTS = {instrument:"polysynth_pad", **POLYSYNTH_DEFAULTS}
ADDITIVE_HARMONICS = {pad_polysynth:[1.0,0.75,0.55,0.38,0.25,0.15,0.09]}
ADDITIVE_DEFAULTS = {attack:0.35, detune:0.012, stack:4, release:0.6,
                     sustain_level:0.9, decay_S:1e-4}
FM_DEFAULTS = {carrier:"saw", mod:"sine", ratio:1.0, depth:1.8,
               attack:0.4, release:0.6, sustain:0.85}
MODAL_PRESET = "string"
REVERB_TAIL = 3.0
EQ_BODY = (250, -2.5) ; EQ_PRESENCE = (2800, 2.0) ; EQ_AIR = (8000, 1.5)
PAN = 0.0
midi_to_freq(69) = 440.0 Hz
```

## 7. Registration proof

Registered in `_INSTRUMENT_MODULES` as
`"Synth.polysynth_pad.polysynth_pad": "polysynth_pad"`, constant
`POLYSYNTH_PAD = ALL_INSTRUMENTS["polysynth_pad"]`, registry-table role
branch added for "pad 3 (polysynth)". Registry `_FIELDS` already carried
`polysynth_defaults` (added for synth_strings_1) — **no extension needed**.

`instrument_registry.py` output (excerpt — table row + verification block):

```
| Synth | Pad 3 (polysynth) | 90 | 36–96 | pad, harmony, texture, drone, accent |

=== Pad 3 (polysynth, GM90) ===
  POLYSYNTH_PAD.midi_program = 90 (should be 90)
  by_name('polysynth pad') = <Instrument Pad 3 (polysynth) (family=Synth, program=90, range=36-96)>
  by_name('Pad 3 (polysynth)') = <Instrument Pad 3 (polysynth) (family=Synth, program=90, range=36-96)>
  by_program(90) = <Instrument Pad 3 (polysynth) (family=Synth, program=90, range=36-96)>
  by_program(89) = <Instrument Pad 2 (warm) (family=Synth, program=89, range=36-96)> (distinct: warm pad — Pad 2)
  POLYSYNTH_PAD.in_sweet_spot(72) = True
  POLYSYNTH_PAD.in_sweet_spot(24) = False
  POLYSYNTH_PAD.range_min = 36 POLYSYNTH_PAD.range_max = 96
  POLYSYNTH_PAD.solo_range = (55, 84)
  POLYSYNTH_PAD.stem_label = 'Pad_3_polysynth'
  POLYSYNTH_PAD.synthesis = 'polysynth'
  POLYSYNTH_PAD.polysynth_defaults = {'osc1_waveform': 'saw', 'osc2_waveform': 'saw', 'osc2_detune_cents': 7.0, 'osc3_waveform': 'triangle', 'osc3_detune_cents': -7.0, 'osc3_level': 0.7, 'filter_cutoff': 1800.0, 'filter_resonance': 0.3, 'env_attack': 0.35, 'env_decay': 0.2, 'env_sustain': 0.85, 'env_release': 0.6, 'unison_voices': 4}
  POLYSYNTH_PAD.reverb_tail = 3.0 POLYSYNTH_PAD.pan = 0.0
  POLYSYNTH_PAD.articulations = ['sustain', 'legato', 'swell', 'staccato', 'marcato', 'drone', 'accent', 'bloom']
```

Registry table row count: 100 → 101 instrument rows in `ALL_INSTRUMENTS`
(after adding polysynth_pad).

## 8. Verification results

Script: `_test/verify_polysynth_pad.py` (constants imported via
`from instrument_registry import by_name, POLYSYNTH_PAD`; WAV via
`discover_soundfont()`; SOLO render).

Composition: 1 bar / 1 section, bpm 104 — voice 0 = Pad 3 (polysynth) (ch0,
sustained Cmaj7 pad C4-E4-G4-B4 held the whole bar), voice 1 = drum kit (ch9,
kick/snare/hats, terminal landmark). **No second melodic patch** — the
2026-09-01 comb-filter rule.

```
Registered: <Instrument Pad 3 (polysynth) (family=Synth, program=90, range=36-96)>
  program=90 gm='Pad 3 (polysynth)' stem='Pad_3_polysynth'
  range=36-96 solo=(55, 84) sweet=(60, 84)
  synth='polysynth' poly={...saw core, 1800 Hz cutoff, unison 4...}
  reverb=3.0s eq_body=(250, -2.5) eq_presence=(2800, 2.0) eq_air=(8000, 1.5) pan=0.0

Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/polysynth_pad_test.mid (134 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
WAV (solo): /opt/data/projects/Instruments/_test/polysynth_pad_test.wav (1279788 bytes)
Spectral check: 4-8kHz buzz energy = 0.8% (OK)

Stem label: GM_PROGRAMS[90] = 'Pad 3 (polysynth)'

Stems rendered (2 files):
  track00_Pad_3_polysynth.wav (1279788 bytes)
  track01_Drums.wav (784428 bytes)

PolySynth: peak=0.972 early(0.5-0.7s)=0.486 late(1.3-1.5s)=0.484 late/early=0.995

ALL CHECKS PASSED
```

| Gate | Result |
|---|---|
| Zero-drift `validate()` | ✓ True (OK) |
| MIDI size | 134 bytes (> 40) ✓ |
| WAV solo size | 1,279,788 bytes (> 40) ✓ |
| 4–8 kHz buzz (solo) | 0.8% (≤ 20%) ✓ |
| Stem label on disk | `track00_Pad_3_polysynth.wav` ✓ |
| PolySynth sustain behaviour | late/early 0.995 — flat sustain (no natural decay) ✓ |
| `tests/test_voice_hybrid.py` + `test_ballad_palette.py` | 34 passed (registry change safe) ✓ |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36–108 step 12):
preset 90 audible **7/7** notes, no gaps — SF2 never clips a composition:

| MIDI | Pitch | RMS |
|---|---|---|
| 36 | C2 | 0.0811 |
| 48 | C3 | 0.0647 |
| 60 | C4 | 0.0908 |
| 72 | C5 | 0.0921 |
| 84 | C6 | 0.0886 |
| 96 | C7 | 0.0814 |
| 108 | C8 | 0.0405 |

## 9. Quirks found

1. **No stem-label quirk**: `GM_PROGRAMS[90]` = "Pad 3 (polysynth)" →
   sanitized `Pad_3_polysynth` (parens stripped, spaces → underscore);
   `STEM_LABEL` matches the pipeline's real sanitization. FluidR3 preset 90 =
   "Polysynth" — the SF2 internal name IS the engine name (contrast 88
   "Fantasia" / 89 "Warm Pad").
2. **Enum gap**: `MidiInstrument` exposes only 10 programs and has no
   polysynth constant — raw GM 90 must be used. Registry is the full KB.
3. **Sustain measurement**: the synth_strings_1-style tail-vs-peak flatness
   check skews low at sustain < 1.0 (saw RMS ≈ 0.577 × sustain 0.85 ≈ 0.49,
   below any 0.5 threshold) — measure flatness INSIDE the sustain plateau
   (early vs late window, ratio → 1.0) instead. Documented so future pad
   entries don't trip on the same artifact.
4. **GM90 is the middle pad**: 88 glass / 89 dark / 90 round-present —
   composition jobs should pick by the arrangement's top-end need (air →
   88, dark bed → 89, 80s analog body → 90).
5. **Program collision watch**: GM80 "Lead 1 (square)" and GM81 "Lead 2
   (sawtooth)" are the same programs the Vocal family's Talkbox (80) and
   Singing Saw (81) use as MIDI stand-ins — a future lead entry must resolve
   the `by_program` collision before registering (recorded in registry.md).
6. **`_FIELDS` unchanged**: `polysynth_defaults` already existed (from
   synth_strings_1) — no registry schema change needed this time.

## 10. Remaining sibling candidates

GM51 Synth Strings 2, GM112 Tinkle Bell, GM118 Synth Drum, GM63 Synth Brass 2,
GM37 Slap Bass 2, GM80/81 Lead square/saw (program collision with Vocal
Talkbox/Singing-Saw stand-ins to resolve first).
