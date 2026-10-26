# REPORT — Choir (GM52, "Choir Aahs")

**Job**: nightly instrument research (layer-aligned), run 2026-10-26
**Instrument**: Choir — the sampled **mixed chorus** (SATB section, wordless
open "ah")
**Family**: Vocal (third entry: `human_voice`, `voice_like` family, `choir`)
**Files**: `Vocal/choir/instrument.md`, `Vocal/choir/choir.py`,
`Vocal/choir/REPORT.md`
**Test**: `_test/verify_choir.py` (solo render; one voice, one track)

---

## 1. Identity & program

| Field | Value |
|---|---|
| MIDI/GM program | **52** — GM1 "Choir Aahs" (0-based, the 53rd entry) |
| GM name / stem label | `Choir Aahs` → `Choir_Aahs` |
| FluidR3 preset | `Ahh Choir` (phdr-verified; cosmetic SF2 spelling) |
| Preset 53 (for contrast) | `Ohh Voices` — the `human_voice` stand-in |
| Channel | melodic 0–9 (channel 9 = drum map, never for choir) |
| Enum | none in `MidiInstrument` (only 10 exposed) — raw GM 52 via registry |

**Why this instrument**: the KB had a synthetic *solo* singer (`human_voice`,
GM53 stand-in) and six *non-vocal* voice-adjacent instruments (`voice_like`),
but no **choral section**. Choir is the pad/anthem/cinematic voice the
composition jobs reach for and could not find.

**Candidate rejected first (documented quirk)**: a Synth Lead at GM81
"Lead 2 (sawtooth)" — blocked because **both GM80 and GM81 are claimed by
voice_like stand-ins** (`talkbox` → 80/`Lead_1_square`, `singing_saw` →
81/`Lead_2_sawtooth`). A registration there fails `by_program(81)` uniqueness
(`by_program` returned *Singing Saw*) and would share the
`Lead_2_sawtooth` stem filename. GM52 has zero collisions.

## 2. Range

| Zone | MIDI | Pitches | Use |
|---|---|---|---|
| Full (writing band) | 40–88 | E2–E6 | real SATB span; patch plays wider, extremes thin |
| bass | 40–55 | E2–G3 | roots, pedal tones, low "ah" bed |
| tenor | 48–64 | C3–E4 | inner voice / melody at pitch |
| alto | 53–72 | F3–C5 | chord body, most stable blend |
| soprano | 60–88 | C4–E6 | top line, descant, climax |

Sweet spot **48–76** (C3–E5); solo range **55–79** (G3–G5).

Empirical FluidR3 pitch sweep (RMS, vel 74, 1-bar held):

| note | 24 | 36 | 40 | 48 | 60 | 72 | 84 | 88 | 96 |
|---|---|---|---|---|---|---|---|---|---|
| RMS | 963 | 988 | 904 | 1065 | 1015 | 1167 | 1360 | 1363 | 1388 |

All audible, no gaps. RMS **rises** with pitch → balance soprano 8–12 velocity
units below the bass.

## 3. Roles

`pad, harmony, melody (slow/sustained only), countermelody, anthem, texture`
— **not** a bass voice below E2, **not** comping/rhythm (every onset is a
100–300 ms breath), **not** a melisma soloist (use `human_voice`).

## 4. Articulations (velocity, duration factor)

| Technique | Vel | Dur | Timbre |
|---|---|---|---|
| ah | 68–78 | 1.0 | default sustained vowel |
| legato | 66–74 | 1.0 | seamless phrase join |
| swell | 58→78 | 1.0 | held-chord crescendo |
| decrescendo | 60→52 | 1.0 | phrase-end taper |
| staccato | 72–78 | 0.3 | short "ah" stab (blurs — needs rhythmic double) |
| marcato | 85–92 | 0.85 | hard "HAH" anthem hit |
| hum | 48–56 | 1.0 | low-velocity closed-mouth bed |

## 5. Timbre DNA

- Ensemble unison: many voices, ±5–20 cents detune → 1–5 Hz beating, wide unison
- Vowel formants "ah": F1 730 / F2 1090 / F3 2440 Hz (Peterson & Barney 1952)
- Singer's-formant ring smeared to a broad 2.8–3.2 kHz presence band
- Aspiration (breath noise ~1–5 kHz) at ~10%, staggered onsets → soft attack
- Unsynchronised vibrato 4.5–6 Hz per voice (never one LFO on the whole section)
- No consonants — wordless vowels only

## 6. Synthesis engine recommendation

**Primary: Additive** (`sound/synthesis/additive.py` SoundWave) — a chorus is a
formant-shaped harmonic stack.

```
ADDITIVE_HARMONICS["choir_ah"] = [1.0, 0.72, 0.55, 0.60, 0.34, 0.22, 0.14, 0.09]
ADDITIVE_HARMONICS["choir_hum"] = [1.0, 0.45, 0.22, 0.10, 0.05, 0.03]
SYNTHESIS_DEFAULTS = {
    "instrument": "choir", "attack": 0.18, "detune": 0.009, "stack": 5,
    "release": 0.45, "sustain_level": 0.88, "vowel": "a",
    "formants_hz": (730.0, 1090.0, 2440.0), "breath": 0.10,
}
```

**Secondary: SingingVoice** (`singing_voice.py`), 4–5 detuned voices:

```
SINGING_VOICE_DEFAULTS = {
    "voice_type": "alto", "vibrato_hz": 5.2, "vibrato_depth": 0.28,
    "breathiness": 0.22, "jitter": 0.012, "shimmer": 0.05,
    "stack": 4, "detune": 0.009,
}
```

**Tertiary: PhaseModSynth** — `FM_DEFAULTS`: sine carrier, ratio 2.0,
depth 1.6, attack 0.2, release 0.45, sustain 0.85.

**Production path**: FluidSynth preset 52 via `discover_soundfont()`
(FluidR3_GM.sf2 preferred).

## 7. All constants (`Vocal/choir/choir.py`)

```python
MIDI_PROGRAM = 52
GM_NAME = "Choir Aahs"
STEM_LABEL = "Choir_Aahs"
RANGE_MIN = 40
RANGE_MAX = 88
SOLO_RANGE = (55, 79)
SWEET_SPOT = (48, 76)
ZONES = {"bass": (40, 55), "tenor": (48, 64), "alto": (53, 72), "soprano": (60, 88)}
ARTICULATIONS = {"ah": (72, 1.0), "legato": (70, 1.0), "swell": (60, 1.0),
                 "staccato": (74, 0.3), "marcato": (88, 0.85),
                 "decrescendo": (58, 1.0), "hum": (52, 1.0)}
SYNTHESIS = "additive"
REVERB_TAIL = 2.8
EQ_BODY = (350, -2.5)
EQ_PRESENCE = (3000, 2.0)
EQ_AIR = (7000, 1.0)
PAN = 0.0
def midi_to_freq(midi): return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## 8. Registration proof

Registered in `/opt/data/projects/Instruments/instrument_registry.py`:

```python
# _INSTRUMENT_MODULES
"Vocal.choir.choir": "choir",
...
CHOIR = ALL_INSTRUMENTS["choir"]
# registry_table() role row
elif low == "choir aahs":
    role = "pad, harmony, melody, countermelody, anthem, texture"
```

Verification run (`python instrument_registry.py`, full output in
`_test/choir_registry_out.txt`) — new rows:

```
| Vocal | Choir Aahs | 52 | 40–88 | pad, harmony, melody, countermelody, anthem, texture |
| Vocal | Didgeridoo | 20 | 24–55 | lead, harmony, accent |
| Vocal | Human Voice | 53 | 48–84 | lead, melody, countermelody |
...
  CHOIR.midi_program = 52 (should be 52)
  by_name('choir') = <Instrument Choir Aahs (family=Vocal, program=52, range=40-88)>
  by_name('choir aahs') = <Instrument Choir Aahs (family=Vocal, program=52, range=40-88)>
  by_program(52) = <Instrument Choir Aahs (family=Vocal, program=52, range=40-88)>
  CHOIR.in_sweet_spot(64) = True
  CHOIR.in_sweet_spot(24) = False
```

`by_program(53)` → `Human Voice` (distinct). Registry load count **77**
objects (70 → 71 instrument folders + voice_like members).

## 9. Verification results (`_test/verify_choir.py`, all checks passed)

| Check | Result |
|---|---|
| Zero-drift `validate()` | **True (OK)** |
| MIDI | `_test/choir_test.mid` — **81 bytes** (> 40) |
| Solo WAV | `_test/choir_test.wav` — **1,077,292 bytes** (> 40) |
| Spectral buzz 4–8 kHz | **2.0%** (gate < 20%) |
| Stem | `stems_choir/track00_Choir_Aahs.wav` — 1,077,292 bytes |
| Pitch sweep | audible 24/36/40/48/60/72/84/88/96, no gaps |
| Additive envelope | late-sustain weight **0.718** (collapse gate ≥ 0.45) |
| SingingVoice single voice | peak 0.800, sustain/peak **0.290** |
| SingingVoice 5-voice stack | rms **0.0878**, raw peak 1.722 (needs normalizing) |
| `by_program(52)` | Choir Aahs; `by_program(53)` Human Voice |

Audio chain: UnitMatrixComposer (1 voice, 1 bar, SATB chord 43/48/55/60/64
held to BAR) → `validate()` → `to_midi` → `render_midi(..., solo=0)` →
`discover_soundfont()` (FluidR3_GM.sf2) → `fluidsynth -ni -g 1.2 -F`.
**Solo only** — no second melodic patch on the same pitches (comb-filter
lesson 2026-09-01).

## 10. Quirks found

1. **GM80 + GM81 are taken by voice_like stand-ins** (`talkbox`, `singing_saw`,
   the latter owning stem `Lead_2_sawtooth`). Any future "saw lead" /
   "square lead" instrument must pick a different program (82/83/86 free).
2. **Choir Aahs (52) has no collisions** — 52 free, 53 = human_voice,
   54 = Synth Voice (still unused), 55 = Orchestra Hit (unused).
3. **SF2 name mismatch**: FluidR3 preset 52 = "Ahh Choir" vs GM "Choir Aahs" —
   cosmetic; pipeline labels stems from `GM_PROGRAMS`, so no routing impact.
4. **Additive per-grid-step decay**: `apply_overtones` leaves `frequency` at
   the TOP partial, so `decay_S` must be ~1e-4 to hold a 2 s chord (inherited
   synth_pad quirk, re-verified here at 0.718).
5. **`get_adsr_weights` asserts length proportions sum to exactly 1.0** — an
   [0.18, 0.05, 0.6, 0.05] set (0.88) raises `AssertionError`; use
   [0.18, 0.07, 0.65, 0.10].
6. **SingingVoice stack clips if summed raw**: 5 voices at amp 0.8 peak at
   1.722 → divide by N or √N.
7. **RMS rises with pitch** on preset 52 (904 at E2 → 1388 at C7): choral
   chords need upper-voice velocity trim.
8. **Pre-existing table noise**: `registry_table()` shows two identical
   "Vox Humana" rows (voice_like umbrella + FAMILY member share the label).
   Not caused by this entry; left untouched.

## 11. Files written / updated

- `Vocal/choir/choir.py` (new)
- `Vocal/choir/instrument.md` (new)
- `Vocal/choir/REPORT.md` (new, this file)
- `instrument_registry.py` — module entry, `CHOIR` constant, role row,
  verification prints
- `registry.md` — Registry table row, stem-label quirks row (52), changelog
  entry 2026-10-26
- `README.md` — registry load count 38 → 77, tree note (71 folders)
- `_test/verify_choir.py` (new), `_test/choir_registry_out.txt` (verification
  log), `_test/choir_test.mid`, `_test/choir_test.wav`,
  `_test/stems_choir/track00_Choir_Aahs.wav`
