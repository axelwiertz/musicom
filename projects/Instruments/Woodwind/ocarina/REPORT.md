# Ocarina — Nightly Instrument Research Report (2026-09-27)

## Instrument

- **Name**: Ocarina
- **Family**: Woodwind
- **GM Program**: 79
- **Pipeline Label**: GM_PROGRAMS[79] = "Ocarina" (exact match, no quirk)
- **SF2 Preset**: FluidR3 preset 79 = "Ocarina"

## Range

| Parameter | Value |
|---|---|
| Range Min | 55 (G3) |
| Range Max | 96 (C7) |
| Solo Range | (64, 88) — E4–E6 |
| Sweet Spot | (72, 84) — C5–C6 |

### Zones

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Low | 55–67 | G3–G4 | breathy, soft, dark chamber tone |
| Mid | 68–79 | G#4–G5 | sweetest, clearest, primary register |
| High | 80–96 | G#5–C7 | brighter, thinner, more airy |

## Role

lead, melody, ornament, accent, countermelody

**Mono-line quirk**: ocarina is a single breath line (vessel flute), NOT a
harmony/pad voice — no dense chords. The ocarina is the ONLY vessel flute
(Helmholtz resonator) in the KB — its range is inherently limited to about an
octave+a-fourth on a single chamber, so composition should keep lines within
roughly G3–C6 (55–84) for idiomatic tone.

## Articulations

| Technique | Velocity | Duration Factor |
|---|---|---|
| legato | 78 | 1.0 |
| staccato | 62 | 0.20 |
| accent | 92 | 0.85 |
| breath | 55 | 0.9 |
| trill | 72 | 0.35 |
| portamento | 70 | 1.2 |

## Synthesis Engine

**Primary**: PhaseModSynth (sine carrier + sine modulator, ratio 1.0, depth 0.8)
**Fallback**: Additive (4 partials: 0.9, 0.3, 0.1, 0.03 — strongest fundamental falloff)

The PhaseModSynth depth of 0.8 is the shallowest in the woodwind set, reflecting
the near-sine vessel flute tone (Helmholtz chamber suppresses upper harmonics).

**FM Defaults**:
- carrier_shape: sine
- mod_shape: sine
- mod_freq_ratio: 1.0
- mod_depth: 0.8
- attack: 0.06 s
- release: 0.12 s

## Production Defaults

| Parameter | Value |
|---|---|
| REVERB_TAIL | 1.6 s |
| EQ_BODY | (500, -1.5) — peaking cut |
| EQ_PRESENCE | (3000, 2.0) — peaking boost |
| EQ_AIR | (8000, 1.8) — highshelf |
| PAN | 0.0 |

## Registration Proof

### registry_table() output (Ocarina row)

```
| Woodwind | Ocarina | 79 | 55–96 | lead, harmony, accent |
```

### Verification lines

```
OCARINA.midi_program = 79 (should be 79)
by_name('ocarina') = <Instrument Ocarina (family=Woodwind, program=79, range=55-96)>
by_program(79) = <Instrument Ocarina (family=Woodwind, program=79, range=55-96)>
OCARINA.in_sweet_spot(74) = True
```

All pass. Registered in `instrument_registry.py` as:
- `_INSTRUMENT_MODULES["Woodwind.ocarina.ocarina"] = "ocarina"`
- `OCARINA = ALL_INSTRUMENTS["ocarina"]`

## Verification Results

### Zero-drift

```
Zero-drift: True (OK)
```

### MIDI

```
MIDI: /opt/data/projects/Research/outputs/ocarina_test.mid (111 bytes)
```
Size > 40 bytes ✓

### WAV (Solo render via FluidSynth + FluidR3_GM.sf2)

```
WAV (solo): /opt/data/projects/Research/outputs/ocarina_test.wav (759596 bytes)
```
Size > 40 bytes ✓

### Spectral Buzz Check

```
Spectral check: 4-8kHz buzz = 1.0% (OK)
```
Well below the 20% gate. The near-sine tone produces the cleanest spectral
profile in the woodwind set — no comb-filtering, no buzz.

### Stem Label

```
Ocarina -> 'Ocarina' (matches STEM_LABEL='Ocarina')
GM_PROGRAMS[79] = 'Ocarina' (exact match, no quirk)
```

### RenderPipeline Stem Render

```
Stems rendered (1 files):
  track00_Ocarina.wav (759596 bytes)
```
Single ocarina voice renders correctly. Stem label matches pipeline GM_PROGRAMS.

## Quirks

1. **No stem-label quirk**: GM_PROGRAMS[79] = "Ocarina" matches STEM_LABEL =
   "Ocarina" exactly. FluidR3 preset 79 = "Ocarina" also matches.
2. **Vessel flute identity**: The ocarina is the only Helmholtz-resonator
   (vessel flute) in the KB. All other woodwinds are tube flutes, reeds, or
   free reeds. This changes the synthesis recommendation (shallowest FM depth,
   additive fundamental dominance).
3. **Mono-line instrument**: Ocarina is a single breath line — no dense
   chords or harmony. Composition should keep lines within G3–C6 for
   idiomatic tone.
4. **Zelda cultural association**: The ocarina's most famous role is in the
   Legend of Zelda series — it excels as a signature melodic color in
   fantasy/folk/pastoral arrangements.

## Files Created

| File | Path |
|---|---|
| Constants | `projects/Instruments/Woodwind/ocarina/ocarina.py` |
| Research Doc | `projects/Instruments/Woodwind/ocarina/instrument.md` |
| Verify Script | `projects/Instruments/_test/verify_ocarina.py` |
| This Report | `projects/Instruments/Woodwind/ocarina/REPORT.md` |
| MIDI Output | `/opt/data/projects/Research/outputs/ocarina_test.mid` |
| WAV Output | `/opt/data/projects/Research/outputs/ocarina_test.wav` |
| Stems | `/opt/data/projects/Research/outputs/stems_ocarina/` |

## registry.md Updated

- Added changelog entry "Ocarina added (2026-09-27)" before Tubular Bells
- Added registry table row `| Woodwind | Ocarina | 79 | 55–96 | lead, harmony, accent |`
- Added stem label quirks row for program 79