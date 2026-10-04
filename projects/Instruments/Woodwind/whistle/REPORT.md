# Nightly Instrument Research Report — Whistle (GM 78)

**Date**: 2026-10-04
**Instrument**: Whistle (Tin Whistle / Penny Whistle)
**Family**: Woodwind
**MIDI Program**: 78
**GM Name**: "Whistle"
**Stem Label**: "Whistle" — GM_PROGRAMS[78] → `trackXX_Whistle.wav` (exact match, **no quirk**)

---

## Constants (whistle.py)

| Field | Value |
|---|---|
| MIDI_PROGRAM | 78 |
| GM_NAME | "Whistle" |
| STEM_LABEL | "Whistle" |
| RANGE_MIN | 62 (D4) |
| RANGE_MAX | 93 (A6) |
| SOLO_RANGE | (67, 86) — G4 to D6 |
| SWEET_SPOT | (67, 86) — G4 to D6 |

### Zones

| Zone | Range |
|---|---|
| low | 62–69 (D4–A4) — 1st octave, round flute-like tone |
| mid | 70–79 (A#4–G5) — 2nd octave start, bright sweet folk zone |
| high | 80–93 (G#5–A6) — 2nd octave top + overblow, piercing |

### Articulations

| Technique | Velocity | Duration Factor |
|---|---|---|
| legato | 78 | 1.0 |
| staccato | 65 | 0.18 |
| cut | 76 | 0.06 |
| roll | 72 | 0.15 |
| breath | 55 | 0.9 |
| accent | 92 | 0.85 |

### Synthesis Engine

**Primary**: PhaseModSynth (`sound/synthesis/phase_mod.py`, SP-002)
- carrier_shape: sine, mod_shape: sine
- mod_freq_ratio: 1.0
- mod_depth: 1.5 (between ocarina 0.8 and shakuhachi 2.0)
- attack: 0.04 s (fast fipple onset, same as piccolo)
- release: 0.10 s

**Fallback**: Additive (`sound/synthesis/additive.py`)
- 6 harmonics: weights [0.9, 0.6, 0.4, 0.2, 0.1, 0.05]
- attack: 0.04, release: 0.10

### Production Defaults

| Param | Value |
|---|---|
| REVERB_TAIL | 1.6 s (intimate folk room) |
| EQ_BODY | 500 Hz, -2.0 dB (cut honk/boxiness) |
| EQ_PRESENCE | 3000 Hz, +2.5 dB (fipple edge brightness) |
| EQ_AIR | 7000 Hz, +1.5 dB (gentle air, avoid shrill) |
| PAN | 0.0 (center solo; ±0.2 ensemble) |

---

## Registration Proof (instrument_registry.py)

Loaded successfully from `Woodwind.whistle.whistle` → key `whistle`:

```
Registry table row:
| Woodwind | Whistle | 78 | 62–93 | lead, harmony, accent |

WHISTLE.midi_program = 78 (should be 78)
by_name('whistle') -> <Instrument Whistle (family=Woodwind, program=78, range=62-93)>
by_program(78) -> <Instrument Whistle (family=Woodwind, program=78, range=62-93)>
WHISTLE.in_sweet_spot(72) = True
WHISTLE.in_sweet_spot(48) = False
```

Convenience constant `WHISTLE` added to `instrument_registry.py`.

---

## Engine Verification Results

### UnitMatrixComposer (1 bar, 1 voice solo)

| Check | Result |
|---|---|
| Zero-drift | True (OK) |
| MIDI size | 120 bytes (> 40 ✓) |
| WAV size (solo) | 810,028 bytes (> 40 ✓) |
| Spectral 4–8 kHz buzz | 0.4% (well under 20% gate — clean single voice) |

### Stem Label

GM_PROGRAMS[78] = "Whistle" → `track00_Whistle.wav` (810,028 bytes)
**No quirk**: label matches exactly.

### SoundFont Mapping

FluidR3_GM.sf2 preset 78 = "Whistle" (phdr chunk verified)

### PhaseModSynth Smoke Test

| Param | Value |
|---|---|
| Note | C5 (523.25 Hz) |
| Peak amplitude | 0.794 |
| Audio length | 11,025 samples (0.5 s at 22050 Hz) |

PhaseModSynth confirms a viable whistle tone at the recommended parameters (mod_depth 1.5, attack 0.04, release 0.10).

---

## Stem-Label Quirks

**None.** GM 78 in the pipeline `GM_PROGRAMS` list is exactly "Whistle", matching the instrument's GM_NAME and STEM_LABEL exactly. No potential confusion like the flute/GM74="Recorder" quirk.

---

## Files Created / Modified

| File | Action |
|---|---|
| `Woodwind/whistle/instrument.md` | CREATED — full research doc |
| `Woodwind/whistle/whistle.py` | CREATED — importable constants |
| `instrument_registry.py` | MODIFIED — module entry + WHISTLE constant + verification |
| `registry.md` | MODIFIED — changelog entry added |
| `_test/verify_whistle.py` | CREATED — full verification script |
| `_test/whistle_test.mid` | CREATED — 120 bytes (verification artifact) |
| `_test/whistle_test.wav` | CREATED — 810 KB (verification artifact) |
| `_test/stems_whistle/track00_Whistle.wav` | CREATED — 810 KB (stem render) |
| `Woodwind/whistle/REPORT.md` | CREATED — this file |