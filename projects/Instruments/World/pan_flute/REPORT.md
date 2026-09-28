# Pan Flute (GM75) — Instrument Research Report

**Date**: 2026-10-01
**Instrument**: Pan Flute (South American Andean panpipes / zampoña / siku / antara)
**Family**: World
**GM Program**: 75
**SF2 Preset**: "Pan Flute" (FluidR3_GM.sf2)
**Pipeline Label**: "Pan Flute" (GM_PROGRAMS[75]) — exact match, **no quirk**
**Stem Label**: `trackXX_Pan_Flute.wav`

---

## Constants Summary

| Constant | Value |
|---|---|
| MIDI_PROGRAM | 75 |
| GM_NAME | "Pan Flute" |
| STEM_LABEL | "Pan_Flute" |
| RANGE_MIN | 55 (G3) |
| RANGE_MAX | 100 (E7) |
| SOLO_RANGE | (62, 89) — D4–F6 |
| SWEET_SPOT | (64, 84) — E4–C6 (malta register) |
| SYNTHESIS | "phase_mod" (PhaseModSynth) |
| REVERB_TAIL | 2.0 s |
| EQ_BODY | (300, -2.0) — cut tube boxiness |
| EQ_PRESENCE | (2200, 2.0) — breath presence |
| PAN | 0.0 (center) |

## Zones

| Zone | MIDI | Pitches | Description |
|---|---|---|---|
| zankha (low) | 55–61 | G3–B3 | bass tubes — deep, airy, breathy |
| malta (mid) | 62–78 | D4–F5 | primary melodic register — warmest round tone |
| chuli (high) | 79–100 | F#5–E7 | high tubes — bright, piercing, whistle-like |

## Articulations

| Technique | Velocity | Duration Factor |
|---|---|---|
| sustain | 78 | 1.0 |
| staccato | 65 | 0.30 |
| accent | 90 | 0.85 |
| legato | 72 | 1.0 |
| trill | 70 | 0.20 |
| grace | 62 | 0.15 |
| vibrato | 75 | 1.0 |
| airy | 50 | 1.0 |

## Synthesis

**PhaseModSynth** (primary) — stopped-pipe flue tone:
- Sine carrier + sine modulator, ratio 1.0
- mod_depth 1.2 (pure fundamental dominance — shallowest in World wind set)
- attack 0.05 s, release 0.15 s

**Additive** (fallback) — odd-only partials:
- (1: 0.9), (3: 0.35), (5: 0.15), (7: 0.05) — strongest fundamental dominance of World wind

**AirPipe** (physical model fallback):
- stopped=True, length_scale=0.85, pressure=0.55, noise=0.15

## Range

Full GM-patch compass: 55–100 (G3–E7). Confirmed empirically — see sweep results below.
Standard 1.5-octave siku: D4–A5 (62–81); large 3-octave chromatic zampoña: G3–C7 (55–96).

---

## Registry Verification

### Registry table output (matching row):

```
| World | Pan Flute | 75 | 55–100 | lead, harmony, accent |
```

### Lookups:

```
PAN_FLUTE.midi_program = 75 (should be 75) ✓
by_name('pan flute') = <Instrument Pan Flute (family=World, program=75, range=55-100)> ✓
by_program(75) = <Instrument Pan Flute (family=World, program=75, range=55-100)> ✓
PAN_FLUTE.in_sweet_spot(72) = True ✓
```

---

## Verification Results

### Zero-drift
```
Zero-drift: True (OK)
```

### MIDI export
```
MIDI: /opt/data/projects/Instruments/World/pan_flute/pan_flute_test.mid (111 bytes)
```
Size > 40 ✓

### WAV render (solo — FluidR3_GM.sf2 via discover_soundfont())
```
WAV (solo): /opt/data/projects/Instruments/World/pan_flute/pan_flute_test.wav (731180 bytes)
```
Size > 40 ✓

### Spectral buzz check
```
4-8kHz buzz energy = 1.5% (OK)
```
Well below 20% gate ✓. The stopped-pipe roll-off keeps high-frequency content minimal.

### Stem label check (pipeline GM_PROGRAMS)
```
[75] = 'Pan Flute'
Pan_Flute STEM_LABEL matches pipeline label ✓
```
**No quirk** — labels match exactly.

### SF2 preset check (FluidR3_GM.sf2 phdr)
```
SF2 preset 75 -> 'Pan Flute'
```
Exact match ✓

### RenderPipeline stem render
```
Stems rendered (1 files):
  track00_Pan_Flute.wav (731180 bytes)
```
Stem file > 40 ✓

---

## Quirks

1. **Line instrument**: Pan flute is a monophonic breath instrument — each tube produces exactly one pitch. No dense chords or harmony. The traditional siku uses arqa/ira complementary pairs for rapid note alternation, but this is a melodic technique, not chordal.

2. **Stopped-pipe acoustics**: The only stopped-pipe aerophone in the KB (tube closed at one end). This means only odd-numbered partials (1, 3, 5, 7...) are present, unlike open flutes/recorders which have all partials. This gives the pan flute its characteristic hollow, round, warm tone.

3. **Breath transient**: The attack is a gentle blow transient with air hiss — no reed/tongue snap. This is part of the instrument's identity and should be preserved rather than removed.

4. **Channel quirk**: Must use a melodic channel (0–9) with program 75 — channel 9 would trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback label.

5. **GM program note**: GM75 = "Pan Flute" in the pipeline's GM_PROGRAMS list. Note that GM78 is "Whistle" — not to be confused with pan flute.

---

## Empirical FluidR3 Pitch Sweep

| MIDI | Pitch | RMS Level | Audible |
|---|---|---|---|
| 55 | G3 | 0.042 | ✓ |
| 60 | C4 | 0.051 | ✓ |
| 66 | F#4 | 0.062 | ✓ |
| 72 | C5 | 0.071 | ✓ |
| 78 | F5 | 0.065 | ✓ |
| 84 | C6 | 0.058 | ✓ |
| 90 | F6 | 0.044 | ✓ |
| 96 | C7 | 0.032 | ✓ |
| 100 | E7 | 0.021 | ✓ |

All 9/9 notes across the full 55–100 range are audible. No gaps or dropouts.
Sweet spot 64–84 (E4–C6) shows peak RMS 0.058–0.071 — the warmest bloom zone.

---

## File Locations

| File | Path |
|---|---|
| instrument.md | `/opt/data/projects/Instruments/World/pan_flute/instrument.md` |
| pan_flute.py | `/opt/data/projects/Instruments/World/pan_flute/pan_flute.py` |
| verify_pan_flute.py | `/opt/data/projects/Instruments/World/pan_flute/verify_pan_flute.py` |
| MIDI test | `/opt/data/projects/Instruments/World/pan_flute/pan_flute_test.mid` |
| WAV test | `/opt/data/projects/Instruments/World/pan_flute/pan_flute_test.wav` |
| Report | `/opt/data/projects/Instruments/World/pan_flute/REPORT.md` |

---

## Commitment

- Registered in `instrument_registry.py` (module + PAN_FLUTE constant + verification)
- Updated `registry.md` (Registry table + Stem label table + Dated changelog)
- Verified: zero-drift ✓ → MIDI ✓ → FluidSynth WAV ✓ → spectral clean ✓
- RenderPipeline stem label confirmed: "Pan_Flute" — no quirk