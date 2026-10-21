# Drawbar Organ (Hammond tonewheel) — research + verification report

**Date**: 2026-10-21
**Family**: Keys (10th entry; joins Piano, Church Organ, Reed Organ, Accordion,
Harpsichord, Clavi, Celesta, Dulcimer, Rhodes, Electric Piano 2)
**Instrument**: Drawbar Organ — Hammond B-3 / C-3 tonewheel organ (GM16)
**Files**: `Keys/drawbar_organ/instrument.md`, `Keys/drawbar_organ/drawbar_organ.py`
**Verify script**: `_test/verify_drawbar_organ.py` (SOLO render, 1 voice)

## 1. Identity and why GM16

The drawbar organ is the electromechanical tonewheel organ (Hammond, 1935;
B-3 console 1954-1975). 91 toothed tonewheels generate sine partials that
nine drawbars per manual mix at levels 0-8. It is the one common instrument
whose timbre *is* additive synthesis — the pedal drawbars, the 1.5x "quint",
the key click and the Leslie are all measurable, model-able properties.

Distinct from the two neighbouring GM organ patches already in the library:

| Patch | Instrument | Character |
|---|---|---|
| GM16 Drawbar Organ | **this entry** | Tonewheel, drawbar-built partials, key click, percussion, Leslie |
| GM19 Church Organ | `Keys/organ` | Pipe organ, chiff, 2.2 s cathedral tail |
| GM20 Reed Organ | `Keys/reed_organ` | Harmonium, free reed, bellows |

GM16 was the largest untouched program in the Keys family and the only
program where the additive engine is a physical model rather than a fallback.

## 2. MIDI / GM

- **Program**: 16 (raw; `MidiInstrument` enum exposes only 10 instruments)
- **GM name**: "Drawbar Organ"
- **Channel**: any melodic channel 0-9; polyphonic
- **FluidSynth**: `discover_soundfont()` → `FluidR3_GM.sf2` (141 MB), bank-0
  preset 16, internal preset name `"DrawbarOrgan"` (no space — cosmetic)
- **RenderPipeline label**: `GM_PROGRAMS[16] = "Drawbar Organ"` →
  `track00_Drawbar_Organ.wav` — matches `STEM_LABEL = "Drawbar_Organ"` exactly,
  **no routing quirk**
- **Empirical sweep**: preset 16 audible on every pitch 20-96 (rms
  0.060-0.082, peak 0.17-0.24), no silent gaps, no clipping

## 3. Range and zones

| Zone | MIDI | Pitches | Use |
|---|---|---|---|
| Full | 24-89 | C1-F6 | 25-note pedal board + two 61-key manuals |
| Pedal | 24-48 | C1-C3 | 16'+8' pedal roots, bass foundation |
| Lower manual | 29-65 | F1-F4 | left-hand comping, chords, key bass |
| Upper manual | 48-89 | C3-F6 | right-hand lead, stabs, smears |

- `RANGE_MIN = 24`, `RANGE_MAX = 89`
- `SOLO_RANGE = (48, 84)` (C3-C6), `SWEET_SPOT = (55, 79)` (G3-G5)
- Written = sounding pitch (non-transposing). Manual compass is F1-F6
  (61 keys), pedals C1-C3 (25 notes).

## 4. Constants (drawbar_organ.py)

```python
MIDI_PROGRAM = 16
GM_NAME = "Drawbar Organ"
STEM_LABEL = "Drawbar_Organ"
RANGE_MIN = 24; RANGE_MAX = 89
SOLO_RANGE = (48, 84); SWEET_SPOT = (55, 79)
ZONES = {"pedal": (24, 48), "lower": (29, 65), "upper": (48, 89)}
ARTICULATIONS = {
    "sustain": (85, 1.0), "legato": (80, 1.0), "staccato": (70, 0.18),
    "percussion": (88, 0.35), "key_click": (74, 0.06), "accent": (96, 0.85),
    "palm_smear": (64, 0.9), "bass_pedal": (82, 0.95),
}
SYNTHESIS = "additive"
ADDITIVE_ENVELOPE = {"attack": 0.004, "decay": 0.0, "sustain": 1.0, "release": 0.05}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 2.0, "mod_depth": 2.5,
               "attack": 0.004, "release": 0.05}
MOTOR_DEFAULTS = {"rate_hz": 6.9, "depth": 0.30, "rate_range_hz": (0.7, 7.0),
                  "doppler_cents": 6.0, "accel_s": 1.0}
REVERB_TAIL = 1.8
EQ_BODY = (200, -2.0); EQ_PRESENCE = (2500, 2.0); EQ_AIR = (8000, 1.0)
PAN = 0.0
```

**Nine drawbar footages (ratio vs 8' = 1.0):**

| Drawbar | 16' | 5 1/3' | 8' | 4' | 2 2/3' | 2' | 1 3/5' | 1 1/3' | 1' |
|---|---|---|---|---|---|---|---|---|---|
| Ratio | 0.5 | 1.5 | 1.0 | 2.0 | 3.0 | 4.0 | 5.0 | 6.0 | 8.0 |

`DRAWBAR_PRESETS` (levels 0-8, console order): `full` 888888888, `jazz` /
`perc` 888000000, `gospel` 888864000, `flute`/`bass` 808000000, `ska` 868400000.
`drawbar_harmonics(registration)` → `{ratio: level/8}`; for 888000000 that is
`{0.5: 1.0, 1.5: 1.0, 1.0: 1.0}`. `ADDITIVE_HARMONICS` holds engine-compatible
integer-partial banks (SoundWave.apply_overtones only sums 1x, 2x, 3x …).

`midi_to_freq(midi) = 440 * 2 ** ((midi-69)/12)`; C4 = 261.6 Hz, so 16' = 130.8 Hz,
4' = 523.3 Hz.

## 5. Timbre DNA, role, synthesis

- Sine partials only; no formants, no noise bed. The 1.5x quint drawbar is
  what makes 888000000 sound hollow/horn-like.
- Attack: 4-10 ms electrical rise + broadband 2-4 kHz **key click** (nine
  busbar contacts close a few ms apart). Percussion = one decaying 2nd/3rd
  harmonic, ~0.35 s.
- Decay: **none** while held (flat tonewheel output) — modelled as
  `sustain = 1.0`, no decay stage. Only percussion and room/Leslie tail decay.
- Leslie: 6.9 Hz tremolo (fast) / 0.7 Hz chorale, AM depth 0.30, ~6 cents
  Doppler, ~1 s spin-up.
- Roles: harmony, pad, comp, lead, bass (pedal), rhythm (stabs), drone, accent.
- Engines: **Additive** (primary, physical model) → PhaseModSynth (DX7-style,
  ratio 2.0 / depth 2.5) → ModalSynth (weakest; no organ preset in the stock
  bank `['marimba','bell','drum','string','plate','tube']`, 'plate' nearest).
- **Velocity quirk**: a real tonewheel key contact is binary — no velocity
  response. Keep MIDI velocity 70-100 as a mix-balance value; carry dynamics
  with drawbar changes / swell / density, not velocity.

## 6. Registration

`instrument_registry.py`:
- `_INSTRUMENT_MODULES["Keys.drawbar_organ.drawbar_organ"] = "drawbar_organ"`
- `DRAWBAR_ORGAN = ALL_INSTRUMENTS["drawbar_organ"]`
- `registry_table()` role row added (otherwise it defaults to
  "lead, harmony, accent")

### Registration proof — `python instrument_registry.py`

```
=== Drawbar Organ (Hammond tonewheel, GM16) ===
  DRAWBAR_ORGAN.midi_program = 16 (should be 16)
  by_name('drawbar organ') = <Instrument Drawbar Organ (family=Keys, program=16, range=24-89)>
  by_program(16) = <Instrument Drawbar Organ (family=Keys, program=16, range=24-89)>
  DRAWBAR_ORGAN.in_sweet_spot(67) = True
  DRAWBAR_ORGAN.in_sweet_spot(24) = False
  DRAWBAR_ORGAN.range_min = 24 DRAWBAR_ORGAN.range_max = 89
  DRAWBAR_ORGAN.stem_label = 'Drawbar_Organ'
```

### Full `registry_table()` printed by the same run

| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
| Brass | Brass Section | 61 | 36–96 | lead, accent, fanfare, counter, harmony, pad |
| Brass | French Horn | 60 | 41–84 | lead, countermelody, melody, harmony, accent |
| Brass | Muted Trumpet | 59 | 54–86 | lead, countermelody, accent, fanfare, ornament |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | Trumpet | 56 | 54–86 | lead, harmony, accent |
| Brass | Tuba | 58 | 26–72 | bass, counter, accent, harmony |
| Guitar | Acoustic Guitar (nylon) | 24 | 40–84 | lead, harmony, accent |
| Guitar | Acoustic Guitar (steel) | 25 | 40–86 | harmony, rhythm, strum, lead, melody, ornament, countermelody |
| Guitar | Electric Guitar (clean) | 27 | 28–84 | harmony, rhythm, strum, lead, melody, ornament, countermelody, accent |
| Guitar | Overdriven Guitar | 29 | 28–84 | lead, harmony, accent |
| Keys | Accordion | 21 | 36–96 | harmony, melody, bass, rhythm, ornament |
| Keys | Acoustic Grand Piano | 1 | 21–108 | lead, harmony, accent |
| Keys | Celesta | 8 | 48–108 | lead, melody, ornament, arpeggio, countermelody, accent |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Clavi | 7 | 29–89 | lead, harmony, accent |
| Keys | Drawbar Organ | 16 | 24–89 | harmony, pad, comp, lead, bass, rhythm, drone, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Keys | Electric Piano 1 | 4 | 36–96 | harmony, melody, bass, accent, color |
| Keys | Electric Piano 2 | 5 | 36–96 | harmony, melody, bass, accent, color |
| Keys | Harpsichord | 6 | 29–89 | harmony, continuo, melody, ornament, countermelody, accent |
| Keys | Reed Organ | 20 | 36–96 | harmony, pad, melody, drone, ornament |
| Percussion | Drum Kit | 0 | - | rhythm, groove, accent |
| Percussion | Glockenspiel | 9 | 79–108 | lead, melody, ornament, accent, countermelody |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Music Box | 10 | 60–96 | lead, harmony, accent |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Percussion | Tubular Bells | 14 | 60–78 | lead, harmony, accent |
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
| Percussion | Xylophone | 13 | 53–89 | lead, melody, ornament, accent, countermelody |
| Strings | Cello | 42 | 36–84 | bass, counter, accent, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, counter, accent, harmony |
| Strings | Orchestral Harp | 46 | 24–103 | harmony, arpeggio, glissando, melody, countermelody, accent |
| Strings | Pizzicato Strings | 45 | 36–96 | rhythm, ostinato, bass, accompaniment, countermelody, accent |
| Strings | String Ensemble 1 | 48 | 28–96 | harmony, pad, melody, countermelody, accent |
| Strings | Viola | 41 | 48–91 | lead, harmony, accent |
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Synth | Pad 1 (new age) | 88 | 36–96 | pad, harmony, texture, drone, accent |
| Vocal | Didgeridoo | 20 | 24–55 | lead, harmony, accent |
| Vocal | Human Voice | 53 | 48–84 | lead, melody, countermelody |
| Vocal | Jaw Harp | 106 | 36–74 | lead, harmony, accent |
| Vocal | Kazoo | 59 | 50–86 | lead, harmony, accent |
| Vocal | Singing Saw | 81 | 55–91 | lead, harmony, accent |
| Vocal | Talkbox | 80 | 45–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, countermelody, accent, harmony |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
| Woodwind | Baritone Saxophone | 67 | 36–80 | bass, harmony, accent, lead, countermelody |
| Woodwind | Bassoon | 70 | 34–88 | lead, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, harmony, accent |
| Woodwind | English Horn | 69 | 50–85 | lead, countermelody, melody, harmony, accent |
| Woodwind | Flute | 73 | 60–96 | lead, harmony, accent |
| Woodwind | Harmonica | 22 | 48–96 | lead, harmony, accent |
| Woodwind | Oboe | 68 | 52–92 | lead, harmony, accent |
| Woodwind | Ocarina | 79 | 55–96 | lead, harmony, accent |
| Woodwind | Piccolo | 72 | 72–108 | lead, melody, ornament, accent, countermelody |
| Woodwind | Recorder | 74 | 60–100 | lead, melody, ornament, countermelody, accent |
| Woodwind | Soprano Saxophone | 64 | 54–89 | lead, countermelody, ornament, accent |
| Woodwind | Tenor Saxophone | 66 | 44–88 | lead, countermelody, accent, harmony |
| Woodwind | Whistle | 78 | 62–93 | lead, harmony, accent |
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Pan Flute | 75 | 55–100 | lead, harmony, accent |
| World | Shakuhachi | 77 | 55–100 | lead, melody, ornament, drone, accent |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
| World | Taiko Drum | 116 | 36–67 | accent, rhythm, drone, ornament |

## 7. Verification results (`_test/verify_drawbar_organ.py`)

```
Drawbar Organ: program=16 gm='Drawbar Organ' stem='Drawbar_Organ' range=24-89 sweet=(55, 79) solo=(48, 84)
Drawbar Organ: zones={'pedal': (24, 48), 'lower': (29, 65), 'upper': (48, 89)}
Drawbar Organ: art=['sustain', 'legato', 'staccato', 'percussion', 'key_click', 'accent', 'palm_smear', 'bass_pedal'] synth=additive
Drawbar Organ: reverb=1.8s eq=(200, -2.0),(2500, 2.0),(8000, 1.0) pan=0.0
Drawbar Organ: octaves 16'=130.8Hz 8'=261.6Hz 4'=523.3Hz (C4 registration)

registry_table row: ['| Keys | Drawbar Organ | 16 | 24–89 | harmony, pad, comp, lead, bass, rhythm, drone, accent |']

Zero-drift: True (OK)
MIDI: _test/drawbar_organ_test.mid (109 bytes)
WAV (solo): _test/drawbar_organ_test.wav (737068 bytes, 720 KB)
Spectral check: 4-8kHz buzz energy = 5.8% (OK)

SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
  GM_PROGRAMS[16] = 'Drawbar Organ'  STEM_LABEL = 'Drawbar_Organ'
  SF2 preset 16 -> 'DrawbarOrgan' (cosmetic only)

Stems (1): ['track00_Drawbar_Organ.wav']

Additive (jazz bank) C4: peak=3377 early/late RMS ratio=0.989
Drawbar 888000000 partials: 8'=2082 16'=1664 5 1/3'(quint)=2035
Motor: rate=6.9Hz depth=0.3 sidebands/f0 = 0.084 up, 0.083 down

ALL CHECKS PASSED
```

Checks that passed:

1. Constants imported **through the registry** (`by_name`, `by_program`
   identity, sweet-spot/in-range gates, family = Keys).
2. `registry_table()` contains `| Keys | Drawbar Organ | 16 | 24–89 | …`.
3. UnitMatrixComposer 1 bar / 1 section / **1 voice (solo)** — gospel comp
   line G3-G5 with staccato stabs and one accented sustain; `validate()` →
   `True (OK)` (zero-drift).
4. MIDI exported, 109 bytes > 40.
5. WAV rendered with `discover_soundfont()` (FluidR3_GM, never hardcoded
   TimGM6mb), 737,068 bytes / 720 KB > 40.
6. Spectral buzz 4-8 kHz = **5.8%** (< 20% gate) — no comb-filtering; no
   unison doubling (single voice).
7. RenderPipeline stem on disk: `track00_Drawbar_Organ.wav` > 40 bytes.
8. SF2 preset name read from the phdr chunk = `DrawbarOrgan` vs pipeline
   `Drawbar Organ` — cosmetic only.
9. Additive engine: jazz bank normalized, C4 peak 3377, late/early RMS
   ratio 0.989 → the tone is FLAT while held (no decay), as a tonewheel
   should be.
10. True drawbar ratios: 0.5x and 1.5x partials both present at > 50% of the
    1x peak (custom additive sum, since `apply_overtones` is integer-only).
11. Leslie AM: sidebands at f0 ± 6.9 Hz at 8.4% / 8.3% of the carrier.

## 8. Quirks and notes found

- **SF2 internal name**: FluidR3 bank-0 preset 16 = `DrawbarOrgan` (no space).
  Pipeline/GM label is "Drawbar Organ". Cosmetic, no routing impact. NOTE:
  bank-1 preset 16 is `Detuned Organ 1` — always filter on `bank == 0` when
  reading phdr, or you get the wrong preset name.
- **Velocity is not expressive** on a real tonewheel organ (binary contact).
  Use velocity for balance (70-100), drawbars/swell for dynamics.
- **`apply_overtones()` is integer-partial only** — it cannot express the
  0.5x sub-octave (16') or 1.5x quint (5 1/3'). Use `drawbar_harmonics()`
  for a true additive render; `ADDITIVE_HARMONICS` is the near-equivalent
  integer bank for the stock engine API.
- **ADSR length proportions** in `SoundWave.get_adsr_weights` must sum to
  1.0 (proportions, not seconds) — organ uses [0.02, 0, 0.94, 0.04].
- **Motor test method differs from vibraphone**: a steady (non-decaying)
  tone produces no AM energy in an envelope-follower spectrum; detect AM as
  sidebands at f0 ± rate instead.
- **Stem index**: with one voice the pipeline names the file
  `track00_Drawbar_Organ.wav` (track_idx starts at 0 for the first voice
  track, tempo track skipped).
- Drive-by doc fix: `registry.md` table row "Flute | 74" was stale from the
  2026-10-16 GM73/74 swap — corrected to 73.
