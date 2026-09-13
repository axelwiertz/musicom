# REPORT — Vibraphone (GM11) added 2026-09-13

## Instrument

- **Name**: Vibraphone (also "vibraharp", "vibes") — tuned **aluminium alloy
  bars** suspended over **resonator tubes**, struck with yarn/cord-wrapped
  rubber mallets, with a **piano-style sustain pedal** and an electric
  **motor** that spins fans in the tube tops for a tremolo
- **Family**: Percussion (keyboard/metallophone, pitched) — fifth entry after
  Drum Kit, Marimba, Steel Drums, Timpani
- **MIDI program**: 11 (GM1 "Vibraphone", bank 0)
- **GM name**: "Vibraphone" (matches GM spec, pipeline, and SoundFont)
- **Stem label**: `trackXX_Vibraphone.wav` (GM_PROGRAMS[11] = "Vibraphone" —
  matches exactly, **no quirk**)
- **Channel**: melodic 0–9 — the vibraphone is PITCHED; channel 9 would swap in
  the drum-kit map and mislabel the stem `Acoustic_Grand_Piano`

### Why this pick

Next in the documented roadmap. `Percussion/timpani/REPORT.md` "Next
candidates" lists: *"Percussion: Vibraphone (GM 11 — already ground-truth
'Vibraphone' on both pipeline and FluidR3), Xylophone (GM 13), Tubular Bells
(GM 14)"*. The vibraphone is the highest-value item: it is the **second most
popular solo keyboard-percussion instrument in classical music after the
marimba** and the defining jazz-vibes voice, i.e. the melodic-percussion entry
with the largest arrangement surface, and both pipeline and SF2 labels were
already confirmed clean before writing.

Candidate ground truth (re-verified live this run, `_test/probe_harpsichord.py`
+ `probe_candidates2.py`):

| Prog | Pipe label (GM_PROGRAMS) | FluidR3 preset | Match |
|---|---|---|---|
| 6 | Harpsichord | Harpsichord | OK (next candidate) |
| 9 | Glockenspiel | Glockenspiel | OK |
| 10 | Music Box | Music Box | OK |
| **11** | **Vibraphone** | **Vibraphone** | **OK — exact** |
| 12 | Marimba | Marimba | OK (registered 2026-09-01) |
| 13 | Xylophone | Xylophone | OK |
| 14 | Tubular Bells | Tubular Bells | OK |

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–89 | C3–F6 | 4-octave models from C3 to the standard F6 top |
| Sweet spot | 60–84 | C4–C6 | roundest, most singing; fullest resonator bloom |
| Solo range | 53–89 | F3–F6 | the standard 3-octave instrument |
| Low | 48–59 | C3–B3 | 4-octave model bass bars — dark, mellow, long bloom |
| Mid | 60–77 | C4–F5 | principal melodic/vocal register (ballad/jazz zone) |
| High | 78–89 | F#5–F6 | bright, metallic, shorter ring; clang + bowed glass |

Grounded facts (Wikipedia `Vibraphone`, rev **1373879017**, fetched this run):

- standard modern instrument = **3 octaves, F to F** (F3–F6); *"Larger or
  4-octave models from the C below middle C are also becoming more common
  (C to F or C)"*
- *"the vibraphone is generally a non-transposing instrument, written at
  concert pitch"*
- developed from **Herman E. Winterhoff's** Leedy experiments (~1916; marketed
  from 1924); **Henry Schluter** (J. C. Deagan) re-made it in 1927 with
  **aluminium bars for a mellower tone** and *"adjusted the dimensions and
  tuning of the bars to eliminate the dissonant harmonics present in the Leedy
  design"* plus the **foot-controlled damper bar**
- bars are suspended at the **nodal points (22.4% from each end)** by paracord;
  the **deep arch** ground into the underside is *"the key to the mellow sound
  of the vibraphone (and marimba...)"* vs the xylophone's shallow arch and the
  glockenspiel's none
- the arch retunes the three primary bar modes to **f0, f0×4 (two octaves),
  and (f0×4)+major-3rd (i.e. 1 : 4 : 10)** — documented with the concrete
  F-bar example
- resonator tubes are closed quarter-wavelength tubes that amplify **the
  fundamental but not the upper partials**, and are *"usually tuned slightly
  off-pitch to create a balance between loudness and sustain"* — the
  loudness-vs-sustain trade-off; *"vibraphone bars can ring for many
  seconds"* (marimbas/xylophones cannot)
- the **motor** spins "fans" in the resonator tops: *"rotation of the fans
  creates a tremolo effect and a slight vibrato"*; variable-speed motors
  *"typically support rotation rates in the range of 1–12 Hz"*
- **damper mechanism**: pedal up = felt pad on bars (muted), pedal down = ring;
  "after pedaling" and "half pedaling" are standard techniques; the
  all-or-nothing pedal is why four-mallet players also use mallet and hand
  damping
- **dead strokes** (mallet pressed onto the bar) and **finger/hand damping**
  are named techniques; **pitch bend** ≈ a half step down by sliding a mallet
  from nodal point to center
- **bowing** the bar edge gives a sustained, attack-free, more "glassy" tone
  emphasizing the higher harmonics — *"fast passages are not often written for
  bowed vibraphone"*
- mallet hardness *"can have a great effect on the timbre, ranging from a
  bright metallic clang to a mellow ring with no obvious initial attack"*

Empirical FluidR3 pitch sweep (`_test/sweep_vibraphone.py`, RMS, notes
36–96): **13/13 notes audible, no gaps** — the SF2 patch never clips a
composition. Range 48–89 is the real-instrument span; the sweep proves the
patch is audible from C2 up to C7 beyond it.

## Role

- **Lead / melody** (mid zone C4–F5) — the classic jazz-vibes solo voice
- **Harmony / comping** (2–4 note rolled or block four-mallet voicings) —
  rhythm-section substitute for piano/guitar
- **Countermelody** against a horn or vocal lead
- **Accent / colour** (hard-mallet clangs, bowed bars, motor-on washes)
- **NOT a bass voice** (nothing useful below C3; tone is soft)
- NOT channel 9 (pitched instrument → must use a melodic channel)

## Synthesis engine (musicom)

- **Primary**: **ModalSynth** (`sound/synthesis/modal.py`) — a vibraphone bar
  is a struck bar, i.e. an impulse-excited resonator bank. Exact custom bank
  `VIBRAPHONE_MODES` in `vibraphone.py`: the **arch-tuned** ratios
  **1 : 4 : 10** (fundamental / two octaves / octave + major third) with
  amplitudes 1.00 / 0.14 / 0.05 — the fundamental dominates because the
  resonator tubes amplify it and not the upper partials — and decay rates
  **0.30 / 0.60 / 1.10** (LOW / slow: a bar rings for seconds).
  `ModalSynth.render_custom(VIBRAPHONE_MODES, duration, excitation='impulse')`;
  use `excitation='noise'` for the soft-yarn mallet's softer onset. Modes are
  referenced to A4=440 — scale by the played note.
- **Motor tremolo** — `MOTOR_DEFAULTS` (rate_hz 5.0, depth 0.35, span
  1.0–12.0 Hz) defines the namesake amplitude modulation. This is an
  effect/production step over a sustained render, not a different oscillator;
  it is the single most idiomatic jazz-vibes signature.
- **MODAL_PRESET = `'bell'`** — closest STOCK bank (inharmonic-ish partials,
  comparatively slow decay). Approximation only: neither the 1 : 4 : 10 tuning
  nor the multi-second ring.
- **Alt**: **PhaseModSynth** — sine carrier, `mod_freq_ratio` 4.0 (the
  2-octave partial), `mod_depth` 1.6 (mellow, not bell), attack 0.004,
  release 1.6. Cheap vibes comp patch.
- **Fallback**: **Karplus-Strong** (SP-011) — the bar is STRUCK, not plucked;
  `loop_gain` 0.9975 (sitar-class damping) approximates the multi-second ring
  and nothing else. Demoted, not rejected (contrast timpani, where KS is
  rejected outright because a membrane has no string *and* the wrong partial
  structure).
- **Avoid BowedString** as the main engine (bowing is a genuine but rare
  extended technique — model it as a sustained additive/pad render).

## Constants (`vibraphone.py`)

```python
MIDI_PROGRAM = 11
GM_NAME = "Vibraphone"
STEM_LABEL = "Vibraphone"
RANGE_MIN = 48      # C3 — 4-octave models
RANGE_MAX = 89      # F6 — standard 3-octave top
SOLO_RANGE = (53, 89)   # F3–F6 — standard 3-octave instrument
SWEET_SPOT = (60, 84)   # C4–C6
ZONES = {"low": (48,59), "mid": (60,77), "high": (78,89)}
ARTICULATIONS = {"strike": (82,1.0), "hard_mallet": (92,0.9), "soft_mallet": (62,1.0),
                 "motor": (78,1.0), "roll": (70,0.08), "dead_stroke": (66,0.12),
                 "damped": (54,0.10), "bowed": (60,1.0), "bend": (72,0.8)}
SYNTHESIS = "modal"; MODAL_PRESET = "bell"
VIBRAPHONE_MODES = [(440.0,1.00,0.30), (1760.0,0.14,0.60), (4400.0,0.05,1.10)]
MOTOR_DEFAULTS = {"rate_hz": 5.0, "depth": 0.35, "rate_range_hz": (1.0, 12.0)}
KARPLUS_DEFAULTS = {"loop_gain": 0.9975, "width": 0.30, "role": "lead"}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 4.0, "mod_depth": 1.6,
               "attack": 0.004, "release": 1.6}
REVERB_TAIL = 1.8
EQ_BODY = (300, -2.0); EQ_PRESENCE = (4000, 2.0); EQ_AIR = (9000, 1.5)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

Frontmatter (`instrument.md`): `type: instrument`, `family: Percussion`,
`name: Vibraphone`, `midi_program: 11`, `gms: "Vibraphone"`, `range_min: 48`,
`range_max: 89`, `solo_range: [53, 89]`,
`role: [lead, melody, harmony, countermelody, accent]`,
`synthesis: [modal, phase_mod, karplus]`.

## Registration proof (registry)

`instrument_registry.py` updated:

1. `"Percussion.vibraphone.vibraphone": "vibraphone"` added to
   `_INSTRUMENT_MODULES`
2. `VIBRAPHONE = ALL_INSTRUMENTS["vibraphone"]` convenience constant added
3. `_FIELDS` extended with **`motor_defaults`** (new engine-preset field so
   `MOTOR_DEFAULTS` loads through the registry as
   `VIBRAPHONE.motor_defaults` — same pattern as the earlier
   `karplus_defaults` / `bowed_defaults` / `drum606_defaults` additions)
4. `_member_module` (voice-like family helper) also forwards `MOTOR_DEFAULTS`
   so it is reachable from the family-member instruments that have one
5. role mapping `"vibraphone"` → `lead, melody, harmony, countermelody, accent`
6. 4 `__main__` verification lines added

Run output
(`cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`),
new row + verification lines:

```
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
...
  VIBRAPHONE.midi_program = 11 (should be 11)
  by_name('vibraphone') = <Instrument Vibraphone (family=Percussion, program=11, range=48-89)>
  by_program(11) = <Instrument Vibraphone (family=Percussion, program=11, range=48-89)>
  VIBRAPHONE.in_sweet_spot(69) = True
```

Count check (`_test/check_vibraphone_registry.py`):

```
count 38
has vibraphone True
programs dup 11: ['vibraphone']        # no program-11 collision
row: ['| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |']
```

`ALL_INSTRUMENTS` count is **38** (was 37 with the Vocal voice-like family
members in place) — the per-family curated table in `registry.md` lists 30
entries; the registry additionally registers six voice-like members
(vox_humana, kazoo, jaw_harp, didgeridoo, singing_saw, talkbox) individually.
The vibraphone adds exactly +1.

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
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
| Strings | Cello | 42 | 36–84 | bass, counter, accent, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, counter, accent, harmony |
| Strings | Viola | 41 | 48–91 | lead, harmony, accent |
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Vocal | Didgeridoo | 20 | 24–55 | lead, harmony, accent |
| Vocal | Human Voice | 53 | 48–84 | lead, melody, countermelody |
| Vocal | Jaw Harp | 106 | 36–74 | lead, harmony, accent |
| Vocal | Kazoo | 59 | 50–86 | lead, harmony, accent |
| Vocal | Singing Saw | 81 | 55–91 | lead, harmony, accent |
| Vocal | Talkbox | 80 | 45–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
| Vocal | Vox Humana | 20 | 48–84 | lead, harmony, accent |
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
> Saxophone/Acoustic Guitar/Piano and for all six Vocal entries, matching
> `registry.md` rows only loosely (registry.md carries the curated roles — the
> generated table's hardcoded branches cover a subset). Piano's GM name shows
> as "Acoustic Grand Piano" with program 1 (documented legacy row). Drum Kit
> shows range "-" and program 0 (channel-9 instrument, no GM program). The two
> "Vox Humana" rows are the voice_like umbrella + its vox_humana member — both
> carry program 20 by design. **The new row is curated and prints exactly as
> intended.**

## Verification results (`_test/verify_vibraphone.py` — ALL CHECKS PASSED)

- Registry import through `by_name('vibraphone')` / `by_program(11)` ✓
- All `_FIELDS` load through the registry (incl. new `motor_defaults`) ✓
- Arch-tuned partial assertion: `VIBRAPHONE_MODES` ratios == `[1.0, 4.0, 10.0]` ✓
- **Zero-drift**: `True (OK)` — 2 voices × 1 section, 1 bar, terminal landmark
  at BAR ✓
- **Voice stack**: Vibraphone **SOLO** line ch0 (program 11) + context low bass
  E2 (40, GM33) ch1 — NO second melodic patch on the same pitches, no drums
  stacked ✓
- **MIDI**: `_test/vibraphone_test.mid` — **135 bytes** (> 40 ✓)
- **WAV (solo, FluidR3 via `discover_soundfont()`)**: `_test/vibraphone_test.wav`
  — **804,396 bytes** (> 40 ✓)
- **Spectral check**: 4–8 kHz buzz energy = **0.8%** (OK — no comb-filtering)
- **Stem label**: pipeline `GM_PROGRAMS[11]` = `'Vibraphone'` ✓ (STEM_LABEL
  matches exactly); neighbors checked live: [9] `Glockenspiel`,
  [10] `Music Box`, [12] `Marimba`, [13] `Xylophone`, [14] `Tubular Bells` —
  all clean. Stems on disk: `track00_Vibraphone.wav` (804,396 B) +
  `track01_Electric_Bass_finger.wav` (741,676 B) ✓
- **SF2 preset**: FluidR3 preset 11 = `'Vibraphone'` ✓ (phdr chunk)
- **ModalSynth `VIBRAPHONE_MODES`**: peak 0.900, late(1.0–1.5 s) rms/peak =
  **0.445** ✓ — multi-second ring confirmed
- **Contrast control**: stock `'marimba'` preset late(1.0–1.5 s) rms/peak =
  **0.0001** → the vibraphone bank out-rings the marimba bank by ~**4400×**
  (assert is >3×) ✓
- **Partial dominance**: f0 = 8386.7, 4× = 1092.4 (**13.0%** of f0),
  10× = 347.3 (**4.1%** of f0) ✓ — fundamental dominates, exactly as the
  resonator tubes dictate
- **Motor tremolo** (`MOTOR_DEFAULTS` rate 5.0 Hz, depth 0.35 applied as
  AM): envelope spectral peak at the motor rate = **0.670** of the nearby
  envelope max ✓ — the namesake tremolo is measurable
- **Karplus-Strong fallback**: tail_rms/peak(1–2 s) = **0.0053** vs dull
  control **0.0016** (3.3× ring advantage) ✓
- **Pitch sweep** (`_test/sweep_vibraphone.py`): **13/13 notes audible**
  (36, 48, 53, 55, 60, 65, 69, 72, 76, 81, 84, 89, 96), no gaps ✓

## Stem-label quirks found

- **None for GM11.** `GM_PROGRAMS[11]` = "Vibraphone" (one word, exact GM1
  spelling) → stem `trackXX_Vibraphone.wav`; FluidR3 preset 11 = "Vibraphone"
  — labels match exactly.
- Neighbourhood (live this run): GM9 `Glockenspiel` / SF2 `Glockenspiel`,
  GM10 `Music Box` / SF2 `Music Box`, GM13 `Xylophone` / SF2 `Xylophone`,
  GM14 `Tubular Bells` / SF2 `Tubular Bells` — **all clean, none affect
  GM11**.
- Known quirks unchanged: GM109 `Bag pipe` → `Bag_pipe`, GM111 `Shanai`,
  GM74 Flute → `Recorder`, GM101/102 (Sitar `Sitar`), ch9/pgm0 →
  `Acoustic_Grand_Piano`.

## Quirks / gotchas worth carrying forward

1. **Arch tuning is the whole tone story** — a vibraphone bar is NOT a raw
   free-free bar. The raw free-free/tuning-tine ratios are
   `1 : 6.27 : 17.55 : 34.39` (see `sound/synthesis/music_box.py`,
   `TINE_RATIOS`); the arch ground into the bar's underside retunes the first
   three modes to **1 : 4 : 10**. Use `VIBRAPHONE_MODES`, never `TINE_RATIOS`,
   for this instrument. (The arch recipe is shared with marimba —
   `marimba.py` uses the same struck-bar family — but the vibraphone's
   aluminium + resonator tubes + pedal make the envelope completely
   different.)
2. **Sustain is the definition, not a detail** — the timpani REPORT established
   that ModalSynth's `decay` arg is a RATE (higher = faster), needing 0.9–3.0
   for a long drum ring vs marimba's 8–20. The vibraphone goes further still:
   **0.30–1.10**, and measures a **0.445** late-window ring — the longest
   synthetic sustain of any KB instrument so far. Any future "percussion =
   fast decay" shortcut will destroy this instrument.
3. **Motor tremolo has no engine** — `MOTOR_DEFAULTS` is documented as an
   amplitude-modulation step over a sustained render. There is no motor
   oscillator in `sound/`. Composition jobs that want the vibe tremolo must
   apply the AM themselves (verified in the test: a simple
   `1 - depth*0.5*(1-cos(2π·rate·t))` envelope produces measurable movement at
   5 Hz).
4. **Dynamic range is deliberately narrow, and mallet hardness is coupled to
   brightness** — the resonator tuning trades peak loudness for sustain. Do
   not "fix" quiet vibes with compression or velocity; use pedal/motor and
   mallet choice as the expressive axes. Hard-mallet = louder AND brighter
   (unlike marimba, where mallet choice is mostly about tone).
5. **Pitched percussion still needs a melodic channel** — same trap as
   marimba/steel drums/timpani: ch9 triggers the drum-kit map + the
   `Acoustic_Grand_Piano` program-0 fallback label.
6. **Four-mallet voicings are legitimate chords** — unlike fiddle/bagpipe/
   shamisen (line instruments), the vibraphone can take 2–4 note block chords
   and a walking bass-ish left hand; it is a genuine harmony/comping voice.
   Only the BASS register is off-limits (nothing useful below C3).
7. **`orchestrator.py` still has no Vibraphone program mapping** — the
   pre-existing gap flagged in the timpani REPORT (the mapping dict is stale
   for every instrument added since 2026-08-21) is unchanged; `ROLE_PROFILES`
   `["harmony"]`/`["melody"]` secondaries never mention the vibraphone either.
   Left untouched to stay consistent with prior nights — composition jobs read
   programs from `instrument_registry` (the full KB), which is exactly why
   registration matters.
8. **`registry.md` == `docs/instruments.md`** — verified byte-identical with
   `diff -q` after the edit (mirror re-copied tonight), so both carry the new
   changelog entry, registry row and quirks-table row.
9. **Registry count vs curated-table count** — `ALL_INSTRUMENTS` is 38 because
   the Vocal voice-like family registers six members individually on top of
   the umbrella; `registry.md`'s curated table lists the 30 per-family
   entries. The vibraphone is +1 in both.

## Files

- `Percussion/vibraphone/instrument.md` — full research reference (new)
- `Percussion/vibraphone/vibraphone.py` — importable constants (new)
- `Percussion/vibraphone/REPORT.md` — this report (new)
- `instrument_registry.py` — registered; `_FIELDS` + `motor_defaults`;
  constant `VIBRAPHONE`; role row; `_member_module` forwards MOTOR_DEFAULTS;
  verification lines (38 instruments loaded)
- `registry.md` — changelog entry + Registry table row + quirks table row
- `docs/instruments.md` — same edits (byte-identical mirror, re-copied)
- `README.md` — structure tree + instrument count + status checklist entry
- `_test/verify_vibraphone.py` — end-to-end verification (ALL CHECKS PASSED)
- `_test/sweep_vibraphone.py` — FluidR3 pitch sweep (13/13 audible, no gaps)
- `_test/check_vibraphone_registry.py` — count / collision check
- `_test/probe_harpsichord.py`, `_test/probe_candidates2.py` — label ground
  truth probes (pipeline GM_PROGRAMS + FluidR3 phdr)
- `_test/vibraphone_test.mid` (135 B), `_test/vibraphone_test.wav`
  (804,396 B), `_test/stems_vibraphone/` — artifacts

## Regression suite (repo-wide)

`/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/ -q` →
**1 failed, 482 passed, 1 skipped** (336 s).

The single failure is **pre-existing and unrelated to this instrument**:

```
FAILED tests/test_paths_step1.py::test_midi_exists_nonempty - AssertionError
  ... '/opt/data/projects/Styles/Pop/path-C/MIDI/pop-C-42.mid' ... os.path.getsize
```

That test asserts on a HipHop/Pop *style* composition artifact under
`projects/Styles/Pop/path-C/` (a concurrent nightly composition job's output
tree — the working tree shows that directory already modified by other jobs
tonight). Nothing in the instrument KB, the registry, or the vibraphone
verification touches it; the vibraphone's own end-to-end check is green.

## Next candidates (roadmap, not done)

- Percussion: Xylophone (GM 13 — ground truth clean on both), Tubular Bells
  (GM 14), Glockenspiel (GM 9), Music Box (GM 10)
- Keys: Harpsichord (GM 6 — ground truth clean), Celesta (GM 8), Synth Pad
  (GM 88)
- Guitar: Electric (GM 27/28/29/30)
- World: Porch/porch-style entries — Erhu, Shakuhachi (GM 77), Pan Flute
  (GM 75), Ocarina (GM 79), Djembe/Congas (no standalone GM program)
- Housekeeping: orchestrator `instrument_program()` is stale for every
  instrument added since 2026-08-21 (see quirks #7)
