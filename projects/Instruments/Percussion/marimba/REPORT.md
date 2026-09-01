# REPORT — Marimba

**Date**: 2026-09-01 (nightly instrument research job)
**Instrument**: Marimba (GM 12)
**Family**: Percussion
**Status**: ✅ VERIFIED end-to-end

---

## Instrument

| Field | Value |
|---|---|
| Family | Percussion |
| Name | Marimba |
| MIDI program | 12 |
| GM name | "Marimba" |
| SF2 preset | `Marimba` (preset 12, verified from phdr chunk — exact match) |
| RenderPipeline stem label | `Marimba` → `trackXX_Marimba.wav` (no quirk) |
| Channel | any melodic channel 0–9 (NOT channel 9 — melodic percussion) |

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 45–96 | A2–C7 | standard 5-octave marimba (4.3-octave A2–C7 common) |
| Solo range | 60–84 | C4–C6 | solo repertoire focus |
| Sweet spot | 60–84 | C4–C6 | warm round tone, best projection |
| Low | 45–59 | A2–B3 | dark woody bass bars, long decay, soft attack |
| Mid | 60–71 | C4–B4 | warm, round, singing — classic marimba voice |
| High | 72–96 | C5–C7 | bright, dry, cutting; mallet click prominent |

## Role

- Lead melody (C4–C6 sweet spot — solo marimba repertoire, mallet ensembles)
- Accent/ornament (high register runs, glissandi, fills)
- Countermelody (interlocking lines, Reich-style phase patterns)
- Harmony (mallets play 2–4 note chords; ostinato accompaniment)
- NOT bass (low bars too soft/wooden to anchor a mix), NOT kit groove

## Synthesis Engine

- **Primary**: `modal` — ModalSynth (`sound/synthesis/modal.py`)
  - Dedicated preset `ResonatorBank.preset('marimba')`: fundamental + 2nd/3rd/
    4th/5th modes, decay rates 8–20 (fast exponential decay)
  - `ModalSynth.render_preset('marimba', duration, excitation='impulse')` —
    mallet strike = impulse; `'noise'` excitation approximates a hard mallet
  - Preset is tuned at A4=440 — pitch-shift rendered note or scale mode freqs
  - Fast decay inherent to preset; no ADSR needed
- **Alt**: `additive` — decaying harmonic stack, fundamental-dominant with odd
  partials + 4× inharmonic mode (marimba's characteristic tuning), fast attack
- **Avoid**: PhaseModSynth (FM for reed/brass/synth, not struck bars)

## Constants (marimba.py)

```python
MIDI_PROGRAM = 12
GM_NAME = "Marimba"
STEM_LABEL = "Marimba"          # pipeline GM_PROGRAMS[12] = "Marimba" -> Marimba
RANGE_MIN = 45      # A2
RANGE_MAX = 96      # C7
SOLO_RANGE = (60, 84)
SWEET_SPOT = (60, 84)
ZONES = {"low": (45, 59), "mid": (60, 71), "high": (72, 96)}
ARTICULATIONS = {
    "sustain": (80, 1.0), "roll": (68, 0.06), "staccato": (64, 0.2),
    "accent": (96, 0.9), "dead_stroke": (48, 0.15),
}
SYNTHESIS = "modal"
MODAL_PRESET = "marimba"
REVERB_TAIL = 1.0
EQ_BODY = (400, -2.0)
EQ_PRESENCE = (3000, 2.0)
EQ_AIR = (7000, 1.0)
PAN = 0.0
```

## Verification (engine test, 2026-09-01)

Full UnitMatrixComposer test (1 bar, 3 voices: Marimba + Clarinet + Piano):

- **Zero-drift validate**: ✅ `True (OK)`
- **MIDI export**: `/opt/data/projects/Instruments/_test/marimba_test.mid` — **183 bytes** (> 40 ✓)
- **FluidSynth render** (`-ni -g 1.2`, TimGM6mb.sf2): exit 0
- **WAV**: `/opt/data/projects/Instruments/_test/marimba_test.wav` — **965,164 bytes** (> 40 ✓)
- **RenderPipeline stems**: 3 files, incl. `track00_Marimba.wav` (965,164 bytes > 40 ✓)
- SF2 preset 12 = `Marimba` ✓ (phdr check)
- Stem label `GM_PROGRAMS[12]` = `"Marimba"` ✓
- ModalSynth `'marimba'` smoke: peak=0.900, tail_rms/peak=0.019 at t=0.4s —
  fast exponential decay confirmed (no sustain plateau)

Verify script: `_test/verify_marimba.py` — **ALL CHECKS PASSED**

## Registry

- Added to `instrument_registry.py`: module entry `Percussion.marimba.marimba`,
  `MARIMBA` convenience constant, role mapping for the auto-table.
  **BUG FIXED**: `_load_all` overwrote ALL percussion GM_NAMEs with "Drum Kit"
  — now only drum_kit is overridden (marimba keeps GM_NAME="Marimba").
- Added to `registry.md`: Registry table row (Percussion | Marimba | 12 |
  45–96 | lead, melody, accent, countermelody, harmony) + quirks table row
  (program 12 → Marimba ✓) + changelog entry.
- Registry self-test: 18 instruments loaded, `by_name('marimba')` /
  `by_program(12)` resolve, table prints correctly.

## Quirks Found

1. **No stem-label quirk** — pipeline `GM_PROGRAMS[12]` = "Marimba", SF2
   preset 12 = "Marimba", and disk stem `trackXX_Marimba.wav` all match
   exactly. (Contrast: GM11=Vibraphone, GM13=Xylophone, GM14=Tubular Bells —
   all clean labels too.)
2. **Melodic percussion is NOT channel 9** — marimba is a pitched melodic
   instrument on a normal program channel (0–9 melodic). Using channel 9 would
   trigger the program-0 fallback stem label `Acoustic_Grand_Piano` (the
   drum_kit quirk) — do NOT route marimba to channel 9.
3. **MidiInstrument enum has NO marimba** — only 10 instruments exposed
   (PIANO=1, CHURCH_ORGAN=20, ACOUSTIC_GUITAR=25, VIOLIN=41, STRING_ENSEMBLE=49,
   TRUMPET=57, FLUTE=74, SYNTH_PAD=88, BASS=33). Use raw `program=12`.
4. **ModalSynth 'marimba' preset is fixed at A4=440** — a struck bar is
   impulse-excited with a single fixed mode set; the played pitch must be
   realized by pitch-shifting the rendered note or scaling the mode
   frequencies, not by retuning the preset.
5. **Registry percussion-name bug (fixed)** — `_load_all` previously set
   `human = "Drum Kit"` for every percussion-family instrument, which would
   have mislabeled marimba as "Drum Kit" in `by_name`/tables. Guard narrowed to
   `key == "drum_kit"` only.

## Next candidates (roadmap, not done)

- Keys: Synth Pad (GM 88 = `MidiInstrument.SYNTH_PAD`), Harpsichord (GM 6)
- Guitar: Electric (GM 27/28/29/30)
- Percussion: Vibraphone (GM 11), Timpani (GM 47), Congas (ch9 notes 62 mute/63
  open — kit perc, no standalone GM program), Djembe (no GM — world family)
