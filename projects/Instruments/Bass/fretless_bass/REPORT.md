# REPORT — Fretless Bass (GM35)

**Date**: 2026-10-27
**Family**: Bass (third entry: 33 Electric Bass finger, 35 Fretless, 38 Synth Bass 1)
**Files**: `Bass/fretless_bass/instrument.md`, `Bass/fretless_bass/fretless_bass.py`
**Test**: `_test/verify_fretless_bass.py`, `_test/_probe_fretless_bass.py`
**Registry**: `instrument_registry.py` (`_INSTRUMENT_MODULES` + `FRETLESS_BASS`)

---

## 1. Instrument

The fretless electric bass — a solidbody electric bass with the frets removed
and the fingerboard filled/sanded smooth. Pitch is set by finger POSITION
rather than a fret crown, which gives:

- continuous **portamento/glissando** (the signature slide),
- a nasal, vocal **"mwah"** midrange from the compliant fingerboard stop,
- **no fretwire click** on attack (rounder, more contrabass-like thump).

Reference players: Jaco Pastorius, Pino Palladino, Mick Karn, Sting,
Tony Franklin, Gary Willis, Percy Jones.

Distinct from GM33 Electric Bass (finger) — same body/electronics family,
different string stop — and from GM38 Synth Bass 1 (oscillator + filter, no
string at all).

## 2. MIDI / GM

| Field | Value |
|---|---|
| MIDI program | **35** (0-indexed GM1 "Fretless Bass") |
| GM name | `Fretless Bass` |
| FluidR3 preset 35 | `Fretless Bass` (phdr-verified — exact match) |
| RenderPipeline `GM_PROGRAMS[35]` | `"Fretless Bass"` → `trackXX_Fretless_Bass.wav` |
| Stem quirk | **none** (pipeline label + SF2 preset both "Fretless Bass") |
| MidiInstrument enum | absent (enum exposes only 10) — raw `program=35` |
| Channel | 0–9 melodic; channel 9 = drum map |
| Collisions | **none** — 33 and 38 were the only Bass programs claimed |

## 3. Range

| Field | Value |
|---|---|
| RANGE_MIN / RANGE_MAX | 24 / 72 (C1–C5) |
| 4-string tuning | E1–G3 = 28–55 (24-fret board reaches ~G4 67) |
| 5-string extension | B0 = MIDI 23 |
| SWEET_SPOT | 33–55 (A1–G3) |
| SOLO_RANGE | 28–60 (E1–C4) |

Zones: `sub` 24–35, `groove` 36–50, `singing_mid` 51–62, `upper` 63–72.

Empirical FluidR3 pitch sweep (solo render, velocity 90, RMS):

| MIDI | 24 | 28 | 33 | 40 | 45 | 50 | 55 | 60 | 62 | 67 | 72 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RMS | 1817 | 1740 | 1826 | 1940 | 2430 | 1877 | 1842 | 1809 | 1766 | 1519 | 1043 |

No gaps; level essentially flat 24–62 (45 is the patch's own "mwah" sample
peak), falls off at 72 → sustained lines at or below C4 (60), 63–72 for
exposed fills only.

## 4. Articulations (velocity, duration_factor)

| Technique | Vel | Dur | Note |
|---|---|---|---|
| sustain | 70 | 1.00 | round fingerboard pluck, long ring |
| staccato | 76 | 0.30 | palm/board damping, dry |
| slide | 72 | 1.05 | signature glissando between pitches |
| portamento | 64 | 1.00 | bend into target — GM patch ignores CC5/CC65 |
| vibrato | 76 | 0.90 | finger-roll, 5–6 Hz |
| harmonic | 62 | 1.00 | natural node touch (12th/7th/5th) |
| double_stop | 80 | 0.70 | adjacent strings, third/sixth |
| ghost | 36 | 0.12 | dead-note tap, no pitch |
| arco | 70 | 1.00 | bowed with double bass bow, cello-like |

## 5. Role

`bass, melody, countermelody, groove, slide, color`

- Primary: root–fifth bass support with slide approach notes.
- Melody: the one bass that can carry a line — keep it in 51–62.
- Countermelody: cello/trombone register, excellent under a vocal.
- NOT pad/chord, NOT slap (needs frets), NOT high lead above C4.

## 6. Synthesis engine

**Primary: Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — a
plucked-string waveguide is the physical model; the loop low-pass IS the
fingerboard damping.

```python
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,   # > fretted bass 0.9970 — bare board damps less
    "lowpass_hz": 2200.0,  # darker than fretted: the nasal "mwah" band
    "width": 0.55,
    "excitation": "pluck",
    "role": "bass",
}
```

**Secondary: BowedString** (arco only) — `bow_velocity` 0.18, `bow_force` 1.4,
`bow_position` 0.18 (sul tasto), `lpf_coef` 0.6, attack 0.16 s,
vibrato 5.4 Hz / 0.004 depth.

**Fallback: ModalSynth** preset `'string'` (generic plucked body, no pickup
colour). **PhaseModSynth** only for a deliberately synthetic fretless colour.

## 7. Constants (fretless_bass.py)

```python
MIDI_PROGRAM = 35
GM_NAME = "Fretless Bass"
STEM_LABEL = "Fretless_Bass"
RANGE_MIN = 24
RANGE_MAX = 72
SOLO_RANGE = (28, 60)
SWEET_SPOT = (33, 55)
ZONES = {
    "sub": (24, 35),
    "groove": (36, 50),
    "singing_mid": (51, 62),
    "upper": (63, 72),
}
ARTICULATIONS = {
    "sustain": (70, 1.0),
    "staccato": (76, 0.30),
    "slide": (72, 1.05),
    "portamento": (64, 1.0),
    "vibrato": (76, 0.90),
    "harmonic": (62, 1.0),
    "double_stop": (80, 0.70),
    "ghost": (36, 0.12),
    "arco": (70, 1.0),
}
SYNTHESIS = "karplus"
MODAL_PRESET = "string"
REVERB_TAIL = 1.6
EQ_BODY = (250, -2.5)
EQ_PRESENCE = (800, 3.0)     # the "mwah" formant — THE fretless EQ move
EQ_AIR = (5000, 1.5)
PAN = 0.0
```

`midi_to_freq(midi)` — standard A440 equal temperament.

## 8. Registration proof

`_INSTRUMENT_MODULES` entry:

```python
"Bass.fretless_bass.fretless_bass": "fretless_bass",
```

Convenience constant:

```python
FRETLESS_BASS = ALL_INSTRUMENTS["fretless_bass"]
```

`registry_table()` now contains (Bass block, auto-generated from code):

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
| Bass | Fretless Bass | 35 | 24–72 | bass, melody, countermelody, groove, slide, color |
| Bass | Synth Bass 1 | 38 | 24–84 | bass, rhythm, groove, accent |
```

Verification block output (bottom of `instrument_registry.py`, exit code 0):

```
=== Fretless Bass (GM35) ===
  FRETLESS_BASS.midi_program = 35 (should be 35)
  by_name('fretless bass') = <Instrument Fretless Bass (family=Bass, program=35, range=24-72)>
  by_name('FRETLESS BASS') = <Instrument Fretless Bass (family=Bass, program=35, range=24-72)>
  by_program(35) = <Instrument Fretless Bass (family=Bass, program=35, range=24-72)>
  FRETLESS_BASS.in_sweet_spot(43) = True
  FRETLESS_BASS.in_sweet_spot(24) = False
  FRETLESS_BASS.range_min = 24 FRETLESS_BASS.range_max = 72
  FRETLESS_BASS.stem_label = 'Fretless_Bass'
```

Full run saved: `_test/final_registry_fretless.txt`. Registry load count 78.

## 9. Verification results (`_test/verify_fretless_bass.py`)

```
Registry: <Instrument Fretless Bass (family=Bass, program=35, range=24-72)>
Fretless Bass: program=35 gm='Fretless Bass' stem='Fretless_Bass' sweet=(33, 55) A4=440.0Hz
Fretless Bass: E1=41.20Hz A1=55.00Hz G3=196.00Hz

Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/fretless_bass_test.mid (172 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
WAV (solo): /opt/data/projects/Instruments/_test/fretless_bass_test.wav (751148 bytes)
Spectral check: 4-8kHz buzz energy = 4.6% (OK)

Stem label: GM_PROGRAMS[35] = 'Fretless Bass'
SF2 preset 35 -> 'Fretless Bass'

Stems rendered (2 files):
  track00_Fretless_Bass.wav (751148 bytes)
  track01_Drums.wav (706092 bytes)

Karplus-Strong E2: peak=0.290 head_rms=0.0069 tail_rms=0.0005
BowedString(arco) OK: BowedString

ALL CHECKS PASSED
```

- Composition: 1 bar / 1 section, voice 0 Fretless Bass (E2–G2–slide–A2–B2–A2,
  terminal note flush at BAR 1920), voice 1 drum kit on ch9 (context only).
- Audio: **solo track 1 only** — no unison doubling (2026-09-01 rule).
- MIDI 172 bytes > 40 ✓, WAV 751,148 bytes > 40 ✓, stems > 40 ✓.

## 10. Quirks found

1. **SF2 ignores portamento.** FluidR3 preset 35 has slides baked into some
   velocity layers, but CC5/CC65 portamento is not honoured — write slides as
   fast chromatic runs of short notes (e.g. 44 → 45 at 16th spacing) unless
   the renderer applies pitch-bend.
2. **Effectively monophonic.** No chords; thumb-position dyads are an
   overdub, not patch behaviour. Do not ask the composer for a 3-note
   "fretless chord".
3. **No unison doubling** with another melodic patch on identical pitches
   (comb filtering). Octaves or a bass note an octave+ below are fine; so is
   a drum kit.
4. Patch level peaks at MIDI 45 (RMS 2430 vs ~1800 neighbours) — the sample
   set's "mwah" layer; trim ~1.5 dB on that pitch band in dense mixes.
5. Above MIDI 67 the fundamental thins sharply (RMS 1043 at 72) — treat 63–72
   as an exposed-solo register, not sustained support.
