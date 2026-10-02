# Baritone Saxophone (GM 67) — Instrument Report

## Instrument Identity

| Field | Value |
|---|---|
| **Instrument** | Baritone Saxophone |
| **Family** | Woodwind |
| **GM Program** | 67 (0-indexed; GM spec #68 "Baritone Sax") |
| **Transposition** | E♭ instrument (sounds octave + major 6th below written) |
| **Pipeline label** | GM_PROGRAMS[67] = "Baritone Sax" → `trackXX_Baritone_Sax.wav` |
| **FluidR3 preset** | 67 = "Baritone Sax" (exact match, **no quirk**) |
| **STEM_LABEL** | `"Baritone_Sax"` |

## Range

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| **Full range** | 36–80 | C2–G5 (concert) | GM patch with altissimo extension |
| **Sweet spot** | 48–65 | C3–F4 | Warm, round, singing — the bari's money register |
| **Low** | 36–47 | C2–B2 | Dark, rumbling, tuba-like depth |
| **Mid** | 48–60 | C3–C4 | Warm, vocal, woody core — Gerry Mulligan territory |
| **High** | 61–80 | C#4–G5 | Bright, cutting, altissimo scream — punchy accent |

## Role

**Bass / Harmony / Accent / Lead / Countermelody**

The baritone sax is the **bass of the sax section** — the lowest voice in the sax family, covering bass lines in a standard 4-part section (soprano/alto/tenor/bari). In big band, the bari doubles bass trombone or plays independent bass figures. In smaller combos, it walks bass lines, holds pedal tones, and provides low-end body. Also capable of iconic lead (Gerry Mulligan, Serge Chaloff, Pepper Adams, Leo Parker) and punchy accent (the "bari bark").

## Synthesis Engine

**PhaseModSynth** (`sound/synthesis/phase_mod.py`) — primary

| Parameter | Value | Rationale |
|---|---|---|
| carrier_shape | `"saw"` | Conical bore single reed: even+odd harmonics |
| mod_freq_ratio | 1.0 | Reed-driven oscillator, fundamental locked |
| mod_depth | **3.2** | Deepest in the sax family — the thickest, darkest reed core |
| attack | 0.07 s | Heaviest reed in the family (60-80 ms onset) |
| release | 0.12 s | Massive air column takes longer to stop |

**Additive** (`sound/synthesis/additive.py`) — fallback: explicit even+odd partials with strong fundamental dominance, boost 800–2000 Hz partials for the bari bark.

## Constants

```python
MIDI_PROGRAM = 67
GM_NAME = "Baritone Saxophone"
STEM_LABEL = "Baritone_Sax"

RANGE_MIN = 36       # C2
RANGE_MAX = 80       # G5
SOLO_RANGE = (42, 72)   # F2-C5
SWEET_SPOT = (48, 65)   # C3-F4

ZONES = {
    "low": (36, 47),
    "mid": (48, 60),
    "high": (61, 80),
}

ARTICULATIONS = {
    "legato": (78, 1.0),
    "tenuto": (70, 0.85),
    "staccato": (64, 0.25),
    "accent": (94, 0.9),
    "growl": (78, 1.0),
    "vibrato": (78, 1.0),
    "subtoned": (55, 1.2),
    "slap_tongue": (88, 0.05),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw",
    "mod_freq_ratio": 1.0,
    "mod_depth": 3.2,
    "attack": 0.07,
    "release": 0.12,
}

REVERB_TAIL = 1.8
EQ_BODY = (400, -3.0)
EQ_PRESENCE = (1600, 2.5)
EQ_AIR = (5000, 1.5)
PAN = 0.0
```

## Registration Proof

Registry verification output (from `instrument_registry.py __main__`):

```
BARITONE_SAX.midi_program = 67 (should be 67)
by_name('baritone sax') = <Instrument Baritone Saxophone (family=Woodwind, program=67, range=36-80)>
by_program(67) = <Instrument Baritone Saxophone (family=Woodwind, program=67, range=36-80)>
BARITONE_SAX.in_sweet_spot(60) = True
BARITONE_SAX.in_sweet_spot(30) = False
```

Registry table row:
```
| Woodwind | Baritone Saxophone | 67 | 36–80 | bass, harmony, accent, lead, countermelody |
```

## Verification Results

| Check | Result |
|---|---|
| Zero-drift | True (OK) |
| MIDI size | 173 bytes (> 40 ✓) |
| WAV size (solo) | 737836 bytes (> 40 ✓) |
| Spectral check (4-8 kHz buzz) | 0.5% (< 20% gate ✓) |
| Pipeline stem label | `track00_Baritone_Sax.wav` ✓ |
| Stem label match | GM_PROGRAMS[67] = "Baritone Sax" → `Baritone_Sax` ✓ |

No comb-filtering buzz — solo baritone sax line (13 notes in C3-F4 sweet spot), no unison doubling. Zero-drift invariant holds.

## Quirks

- **No stem label quirk**: GM_PROGRAMS[67] = "Baritone Sax" → `Baritone_Sax` — matches FluidR3 preset 67 = "Baritone Sax". Exact match, no routing impact.
- **Line instrument**: Baritone sax is a single-wind monophonic voice — no dense chords (a sax can only play one note at a time). Composition jobs write single-note lines.
- **Bass voice of the sax section**: In 4-part writing (soprano/alto/tenor/bari), the bari plays the bottom part. DON'T stack another bass instrument on the same pitch class as the bari in the same register — comb-filtering risk.
- **Transposition**: E♭ instrument (sounds octave + major 6th below written). The constants use **concert (sounding) pitch** — composition jobs write at concert pitch and let the MIDI patch transpose.
- **Heaviest reed in the sax family**: Attack is the slowest (0.07 s) — don't write 32nd-note runs at high tempo expecting crisp articulation.

## File Locations

| File | Path |
|---|---|
| instrument.md | `Woodwind/baritone_sax/instrument.md` |
| Constants | `Woodwind/baritone_sax/baritone_sax.py` |
| Registry | `instrument_registry.py` |
| Registry verifier | `_test/verify_baritone_sax_registry.py` |
| Engine verifier | `_test/verify_baritone_sax.py` |
| Test MIDI | `_test/baritone_sax_test.mid` |
| Test WAV | `_test/baritone_sax_test.wav` |
| Stems output | `_test/stems_baritone_sax/track00_Baritone_Sax.wav` |