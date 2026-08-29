# Oboe — Instrument Research Report

- **Date**: 2026-08-29 (nightly research job)
- **Family**: Woodwind
- **Status**: VERIFIED end-to-end
- **Instrument**: Oboe
- **MIDI program**: 68 (0-indexed; strict GM #69 "Oboe")
- **Report path**: `/opt/data/projects/Instruments/Woodwind/oboe/REPORT.md`

## Why oboe

Priority list: Strings (viola, double_bass) and Brass (trombone, french_horn,
tuba) were already added on previous nights. Woodwind had flute + clarinet +
bassoon but **no double-reed treble voice** — oboe (GM 68) is the iconic
double-reed solo instrument (the orchestra's tuning reference, A4=440), and
sits between clarinet (single reed, odd harmonics) and bassoon (double reed,
bass) as the piercing melodic voice of the woodwind choir. Candidate ground
truth check (below) shows it is also clean label-wise.

## Candidate ground-truth check (2026-08-29)

SF2 preset names (TimGM6mb.sf2 phdr chunk) vs pipeline GM_PROGRAMS labels
(0-indexed) for remaining candidates:

| pgm | pipeline label | SF2 preset | match |
|---|---|---|---|
| 6 | Harpsichord | Harpsichord | OK |
| 11 | Vibraphone | Vibraphone | OK |
| 12 | Marimba | Marimba | OK |
| 19 | Church Organ | Church Organ | OK |
| 47 | Timpani | Timpani | OK |
| 65 | Alto Sax | AltoSax (TB) v2.3 | DIFF (cosmetic) |
| **68** | **Oboe** | **Oboe (Orch)** | **DIFF (cosmetic suffix only)** |
| 88 | Pad 1 (new age) | Fantasia | DIFF (cosmetic) |

Oboe is the remaining priority woodwind with EXACT pipeline label ("Oboe") and
only a cosmetic "(Orch)" suffix on the SF2 preset — no quirk, no routing impact.

## Instrument facts

- **GM program**: 68 (0-indexed = strict GM #69 Oboe). NOT in
  `structures/instrument.py` `MidiInstrument` enum (exposes only 10
  instruments); use raw `program=68` in `add_voice`.
- **Range**: Bb3 (52) – G6 (92), sounding pitch, concert oboe. Orchestral
  writing Bb3–E6 (52–88); solo literature Bb4–F5 focus; altissimo to C6 (84)
  common, G6 (92) practical top.
- **Sweet spot**: Bb4–B5 (71–83) — the plaintive, piercing singing register
  that cuts through a full orchestra.
- **Roles**: lead, countermelody, harmony, accent. The oboe is the orchestra's
  tuning reference (A4); NOT bass (low register too weak/dark), NOT rhythm.
- **Timbre DNA**: double reed, conical bore — strong fundamental + rich even
  AND odd harmonics (brighter/nasal than clarinet's odd-only); attack 30–80 ms
  (clearest reed attack of the woodwinds); sustained decay; release 50–120 ms;
  reed buzz transient + breath hiss; vibrato 4–6 Hz narrow (±0.1–0.3 st).

## Constants (Woodwind/oboe/oboe.py)

```python
MIDI_PROGRAM = 68
GM_NAME = "Oboe"
STEM_LABEL = "Oboe"
RANGE_MIN = 52      # Bb3
RANGE_MAX = 92      # G6
SOLO_RANGE = (58, 84)   # Bb3-C6
SWEET_SPOT = (71, 83)   # Bb4-B5
ZONES = {"low": (52, 67), "mid": (68, 76), "high": (77, 92)}
ARTICULATIONS = {
    "legato": (78, 1.0), "tenuto": (70, 0.9), "staccato": (64, 0.25),
    "accent": (92, 0.9), "flutter": (66, 1.0), "sforzando": (95, 1.0),
}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw", "mod_freq_ratio": 1.0, "mod_depth": 2.5,
    "attack": 0.05, "release": 0.10,
}
REVERB_TAIL = 1.8
EQ_BODY = (400, -2.0)
EQ_PRESENCE = (3000, 2.5)
EQ_AIR = (7000, 1.5)
PAN = 0.0
```

Frequency spot-checks: Bb3=164.8 Hz, A4=440.0 Hz, Bb4=466.2 Hz, F5=698.5 Hz,
G6=1661.2 Hz.

## Synthesis recommendation

**PhaseModSynth** (`sound/synthesis/phase_mod.py`) — PM/FM is the best match
for a double reed: saw carrier (even+odd harmonic mix, brighter/nasal vs
bassoon's triangle), sine modulator at 1:1 ratio, mod depth 2.5 (brighter than
bassoon 2.0, nasal presence), attack 30–80 ms (double reed speaks fast-ish),
release 100 ms.

Secondary: **Additive** (`sound/synthesis/additive.py`) for explicit harmonic
control — boost 2–4 kHz partials for the piercing oboe presence. ModalSynth:
avoid (better for strings/percussion).

## Production defaults

- Reverb: hall 1.5–2.5 s tail (1.8 default) — medium, keep articulation clarity
- EQ: cut 300–500 Hz boxiness (400 Hz, -2.0 dB); boost ~3 kHz reed presence
  (3000 Hz, +2.5 dB — the oboe's piercing trademark); gentle high shelf above
  7 kHz (7000 Hz, +1.5 dB)
- Delay: none for classical; dotted 8th echo for pop/jazz solo lines (rare)
- Pan: center solo; -0.15..-0.25 in section

## Verification (2026-08-29)

Script: `/opt/data/projects/Instruments/_test/verify_oboe.py`

| Check | Result |
|---|---|
| Constants import + freq conversion | ✓ A4=440.0 Hz |
| UnitMatrixComposer (3 voices: Oboe+Clarinet+Piano, 1 bar, 1 section) | ✓ built |
| Zero-drift validate() | ✓ True (OK) |
| MIDI export | ✓ 180 bytes (>40) |
| FluidSynth WAV (`-ni -g 1.2 -F`) | ✓ exit 0, 880428 bytes (>40) |
| Pipeline stem label GM_PROGRAMS[68] | ✓ "Oboe" (exact, no quirk) |
| SF2 preset 68 (phdr chunk) | ✓ "Oboe (Orch)" (cosmetic suffix only) |
| RenderPipeline render_stems | ✓ track00_Oboe.wav (808236 B), track01_Clarinet.wav, track02_Bright_Acoustic_Piano.wav |
| Assertions | ✓ ALL CHECKS PASSED |

Note: piano.py uses program 1 → pipeline labels it `Bright_Acoustic_Piano`
(known off-by-one in existing entries, GM #2) — cosmetic, no routing impact.

## Quirks found

- **None for oboe.** GM_PROGRAMS[68] = "Oboe" and SF2 preset 68 = "Oboe
  (Orch)" — pipeline label exact; SF2 suffix "(Orch)" is cosmetic only, no
  routing impact (unlike flute 74→"Recorder", piano 1→"Bright_Acoustic_Piano",
  ch9/pgm0→"Acoustic_Grand_Piano").
- MidiInstrument enum does NOT expose oboe (only 10 instruments) — use raw
  `program=68`.
- `RenderPipeline.render_stems` requires `soundfont_path` + `fluidsynth_bin`
  constructor args (no defaults) — pass them explicitly.
- Registry table row added (Woodwind | Oboe | 68 | 52–92 | lead, counter,
  harmony, accent); stem-label quirks table row 68 → Oboe ✓.

## Artifacts

| File | Path |
|---|---|
| instrument.md | `/opt/data/projects/Instruments/Woodwind/oboe/instrument.md` |
| oboe.py | `/opt/data/projects/Instruments/Woodwind/oboe/oboe.py` |
| REPORT.md | `/opt/data/projects/Instruments/Woodwind/oboe/REPORT.md` |
| verify script | `/opt/data/projects/Instruments/_test/verify_oboe.py` |
| test MIDI | `/opt/data/projects/Instruments/_test/oboe_test.mid` (180 B) |
| test WAV | `/opt/data/projects/Instruments/_test/oboe_test.wav` (880428 B) |
| stems | `/opt/data/projects/Instruments/_test/stems_oboe/track00_Oboe.wav` (+ clarinet, piano stems) |
