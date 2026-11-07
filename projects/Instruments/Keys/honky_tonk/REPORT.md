# REPORT — Honky-tonk Piano (GM3)

**Date**: 2026-11-07 · **Family**: Keys (11th entry) · **Registry key**: `honky_tonk`

## 1. Instrument

The honky-tonk piano is a **deliberately detuned, hardened-hammer piano** — the
saloon/barrelhouse/tack piano of ragtime, stride, boogie-woogie and country
honky-tonk. Two physical facts define the timbre:

1. **Detuned unisons** — each note's 2–3 unison strings sit 10–25 cents apart, so
   every sustained note beats at 1–8 Hz (the "jangle").
2. **Hard hammers / tacks** — thumbtacks or hardened felt on the hammer heads give
   a metallic **clack** attack (2–6 kHz) instead of a soft felt tone.

Historically the detuning was functional: in a loud, crowded bar with no PA, a
beating midrange + clacky attack cut through the room. Later it became an
aesthetic (Westerns, ragtime revival, country, Tom Waits / Dr. John / Jerry Lee
Lewis).

## 2. MIDI / GM

| Item | Value |
|---|---|
| GM program | **3** (0-based MIDI program 3 = 4th GM entry, "Honky-tonk Piano") |
| Enum | NOT in `structures/instrument.py` `MidiInstrument` (10 only) — use raw `program=3` |
| Channel | melodic 0–9 (ch9 would hit the drum map + `Acoustic_Grand_Piano` fallback label) |
| FluidR3 (resolved by `discover_soundfont()`) | bank-0 preset 3 = **"Honky Tonk"** (phdr-verified) |
| RenderPipeline stem | `GM_PROGRAMS[3]` = "Honky-tonk Piano" → `trackXX_Honky-tonk_Piano.wav` |
| Stem quirk | sanitizer keeps the **hyphen** (only spaces/parens/slashes rewritten); SF2 drops the hyphen — cosmetic, no routing impact |

## 3. Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full (idiomatic) | 33–96 | A1–C7 |
| Solo / focus | 48–84 | C3–C6 |
| Sweet spot | 55–84 | G3–C6 (nasal honk band) |
| Bass | 33–47 | A1–B2 (stride/boogie LH) |
| Mid-low | 48–59 | C3–B3 (comp body) |
| Mid | 60–71 | C4–B4 (ragtime melody/chords) |
| High | 72–96 | C5–C7 (runs, octave tremolo, gliss) |

Real piano compass is A0–C8 (21–108), but the honky patch is mud below A1 and
tack-noise above C7. Empirical FluidR3 sweep (RMS, velocity 90, notes 24–108
step 12): **audible 8/8, no gaps** — 968.4 / 582.5 / 593.7 / 469.0 / 238.6 /
167.1 / 69.4 / 99.9 (×10⁻⁴).

## 4. Articulations (velocity, duration factor)

| Name | Vel | Dur | Use |
|---|---|---|---|
| ragtime_melody | 88 | 0.95 | syncopated RH line (default) |
| stride_bass | 92 | 0.50 | LH "oom" percussive octave |
| stride_chord | 80 | 0.40 | clipped off-beat "pah" |
| boogie_ostinato | 85 | 0.45 | rolling LH eighths |
| comp_chop | 76 | 0.30 | country/pop stab |
| octave_tremolo | 82 | 1.0 | alternating octaves |
| glissando | 95 | 0.90 | white-key rake |
| tack_accent | 108 | 0.85 | metallic clack |
| sustain_wash | 58 | 1.0 | pedal-down chord ring |
| dead_thud | 44 | 0.18 | damped comic "plunk" |

## 5. Synthesis

**Primary — ModalSynth** (`sound/synthesis/modal.py`), `MODAL_PRESET = "string"`,
plus a custom bank `HONKY_TONK_MODES` where **each partial is doubled at a
+17-cent twin** (5 partials × 2 strings, stretched ratios):

```
440.0 1.00 0.70   444.3 0.80 0.72   # f0 + detuned twin -> 4.3 Hz beat
881.5 0.55 0.95   890.1 0.44 0.98   # 2nd (2.004x)
1325.0 0.32 1.20  1337.9 0.26 1.24  # 3rd (3.011x)
1773.9 0.18 1.50  1791.2 0.14 1.55  # 4th (4.031x)
2227.7 0.10 1.90  2687.0 0.06 2.40  # 5th (5.063x), 6th (6.107x)
```

**Measured on the rendered bank**: dominant envelope-AM peak **4.50 Hz**
(gate 3.5–5.5), AM depth **1.25**; the no-twin control's dominant peak is
8.50 Hz — i.e. the beating is produced by the model, not an artifact.

**Secondary — Additive** (`sound/synthesis/additive.py`): detuned harmonic stack,
`ADDITIVE_HARMONICS["honky_tonk"] = [1.0, 0.62, 0.44, 0.27, 0.16, 0.09, 0.04]`
(relative — normalize to sum 1.0), `stack=2`, `detune=0.010` (±17 cents),
`decay_S=1e-4` for long holds.

**Tertiary — PhaseModSynth** (`sound/synthesis/phase_mod.py`): sine carrier +
sine modulator, ratio 2.01, depth 1.6, attack 3 ms, release 0.35 s.

## 6. Constants (Keys/honky_tonk/honky_tonk.py)

```python
MIDI_PROGRAM = 3
GM_NAME = "Honky-tonk Piano"
STEM_LABEL = "Honky-tonk_Piano"
RANGE_MIN = 33;  RANGE_MAX = 96
SOLO_RANGE = (48, 84);  SWEET_SPOT = (55, 84)
SYNTHESIS = "modal";  MODAL_PRESET = "string"
REVERB_TAIL = 1.4
EQ_BODY = (300, -2.0); EQ_PRESENCE = (1800, 2.5); EQ_AIR = (8000, 1.5)
PAN = 0.0
SYNTHESIS_DEFAULTS = {instrument: "honky_tonk", attack: 0.004, detune: 0.010,
                      stack: 2, release: 0.25, sustain_level: 0.55, decay_S: 1e-4}
```

Production rationale: small wooden **room** reverb (1.4 s) — a hall smears the
tack attack and turns the beating to mud; EQ cut 300 Hz (upright cabinet boom),
boost 1.8 kHz (nasal honk), air shelf 8 kHz +1.5 dB (tack clack).

## 7. Registration proof

`_INSTRUMENT_MODULES["Keys.honky_tonk.honky_tonk"] = "honky_tonk"`, constant
`HONKY_TONK`, role branch in `registry_table()`, verification block in
`instrument_registry.py __main__`.

`registry_table()` row (full run: `_test/registry_out_honky_tonk.txt`, 90 table
lines, exit 0):

```
| Keys | Honky-tonk Piano | 3 | 33–96 | rhythm, harmony, melody, bass, ornament, color |
```

Verification lines:

```
=== Honky-tonk Piano (Tack Piano, GM3) ===
  HONKY_TONK.midi_program = 3 (should be 3)
  by_name('honky tonk') = <Instrument Honky-tonk Piano (family=Keys, program=3, range=33-96)>
  by_name('Honky-tonk Piano') = <Instrument Honky-tonk Piano (family=Keys, program=3, range=33-96)>
  by_program(3) = <Instrument Honky-tonk Piano (family=Keys, program=3, range=33-96)>
  HONKY_TONK.in_sweet_spot(67) = True
  HONKY_TONK.in_sweet_spot(24) = False
  HONKY_TONK.range_min = 33 HONKY_TONK.range_max = 96
  HONKY_TONK.stem_label = 'Honky-tonk_Piano'
```

## 8. End-to-end verification (`_test/verify_honky_tonk.py`)

Composition: 1 bar, 1 section, 2 voices — Honky-tonk **SOLO** voice (stride
octaves on 1 & 3, clipped off-beat chords on 2 & 4, ragtime C5-E5-G5 turn) +
drum-kit context on channel 9. **No second melodic patch on the same pitches**
(no unison doubling → no comb buzz).

| Check | Result |
|---|---|
| Zero-drift `validate()` | **True (OK)** |
| MIDI export | `_test/honky_tonk_test.mid` — **245 bytes** (> 40 ✓) |
| FluidSynth solo WAV | `_test/honky_tonk_test.wav` — **808,748 bytes**, FluidR3_GM.sf2 via `discover_soundfont()` |
| 4–8 kHz spectral buzz | **0.5 %** (gate ≤ 20 %) — clean |
| Pipeline stem label | `GM_PROGRAMS[3]` = `'Honky-tonk Piano'` ✓ |
| SF2 preset | preset 3 → `'Honky Tonk'` (phdr) |
| Stems on disk | `track00_Honky-tonk_Piano.wav` (808,748 B), `track01_Drums.wav` (835,628 B) |
| Modal beating | **4.50 Hz**, AM depth 1.25 (control 8.50 Hz) |
| Additive stack | weights normalized, renders non-zero |
| Pitch sweep 24–108 | 8/8 audible, no gaps |
| Pytest regression | `tests/test_ballad_palette.py tests/test_voice_hybrid.py` → **34 passed** |

## 9. Quirks / writing notes

1. **Beating is intended** — but never double it: a second detuned piano (or a
   piano + honky-tonk on the same pitches) multiplies the beat rate and sounds
   seasick. Octave-split or pan apart.
2. **Keep chords open** (≤3 notes in the mid) — the doubled partials already
   make the spectrum dense; close voicings turn to mush.
3. **Rhythmic voice, not a foundation** — A1 bottom; pair with a real bass for
   sub-A1 weight. The GM patch is compressed: carry dynamics by articulation
   and register, not velocity extremes.
4. **Sanitizer keeps the hyphen** — stem files are `trackXX_Honky-tonk_Piano.wav`
   (no underscore between "Honky" and "tonk").
5. **Modal bank is A4-referenced** — `HONKY_TONK_MODES` frequencies are ratios of
   A4; scale per note at render time, as with `RHODES_MODES` / `CELESTA_MODES`.
6. **Legacy numbering note** — the registry's `piano` entry uses 1 for Acoustic
   Grand (one above the 0-based GM slot); honky-tonk correctly uses **3**, which
   is both the 0-based program and the `GM_PROGRAMS[3]` index.

## 10. Artifacts

- `Keys/honky_tonk/instrument.md`
- `Keys/honky_tonk/honky_tonk.py`
- `Keys/honky_tonk/REPORT.md` (this file)
- `_test/verify_honky_tonk.py`, `_test/verify_honky_tonk_out.txt`
- `_test/registry_out_honky_tonk.txt`
- `_test/honky_tonk_test.mid`, `_test/honky_tonk_test.wav`,
  `_test/stems_honky_tonk/`
