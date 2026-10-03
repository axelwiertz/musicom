# Muted Trumpet (GM59) — Nightly Instrument Research Report

**Date**: 2026-10-03
**Job**: Nightly Instrument Research — LAYER-ALIGNED
**Instrument**: Muted Trumpet (GM59)
**Family**: Brass

---

## Instrument Identity

| Field | Value |
|---|---|
| **GM Program** | 59 |
| **GM Name** | "Muted Trumpet" |
| **MIDI Range** | 54–86 (F#3–D6) |
| **Sweet Spot** | 62–79 (D4–G5) |
| **Solo Range** | 60–84 (C4–C6) |
| **Role** | lead, countermelody, accent, melody, ornament |
| **Synthesis** | PhaseModSynth (FM brass) |

The muted trumpet is the same physical instrument as the open trumpet (GM56) with a mute inserted in the bell. The GM 59 specification defaults to the harmon mute (wah-wah effect), but the instrument covers all common mutes: straight, cup, harmon, plunger, bucket. The mute affects timbre, attack transient, and projection — not pitch range.

## Synthesis Engine

**Primary**: PhaseModSynth (`sound/synthesis/phase_mod.py`)

| Parameter | Muted Trumpet | Trumpet (GM56, reference) | Reason |
|---|---|---|---|
| carrier_shape | saw | saw | same brass bore |
| mod_freq_ratio | **2.0** | 1.5 | higher ratio = more nasal/focused muted tone |
| mod_depth | **2.5** | 4.0 | lower depth = less brassy edge, more focused |
| attack | **0.03 s** | 0.02 s | mute back-pressure resists air column |
| release | 0.12 | 0.1 | slightly longer |

**Fallbacks**: ModalSynth 'brass' preset (generic resonator), Additive (odd-harmonic stack + bandpass at 2 kHz for harmon-mute simulation).

## Register Zones

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Low | 54–65 | F#3–F4 | dark, breathy, less projection with mute |
| Mid | 66–79 | F#4–G5 | primary muted register — focused, nasal |
| High | 80–86 | G#5–D6 | bright, cutting — mute brightens altissimo |

## Articulations

| Technique | Velocity | Duration Factor | Description |
|---|---|---|---|
| sustain (straight mute) | 78 | 1.0 | metallic mute, even tone |
| staccato | 64 | 0.3 | crisp — cup mute jazz stabs |
| marcato | 92 | 0.9 | accented — harmon wah attack |
| cup | 66 | 0.9 | dark, mellow, warm — jazz ballad |
| harmon | 80 | 1.0 | nasal, wah-wah capability |
| plunger | 85 | 0.6 | talking effect, rhythmic |
| bucket | 60 | 0.95 | very dark, soft, velvety |
| flutter | 72 | 1.0 | flutter-tongue tremolo |

## Production Defaults

| Parameter | Value | Description |
|---|---|---|
| REVERB_TAIL | 1.2 s | room — muted trumpet is intimate; shorter than trumpet (1.8) |
| EQ_BODY | 400 Hz, -3.0 dB | peaking cut — remove mute honk/boxiness |
| EQ_PRESENCE | 3200 Hz, +2.5 dB | peaking boost — mute buzz + air clarity |
| EQ_AIR | 9000 Hz, +1.5 dB | highshelf — harmon mute sizzle |
| PAN | 0.0 | center for solo; -0.1..-0.25 for section |

## Stem Label & Quirks

| Check | Result |
|---|---|
| GM_PROGRAMS[59] | "Muted Trumpet" ✓ |
| Pipeline stem label | `Muted_Trumpet` ✓ |
| FluidR3 SF2 preset 59 | "Muted Trumpet" ✓ |
| **Quirk?** | **None** — all labels match exactly |

No quirk. Labels are globally consistent across pipeline, SF2, and instrument constants.

## Registration Proof

From `instrument_registry.py` verification run:

```
| Brass | Muted Trumpet | 59 | 54–86 | lead, harmony, accent |

MUTED_TRUMPET.midi_program = 59 (should be 59)
by_name('muted trumpet') = <Instrument Muted Trumpet (family=Brass, program=59, range=54-86)>
by_program(59) = <Instrument Muted Trumpet (family=Brass, program=59, range=54-86)>
MUTED_TRUMPET.in_sweet_spot(69) = True
```

## Verification Results

| Test | Result |
|---|---|
| **Zero-drift** | ✅ True (OK) |
| **MIDI size** | 161 bytes (> 40 ✓) |
| **WAV size (solo)** | 759,596 bytes (742 KB, > 40 ✓) |
| **Spectral buzz** | 6.4% (under 20% gate ✓ no comb-filtering) |
| **Stem label** | `track00_Muted_Trumpet.wav` ✓ |
| **PhaseModSynth smoke** | peak=0.785 (audible ✓) |

## Pipeline Quirks

**None.** GM program 59 "Muted Trumpet" is a clean label match:
- Pipeline GM_PROGRAMS[59] = "Muted Trumpet"
- FluidR3 preset 59 = "Muted Trumpet"
- STEM_LABEL = "Muted Trumpet"
- Stem file: `trackXX_Muted_Trumpet.wav`

## Files Created

| File | Path |
|---|---|
| Constants | `Brass/muted_trumpet/muted_trumpet.py` |
| Research | `Brass/muted_trumpet/instrument.md` |
| Verification | `Brass/muted_trumpet/verify_muted_trumpet.py` |
| Registry update | `instrument_registry.py` (+module, +constant, +verification) |
| Registry doc | `registry.md` (+changelog, +table row, +stem label) |
| Report | `Brass/muted_trumpet/REPORT.md` (this file) |