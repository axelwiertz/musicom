# Instruments — musicom lookup registry

Importable instrument constants for compositions. Each instrument folder has
`instrument.md` (full research reference) + `<name>.py` (constants).

**Orchestration layer**: `orchestrator.py` + `orchestration.md` — role→instrument
mapping, register allocation, section dynamics, velocity balance. Turns the
instrument KB into arrangement decisions. Verified end-to-end (2026-08-21).

**Verified end-to-end** (2026-08-20): violin+piano+drumkit composition through
UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓.

**Viola added** (2026-08-23): GM41, full strings-family entry (instrument.md +
viola.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI →
FluidSynth WAV ✓; RenderPipeline stem label `trackXX_Viola.wav` ✓ (no quirk).

**Double Bass added** (2026-08-24): GM43, strings-family bass entry
(instrument.md + double_bass.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Contrabass.wav` ✓ (label is "Contrabass", not "Double_Bass" — matches
pipeline GM_PROGRAMS[43] and SF2 preset name; no quirk).

**Clarinet added** (2026-08-25): GM71, woodwind-family entry
(instrument.md + clarinet.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Clarinet.wav` ✓ (GM_PROGRAMS[71] = "Clarinet", SF2 preset 71 =
Clarinet; no quirk).

**French Horn added** (2026-08-26): GM60, brass-family entry
(instrument.md + french_horn.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_French_Horn.wav` ✓ (GM_PROGRAMS[60] = "French Horn"; SF2 preset 60
= "French Horns" plural — cosmetic label difference only, no routing impact).

**Tuba added** (2026-08-27): GM58, brass-family bass entry
(instrument.md + tuba.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Tuba.wav` ✓ (GM_PROGRAMS[58] = "Tuba", SF2 preset 58 = "Tuba" —
labels match exactly, no quirk).

**Bassoon added** (2026-08-28): GM70, woodwind-family bass entry
(instrument.md + bassoon.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Bassoon.wav` ✓ (GM_PROGRAMS[70] = "Bassoon", SF2 preset 70 =
"Bassoon" — labels match exactly, no quirk).

**Oboe added** (2026-08-29): GM68, woodwind-family double-reed entry
(instrument.md + oboe.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Oboe.wav` ✓ (GM_PROGRAMS[68] = "Oboe"; SF2 preset 68 = "Oboe (Orch)"
— cosmetic suffix only, no routing impact).

## Python usage

```python
# From anywhere (Instruments is under projects/)
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from Strings.violin.violin import MIDI_PROGRAM, SWEET_SPOT
from Keys.piano.piano import midi_to_freq
from Percussion.drum_kit.drum_kit import KIT, beat_pattern

# In UnitMatrixComposer
composer.add_voice("Violin", program=MIDI_PROGRAM, channel=0)
```

Zero-drift pitfall: drum units MUST end with a terminal landmark
(`MusicEvent(0,0,len_ticks,BAR)`) or validate() fails — see `_test/`.

## Registry

| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Strings | Viola | 41 | 48–91 | harmony, counter, lead, accent |
| Strings | Cello | 42 | 36–84 | bass, lead, counter, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, rhythm, accent, harmony |
| Keys | Piano | 1 | 21–108 | harmony, melody, bass, rhythm |
| Brass | Trumpet | 56 | 54–86 | lead, accent, fanfare |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | French Horn | 60 | 41–84 | harmony, counter, accent, lead |
| Brass | Tuba | 58 | 26–72 | bass, harmony, accent, rhythm |
| Woodwind | Flute | 74 | 60–96 | lead, counter, ornament |
| Woodwind | Oboe | 68 | 52–92 | lead, counter, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, counter, harmony, accent |
| Woodwind | Bassoon | 70 | 34–88 | bass, harmony, counter, lead |
| Guitar | Acoustic | 25 | 40–84 | harmony, rhythm, strum |
| Percussion | Drum Kit | ch9 | 35–81 | rhythm, groove, accent |

## Stem label quirks (RenderPipeline)

GM_PROGRAMS list is **0-indexed** (index N = GM program N). Verified 2026-08-22 against pipeline source + TimGM6mb.sf2 phdr.

| Program | Expected label | Actual label |
|---|---|---|
| 40 | Violin | Violin ✓ |
| 41 | Viola | Viola ✓ |
| 42 | Cello | Cello ✓ |
| 43 | Contrabass | Contrabass ✓ (labeled "Contrabass", not "Double_Bass") |
| 1 | Acoustic Grand Piano | **Bright_Acoustic_Piano** ✗ (list[1]) |
| 56 | Trumpet (correct GM) | Trumpet ✓ |
| 57 | Trombone | Trombone ✓ |
| 58 | Tuba | Tuba ✓ |
| 60 | French Horn | French Horn ✓ (SF2 preset is "French Horns" plural — cosmetic) |
| 70 | Bassoon | Bassoon ✓ |
| 68 | Oboe | Oboe ✓ (SF2 preset is "Oboe (Orch)" — cosmetic suffix only) |
| 74 | Flute | **Recorder** ✗ |
| 25 | Acoustic Guitar (nylon) | Acoustic_Guitar_nylon ✓ |
| ch9/pgm0 | Drums | **Acoustic_Grand_Piano** ✗ (program-0 fallback) |

> **Known off-by-one in existing entries**: ~~`trumpet.py` uses 57~~ **FIXED 2026-08-27**: trumpet is now 56 (SF2 preset 56=`SoloTrumpet`). `piano.py`=1 → actually Bright Acoustic Piano (GM #2) — cosmetic label difference only, no routing impact. Legacy registry rows kept as-is for piano; new instruments use 0-indexed programs matching pipeline+SF2.

Match production code on ACTUAL labels, not intended names.
