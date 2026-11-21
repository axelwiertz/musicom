# Electric Grand Piano (GM2) — Instrument Research Report

**Date**: 2026-11-21 (nightly instrument research job)
**Family**: Keys (twelfth entry)
**Instrument**: Electric Grand Piano — Yamaha CP-70/CP-80 (1974) amplified grand
**GM program**: 2 (0-based; GM1 "Electric Grand Piano")
**Files**: `Keys/electric_grand/instrument.md`, `Keys/electric_grand/electric_grand.py`,
`_test/verify_electric_grand.py`, `_test/electric_grand_test.mid/.wav`,
`_test/stems_electric_grand/`

---

## 1. Instrument identity

GM2 = the **amplified/electrified grand piano**. The Yamaha CP-70 (1974,
73 keys, E1–E7 = 28–100) and CP-80 (88 keys, A0–C8 = 21–108) are *real
acoustic grand pianos* — full-size strings, real hammers, real dampers —
built with **no soundboard**: each string group sits over a **magnetic
pickup** (electric-guitar style) wired to a built-in preamp and an external
amplifier.

Consequences that define the voice:

- **Long clean sustain** — the soundboard is the main energy sink of an
  acoustic grand; without it the string rings 3–8 s, almost undamped.
- **Glassy attack** — the hammer-on-wound-steel transient is captured close
  by the pickup: bright, metallic, cutting (the instrument's signature).
- **Huge clear bass** — the pickup captures the full string vibration; the
  CP-80 low register is round and present (firmer than the Rhodes' soft sub).
- **Clean tone, no soundboard bloom** — no body resonance under the note.
- **Fully polyphonic** keyboard — melody, harmony, bass all at once.

Famous voice: Supertramp "The Logical Song" / "Goodbye Stranger" (CP-80),
Billy Joel "My Life" (CP-70), Toto "Africa" intro (CP-80), Queen "You're My
Best Friend" (John Deacon, CP-80), Peter Gabriel "Sledgehammer" (CP-80),
Journey "Don't Stop Believin'" (CP-70).

Distinct from: GM1 Acoustic (soundboard projection, warm bloom), GM4 Rhodes
(tine, pickup-compressed dynamics, "bark"), GM5 FM EP2 (no string at all,
synthetic bell). The CP is the **brightest of the electric pianos**.

## 2. Program / channel / range

| Property | Value |
|---|---|
| MIDI program | **2** (raw 0-based GM; `MidiInstrument` enum does NOT expose it — 10-instrument legacy enum) |
| Channel | any melodic channel 0–9 (ch9 would trigger the drum-kit map + `Acoustic_Grand_Piano` program-0 fallback label) |
| Range | 21–108 (A0–C8) — full 88-key CP-80 compass; CP-70 = 73 keys E1–E7 (28–100) |
| Sweet spot | 60–84 (C4–C6) — the glassy attack zone ("The Logical Song" register) |
| Solo range | 48–84 (C3–C6) |
| Zones | sub 21–35 (A0–B1, huge clear sub), bass 36–47 (C2–B2, left-hand), mid 48–71 (C3–B4, primary), high 72–96 (C5–C7, glassy lead), top 97–108 (C#7–C8, sparkle) |

## 3. Role

**harmony, melody, bass, rhythm, accent, color** — the fully polyphonic
amplified-grand voice. NOT a sub-bass foundation (that is a bass guitar), NOT
a Rhodes/FM substitute. Records double it with an acoustic grand or strings —
but NEVER a second melodic patch on the same pitches (2026-09-01 comb-filter
rule).

Humanize DNA: Keys family (6.0 ms timing sigma, 5.0 velocity sigma, 0.0
layback, 0.015 duration sigma) — sits on the grid.

## 4. Synthesis engines (musicom)

| Rank | Engine | Preset / defaults | Evidence |
|---|---|---|---|
| 1 (primary) | **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) | `loop_gain` **0.9982** (above sitar 0.9975, near harp 0.9985 — no soundboard to damp the string), `width` 0.8, `lowpass_hz` 5500 (pickup bandwidth), `noise_component` 0.02 (hammer felt) | ring test vs 0.990 dull control: **4.2×** late(1.5–2.0 s) rms (0.0005 vs 0.0001) |
| 2 (secondary) | **ModalSynth-family `ResonatorBank`** (`sound/synthesis/modal.py`) | custom `ELECTRIC_GRAND_MODES` near-harmonic 1:2:3:4:5 (440/880/1320/1760/2200 Hz, amps 1.0/0.6/0.35/0.18/0.09, decay rates 0.9–2.2) — piano strings are near-harmonic, NOT the Rhodes tine's compressed inharmonic set; `MODAL_PRESET 'string'` = closest stock bank | measured late(1.5–2.0 s) rms/peak **0.100** — long soundboard-less ring |
| 3 (tertiary) | **PhaseModSynth** (`sound/synthesis/phase_mod.py`) | `FM_DEFAULTS`: sine carrier, ratio 2.0, depth 2.0 (bright but not nasal; DX EP2 uses 2.8 for the bell), attack 0.003 s, release 1.2 s | smoke: C5 peak 0.798 |

## 5. Constants (electric_grand.py)

```python
MIDI_PROGRAM = 2
GM_NAME = "Electric Grand Piano"
STEM_LABEL = "Electric_Grand_Piano"
RANGE_MIN, RANGE_MAX = 21, 108
SOLO_RANGE = (48, 84)
SWEET_SPOT = (60, 84)
ZONES = {"sub": (21, 35), "bass": (36, 47), "mid": (48, 71),
         "high": (72, 96), "top": (97, 108)}
ARTICULATIONS = {"legato_pedal": (50, 1.0), "touch": (70, 1.0),
                 "accent": (92, 0.95), "hard_accent": (108, 0.95),
                 "staccato": (75, 0.25), "glassy": (85, 0.9),
                 "tremolo": (60, 1.0), "muted": (38, 0.20),
                 "comping_chop": (78, 0.50)}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9982, "width": 0.8,
                    "role": "electric_grand", "lowpass_hz": 5500,
                    "noise_component": 0.02}
MODAL_PRESET = "string"
ELECTRIC_GRAND_MODES = [(440.0, 1.00, 0.9), (880.0, 0.60, 1.2),
                        (1320.0, 0.35, 1.5), (1760.0, 0.18, 1.8),
                        (2200.0, 0.09, 2.2)]
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 2.0,
               "mod_depth": 2.0, "attack": 0.003, "release": 1.2}
REVERB_TAIL = 2.2
EQ_BODY = (300, -2.0)
EQ_PRESENCE = (3500, 2.5)
EQ_AIR = (8500, 1.5)
PAN = 0.0
midi_to_freq(midi) -> 440.0 * 2 ** ((midi - 69) / 12)
```

## 6. Registration (REGISTRY DISCIPLINE)

`instrument_registry.py` updated:
1. `_INSTRUMENT_MODULES` += `"Keys.electric_grand.electric_grand": "electric_grand"`
2. `_FIELDS` += `electric_grand_modes` (custom modal bank loads through the registry)
3. Convenience constant `ELECTRIC_GRAND = ALL_INSTRUMENTS["electric_grand"]`
4. `registry_table()` role row for "electric grand piano"
5. `__main__` verification block

Registry verification run (`/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`):

```
| Keys | Electric Grand Piano | 2 | 21–108 | harmony, melody, bass, rhythm, accent, color |

=== Electric Grand Piano (Yamaha CP-70/CP-80, GM2) ===
  ELECTRIC_GRAND.midi_program = 2 (should be 2)
  by_name('electric grand piano') = <Instrument Electric Grand Piano (family=Keys, program=2, range=21-108)>
  by_name('Electric Grand Piano') = <Instrument Electric Grand Piano (family=Keys, program=2, range=21-108)>
  by_program(2) = <Instrument Electric Grand Piano (family=Keys, program=2, range=21-108)>
  by_program(1) = <Instrument Acoustic Grand Piano (family=Keys, program=1, range=21-108)> (distinct: acoustic grand)
  ELECTRIC_GRAND.in_sweet_spot(72) = True
  ELECTRIC_GRAND.in_sweet_spot(30) = False
  ELECTRIC_GRAND.range_min = 21 ELECTRIC_GRAND.range_max = 108
  ELECTRIC_GRAND.solo_range = (48, 84)
  ELECTRIC_GRAND.stem_label = 'Electric_Grand_Piano'
  ELECTRIC_GRAND.synthesis = 'karplus'
  ELECTRIC_GRAND.karplus_defaults = {'loop_gain': 0.9982, 'width': 0.8, 'role': 'electric_grand', 'lowpass_hz': 5500, 'noise_component': 0.02}
  ELECTRIC_GRAND.reverb_tail = 2.2 ELECTRIC_GRAND.pan = 0.0
```

The composition job (`daily-algorithmic-composition-production`) can now pick
this instrument via `by_name('electric grand piano')` / `by_program(2)` /
`ELECTRIC_GRAND`.

## 7. Verification results (engine test — `_test/verify_electric_grand.py`)

| Check | Result |
|---|---|
| Registration (through registry) | `by_name('electric grand piano')` / `by_name('Electric Grand Piano')` / `by_program(2)` → Electric Grand Piano; `ELECTRIC_GRAND is ALL_INSTRUMENTS['electric_grand']` = True |
| Composition | UnitMatrixComposer, 1 bar × 1 section, 104 bpm, Electric Grand SOLO on ch0 (glassy C5–E5–G5–C6 hook + low C2 pedal, octave+ below) + drum-kit context ch9 |
| Zero-drift | **True (OK)** |
| MIDI | `electric_grand_test.mid` — **204 bytes** (> 40 ✓) |
| WAV (SOLO render, FluidR3 via `discover_soundfont()`) | `electric_grand_test.wav` — **982,060 bytes** (> 40 ✓) |
| Spectral gate (4–8 kHz buzz) | **2.0%** (OK, ≤ 20% — clean single voice, no comb-filtering) |
| Pipeline stem labels | `GM_PROGRAMS[2]` = "Electric Grand Piano" (exact match); STEM_LABEL `Electric_Grand_Piano` matches the pipeline's real label |
| RenderPipeline stems on disk | `track00_Electric_Grand_Piano.wav` (982,060 B) + `track01_Drums.wav` (835,628 B) — both > 40 B ✓ |
| Karplus-Strong smoke | C5 loop_gain 0.9982: late(1.5–2.0 s) rms 0.0005 vs 0.990 dull control 0.0001 → **4.2× ring** (long soundboard-less string) |
| ResonatorBank smoke | custom `ELECTRIC_GRAND_MODES` impulse: peak 0.900, late(1.5–2.0 s) rms/peak **0.100** (long ring, no collapse) |
| PhaseModSynth smoke | C5 with FM_DEFAULTS: peak 0.798 (audible) |

## 8. Quirks found

1. **SF2 spelling quirk (cosmetic, no routing impact)**: FluidR3 preset 2 is
   named **"Electric Piano"** (the generic GM electric-piano family name),
   NOT "Electric Grand Piano". The pipeline names stems from
   `GM_PROGRAMS[2] = "Electric Grand Piano"`, so the stem file is
   `trackXX_Electric_Grand_Piano.wav` — STEM_LABEL matches the pipeline's
   real label so stem-file lookups work.
2. **No stem-label quirk**: the sanitizer only rewrites spaces/parens/slashes
   — "Electric Grand Piano" → `Electric_Grand_Piano` (no hyphen, no parens).
3. **No pitch quirk**: the patch is a normal chromatic keyboard (contrast
   GM115 woodblock / GM117 melodic tom — GM2 really transposes).
4. **Legacy note**: `piano.py` uses program 1 which the pipeline labels
   "Bright Acoustic Piano" (known legacy off-by-one, documented 2026-08-27);
   this entry uses the modern 0-indexed program 2 which matches the pipeline
   AND FluidR3 exactly.
5. **No unison doubling**: the records double the CP with an acoustic grand
   or strings (octaves / different octave), NEVER a second melodic patch on
   the same pitches (2026-09-01 comb-filter rule).
6. **Engine API note**: the custom modal bank uses `ResonatorBank`
   (`add_mode`/`excite_impulse`), NOT `ModalSynth.render_preset` — the preset
   class only exposes the stock banks. Decay is a rate
   (`y(t) = A·exp(−decay·t)`): 0.9–2.2 = slow = long ring (timpani
   convention; marimba's 8–20 is the fast end).

## 9. Remaining sibling candidates (unclaimed programs)

GM112 Tinkle Bell, GM118 Synth Drum, GM50/51 Synth Strings 1/2, GM63 Synth
Brass 2, GM37 Slap Bass 2, GM53 Voice Oohs, GM90–95 Pad 3–8, GM96–103 FX,
GM119–127 sound effects, GM2 now CLAIMED by this entry.
