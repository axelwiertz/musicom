# Nightly Instrument Research Report — Brass Section (GM61)

**Date**: 2026-10-15  
**Instrument**: Brass Section (GM61)  
**Family**: Brass  
**Role**: tutti brass ensemble — fanfares, orchestral stabs, sustained harmony

## Constants

| Field | Value |
|---|---|
| MIDI_PROGRAM | 61 |
| GM_NAME | "Brass Section" |
| STEM_LABEL | "Brass_Section" |
| RANGE_MIN | 36 (C2) |
| RANGE_MAX | 96 (C7) |
| SOLO_RANGE | (48, 84) — C3 to C6 |
| SWEET_SPOT | (55, 79) — G3 to G5 |
| SYNTHESIS | "phase_mod" |
| REVERB_TAIL | 2.5 s |
| EQ_BODY | (250 Hz, -3.0 dB) |
| EQ_PRESENCE | (2500 Hz, 3.5 dB) |
| EQ_AIR | (8000 Hz, 1.0 dB) |
| PAN | -0.25 |

### Zones

| Zone | MIDI | Pitches |
|---|---|---|
| low | 36–55 | C2–G3 |
| mid | 56–71 | B3–C5 |
| high | 72–84 | C5–C6 |
| top_extension | 85–96 | C6–C7 |

### Articulations

| Articulation | Velocity | Duration factor |
|---|---|---|
| sustain | 82 | 1.0 |
| fanfare_stab | 92 | 0.40 |
| marcato | 85 | 0.65 |
| accent | 98 | 0.30 |
| staccato | 70 | 0.20 |
| sfz | 100 | 0.25 |
| swell | 72 | 1.20 |
| sfp | 65 | 1.10 |

### Synthesis defaults (PhaseModSynth)

```python
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.8,
    "attack": 0.06,
    "release": 0.30,
}
```

## Registration proof

Registry verification output showing Brass Section row:

```
| Brass | Brass Section | 61 | 36–96 | lead, accent, fanfare, counter, harmony, pad |
```

Verification lines:
```
  BRASS_SECTION.midi_program = 61 (should be 61)
  by_name('brass section') = <Instrument Brass Section (family=Brass, program=61, range=36-96)>
  by_program(61) = <Instrument Brass Section (family=Brass, program=61, range=36-96)>
  BRASS_SECTION.in_sweet_spot(67) = True
  BRASS_SECTION.in_sweet_spot(30) = False
  BRASS_SECTION.range_min = 36 BRASS_SECTION.range_max = 96
  BRASS_SECTION.stem_label = 'Brass_Section'
```

## Verification results

| Check | Result | Detail |
|---|---|---|
| Zero-drift | ✓ PASS | validate() returned True |
| MIDI file | ✓ 92 bytes | > 40 bytes threshold |
| WAV file (solo) | ✓ 794,668 bytes | > 40 bytes threshold |
| Spectral buzz | ✓ 1.5% | 4–8 kHz band, well below 20% gate |
| Stem label | ✓ "Brass_Section" | GM_PROGRAMS[61] = "Brass Section" → sanitized `Brass_Section` |
| FluidR3 SF2 | ✓ "Brass Section" | preset 61 label matches exactly |

## Stem label quirks

**No quirk.** GM_PROGRAMS[61] = "Brass Section", FluidR3 preset 61 = "Brass Section" — labels match exactly. STEM_LABEL = "Brass_Section" matches the sanitized pipeline form.

## Identity notes

- Brass Section (GM61) is the **full brass ensemble** patch — trumpets, trombones, horns, and tuba samples mixed into a single multi-sample patch
- **Not a solo instrument** — use trumpet/trombone/french_horn/tuba individually for solo lines
- Idiomatic for tutti fanfares (Star Wars, Olympic fanfares), orchestral stabs, sustained harmonic pads, and brass countermelodies behind strings
- The PhaseModSynth saw carrier with mod_depth 2.8 produces the right stacked-brass harmonic content
- Range 36–96 covers the full GM patch span; idiomatic writing zone is 48–84 (C3–C6)
- Channel quirk: must use melodic channel (0–9) with program 61 — channel 9 triggers the drum-kit map

## Report path

`/opt/data/projects/Instruments/Brass/brass_section/REPORT.md`