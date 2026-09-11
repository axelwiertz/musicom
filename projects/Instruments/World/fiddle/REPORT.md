# REPORT — Fiddle (GM110) — 2026-09-11

## Instrument

**Fiddle** (folk fiddle) — new **World** family entry (seventh in World),
GM2 program 110 "Fiddle". The folk double of the classical violin: same
GDAE tuning and body dimensions, different idiom — flat/narrow vibrato,
aggressive bow drive, heavy rosin noise at every bow change. Used in
Anglo-American (old-time, bluegrass), Celtic (Irish/Scottish) and Nordic
traditions as the lead tune voice.

## MIDI / GM

- Program: **110** (GM2 "Fiddle"; 0-indexed — the 111th entry of the GM1
  list). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) —
  raw `program=110` in `add_voice`.
- Pipeline stem label: `GM_PROGRAMS[110]` = `"Fiddle"` → `trackXX_Fiddle.wav`.
  **No quirk** — pipeline label, instrument name, and FluidR3 preset name
  all "Fiddle" (distinct from the "Shanai" spelling quirk at 111).
- FluidR3 preset 110 = `"Fiddle"` (phdr-verified via `discover_soundfont()`
  → `/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2`).

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full range | 55–96 | G3–C6 (GM-patch span — empirical FluidR3 sweep 8/8 audible, no gaps) |
| Sweet spot | 62–86 | D4–D6 — melodic core: GDAE first position + quick shifts |
| Solo | 60–89 | C4–A6 — folk tune register (tunes C4–E6, high ornaments to A6) |
| Low | 55–61 | G3–B3 — dark open-G register; drones, double stops |
| High | 78–96 | F#5–C6 — bright, singing, cutting; ornaments |

## Role

Lead melody (mid zone), ornament (grace/cut notes, rolls, drones), idiom
double-stops against open strings, countermelody/call-response, accent.
NOT harmony (line voice), NOT bass, NOT background pad.

## Synthesis engine

**BowedString** (`sound/synthesis/bowed.py`, SP-024) — friction waveguide,
the correct physical model (Helmholtz stick-slip). Fiddle idiom pushes
harder than concert violin: `bow_velocity` 0.24 (vs 0.2 violin), `bow_force`
1.8, `bow_position` 0.15, `noise_level` 0.025 (rosin scratch). Smoke test:
peak 1.000, late-window (0.5–0.7 s) RMS/peak = **0.572** → sustained bow,
no collapse. ModalSynth `'string'` preset = pizzicato/pluck fallback;
PhaseModSynth saw carrier = cheap alt.

## Constants (World/fiddle/fiddle.py)

- `MIDI_PROGRAM = 110`, `GM_NAME = "Fiddle"`, `STEM_LABEL = "Fiddle"`
- `RANGE_MIN = 55`, `RANGE_MAX = 96`, `SOLO_RANGE = (60, 89)`,
  `SWEET_SPOT = (62, 86)`
- `ZONES`: low (55,61) / mid tune (62,77) / high (78,96)
- `ARTICULATIONS`: sustain (80,1.0) drive (84,0.9) staccato (68,0.25)
  spiccato (74,0.125) tremolo (70,0.06) pizzicato (58,0.2) accent (92,0.9)
  grace (66,0.05)
- `SYNTHESIS = "bowed"`, `BOWED_DEFAULTS` above, `MODAL_PRESET = "string"`
- `REVERB_TAIL = 1.6`, `EQ_BODY = (400,-2.0)`, `EQ_PRESENCE = (2800,2.5)`,
  `EQ_AIR = (7500,1.5)`, `PAN = 0.0`
- `midi_to_freq()` standard A440

## Registration proof

`instrument_registry.py` updated: `"World.fiddle.fiddle": "fiddle"` in
`_INSTRUMENT_MODULES`, `FIDDLE = ALL_INSTRUMENTS["fiddle"]` constant,
role mapping added, and `_FIELDS` extended with `bowed_defaults` (so the
bowed-engine preset loads through the registry). `python instrument_registry.py`
output includes:

```
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
```

(verify script also asserts `"| World | Fiddle | 110 |"` in
`registry_table()`; ALL_INSTRUMENTS count = **28**.)

## Verification results

- Zero-drift: **True (OK)** — UnitMatrixComposer, 1 bar, 1 section, 2 voices
  (Fiddle solo ch0 + low bass D2 ch1 — no unison doubling)
- MIDI: `_test/fiddle_test.mid` — **144 bytes** (> 40 ✓)
- WAV (solo, FluidR3 via `discover_soundfont()`): `_test/fiddle_test.wav` —
  **756,012 bytes** (> 40 ✓)
- Spectral check: 4–8 kHz buzz energy = **2.9%** (OK, ≤ 20% gate — no
  comb-filtering; solo render only)
- Stems: `track00_Fiddle.wav` (756,012 B) + `track01_Electric_Bass_finger.wav`
  — pipeline label `GM_PROGRAMS[110] = 'Fiddle'` asserted
- SF2 preset 110 = `'Fiddle'` (phdr-verified, `discover_soundfont()` →
  FluidR3_GM.sf2)
- Empirical sweep (55/62/66/69/76/84/90/96): **8/8 audible**, RMS 0.076–0.116
  — SF2 never clips a composition

## Quirks found

1. **No stem-label quirk**: GM_PROGRAMS[110] = "Fiddle" = GM_NAME = SF2
   preset = STEM_LABEL. Cleanest of the World entries — contrast with
   109 ("Bag pipe" → `Bag_pipe`) and 111 ("Shanai" GM spelling).
2. **Violin vs Fiddle distinction**: GM110 is a *separate* patch from GM40
   Violin (FluidR3 has both). Do not subsume fiddle under violin constants —
   the bowing idiom (drive, rosin, flat vibrato) differs.
3. **Line voice**: fiddle is monophonic; the only harmony trick is an
   open-string drone double-stop. No dense chords.

## Files

- `World/fiddle/instrument.md`
- `World/fiddle/fiddle.py`
- `_test/verify_fiddle.py` (ALL CHECKS PASSED)
- `_test/sweep_fiddle.py` (ALL AUDIBLE)
- `instrument_registry.py` (registered), `registry.md` (updated)