# Overdriven Guitar — Nightly Instrument Research Report

**Date**: 2026-10-14
**Instrument**: Overdriven Guitar
**Family**: Guitar
**MIDI Program**: 29 (GM1 — Overdriven Guitar)
**GM Name**: "Overdriven Guitar"

---

## Instrument Overview

The Overdriven Guitar (GM29) is the solidbody electric guitar pushed into
tube-amp saturation (soft-clipping distortion). It is the classic rock/metal
lead and rhythm voice — Marshall Plexi-style, Vox AC15, Fender Bassman on 10.

Distinct from the existing Guitar-family entries:
- **Acoustic Guitar (nylon)** GM24 — warm fingerstyle/classical
- **Acoustic Guitar (steel)** GM25 — bright strumming/fingerpicking
- **Clean Electric Guitar** GM27 — clean amp, rhythm comping/chords
- **Overdriven Guitar** GM29 — saturated, compressed, sustained rock lead

## MIDI / GM

| Property | Value |
|----------|-------|
| Program | 29 |
| GM Name | Overdriven Guitar |
| Channel | Any melodic (0-9); polyphonic (6 strings) |
| Pipeline stem label | GM_PROGRAMS[29] = "Overdriven Guitar" → `trackXX_Overdriven_Guitar.wav` |
| FluidR3 preset | 29 = "Overdrive Guitar" (cosmetic: "Overdrive" vs "Overdriven", no routing impact) |
| STEM_LABEL | `Overdriven_Guitar` |

## Range

| Zone | MIDI | Pitches | Character |
|------|------|---------|-----------|
| Full range | 28–84 | E1–C6 | GM patch span |
| Low strings | 28–47 | E1–B2 | Palm-muted chugs, low power-chord roots |
| Mid (sweet spot) | 48–64 | C3–E4 | Rich harmonic saturation, fat leads |
| High | 65–84 | F4–C6 | Bright cutting single-note leads |

- **SOLO_RANGE**: (45, 76) = A2–E6 (idiomatic lead zone)
- **SWEET_SPOT**: (52, 72) = E3–C5 (richest harmonic saturation)
- **RANGE_MIN**: 28 (E1 — GM patch floor)
- **RANGE_MAX**: 84 (C6 — GM patch ceiling)

## Articulations

14 articulations defined:

| Technique | Velocity | Duration | Description |
|-----------|----------|----------|-------------|
| sustained_lead | 82 | 1.0 | Singing legato line — default overdrive articulation |
| power_chord | 88 | 0.40 | Root-fifth power chord — #1 rhythm technique |
| palm_mute | 55 | 0.12 | Edge-of-hand damped percussive chug |
| open_chord | 75 | 0.45 | Full strumed chord, compressed by drive |
| staccato | 65 | 0.15 | Quick muted chord stab |
| bend | 95 | 1.20 | String bend — pitch rise + max sustain |
| hammer_on | 78 | 0.60 | Legato slur up — pronounced on overdrive |
| pull_off | 68 | 0.60 | Legato slur down — connected line |
| slide | 72 | 0.90 | Continuous pitch glide |
| vibrato | 80 | 1.0 | Arm whammy or finger vibrato |
| harmonic | 92 | 0.40 | Natural overtone, sustained by amp |
| grace | 70 | 0.10 | Quick pre-note flick (B.B. King style) |
| accent | 98 | 0.35 | Emphatic pick dig |
| feedback | 65 | 1.50 | Sustained note from amp–guitar coupling |

## Synthesis

### Primary: Karplus-Strong with non-linear saturation

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | 0.9990 | HIGHEST in plucked set — overdrive sustain ~5-10 s |
| excitation | "pick" | Bright pick attack |
| width | 0.55 | Compressed envelope |
| lowpass_hz | 4000 | Amp speaker roll-off warmth |
| noise_component | 0.060 | Tube hiss + amp floor (2.4x clean) |
| saturation | 0.60 | Soft-knee clipping |

### Secondary: PhaseModSynth

Saw carrier + high mod_depth (4.0) for harmonic foldover.

### Tertiary: Additive

8-harmonic stack approximating clipped waveform.

## Production Defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 2.2 s | Hall/room — hybrid spring+room ambience |
| EQ_BODY | (400, -4.0) | Peaking cut — reduce compression mud |
| EQ_PRESENCE | (2200, 3.0) | Peaking boost — cutting edge presence |
| EQ_AIR | (6000, 0.5) | High shelf — gentle top, not shrill |
| PAN | -0.15 | Centre-left for mono stage amp |

## Stem Label Quirks

**No quirk.** GM_PROGRAMS[29] = "Overdriven Guitar" → sanitized
`Overdriven_Guitar`. FluidR3 preset 29 = "Overdrive Guitar" (cosmetic name
difference — "Overdrive" vs "Overdriven" — no routing impact).

FluidR3 preset 29 multi-velocity layers:
- Vel < 60: cleaner layer (pre-overdrive breakup)
- Vel 60–100: classic overdrive tone
- Vel ≥ 110: highest gain layer (increased distortion, less separation)

## Registration in instrument_registry.py

Instrument module path: `Guitar.overdriven.overdriven` → key `"overdriven"`
Convenience constant: `OVERDRIVEN_GUITAR = ALL_INSTRUMENTS["overdriven"]`

### Registry Table Output (showing new row)

```
| Guitar | Overdriven Guitar | 29 | 28–84 | lead, harmony, accent |
```

### Verification Proof

```
=== Overdriven Guitar (GM29) ===
  OVERDRIVEN_GUITAR.midi_program = 29 (should be 29)
  by_name('overdriven guitar') = <Instrument Overdriven Guitar (family=Guitar, program=29, range=28-84)>
  by_program(29) = <Instrument Overdriven Guitar (family=Guitar, program=29, range=28-84)>
  OVERDRIVEN_GUITAR.in_sweet_spot(64) = True
  OVERDRIVEN_GUITAR.in_sweet_spot(24) = False
  OVERDRIVEN_GUITAR.range_min = 28 OVERDRIVEN_GUITAR.range_max = 84
  OVERDRIVEN_GUITAR.stem_label = 'Overdriven_Guitar'
```

## Engine Verification Results

### UnitMatrixComposer Test

- **Composer**: UnitMatrixComposer (bpm=120, 4/4, 1 bar, 1 voice solo)
- **Pattern**: Pentatonic lead line E4-G4-B4-E5 ascending-desceding (7 notes)
- **Zero-drit**: True (OK)
- **MIDI export**: 111 bytes (> 40, good)

### Sol Render (FluidSynth via discover_soundfont)

- **WAV file**: 731,180 bytes (> 40, good)
- **Spectral check**: 4-8 kHz buzz energy = 1.6% (well below 20% gate — no comb-filtering)
- **Method**: `render_midi(midi_path, wav_path, solo=0)` — ONLY the overdriven
  guitar track (voice 0), no unison doubling

### Stem Render

- **Stem file**: `track00_Overdriven_Guitar.wav` (731,180 bytes)
- **Label match**: ✅ "Overdriven_Guitar" matches pipeline GM_PROGRAMS[29]

## FluidSynth/SF2 Notes

FluidR3_GM.sf2 preset 29 plays the full 28–84 range with no gaps. Multi-velocity
layers provide natural gain-staging overdrive at higher velocities. The sample
set has baked-in amp hiss (~-50 dB noise floor). Recommend writing velocities
75–90 for classic overdrive, 95–100 for accents.

## Identity / Writing Quirks

1. **Power chords (root-fifth, no 3rd)** are the #1 rhythm texture — full
   chords on high gain intermodulate and get washy.
2. **Single-note leads** with bends/hammer-ons/pull-offs are the quintessential
   melodic voice.
3. **Compression reduces dynamic range** — phrase with note density, not
   velocity marks.
4. **Low E string (41 Hz)** is weak on overdrive due to speaker roll-off —
   keep main lines above MIDI 40 (E2).
5. **Palm-muted rhythm** should be 8th/16th note patterns with the palm_mute
   articulation.

## Files Created

| File | Path |
|------|------|
| instrument.md | `Guitar/overdriven/instrument.md` |
| Constants | `Guitar/overdriven/overdriven.py` |
| Verify script | `_test/verify_overdriven.py` |
| Test MIDI | `_test/overdriven_test.mid` |
| Test WAV | `_test/overdriven_test.wav` |
| Stems | `_test/stems_overdriven/track00_Overdriven_Guitar.wav` |
| Registry update | `instrument_registry.py` |
| Registry doc | `registry.md` |