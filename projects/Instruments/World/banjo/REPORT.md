# Banjo — Instrument Research & Verification Report

**Date**: 2026-09-06 (nightly layer-aligned job)
**Family**: World (fifth entry — after sitar, koto, shamisen, kalimba)
**Files**: `instrument.md`, `banjo.py`, `REPORT.md` in `World/banjo/`
**Registry**: registered in `instrument_registry.py` (module
`World.banjo.banjo` → key `banjo`, constant `BANJO`)

---

## 1. Instrument

**Banjo** — plucked string instrument of American folk/bluegrass. 4–6
strings over a taut Mylar/animal-skin head stretched on a rim; the
vibrating membrane is the whole tone (bright, percussive "snap" that
decays fast). The standard 5-string banjo uses open **gDGBD** tuning with a
short 5th (drone) string. Two classic right-hand styles: **Scruggs
three-finger** (bluegrass rolls: T-I-M-T-M-I-T-M) and **clawhammer**
(old-time, downward brushing + drop-thumb). Prior art in repo: bluegrass /
folk styles (GM105 or GM25 lines), `SP011-karplus-jazz-swing` (Karplus
method, plucked-string family).

## 2. MIDI / GM program

| Thing | Value |
|---|---|
| GM program | **105** (GM1 Banjo) |
| GM name | `Banjo` |
| Stem label | `Banjo` (GM_PROGRAMS[105] = "Banjo" — **no quirk**) |
| FluidR3 preset 105 | `Banjo` (verified from phdr chunk) |
| TimGM6mb preset 105 | `Banjo` (fallback only; FluidR3 preferred) |

`MidiInstrument` enum (structures/instrument.py) does NOT expose 105 (it only
has 10 entries) — used the raw GM number, per the registry-is-the-full-KB rule.

## 3. Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 46–93 | A#2–A6 | practical 5-string banjo |
| Low | 46–59 | A#2–B3 | 4th/5th strings (C & g) — dark, thumpy head |
| Mid | 60–74 | C4–D5 | 3rd/2nd strings (G & B) — **primary melodic register** |
| High | 75–93 | D#5–A6 | 1st string (D) — bright, thin, cutting |

- `RANGE_MIN = 46`, `RANGE_MAX = 93`
- `SOLO_RANGE = (60, 84)` — C4–C6 solo repertoire focus
- `SWEET_SPOT = (62, 81)` — D4–A5, fullest head snap + string cut
- Open gDGBD tuning = MIDI 55-50-55-59-62 (low to high)
- Empirical FluidR3 sweep (RMS, notes 24–96): preset 105 **audible across
  the whole span, no gaps** — SF2 never clips a composition

## 4. Role in arrangement

`lead, melody, ornament, rhythm, accent` — monophonic roll/line instrument
(Scruggs rolls, hammer-ons/pull-offs), rhythmic backup strums, call-response
with fiddle/mandolin. NOT a harmony/pad instrument (roll voice by design).

## 5. Synthesis engine

| Priority | Engine | Why |
|---|---|---|
| **1 (primary)** | **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) | Plucked waveguide = correct physical model. `loop_gain` 0.9960 = moderate damping = snappy bright ring, head-snap decay |
| 2 | PhaseModSynth (FM) | cheap banjo: saw carrier, mod ratio 2.2, depth 3.2, instant attack |
| 3 | ModalSynth `'string'` preset | generic plucked-string resonator, loses head snap |

`SYNTHESIS = "karplus"`, `KARPLUS_DEFAULTS = {"loop_gain": 0.9960, "width": 0.40, "role": "lead"}`.

## 6. All constants (banjo.py)

```python
MIDI_PROGRAM = 105
GM_NAME = "Banjo"
STEM_LABEL = "Banjo"
RANGE_MIN = 46
RANGE_MAX = 93
SOLO_RANGE = (60, 84)
SWEET_SPOT = (62, 81)
ZONES = {"low": (46, 59), "mid": (60, 74), "high": (75, 93)}
ARTICULATIONS = {
    "pluck": (82, 1.0), "roll": (74, 0.12), "hammer": (88, 0.35),
    "pull": (70, 0.3), "choke": (48, 0.12),
}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9960, "width": 0.40, "role": "lead"}
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 2.2, "mod_depth": 3.2,
               "attack": 0.002, "release": 0.18}
REVERB_TAIL = 1.0
EQ_BODY = (280, -2.5)
EQ_PRESENCE = (3000, 2.5)
EQ_AIR = (8000, 1.0)
PAN = 0.0
# midi_to_freq: 440.0 * 2 ** ((midi - 69) / 12.0)
```

## 7. Registration proof

`python instrument_registry.py` — full `registry_table()` including the new row:

```
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
```

Verification lines:

```
  BANJO.midi_program = 105 (should be 105)
  by_name('banjo') = <Instrument Banjo (family=World, program=105, range=46-93)>
  by_program(105) = <Instrument Banjo (family=World, program=105, range=46-93)>
  BANJO.in_sweet_spot(69) = True
```

`ALL_INSTRUMENTS` count: 22 → **23**.

## 8. Verification results (engine test)

Script: `_test/verify_banjo.py` (pattern: `_test/verify_kalimba.py`, registry-backed).

| Check | Result |
|---|---|
| Registry import (`by_name("banjo")`, `by_program(105)`) | ✓ |
| UnitMatrixComposer 1 bar / 1 section (Banjo solo ch0 + context bass ch1 GM33, G#1 — below banjo low A#2, no overlap) | ✓ built |
| Zero-drift `validate()` | **True (OK)** |
| MIDI export `banjo_test.mid` | 135 bytes (>40 ✓) |
| WAV render (FluidSynth, `discover_soundfont()` → FluidR3_GM.sf2, **Banjo solo track only** — no unison doubling) | 2,408,236 bytes (>40 ✓) |
| Spectral buzz check (4–8 kHz band) | 5.4% (OK, ≤20%) |
| Stem label `GM_PROGRAMS[105]` | `'Banjo'` ✓ (STEM_LABEL matches) |
| SF2 preset 105 (phdr) | `'Banjo'` ✓ |
| Full RenderPipeline stem render | `track00_Banjo.wav` (2,408,236 B) + `track01_Electric_Bass_finger.wav` ✓ |
| Karplus-Strong smoke (loop_gain 0.9960 vs 0.990 control, 0.2–0.6 s window) | 0.019 vs 0.008 → **2.4× ring advantage** ✓ |
| Banjo ring vs sitar (0.9975) | 0.019 < 0.023 — decays faster ✓ (taut head vs sympathetic strings) |
| Empirical FluidR3 sweep (RMS 24–96) | audible 24..96, no gaps ✓ |

FluidSynth command (per pitfall spec):
`/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -g 1.2 -F <wav> <sf2> <mid>`
— via `_test/render_audio.py` `render_midi(midi_path, wav, solo=0)`.

## 9. Quirks found

1. **No stem-label quirk**: GM_PROGRAMS[105] = "Banjo" and FluidR3 preset
   105 = "Banjo" — labels match exactly (same as sitar/shamisen/koto/kalimba;
   the World plucked block 104–108 is fully clean).
2. **Loop_gain placement**: 0.9960 sits between kalimba (0.9940, metal tine)
   and koto (0.9970) — empirically verified 2.4× ring advantage over the
   0.990 dull control at the 0.2–0.6 s window (the 1–2 s window used for
   sitar/koto is past the banjo's head-snap ring).
3. **Line/rhythm instrument**: banjo is a roll/strum voice (Scruggs
   T-I-M-T-M-I-T-M + clawhammer), NOT a harmony voice — composition jobs
   write melodic/roll lines and rhythmic backup strums, not dense chords.
4. **Context bass note**: verify uses GM33 (Electric Bass finger) at G#1 —
   below the banjo's low A#2, so no unison doubling.
5. **Verify runtime note**: the full verify script takes ~2–5 min (FluidSynth
   solo render + stem render + sweep); the earlier 300 s foreground timeout
   hit mid-run — re-ran with tee + 600 s timeout, ALL CHECKS PASSED.

## Files

- `/opt/data/projects/Instruments/World/banjo/instrument.md`
- `/opt/data/projects/Instruments/World/banjo/banjo.py`
- `/opt/data/projects/Instruments/World/banjo/REPORT.md` (this file)
- `/opt/data/projects/Instruments/_test/verify_banjo.py`
- `/opt/data/projects/Instruments/_test/sweep_banjo.py`
- `/opt/data/projects/Instruments/_test/banjo_test.mid` (135 B)
- `/opt/data/projects/Instruments/_test/banjo_test.wav` (2.4 MB)
- `/opt/data/projects/Instruments/_test/banjo_sweep.mid/.wav` (5.1 MB sweep)
- `/opt/data/projects/Instruments/_test/stems_banjo/track00_Banjo.wav` + `track01_Electric_Bass_finger.wav`
- `/opt/data/projects/Instruments/instrument_registry.py` (registered)
- `/opt/data/projects/Instruments/registry.md` (changelog + table + quirks)
