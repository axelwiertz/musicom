# REPORT — Synth Bass 1 (GM38)

**Date**: 2026-10-23 — Nightly Instrument Research Job (layer-aligned)
**Family**: Bass (second entry, after Electric Bass (finger) GM33)
**Folder**: `Bass/synth_bass_1/`

## Instrument

- **GM38 Synth Bass 1** (GM1 spec; Roland GS "Synth Bass 1 (analog)",
  Yamaha XG "SynthBass1"). The classic analog synth bass: VCO
  (saw/square) → resonant low-pass filter → ADSR gate. TB-303 acid,
  Minimoog fat, MC-202 bass-line lineage. **Distinct from Electric Bass
  (finger) GM33**: there is NO string — the tone is oscillator + filter.
- Files written:
  - `instrument.md` — full research (YAML frontmatter + sections)
  - `synth_bass_1.py` — importable constants
  - `verify_synth_bass_1.py` — engine verification (solo render)
  - `synth_bass_1_test.mid` / `synth_bass_1_test.wav` / `stems_synth_bass_1/` — artifacts
  - `REPORT.md` — this file

## Program / labels

| Field | Value |
|---|---|
| MIDI program | 38 (0-indexed, matches FluidR3 preset 38 + pipeline GM_PROGRAMS[38]) |
| GM name | "Synth Bass 1" |
| Stem label | `Synth_Bass_1` → `trackXX_Synth_Bass_1.wav` — **no quirk** (GM_PROGRAMS[38] = "Synth Bass 1"; FluidR3 preset 38 = "Synth Bass 1", phdr-verified) |
| MidiInstrument enum | NOT exposed (enum has 10 only) — use raw `program=38` in `add_voice` |

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full range (GM patch) | 24–84 | C1–C5 |
| Sub | 24–35 | C1–E2 |
| Groove (root pocket) | 36–50 | E2–D3 |
| Mid (riff centre) | 51–62 | D#3–D4 |
| High (lead-bass) | 63–84 | D#4–C5 |

- `SOLO_RANGE = (31, 60)` (G1–C4), `SWEET_SPOT = (38, 62)` (D2–D4)
- Empirical FluidR3 sweep (RMS, notes 24–84): audible 6/6, smooth rolloff
  0.0355 → 0.0201, no gaps — SF2 never clips a composition.

## Role

bass, rhythm, groove, accent — the electronic bass foundation. Locks with
the kick like the electric bass but with filter color. Monophonic line
voice: one note at a time, NO chords.

## Synthesis engine

- **Primary: MonoSynth** (`sound/synthesis/mono_synth.py`) — the exact
  subtractive architecture of the classic analog bass (MC-202/AD-202
  lineage). `SYNTHESIS_DEFAULTS` (loads through the registry):
  ```python
  {"waveform": "saw", "sub_level": 0.3, "filter_cutoff": 1800.0,
   "filter_resonance": 0.55, "filter_env_amount": 0.5, "filter_keytrack": 0.5,
   "env_a": 0.005, "env_d": 0.18, "env_s": 0.75, "env_r": 0.12,
   "saturation": 0.15, "drift_amount": 0.002}
  ```
  Smoke test: D2 peak 0.800, sustain_rms/peak 0.338 — gate sustain
  confirmed, no collapse.
- **Secondary: PhaseModSynth** (`FM_DEFAULTS`: saw carrier, sine mod,
  ratio 1.0, depth 2.5, attack 0.005, release 0.12) — FM "Solid Bass".
- **Tertiary: Karplus-Strong** (`KARPLUS_DEFAULTS`: loop_gain 0.9960,
  lowpass_hz 1500, excitation "pluck") — "rubber band" fallback.
- **Weak fallback: ModalSynth** 'string' preset (`MODAL_PRESET`).

## All constants (`synth_bass_1.py`)

```python
MIDI_PROGRAM = 38
GM_NAME = "Synth Bass 1"
STEM_LABEL = "Synth_Bass_1"
RANGE_MIN = 24; RANGE_MAX = 84
SOLO_RANGE = (31, 60); SWEET_SPOT = (38, 62)
ZONES = {"sub": (24, 35), "groove": (36, 50), "mid": (51, 62), "high": (63, 84)}
ARTICULATIONS = {
    "legato": (68, 1.0), "staccato": (74, 0.35), "accent": (96, 0.6),
    "glide": (64, 1.0), "squelch": (88, 0.5), "octave_jump": (80, 0.4),
    "ghost": (40, 0.15),
}
SYNTHESIS = "mono_synth"
SYNTHESIS_DEFAULTS = {...}  # see above
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_shape": "sine", "mod_freq_ratio": 1.0,
               "mod_depth": 2.5, "attack": 0.005, "release": 0.12}
KARPLUS_DEFAULTS = {"loop_gain": 0.9960, "lowpass_hz": 1500.0,
                    "excitation": "pluck", "role": "bass"}
REVERB_TAIL = 1.0
EQ_BODY = (250, -2.5); EQ_PRESENCE = (900, 2.0); EQ_AIR = (6000, 1.0)
PAN = 0.0
# midi_to_freq(midi) standard 440·2^((midi-69)/12)
```

## Registration proof

`instrument_registry.py` changes:
1. `_INSTRUMENT_MODULES["Bass.synth_bass_1.synth_bass_1"] = "synth_bass_1"`
2. `SYNTH_BASS_1 = ALL_INSTRUMENTS["synth_bass_1"]` convenience constant
3. `registry_table()` role row: `elif low == "synth bass 1": role = "bass, rhythm, groove, accent"`
4. `__main__` verification block for SYNTH_BASS_1

Registry run (`python instrument_registry.py`, exit 0) — new row in table:

```
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
| Bass | Synth Bass 1 | 38 | 24–84 | bass, rhythm, groove, accent |
```

Verification lines:

```
=== Synth Bass 1 (GM38) ===
  SYNTH_BASS_1.midi_program = 38 (should be 38)
  by_name('synth bass 1') = <Instrument Synth Bass 1 (family=Bass, program=38, range=24-84)>
  by_name('SYNTH BASS 1') = <Instrument Synth Bass 1 (family=Bass, program=38, range=24-84)>
  by_program(38) = <Instrument Synth Bass 1 (family=Bass, program=38, range=24-84)>
  SYNTH_BASS_1.in_sweet_spot(48) = True
  SYNTH_BASS_1.in_sweet_spot(20) = False
  SYNTH_BASS_1.range_min = 24 SYNTH_BASS_1.range_max = 84
  SYNTH_BASS_1.stem_label = 'Synth_Bass_1'
```

Full registry output saved to `_test/synth_bass_registry_out.txt`.

## Verification results (verify_synth_bass_1.py — ALL CHECKS PASSED)

| Check | Result |
|---|---|
| Registry by_name('synth bass 1') | `<Instrument Synth Bass 1 ...>` ✓ |
| Registry by_program(38) | same object ✓ |
| Zero-drift (UnitMatrixComposer, 1 bar, 1 voice SOLO) | True (OK) ✓ |
| MIDI export | 111 bytes (> 40) ✓ |
| WAV solo render (FluidSynth, discover_soundfont → FluidR3_GM.sf2) | 798,252 bytes (> 40) ✓ |
| Spectral 4–8 kHz buzz | 1.8% (gate 20%) — no comb-filtering ✓ |
| Stem label vs pipeline | GM_PROGRAMS[38] = "Synth Bass 1" → `Synth_Bass_1` ✓ |
| SF2 preset 38 phdr | "Synth Bass 1" ✓ |
| RenderPipeline stem | `track00_Synth_Bass_1.wav` (798,252 bytes) ✓ |
| MonoSynth smoke | peak 0.800, sustain_rms/peak 0.338 ✓ |
| FluidR3 pitch sweep 24–84 | 6/6 audible, no gaps ✓ |

Audio check was **instrument SOLO only** (one voice, one track) — no
unison doubling, no comb-filtering (the 2026-09-01 lesson).

## Quirks found

- **No stem-label quirk**: GM_PROGRAMS[38] = "Synth Bass 1" and FluidR3
  preset 38 = "Synth Bass 1" — exact match both sides (contrast the
  "Bag pipe"/"Shanai" quirks at 109/111).
- **Monophonic gate voice**: synth bass is one oscillator voice — one
  note at a time, NO chords. Gate time (note length) IS the articulation;
  velocity triggers filter-envelope amount on many synths, but the gate is
  the signature. Composition jobs should write staccato/legato patterns,
  not dense harmony.
- **Channel quirk**: melodic channel (0–9) with program 38 — channel 9
  would trigger the drum-kit map (timpani lesson).
- **Dark by design**: little energy above 4 kHz once the filter closes —
  spectral buzz 1.8% is expected LOW; the 6 kHz air shelf is for
  oscillator/saturation texture, not harmonic content.
- **REVERB_TAIL 1.0 s** is the shortest in the Bass family (electric bass
  1.4 s) — synth bass is almost always dry; verb thins the low end.
- **Registry.md static table was stale**: the Electric Bass (finger) row
  was missing from the Registry table (added as a drive-by fix alongside
  the new Synth Bass 1 row).

## Registry.md updates

- Changelog: **Synth Bass 1 added** (2026-10-23) entry appended.
- Registry table: added `| Bass | Electric Bass (finger) | 33 | ...` (gap
  fix) and `| Bass | Synth Bass 1 | 38 | 24–84 | bass, rhythm, groove, accent |`.
- Stem-label quirks table: added row 38 → `Synth_Bass_1` ✓ (no quirk).
