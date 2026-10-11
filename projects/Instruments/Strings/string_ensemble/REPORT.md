# REPORT — String Ensemble 1 (GM48)

Nightly instrument research job, layer-aligned. Run date: 2026-10-11.

## Instrument

| Field | Value |
|---|---|
| Name | String Ensemble 1 |
| Family | Strings |
| GM program | **48** (GM1 String Ensemble 1) |
| Pipeline label | GM_PROGRAMS[48] = "String Ensemble 1" → stem `trackXX_String_Ensemble_1.wav` |
| FluidR3 preset | 48 = "Strings" (one-word SF2 spelling — cosmetic only, **no quirk**) |
| Range | 28–96 (E1–C7), empirical sweep: audible 24–96 (13/13), SILENT at 102+ |
| Sweet spot | 60–84 (C4–C6) |
| Solo range | 53–89 (F3–A6) |
| Role | harmony, pad, melody, countermelody, accent — the **Pad** voice |
| Synthesis | **additive** (primary), bowed (single-string alt), phase_mod (string machine), modal (pizz) |

**Why this instrument**: orchestration.md's Role table has listed
"Pad → Strings (sustained)" and "Harmony → Strings (section)" since the
beginning — but the KB had **no sustained-section pad**: the Strings family
was solo bowed voices (violin/viola/cello/double_bass/fiddle) + the plucked
section (pizzicato_strings). String Ensemble 1 (GM48) is the standard GM
sustained-section patch and fills that exact gap.

## Files written

- `Strings/string_ensemble/instrument.md` — full research reference
- `Strings/string_ensemble/string_ensemble.py` — importable constants
- `_test/verify_string_ensemble.py` — end-to-end verification (SOLO render)
- `_test/_sweep_gm48.py` — empirical FluidR3 pitch sweep (kept for audit)
- Registration: `instrument_registry.py` (`_INSTRUMENT_MODULES`,
  `STRING_ENSEMBLE` constant, registry_table role branch, verification lines)
- `registry.md`: changelog entry + Registry table row + stem-quirk table row

## Constants (string_ensemble.py)

```python
MIDI_PROGRAM = 48
GM_NAME = "String Ensemble 1"
STEM_LABEL = "String_Ensemble_1"
RANGE_MIN = 28; RANGE_MAX = 96
SOLO_RANGE = (53, 89); SWEET_SPOT = (60, 84)
ZONES = {"low": (28, 47), "mid": (48, 71), "high": (72, 96)}
ARTICULATIONS = sustain(78,1.0) legato(74,1.0) marcato(88,0.8) staccato(66,0.25)
                spiccato(72,0.125) tremolo(70,0.06) sforzando(95,0.9) accent(92,0.9)
SYNTHESIS = "additive"
ADDITIVE_HARMONICS = {"section_full": [1.0,0.9,0.7,0.5,0.35,0.25,0.18],
                      "section_sul": [1.0,0.6,0.4,0.25,0.15,0.1,0.05]}
SYNTHESIS_DEFAULTS = {"instrument":"string_ensemble","attack":0.35,"detune":0.006,
                      "stack":3,"release":0.4}
BOWED_DEFAULTS = {"bow_velocity":0.2,"bow_force":1.5,"bow_position":0.15,"noise_level":0.01}
FM_DEFAULTS = {"carrier_shape":"saw","mod_freq_ratio":1.0,"mod_depth":1.8,
               "attack":0.05,"release":0.3}
REVERB_TAIL = 2.6   # longest in Strings family
EQ_BODY = (250, -2.5); EQ_PRESENCE = (3200, 2.0); EQ_AIR = (8500, 1.5)
PAN = 0.0
```

## Registration proof

`instrument_registry.py` run (2026-10-11) — new row present:

```
| Strings | String Ensemble 1 | 48 | 28–96 | harmony, pad, melody, countermelody, accent |

=== String Ensemble 1 (GM48) ===
  STRING_ENSEMBLE.midi_program = 48 (should be 48)
  by_name('string ensemble') = <Instrument String Ensemble 1 (family=Strings, program=48, range=28-96)>
  by_name('string ensemble 1') = <Instrument String Ensemble 1 (family=Strings, program=48, range=28-96)>
  by_program(48) = <Instrument String Ensemble 1 (family=Strings, program=48, range=28-96)>
  STRING_ENSEMBLE.in_sweet_spot(72) = True
  STRING_ENSEMBLE.in_sweet_spot(20) = False
  STRING_ENSEMBLE.range_min = 28 STRING_ENSEMBLE.range_max = 96
  STRING_ENSEMBLE.stem_label = 'String_Ensemble_1'
```

Full `registry_table()` prints all ~62 instruments incl. the new row (see
verified run in `instrument_registry.py` __main__ output).

## Verification results (verify_string_ensemble.py)

| Check | Result |
|---|---|
| Registry import (`by_name`, `by_program`) | ✅ both resolve to String Ensemble 1 |
| Zero-drift validate | ✅ `True (OK)` — chord unit ends flush at BAR |
| MIDI export | ✅ 75 bytes (> 40) |
| FluidSynth render (discover_soundfont → FluidR3_GM.sf2) | ✅ WAV 1,040,428 bytes (> 40) |
| Spectral buzz check (SOLO render, 4–8 kHz) | ✅ 1.4% (≤ 20% gate, no comb-filtering) |
| Stem label vs pipeline GM_PROGRAMS[48] | ✅ "String Ensemble 1" → STEM_LABEL "String_Ensemble_1" |
| SF2 preset 48 phdr | ✅ "Strings" |
| Additive pad smoke (late 1.0–1.5 s rms/peak) | ✅ 0.295 — pad sustains, no collapse |
| Full pytest suite | ✅ 693 passed, 1 skipped (0 failures) |

Render was **SOLO only** (one voice, one track — the String Ensemble playing
a sustained C4-E4-G4-C5 chord). No second melodic patch on the same pitches:
no unison doubling, no comb-filtering.

## Empirical FluidR3 pitch sweep (preset 48)

Notes 24–108 step 6, single held note, RMS 0.2–0.5 s window:

```
 24 0.048  30 0.063  36 0.059  42 0.053  48 0.052  54 0.068
 60 0.062  66 0.065  72 0.089  78 0.084  84 0.072  90 0.085  96 0.079
102 SILENT (0.00003)  108 SILENT (0.00003)
```

Audible 13/13 across 24–96, no gaps, **hard patch ceiling at 102** — never
write above C7=96. This grounds RANGE_MAX=96 (like pizzicato's 36–96 which
was also empirically capped).

## Quirks found

1. **Additive engine bug FIXED** (`sound/synthesis/additive.py`,
   `get_adsr_weights`): the tail-fill block computed
   `tail = int(sr*duration - weights.shape[0])` against the **pre-repeat**
   envelope (`weights`, len ≈ `intervals` ≈ 3662 for a 2 s C4) but then
   concat'd that SAME pre-repeat array + a near-zero ramp into
   `self.weights` — so the `np.repeat` result (len 43932) was **discarded**
   and every note collapsed to ~1e-38 after ~0.17 s **regardless of
   `sustain_level`**. The organ entry (2026-08-31) flagged the
   smoothing-discard but verified sustain only via onset peak (2873) with
   the wrong array, missing the collapse. Fix: compute `tail` from
   `self.weights.shape[0]` and concat the repeated envelope with a linear
   release ramp (`self.weights[-1] * np.linspace(1, 0, tail + 1)[1:]`).
   Post-fix verification: organ-style params sustain at 1.0 for the full
   2.0 s; string-pad params hold late-window ratio 0.295. Full test suite
   green after the fix (693 passed, 1 skipped) — no golden regressions.
2. **`MidiInstrument.STRING_ENSEMBLE = 49` is 1-indexed legacy** — GM49 is
   actually String Ensemble 2 (FluidR3 "Slow Strings"). Same off-by-one
   class as CHURCH_ORGAN=20→19, TRUMPET=57→56. Use raw program 48.
3. **`apply_overtones` factor-sum assertion**: the harmonic factor list must
   sum to 1.0 (`abs(1 - sum(factor)) < 1e-8`). Human-readable ADDITIVE_
   HARMONICS stacks (sum > 1) must be normalized before use — same quirk
   organ documented.
4. **Stem label clean**: GM_PROGRAMS[48] = "String Ensemble 1" → sanitized
   `String_Ensemble_1` → `trackXX_String_Ensemble_1.wav`; FluidR3 preset 48
   is one-word "Strings" (cosmetic). No routing quirk (unlike 74→Recorder,
   109→Bag_pipe, 111→Shanai).
5. **Channel quirk**: melodic channel (0–9) with program 48 — channel 9
   would trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0
   fallback label (timpani/pizzicato lesson).

## Notes for composition jobs

- The section **IS** plurality: write full chords (3–5 notes) freely — this
  is a pad, not a line. Idiomatic doubling is **octaves** (violin + cello
  8va), NOT unison with another melodic patch.
- Slow attack (0.35 s) is the identity — don't fight it with staccato
  unless you want marcato/staccato articulations.
- Velocities 75–90 for pad duty; sforzando 90–100 for cinematic hits.
- REVERB_TAIL 2.6 s hall — the longest in the Strings family; keep the
  8.5 kHz shelf gentle (a wall of 9k+ shimmer is an artifact).
- Never write above C7=96 (patch ceiling, empirically silent at 102+).

## Verification artifacts

- MIDI: `/opt/data/projects/Instruments/_test/string_ensemble_test.mid` (75 B)
- WAV: `/opt/data/projects/Instruments/_test/string_ensemble_test.wav` (1.04 MB)
- Sweep: `_test/_sweep_gm48.py`
- Engine fix: `sound/synthesis/additive.py` `get_adsr_weights` tail block