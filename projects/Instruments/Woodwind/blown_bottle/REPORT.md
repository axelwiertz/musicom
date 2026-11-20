# REPORT — Blown Bottle (GM76) added to Instruments KB

**Date**: 2026-11-20 (nightly instrument research job)
**Instrument**: Blown Bottle — `Woodwind/blown_bottle/`
**Files**: `instrument.md`, `blown_bottle.py`, registered in
`instrument_registry.py` (key `blown_bottle`, constant `BLOWN_BOTTLE`),
changelog + registry table updated in `registry.md`.

---

## 1. Instrument identity

GM76 "Blown Bottle" = the sound of blowing across the mouth of an empty
bottle — a **Helmholtz-resonator aerophone**: an air jet across the neck
excites the cavity resonance (frequency set by cavity volume + neck geometry;
a typical soda bottle ≈ 100–300 Hz = G2–E4; bigger bottles lower, small
bottles higher). A single physical bottle is ONE pitch — the GM patch
transposes chromatically. The same physics family as the ocarina (vessel
flute) but a WIDE mouth = far more breath turbulence and a slower, swelly
onset.

Placed in **Woodwind** (it is in the GM woodwind flute/whistle block 73–80;
closest KB cousins Whistle GM78 and Ocarina GM79 are also Woodwind).
**Completes the 73–80 block**: Flute, Recorder, Pan Flute, **Blown Bottle**,
Shakuhachi, Whistle, Ocarina — ALL present in the KB now.

## 2. Program / GM / channel

| Field | Value |
|---|---|
| MIDI program | **76** (raw GM number — NOT in `structures/instrument.py` `MidiInstrument` enum, which only exposes 10; use `program=76` in `add_voice`) |
| GM name | "Blown Bottle" |
| Channel | melodic (0–9) — blown aerophone, NOT channel 9 |
| Stem label | `trackXX_Blown_Bottle.wav` — pipeline `GM_PROGRAMS[76]` = "Blown Bottle", matches exactly, **no stem quirk** |
| SF2 preset | FluidR3 preset 76 = **"Bottle Chiff"** — **spelling quirk** (see §7) |

## 3. Range (empirically measured)

Empirical FluidR3 pitch sweep (RMS, notes 24–108 step 6): **audible across
the whole span, no gaps, level flat within 7.9 dB** (min 0.072 @24, max 0.179
@30). Chromatic pitch tracking confirmed: band-limited peak (search ±10% of
expected f0) at 0.90–1.10× f0 for EVERY note 24–108 — GM76 really transposes
(unlike GM115 woodblock / GM117 melodic-tom, which barely pitch-track).

| Zone | MIDI | Pitches | Notes |
|---|---|---|---|
| Full writing range | 48–96 | C3–C7 | patch plays 24–108; trimmed for TONE not audibility |
| Sweet spot | 65–79 | G4–G5 | cleanest Helmholtz tone, moderate breath |
| Solo range | 60–84 | C4–C6 | attack ≤ ~1 s, cleanest pitch identity |
| Low | 48–59 | C3–B3 | blow-in swell 0.5–2.2 s, sub-octave layer heavy — roots/drone colour only |
| Mid | 60–71 | C4–B4 | primary melody zone |
| High | 72–96 | C5–C7 | fast attack (40–500 ms), breathy; 84+ noisy (4–8 kHz ~16%) |

## 4. Role

`lead, melody, ornament, accent, texture` — novelty/folk/psychedelic colour
lines, "nature" melody voice; ornament (puffs, swells, breath ghosts,
flutter); color/texture (long swelling single notes, breath beds, "wind in a
bottle" ambience); countermelody under/above whistle/ocarina/recorder.
NOT harmony/pad (monophonic breath line — no dense chords), NOT bass (low
register is sub-octave rumble with >1 s swell), NOT rhythmic (slow attack
smears fast gestures — re-articulate puffs).

## 5. Synthesis engine

**`phase_mod` (PhaseModSynth) primary** — Helmholtz-resonator aerophone:
sine carrier + sine modulator, `mod_freq_ratio` 1.0, `mod_depth` **0.7**
(shallowest of the flute set — ocarina 0.8, whistle 1.5, shakuhachi 2.0 —
reflecting the near-sinusoidal cavity tone), `attack` **0.12 s** (slowest of
the set — the blow-in swell), `release` 0.20 s (breath tail).
**Additive fallback**: 4 partials, weights 0.9/0.25/0.1/0.04 (cavity
suppresses harmonics), attack 0.12 / release 0.20.
**ModalSynth ALT**: struck-resonator for short "bloop" puffs only (bottle is
BLOWN, not struck). **Karplus-Strong REJECTED** — no string; a KS loop's
harmonic series is the wrong partial structure for a Helmholtz cavity.

PhaseModSynth smoke test (FM_DEFAULTS, C5 = 523.25 Hz, 1.5 s, 22050 Hz):
peak = **0.799**, late_rms/peak = **0.354** (sustain holds — no collapse),
2nd/1st partial = **0.46** (near-sine Helmholtz tone confirmed).

## 6. Constants (blown_bottle.py)

```python
MIDI_PROGRAM = 76
GM_NAME = "Blown Bottle"
STEM_LABEL = "Blown_Bottle"
RANGE_MIN = 48          # C3 — below: swell >2 s + sub-octave dominates
RANGE_MAX = 96          # C7 — above: breathy/noisy (4-8 kHz ~16%)
SOLO_RANGE = (60, 84)   # C4–C6
SWEET_SPOT = (65, 79)   # G4–G5
ZONES = {"low": (48, 59), "mid": (60, 71), "high": (72, 96)}
ARTICULATIONS = {
    "blow": (78, 1.0), "swell": (85, 1.0), "puff": (64, 0.25),
    "breath": (50, 0.9), "accent": (95, 0.8), "ghost": (36, 0.15),
    "flutter": (70, 0.5),
}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {"carrier_shape": "sine", "mod_shape": "sine",
               "mod_freq_ratio": 1.0, "mod_depth": 0.7,
               "attack": 0.12, "release": 0.20}
ADDITIVE_DEFAULTS = {"harmonic_count": 4,
                     "harmonic_weights": [0.9, 0.25, 0.1, 0.04],
                     "attack": 0.12, "release": 0.20}
REVERB_TAIL = 1.8
EQ_BODY = (350, -2.5)
EQ_PRESENCE = (2500, 2.0)
EQ_AIR = (7000, 1.5)
PAN = 0.0

def midi_to_freq(midi): return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## 7. Quirks found (measured, FluidR3)

1. **SF2 spelling quirk**: FluidR3 preset 76 is named **"Bottle Chiff"** in
   the phdr chunk, NOT "Blown Bottle" (the sample's chiff/breath character).
   Cosmetic only — no routing impact; the stem label comes from the pipeline's
   GM_PROGRAMS[76] = "Blown Bottle" → `trackXX_Blown_Bottle.wav`. Documented
   in instrument.md + verify script assertion.
2. **Two-stage attack IS the identity**: initial breath onset ~80–120 ms, but
   the full swell is register-dependent — 40 ms (C6+) / ~500 ms (C5) /
   0.5–2.2 s (C3–B4). Low notes are slow swells: write them ≥ 1–2 s or they
   never speak.
3. **Weak sustain + ~1 Hz "breathing" wobble**: envelope swells to ~0.2 peak,
   dips, re-swells at ~0.5 s, decays, with a slow amplitude wobble
   (sample-loop behaviour). Not a flat flute sustain — re-articulate long
   pads every 2–4 bars.
4. **Velocity → amplitude only**: spectral centroid flat 1593–1656 Hz across
   vel 20–120; peak near-linear 0.017 → 0.592. Accents need real velocity.
5. **Sub-octave layer on low notes**: at 48–60 the dominant spectral
   component is an octave BELOW the written note (e.g. C3 → peak at C2).
   Pitch identity remains unambiguous (band-limited check passes everywhere),
   but low lines sound dark/deep — keep melody ≥ C4.
6. No stem quirk (label "Blown Bottle" matches GM name exactly — unlike
   GM74→"Recorder", GM109→"Bag_pipe", GM111→"Shanai").

## 8. Registration proof

Registry verification run (`/opt/data/micromamba/envs/musicom/bin/python
instrument_registry.py`, exit 0) — new row in `registry_table()`:

```
| Woodwind | Blown Bottle | 76 | 48–96 | lead, melody, ornament, accent, texture |
```

Verification block:

```
=== Blown Bottle (Woodwind, GM76) ===
  BLOWN_BOTTLE.midi_program = 76 (should be 76)
  by_name('blown bottle') = <Instrument Blown Bottle (family=Woodwind, program=76, range=48-96)>
  by_name('Blown Bottle') = <Instrument Blown Bottle (family=Woodwind, program=76, range=48-96)>
  by_program(76) = <Instrument Blown Bottle (family=Woodwind, program=76, range=48-96)>
  by_program(75) = <Instrument Pan Flute (family=World, program=75, range=55-100)> (distinct: pan flute)
  BLOWN_BOTTLE.in_sweet_spot(72) = True
  BLOWN_BOTTLE.in_sweet_spot(36) = False
  BLOWN_BOTTLE.range_min = 48 BLOWN_BOTTLE.range_max = 96
  BLOWN_BOTTLE.solo_range = (60, 84)
  BLOWN_BOTTLE.stem_label = 'Blown_Bottle'
  BLOWN_BOTTLE.synthesis = 'phase_mod'
  BLOWN_BOTTLE.reverb_tail = 1.8 BLOWN_BOTTLE.pan = 0.0
```

## 9. End-to-end verification results (`_test/verify_blown_bottle.py`)

Composition: 1 bar / 1 section UnitMatrixComposer (104 bpm), voice 1 = Blown
Bottle SOLO (G4–D5 sweet-spot line with swells/puffs/accents/ghost), voice 2 =
drums context on channel 9 (kick + hat) — NO second melodic patch on the same
pitches (2026-09-01 comb-filter rule).

| Check | Result |
|---|---|
| Registry import | `by_name('blown bottle')` / `by_name('Blown Bottle')` / `by_program(76)` → Blown Bottle ✓; `BLOWN_BOTTLE is ALL_INSTRUMENTS['blown_bottle']` = True ✓ |
| Zero-drift | **True (OK)** — terminal landmark flush at BAR ✓ |
| MIDI | `_test/blown_bottle_test.mid` — **195 bytes** (> 40 ✓) |
| WAV (SOLO render) | `_test/blown_bottle_test.wav` — **866,604 bytes** (> 40 ✓) |
| Spectral check | 4–8 kHz buzz energy = **5.2%** (OK, ≤ 20% gate) |
| Stem labels | pipeline `GM_PROGRAMS[74..78]` = Recorder / Pan Flute / **Blown Bottle** / Shakuhachi / Whistle; `[76]` == "Blown Bottle" ✓ |
| SF2 phdr | preset 76 = **"Bottle Chiff"** (quirk documented, assertion matches actual) |
| Stems on disk | `track00_Blown_Bottle.wav` (866,604 B) + `track01_Drums.wav` (835,628 B) ✓ |
| PhaseModSynth | FM_DEFAULTS C5 render: peak 0.799, late/peak 0.354 (> 0.1, sustain holds), 2nd/1st = 0.46 (< 0.5, near-sine) ✓ |

`_test/verify_blown_bottle_out.txt` contains the full pass log.
Probe scripts: `_test/_probe_blown_bottle.py` (24–108 sweep), `_test/_probe_blown_bottle2.py`
(envelope/spectrum/velocity).

## 10. Registry.md updates

- Registry table: added `| Woodwind | Blown Bottle | 76 | 48–96 | lead,
  melody, ornament, accent, texture |` (after Bassoon).
- Changelog: dated 2026-11-20 entry with full identity/range/synthesis/quirks
  (including the "Bottle Chiff" spelling quirk).
- Remaining sibling candidates noted: GM112 Tinkle Bell, GM118 Synth Drum,
  GM50/51 Synth Strings 1/2, GM63 Synth Brass 2, GM37 Slap Bass 2, GM2
  Electric Grand Piano.
