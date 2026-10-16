# Recorder — Instrument Report (2026-10-16)

## Instrument Identity

| Field | Value |
|---|---|
| **Type** | instrument |
| **Family** | Woodwind |
| **Name** | Recorder |
| **GM program** | 74 (0-indexed) |
| **GM name** | "Recorder" |
| **Pipeline stem label** | `Recorder` → `trackXX_Recorder.wav` |
| **FluidR3 preset** | 74 = "Recorder" |

## Background: Flute GM74 Data Bug

The existing `flute.py` had `MIDI_PROGRAM = 74` and `STEM_LABEL = "Recorder"`,
which was incorrect. Per General MIDI standard:
- **GM73** = Flute
- **GM74** = Recorder

The pipeline `GM_PROGRAMS[73]` = "Flute" and `GM_PROGRAMS[74]` = "Recorder"
were correct. The flute module was pointing to the wrong program. Fix applied:
- `flute.py`: MIDI_PROGRAM → 73, STEM_LABEL → "Flute"
- `flute/instrument.md`: Updated to GM73, removed all "Recorder" quirk references
- `recorder.py`: Added at GM74, its correct program number
- `by_program(74)` now returns Recorder (not Flute)

## Constants

```python
MIDI_PROGRAM = 74
GM_NAME = "Recorder"
STEM_LABEL = "Recorder"
RANGE_MIN = 60       # C4
RANGE_MAX = 100      # E7
SOLO_RANGE = (72, 89)   # C5–C7
SWEET_SPOT = (76, 84)   # E5–C6
```

### Register Zones

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Low | 60–74 | C4–D5 | Breathy, soft, hollow |
| Mid | 75–84 | D#5–C6 | Sweet, clear, liquid — classic recorder voice |
| High | 85–93 | C#6–D7 | Bright, piercing, Baroque brilliance |
| Altissimo | 94–100 | D#7–E7 | Thin, shrill, extreme overblown |

### Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Legato | 68 | 1.0 | Smooth slurred phrases |
| Staccato | 62 | 0.2 | Crisp single-tongue |
| Accent | 92 | 0.85 | Sharp sforzando |
| Double tongue | 72 | 0.07 | Rapid tu-ku-tu-ku |
| Triple tongue | 72 | 0.06 | tu-tu-ku pattern |
| Flutter | 65 | 1.0 | Guttural rolled-R |
| Breath | 50 | 0.85 | Airy pianissimo |
| Trill | 70 | 0.5 | Rapid finger trill |

### Synthesis

| Engine | Details |
|---|---|
| **PhaseModSynth** (primary) | sine carrier + sine mod, ratio 1.0, depth 1.5, attack 0.03 s, release 0.08 s |
| **AirPipe** (physical model) | stopped=False, length_scale=0.45, pressure=0.60 |
| **Additive** (fallback) | odd-harmonic stack 1:1.0, 3:0.40, 5:0.22, 7:0.10 |

### Production Defaults

| Parameter | Value |
|---|---|
| REVERB_TAIL | 1.6 s (intimate chamber/room) |
| EQ_BODY | (600, −1.5) cut duct/body resonance |
| EQ_PRESENCE | (3000, +2.5) articulation clarity |
| EQ_AIR | (9000, +1.5) fipple breath shimmer |
| PAN | −0.1 (slightly left) |

## Registration Proof

Registry verification output:

```
| Woodwind | Recorder | 74 | 60–100 | lead, melody, ornament, countermelody, accent |
  RECORDER.midi_program = 74 (should be 74)
  by_name('recorder') = <Instrument Recorder (family=Woodwind, program=74, range=60-100)>
  by_program(74) = <Instrument Recorder (family=Woodwind, program=74, range=60-100)>
  RECORDER.in_sweet_spot(79) = True
  RECORDER.in_sweet_spot(40) = False
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift | True (OK) |
| MIDI size | 111 bytes (> 40 ✓) |
| WAV size (solo) | 738,604 bytes (> 40 ✓) |
| Spectral buzz (4–8 kHz) | 1.3% (OK, below 20% gate) |
| Stem label | `track00_Recorder.wav` ✓ |
| Pipeline GM_PROGRAMS[74] | "Recorder" (match ✓) |
| FluidR3 preset 74 | "Recorder" (match ✓) |
| PhaseModSynth smoke test | peak=0.794 (> 0 ✓) |

## Quirks

- **No quirk**: GM_PROGRAMS[74] = "Recorder", FluidR3 preset 74 = "Recorder",
  STEM_LABEL = "Recorder" — all three labels match exactly.
- **Monophonic line instrument**: Recorder is a mono-line wind instrument —
  NO chords or harmony; write single-note melodic lines.
- **Limited dynamic range**: The fipple flute cannot play truly loud or truly
  soft; velocity simulation substitutes as a creative affordance.
- **GM73/GM74 fix applied**: Flute corrected to GM73 (its proper GM program),
  Recorder added at GM74.

## Report Location

`/opt/data/projects/Instruments/Woodwind/recorder/REPORT.md`