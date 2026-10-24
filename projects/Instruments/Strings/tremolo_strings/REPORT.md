# Tremolo Strings — Instrument Research Report

**Date**: 2026-10-24 (nightly instrument research job)
**Status**: ✅ registered + verified end-to-end
**Files**: `Strings/tremolo_strings/instrument.md`, `Strings/tremolo_strings/tremolo_strings.py`,
`Strings/tremolo_strings/verify_tremolo_strings.py`, `Strings/tremolo_strings/REPORT.md`

---

## 1. Instrument & Program

| Field | Value |
|---|---|
| Instrument | **Tremolo Strings** |
| Family | Strings (eighth entry; bowed block complete) |
| MIDI program | **44** (0-indexed GM_PROGRAMS[44]; GM1 spec program 45 "Tremolo Strings"; Roland GS / Yamaha XG same) |
| GM name | "Tremolo Strings" |
| MidiInstrument enum | NOT exposed (enum only has 10) → raw 44 used; the registry is the full KB |

**Identity**: the bowed string SECTION playing rapid repeated bow strokes —
the film-score tension texture. Distinct from String Ensemble 1 (GM48,
sustained bows) and Pizzicato Strings (GM45, plucked): the section is
bowed and the bow never stops. The FluidR3 sample is genuinely
amplitude-modulated — measured trem-ripple **1.00** (near-silent between
bow strokes) on every note.

## 2. Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 24–96 | C1–C7 | full-section span (empirical sweep: audible every note, SILENT at 108+) |
| Low | 24–47 | C1–B2 | contrabass/cello — rumbling tension bottom, blurs fast |
| Middle | 48–71 | C3–B4 | viola/cello — the underscore workhorse |
| High | 72–96 | C5–C7 | violin top — cutting, glassy, chattering |
| Solo range | 53–89 | F3–A6 | solo-section focus |
| Sweet spot | 60–84 | C4–C6 | cleanest chattering zone |

## 3. Role

`accent, tension, texture, harmony, pad, countermelody` — the chattering
tension voice. NOT a solo melody voice (the AM masks pitch clarity — solo
lines go to violin/string_ensemble). NOT a bass voice (low tremolo is
rumble, not pitch).

## 4. Synthesis Engine

**Additive** (primary, `sound/synthesis/additive.py` — section = detuned
harmonic stack, String Ensemble 1 precedent):

- `ADDITIVE_HARMONICS["section_full"]` = [1.0, 0.9, 0.7, 0.5, 0.35, 0.25, 0.18]
- `SYNTHESIS_DEFAULTS`: instrument `tremolo_strings`, attack 0.02 (bow
  already moving), detune ±0.006, stack 3, release 0.20, `tremolo_hz` 7.0
- **Tremolo is NOT a musicom synthesis parameter** (verified: BowedString
  and Additive have no internal AM) → write at the note layer (fast
  repeated 16ths/32nds ≈ 7 Hz) or AM a long note at 7 Hz in production.
  The FluidR3 patch carries the tremolo already.

Secondary: **BowedString** (bow_velocity 0.26 — tremolo bowing is driven,
faster than fiddle 0.24 / section 0.2; bow_force 1.6; bow_position 0.12;
noise 0.015). Tertiary: PhaseModSynth saw "string machine" + AM.
Fallback: ModalSynth 'string' (section pizz).

## 5. Constants (`tremolo_strings.py`)

```python
MIDI_PROGRAM = 44
GM_NAME = "Tremolo Strings"
STEM_LABEL = "Tremolo_Strings"
RANGE_MIN = 24      RANGE_MAX = 96
SOLO_RANGE = (53, 89)   SWEET_SPOT = (60, 84)
ZONES = {"low": (24, 47), "mid": (48, 71), "high": (72, 96)}
ARTICULATIONS = {
    "tremolo": (72, 1.0), "sustain": (74, 1.0),
    "sul_ponticello": (80, 0.9), "staccato": (66, 0.25),
    "accent": (92, 0.9), "crescendo": (78, 1.4),
}
SYNTHESIS = "additive"
ADDITIVE_HARMONICS = {"section_full": [...], "section_sul": [...]}
SYNTHESIS_DEFAULTS = {"instrument": "tremolo_strings", "attack": 0.02,
    "detune": 0.006, "stack": 3, "release": 0.20, "tremolo_hz": 7.0}
MODAL_PRESET = "string"
BOWED_DEFAULTS = {"bow_velocity": 0.26, "bow_force": 1.6,
    "bow_position": 0.12, "noise_level": 0.015}
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 1.0,
    "mod_depth": 1.8, "attack": 0.02, "release": 0.2}
REVERB_TAIL = 2.4
EQ_BODY = (250, -2.5)   EQ_PRESENCE = (3000, 2.0)   EQ_AIR = (8500, 1.5)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## 6. Registration Proof

`instrument_registry.py`: module `"Strings.tremolo_strings.tremolo_strings": "tremolo_strings"`
added to `_INSTRUMENT_MODULES`; `TREMOLO_STRINGS = ALL_INSTRUMENTS["tremolo_strings"]`
convenience constant; `registry_table()` role row (`tremolo strings` → accent,
tension, texture, harmony, pad, countermelody); `__main__` verification lines.

Registry run output (full `registry_table()` printed, exit 0):

```
| Strings | String Ensemble 1 | 48 | 28–96 | harmony, pad, melody, countermelody, accent |
| Strings | Tremolo Strings | 44 | 24–96 | accent, tension, texture, harmony, pad, countermelody |
| Strings | Viola | 41 | 48–91 | lead, harmony, accent |
...
Verification:
  by_name('tremolo strings') = <Instrument Tremolo Strings (family=Strings, program=44, range=24-96)>
  by_program(44) = <Instrument Tremolo Strings (family=Strings, program=44, range=24-96)>
  TREMOLO_STRINGS.in_sweet_spot(72) = True
```

Full output saved to `_test/tremolo_registry_out.txt`.

## 7. Verification Results (engine test — SOLO render)

| Check | Result |
|---|---|
| Zero-drift | **True (OK)** — 1 bar, SOLO voice, terminal landmark flush at BAR |
| MIDI | `tremolo_strings_test.mid` — **93 bytes** (> 40 ✓) |
| WAV (solo, discover_soundfont → FluidR3_GM.sf2) | `tremolo_strings_test.wav` — **1,235,756 bytes** (> 40 ✓) |
| Spectral buzz gate (4–8 kHz) | **1.5%** (≤ 20% ✓, no comb-filtering — solo render, no unison doubling) |
| Stem label | GM_PROGRAMS[44] = "Tremolo Strings" → `track00_Tremolo_Strings.wav` ✓ (STEM_LABEL matches) |
| SF2 preset | preset 44 = **"Tremolo"** (phdr-verified; one-word SF2 spelling, cosmetic only) |
| RenderPipeline stems | `track00_Tremolo_Strings.wav` on disk, 1,235,756 bytes ✓ |
| Additive smoke | A3 note peak 0.124, late(1.0–1.5 s) rms/peak **0.241** — sustain holds, no collapse |
| AM rate check | envelope-AM peak at **exactly 7.00 Hz** (documented `tremolo_hz`) |
| FluidR3 pitch sweep | notes 24–96 ALL audible (rms 0.030–0.045), **SILENT at 108** — never write above C7=96 |

## 8. Quirks Found

1. **Stem label**: NO quirk — GM_PROGRAMS[44] = "Tremolo Strings" →
   `trackXX_Tremolo_Strings.wav` matches exactly. FluidR3 preset 44 =
   "Tremolo" (one-word SF2 spelling, cosmetic only, no routing impact).
2. **MidiInstrument enum**: 44 not exposed (enum has only ~10) — use raw 44.
3. **Channel quirk**: melodic channel (0–9) with program 44 — channel 9
   would trigger the drum-kit map (timpani/taiko lesson).
4. **Patch ceiling**: silent above 96 (C7) — sweep showed 96 OK, 108
   SILENT (rms 0.0000). Same class of ceiling as String Ensemble 1 (silent
   at 102+) but the floor extends lower (24 vs 28 — C1 audible here).
5. **Tremolo is not a synth-engine parameter**: BowedString/Additive have
   no internal AM — the tremolo must be written at the note layer (fast
   repeated 16ths/32nds ≈ 7 Hz) or AM in production. The GM patch itself
   is deeply amplitude-modulated (ripple 1.00).
6. **Additive decay_S quirk** (known): `get_adsr_weights` grid step scales
   with the top partial — decay_S 3e-5 holds a 2 s chord (synth_pad lesson
   applied); attack must be ~0.02 (bow already moving) NOT the 0.35 s
   String Ensemble 1 swell.
7. **Reverb**: 2.6 s (string_ensemble) is TOO long for tremolo — the
   chattering attack muddies; 2.4 s keeps it defined.
8. **Layering**: idiomatic doubling is octaves or a low sustained string
   BELOW — NEVER unison with another melodic patch (comb-filter buzz rule
   from 2026-09-01).

## 9. Files

- `Strings/tremolo_strings/instrument.md` — full research reference
- `Strings/tremolo_strings/tremolo_strings.py` — importable constants
- `Strings/tremolo_strings/verify_tremolo_strings.py` — verification script
- `Strings/tremolo_strings/tremolo_strings_test.mid/.wav` — artifacts
- `Strings/tremolo_strings/stems_tremolo_strings/track00_Tremolo_Strings.wav`
- `instrument_registry.py` — registered (module, constant, role row)
- `registry.md` — changelog entry + stem-label quirks row (2026-10-24)
