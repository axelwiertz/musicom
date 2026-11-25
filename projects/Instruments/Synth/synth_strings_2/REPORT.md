# REPORT — Synth Strings 2 (GM51)

Nightly instrument research job, 2026-11-25. Instrument added to the musicom
Instruments reference library **and registered in the importable registry**,
so it is usable by composition jobs immediately.

- **Folder**: `Synth/synth_strings_2/`
- **Files**: `instrument.md`, `synth_strings_2.py`, `REPORT.md`
- **Registry key**: `synth_strings_2` → constant `SYNTH_STRINGS_2`
- **Registry load count**: 101 → **102**

---

## 1. What was added and why

GM51 "Synth Strings 2" was the top-listed remaining candidate carried forward
in `registry.md` (the changelog for GM50 named it explicitly as "the
slower/airier variant, still open"). It completes the synth-string block
(GM48/49 sampled sections, GM50 bright string machine, GM51 slow-swell
variant) and fills a real gap: the KC had **no dark-topped, slow-onset
string-machine pad** — everything in the pad block was either bright (GM50,
GM88) or rounder-but-different (GM89/90).

The census before/after:

```
before: instrument count: 101
        missing GM programs: [37, 51, 63, 83, 84, 85, 86, 87, 91..103, 112, 118..127]
after:  instrument count: 102
        missing GM programs: [37, 63, 83, 84, 85, 86, 87, 91..103, 112, 118..127]
```

## 2. Identity

The second voice of the **divide-down string machine** family (1972–1982):
Eminent 310 Unique, ARP Solina String Ensemble, ARP Omni, Roland RS-202, Korg
Poly-Ensemble, Elka Rhapsody, Logan String Melody, Crumar Performer.
Architecture inherited from GM50 and modelled identically:

- divide-down oscillator bank (bright buzzy core, band-limited by the divider
  chain)
- **one shared filter + one shared LFO** → paraphonic, not truly polyphonic
  (all held notes share the chorus phase; modelled as static per-voice detune,
  never per-note vibrato)
- **triple BBD ensemble chorus** — the slow wide swirl, measured as a ±25%
  envelope wobble during sustain (also present on GM50; it is the machine)
- no velocity sensitivity, infinite sustain while held, short capacitor
  release

## 3. Measured A/B vs GM50 (the empirical basis for every default)

Method: identical Cmaj7 chord (60/64/67/71; also 36/43/48/52 and 72/76/79/83),
velocity 76, 2 bars @120 BPM, rendered **solo** through FluidR3_GM via
`discover_soundfont()`, analysed over a 1.5 s window.

| Metric | GM50 Synth Strings 1 | GM51 Synth Strings 2 |
|---|---|---|
| centroid, mid (C4–B4) | 1738 Hz | **1853 Hz** |
| centroid, low (C2–E3) | 717 Hz | **1487 Hz** |
| centroid, high (C5–B5) | 2727 Hz | **2361 Hz** |
| 50–500 Hz share | 35.7% | 34.3% |
| 6–12 kHz air share | 4.2% | **3.4%** |
| envelope at 20 ms | 16% of peak | **12%** |
| envelope at 100 ms | 30% | **35%** |
| peak amplitude | 0.496 | **0.544** |

Interpretation → design decisions:

- **≈2× upper-partial energy in the bass register** (1487 vs 717 Hz centroid)
  → `SOLO_RANGE` bottom dropped to C3 (48) instead of GM50's E3 (52); low zone
  documented as a strength, not mud.
- **Top-octave roll-off** (2361 vs 2727 Hz, air 3.4% vs 4.2%) → PolySynth
  filter 2700 Hz (GM50: 3000), no square-wave edge (saw + saw + triangle),
  EQ air shelf 9 kHz +1.0 (GM50: 8 kHz +1.5), presence 2.6 kHz (GM50: 3.2).
- **Softer onset** (12% vs 16% of peak at 20 ms) → `env_attack` 0.09 s (GM50:
  0.03), release 0.45 s (GM50: 0.25), reverb 3.4 s (GM50: 2.8).
- **Louder at same velocity** (+0.8 dB) → no gain compensation needed, but
  flagged so arrangement balance is not surprised.

Pitch check (single notes, FFT peak vs equal temperament):

```
GM51 written 48 (130.8 Hz) -> peak 130.8 Hz
GM51 written 60 (261.6 Hz) -> peak 261.7 Hz
GM51 written 72 (523.3 Hz) -> peak 521.7 Hz
```

→ plays at the **written octave**, no transpose quirk (contrast GM31 Guitar
Harmonics, which sounds +12).

## 4. Constants (`synth_strings_2.py`)

```
MIDI_PROGRAM = 51
GM_NAME      = "Synth Strings 2"
STEM_LABEL   = "Synth_Strings_2"
RANGE_MIN    = 36      # C2
RANGE_MAX    = 96      # C7
SOLO_RANGE   = (48, 86)   # C3–D6
SWEET_SPOT   = (55, 84)   # G3–C6
ZONES        = low (36,55) / mid (56,79) / high (80,96)

ARTICULATIONS = sustain 70/1.0, legato 68/1.0, swell 84/1.0, bloom 76/0.9,
                staccato 62/0.25, marcato 82/0.85, drone 56/1.0, accent 88/0.9

SYNTHESIS = "polysynth"
POLYSYNTH_DEFAULTS = saw + saw(+11c) + triangle(-11c)@0.75,
                     filter 2700 Hz, resonance 0.25, attack 0.09,
                     decay 0.08, sustain 1.0, release 0.45, unison 3
ADDITIVE_HARMONICS = {"string_machine_airy":
                      [1.0, 0.82, 0.64, 0.48, 0.34, 0.22, 0.12, 0.06]}
SYNTHESIS_DEFAULTS = instrument "synth_strings_2", attack 0.09, detune 0.012,
                     stack 3, release 0.45, sustain_level 1.0, decay_S 1e-4
MODAL_PRESET = "string"
FM_DEFAULTS  = saw carrier, ratio 1.0, depth 0.9, attack 0.09, release 0.5

REVERB_TAIL = 3.4 s
EQ_BODY     = (300, -2.0)
EQ_PRESENCE = (2600, 1.5)
EQ_AIR      = (9000, 1.0)
PAN         = 0.0
midi_to_freq()  # 440 * 2**((m-69)/12)
```

## 5. Role

`pad, harmony, texture, drone, swell, countermelody`

- **pad / harmony** — sustained chords under lead or vocal (default)
- **texture** — wide chorus bed that does not mask a bright lead (no top fizz)
- **drone** — static held root/fifth, ambient/cinematic writing
- **swell** — section-boundary crescendo; the soft onset makes builds sound
  played rather than switched on (this is the gesture GM50 cannot do well)
- **countermelody** — long-note line under a moving lead
- NOT a lead voice for fast lines (soft onset smears articulation)
- NOT rhythm/comp, NOT a bass foundation (chorused bottom)
- NOT a realistic orchestral section (GM48/49)

## 6. Registration proof (REGISTRY DISCIPLINE)

`instrument_registry.py` changes:

1. `_INSTRUMENT_MODULES`: added
   `"Synth.synth_strings_2.synth_strings_2": "synth_strings_2",`
2. convenience constant: `SYNTH_STRINGS_2 = ALL_INSTRUMENTS["synth_strings_2"]`
3. `registry_table()` role branch:
   `elif low == "synth strings 2": role = "pad, harmony, texture, drone, swell, countermelody"`
4. `__main__` verification block for GM51 added.

`python instrument_registry.py` → exit 0. Extracted rows and verification:

```
| Synth | Synth Strings 1 | 50 | 36–96 | pad, harmony, texture, drone, lead, countermelody, accent |
| Synth | Synth Strings 2 | 51 | 36–96 | pad, harmony, texture, drone, swell, countermelody |

=== Synth Strings 2 (slow-swell string machine, GM51) ===
  SYNTH_STRINGS_2.midi_program = 51 (should be 51)
  by_name('synth strings 2') = <Instrument Synth Strings 2 (family=Synth, program=51, range=36-96)>
  by_name('Synth Strings 2') = <Instrument Synth Strings 2 (family=Synth, program=51, range=36-96)>
  by_program(51) = <Instrument Synth Strings 2 (family=Synth, program=51, range=36-96)>
  by_program(50) = <Instrument Synth Strings 1 (family=Synth, program=50, range=36-96)> (distinct: synth strings 1 — bright sibling)
  SYNTH_STRINGS_2.in_sweet_spot(72) = True
  SYNTH_STRINGS_2.in_sweet_spot(24) = False
  SYNTH_STRINGS_2.range_min = 36 SYNTH_STRINGS_2.range_max = 96
  SYNTH_STRINGS_2.solo_range = (48, 86)
  SYNTH_STRINGS_2.stem_label = 'Synth_Strings_2'
  SYNTH_STRINGS_2.synthesis = 'polysynth'
  SYNTH_STRINGS_2.reverb_tail = 3.4 SYNTH_STRINGS_2.pan = 0.0
  SYNTH_STRINGS_2.articulations = ['sustain', 'legato', 'swell', 'bloom', 'staccato', 'marcato', 'drone', 'accent']
```

Full run captured at `_test/registry_out_synth_strings_2.txt` (638+ lines).

## 7. End-to-end verification (`_test/verify_synth_strings_2.py`)

Composition: 1 bar / 1 section @104 BPM — voice 0 Synth Strings 2 **SOLO** on
ch0 (sustained C3 + C4-E4-G4-Bb4 body held the full bar), voice 1 drum kit on
ch9 as context. **No second melodic patch on the same pitches** (2026-09-01
comb-filter rule).

```
Registered: <Instrument Synth Strings 2 (family=Synth, program=51, range=36-96)>
  program=51 gm='Synth Strings 2' stem='Synth_Strings_2'
  range=36-96 solo=(48, 86) sweet=(55, 84)
  synth='polysynth' poly={... filter_cutoff 2700.0, env_attack 0.09, env_release 0.45, unison_voices 3 ...}
  reverb=3.4s eq_body=(300, -2.0) eq_presence=(2600, 1.5) eq_air=(9000, 1.0) pan=0.0

Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/synth_strings_2_test.mid (140 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
WAV (solo): /opt/data/projects/Instruments/_test/synth_strings_2_test.wav (1290028 bytes)
Spectral check: 4-8kHz buzz energy = 1.9% (OK)

Stem label: GM_PROGRAMS[51] = 'Synth Strings 2'

Stems rendered (2 files):
  track00_Synth_Strings_2.wav (1290028 bytes)
  track01_Drums.wav (784428 bytes)

PolySynth: peak=0.980 tail_rms/peak=0.581 early(20-40ms)/mid(0.4-0.6s)=0.325
SF2 preset 51 -> 'Synth Strings 2' (sibling 50 -> 'Synth Strings 1')

ALL CHECKS PASSED
```

- **Zero-drift**: `validate()` True; every unit ends flush at BAR.
- **MIDI**: 140 bytes (> 40 gate).
- **WAV**: 1,290,028 bytes solo (FluidR3 via `discover_soundfont()`, not a
  hardcoded TimGM6mb path).
- **Buzz gate**: 1.9% in 4–8 kHz (gate ≤20%) — clean single voice.
- **Stem on disk**: `track00_Synth_Strings_2.wav`, label matches pipeline
  exactly.
- **Engine smoke test**: PolySynth sustains (tail/peak 0.581 > 0.5) but swells
  (early/mid 0.325 < 0.5) — the GM51 envelope behaves as documented, unlike
  GM50's near-instant onset.

## 8. Quirks and notes

- **Stem label**: `GM_PROGRAMS[51]` = "Synth Strings 2" → sanitized
  `Synth_Strings_2`. Exact match, **no quirk**.
- **SF2 preset**: FluidR3 preset 51 = "Synth Strings 2" (exact). TimGM6mb
  fallback also has a preset 51 but is thin — always resolve via
  `discover_soundfont()`.
- **No transpose quirk** (verified: written C3/C4/C5 → 130.8/261.7/521.7 Hz).
- **Sustain is not flat**: envelope wobbles ±25% — BBD chorus amplitude/phase
  modulation, present on GM50 too. Do not "fix" it; do not measure decay from
  tail-vs-peak on this patch.
- **Onset**: ~90 ms — slowest in the synth-string block. Stabs/chops are the
  wrong gesture; that is GM50 or a brass patch's job.
- **Doubling**: never unison-double against GM50 or a sampled section on the
  same pitches (comb-filtering buzz). Octave-down or different chord tone only.
- **MidiInstrument enum** exposes only 10 programs and has no synth-strings
  constant — the raw GM number 51 is used; the registry is the full KB.

## 9. Docs updated

- `registry.md`: registry-table row added; stem-label quirks row added
  (no quirk); dated changelog entry "**Synth Strings 2 added** (2026-11-25)".
- `README.md`: counts corrected 82→96 folders, 88/97→102 registry keys.
- `instrument_registry.py`: module entry, constant, role branch, verification
  block.

## 10. Remaining candidates

GM63 Synth Brass 2, GM37 Slap Bass 2, GM112 Tinkle Bell, GM118 Synth Drum,
GM119 Reverse Cymbal, GM91–103 pads/FX block, GM80/81 Lead square/saw
(program collision with the Vocal talkbox / singing-saw stand-ins must be
resolved before adding).
