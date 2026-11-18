# REPORT — Rock Organ (GM18)

**Nightly instrument research job — 2026-09-02 (layer-aligned run)**
**Instrument**: Rock Organ · `Keys/rock_organ/`
**Family**: Keys (overdriven tonewheel / transistor combo organ)
**Status**: registered, verified end-to-end, usable by composition jobs.

---

## 1. Instrument identity

| Field | Value |
|---|---|
| MIDI / GM program | **18** (GM1 0-based "Rock Organ", 19th entry) |
| GM name | `Rock Organ` |
| Channel | melodic (not 10) |
| SoundFont | FluidR3_GM.sf2 bank 0 preset 18 = **"Rock Organ"** (verified from `phdr`) |
| Stem label | `Rock_Organ` → `trackXX_Rock_Organ.wav` (no quirk) |
| Registry key | `rock_organ` |
| Convenience constant | `ROCK_ORGAN` |

Identity: the *amplified* organ of rock — Jon Lord (Deep Purple, Hiwatt +
Marshall stacks), Keith Emerson (L-100 through fuzz), Booker T. Jones ("Green
Onions", M3), Steve Winwood, Rick Wright, Gregg Allman, Jackie Mittoo
(ska/rocksteady). Deliberately distinct from GM16 Drawbar Organ (clean
jazz/gospel B-3): same additive tonewheel source, plus a tanh overdrive stage,
key-click percussion and a Leslie parked on FAST.

## 2. Range

| Zone | MIDI | Pitches | Use |
|---|---|---|---|
| Full | 36–96 | C2–C7 | 61-key manual (GM18 patch span) |
| Bass | 36–55 | C2–G3 | left-hand key bass, 16'+8' |
| Mid | 56–79 | G#3–G5 | comp + lead, full drawbars |
| High | 80–96 | G#5–C7 | 1' partial, screaming solos |

- `SOLO_RANGE = (48, 84)` C3–C6
- `SWEET_SPOT = (55, 79)` G3–G5

## 3. Articulations (velocity, duration_factor)

| Technique | Vel | Dur |
|---|---|---|
| sustain | 85 | 1.0 |
| stab | 94 | 0.22 |
| chop | 78 | 0.10 |
| percussion | 90 | 0.35 |
| key_click | 72 | 0.06 |
| accent | 100 | 0.85 |
| smear | 66 | 0.90 |
| swell | 96 | 1.0 |

Velocity is a **mix/attack** value — the tonewheel key contact is a binary
switch; dynamics come from drawbars, note density and the swell pedal.

## 4. Role

`lead, rhythm, harmony, comp, pad, bass, accent, drone`

- Lead: unison lines with guitar / organ solo
- Rhythm: backbeat stabs (rock), up-strokes (ska/reggae)
- Harmony/pad: sustained 3–4 note voicings, omit the 5th when driven
- Bass: left-hand key bass when no bass guitar
- Accent / drone: section markers, held root-fifth vamp

**No unison doubling**: never double identical sustained pitches with piano or
a second organ patch (comb-filter buzz, the 2026-09-01 bug).

## 5. Synthesis engine

**`additive`** — `sound/synthesis/additive.py` (`SoundWave`). The Hammond
tonewheel generator *is* additive synthesis (91 sine wheels, 9 drawbar levels).

- `ADDITIVE_HARMONICS` — 7 normalized integer-partial banks:
  `rock [1.00, 0.85, 0.75, 0.55, 0.40, 0.30, 0.15, 0.22]`,
  `scream`, `ska`, `booker`, `gospel`, `bass`, `ballad`.
  Extra 4x/6x/8x content vs the GM16 banks = the saturated bark.
- `ADDITIVE_ENVELOPE` = `{attack: 0.003, decay: 0.0, sustain: 1.0, release: 0.045}`
- `OVERDRIVE_DEFAULTS` = `{drive: 2.6, tone_hz: 2400, output_trim_db: -3.0, asymmetry: 0.15}`
- `MOTOR_DEFAULTS` (Leslie fast) = `{rate_hz: 6.9, depth: 0.34, rate_range_hz: (0.8, 7.0), doppler_cents: 7.0, accel_s: 0.8}`
- `FM_DEFAULTS` (PhaseModSynth fallback) = `{carrier_shape: sine, mod_freq_ratio: 3.0, mod_depth: 3.2, attack: 0.003, release: 0.05}`
- `DRAWBAR_FOOTAGES` (9 bars, console order) + `DRAWBAR_PRESETS`
  (`rock`, `scream`, `ska`, `booker`, `gospel`, `bass`, `ballad`) +
  `drawbar_harmonics()` (expresses the non-integer 16' 0.5x and 5 1/3' 1.5x bars)
- **Rejected**: Karplus-Strong (no string), ModalSynth (no struck resonator).

## 6. Production defaults

| Param | Value |
|---|---|
| `REVERB_TAIL` | 1.3 s (club/stage, not cathedral) |
| `EQ_BODY` | (250 Hz, −1.5 dB) |
| `EQ_PRESENCE` | (1800 Hz, +3.0 dB) |
| `EQ_AIR` | (7000 Hz, +1.5 dB) |
| `PAN` | 0.0 |
| `midi_to_freq` | `440 * 2**((m-69)/12)` (A4 = 440.0 Hz, C2 = 65.4, C4 = 261.6, C7 = 2093.0) |

## 7. Registration proof

`instrument_registry.py` changes:

```python
"Keys.rock_organ.rock_organ": "rock_organ",     # _INSTRUMENT_MODULES
ROCK_ORGAN = ALL_INSTRUMENTS["rock_organ"]      # convenience constant
elif low == "rock organ":                       # registry_table() role row
    role = "lead, rhythm, harmony, comp, pad, bass, accent, drone"
```

`registry_table()` (96 instruments now; excerpt):

```
| Keys | Drawbar Organ | 16 | 24–89 | harmony, pad, comp, lead, bass, rhythm, drone, accent |
| Keys | Rock Organ | 18 | 36–96 | lead, rhythm, harmony, comp, pad, bass, accent, drone |
```

Verification block printed by `python instrument_registry.py`:

```
=== Rock Organ (Keys, GM18) ===
  ROCK_ORGAN.midi_program = 18 (should be 18)
  by_name('rock organ') = <Instrument Rock Organ (family=Keys, program=18, range=36-96)>
  by_name('Rock Organ') = <Instrument Rock Organ (family=Keys, program=18, range=36-96)>
  by_program(18) = <Instrument Rock Organ (family=Keys, program=18, range=36-96)>
  by_program(16) = <Instrument Drawbar Organ (family=Keys, program=16, range=24-89)> (distinct: drawbar organ)
  ROCK_ORGAN.in_sweet_spot(67) = True
  ROCK_ORGAN.in_sweet_spot(30) = False
  ROCK_ORGAN.range_min = 36 ROCK_ORGAN.range_max = 96
  ROCK_ORGAN.solo_range = (48, 84)
  ROCK_ORGAN.stem_label = 'Rock_Organ'
  ROCK_ORGAN.synthesis = 'additive'
  ROCK_ORGAN.reverb_tail = 1.3 ROCK_ORGAN.pan = 0.0
  ROCK_ORGAN.motor_defaults = {'rate_hz': 6.9, 'depth': 0.34, 'rate_range_hz': (0.8, 7.0), 'doppler_cents': 7.0, 'accel_s': 0.8}
  ROCK_ORGAN.articulations = ['sustain', 'stab', 'chop', 'percussion', 'key_click', 'accent', 'smear', 'swell']
```

## 8. Verification results

Script: `_test/verify_rock_organ.py` (exports via **registry**, renders **SOLO**
— one voice, one track — through `discover_soundfont()`).

```
Registered: <Instrument Rock Organ (family=Keys, program=18, range=36-96)>
additive banks OK (7 registrations, normalized)
drawbar_harmonics(rock): {0.5: 1.0, 1.5: 1.0, 1.0: 1.0, 2.0: 0.75, 3.0: 0.5, 4.0: 0.25}
zero-drift: True (OK)
MIDI: _test/rock_organ_test.mid (84 bytes)
WAV (solo): _test/rock_organ_test.wav (743724 bytes)
spectral check: 4-8kHz buzz energy = 0.3% (OK)
soundfont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
GM_PROGRAMS[18] = 'Rock Organ'  (16: 'Drawbar Organ')
SF2 bank0 preset 18 = 'Rock Organ'
stems: ['track00_Rock_Organ.wav']
stem track00_Rock_Organ.wav: 743724 bytes
additive SoundWave rock: peak=213.5 (sample_count=44100)

ALL CHECKS PASSED
```

- Zero-drift: **PASS** (`validate()` → True / OK)
- MIDI: 84 bytes (> 40 ✓)
- WAV (solo, FluidR3): 743,724 bytes (> 40 ✓)
- Solo buzz energy 4–8 kHz: 0.3 % (no comb filtering — single voice only)
- RenderPipeline stem: `track00_Rock_Organ.wav`, 743,724 bytes ✓

## 9. Quirks found

1. **GM18 vs GM16 collision risk (by design)**: both are Hammond-family
   patches. Stems are separable (`Rock_Organ` vs `Drawbar_Organ`) but they
   sound alike — expected, not a routing bug. Use GM18 for driven rock/ska
   comping and solos, GM16 for clean jazz/gospel pads.
2. **SF2 preset 18 already contains Leslie-style movement.** Adding the
   external `MOTOR_DEFAULTS` on top of a FluidR3 render doubles the wobble —
   pick one (SF2 render → skip the motor stage; native additive → keep it).
3. **No velocity→brightness mapping** in FluidR3's organ presets: velocity is
   amplitude only. Write dynamics with density/register, not velocity curves.
4. **Hard key-off**: GM organ notes cut ~immediately; overlap note-ends a few
   ticks for legato.
5. **Pipeline-wide note-on behaviour** (documented with Melodic Tom,
   2026-11-15): every second note-on *event* in a track can render 30–50 dB
   down in this FluidSynth binary. Masked on sustained organ tones, but
   alternate staccato stabs may drop — keep stabs in separate units/sections
   or accept the accent pattern.
6. **Organs do not blend with strings in the same octave** (organ masks bow
   noise) — place the organ above or below the pad.

## 10. Artifacts

| File | Purpose |
|---|---|
| `Keys/rock_organ/instrument.md` | full research reference (YAML frontmatter + sections) |
| `Keys/rock_organ/rock_organ.py` | importable constants |
| `Keys/rock_organ/REPORT.md` | this report |
| `_test/verify_rock_organ.py` | registry-path verification (solo render) |
| `_test/rock_organ_test.mid` | 84-byte MIDI export |
| `_test/rock_organ_test.wav` | 743,724-byte solo FluidR3 render |
| `_test/stems_rock_organ/track00_Rock_Organ.wav` | RenderPipeline stem |
| `registry.md` | table row + stem-label row + 2026-09-02 changelog |
| `instrument_registry.py` | module map, `ROCK_ORGAN` constant, table role, verification block |

Remaining unused GM programs after this run: 2 Electric Grand Piano,
17 Percussive Organ, 37 Slap Bass 2, 50/51 Synth Strings 1/2,
63 Synth Brass 2, 76 Blown Bottle, 83–87 Leads 4–8, 90–103 Pads/FX,
112 Tinkle Bell, 118 Synth Drum, 119 Reverse Cymbal, 120–127 SFX.
