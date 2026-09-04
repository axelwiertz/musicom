# Shamisen — Nightly Instrument Research Report (2026-09-04)

New instrument added to the musicom Instruments reference library. Third
World-family entry (after Sitar GM104 and Koto GM107 — both added 2026-09-02
by earlier nightly runs). World family now has three plucked-string
instruments: sitar, koto, shamisen.

## Instrument

| Field | Value |
|---|---|
| Family | World |
| Name | Shamisen |
| MIDI program | **106** (GM1, 0-indexed — matches pipeline + SF2) |
| GM name | Shamisen |
| Full range | A2 (45) – F6 (89) |
| Solo range | A3 (57) – C6 (84) |
| Sweet spot | C4 (60) – G5 (79) |
| Role | lead, melody, ornament, drone, countermelody |
| Synthesis | Karplus-Strong (primary), ModalSynth 'string' (fallback), PhaseModSynth (cheap) |

3-string Japanese lute, struck with a large wooden plectrum (bachi). Signature
tone: sharp percussive attack (wood-on-skin transient) + the *sawari* — a
sympathetic buzz at the nut (cousin of the koto's sawari). Honchoshi open
tuning D-A-D (D3-A3-D4 = MIDI 50-57-62). The shamisen is a **line instrument**
(folk/min'yo + kabuki theatre) — composition jobs write monophonic
melodic/ostinato lines, NOT dense chords.

## Range zones

| Zone | MIDI | Register |
|---|---|---|
| low | 45–56 | niagari (thick 1st) string — dark, gut thump |
| mid | 57–75 | middle string — primary melodic register |
| high | 76–89 | 3rd string — bright, thin, cutting |

Empirical FluidR3 pitch sweep (RMS per note, 24–96): preset 106 audible
across the WHOLE span (24–96), no gaps — the SoundFont never clips a
composition within or beyond the physical range.

## Articulations (velocity, duration_factor)

| Technique | Velocity | Dur | Meaning |
|---|---|---|---|
| pluck | 80 | 1.0 | standard bachi stroke, sharp attack, natural decay |
| tsubushi | 92 | 0.33 | hard bachi slap on skin head — percussive thump |
| suzume | 86 | 0.25 | grace-note chirp ornament |
| uchijime | 60 | 0.12 | left-hand damp after pluck — short, dry |
| hikiyose | 72 | 1.5 | bend up ~1–3 semitones — vocal |
| tremolo | 78 | 2.0 | suki fast repeated strokes — sustained tension |

## Constants (shamisen.py — full)

```python
MIDI_PROGRAM = 106
GM_NAME = "Shamisen"
STEM_LABEL = "Shamisen"
RANGE_MIN = 45; RANGE_MAX = 89
SOLO_RANGE = (57, 84); SWEET_SPOT = (60, 79)
ZONES = {"low": (45, 56), "mid": (57, 75), "high": (76, 89)}
ARTICULATIONS = {"pluck": (80, 1.0), "tsubushi": (92, 0.33), "suzume": (86, 0.25),
                 "uchijime": (60, 0.12), "hikiyose": (72, 1.5), "tremolo": (78, 2.0)}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9955, "width": 0.40, "role": "lead"}
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 2.5,
               "mod_depth": 3.0, "attack": 0.002, "release": 0.2}
REVERB_TAIL = 1.2
EQ_BODY = (300, -2.0); EQ_PRESENCE = (2800, 2.0); EQ_AIR = (8000, 1.0)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## Registration proof

`instrument_registry.py` updated:
- `_INSTRUMENT_MODULES["World.shamisen.shamisen"] = "shamisen"`
- `SHAMISEN = ALL_INSTRUMENTS["shamisen"]` convenience constant
- `registry_table()` role branch for shamisen
- `__main__` verification lines for SHAMISEN

Registry run output (full `registry_table()` INCLUDING new row + verification):

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
...
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |

Verification:
  ...
  SHAMISEN.midi_program = 106 (should be 106)
  by_name('shamisen') = <Instrument Shamisen (family=World, program=106, range=45-89)>
  by_program(106) = <Instrument Shamisen (family=World, program=106, range=45-89)>
  SHAMISEN.in_sweet_spot(69) = True
```

ALL_INSTRUMENTS count = **21** (was 20).

## Verification results (verify_shamisen.py)

| Check | Result |
|---|---|
| Import through registry (`by_name('shamisen')`) | ✓ 21 instruments |
| Zero-drift (`validate()`) | ✓ True (OK — terminal landmark flush at BAR) |
| MIDI export | ✓ 135 bytes (> 40) |
| WAV solo render (FluidR3 via `discover_soundfont()`) | ✓ 915,756 bytes (> 40) |
| Spectral buzz check (4–8 kHz) | ✓ 7.4% (≤ 20%) — solo shamisen, no comb-filter buzz |
| Stem label (pipeline GM_PROGRAMS[106]) | ✓ "Shamisen" → `track00_Shamisen.wav` on disk |
| SF2 preset 106 (phdr chunk) | ✓ "Shamisen" (FluidR3_GM.sf2) |
| Karplus-Strong ring | ✓ tail_rms/peak(0.5–1 s) = 0.007 vs 0.002 dull control (~3.5×, punchy dry) |
| FluidR3 audible span (RMS sweep) | ✓ 24–96, no gaps |

Voice stack was Shamisen SOLO (ch0) + one low bass A1 (ch1, GM33, octave+
below) — no second melodic patch on the same pitches (no unison doubling).

Stems rendered: `track00_Shamisen.wav`, `track01_Electric_Bass_finger.wav`.

## Quirks found

1. **Stem label**: GM_PROGRAMS[106] = "Shamisen" — matches exactly, **no
   quirk** (unlike GM74→"Recorder" or ch9 pgm0→"Acoustic_Grand_Piano").
2. **SF2 preset**: FluidR3 preset 106 = "Shamisen" — matches exactly (unlike
   French Horn 60→"French Horns" or Oboe 68→"Oboe (Orch)").
3. **Physical range vs SF2 range**: FluidR3 preset 106 is audible 24–96
   (empirical RMS sweep), far wider than the 3-string instrument's practical
   A2–F6 (45–89). Constants use the PHYSICAL range; the SF2 never clips.
4. **Line-instrument quirk** (musical, not pipeline): shamisen is monophonic
   by design — dense chords unidiomatic (contrast: koto allows sparse 2–3
   note clusters; shamisen role excludes harmony). Documented in
   instrument.md + registry.md.
5. **MidiInstrument enum**: `structures/instrument.py` only exposes 10
   programs (PIANO=0, CHURCH_ORGAN=20, ..., FLUTE=74) — no 106. Raw GM
   number used directly; the registry is the full KB (as designed).

## Files

- `/opt/data/projects/Instruments/World/shamisen/instrument.md` — full research
- `/opt/data/projects/Instruments/World/shamisen/shamisen.py` — importable constants
- `/opt/data/projects/Instruments/World/shamisen/REPORT.md` — this report
- `/opt/data/projects/Instruments/instrument_registry.py` — registered
- `/opt/data/projects/Instruments/registry.md` — changelog + table + quirks
- `/opt/data/projects/Instruments/_test/verify_shamisen.py` — verification script
- `/opt/data/projects/Instruments/_test/sweep_shamisen.py` — FluidR3 pitch-sweep probe
- `/opt/data/projects/Instruments/_test/shamisen_test.mid` — 135 B
- `/opt/data/projects/Instruments/_test/shamisen_test.wav` — solo render, 915,756 B
- `/opt/data/projects/Instruments/_test/stems_shamisen/` — pipeline stems
