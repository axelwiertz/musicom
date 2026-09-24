# Harmonica — Nightly Instrument Research Report (2026-09-24)

## Instrument

| Field | Value |
|---|---|
| **Instrument** | Harmonica |
| **Family** | Woodwind |
| **GM Program** | 22 |
| **GM Name** | "Harmonica" |
| **Stem Label** | "Harmonica" (no quirk — GM_PROGRAMS[22] = "Harmonica") |
| **FluidR3 Preset** | "Harmonica" (exact match) |
| **Range** | 48–96 (C3–C7) |
| **Sweet Spot** | 64–79 (E4–G6) |
| **Role** | lead, melody, ornament, accent, harmony |
| **Synthesis** | PhaseModSynth (free-reed aerophone, sound/synthesis/phase_mod.py) |

## Constants

```
MIDI_PROGRAM = 22
GM_NAME = "Harmonica"
STEM_LABEL = "Harmonica"
RANGE_MIN = 48      # C3
RANGE_MAX = 96      # C7
SOLO_RANGE = (60, 84)   # C4-C6
SWEET_SPOT = (64, 79)   # E4-G6
ZONES = {
    "low": (48, 59),     # C3-B3 — chromatic bass reeds
    "mid": (60, 76),     # C4-E5 — primary melodic register
    "high": (77, 89),    # F5-F6 — bright, cutting
    "extreme": (90, 96), # G6-C7 — thin, piercing
}
ARTICULATIONS = {
    "blow": (74, 1.0),      # standard exhaled note
    "draw": (68, 1.0),      # inhaled note
    "staccato": (75, 0.15), # tongue-stop
    "shakes": (82, 0.5),    # hand tremolo (wah-wah)
    "bend": (62, 1.6),      # pitch bend 2-3 semitones
    "overblow": (90, 0.25), # extreme reed-bending
}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.5,
    "attack": 0.010,
    "release": 0.04,
}
REVERB_TAIL = 1.2     # shortest in Woodwind family
EQ_BODY = (500, -2.0)
EQ_PRESENCE = (2000, 3.0)
EQ_AIR = (7000, 2.0)
PAN = 0.0
```

## Registration Proof

```
| Woodwind | Harmonica | 22 | 48–96 | lead, harmony, accent |
```

Verification lines from `instrument_registry.py __main__`:

```
HARMONICA.midi_program = 22 (should be 22)
by_name('harmonica') = <Instrument Harmonica (family=Woodwind, program=22, range=48-96)>
by_program(22) = <Instrument Harmonica (family=Woodwind, program=22, range=48-96)>
HARMONICA.in_sweet_spot(69) = True
```

## Verification Results

| Check | Status | Detail |
|---|---|---|
| **Constants load** | ✓ | program=22, stem='Harmonica', zones=4, arts=6 |
| **Zero-drift** | ✓ | `validate()` returned True (OK) |
| **MIDI** | ✓ | 111 bytes (> 40) |
| **SoundFont** | ✓ | FluidR3_GM.sf2 (preferred) — NOT TimGM6mb |
| **WAV (solo)** | ✓ | 736300 bytes (> 40) — solo harmonica, no unison doubling |
| **Spectral buzz** | ✓ | 4-8 kHz = 2.3% (well under 20% gate) |
| **Stem label** | ✓ | pipeline GM_PROGRAMS[22] = "Harmonica" — no quirk |
| **SF2 preset** | ✓ | FluidR3 preset 22 = "Harmonica" — exact match |
| **RenderPipeline stems** | ✓ | `track00_Harmonica.wav` (736300 bytes) |
| **Pitch sweep (48–96)** | ✓ | All 13/13 notes play (C3–C7, every 4th) |

## Stem-Label Quirks

**None.** GM22 → GM_PROGRAMS[22] = "Harmonica" → STEM_LABEL = "Harmonica" → FluidR3 preset 22 = "Harmonica" — all three match exactly.

## Synthesis Recommendation

**PhaseModSynth** (primary): free-reed aerophone with saw carrier, mod_depth 2.5 (between flute 1.5 and accordion 3.2), attack 0.010 (fastest reed onset in KB), release 0.04 (near-instant breath cutoff). Bend simulation requires MIDI pitch-bend events (the GM patch is clean chromatic).

## Quirks Found

1. **Spectral character**: 2.3% buzz — harmonica's natural reed buzz is moderate, well under the 20% gate. No comb-filtering (solo render).
2. **Bend simulation**: GM FluidSynth doesn't model reed bends. Composition jobs must use pitch-bend MIDI events for blues expression. The bend is a pitch-wheel slide (not a reed drop) in GM.
3. **Shortest reverb tail**: REVERB_TAIL = 1.2 s is the shortest in the Woodwind family — intentional for dry, close-mic'd harmonica tone.

## Files Created

| File | Purpose |
|---|---|
| `Woodwind/harmonica/instrument.md` | Full research reference (YAML frontmatter + sections) |
| `Woodwind/harmonica/harmonica.py` | Importable constants |
| `_test/verify_harmonica.py` | Verification script |
| `instrument_registry.py` | Registered as `HARMONICA` constant |
| `registry.md` | Updated with 2026-09-24 entry |