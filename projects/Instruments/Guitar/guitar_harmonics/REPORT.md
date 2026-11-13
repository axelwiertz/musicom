# REPORT — Guitar Harmonics (GM31) added to the Instruments KB

**Date**: 2026-11-13
**Instrument**: Guitar Harmonics — the guitar's node-touched chiming voice
(natural 12th/7th/5th-fret harmonics, artificial + pinch harmonics)
**Family**: Guitar (eighth entry: nylon 24, steel 25, jazz 26, clean 27,
muted 28, overdriven 29, distortion 30, **harmonics 31**)
**Files**: `Guitar/guitar_harmonics/instrument.md`,
`Guitar/guitar_harmonics/guitar_harmonics.py`, this report
**Registry key**: `guitar_harmonics` ·
`Guitar.guitar_harmonics.guitar_harmonics` · constant `GUITAR_HARMONICS`
**KB size after this entry**: 91 → **92 instruments**

## 1. MIDI / GM

| Item | Value |
|---|---|
| GM program (0-based) | **31** — GM1 "Guitar Harmonics" / GM2 spec "Guitar harmonics" |
| Channel | melodic (0–9), polyphonic (harmonic dyads/chords idiomatic) |
| SF2 preset (FluidR3_GM.sf2) | 31 = **"Guitar Harmonics"** (verified from the `phdr` chunk) |
| Pipeline stem label | `GM_PROGRAMS[31] = "Guitar harmonics"` → file `trackXX_Guitar_harmonics.wav` |
| STEM_LABEL constant | `"Guitar_harmonics"` (matches the sanitized pipeline label) |
| Stem quirk | label has a lowercase "h" + a SPACE → underscore-sanitized; capitalisation-only diff vs the SF2 name. **No routing impact.** |
| Pitch quirk | **patch sounds +12 semitones (one octave up) vs written pitch** — see §6 |

## 2. Range

Written pitch (what goes in the MIDI file); sounding pitch = written **+12**.

| Zone | Written | Written pitch | Sounds | Meaning |
|---|---|---|---|---|
| Full | 40–84 | E2–C6 | E3–C7 | GM patch span; **patch silent at ≥ 86** |
| low | 40–47 | E2–B2 | E3–B3 | 12th-fret harmonics on wound bass strings |
| mid | 48–64 | C3–E4 | C4–E5 | 7th/5th/4th-fret nodes — primary melody |
| high | 65–84 | F4–C6 | F5–C7 | artificial / pinch harmonics, glassy |

- `SOLO_RANGE = (48, 76)` — real 22-fret natural-harmonic compass
  (sounding C4–E6)
- `SWEET_SPOT = (52, 72)` — fullest chime (sounding E4–C6)
- Empirical FluidR3 sweep, written notes 18–96: audible **18–85**, RMS
  0.0000 at 86/87/88/91/96 → the patch can never clip a composition written
  inside 40–84.

## 3. Role in arrangement

`lead, melody, ornament, texture, accent, countermelody`

- **lead / melody** — artificial-harmonic lines floating an octave above the
  arrangement
- **ornament / accent** — 12th-fret chimes punctuating a phrase; pinch squeals
- **texture** — arpeggiated harmonic chords, let-ring cascades, ambient
  "ice intro" beds
- **countermelody** — answers a vocal from above (glockenspiel register,
  guitar attack)
- **NOT bass** (lowest sound E3; fundamental missing by design) and
  **NOT a chord/rhythm bed** (2–3 note harmonic dyads only)

## 4. Synthesis engine

**Primary: ModalSynth** (`sound/synthesis/modal.py`) with a custom
`GUITAR_HARMONICS_MODES` bank — the measured ODD-harmonic spectrum of the
sounding pitch **1 : 3 : 5 : 7** (the node kills even partials):

```python
GUITAR_HARMONICS_MODES = [
    (440.0,  1.00, 0.35),   # sounding fundamental (octave harmonic)
    (1320.0, 0.42, 0.60),   # 3f — octave+fifth chime colour
    (2200.0, 0.18, 0.95),   # 5f — major third + 2 octaves, glass
    (3080.0, 0.08, 1.30),   # 7f — flat "harmonic 7th" sparkle
]
```

Decay rates 0.35–1.30 are the **slowest in the struck/plucked set**
(vibraphone 0.30–1.10, timpani 0.9–3.0, xylophone 9–20) — one surviving
partial has nowhere to leak energy.

**Fallback: Karplus-Strong** (`sound/synthesis/karplus_strong.py`) — the
string *is* plucked (unlike the struck bars), so KS is a legitimate second
engine: `loop_gain 0.9988` (highest in the KB, just above harp 0.9985),
`width 0.22`, `lowpass_hz 9000`, `noise_component 0.004`.

**Alt: PhaseModSynth** — sine carrier, mod ratio 2.0, depth 0.8, attack
0.002 s, release 0.60 s.

## 5. All constants (`guitar_harmonics.py`)

```
MIDI_PROGRAM = 31
GM_NAME = "Guitar Harmonics"
STEM_LABEL = "Guitar_harmonics"
TRANSPOSE_SEMITONES = 12
RANGE_MIN = 40            RANGE_MAX = 84
SOLO_RANGE = (48, 76)     SWEET_SPOT = (52, 72)
ZONES = {low: (40,47), mid: (48,64), high: (65,84)}
ARTICULATIONS = harmonic_12 (84,1.6) · harmonic_7 (82,1.4) · harmonic_5 (78,1.4)
                artificial (80,1.0) · pinch_squeal (92,0.6) · harp_harmonic (70,2.0)
                chime_double_stop (74,1.2) · tap_harmonic (60,0.4)
                let_ring (68,2.5) · muted (40,0.2)
SYNTHESIS = "modal"   MODAL_PRESET = "string"
GUITAR_HARMONICS_MODES = [(440,1.00,0.35),(1320,0.42,0.60),(2200,0.18,0.95),(3080,0.08,1.30)]
KARPLUS_DEFAULTS = {loop_gain 0.9988, excitation "harmonic", width 0.22,
                    lowpass_hz 9000, noise_component 0.004, role "lead"}
FM_DEFAULTS = {carrier sine, ratio 2.0, depth 0.8, attack 0.002, release 0.60}
REVERB_TAIL = 2.6 s
EQ_BODY = (240, -2.0)   EQ_PRESENCE = (5000, 2.0)   EQ_AIR = (10500, 2.0)
PAN = -0.15
def midi_to_freq(midi) -> 440 * 2 ** ((midi - 69) / 12)     # written pitch
```

## 6. Quirks found

1. **PITCH TRANSPOSITION (new quirk class, measured)** — FluidR3 preset 31
   sounds **one octave above the written note**:

   | Written | Expected f0 | Rendered peak | Ratio |
   |---|---|---|---|
   | 60 (C4) | 261.6 Hz | 522.0 Hz | 2.00× |
   | 67 (G4) | 392.0 Hz | 782.0 Hz | 1.99× |
   | 72 (C5) | 523.3 Hz | 1044.0 Hz | 2.00× |

   Controls: preset 25 (steel guitar) and preset 105 (banjo) both sound at
   written pitch (ratio 1.00×) → **patch property, not a render-path bug**.
   Composition jobs must write an octave below the desired sound
   (`TRANSPOSE_SEMITONES = 12`). It mirrors real physics: a 12th-fret node
   halves the string and doubles the pitch.
2. **Odd-harmonic-only spectrum** — measured peaks at 2×, 6×, 10×, 14× of
   the written note = 1×, 3×, 5×, 7× of the sounding pitch (28% / 10% / 11% /
   1% of band energy). Even partials are removed by the node.
3. **Looped, sustained sample** — RMS/peak stays flat (0.38 → 0.45 → 0.41)
   across 0.2 s–2.5 s while the note is held; there is no natural decay in
   the SF2 patch, so REVERB_TAIL 2.6 s and long articulation durations are
   needed to match it.
4. **Patch ceiling 85** — silent from written 86 up (RMS 0.0000), so
   `RANGE_MAX = 84` is the safe top.
5. **Stem label** `Guitar_harmonics` (space sanitized, lowercase "h" in the
   GM2 label) — no routing impact; `STEM_LABEL` matches the pipeline.

## 7. Registration proof

`_INSTRUMENT_MODULES` gained
`"Guitar.guitar_harmonics.guitar_harmonics": "guitar_harmonics"`; the
convenience constant `GUITAR_HARMONICS = ALL_INSTRUMENTS["guitar_harmonics"]`
was added; `registry_table()` gained the role branch
`guitar harmonics → "lead, melody, ornament, texture, accent, countermelody"`;
the `__main__` verification block prints a `=== Guitar Harmonics (GM31) ===`
section.

`registry_table()` row (from `_test/registry_out_guitar_harmonics.txt`):

```
| Guitar | Guitar Harmonics | 31 | 40–84 | lead, melody, ornament, texture, accent, countermelody |
```

Verification lines (full output: `_test/registry_out_guitar_harmonics.txt`):

```
=== Guitar Harmonics (GM31) ===
  GUITAR_HARMONICS.midi_program = 31 (should be 31)
  by_name('guitar harmonics') = <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>
  by_name('Guitar harmonics') = <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>
  by_program(31) = <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>
  by_program(30) = <Instrument Distortion Guitar (family=Guitar, program=30, range=28-84)> (distinct: distortion guitar)
  GUITAR_HARMONICS.in_sweet_spot(60) = True
  GUITAR_HARMONICS.in_sweet_spot(24) = False
  GUITAR_HARMONICS.range_min = 40 GUITAR_HARMONICS.range_max = 84
  GUITAR_HARMONICS.stem_label = 'Guitar_harmonics'
  GUITAR_HARMONICS.synthesis = 'modal'
```

Registry load count after the addition: **92 instruments** (was 91).

## 8. End-to-end verification (`_test/verify_guitar_harmonics.py`)

```
registry: <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>
GH.midi_program=31 name='Guitar Harmonics' stem='Guitar_harmonics' range=40-84 sweet=(52, 72) synth=modal
by_name('guitar harmonics') = <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>
by_program(31) = <Instrument Guitar Harmonics (family=Guitar, program=31, range=40-84)>

zones={'low': (40, 47), 'mid': (48, 64), 'high': (65, 84)}
articulations=['harmonic_12', 'harmonic_7', 'harmonic_5', 'artificial', 'pinch_squeal', 'harp_harmonic', 'chime_double_stop', 'tap_harmonic', 'let_ring', 'muted']
transpose=+12 semitones (SF2 patch sounds octave up)
reverb=2.6s eq_body=(240, -2.0) eq_presence=(5000, 2.0) eq_air=(10500, 2.0) pan=-0.15
freq: written 48=130.8Hz sounds 261.6Hz

Zero-drift: True (OK)
MIDI: .../_test/guitar_harmonics_test.mid (219 bytes)
soundfont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
WAV (solo): .../_test/guitar_harmonics_test.wav (709164 bytes)
Spectral check: 4-8kHz buzz energy = 0.7% (OK)

Written 48 (130.8 Hz) rendered peak 264.0 Hz (expected octave-up 261.6 Hz, ratio 2.02x)
partials re sounding pitch: 1x=118 2x=85 3x=44 5x=23 -> odd share 69%

ModalSynth custom bank: peak=0.900 late(1.0-1.5s) rms/peak=0.489
  reference marimba preset late rms/peak=0.0001 -> harmonics ring 6280x longer
Karplus loop_gain=0.9988: peak=0.369 tail(1-2s)=0.00156 vs 0.990 dull control 0.00015 -> 10.7x
Stem label: GM_PROGRAMS[31] = 'Guitar harmonics' -> file 'Guitar_harmonics'
SF2 preset 31 -> 'Guitar Harmonics'
Stems (2):
  track00_Guitar_harmonics.wav (709164 bytes)
  track01_Drums.wav (787756 bytes)

ALL CHECKS PASSED
```

Test composition: 1 bar, 1 section, 2 voices. Voice 0 = Guitar Harmonics
(channel 0, written arpeggio 48-55-60-64-67-72-67-60 = sounding
C4-G4-C5-E5-G5-C6 chime), voice 1 = drums (channel 9) as *context only*.
**The audio check renders voice 0 SOLO** (`render_midi(..., solo=0)` — one
voice, one track, no unison doubling), with the SF2 resolved through
`discover_soundfont()` (→ FluidR3_GM.sf2, 141 MB).

## 9. Files written

| File | Bytes |
|---|---|
| `Guitar/guitar_harmonics/instrument.md` | 9,655 |
| `Guitar/guitar_harmonics/guitar_harmonics.py` | 8,332 |
| `Guitar/guitar_harmonics/REPORT.md` | this file |
| `_test/verify_guitar_harmonics.py` | 9,047 |
| `_test/_probe_harmonics.py` | 2,760 (range/spectrum/decay probe) |
| `_test/guitar_harmonics_test.mid` | 219 |
| `_test/guitar_harmonics_test.wav` | 709,164 |
| `_test/stems_guitar_harmonics/track00_Guitar_harmonics.wav` | 709,164 |
| `_test/stems_guitar_harmonics/track01_Drums.wav` | 787,756 |
| `_test/registry_out_guitar_harmonics.txt` | registry verification log |
| `_test/verify_guitar_harmonics_out.txt` | verify log |

`registry.md` updated: Registry table row (Guitar / 31), stem-label quirk row
(incl. the pitch quirk), and the dated changelog entry
"**Guitar Harmonics added** (2026-11-13)".
