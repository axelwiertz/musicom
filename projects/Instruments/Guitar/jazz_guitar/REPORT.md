# Jazz Guitar (GM26) — Nightly Instrument Research Report

**Date**: 2026-10-22
**Family**: Guitar (5th entry — completes the nylon/steel/jazz/clean/overdriven tier)
**Module**: `Guitar/jazz_guitar/jazz_guitar.py` · `Guitar/jazz_guitar/instrument.md`
**Registry key**: `jazz_guitar` · **Constant**: `JAZZ_GUITAR`

## Instrument

GM26 = **Electric Guitar (jazz)** — the archtop hollow-body electric guitar
(Gibson ES-175 / L-5 / Super 400 lineage). The warm/round jazz voice: f-hole
hollow body + flatwound strings + **thumb** attack (Wes Montgomery octaves,
Freddie Green comping). NOT the solidbody clean electric (GM27): the archtop
is an acoustic resonator first, the pickup amplifies that voice; the tone is
dark, woody, vocal — the roundest guitar timbre in the KB.

## Program / GM

| Field | Value |
|---|---|
| MIDI_PROGRAM | 26 |
| GM_NAME | "Electric Guitar (jazz)" |
| STEM_LABEL | "Electric_Guitar_jazz" |
| Pipeline label | `GM_PROGRAMS[26] = "Electric Guitar (jazz)"` |
| FluidR3 preset 26 | "Jazz Guitar" (SF2 uses the common name — cosmetic) |
| MidiInstrument enum | NOT exposed (enum has 10; raw GM 26 used) |

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| RANGE_MIN | 28 | E1 (GM patch floor; real guitar E2=40) |
| RANGE_MAX | 84 | C6 (GM patch ceiling; real 22-fret ceiling E6=76) |
| SOLO_RANGE | (43, 76) | G2–E6 — idiomatic lead zone |
| SWEET_SPOT | (48, 72) | C3–C5 — comping heart |
| ZONES.low_strings | (28, 47) | E1–B2 — low roots, bass-note comping |
| ZONES.mid | (48, 64) | C3–E4 — THE jazz zone: comping, shell voicings, thumb melodies |
| ZONES.high | (65, 84) | F4–C6 — octave melodies, single-note fills |

Empirical FluidR3 sweep (notes 24–96, step 6): preset 26 audible **13/13**,
no gaps, **no treble cliff** (bottom 0.070 rms, top 0.065) — the SF2 patch
never clips a composition. The dark archtop tone is flat across the span.

## Role

`harmony, rhythm, comp, lead, melody, ornament, countermelody, accent` —
fully polyphonic, two idiomatic faces: **comping** (Freddie Green chords on
beats 2 & 4, shell voicings root-7th-3rd, 2–4 notes — NOT dense barre
chords) and **melody** (thumb single lines + Wes-style octave melodies).

## Synthesis engine

**Primary: Karplus-Strong** (`sound/synthesis/karplus_strong.py`) — the jazz
guitar IS a plucked string; the waveguide is the exact physical model.

| Parameter | Value | Rationale |
|---|---|---|
| loop_gain | 0.9975 | Flatwound ring 2–4 s; between steel_acoustic 0.9970 and harp 0.9985; overdriven 0.9990 = compression sustain |
| excitation | "thumb" | Round Wes attack, no pick click |
| width | 0.5 | Moderate pulse, round not bright |
| lowpass_hz | 3500 | Archtop neck-pickup rolloff — darker than clean electric 5000 |
| noise_component | 0.015 | Thumb is quiet; flatwounds reduce finger noise |

**Ring test**: late(1–2 s) rms/peak **0.0010** vs 0.0001 dull (0.990)
control → **6.7×** — flatwound ring clearly above the damped control.

**Fallback**: ModalSynth `'string'` preset. **Alt**: PhaseModSynth saw
carrier, ratio 1.0, mod_depth 1.5 (gentle twang), attack 0.01 s,
release 0.25 s.

## Constants

```python
MIDI_PROGRAM = 26
GM_NAME = "Electric Guitar (jazz)"
STEM_LABEL = "Electric_Guitar_jazz"
RANGE_MIN = 28; RANGE_MAX = 84
SOLO_RANGE = (43, 76); SWEET_SPOT = (48, 72)
ZONES = {"low_strings": (28, 47), "mid": (48, 64), "high": (65, 84)}
ARTICULATIONS = {
    "thumb": (75, 0.9), "pick": (72, 0.35), "finger": (65, 1.0),
    "comp_chord": (60, 0.25), "shell_voicing": (55, 0.5), "octave": (72, 0.6),
    "hammer_on": (72, 0.5), "pull_off": (62, 0.5), "slide": (70, 0.8),
    "bend": (80, 0.9), "vibrato": (68, 0.9), "arpeggio": (62, 0.3),
    "ghost_note": (42, 0.08), "accent": (92, 0.30),
}
SYNTHESIS = "karplus_strong"
KARPLUS_DEFAULTS = {"loop_gain": 0.9975, "excitation": "thumb",
                    "width": 0.5, "lowpass_hz": 3500, "noise_component": 0.015}
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 1.0, "mod_depth": 1.5,
               "attack": 0.01, "release": 0.25}
REVERB_TAIL = 2.0
EQ_BODY = (250, -2.0); EQ_PRESENCE = (2800, 2.0); EQ_AIR = (7500, 1.0)
PAN = -0.2
# midi_to_freq(midi) = 440.0 * 2 ** ((midi - 69) / 12.0)
```

## Registration proof

`instrument_registry.py` updated: `_INSTRUMENT_MODULES` gains
`"Guitar.jazz_guitar.jazz_guitar": "jazz_guitar"`, convenience constant
`JAZZ_GUITAR`, `registry_table()` role row, and `__main__` verification
lines. Verification run (`python instrument_registry.py`) — new row:

```
| Guitar | Electric Guitar (jazz) | 26 | 28–84 | harmony, rhythm, comp, lead, melody, ornament, countermelody, accent |
```

Verification block:

```
=== Jazz Guitar (Electric Guitar jazz, GM26) ===
  JAZZ_GUITAR.midi_program = 26 (should be 26)
  by_name('jazz guitar') = <Instrument Electric Guitar (jazz) (family=Guitar, program=26, range=28-84)>
  by_name('electric guitar (jazz)') = <Instrument Electric Guitar (jazz) (family=Guitar, program=26, range=28-84)>
  by_program(26) = <Instrument Electric Guitar (jazz) (family=Guitar, program=26, range=28-84)>
  JAZZ_GUITAR.in_sweet_spot(60) = True
  JAZZ_GUITAR.in_sweet_spot(24) = False
  JAZZ_GUITAR.range_min = 28 JAZZ_GUITAR.range_max = 84
  JAZZ_GUITAR.stem_label = 'Electric_Guitar_jazz'
```

Exit code 0. Full table (all ~70 instruments) printed with the new row.

## Verification results (`verify_jazz_guitar.py`)

| Check | Result |
|---|---|
| Registry import (by_name / by_program / JAZZ_GUITAR) | ✓ all resolve to Electric Guitar (jazz), program 26 |
| UnitMatrixComposer (1 bar, 1 section, **1 voice solo**) | built with GM26 on channel 0 |
| Zero-drift `validate()` | **True (OK)** |
| MIDI export | 153 bytes (> 40 ✓) |
| WAV render via `discover_soundfont()` (FluidR3_GM.sf2, solo track) | 718,892 bytes (718 KB, > 40 ✓) |
| Spectral check 4–8 kHz buzz | **0.1%** (OK, ≤ 20% gate) — cleanest of the set: the dark archtop tone has virtually no energy above 4 kHz |
| Pipeline stem label | `GM_PROGRAMS[26]` = "Electric Guitar (jazz)" ✓ |
| STEM_LABEL | 'Electric_Guitar_jazz' — matches pipeline sanitized label ✓ |
| SF2 preset phdr | preset 26 = "Jazz Guitar" ✓ |
| Stem render | `track00_Electric_Guitar_jazz.wav` on disk (718,892 bytes) ✓ |
| KS ring character | loop_gain 0.9975 → 0.0010 vs 0.990 → 0.0001 (**6.7×**) ✓ |
| Pitch sweep | notes 24–96 audible 13/13, no gaps, no treble cliff ✓ |

Test files: `Guitar/jazz_guitar/jazz_guitar_test.mid`, `jazz_guitar_test.wav`,
`stems_jazz_guitar/track00_Electric_Guitar_jazz.wav`.

## Quirks found

1. **Stem-label name quirk (cosmetic)**: pipeline `GM_PROGRAMS[26]` =
   "Electric Guitar (jazz)" (GM2 spec spelling) → stem file
   `Electric_Guitar_jazz.wav`; FluidR3 preset 26 = **"Jazz Guitar"** (SF2
   uses the common name). STEM_LABEL = "Electric_Guitar_jazz" matches the
   pipeline's real label so stem-file lookups work — same discipline as the
   "Bag pipe" (109) / "Shanai" (111) quirks. No routing impact.
2. **MidiInstrument enum**: GM26 not exposed (enum only has 10 entries) —
   composition jobs must use raw program 26 (registry is the full KB).
3. **Dark-tone mix note**: the jazz guitar occupies 200 Hz–4 kHz; keep bass
   below 200 Hz and bright instruments above 4 kHz for clean separation.
4. **Comping discipline**: shell voicings (2–4 notes), NOT dense 6-string
   barre chords — the mid-focused archtop tone turns dense chords to mud.
5. **Drive-by fix**: `registry_table()` overdriven-guitar role row corrected
   from generic default to its documented role (lead, melody, accent,
   rhythm, strum, countermelody).
