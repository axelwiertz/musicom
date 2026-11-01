# Acoustic Bass (GM32) — Nightly Instrument Research Report

**Date**: 2026-11-01 · **Family**: Bass · **Folder**: `Bass/acoustic_bass/`

## Instrument

GM32 **Acoustic Bass** = the upright double bass played **pizzicato** — the
jazz walking-bass / bluegrass slap / rockabilly thump voice. The same
instrument as the orchestral Contrabass (GM43) but in its plucked idiom:
finger-plucked gut/steel strings over a huge wooden body give a
fundamental-rich woody thump with a long natural ring and NO electronics in
the signal path. Reference players: Ray Brown, Paul Chambers, Ron Carter,
Charlie Haden, NHØP, Stanley Clarke.

**Family context** (Bass family now complete as 4 voices):

| Program | Instrument | Voice |
|---|---|---|
| 32 | Acoustic Bass | upright pizz (this entry) |
| 33 | Electric Bass (finger) | amplified magnetic-pickup |
| 35 | Fretless Bass | frets-pulled electric |
| 38 | Synth Bass 1 | oscillator + filter |

## Program

- **MIDI_PROGRAM = 32** (GM1 Acoustic Bass; 0-indexed — matches FluidR3
  preset 32 AND the RenderPipeline `GM_PROGRAMS[32]`).
- **Not** in `structures/instrument.py` `MidiInstrument` enum (legacy 10-only
  enum) — use raw `program=32` in `add_voice`; the registry is the full KB.
- Channel: melodic channel (0–9) — channel 9 triggers the drum-kit map.

## Range

- **RANGE_MIN = 24 (C1), RANGE_MAX = 72 (C5)** — idiomatic writing band.
  Real 4-string upright: E1–G4 = 28–67 (tuned E1 A1 D2 G2 = 28, 33, 38, 43);
  5-string adds low B0 = 23.
- **SWEET_SPOT = (40, 57)** — E2–A3, the jazz walking pocket.
- **SOLO_RANGE = (36, 60)** — C2–C4.

Zones:

| Zone | MIDI | Register |
|---|---|---|
| sub | 24–35 | chest thump, felt > heard, single notes only |
| walking | 36–52 | PRIMARY — jazz walking, root-fifth, bluegrass half-notes |
| mid | 53–64 | melodic fills, pizz solos, singing woody tone |
| high | 65–72 | thumb-position, thin, cello-like, exposed solos only |

**Empirical FluidR3 pitch sweep** (velocity 90, held 0.5 s mid-note RMS,
notes 24/28/33/36/40/45/48/52/55/60/64/67/72):

```
note 24: rms=0.1274    note 28: rms=0.1185    note 33: rms=0.0951
note 36: rms=0.0896    note 40: rms=0.1033    note 45: rms=0.0589
note 48: rms=0.0785    note 52: rms=0.0690    note 55: rms=0.0769
note 60: rms=0.0658    note 64: rms=0.0615    note 67: rms=0.0584
note 72: rms=0.0497
audible: 13/13 notes — no gaps
```

Smooth rolloff 0.1274 → 0.0497, NO treble cliff. Patch also plays 20–96
(probe: note 20 rms=0.1272, 84 rms=0.0246, 96 rms=0.0175) — wider than the
idiomatic band; SF2 never clips a composition.

## Role

bass, rhythm, countermelody, accent, melody — a monophonic line instrument
(walking bass, root-fifth groove, slap patterns), NOT a chord/comping voice,
NOT a pad. The pizz ring IS the identity (long, woody, fundamental-rich).

## Articulations (velocity, duration_factor)

| Technique | Vel | Dur | Timbre |
|---|---|---|---|
| pizz | 74 | 1.0 | default finger pluck — round, woody |
| walking | 72 | 0.95 | quarter-note pulse — even, detached |
| slap | 96 | 0.30 | rockabilly string slap — thwack |
| ghost | 38 | 0.15 | dead-note damp — groove filler |
| legato | 70 | 1.0 | slurred pizz / hammer |
| slide | 64 | 1.10 | fingered glissando |
| arco | 78 | 1.0 | jazz bow — sustained, reedy |
| staccato | 68 | 0.35 | short damped pizz |
| accent | 92 | 0.85 | emphatic downbeat |

## Synthesis Engine

**Karplus-Strong primary** (SP-011 — plucked waveguide = exact physical
model):

```python
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9975,   # long pizz ring — between electric bass 0.9970
                           # and harp 0.9985 (sitar/fretless class)
    "lowpass_hz": 1600.0,  # DARKEST of the plucked basses — the huge wooden
                           # body rolls the top off into the woody thump band
    "width": 0.5,
    "excitation": "pluck",
    "noise_component": 0.02,  # finger scrape — part of the idiom
    "role": "bass",
}
```

- **BowedString secondary** (ARCO only: bow_velocity 0.18, bow_force 1.3,
  bow_position 0.20 sul tasto, lpf_coef 0.6, attack 0.14 s — a bowed
  acoustic bass reads as a woody cello).
- **ModalSynth `'string'`** — weak fallback (no body resonance).
- **PhaseModSynth** — weak alternative (sine FM, ratio 1.0, depth 1.6).

Smoke tests: Karplus E2 peak 0.290, head_rms 0.0069 → tail_rms 0.0005 (real
string decay, not a DC plateau); BowedString constructs and renders.

## Production Defaults

```python
REVERB_TAIL = 1.8        # jazz-club room — small wooden room, not a hall
EQ_BODY = (220, -2.5)    # cut body boxiness (woody thump is LOWER ~100 Hz)
EQ_PRESENCE = (700, 2.5) # boost finger attack / pizz growl
EQ_AIR = (4000, 1.5)     # shelf — finger scrape / string shimmer
PAN = 0.0                # center — universally mono
```

## Registration Proof

`instrument_registry.py` additions:

```python
_INSTRUMENT_MODULES["Bass.acoustic_bass.acoustic_bass"] = "acoustic_bass"
ACOUSTIC_BASS = ALL_INSTRUMENTS["acoustic_bass"]
# registry_table() role row: elif low == "acoustic bass": bass, rhythm, countermelody, accent, melody
```

Registry verification run (`/opt/data/micromamba/envs/musicom/bin/python
instrument_registry.py`) — new row in the table:

```
| Bass | Acoustic Bass | 32 | 24–72 | bass, rhythm, countermelody, accent, melody |

=== Acoustic Bass (Upright pizz, GM32) ===
  ACOUSTIC_BASS.midi_program = 32 (should be 32)
  by_name('acoustic bass') = <Instrument Acoustic Bass (family=Bass, program=32, range=24-72)>
  by_name('ACOUSTIC BASS') = <Instrument Acoustic Bass (family=Bass, program=32, range=24-72)>
  by_program(32) = <Instrument Acoustic Bass (family=Bass, program=32, range=24-72)>
  ACOUSTIC_BASS.in_sweet_spot(48) = True
  ACOUSTIC_BASS.in_sweet_spot(20) = False
  ACOUSTIC_BASS.range_min = 24 ACOUSTIC_BASS.range_max = 72
  ACOUSTIC_BASS.stem_label = 'Acoustic_Bass'
```

Full output: `_test/registry_out_acoustic_bass.txt`.

## Verification Results

Verify script: `_test/verify_acoustic_bass.py` (structural template
`_test/verify_fretless_bass.py`; audio render = INSTRUMENT SOLO ONLY per the
2026-09-01 comb-filter rule — drums ride along for context but are excluded
from the solo render).

```
Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/acoustic_bass_test.mid (172 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2  (discover_soundfont())
WAV (solo): /opt/data/projects/Instruments/_test/acoustic_bass_test.wav (727852 bytes)
Spectral check: 4-8kHz buzz energy = 5.3% (OK, < 20% gate, no comb-filtering)

Stem label: GM_PROGRAMS[32] = 'Acoustic Bass'   (matches exactly, no quirk)
SF2 preset 32 -> 'Acoustic Bass'                (phdr-verified, matches)

Stems rendered (2 files):
  track00_Acoustic_Bass.wav (727852 bytes)
  track01_Drums.wav (706092 bytes)

Karplus-Strong E2: peak=0.290 head_rms=0.0069 tail_rms=0.0005
BowedString(arco) OK: BowedString
ALL CHECKS PASSED
```

## Stem-Label Quirks

**None.** `GM_PROGRAMS[32]` = "Acoustic Bass" (pipeline), FluidR3 preset 32 =
"Acoustic Bass" (phdr-verified), `STEM_LABEL = "Acoustic_Bass"` — all three
agree. Contrast with the known quirks elsewhere: GM74 Flute → "Recorder",
GM109 → "Bag pipe", GM111 → "Shanai".

## Writing Quirks (for composition jobs)

1. **Monophonic** — one note at a time; double-stops on adjacent strings are
   a rare overdub. Never ask for a 3-note "acoustic bass chord".
2. **SF2 honours no portamento** — write a slide as a fast chromatic run or
   pitch-bend.
3. **Slap is velocity-hungry** — vel ≥ 90 for the rockabilly thwack; the
   walking line sits 65–80.
4. **No unison doubling** with another melodic patch on the same pitches
   (2026-09-01 comb-filter rule) — octaves or a low bass note an octave+
   below are fine, and a drum kit is fine.
5. Humanize DNA: family Bass (5.0 ms timing, 4.0 vel, 8.0 ms layback — the
   bass lays back, bass-family precedent) via `humanize_dna` "bass" branch.

## Files Written

- `Bass/acoustic_bass/instrument.md` — full research reference
- `Bass/acoustic_bass/acoustic_bass.py` — importable constants
- `instrument_registry.py` — module dict entry + `ACOUSTIC_BASS` constant +
  registry_table role row + verification block (registry load count 81 → 82)
- `registry.md` — changelog entry (2026-11-01), Registry table row, stem-label
  table row
- `README.md` — count refresh (82 registry / 76 folders)
- `_test/verify_acoustic_bass.py` — end-to-end verification (zero-drift, MIDI,
  solo WAV, spectral, stem label, SF2 phdr, stems on disk, KS smoke, bowed
  construct)
- `_test/sweep_acoustic_bass.py` — FluidR3 pitch sweep
- `_test/registry_out_acoustic_bass.txt` — registry verification output
