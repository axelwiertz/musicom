# Tuba — Nightly Instrument Research Report

- **Date**: 2026-08-27
- **Instrument**: Tuba (Brass family — bass voice of the brass choir)
- **Status**: ✅ COMPLETE — added, verified end-to-end, registered

## Instrument summary

| Field | Value |
|---|---|
| Family | Brass |
| Name | Tuba |
| MIDI program | 58 (0-indexed; strict GM #59) |
| GM name | "Tuba" |
| Range | D1 (26) – C5 (72) |
| Solo range | C2 (36) – D4 (62) |
| Sweet spot | G2 (43) – Bb3 (58) |
| Roles | bass, harmony, accent, rhythm |
| Synthesis | phase_mod (PhaseModSynth), additive |
| Report path | `/opt/data/projects/Instruments/Brass/tuba/REPORT.md` |

Chosen over remaining candidates (oboe, bassoon, sax, organ, vibraphone, etc.)
because: fills the missing **brass bass** slot (existing brass = trumpet/
trombone/french_horn — none is a true bass), and GM58 has **clean labels**
everywhere (pipeline + SF2), no quirks to document.

## Range zones

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Low | 26–42 | D1–F2 | pedal/contra, dark sub-bass |
| Mid | 43–58 | G2–Bb3 | warm round, "money" register |
| High | 59–72 | C4–C5 | solo/tenor, effortful above ~G4(67) |

## Articulations (velocity, duration_factor)

| Technique | Velocity | Duration | Notes |
|---|---|---|---|
| sustain | 80 | 1.0 | smooth round fat core |
| tenuto | 72 | 0.9 | full weight, slight separation |
| staccato | 64 | 0.25 | crisp tongue stop |
| marcato | 92 | 0.9 | punchy bass hits |
| sforzando | 104 | 0.7 | explosive onset |
| flutter | 75 | 1.0 | rapid tongue flutter |

## Synthesis (musicom)

- **Primary**: `PhaseModSynth` (`sound/synthesis/phase_mod.py`)
  - `carrier_shape='saw'`, `mod_freq_ratio=1.0`, `mod_depth=2.0`
  - `attack=0.06`, `release=0.16`
  - mod_depth 2.0 = darkest of brass (trumpet 4.0, trombone 3.0, horn 2.5) —
    tuba has few strong upper harmonics
- **Secondary**: `Additive` — dominant fundamental + gentle 2nd/3rd, 4th+ rolls
  off fast
- **Avoid**: ModalSynth (better for strings/percussion)

## Production defaults

| Param | Value | Rationale |
|---|---|---|
| REVERB_TAIL | 1.5 s | short hall tail — long reverb muddies low end |
| EQ_BODY | (200, -2.5) | cut mud/boxiness |
| EQ_PRESENCE | (1200, 2.0) | definition |
| EQ_AIR | (4000, 1.5) | least air of brass |
| PAN | 0.0 | center for solo/root; keep low end centered |

## Verification results (real output)

```
Tuba: program=58 gm='Tuba' stem='Tuba' sweet=(36, 62) A4=440.0Hz
Tuba: D1=36.7Hz C2=65.4Hz G2=98.0Hz Bb3=233.1Hz C5=523.3Hz
Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/tuba_test.mid (180 bytes)
FluidSynth exit: 0
WAV: /opt/data/projects/Instruments/_test/tuba_test.wav (880428 bytes)
Stem labels (pipeline GM_PROGRAMS, 0-indexed):
  [56] = 'Trumpet'
  [57] = 'Trombone'
  [58] = 'Tuba'
  [59] = 'Muted Trumpet'
  [60] = 'French Horn'
  [61] = 'Brass Section'
  Tuba -> 'Tuba'
SF2 preset 58 -> 'Tuba'
ALL CHECKS PASSED
```

- **Zero-drift**: `validate()` → `True (OK)` ✓
- **MIDI size**: 180 bytes (> 40 ✓)
- **WAV size**: 880,428 bytes (> 40 ✓)
- **Stem render** (RenderPipeline.render_stems):
  - `track00_Tuba.wav` (756,780 bytes) ✓
  - `track01_Trombone.wav`, `track02_Bright_Acoustic_Piano.wav` (context voices)

## Quirks found

- **Stem label**: NONE — pipeline `GM_PROGRAMS[58] = "Tuba"`, SF2 preset 58 =
  `Tuba`. Labels match exactly (unlike flute GM74→"Recorder" quirk or piano
  GM1→"Bright_Acoustic_Piano").
- **MidiInstrument enum**: GM58 NOT exposed in `structures/instrument.py`
  (enum only has 10 instruments). Use raw `program=58`.
- **FluidSynth**: use `-g 1.2` to avoid tail truncation (same as all brass).

## Files created

| Path | Purpose |
|---|---|
| `/opt/data/projects/Instruments/Brass/tuba/instrument.md` | Full research reference |
| `/opt/data/projects/Instruments/Brass/tuba/tuba.py` | Importable constants |
| `/opt/data/projects/Instruments/Brass/tuba/REPORT.md` | This report (primary record) |
| `/opt/data/projects/Instruments/_test/verify_tuba.py` | Verification script |
| `/opt/data/projects/Instruments/_test/render_tuba_stems.py` | Stem-label check script |
| `/opt/data/projects/Instruments/_test/tuba_test.mid` | Test MIDI artifact |
| `/opt/data/projects/Instruments/_test/tuba_test.wav` | Test WAV artifact |
| `/opt/data/projects/Instruments/_test/stems_tuba/` | Rendered stems (label proof) |

Registry updated: `registry.md` — new Registry row (Brass | Tuba | 58 | 26–72 |
bass, harmony, accent, rhythm) + GM58 row in Stem-label quirks table + changelog note.
