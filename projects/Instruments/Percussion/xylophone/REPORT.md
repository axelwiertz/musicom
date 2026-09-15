# Xylophone — Verification Report (2026-09-15)

## Instrument

- **Name**: Xylophone (orchestral concert xylophone — rosewood bars,
  resonator tubes, hard polyball/rattan mallets)
- **Family**: Percussion (sixth entry: drum_kit, marimba, steel_drums,
  timpani, vibraphone, xylophone)
- **GM program**: 13 (0-indexed; pipeline `GM_PROGRAMS[13]`, FluidR3 preset
  13)
- **Identity**: the bright dry ancestor of the marimba — 1 octave higher,
  arch-cut rosewood bars, very short ring. NOT the toy glockenspiel
  (steel bars, GM9).

## Registration (registry discipline)

- Added to `instrument_registry.py`:
  - `_INSTRUMENT_MODULES`: `"Percussion.xylophone.xylophone": "xylophone"`
  - Constant: `XYLOPHONE = ALL_INSTRUMENTS["xylophone"]`
  - `registry_table()` role branch: `lead, melody, ornament, accent, countermelody`
  - `__main__` verification lines added
  - `_FIELDS` extended with `xylophone_modes` (like `motor_defaults` for
    vibraphone) so the custom modal bank loads through the registry
- Registry verification run (`/opt/data/micromamba/envs/musicom/bin/python
  instrument_registry.py` from `/opt/data/projects/Instruments`) — new row
  and checks:

```
| Percussion | Xylophone | 13 | 53–89 | lead, melody, ornament, accent, countermelody |
...
  XYLOPHONE.midi_program = 13 (should be 13)
  by_name('xylophone') = <Instrument Xylophone (family=Percussion, program=13, range=53-89)>
  by_program(13) = <Instrument Xylophone (family=Percussion, program=13, range=53-89)>
  XYLOPHONE.in_sweet_spot(72) = True
```

- `ALL_INSTRUMENTS` count after registration: 40

## Constants (all in `xylophone.py`)

| Constant | Value |
|---|---|
| `MIDI_PROGRAM` | 13 |
| `GM_NAME` | "Xylophone" |
| `STEM_LABEL` | "Xylophone" (pipeline GM_PROGRAMS[13] matches exactly) |
| `RANGE_MIN / RANGE_MAX` | 53–89 (F3–F6, standard 4-octave concert xylophone) |
| `SOLO_RANGE` | (60, 84) — C4–C6 |
| `SWEET_SPOT` | (67, 86) — G4–D6, brightest cut; arch partials inside SF2 span |
| `ZONES` | low 53–64 (woody knock), mid 65–76 (melody), high 77–89 (brittle clatter) |
| `ARTICULATIONS` | single_stroke (82, 0.5), roll (64, 2.0), double_stop (74, 0.8), glissando (70, 0.25), wood_block (90, 0.2) |
| `SYNTHESIS` | "modal" |
| `XYLOPHONE_MODES` | (440, 1.0, 9.0), (1320, 0.42, 14.0), (2640, 0.20, 20.0) — arch ratios 1 : 3 : 6 |
| `MODAL_PRESET` | "marimba" (closest stock bank — WRONG partials + too slow, custom bank is the real voice) |
| `KARPLUS_DEFAULTS` | loop_gain 0.9935, width 0.30, role lead (demoted fallback) |
| `FM_DEFAULTS` | sine carrier, ratio 7.0, depth 1.2, attack 0.001, release 0.25 |
| `REVERB_TAIL` | 0.9 s — driest melodic instrument in the KB |
| `EQ_BODY` | (200, -1.5) light clean-up |
| `EQ_PRESENCE` | (2500, +2.5) polyball attack + 12th partial |
| `EQ_AIR` | (9000, +1.5) brittle clatter air |
| `PAN` | 0.0 (single-row bars, narrow spread) |

## Synthesis engine

- **Primary: ModalSynth** (`sound/synthesis/modal.py`) with custom
  `XYLOPHONE_MODES` — rosewood arch tuning **1 : 3 : 6** (fundamental,
  octave+fifth 12th, compressed near-3-octave 17th). The octave partial is
  DISCARDED by the arch cut — unlike the marimba's harmonic 1:2:3 stack.
  Decay rates 9/14/20 (rosewood-dry).
- **Fallback: Karplus-Strong** (SP-011), loop_gain 0.9935 — bar is struck,
  not plucked, so KS is the wrong excitation family (demoted, as for
  vibraphone/timpani).
- **Alt patch: PhaseModSynth** — sine carrier, ratio 7.0, depth 1.2.

## Verification results (`_test/verify_xylophone.py` — ALL CHECKS PASSED)

- **Registry-backed import**: `by_name('xylophone')` + `by_program(13)` →
  `<Instrument Xylophone (family=Percussion, program=13, range=53-89)>`; row
  present in `registry_table()`.
- **Zero-drift**: `validate()` → `True (OK)` — 1 bar, 2 voices (Xylophone
  solo ch0 + ONE low bass G2 ch1 an octave+ below; no melodic doubling),
  terminal landmark at BAR.
- **MIDI export**: `_test/xylophone_test.mid` — 144 bytes (> 40 ✓).
- **WAV (solo render via `discover_soundfont()` → FluidR3_GM.sf2)**:
  `_test/xylophone_test.wav` — 864,044 bytes (> 40 ✓).
- **Spectral gate (solo WAV)**: 4–8 kHz buzz = **0.4%** — OK, no
  comb-filtering (bright clatter, clean).
- **Stem label**: pipeline `GM_PROGRAMS[13] = 'Xylophone'` →
  `trackXX_Xylophone.wav` — matches `STEM_LABEL` exactly, **no quirk**
  (stems dir `_test/stems_xylophone`: `track00_Xylophone.wav` 864,044 B +
  `track01_Electric_Bass_finger.wav` 741,676 B).
- **SF2 preset**: FluidR3_GM.sf2 phdr → preset 13 = "Xylophone" (exact
  match).
- **ModalSynth XYLOPHONE_MODES**: late(1.0–1.5 s) rms/peak = **0.0000** vs
  marimba stock preset 0.0001 — the bar is DRY (first KB instrument whose
  custom modal bank measures BELOW the marimba preset; dryness is the
  identity, not ring advantage). Decay confirmed: rms(0.1–0.2 s) 0.1513 →
  rms(0.3–0.4 s) 0.0245 (ratio 0.162). Fundamental dominance: 3× partial
  27.3% and 6× partial 9.1% of f0 (f0 > 3× > 6×).
- **Karplus-Strong fallback**: tail_rms/peak(0.2–0.5 s) = 0.0145 vs 0.0093
  dull control (loop_gain 0.990) = **1.56×** ring advantage (threshold 1.5×
  per the kalimba short-ring precedent). Ordering check: xylophone 0.0145 <
  kalimba 0.0155 < banjo 0.0202 — xylophone is the SHORTEST ring of the
  struck/plucked set.
- **Empirical FluidR3 pitch sweep** (RMS, notes 53–89, 0.6 s window,
  threshold 0.005): **10/10 audible, no gaps** — 53: 0.0410, 57: 0.0368,
  60: 0.0352, 65: 0.0303, 69: 0.0284, 72: 0.0286, 77: 0.0231, 81: 0.0231,
  84: 0.0259, 89: 0.0215. SF2 never clips a composition inside the
  documented range.

## Quirks / lessons

- **No stem-label quirk** — GM_PROGRAMS[13] and FluidR3 preset 13 are both
  exactly "Xylophone" (contrast: "Bag_pipe", "Shanai" quirks).
- **Melodic channel required** (0–9, program 13): channel 9 would trigger
  the drum-kit map + `Acoustic_Grand_Piano` program-0 fallback label
  (timpani lesson, inherited).
- **Dryness measurement**: short-ring instruments must be verified in an
  early window — xylophone modal ring vanishes by 1.0 s; the KS ring check
  uses the 0.2–0.5 s window (kalimba precedent, threshold 1.5× not 3×).
- **Registry `_FIELDS`**: any new custom-bank constant (here
  `XYLOPHONE_MODES`) must also be added to `instrument_registry._FIELDS` or
  it silently reads as `None` through `by_name()`.
- **Identify carefully**: GM13 = orchestral xylophone (wood bars, F3–F6);
  GM9 = glockenspiel (steel bars, transposing up 2 octaves) — different
  instruments, different ranges, different partial structures.

## Files

- `Percussion/xylophone/instrument.md` — full research reference
- `Percussion/xylophone/xylophone.py` — importable constants
- `instrument_registry.py` — registered (`Percussion.xylophone.xylophone` →
  key `xylophone`, constant `XYLOPHONE`)
- `registry.md` — changelog entry + Registry table row + stem-quirk row
- `_test/verify_xylophone.py` — verification script (registry import,
  composer, solo WAV, modal/KS checks, pitch sweep)
- `_test/xylophone_test.mid` / `_test/xylophone_test.wav` / `_test/stems_xylophone/`
