# REPORT — Melodic Tom (GM117)

**Nightly instrument research job** — 2026-11-16
**Family**: Percussion · **Folder**: `Percussion/melodic_tom/`
**Files**: `instrument.md` + `melodic_tom.py` + this report
**Registered**: `instrument_registry.py` → `Percussion.melodic_tom.melodic_tom` → key `melodic_tom`, constant `MELODIC_TOM`

---

## 1. Instrument

**GM117 Melodic Tom** — the tuned tom-tom set of the GM percussion tail
(block: 113 Agogo, 114 Steel Drums, 115 Woodblock, 116 Taiko Drum, 117
Melodic Tom, 118 Synth Drum). Real-world identity: a set of SINGLE-HEADED
concert toms / rototoms tuned in scale steps — the 70s/80s "melodic tom
fill" voice. Reference recordings: Toto "Africa" intro (Jeff Porcaro's
tuned-tom riff), Men at Work "Down Under" toms, The Police "Every Breath
You Take" intro fills, Phil Collins "In the Air Tonight" gated toms.

Distinct from:
- GM116 Taiko — the low deep festival drum (World family; GM117 is higher,
  drum-set toms tuned for melodic fills)
- GM47 Timpani — pedal-tuned kettledrums, mallets, long hall ring
- GM115 Woodblock — unpitched wooden tick

The MidiInstrument enum (`structures/instrument.py`) only exposes 10
instruments — GM117 is not among them; the raw GM number 117 is used
directly, and the registry is the full KB.

## 2. Program / channel / labels

| Thing | Value |
|---|---|
| MIDI program | **117** (0-based GM) |
| GM name | "Melodic Tom" |
| Channel | melodic channel (0–9). NOT ch9 — ch9 triggers the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem label (timpani lesson) |
| Pipeline stem label | `GM_PROGRAMS[117] = "Melodic Tom"` → `trackXX_Melodic_Tom.wav` — **no quirk** |
| FluidR3 preset | 117 = "Melodic Tom" (verified from the phdr chunk) — matches exactly |
| TimGM6mb | also carries preset 117 (renders the same patch family) |

## 3. Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (window) | 36–96 | C2–C6 | melodic-tom patch span |
| Low | 36–47 | C2–B2 | floor toms: chest thump |
| Mid (fill core) | 48–60 | C3–C4 | classic melodic-fill register |
| High | 61–96 | C#4–C6 | rack toms / rototoms: thin, bright |

- Solo range: 48–72 (C3–C5) · Sweet spot: 52–67 (E3–G4)
- Isolated-note sweep (FluidR3, one note per file, vel 100): notes 30–108
  ALL audible (RMS 0.12–0.16), no gaps, no clipping — the SF2 never clips a
  composition.

## 4. Role

`rhythm, accent, ornament, color` — melodic fills into/out of sections,
drum breaks, intro riffs; downbeat punctuation; ghost taps / rim cracks /
flams / rolls; tuned-drum colour. **NOT** a melodic lead (no chromatic
tracking), **NOT** harmony/pad, **NOT** bass. Humanize: Percussion DNA
(2.5 ms sigma, 0 layback) — fills sit ON the grid.

## 5. Synthesis engine (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with custom `MELODIC_TOM_MODES`: tuned (0,1) head mode
   (174 Hz, F3 reference) + Bessel membrane partners 1.59×/2.14×/2.78×/3.56×,
   decay rates 4.5–9.5 (between timpani 0.9–3.0 and marimba 8–20 — a concert
   tom rings ~0.5–1.0 s). `MODAL_PRESET 'drum'` is the closest stock bank
   (fast, inharmonic) but has no tuned-head fundamental.
2. **DrumSynth606** (`sound/synthesis/drum_synth_606.py`) — strike thump:
   `DRUM606_DEFAULTS` freq 174, decay 0.8, pitch_sweep 1.25.
3. **PhaseModSynth** — cheap thump: sine carrier, mod ratio 1.59, depth 1.2,
   attack 0.001, release 0.5.
4. **Karplus-Strong — EXPLICITLY REJECTED** (no string; timpani/taiko
   precedent).

## 6. All constants (`melodic_tom.py`)

```python
MIDI_PROGRAM = 117
GM_NAME = "Melodic Tom"
STEM_LABEL = "Melodic Tom"
RANGE_MIN = 36
RANGE_MAX = 96
SOLO_RANGE = (48, 72)
SWEET_SPOT = (52, 67)
ZONES = {"low": (36, 47), "mid": (48, 60), "high": (61, 96)}
ARTICULATIONS = {
    "fill_16": (96, 0.35), "fill_8": (104, 0.5), "accent": (112, 0.6),
    "ghost": (40, 0.2), "rim": (88, 0.12), "roll": (80, 0.1),
    "flam": (92, 0.15), "soft": (60, 0.5), "toms_together": (100, 0.4),
}
SYNTHESIS = "modal"
MODAL_PRESET = "drum"
MELODIC_TOM_MODES = [
    (174.0, 1.00, 4.5), (277.0, 0.55, 5.5), (372.0, 0.32, 6.5),
    (483.0, 0.18, 8.0), (620.0, 0.10, 9.5),
]
DRUM606_DEFAULTS = {"freq": 174.0, "decay": 0.8, "pitch_sweep": 1.25}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 1.59,
               "mod_depth": 1.2, "attack": 0.001, "release": 0.5}
REVERB_TAIL = 1.2
EQ_BODY = (280, -2.0)
EQ_PRESENCE = (2400, 2.0)
EQ_AIR = (7000, 0.8)
PAN = 0.0
# midi_to_freq(midi) standard A4=440
```

Registry `_FIELDS` extended with `melodic_tom_modes` (woodblock/agogo
precedent) so the custom modal bank loads through the registry.

## 7. Registration proof

Registry run (`/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`,
exit 0, full table + verification in `_test/registry_out_melodic_tom.txt`):

```
| Percussion | Melodic Tom | 117 | 36–96 | rhythm, accent, ornament, color |     <- NEW ROW (sorted)

=== Melodic Tom (Percussion, GM117) ===
  MELODIC_TOM.midi_program = 117 (should be 117)
  by_name('melodic tom') = <Instrument Melodic Tom (family=Percussion, program=117, range=36-96)>
  by_name('Melodic Tom') = <Instrument Melodic Tom (family=Percussion, program=117, range=36-96)>
  by_program(117) = <Instrument Melodic Tom (family=Percussion, program=117, range=36-96)>
  by_program(116) = <Instrument Taiko Drum (family=World, program=116, range=36-67)> (distinct: taiko drum)
  MELODIC_TOM.in_sweet_spot(60) = True
  MELODIC_TOM.in_sweet_spot(30) = False
  MELODIC_TOM.range_min = 36 MELODIC_TOM.range_max = 96
  MELODIC_TOM.stem_label = 'Melodic Tom'
  MELODIC_TOM.synthesis = 'modal'
  MELODIC_TOM.reverb_tail = 1.2 MELODIC_TOM.pan = 0.0
```

Verify script (`_test/verify_melodic_tom.py`, run through the REGISTRY):
`by_name('melodic tom')` → Melodic Tom; `MELODIC_TOM is ALL_INSTRUMENTS['melodic_tom']` → True.

## 8. Verification results (engine test)

Pattern: `_test/verify_woodblock.py` (2026-09-01 fixes) — imports through
the registry, **SOLO render** (instrument alone; drums ch9 context only, no
unison doubling).

| Check | Result |
|---|---|
| UnitMatrixComposer 1 bar / 1 section, 104 bpm, 2 voices (Tom ch0 + Drums ch9) | built |
| Zero-drift `validate()` | **True (OK)** |
| MIDI export | `_test/melodic_tom_test.mid` — **263 bytes** (> 40 ✓) |
| FluidSynth SOLO render (track 1 only, `discover_soundfont()` → FluidR3_GM.sf2, `-g 1.2`) | `_test/melodic_tom_test.wav` — **851,500 bytes** (> 40 ✓) |
| Spectral gate 4–8 kHz | **10.5%** (OK, < 20%; the stick band, no comb buzz) |
| Stem labels | `GM_PROGRAMS[117] = 'Melodic Tom'`; `STEM_LABEL == 'Melodic Tom'` ✓ |
| SF2 preset | phdr chunk: preset 117 = "Melodic Tom" ✓ |
| Stems on disk | `track00_Melodic_Tom.wav` (851,500 B) + `track01_Drums.wav` (835,628 B) ✓ |
| ModalSynth `MELODIC_TOM_MODES` (1 s, impulse) | peak 0.900; mid/head 0.59 (< 0.9 — decays); late/peak 0.020 (< 0.10 — ~1 s ring ✓); partials 1.59× = 41.3%, 2.14× = 30.7%, 2.78× = 14.6%, 3.56× = 7.3% of f0 — membrane partners present ✓ |

Per-16th RMS of the solo fill (documents the pipeline note-on alternation;
even hits dip ~6–8 dB at fill tempo, ring masks the gap):
`0.177 0.084 0.147 0.074 0.169 0.075 0.151 0.056 0.200 0.104 0.146 0.080 0.175 0.072 0.142 0.062`

## 9. Quirks found (measured)

### 9a. PITCH QUIRK — GM117 does NOT chromatically pitch-track (both soundfonts)
- Isolated notes 30–108 all loud, but the **dominant partial stays in the
  50–95 Hz band**: ~50 Hz at C2 → ~95 Hz at C5 (~1 octave of pitch across 4
  octaves of notes). Spectral centroid creeps only 1.1→1.5 kHz.
- Above ~C6 a weak partial near the written note appears but is not
  reliably in tune (up to ±300 cents).
- **Consequence**: note number is a COARSE timbre/pitch control (the
  woodblock lesson). Composition jobs write fills on a small set of scale
  tones in the sweet spot — NEVER chromatic runs. The 70s/80s fill idiom
  (a 4–6 drum set tuned in scale steps) is exactly what this patch is for.

### 9b. PIPELINE QUIRK — every 2nd note-on EVENT renders ~30–50 dB down
- Deterministic: the 1st, 3rd, 5th... note-ons in a MIDI track sound; the
  2nd, 4th, 6th... are near-silent. Measured on GM117 AND on the registered
  GM47 Timpani, GM115 Woodblock, GM116 Taiko, GM0 Piano, GM33 Electric Bass
  — but NOT on sustained patches (GM40 Violin, GM73 Flute).
- Scope: per MIDI track (splitting tracks shifts the count per track);
  global across channels within a track; ignores CCs, ghost notes on other
  channels, velocity, note length, and gap (2 s vs 6 s both silent);
  NOT fixed by `synth.polyphony=1024`, `synth.reverb.active=0`,
  `synth.chorus.active=0`.
- The previous nightly run's accepted woodblock verify WAV (2026-11-15)
  contains the same artifact — this is a **KNOWN-ACCEPTED pipeline
  behavior** for percussion renders, not a GM117-specific defect.
- Composition consequence: at 16th-note fill tempos the ring of the loud
  hits masks the missing even hits (apparent accent ~6–8 dB — reads as
  natural dynamics); at ≥ 0.5 s spacing the even hits are audibly missing.
  Workarounds: (a) accept it (woodblock precedent); (b) land important fill
  notes on odd note-on indices (1st, 3rd, 5th...); (c) use the
  ModalSynth/DrumSynth606 engine path, which does not have the artifact.

### 9c. No stem-label quirk
GM_PROGRAMS[117] and FluidR3 preset 117 both "Melodic Tom" — exact match
(the "Shanai"/"Bag pipe" kind of quirk does not apply).

## 10. Production defaults

- REVERB_TAIL 1.2 s — pop/rock drum room (taiko 1.6 hall vs woodblock 0.75
  dry); EQ cut 280 Hz −2 dB (box honk), boost 2.4 kHz +2 dB (stick attack),
  7 kHz air +0.8 dB; PAN 0.0 (kit spreads −0.3..+0.3).

## 11. Deliverables

- `Percussion/melodic_tom/instrument.md` — full research reference
- `Percussion/melodic_tom/melodic_tom.py` — importable constants
- `Percussion/melodic_tom/REPORT.md` — this report
- `instrument_registry.py` — module path + `MELODIC_TOM` + role mapping +
  `melodic_tom_modes` field + verification block (registry run exit 0)
- `registry.md` — changelog entry + Registry table row + stem-quirk row
- `_test/verify_melodic_tom.py` + `_test/verify_melodic_tom_out.txt` +
  `_test/registry_out_melodic_tom.txt` + probes 1–12
  (`_test/_probe_melodic_tom*.py`) + `melodic_tom_test.mid/.wav` +
  `stems_melodic_tom/`

Remaining sibling candidates (next nightly slots): GM112 Tinkle Bell,
GM118 Synth Drum, GM76 Blown Bottle, GM17/18 Percussive/Rock Organ, GM50/51
Synth Strings 1/2, GM63 Synth Brass 2, GM37 Slap Bass 2.
