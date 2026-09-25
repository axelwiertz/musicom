# Shakuhachi — Instrument Research Report (2026-09-25)

## Instrument Identity

| Field | Value |
|---|---|
| **Family** | World |
| **Name** | Shakuhachi |
| **GM Program** | 77 |
| **GM Name** | Shakuhachi |
| **Stem Label** | Shakuhachi (exact match, no quirk) |
| **SoundFont Preset** | FluidR3 preset 77 = "Shakuhachi" (exact match) |

## Range

| Zone | Japanese | MIDI | Pitches | Description |
|------|----------|------|---------|-------------|
| Full | — | 55–100 | G3–E7 | 1.8 shaku: D4–D6; 2.4 shaku: A3; expert: E7 |
| Otsu (lower) | 乙/呂 | 62–73 | D4–D5 | Dark, full, meditative |
| Kan (upper) | 甲 | 74–85 | E5–D6 | Bright, penetrating |
| Dai-kan (3rd octave) | 大甲 | 86–100 | E6–E7 | Airy, extended, expert only |
| **Solo range** | — | 62–86 | D4–D6 | Standard 2-octave honkyoku core |
| **Sweet spot** | — | 64–84 | E4–D6 | Expressive melodic zone |

## Constants (shakuhachi.py)

```
MIDI_PROGRAM = 77
GM_NAME = "Shakuhachi"
STEM_LABEL = "Shakuhachi"
RANGE_MIN = 55       # G3
RANGE_MAX = 100      # E7
SOLO_RANGE = (62, 86)   # D4-D6
SWEET_SPOT = (64, 84)   # E4-D6

ZONES = {
    "otsu": (62, 73),
    "kan": (74, 85),
    "dai_kan": (86, 100),
}

ARTICULATIONS = {
    "legato": (72, 1.0),
    "staccato": (60, 0.30),
    "muraiki": (88, 0.80),
    "meri": (75, 1.0),
    "kari": (78, 1.0),
    "yuri": (70, 1.0),
    "accent": (92, 0.85),
    "breath": (48, 1.0),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 2.0,
    "attack": 0.06,
    "release": 0.20,
}

REVERB_TAIL = 2.5
EQ_BODY = (400, -1.5)
EQ_PRESENCE = (3500, 2.5)
PAN = 0.0
```

## Role

lead, melody, ornament, drone, accent

## Synthesis Engine

**PhaseModSynth** (primary): end-blown bamboo flute — sine carrier + sine
modulator, mod_freq_ratio 1.0 (bamboo tube resonator), mod_depth 2.0 (more
than flute 1.5 — richer upper harmonics), attack 0.06 s (breath onset),
release 0.20 s (bamboo resonance ring).

**Additive** (fallback): fundamental + small upper harmonics + noise floor
above 6 kHz for breathy muraiki character.

## Registration Proof

Full `registry_table()` output including Shakuhachi row:

```
| World | Shakuhachi | 77 | 55–100 | lead, melody, ornament, drone, accent |
```

Verification output:
```
SHAKUCHACHI.midi_program = 77 (should be 77)
by_name('shakuhachi') = <Instrument Shakuhachi (family=World, program=77, range=55-100)>
by_program(77) = <Instrument Shakuhachi (family=World, program=77, range=55-100)>
SHAKUCHACHI.in_sweet_spot(74) = True
```

## Verification Results

| Check | Result |
|---|---|
| **Zero-drift** | True (OK) |
| **MIDI size** | 150 bytes (> 40 ✓) |
| **WAV size (solo)** | 1,271,340 bytes (> 1000 ✓) |
| **Spectral buzz (4–8 kHz)** | 0.6% (well below 20% gate ✓) |
| **Stem label** | GM_PROGRAMS[77] = "Shakuhachi" ✓ |
| **FluidR3 preset 77** | "Shakuhachi" ✓ |
| **PhaseModSynth render** | peak=0.800 (audible ✓) |
| **Stem render: track00_Shakuhachi.wav** | 1,269,036 bytes ✓ |

## Quirks Found

- **No stem label quirk**: GM_PROGRAMS[77] = "Shakuhachi" matches the
  instrument name exactly. FluidR3 preset 77 = "Shakuhachi" also matches.
  This is the cleanest label match in the World family (vs. shenai→"Shanai",
  bagpipe→"Bag_pipe").
- **Line instrument**: monophonic bamboo flute — no dense chords. Honkyoku
  tradition is a single melodic line over a drone. Pentatonic writing (D
  minor pentatonic) is idiomatic.
- **Meri/kari bending**: pitch can be bent a whole tone or more via
  embouchure changes. Composition jobs should use MIDI pitch-bend events
  for authentic Zen-style glissando.
- **No fipple**: end-blown across a sharp edge (utaguchi), unlike recorder.
  Breath pressure control is central — the muraiki (explosive breath blast)
  is a characteristic articulation.
- **Channel**: melodic channel (0–9) with program 77. Channel 9 triggers
  percussion map.

## File Locations

- `/opt/data/projects/Instruments/World/shakuhachi/instrument.md`
- `/opt/data/projects/Instruments/World/shakuhachi/shakuhachi.py`
- `/opt/data/projects/Instruments/instrument_registry.py` (registered)
- `/opt/data/projects/Instruments/registry.md` (registry table updated)
- `/opt/data/projects/Instruments/_test/verify_shakuhachi.py` (verify script)
- `/opt/data/projects/Instruments/_test/shakuhachi_test.mid`
- `/opt/data/projects/Instruments/_test/shakuhachi_test.wav`
- `/opt/data/projects/Instruments/_test/stems_shakuhachi/` (stem render output)