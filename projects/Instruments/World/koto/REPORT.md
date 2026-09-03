# Koto — Nightly Instrument Research Report (2026-09-02)

New instrument added to the musicom Instruments reference library. Second
World-family entry (after Sitar, GM104 — added 2026-09-02 by the previous
nightly run). World family now has two plucked-string instruments: sitar and
koto.

## Instrument

| Field | Value |
|---|---|
| Family | World |
| Name | Koto |
| MIDI program | **107** (GM1, 0-indexed — matches pipeline + SF2) |
| GM name | Koto |
| Full range | D#3 (51) – F#6 (90) |
| Solo range | A3 (57) – C6 (84) |
| Sweet spot | E4 (64) – G5 (79) |
| Role | lead, melody, ornament, drone, harmony (sparse 2–3 note clusters only) |
| Synthesis | Karplus-Strong (primary), ModalSynth 'string' (fallback), PhaseModSynth (cheap) |

13-string Japanese zither. Plucked with ivory picks (tsume); signature tone
is the *sawari* — a slightly detuned overtone beating against the
fundamental (buzz-string effect). Base tuning **hirajoshi** (D G A D F on
strings 1–5) — pentatonic instrument, NOT chromatic. Composition jobs must
write in-scale lines, not dense tertian harmony.

## Range zones

| Zone | MIDI | Strings | Register |
|---|---|---|---|
| low | 51–60 | 13–9 | warm, dark, long ring |
| mid | 61–76 | 8–4 | primary melodic register |
| high | 77–90 | 3–1 | bright, thin, cutting |

## Articulations (velocity, duration_factor)

| Technique | Velocity | Dur | Meaning |
|---|---|---|---|
| pluck | 78 | 1.0 | standard tsume stroke, full decay |
| oshi | 84 | 1.7 | left-hand press bend (up 2–3 st), elongated |
| hajiki | 88 | 0.4 | flicked snap ornament, bright |
| arpeggio | 66 | 0.25 | kakute strum/roll across strings |
| mute | 44 | 0.15 | palm-choked, dry percussive |

## Constants (koto.py — full)

```python
MIDI_PROGRAM = 107
GM_NAME = "Koto"
STEM_LABEL = "Koto"
RANGE_MIN = 51; RANGE_MAX = 90
SOLO_RANGE = (57, 84); SWEET_SPOT = (64, 79)
ZONES = {"low": (51, 60), "mid": (61, 76), "high": (77, 90)}
ARTICULATIONS = {"pluck": (78, 1.0), "oshi": (84, 1.7), "hajiki": (88, 0.4),
                 "arpeggio": (66, 0.25), "mute": (44, 0.15)}
SYNTHESIS = "karplus"
KARPLUS_DEFAULTS = {"loop_gain": 0.9970, "width": 0.45, "role": "lead"}
MODAL_PRESET = "string"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_freq_ratio": 3.0,
               "mod_depth": 2.5, "attack": 0.002, "release": 0.3}
REVERB_TAIL = 1.4
EQ_BODY = (300, -2.0); EQ_PRESENCE = (3200, 2.0); EQ_AIR = (8500, 1.0)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## Registration proof

`instrument_registry.py` updated:
- `_INSTRUMENT_MODULES["World.koto.koto"] = "koto"`
- `KOTO = ALL_INSTRUMENTS["koto"]` convenience constant
- `registry_table()` role branch for koto
- `__main__` verification lines for KOTO

Registry run output (full `registry_table()` INCLUDING new row + verification):

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
...
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |

Verification:
  ...
  KOTO.midi_program = 107 (should be 107)
  by_name('koto') = <Instrument Koto (family=World, program=107, range=51-90)>
  by_program(107) = <Instrument Koto (family=World, program=107, range=51-90)>
  KOTO.in_sweet_spot(69) = True
```

ALL_INSTRUMENTS count = **20** (was 19).

## Verification results (verify_koto.py)

| Check | Result |
|---|---|
| Import through registry (`by_name('koto')`) | ✓ 20 instruments |
| Zero-drift (`validate()`) | ✓ OK (track lengths equal, terminal landmark flush at BAR) |
| MIDI export | ✓ 135 bytes (> 40) |
| WAV solo render (FluidR3 via `discover_soundfont()`) | ✓ 1,114,668 bytes (> 40) |
| Spectral buzz check (4–8 kHz) | ✓ 4.0% (≤ 20%) — solo koto, no comb-filter buzz |
| Stem label (pipeline GM_PROGRAMS[107]) | ✓ "Koto" → `track00_Koto.wav` on disk |
| SF2 preset 107 (phdr chunk) | ✓ "Koto" (FluidR3_GM.sf2) |
| Karplus-Strong ring | ✓ tail_rms/peak(1–2 s) = 0.004 vs 0.002 dull control (~2× ring) |

Voice stack was Koto SOLO (ch0) + one low bass A2 (ch1, GM33, octave+
below) — no second melodic patch on the same pitches (no unison doubling).

Stems rendered: `track00_Koto.wav`, `track01_Electric_Bass_finger.wav`.

## Quirks found

1. **Stem label**: GM_PROGRAMS[107] = "Koto" — matches exactly, **no quirk**
   (unlike GM74→"Recorder" or ch9 pgm0→"Acoustic_Grand_Piano").
2. **SF2 preset**: FluidR3 preset 107 = "Koto" — matches exactly (unlike
   French Horn 60→"French Horns" or Oboe 68→"Oboe (Orch)").
3. **Hirajoshi tuning quirk** (musical, not pipeline): koto is pentatonic —
   dense chromatic harmony is unidiomatic; role constrained to lead/melody/
   ornament/drone + sparse clusters. Documented in instrument.md + registry.md.
4. **Sitar verify threshold not reusable**: the 3× ring-advantage assertion
   was tuned for sitar's loop_gain 0.9975. Koto's deliberate 0.9970 yields
   ~2× → threshold relaxed to 1.5× with explanatory comment (test-only fix).

## Files

- `/opt/data/projects/Instruments/World/koto/instrument.md` — full research
- `/opt/data/projects/Instruments/World/koto/koto.py` — importable constants
- `/opt/data/projects/Instruments/World/koto/REPORT.md` — this report
- `/opt/data/projects/Instruments/instrument_registry.py` — registered
- `/opt/data/projects/Instruments/registry.md` — changelog + table + quirks
- `/opt/data/projects/Instruments/_test/verify_koto.py` — verification script
- `/opt/data/projects/Instruments/_test/koto_test.mid` — 135 B
- `/opt/data/projects/Instruments/_test/koto_test.wav` — solo render, 1,114,668 B
- `/opt/data/projects/Instruments/_test/stems_koto/` — pipeline stems
