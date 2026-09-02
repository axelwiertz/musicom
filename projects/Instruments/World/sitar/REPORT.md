# Sitar — Instrument Research & Verification Report

**Date**: 2026-09-02 (nightly layer-aligned job)
**Family**: World (new family — first entry)
**Files**: `instrument.md`, `sitar.py`, `REPORT.md` in `World/sitar/`
**Registry**: registered in `instrument_registry.py` (module `World.sitar.sitar`
→ key `sitar`, constant `SITAR`)

---

## 1. Instrument

**Sitar** — plucked lute of Hindustani classical music. 18–21 strings
(6–7 played over curved frets, remainder sympathetic `tarb` strings that
ring in sympathy). Signature tone comes from the **jawari** bridge: a
shaped, slightly curved bridge surface that lets the string slap it,
producing the characteristic buzzy, sustained overtone-rich sound.
Prior art in repo: `IndianClassical/018-hindustani-bhairavi` (GM104 melody +
tanpura drone), `SP050-spectral-delay-indian-popular` (GM104 melody + GM33
bass), `World/bollywood-study` (GM104 sitar line).

## 2. MIDI / GM program

| Thing | Value |
|---|---|
| GM program | **104** (GM1 Sitar) |
| GM name | `Sitar` |
| Stem label | `Sitar` (GM_PROGRAMS[104] = "Sitar" — **no quirk**) |
| FluidR3 preset 104 | `Sitar` (verified from phdr chunk) |
| TimGM6mb preset 104 | `Sitar` (fallback only; FluidR3 preferred) |
| Prior art programs | 104 used consistently across 3 repo styles |

`MidiInstrument` enum (structures/instrument.py) does NOT expose 104 (it only
has 10 entries) — used the raw GM number, per the registry-is-the-full-KB rule.

## 3. Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | concert sitar (Kharaj Pancham) |
| Low (kharaj) | 55–61 | G3–B3 | bass strings — dark, long meend |
| Mid (jod/baaj) | 62–77 | D4–G5 | **primary melodic register** |
| High (chikari) | 78–96 | G#5–C7 | drone + high melody, thin/cutting |

- `RANGE_MIN = 55`, `RANGE_MAX = 96`
- `SOLO_RANGE = (60, 89)` — C4–A6 solo repertoire focus
- `SWEET_SPOT = (62, 84)` — D4–C6, fullest jawari buzz
- Meend (bend) extends any note up ~7 semitones (Vilayat Khan gayaki ang)

## 4. Role in arrangement

`lead, melody, ornament, drone` — monophonic lead/ornament instrument
(gamak, meend, tans), chikari drone strokes, call-response with voice or
flute. NOT a harmony/pad instrument.

## 5. Synthesis engine

| Priority | Engine | Why |
|---|---|---|
| **1 (primary)** | **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) | Plucked waveguide = correct physical model. High `loop_gain` = low damping = ringing partials = sitar sustain |
| 2 | PhaseModSynth (FM) | cheap sitar: saw carrier, mod ratio 2.0, depth 4, instant attack |
| 3 | ModalSynth `'string'` preset | generic plucked-string resonator, loses buzz character |

`SYNTHESIS = "karplus"`, `KARPLUS_DEFAULTS = {"loop_gain": 0.9975, "width": 0.45, "role": "lead"}`.
Registry `_FIELDS` extended with `karplus_defaults` (was missing — the new
field loads through `instrument_registry.py` like `modal_preset`/`fm_defaults`).

## 6. All constants (sitar.py)

```python
MIDI_PROGRAM = 104
GM_NAME = "Sitar"
STEM_LABEL = "Sitar"
RANGE_MIN = 55
RANGE_MAX = 96
SOLO_RANGE = (60, 89)
SWEET_SPOT = (62, 84)
ZONES = {"low": (55, 61), "mid": (62, 77), "high": (78, 96)}
ARTICULATIONS = {
    "pluck": (78, 1.0), "meend": (70, 1.6), "gamak": (84, 0.35),
    "chikari": (60, 0.12), "mute": (45, 0.15),
}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9975, "width": 0.45, "role": "lead"}
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 2.0, "mod_depth": 4.0,
               "attack": 0.002, "release": 0.25}
REVERB_TAIL = 2.2
EQ_BODY = (350, -2.5)
EQ_PRESENCE = (2500, 2.5)
EQ_AIR = (9000, 1.5)
PAN = 0.0
# midi_to_freq: 440.0 * 2 ** ((midi - 69) / 12.0)
```

## 7. Registration proof

`python instrument_registry.py` — full `registry_table()` including the new row:

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
...
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
```

Verification lines:

```
  SITAR.midi_program = 104 (should be 104)
  by_name('sitar') = <Instrument Sitar (family=World, program=104, range=55-96)>
  by_program(104) = <Instrument Sitar (family=World, program=104, range=55-96)>
  SITAR.in_sweet_spot(69) = True
```

`ALL_INSTRUMENTS` count: 18 → **19**.

## 8. Verification results (engine test)

Script: `_test/verify_sitar.py` (pattern: `_test/verify_marimba.py`, registry-backed).

| Check | Result |
|---|---|
| Registry import (`by_name("sitar")`, `by_program(104)`) | ✓ |
| UnitMatrixComposer 1 bar / 1 section (Sitar solo ch0 + context bass ch1 GM33, C3 — octave below) | ✓ built |
| Zero-drift `validate()` | **True (OK)** |
| MIDI export `sitar_test.mid` | 135 bytes (>40 ✓) |
| WAV render (FluidSynth, `discover_soundfont()` → FluidR3_GM.sf2, **Sitar solo track only** — no unison doubling) | 1,588,268 bytes (>40 ✓) |
| Spectral buzz check (4–8 kHz band) | 2.1% (OK, ≤20%) |
| Stem label `GM_PROGRAMS[104]` | `'Sitar'` ✓ (STEM_LABEL matches) |
| SF2 preset 104 (phdr) | `'Sitar'` ✓ |
| Full RenderPipeline stem render | `track00_Sitar.wav` (1,588,268 B) + `track01_Electric_Bass_finger.wav` ✓ |
| Karplus-Strong smoke (loop_gain 0.9975 vs 0.990 control) | tail 1–2 s rms/peak = 0.005 vs 0.002 → **3.3× ring advantage** ✓ |

FluidSynth command (per pitfall spec): `/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -g 1.2 -F <wav> <sf2> <mid>` — via `_test/render_audio.py` `render_midi(midi_path, wav, solo=0)`.

## 9. Quirks found

1. **`karplus_defaults` missing from registry `_FIELDS`** — first attribute
   access raised `AttributeError`. Fixed by adding the field to
   `instrument_registry._FIELDS` (now `modal_preset`, `karplus_defaults`,
   `fm_defaults` all load). This is a NEW quirk for plucked-synth-family
   instruments; future instruments with engine-preset dicts need their
   fields listed there.
2. **No stem-label quirk**: GM_PROGRAMS[104] = "Sitar" and FluidR3 preset
   104 = "Sitar" — first World-family instrument, labels match exactly.
3. **Karplus fade artifact in measurement**: the module's built-in 10% fade
   clips the tail; the 1–2 s measurement window (pre-fade) was used instead.
4. **Sitar WAV is *supposed* to have twang** — the 4–8 kHz spectral gate
   still passed at 2.1% for a solo pluck (comb-filter buzz from unison
   doubling is the failure mode, not the instrument's own partials).
5. **Neighbor programs for future World entries**: GM105 Banjo, 106
   Shamisen, 107 Koto are already labeled correctly in the pipeline list —
   no off-by-one surprises for the next candidates.
