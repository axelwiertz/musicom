# REPORT — String Ensemble 2 (GM49) added 2026-11-11

Nightly instrument research job (layer-aligned). New instrument added to the
Instruments reference library and **registered** in `instrument_registry.py`.

## Instrument

- **Name**: String Ensemble 2 (GM49)
- **Family**: Strings (ninth entry; sibling of String Ensemble 1 GM48)
- **Identity**: the SLOW-ATTACK string ensemble — the analog "string
  machine" (ARP Solina String Ensemble 1974, Mellotron string tapes, Elka
  Rhapsody 610, Crumar Performer, Logan String Melody, Roland RS-202): a
  divide-down keyboard whose every note fires 3 detuned saw sub-oscillators
  through a band-limiting filter, a slow attack swell and a chorus
  "ensemble" effect. FluidR3 preset 49 = **"Slow Strings"** — the SF2 name
  IS the character. The SLOW sibling of GM48 String Ensemble 1 (bowed
  orchestral section, fast attack).
- **Selection rationale**: named as remaining sibling candidate in the
  three latest registry.md changelog entries (2026-11-07/09/10). GM49 was
  collision-free — `by_program(49)` had no owner, stem `String_Ensemble_2`
  unclaimed.

## Program / stems / SF2

- MIDI program: **49** (GM1 "String Ensemble 2"; melodic channel 0–9 —
  channel 9 would trigger the drum-kit map)
- RenderPipeline stem: GM_PROGRAMS[49] = "String Ensemble 2" →
  `trackXX_String_Ensemble_2.wav` — **exact match, no quirk**
- FluidR3 preset 49 = "Slow Strings" (verified from phdr chunk via
  `discover_soundfont()` → `/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2`);
  SF2 character name vs GM label — cosmetic only, no routing impact
- Enum note: `MidiInstrument.STRING_ENSEMBLE = 49` — the legacy enum's
  string-ensemble constant happens to equal GM49 (Slow Strings), NOT GM48.
  Registry is the full KB.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full | 28–96 | C1–C7 | idiomatic writing band (empirical: audible 12–96, silent 108+) |
| Low | 28–47 | C1–B2 | divide-down rumble — roots/drone, write sparingly |
| Mid | 48–71 | C3–B4 | primary chord-pad body |
| High | 72–96 | C5–C7 | ensemble top — cutting but warm |

- **Sweet spot**: 60–84 (C4–C6); **solo range**: 53–89 (F3–A6)
- Empirical FluidR3 sweep (RMS, vel 90, notes 24–108 step 12): audible
  **8/8 from 24 to 96** — RMS 932–1817, essentially FLAT (no rolloff, no
  gaps); **silent at 108** (0.99 vs ~1200 median = 0.06% — patch ceiling).
  Full-keyboard patch, SF2 never clips a composition.
- Real instrument: Solina = 49-key divide-down ≈ C2–C6 (36–84); below C2
  the machine is rumble — keep chord roots at C3+ in dense writing.

## Role

pad, harmony, texture, melody, countermelody, accent — slow-attack sustained
chords (ballad/lofi/synthwave/ambient bed), dense 4–6 note voicings
idiomatic, whole-bar swells, warm high-register melody — NOT a bass voice,
NOT a rhythm voice.

## Synthesis engine

1. **StringEnsembleVoice** (primary, `sound/synthesis/string_ensemble.py`)
   — dedicated divide-down string-machine model (3 detuned saws at 8'/4'/2',
   drift, A/R, Streichfett-style 3-tap ensemble chorus).
   `STRING_ENSEMBLE_DEFAULTS`: n_voices 3, octave_mix (0.6, 0.35, 0.15),
   detune_cents 8.0, drift_rate 0.4, attack_s 0.8 (slow swell = identity),
   release_s 1.5, layer_mix 0.2, flavour 0.35.
2. **Polysynth** (secondary) — 3 detuned SAWS ±8c, low-pass 2200 Hz,
   resonance 0.3, env attack 0.8 / sustain 0.85 / release 0.8.
3. **Additive** (tertiary) — `slow_strings` stack [1.0, 0.85, 0.62, 0.42,
   0.28, 0.18, 0.11], attack 0.8, detune ±0.010, stack 3, decay_S 1e-4.
4. **PhaseModSynth** (quaternary) — saw carrier, ratio 1.0, depth 1.8.

## Constants (String_Ensemble_2.py)

```python
MIDI_PROGRAM = 49
GM_NAME = "String Ensemble 2"
STEM_LABEL = "String_Ensemble_2"
RANGE_MIN = 28; RANGE_MAX = 96
SOLO_RANGE = (53, 89); SWEET_SPOT = (60, 84)
ZONES = {"low": (28, 47), "mid": (48, 71), "high": (72, 96)}
ARTICULATIONS = {sustain:(72,1.0), legato:(70,1.0), swell:(82,1.0),
                 staccato:(66,0.25), marcato:(85,0.85), drone:(62,1.0),
                 accent:(88,0.9), bloom:(68,1.25)}
SYNTHESIS = "string_ensemble"
STRING_ENSEMBLE_DEFAULTS = {instrument, n_voices 3, octave_mix (0.6,0.35,0.15),
    detune_cents 8.0, drift_rate 0.4, attack_s 0.8, release_s 1.5,
    layer_mix 0.2, flavour 0.35}
POLYSYNTH_DEFAULTS = {osc1/2/3 saw, ±8c, osc3_level 0.8, cutoff 2200,
    res 0.3, env 0.8/0.3/0.85/0.8, unison 3}
ADDITIVE_HARMONICS = {"slow_strings": [1.0, 0.85, 0.62, 0.42, 0.28, 0.18, 0.11]}
SYNTHESIS_DEFAULTS = {instrument, attack 0.8, detune 0.01, stack 3,
    release 0.8, sustain_level 0.9, decay_S 1e-4}
FM_DEFAULTS = {saw carrier, ratio 1.0, depth 1.8, attack 0.5, release 0.6}
REVERB_TAIL = 2.8; EQ_BODY = (300, -2.0); EQ_PRESENCE = (2800, 2.0)
EQ_AIR = (8000, 1.5); PAN = 0.0
midi_to_freq(midi) = 440 * 2 ** ((midi - 69) / 12)
```

## Registration proof (registry run)

```
| Strings | String Ensemble 2 | 49 | 28–96 | pad, harmony, texture, melody, countermelody, accent |
  by_name('string ensemble 2') = <Instrument String Ensemble 2 (family=Strings, program=49, range=28-96)>
  by_name('String Ensemble 2') = <Instrument String Ensemble 2 (family=Strings, program=49, range=28-96)>
  by_program(49) = <Instrument String Ensemble 2 (family=Strings, program=49, range=28-96)>
  by_program(48) = <Instrument String Ensemble 1 (family=Strings, program=48, range=28-96)> (distinct)
  STRING_ENSEMBLE_2.in_sweet_spot(72) = True
  STRING_ENSEMBLE_2.in_sweet_spot(24) = False
  STRING_ENSEMBLE_2.stem_label = 'String_Ensemble_2'
  STRING_ENSEMBLE_2.synthesis = 'string_ensemble'
  STRING_ENSEMBLE_2.synthesis_defaults = {...}
  STRING_ENSEMBLE_2.string_ensemble_defaults = {...}
```

Registration changes in `instrument_registry.py`:
- `_INSTRUMENT_MODULES`: `"Strings.string_ensemble_2.string_ensemble_2":
  "string_ensemble_2"`
- `_FIELDS`: extended with `string_ensemble_defaults`
- Convenience constant: `STRING_ENSEMBLE_2 = ALL_INSTRUMENTS["string_ensemble_2"]`
- `registry_table()` role row: `pad, harmony, texture, melody,
  countermelody, accent`
- Verification block: `=== String Ensemble 2 (Slow Strings, GM49) ===`

Full registry output: `_test/registry_out_string_ensemble_2.txt` (exit 0).

## Verification results (verify_string_ensemble_2.py — ALL CHECKS PASSED)

| Check | Result |
|---|---|
| Zero-drift (1 bar, 1 section, 100 bpm; String Ensemble 2 SOLO ch0 + drums ch9) | **True (OK)** |
| MIDI size | 177 bytes (> 40 ✓) |
| Solo WAV (FluidR3 via discover_soundfont) | 1,693,996 bytes (> 40 ✓) |
| Spectral 4–8 kHz buzz | **0.8%** (clean single voice, no comb-filtering) |
| Stems on disk | `track00_String_Ensemble_2.wav` (1,693,996 B) + `track01_Drums.wav` (849,708 B) |
| Stem label | GM_PROGRAMS[49] = "String Ensemble 2" → `String_Ensemble_2` ✓ |
| SF2 preset 49 | "Slow Strings" ✓ |
| StringEnsembleVoice smoke (Cmaj 2.5 s) | peak 0.900, onset_rms 0.026 → late_rms 0.135 (**5.2× slow swell**, no collapse) |
| Polysynth smoke (A3) | peak 1.107, sustain_rms 0.192 vs release 0.080, hold_ratio **2.39** (no collapse) |
| Additive smoke | late env max **0.883** (decay_S 1e-4 pad-hold recipe, gate ≥ 0.45 ✓) |
| Pitch sweep | 24–96 audible 8/8, flat 932–1817 RMS, silent at 108 (0.06% of median) |

## Quirks found

1. **SF2 name = "Slow Strings"** vs GM label "String Ensemble 2" — the
   FluidR3 preset uses the character name. Cosmetic only (stems are
   labelled from GM_PROGRAMS), no routing impact. Documented in
   instrument.md + registry.md quirks table.
2. **`MidiInstrument.STRING_ENSEMBLE = 49`** — the legacy enum's value
   equals GM49 (Slow Strings), NOT GM48 String Ensemble 1; legacy code
   using the enum already triggered the Slow Strings patch. Registry
   (GM48/GM49 keys) is the truth.
3. **Patch ceiling at 108 (C8)** — silent above C7=96; never write above
   96. (Sweep script's original absolute-0.01 assertion was too strict —
   fluidsynth's noise floor RMS is ~1; fixed to a fraction-of-median
   check: 0.9947/1200 ≈ 0.06%.)
4. **Divide-down low register** — below C2=36 the machine is rumble;
   keep chord roots at C3+ in dense writing (real Solina is 49 keys ≈
   C2–C6).
5. **Slow attack** — the 0.8 s swell IS the identity; never ask this
   patch for a pluck; staccato "blips" at 1/4 are the fastest gesture;
   hold chords ≥ 1.5–2 s or the attack never speaks.
6. **No unison doubling** (2026-09-01 comb-filter rule) — pad + unison
   bowed strings on the same pitches = beating wash; octaves or a low
   bass below are fine; layers beautifully UNDER a lead.

## Files

- `Strings/string_ensemble_2/instrument.md` — full research reference
- `Strings/string_ensemble_2/string_ensemble_2.py` — constants
- `Strings/string_ensemble_2/REPORT.md` — this report
- `_test/verify_string_ensemble_2.py` — end-to-end verification script
- `_test/verify_string_ensemble_2_out.txt` — its output (ALL CHECKS PASSED)
- `_test/registry_out_string_ensemble_2.txt` — registry run output
- `_test/string_ensemble_2_test.mid` / `.wav` — solo-render artifacts
- `_test/stems_string_ensemble_2/` — rendered stems
- `_test/sweep_string_ensemble_2.py` — empirical pitch sweep

## Docs updated

- `instrument_registry.py` — module map, _FIELDS, constant, role row,
  verification block
- `registry.md` — Registry table row, stem-label quirks row (49), dated
  changelog entry (2026-11-11)

Remaining sibling candidates for future nights: GM31 "Guitar harmonics",
GM63 "Synth Brass 2", GM50/51 "Synth Strings 1/2".
