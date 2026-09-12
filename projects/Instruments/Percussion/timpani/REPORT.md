# REPORT — Timpani (GM47) added 2026-09-12

## Instrument

- **Name**: Timpani (kettledrums / "timps") — hemispherical vessel drums, a
  membrane head over a copper bowl, foot-pedal tuned, struck with felt sticks
- **Family**: Percussion (pitched) — fourth entry after Drum Kit, Marimba,
  Steel Drums
- **MIDI program**: 47 (GM1 "Timpani", bank 0)
- **GM name**: "Timpani" (matches GM spec, karaoke/GM2 spec, pipeline, and
  SoundFont)
- **Stem label**: `trackXX_Timpani.wav` (GM_PROGRAMS[47] = "Timpani" — matches
  exactly, **no quirk**)
- **Channel**: melodic 0–9 — a timpano is PITCHED; channel 9 would swap in the
  drum-kit map and mislabel the stem `Acoustic_Grand_Piano`

### Why this pick

Next in the documented roadmap (see `Percussion/marimba/REPORT.md` "Next
candidates"): *"Percussion: Vibraphone (GM 11), Timpani (GM 47)"*. Timpani is
the highest-value remaining item because it is the only instrument already
referenced by the orchestration layer in two places with no KB entry behind it:

- `orchestration.md` role table: **Accent → "Brass, Crash, Timpani"**
- `orchestration.md` classical preset: **"strings + woodwind + brass +
  timpani, full orchestration"**
- `orchestrator.py` `ROLE_PROFILES["accent"]["secondary"]` already lists
  `"Timpani"`

Candidate ground truth (checked before writing, `_test/probe_candidates.py`
line for GM47, re-verified live this run): pipeline label `Timpani`, FluidR3
preset `Timpani` — exact match on both, no cosmetic suffix.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–65 | C2–F4 | 32-inch low drum → piccolo-timpano ceiling |
| Sweet spot | 41–55 | F2–G3 | fullest tone, clearest pitch, best roll projection |
| Solo range | 38–57 | D2–A3 | the standard four-drum set (majority of the repertoire) |
| Low | 36–47 | C2–B2 | 32/29-inch booms — deep, slow roll rumble |
| Mid | 48–57 | C3–A3 | 26/23-inch drums — classic tuning/roll/melodic zone |
| High | 58–65 | B3–F4 | piccolo timpano — thin, hollow, dry; accents/effects |

Grounded facts (Wikipedia `Timpani`, rev 1374429527, fetched this run):

- standard four-drum console (≈81/74/66/58 cm): range **D2–A3**, "a great
  majority of the orchestral repertoire can be played using these four drums"
- a 33-inch drum reaches **C2**; sizes run 84 cm down to *piccoli timpani* of
  ≤30 cm
- **each drum covers about a perfect fifth** (7 semitones) — hence pedal
  re-tuning between pieces
- Stravinsky writes B3 for a *piccolo timpano* in *The Rite of Spring*;
  Milhaud requires F#4 in *La création du monde* → documented ceiling 65 (F4),
  full span to 66 accepted
- "timpanists do not use multiple bounce rolls like those played on the snare
  drum, as the soft nature of timpani sticks causes the rebound to be reduced"
- "Since timpani have a long sustain, *muffling* or *damping* is an inherent
  part of playing" — the longest-ringing drum in the set

Empirical FluidR3 pitch sweep (`_test/sweep_timpani.py`, RMS, notes
24–84): **15/15 notes audible, no gaps** — the SF2 patch never clips a
composition. Range 36–65 is the real-instrument span; the sweep proves the
patch is audible well beyond it (bagpipe/steel-drums precedent).

## Role

- **Accent / punctuation** (the orchestra's punctuation section — hits,
  sforzandi, section-boundary impacts)
- **Rhythm** (pedal-point pulse under tutti; the roll as a sustained low layer)
- **Bass support** (doubles brass/string bass roots; tuned C2–G2 anchoring)
- **Drone / pedal** (continuous roll on tonic or dominant — Haydn, Wagner,
  film-score tension)
- NOT a melody voice at speed (single tuned drums; fast lines are extended
  technique or multi-player)
- NOT a harmony voice (double stops max two drums; Berlioz's *Requiem* needs
  ten timpanists for fully voiced chords)

## Synthesis engine (musicom)

- **Primary**: **ModalSynth** (`sound/synthesis/modal.py`) — a timpano is a
  struck membrane, i.e. an impulse-excited resonator bank. Exact custom bank
  `TIMPANI_MODES` in `timpani.py`: the ideal circular-membrane Bessel ratios
  **1 : 1.594 : 2.136 : 2.296 : 2.653**, pulled toward
  **1 : 1.5 : 2.1 : 2.3 : 2.65** by bowl + air loading — the timpano's
  "definite pitch with a hollow roar". Decay rates **0.9–3.0** (LOW / slow):
  vs marimba's 8–20 (fast). Modes referenced to A4=440; scale by played note.
- **MODAL_PRESET = `'drum'`** — closest stock bank (low inharmonic modes) but
  its decays 15–35 are far too fast; documented as the *damped/covered*
  character only.
- **Alt**: **DrumSynth606** (`DrumSynth606.tom`) — pitch-swept sine gives the
  strike thump (`DRUM606_DEFAULTS`: freq 110, decay 0.9, pitch_sweep 1.35);
  correct for the first ~100 ms.
- **Alt 2**: **Additive** — decaying inharmonic stack, fast attack, long release.
- **Avoid**: BowedString (no bow) and **Karplus-Strong** (there is no string —
  a KS loop's harmonic series is the wrong partial structure; this is the first
  instrument in the KB where KS is explicitly rejected rather than demoted).

## Constants (`timpani.py`)

```python
MIDI_PROGRAM = 47
GM_NAME = "Timpani"
STEM_LABEL = "Timpani"
RANGE_MIN = 36      # C2 — 32-inch drum
RANGE_MAX = 65      # F4 — piccolo-timpano ceiling (Milhaud asks F#4=66)
SOLO_RANGE = (38, 57)   # D2-A3 — standard four-drum set
SWEET_SPOT = (41, 55)   # F2-G3
ZONES = {"low": (36,47), "mid": (48,57), "high": (58,65)}
ARTICULATIONS = {"stroke": (84,1.0), "roll": (72,0.06), "muffle": (60,0.15),
                 "accent": (98,0.9), "soft": (52,1.0), "edge": (70,0.6),
                 "center": (78,0.5), "double_stop": (88,0.9)}
SYNTHESIS = "modal"; MODAL_PRESET = "drum"
TIMPANI_MODES = [(440.0,1.00,0.9), (699.6,0.50,1.3), (941.6,0.28,1.8),
                 (1012.0,0.18,2.4), (1166.0,0.10,3.0)]
DRUM606_DEFAULTS = {"freq": 110.0, "decay": 0.9, "pitch_sweep": 1.35}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 1.59, "mod_depth": 1.2,
               "attack": 0.001, "release": 1.5}
REVERB_TAIL = 2.2   # longest in the instrument set (marimba 1.0 / steel 1.4)
EQ_BODY = (200, -2.0); EQ_PRESENCE = (3000, 2.0); EQ_AIR = (6500, 1.0)
PAN = 0.0           # center solo; -0.3..+0.3 across a 4-drum arc
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

Frontmatter (`instrument.md`): `type: instrument`, `family: Percussion`,
`name: Timpani`, `midi_program: 47`, `gms: "Timpani"`, `range_min: 36`,
`range_max: 65`, `solo_range: [38, 57]`,
`role: [accent, rhythm, bass, drone]`,
`synthesis: [modal, drum606, additive]`.

## Registration proof (registry)

`instrument_registry.py` updated:

1. `"Percussion.timpani.timpani": "timpani"` added to `_INSTRUMENT_MODULES`
2. `TIMPANI = ALL_INSTRUMENTS["timpani"]` convenience constant added
3. `_FIELDS` extended with **`drum606_defaults`** (new engine-preset field, so
   `DRUM606_DEFAULTS` loads through the registry as `TIMP.drum606_defaults` —
   same pattern as the earlier `karplus_defaults`/`bowed_defaults` additions)
4. role mapping `"timpani"` → `accent, rhythm, bass, drone`
5. 4 `__main__` verification lines added

Run output
(`cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`),
new row + verification lines (full table below in the transcript):

```
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
...
  TIMPANI.midi_program = 47 (should be 47)
  by_name('timpani') = <Instrument Timpani (family=Percussion, program=47, range=36-65)>
  by_program(47) = <Instrument Timpani (family=Percussion, program=47, range=36-65)>
  TIMPANI.in_sweet_spot(45) = True
```

`ALL_INSTRUMENTS` count: **29** (was 28).

Full `registry_table()` after the change (new row in place, alphabetical
within family):

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Brass | French Horn | 60 | 41–84 | lead, harmony, accent |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | Trumpet | 56 | 54–86 | lead, counter, accent |
| Brass | Tuba | 58 | 26–72 | bass, counter, accent, harmony |
| Guitar | Acoustic Guitar (nylon) | 25 | 40–84 | lead, harmony, accent |
| Keys | Acoustic Grand Piano | 1 | 21–108 | lead, harmony, accent |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Percussion | Drum Kit | 0 | - | rhythm, groove, accent |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Strings | Cello | 42 | 36–84 | bass, counter, accent, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, counter, accent, harmony |
| Strings | Viola | 41 | 48–91 | lead, harmony, accent |
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, harmony, accent |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
| Woodwind | Bassoon | 70 | 34–88 | lead, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, counter, accent |
| Woodwind | Flute | 74 | 60–96 | lead, counter, accent |
| Woodwind | Oboe | 68 | 52–92 | lead, harmony, accent |
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
```

> Pre-existing table quirks visible above (NOT introduced tonight, unchanged
> from previous runs): the `registry_table()` role fallback prints
> "lead, harmony, accent" for Violin/Viola/Bassoon/Oboe/Clarinet/Flute/Alto
> Saxophone/Acoustic Guitar/Piano, matching `registry.md` rows only loosely
> (registry.md carries the curated roles — the generated table's hardcoded
> branches only cover a subset). Piano's GM name shows as "Acoustic Grand
> Piano" with program 1 (documented legacy row). Drum Kit shows range "-" and
> program 0 (channel-9 instrument, no GM program). None of these affect the
> new row.

## Verification results (`_test/verify_timpani.py` — ALL CHECKS PASSED)

- Registry import through `by_name('timpani')` / `by_program(47)` ✓
- All `_FIELDS` load through the registry (incl. new `drum606_defaults`) ✓
- **Zero-drift**: `True (OK)` — 2 voices × 1 section, 1 bar, terminal landmark
  at BAR ✓
- **Voice stack**: Timpani **SOLO** line ch0 (program 47) + context low bass
  D2 (38, GM33) ch1 — NO second melodic patch on the same pitches, no drums
  stacked ✓
- **MIDI**: `timpani_test.mid` — 135 bytes (> 40 ✓)
- **WAV (solo, FluidR3 via `discover_soundfont()`)**: `timpani_test.wav` —
  **1,170,732 bytes** (> 40 ✓)
- **Spectral check**: 4–8 kHz buzz energy = **0.3%** (OK — no comb-filtering;
  lowest of the whole instrument set)
- **Stem label**: pipeline `GM_PROGRAMS[47]` = `'Timpani'` ✓ (STEM_LABEL
  matches exactly); stem on disk `track00_Timpani.wav` (1,170,732 bytes) +
  `track01_Electric_Bass_finger.wav` (741,676 bytes) ✓
- **SF2 preset**: FluidR3 preset 47 = `'Timpani'` ✓ (phdr chunk)
- **ModalSynth TIMPANI_MODES**: peak 0.900, late(1.0–1.5 s) rms/peak =
  **0.134**, 1.59× partial band energy = **23.7%** ✓ — long ring AND the
  inharmonic membrane partial both confirmed
- **Contrast control**: stock `'marimba'` preset late(1.0–1.5 s) rms/peak =
  **0.0001** → timpani out-rings the marimba bank by ~1000× (assert is >3×) ✓
- **Stock `'drum'` preset** (MODAL_PRESET): peak 0.900 ✓ (documented as
  too-fast for the real envelope)
- **DrumSynth606** `tom` with `DRUM606_DEFAULTS`: peak 1.000, 1.17 s ✓
- **Pitch sweep** (`_test/sweep_timpani.py`): **15/15 notes audible**
  (24, 30, 36, 38, 41, 45, 48, 52, 55, 57, 60, 65, 69, 76, 84), no gaps ✓

## Stem-label quirks found

- **None for GM47.** `GM_PROGRAMS[47]` = "Timpani" (one word, exact GM1
  spelling) → stem `trackXX_Timpani.wav`; FluidR3 preset 47 = "Timpani" —
  labels match exactly.
- Neighbourhood check (live this run): GM46 = "Orchestral Harp" /
  SF2 "Harp" (cosmetic DIFF), GM48 "String Ensemble 1" / SF2 "Strings",
  GM49 "String Ensemble 2" / SF2 "Slow Strings" — **none affect GM47**.
  Known quirks unchanged: GM109 "Bag pipe" → `Bag_pipe`, GM111 "Shanai",
  GM74 Flute → `Recorder`, ch9/pgm0 → `Acoustic_Grand_Piano`.

## Quirks / gotchas worth carrying forward

1. **Inharmonic, NOT harmonic** — the timpani is the first KB instrument whose
   partial structure is the ideal-circular-membrane Bessel set
   (1 : 1.594 : 2.136 : 2.296 : 2.653) rather than a harmonic series. Any
   future engine work that assumes `f0, 2f0, 3f0…` will mis-render it; the
   `TIMPANI_MODES` bank is the reference.
2. **Decay direction is inverted vs marimba** — ModalSynth's `decay` arg is a
   rate (higher = faster). Marimba uses 8–20 for fast bars; timpani needs
   0.9–3.0 for a long ring. Same argument, opposite end of the scale.
3. **No Karplus-Strong** — first KB instrument where KS is explicitly
   *rejected* (no string exists). Don't copy the plucked-family fallback
   pattern into pitched-membrane instruments.
4. **Pitched percussion still needs a melodic channel** — same trap as
   marimba/steel drums: ch9 would trigger the drum-kit map + the
   `Acoustic_Grand_Piano` program-0 fallback label.
5. **`orchestrator.py` has no Timpani program mapping** — `ROLE_PROFILES
   ["accent"]["secondary"]` lists "Timpani" but `instrument_program()` has no
   `"Timpani"` key (returns `None`). Pre-existing gap; the mapping dict is also
   stale for every instrument added since 2026-08-21 (no Marimba, Steel
   Drums, Dulcimer, or any World instrument). Left untouched tonight to stay
   consistent with prior nights — flagging for a dedicated orchestrator sweep.
   Composition jobs should read programs from `instrument_registry` (the full
   KB), which is why registration matters.
6. **`registry.md` == `docs/instruments.md`** — the two files are byte-identical
   (verified with `diff -q`), so both were updated in lockstep tonight.

## Files

- `Percussion/timpani/instrument.md` — full research reference (new)
- `Percussion/timpani/timpani.py` — importable constants (new)
- `Percussion/timpani/REPORT.md` — this report (new)
- `instrument_registry.py` — registered; `_FIELDS` + `drum606_defaults`;
  constant `TIMPANI`; role row; verification lines (29 instruments)
- `registry.md` — changelog entry + Registry table row + quirks table row
- `docs/instruments.md` — same edits (byte-identical mirror)
- `README.md` — status checklist entry
- `_test/verify_timpani.py` — end-to-end verification (ALL CHECKS PASSED)
- `_test/sweep_timpani.py` — FluidR3 pitch sweep (15/15 audible, no gaps)
- `_test/timpani_test.mid` (135 B), `_test/timpani_test.wav` (1,170,732 B),
  `_test/stems_timpani/` — artifacts

## Next candidates (roadmap, not done)

- Percussion: Vibraphone (GM 11 — already ground-truth "Vibraphone" on both
  pipeline and FluidR3), Xylophone (GM 13), Tubular Bells (GM 14)
- Keys: Harpsichord (GM 6), Synth Pad (GM 88)
- Guitar: Electric (GM 27/28/29/30)
- World: Djembe / Congas (no standalone GM program — ch9 kit perc or a
  dedicated world entry), Erhu (no GM program), Ocarina (GM 79), Shakuhachi
  (GM 77), Pan Flute (GM 75)
- Housekeeping: orchestrator `instrument_program()` is stale for every
  instrument added since 2026-08-21 (see quirks #5)
