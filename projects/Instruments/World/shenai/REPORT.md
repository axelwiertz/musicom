# REPORT — Shenai (GM111) — 2026-09-10

## Instrument

**Shenai** (North Indian shehnai) — new **World** family entry, GM2 program
111 "Shanai". Continuous-tone double-reed melody instrument: raga line over a
tanpura-style Sa-Pa drone, circular breathing, kan/meend/gamak ornaments.

## MIDI / GM

- Program: **111** (GM2 "Shanai"; 0-indexed — the 112th entry of the GM1
  list). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) —
  raw `program=111` in `add_voice`.
- Spelling quirk: GM2 spec = **"Shanai"**; instrument name = **Shenai**;
  FluidR3 preset 111 = **"Shenai"** (phdr-verified).
- Pipeline stem label: `GM_PROGRAMS[111]` = `"Shanai"` → `trackXX_Shanai.wav`.
  **QUIRK**: pipeline label ("Shanai") ≠ instrument name ("Shenai") ≠ SF2
  preset ("Shenai"). STEM_LABEL = `"Shanai"` (actual pipeline label) so
  stem-file lookups work.

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full range | 55–96 | G3–C7 (GM-patch span — empirical FluidR3 sweep 8/8 audible, no gaps) |
| Sweet spot | 64–79 | E4–G5 — solo core, fullest reed presence |
| Solo (real) | 62–84 | D4–C6 — physical shehnai register (~2 octaves) |
| Low | 55–61 | G3–B3 — dark, breathy, less carrying |
| High | 85–96 | C#6–C7 — GM extension above physical instrument, thin/whistle-y |

## Role

Lead melody, ornament (kan/meend/gamak), drone partner, ceremonial accent.
NOT harmony (monophonic), NOT background, NOT bass.

## Synthesis engine

**PhaseModSynth** (`sound/synthesis/phase_mod.py`) — saw carrier,
`mod_freq_ratio 1.5`, `mod_depth 3.2` (between oboe 2.5 and bagpipe 4.5),
`attack 0.06` (real reed transient — sharper than bagpipe's pre-blown 0.03).
ModalSynth `'string'` preset = crude continuous-tone fallback. Smoke test:
peak 0.788, late-window (0.5–0.7 s) RMS/peak = **0.400** → sustained reed,
no collapse.

## Constants (World/shenai/shenai.py)

- `MIDI_PROGRAM = 111`, `GM_NAME = "Shenai"`, `STEM_LABEL = "Shanai"`
- `RANGE_MIN = 55`, `RANGE_MAX = 96`, `SOLO_RANGE = (62, 84)`,
  `SWEET_SPOT = (64, 79)`
- `ZONES`: low (55,61) / solo (62,84) / high (85,96)
- `ARTICULATIONS`: sustain (76,1.0) kan (90,0.12) meend (72,1.6) gamak
  (86,0.3) cut (80,0.5) accent (92,1.0)
- `SYNTHESIS = "phase_mod"`, `FM_DEFAULTS` above, `MODAL_PRESET = "string"`
- `REVERB_TAIL = 2.0`, `EQ_BODY = (450,-3.0)`, `EQ_PRESENCE = (2600,3.0)`,
  `EQ_AIR = (7000,1.5)`, `PAN = 0.0`
- `midi_to_freq()` standard A440

## Registration proof

`instrument_registry.py` updated: `"World.shenai.shenai": "shenai"` in
`_INSTRUMENT_MODULES`, `SHENAI = ALL_INSTRUMENTS["shenai"]` constant, role
mapping added. `python instrument_registry.py` output includes:

```
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
```

(verify script also asserts `"| World | Shenai | 111 |"` in
`registry_table()`; ALL_INSTRUMENTS count = 27.)

## Verification results

- Zero-drift: **True (OK)** — UnitMatrixComposer, 1 bar, 1 section, 2 voices
  (Shenai solo ch0 + low A1 drone ch1 — no unison doubling)
- MIDI: `_test/shenai_test.mid` — **144 bytes** (> 40 ✓)
- WAV (solo, FluidR3 via `discover_soundfont()`): `_test/shenai_test.wav` —
  **748,076 bytes** (> 40 ✓)
- Spectral check: 4–8 kHz buzz energy = **1.3%** (OK, ≤ 20% gate — no
  comb-filtering; solo render only)
- Stems: `track00_Shanai.wav` (748,076 B) + `track01_Electric_Bass_finger.wav`
  — pipeline label `GM_PROGRAMS[111] = 'Shanai'` asserted
- SF2 preset 111 = `'Shenai'` (phdr-verified, `discover_soundfont()` →
  FluidR3_GM.sf2)
- Empirical sweep (55/62/66/69/76/84/90/96): **8/8 audible**, RMS 0.037–0.085
  — SF2 never clips a composition

## Quirks found

1. **"Shanai" vs "Shenai"**: GM2 spec says "Shanai"; the instrument is the
   shehnai/shenai. Pipeline stem = `Shanai`; SF2 preset = `Shenai`; GM_NAME =
   `Shenai`. STEM_LABEL matches the pipeline (`Shanai`). This is the second
   pipeline-label ≠ instrument-name quirk (after Bagpipe "Bag_pipe").
2. **Continuous tone**: like bagpipe, shehnai line never stops — tune = note
   changes. Composition jobs write contiguous sustained melody over a drone,
   never dense harmony.
3. **High register (85–96)**: physical instrument tops out at C6 (84); the
   patch plays above but reads "whistle", not "shehnai".

## Files

- `World/shenai/instrument.md`
- `World/shenai/shenai.py`
- `_test/verify_shenai.py` (ALL CHECKS PASSED)
- `_test/sweep_shenai.py` (ALL AUDIBLE)
- `instrument_registry.py` (registered), `registry.md` (updated)
