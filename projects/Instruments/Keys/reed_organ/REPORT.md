# Reed Organ (Harmonium) — Instrument Research Report

**Date**: 2026-10-07
**Instrument**: Reed Organ (GM20) — Harmonium / Pump Organ
**Family**: Keys
**Report path**: `/opt/data/projects/Instruments/Keys/reed_organ/`

---

## 1. Instrument Identity

| Field | Value |
|---|---|
| **GM Program** | 20 |
| **GM Name** | "Reed Organ" |
| **Pipeline label** | GM_PROGRAMS[20] = "Reed Organ" |
| **SF2 label** | FluidR3 preset 20 = "Reed Organ" |
| **Stem label** | `Reed_Organ` → `trackXX_Reed_Organ.wav` |
| **Stem quirk** | **None** — labels match exactly |

**Identity**: The Reed Organ (Harmonium / Pump Organ) is a free-reed aerophone keyboard instrument operated by foot-pumped or hand-pumped bellows. Unlike the pipe organ (GM19), the reed organ has **one reed per pitch** with no pipes — the tone is shaped by the wooden cabinet resonator. Three main traditions:
- **American Reed Organ** (suction): foot-treadle vacuum, softer sweeter tone
- **European Harmonium** (pressure): foot-pumped, louder/sharp attack
- **Indian Harmonium**: hand-pumped, ubiquitous in North Indian classical/Qawwali, with drone stops

---

## 2. Range & Register

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Bass | 36–47 | C2–B2 | Dark, rumbling, 8' bass reeds |
| Low (tenor) | 48–59 | C3–B3 | Warm, reedy, cello-like |
| Middle | 60–76 | C4–E5 | Primary melodic: richest cabinet tone |
| High | 77–89 | F5–F6 | Bright, cutting, 4' treble |
| Extended | 90–96 | G6–C7 | Thin, low reed density |

- **Full range**: 36–96 (C2–C7)
- **Sweet spot**: 60–84 (C4–C6)
- **Solo range**: 48–84 (C3–C6)

---

## 3. Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Sustain | 74 | 1.0 | Steady bellows, held — default |
| Staccato | 78 | 0.2 | Short bellows pulse, crisp |
| Legato | 68 | 1.0 | Smooth connected, minimal bellows |
| Marcato | 86 | 0.85 | Hard accent, cabinet bloom |
| Sforzando | 92 | 0.8 | Sudden forceful bellows push |
| Tremolo | 70 | 0.6 | Bellows shake — amplitude vibrato |

---

## 4. Synthesis Engine

**Primary**: `phase_mod` (PhaseModSynth — free-reed aerophone)

```python
FM_DEFAULTS = {
    "carrier_shape": "saw",      # Free reed = even+odd harmonics
    "mod_freq_ratio": 1.0,       # Fundamental-locked
    "mod_depth": 3.5,            # Between accordion (3.2) and bagpipe (4.5)
    "attack": 0.04,              # Wind chest fill time
    "release": 0.06,             # Bellows release
}
```

**Fallback**: `modal` (ModalSynth stock 'string' preset)
**Alt**: `additive` (saw+bandpass for cabinet shaping)

---

## 5. Production Defaults

| Parameter | Value | Reason |
|---|---|---|
| Reverb tail | 1.6 s | Chamber — keep reed clarity, avoid washout |
| EQ body | −2.5 dB @ 250 Hz | Cut cabinet honk/boxiness |
| EQ presence | +2.5 dB @ 2200 Hz | Reed definition and cut |
| EQ air | +1.5 dB @ 7.5 kHz | Subtle reed buzz sparkle |
| Pan | 0.0 | Center; ±0.15–0.25 for stereo |

---

## 6. Registration Proof

```
| Keys | Reed Organ | 20 | 36–96 | harmony, pad, melody, drone, ornament |
```

Verification output:
```
REED_ORGAN.midi_program = 20 (should be 20)
by_name('reed organ') = <Instrument Reed Organ (family=Keys, program=20, range=36-96)>
by_program(20) = <Instrument Reed Organ (family=Keys, program=20, range=36-96)>
REED_ORGAN.in_sweet_spot(72) = True
REED_ORGAN.in_sweet_spot(30) = False
REED_ORGAN.range_min = 36 REED_ORGAN.range_max = 96
REED_ORGAN.stem_label = 'Reed Organ'
```

Registered in `instrument_registry.py` as `REED_ORGAN` convenience constant.

---

## 7. Engine Verification Results

| Check | Result |
|---|---|
| Zero-drift validation | ✓ (OK) |
| MIDI export | 103 bytes (≥ 40 ✓) |
| FluidSynth WAV solo | 777,004 bytes (≥ 40 ✓) |
| SoundFont | FluidR3_GM.sf2 (via discover_soundfont()) |
| Spectral buzz (4–8 kHz) | 1.5% (≤ 20% gate ✓) |
| Stem label | `track00_Reed_Organ.wav` ✓ |
| Pipeline GM label | GM_PROGRAMS[20] = "Reed Organ" ✓ |
| SF2 preset name | "Reed Organ" ✓ |
| PhaseModSynth C4 (262 Hz) | peak=0.7882 ✓ |
| PhaseModSynth C5 (523 Hz) | peak=0.7904 ✓ |
| PhaseModSynth C6 (1047 Hz) | peak=0.7816 ✓ |
| Stem render | 1 file (777 KB) ✓ |

---

## 8. Quirks Found

| # | Quirk | Severity |
|---|---|---|
| 1 | **None** — all labels match exactly | ✅ Clean |
| 2 | Channel 9 quirk (standard): MUST use melodic channel (0–8, 10–15) with program 20 — channel 9 triggers drum-kit map + `Acoustic_Grand_Piano` label | ⚠️ Standard |
| 3 | Polyphonic instrument: unlike line voices (clarinet, fiddle), the reed organ supports full 3–5 note chords — composition jobs should write chordal textures | ✅ Feature |
| 4 | Cabinet resonance at ~250 Hz: the wooden resonator box gives the reed organ a distinctive warm/nasal tone distinct from accordion or harmonica — EQ body cut at 250 Hz tames the "honk" | ✅ Noted |
| 5 | Indian hand-pumped harmonium tuning: may be tuned to Sa=Pa rather than equal temperament in traditional contexts — composition jobs using equal-temperament MIDI match the GM patch | ✅ Noted |

---

## 9. Files Created

| File | Description |
|---|---|
| `Keys/reed_organ/instrument.md` | Full research reference (YAML frontmatter + sections) |
| `Keys/reed_organ/reed_organ.py` | Importable constants (MIDI_PROGRAM, zones, articulations, synthesis defaults, etc.) |
| `Keys/reed_organ/verify_reed_organ.py` | Verification script (runs engine test) |
| `Keys/reed_organ/reed_organ_test.mid` | MIDI output (103 bytes) |
| `Keys/reed_organ/reed_organ_test.wav` | FluidSynth WAV (777 KB) |
| `Keys/reed_organ/stems/track00_Reed_Organ.wav` | Pipeline stem render (777 KB) |
| `Keys/reed_organ/REPORT.md` | This report |

**Registry updated**: `instrument_registry.py` — module entry, convenience constant, verification lines, role assignment, stem label quirk entry.

**Registry documentation updated**: `registry.md` — changelog entry, registry table row, stem label quirk row.