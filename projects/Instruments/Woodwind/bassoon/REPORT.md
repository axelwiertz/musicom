# Bassoon — Instrument Research Report

- **Date**: 2026-08-28 (nightly research job)
- **Family**: Woodwind
- **Status**: VERIFIED end-to-end
- **Instrument**: Bassoon
- **MIDI program**: 70 (0-indexed; strict GM #71 "Bassoon")
- **Report path**: `/opt/data/projects/Instruments/Woodwind/bassoon/REPORT.md`

## Why bassoon

Priority list: Strings (viola, double_bass) and Brass (trombone, french_horn,
tuba) were already added on previous nights. Woodwind had flute + clarinet but
**no bass-voice reed** — bassoon (GM 70) fills the woodwind bass gap and is a
distinctive double-reed timbre (vs clarinet's single reed). Candidate check
(see below) showed it is also the cleanest remaining woodwind choice label-wise.

## Candidate ground-truth check (2026-08-28)

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
| 66 | Tenor Sax | Tenor Sax (TB) v2.3 | DIFF (cosmetic) |
| 68 | Oboe | Oboe (Orch) | DIFF (cosmetic) |
| **70** | **Bassoon** | **Bassoon** | **OK — exact** |
| 88 | Pad 1 (new age) | Fantasia | DIFF (cosmetic) |

Bassoon is the only remaining priority woodwind with EXACT pipeline/SF2 label
match — no quirk, no cosmetic difference.

## Instrument facts

- **GM program**: 70 (0-indexed = strict GM #71 Bassoon). NOT in
  `structures/instrument.py` `MidiInstrument` enum (exposes only 10
  instruments); use raw `program=70` in `add_voice`.
- **Range**: Bb1 (34) – E6 (88), sounding pitch, concert bassoon.
  Orchestral bass writing Bb1–C4 (34–60); solo literature G2–D5 (43–74);
  altissimo to C6 (84) common, E6 (88) practical top.
- **Sweet spot**: C3–C5 (48–72) — warm singing tenor register.
- **Roles**: bass, harmony, countermelody, lead. Bass of the woodwind choir;
  doubles cello/contrabass; NOT rhythm, NOT pad.
- **Timbre DNA**: double reed — strong fundamental + even/odd harmonic mix,
  darker than oboe, tuba-like low end; attack 40–80 ms; sustained decay;
  release 60–140 ms; reed buzz transient + key clacks; vibrato 4–6 Hz narrow.

## Constants (Woodwind/bassoon/bassoon.py)

```python
MIDI_PROGRAM = 70
GM_NAME = "Bassoon"
STEM_LABEL = "Bassoon"
RANGE_MIN = 34      # Bb1
RANGE_MAX = 88      # E6
SOLO_RANGE = (43, 74)   # G2-D5
SWEET_SPOT = (48, 72)   # C3-C5
ZONES = {"low": (34, 52), "mid": (53, 72), "high": (73, 88)}
ARTICULATIONS = {
    "legato": (76, 1.0), "tenuto": (68, 0.9), "staccato": (60, 0.25),
    "marcato": (88, 0.9), "accent": (90, 0.9), "flutter": (64, 1.0),
}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "triangle", "mod_freq_ratio": 1.0, "mod_depth": 2.0,
    "attack": 0.06, "release": 0.12,
}
REVERB_TAIL = 1.7
EQ_BODY = (300, -2.5)
EQ_PRESENCE = (2500, 2.0)
EQ_AIR = (6000, 1.5)
PAN = 0.0
```

Frequency spot-checks: Bb1=58.3 Hz, C3=130.8 Hz, C4=261.6 Hz, C5=523.3 Hz,
E6=1318.5 Hz.

## Synthesis recommendation

**PhaseModSynth** (`sound/synthesis/phase_mod.py`) — PM/FM is the best match
for a double reed: triangle carrier (strong fundamental, even/odd mix), sine
modulator at 1:1 ratio, mod depth 2.0 (darker than oboe, brighter than tuba),
attack 50–80 ms (double reed speaks slow-ish), release 100–140 ms.

Secondary: **Additive** (`sound/synthesis/additive.py`) for explicit harmonic
control (strong fundamental + even/odd mix, upper harmonics softer than oboe).
ModalSynth: avoid (better for strings/percussion).

## Production defaults

- Reverb: hall 1.4–2.0 s tail (1.7 default) — medium, keep articulation clarity
- EQ: cut 200–400 Hz mud/boxiness (300 Hz, -2.5 dB); boost 2–3 kHz presence
  (2500 Hz, +2.0 dB); gentle high shelf above 6 kHz (6000 Hz, +1.5 dB)
- Delay: none for classical; dotted 8th echo for pop/jazz solo lines (rare)
- Pan: center solo; -0.15..-0.25 in section

## Verification (2026-08-28)

Script: `/opt/data/projects/Instruments/_test/verify_bassoon.py`

| Check | Result |
|---|---|
| Constants import + freq conversion | ✓ A4=440.0 Hz |
| UnitMatrixComposer (3 voices: Bassoon+Clarinet+Piano, 1 bar, 1 section) | ✓ built |
| Zero-drift validate() | ✓ True (OK) |
| MIDI export | ✓ 180 bytes (>40) |
| FluidSynth WAV (`-ni -g 1.2 -F`) | ✓ exit 0, 881452 bytes (>40) |
| Pipeline stem label GM_PROGRAMS[70] | ✓ "Bassoon" (exact, no quirk) |
| SF2 preset 70 (phdr chunk) | ✓ "Bassoon" (exact match) |
| RenderPipeline render_stems | ✓ track00_Bassoon.wav (745516 B), track01_Clarinet.wav, track02_Bright_Acoustic_Piano.wav |
| Assertions | ✓ ALL CHECKS PASSED |

Note: piano.py uses program 1 → pipeline labels it `Bright_Acoustic_Piano`
(known off-by-one in existing entries, GM #2) — cosmetic, no routing impact.

## Quirks found

- **None for bassoon.** GM_PROGRAMS[70] = "Bassoon" and SF2 preset 70 =
  "Bassoon" — labels match exactly (unlike flute 74→"Recorder", piano 1→
  "Bright_Acoustic_Piano", ch9/pgm0→"Acoustic_Grand_Piano").
- MidiInstrument enum does NOT expose bassoon (only 10 instruments) — use raw
  `program=70`.
- Registry table row added (Woodwind | Bassoon | 70 | 34–88 | bass, harmony,
  counter, lead); stem-label quirks table row 70 → Bassoon ✓.

## Artifacts

| File | Path |
|---|---|
| instrument.md | `/opt/data/projects/Instruments/Woodwind/bassoon/instrument.md` |
| bassoon.py | `/opt/data/projects/Instruments/Woodwind/bassoon/bassoon.py` |
| REPORT.md | `/opt/data/projects/Instruments/Woodwind/bassoon/REPORT.md` |
| verify script | `/opt/data/projects/Instruments/_test/verify_bassoon.py` |
| test MIDI | `/opt/data/projects/Instruments/_test/bassoon_test.mid` (180 B) |
| test WAV | `/opt/data/projects/Instruments/_test/bassoon_test.wav` (881452 B) |
| stems | `/opt/data/projects/Instruments/_test/stems_bassoon/track00_Bassoon.wav` (+ clarinet, piano stems) |
