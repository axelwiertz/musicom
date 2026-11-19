# REPORT — Percussive Organ (GM17)

Nightly instrument research job, 2026-11-19. Layer-aligned addition to the
musicom Instruments KB, registered in the importable registry.

## Summary

| Field | Value |
|---|---|
| Instrument | Percussive Organ (tonewheel organ + key-on percussion tab) |
| Family | Keys |
| MIDI / GM program | **17** (GM1 0-based; bank 0) |
| GM name | "Percussive Organ" |
| Path | `Keys/percussive_organ/{instrument.md, percussive_organ.py}` |
| Range | 36–96 (C2–C7), solo 48–84 (C3–C6), sweet spot 52–84 (E3–C6) |
| Role | comp, rhythm, harmony, pad, lead, bass, accent, drone |
| Synthesis engine | `additive` (SoundWave) + separate percussion-ping voice; PhaseModSynth fallback |
| Registry key / constant | `percussive_organ` / `PERCUSSIVE_ORGAN` |
| Stem label | `Percussive_Organ` (no quirk) |

Why this instrument: remaining backlog candidate, and it completes the Hammond
tonewheel set — GM16 Drawbar (clean), **GM17 Percussive** (percussion tab),
GM18 Rock (saturated), GM19 Church (pipes), GM20 Reed. Distinct identity: the
percussion tab fires a fast-decaying 2nd/3rd harmonic ping on every key-on, so
the patch is *articulate* — the classic jazz/funk/soul comping organ (Jimmy
Smith, Jimmy McGriff, Billy Preston, Booker T. on bright stops).

## Constants (`percussive_organ.py`)

```python
MIDI_PROGRAM = 17
GM_NAME = "Percussive Organ"
STEM_LABEL = "Percussive_Organ"

RANGE_MIN = 36          # C2
RANGE_MAX = 96          # C7
SOLO_RANGE = (48, 84)   # C3–C6
SWEET_SPOT = (52, 84)   # E3–C6
ZONES = {
    "bass": (36, 55),   # left-hand key bass, percussion OFF
    "mid":  (56, 79),   # primary comp register, 3rd-harmonic ping
    "high": (80, 96),   # funk stabs, 2nd-harmonic ping, solos
}

ARTICULATIONS = {                  # (velocity, duration_factor)
    "sustain":    (82, 1.0),
    "stab":       (96, 0.18),
    "chop":       (74, 0.09),
    "percussion": (92, 0.30),
    "key_click":  (70, 0.05),
    "accent":     (104, 0.80),
    "swell":      (94, 1.0),
    "smear":      (64, 0.90),
}

SYNTHESIS = "additive"

DRAWBAR_PRESETS = {
    "perc3":  (8, 8, 8, 0, 0, 0, 0, 0, 0),
    "perc2":  (8, 8, 8, 0, 0, 0, 0, 0, 0),
    "funk":   (8, 8, 8, 6, 0, 0, 0, 0, 0),
    "gospel": (8, 8, 8, 8, 6, 0, 0, 0, 0),
    "jazz":   (8, 6, 8, 4, 0, 0, 0, 0, 0),
    "soul":   (8, 0, 8, 4, 0, 0, 0, 0, 0),
    "bass":   (8, 0, 8, 0, 0, 0, 0, 0, 0),
    "ballad": (0, 0, 8, 0, 0, 0, 0, 0, 0),
}

ADDITIVE_HARMONICS = {             # 1x … 8x partial amplitudes
    "perc3":  [1.00, 0.55, 0.75, 0.30, 0.08, 0.04, 0.00, 0.02],
    "perc2":  [1.00, 0.85, 0.40, 0.35, 0.06, 0.03, 0.00, 0.02],
    "funk":   [1.00, 0.60, 0.70, 0.45, 0.15, 0.06, 0.00, 0.04],
    "gospel": [1.00, 0.80, 0.85, 0.60, 0.30, 0.15, 0.05, 0.10],
    "jazz":   [1.00, 0.50, 0.55, 0.28, 0.06, 0.03, 0.00, 0.00],
    "soul":   [1.00, 0.35, 0.30, 0.18, 0.04, 0.00, 0.00, 0.00],
    "bass":   [1.00, 0.45, 0.00, 0.12, 0.00, 0.00, 0.00, 0.00],
    "ballad": [1.00, 0.15, 0.00, 0.03, 0.00, 0.00, 0.00, 0.00],
}

ADDITIVE_ENVELOPE = {"attack": 0.004, "decay": 0.0, "sustain": 1.0,
                     "release": 0.040}

PERCUSSION_DEFAULTS = {
    "harmonic": 3, "level": 0.45, "decay_s": 0.18,
    "decay_setting": "fast", "key_click_level": 0.10, "key_click_ms": 4.0,
}

FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 3.0,
               "mod_depth": 2.4, "mod_decay_s": 0.18,
               "attack": 0.004, "release": 0.04}

REVERB_TAIL = 1.6
EQ_BODY = (300, -1.0)
EQ_PRESENCE = (2500, 2.5)
EQ_AIR = (8000, 1.5)
PAN = 0.0

# helpers: drawbar_harmonics(), percussion_envelope(), midi_to_freq()
```

## Registration proof

`cd /opt/data/projects/Instruments && /opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`
→ exit 0, full `registry_table()` including:

```
| Keys | Percussive Organ | 17 | 36–96 | comp, rhythm, harmony, pad, lead, bass, accent, drone |
```

Verification block printed by the registry run (GM17 section):

```
=== Percussive Organ (Keys, GM17) ===
  PERCUSSIVE_ORGAN.midi_program = 17 (should be 17)
  by_name('percussive organ') = <Instrument Percussive Organ (family=Keys, program=17, range=36-96)>
  by_name('Percussive Organ') = <Instrument Percussive Organ (family=Keys, program=17, range=36-96)>
  by_program(17) = <Instrument Percussive Organ (family=Keys, program=17, range=36-96)>
  by_program(16) = <Instrument Drawbar Organ (family=Keys, program=16, range=24-89)> (distinct: drawbar organ)
  by_program(18) = <Instrument Rock Organ (family=Keys, program=18, range=36-96)> (distinct: rock organ)
  PERCUSSIVE_ORGAN.in_sweet_spot(67) = True
  PERCUSSIVE_ORGAN.in_sweet_spot(30) = False
  PERCUSSIVE_ORGAN.range_min = 36 PERCUSSIVE_ORGAN.range_max = 96
  PERCUSSIVE_ORGAN.solo_range = (48, 84)
  PERCUSSIVE_ORGAN.stem_label = 'Percussive_Organ'
  PERCUSSIVE_ORGAN.synthesis = 'additive'
  PERCUSSIVE_ORGAN.reverb_tail = 1.6 PERCUSSIVE_ORGAN.pan = 0.0
  PERCUSSIVE_ORGAN.articulations = ['sustain', 'stab', 'chop', 'percussion', 'key_click', 'accent', 'swell', 'smear']
```

Full registry output archived at `_test/registry_out_percussive_organ.txt`
(97 registry rows after the addition).

## Engine verification (`_test/verify_percussive_organ.py`)

Imports through the registry (`from instrument_registry import by_name`), one
voice, one track — SOLO render (no unison doubling → no comb buzz).

```
zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/percussive_organ_test.mid (131 bytes)
WAV (solo): /opt/data/projects/Instruments/_test/percussive_organ_test.wav (748844 bytes)
spectral check: 4-8kHz buzz energy = 1.1% (OK)
soundfont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
GM_PROGRAMS[17] = 'Percussive Organ'  (16: 'Drawbar Organ')
SF2 bank0 preset 17 = 'Percussive Organ'
stems: ['track00_Percussive_Organ.wav']
stem track00_Percussive_Organ.wav: 748844 bytes
additive SoundWave perc3: peak=29.9 (sample_count=44100)
ALL CHECKS PASSED
registry rows: 97
```

Test material: 1-bar C7 funk comp (C4 E4 G4 Bb4), downbeat 1/8 stab, "and of
2" stab, held chord to the bar line, terminal landmark `MusicEvent(0,0,len,BAR)`
for zero-drift.

## Measured FluidR3 behaviour / quirks

Solo sweeps and envelope measurements (all from renders through
`discover_soundfont()`; FluidR3_GM.sf2):

1. **Preset name matches pipeline** — GM_PROGRAMS[17] = "Percussive Organ" =
   FluidR3 bank-0 preset 17; stem `track00_Percussive_Organ.wav`. No quirk.
2. **Level flatness** — RMS 0.112–0.176 across 24 notes (MIDI 24–108, step 4):
   within ±2 dB, no gaps, no dead notes.
3. **Pitch tracking correct but harmonics dominate** — strongest partial per
   note (relative dB): C4 → 262 Hz 0 dB, quint 392 Hz −1 dB, sub 65 Hz −3 dB;
   G4 → sub 98 Hz 0 dB, fundamental 391 Hz −9 dB; C5 → 3rd harmonic 786 Hz
   0 dB, fundamental 524 Hz −5 dB. Pitch is unambiguous in context; avoid a
   bare top-octave unison line with GM17 alone.
4. **Sub-octave layer** — 0.25× partial present at −3 dB (C4): the patch
   sounds heavier than written. Keep left hand above C2 with a bass guitar
   present.
5. **Slow body swell** — peak 0.048 at note-on → 0.386 at 250 ms. Staccato
   shorter than ~1/8 at 120 bpm reads as a click; use velocity ≥ 92 for stabs.
6. **Slow decay + wobble** — ~−5 dB/s body decay and ±2 dB at ~0.7 Hz while
   held (preset chorus/rotary). Re-trigger long pads every 2–4 bars.
7. **Velocity → amplitude only** — centroid flat 1.37–1.43 kHz from vel 20 to
   127; peak 0.016 → 0.64 (≈ +32 dB). Accents need real velocity, unlike GM16.
8. Build-up/swell: additive `percussion_envelope(0.18)` → 7938 samples,
   head 1.000, tail 0.0010 (−60 dB).

## Files touched

- `Keys/percussive_organ/instrument.md` (new)
- `Keys/percussive_organ/percussive_organ.py` (new)
- `Keys/percussive_organ/REPORT.md` (this file)
- `instrument_registry.py` — `_INSTRUMENT_MODULES` entry, `PERCUSSIVE_ORGAN`
  constant, `registry_table()` role mapping, `__main__` verification block
- `registry.md` — Registry table row, stem-quirks row, dated changelog entry
- `README.md` — counts 82→91 folders / 88→97 registry keys
- `_test/verify_percussive_organ.py`, `_test/registry_out_percussive_organ.txt`
  (verification artifacts); probe scripts `_test/_probe_perc_organ*.py`
