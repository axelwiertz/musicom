# REPORT — Synth Brass 1 (GM62)

**Date**: 2026-10-29 (nightly instrument research job, LAYER-ALIGNED)
**Family**: Synth (second entry — after synth_pad GM88)
**Files**: `Synth/synth_brass_1/instrument.md` + `Synth/synth_brass_1/synth_brass_1.py`
**Registered**: `instrument_registry.py` (`SYNTH_BRASS_1`, module map, role row, verification block)

## Instrument

**GM62 "Synth Brass 1"** — the classic analog synth brass: a stack of
slightly-detuned sawtooth oscillators through a resonant low-pass filter
with a fast attack and punchy ADSR. The "brassy stab" voice of
funk/disco/synth-pop/film (Prophet-5 / OB-Xa brass patches, Earth Wind &
Fire "Shining Star" stab, Gary Numan / Depeche Mode brass swells).

Distinct from the acoustic Brass family (trumpet 56 / trombone 57 / tuba 58 /
muted_trumpet 59 / french_horn 60 / brass_section 61 — all PhaseModSynth saw
carriers): GM62's tone is an **oscillator + filter**, no physical instrument,
and it is **polyphonic** (stab chords, brass-pad harmony, unison leads all
idiomatic).

Selection note: the earlier `_test/_probe_candidates.py` probed GM programs
52/54/55/62/82–87. GM52 (Choir Aahs) was claimed 2026-10-26. GM62 is the
next broadly-usable candidate: collision-free (`by_program(62)` unique;
voice_like members claim 80/81, choir took 52), complementary to the Synth
family, and the classic electronic "horn section" voice. GM55 (Orchestra
Hit) and GM54 (Synth Voice) remain as future candidates.

## Program

- **MIDI_PROGRAM = 62** (GM1 "Synth Brass 1"; raw GM number — the
  `MidiInstrument` enum in `structures/instrument.py` exposes only 10
  legacy instruments and has NO synth-brass constant; the registry is the
  full KB)
- **GM_NAME = "Synth Brass 1"**; **STEM_LABEL = "Synth_Brass_1"**
- RenderPipeline stem: `GM_PROGRAMS[62]` = `"Synth Brass 1"` → sanitized
  `track00_Synth_Brass_1.wav` — **labels match exactly, no quirk**
- FluidR3 preset 62 (phdr-verified) = `"Synth Brass 1"` — **exact match**
  (contrast the known quirks: GM74 Flute→"Recorder", GM109→"Bag pipe",
  GM111→"Shanai")

## Range

| Zone | MIDI | Pitches |
|---|---|---|
| Full range (writing band) | 36–96 | C2–C7 |
| Low | 36–55 | C2–G3 |
| Mid | 56–71 | B3–C5 |
| High | 72–84 | C5–C6 |
| Top extension | 85–96 | C6–C7 |

- **SOLO_RANGE = (48, 84)** (C3–C6); **SWEET_SPOT = (55, 79)** (G3–G5 — the
  funk stab/punch zone)
- Empirical FluidR3 pitch sweep (velocity 90, held notes): notes
  36/48/60/72/84/96/108 → RMS 2192/2153/2170/2306/2215/2427/2330 —
  **7/7 audible, no gaps, essentially flat across the whole span**. GM synth
  patches are full-keyboard: **no patch ceiling** — SF2 never clips a
  composition. 36–96 is the idiomatic writing band (mud below C2, squeak
  above C7), not a physical limit.

## Role

`lead, harmony, accent, stab, pad, countermelody` — polyphonic:

- **Lead** — unison synth-brass leads (octave-doubled for width); piercing
  top lines 72–84
- **Harmony** — brass-pad sustained chords; stab-chord comping (funk "horn
  hit" on the 1 and the "and")
- **Accent** — sfz hits, marcato downbeats, riser swells
- **Stab** — the signature: short gates (≤ 0.3 bar) keep the punch a punch
- **Pad** — sustained brass swells (swell articulation)
- **NOT** a bass voice (use synth_bass_1 / electric_bass), NOT an
  acoustic-brass substitute (no physical articulation — no real brass
  fall/rip without pitch-bend)

## Synthesis Engine

**Polysynth primary** (`sound/synthesis/polysynth.py` PolyVoice) — the
polyBLEP subtractive architecture IS the analog brass (saw osc stack + 24dB
multimode low-pass + ADSR), and it is POLYPHONIC so stabs/chords work.

- `POLYSYNTH_DEFAULTS`: osc1 saw, osc2 saw detuned +7 cents, osc3 square
  (level 0.25), filter cutoff 2800 Hz, resonance 0.45, filter env 0.35,
  ADSR attack 0.015 s / decay 0.18 / sustain 0.75 / release 0.25,
  unison_voices 2
- Smoke: PolyVoice G4 (22050 Hz) peak = 1.404, sustain_rms/peak = 0.162
  (sustain holds — no collapse)

**PhaseModSynth secondary** (FM brass, `FM_DEFAULTS`): saw carrier, sine
mod, ratio 1.0, depth **3.2** (between brass_section 2.8 and overdriven 4.0
— the synth edge), attack 0.02 s, release 0.25 s, sustain 0.75. Smoke: G4
peak = 0.764.

**Additive tertiary** (`ADDITIVE_DEFAULTS`): brass-rolloff stack
[1.0, 0.9, 0.7, 0.5, 0.35, 0.2, 0.12, 0.08].

## Constants (synth_brass_1.py)

```python
MIDI_PROGRAM = 62
GM_NAME = "Synth Brass 1"
STEM_LABEL = "Synth_Brass_1"
RANGE_MIN = 36
RANGE_MAX = 96
SOLO_RANGE = (48, 84)
SWEET_SPOT = (55, 79)
ZONES = {"low": (36, 55), "mid": (56, 71), "high": (72, 84),
         "top_extension": (85, 96)}
ARTICULATIONS = {"stab": (96, 0.30), "sustain": (78, 1.0), "swell": (72, 1.15),
                 "legato": (74, 1.0), "marcato": (88, 0.70),
                 "staccato": (70, 0.25), "sfz": (100, 0.35), "rip": (92, 0.20)}
SYNTHESIS = "polysynth"
POLYSYNTH_DEFAULTS = {"osc1_waveform": "saw", "osc2_waveform": "saw",
                      "osc2_detune_cents": 7.0, "osc3_waveform": "square",
                      "osc3_level": 0.25, "filter_cutoff": 2800.0,
                      "filter_resonance": 0.45, "filter_env_amount": 0.35,
                      "env_attack": 0.015, "env_decay": 0.18,
                      "env_sustain": 0.75, "env_release": 0.25,
                      "unison_voices": 2}
SYNTHESIS_DEFAULTS = {"instrument": "synth_brass_1", **POLYSYNTH_DEFAULTS}
FM_DEFAULTS = {"carrier_shape": "saw", "mod_shape": "sine",
               "mod_freq_ratio": 1.0, "mod_depth": 3.2,
               "attack": 0.02, "release": 0.25, "sustain_level": 0.75}
ADDITIVE_DEFAULTS = {"harmonic_count": 8,
                     "harmonic_weights": [1.0, 0.9, 0.7, 0.5, 0.35, 0.2, 0.12, 0.08],
                     "attack": 0.02, "release": 0.25}
REVERB_TAIL = 2.2
EQ_BODY = (300, -2.5)
EQ_PRESENCE = (2800, 2.5)
EQ_AIR = (8000, 1.0)
PAN = 0.0
```

## Registration Proof

`instrument_registry.py` changes:
1. `_INSTRUMENT_MODULES["Synth.synth_brass_1.synth_brass_1"] = "synth_brass_1"`
2. `SYNTH_BRASS_1 = ALL_INSTRUMENTS["synth_brass_1"]`
3. `registry_table()` role row for "synth brass 1"
4. `__main__` verification block

Registry run output (new row + verification):

```
| Synth | Pad 1 (new age) | 88 | 36–96 | pad, harmony, texture, drone, accent |
| Synth | Synth Brass 1 | 62 | 36–96 | lead, harmony, accent, stab, pad, countermelody |

=== Synth Brass 1 (GM62) ===
  SYNTH_BRASS_1.midi_program = 62 (should be 62)
  by_name('synth brass 1') = <Instrument Synth Brass 1 (family=Synth, program=62, range=36-96)>
  by_name('SYNTH BRASS 1') = <Instrument Synth Brass 1 (family=Synth, program=62, range=36-96)>
  by_program(62) = <Instrument Synth Brass 1 (family=Synth, program=62, range=36-96)>
  SYNTH_BRASS_1.in_sweet_spot(67) = True
  SYNTH_BRASS_1.in_sweet_spot(24) = False
  SYNTH_BRASS_1.range_min = 36 SYNTH_BRASS_1.range_max = 96
  SYNTH_BRASS_1.stem_label = 'Synth_Brass_1'
```

## Verification Results

Run: `/opt/data/micromamba/envs/musicom/bin/python _test/verify_synth_brass_1.py`

- **Registration**: `SYNTH_BRASS_1 is by_name("synth brass 1")` ✓,
  `by_program(62) is SYNTH_BRASS_1` ✓
- **Zero-drift**: `True (OK)` — 2 voices (Synth Brass 1 ch0 + Drum Kit ch9
  context), 1 bar, stab pattern with terminal landmark flush at BAR
- **MIDI**: `synth_brass_1_test.mid` = **184 bytes** (> 40 ✓)
- **WAV (SOLO render, FluidR3 via `discover_soundfont()`)**: 794,668 bytes
  (> 40 ✓); SoundFont = `/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2`
  (not a hardcoded TimGM6mb path)
- **Spectral check**: 4–8 kHz buzz = **2.6%** (OK — single voice, no
  comb-filtering; the instrument was rendered SOLO, drum track excluded)
- **Stem label**: `GM_PROGRAMS[62]` = `'Synth Brass 1'` == STEM_LABEL
  `'Synth_Brass_1'` ✓; **SF2 preset 62** = `'Synth Brass 1'` ✓ (exact match,
  no quirk)
- **RenderPipeline stems on disk**: `track00_Synth_Brass_1.wav` (794,668 B)
  + `track01_Drums.wav` (706,092 B) ✓
- **Engine smoke**: Polysynth brass G4 peak 1.404, sustain/peak 0.162
  (holds); PhaseModSynth brass G4 peak 0.764
- **Empirical sweep**: 7/7 notes audible (36–108), no gaps

## Quirks Found

1. **Stem label — NO quirk**: GM_PROGRAMS[62] = "Synth Brass 1" = FluidR3
   preset 62 = "Synth Brass 1"; sanitized stem `Synth_Brass_1`. (Contrast
   the known quirks at 74/109/111.)
2. **MidiInstrument enum**: no synth-brass constant (10-instrument legacy
   enum) — composition jobs use raw GM 62; the registry is the full KB.
3. **Channel quirk**: melodic channel (0–9) — channel 9 with program 62
   triggers the drum-kit map + `Acoustic_Grand_Piano` program-0 fallback
   label (timpani lesson).
4. **Full-keyboard patch**: no per-note ceiling (unlike timpani/pizzicato)
   — never clips; the 36–96 range is a writing convention, not a physical
   limit.
5. **No unison doubling** (2026-09-01 rule): render/compose solo or with
   octave doubling; never a second melodic patch on the same pitches.
6. **GM63 "Synth Brass 2"** is the softer/darker sibling — future Synth
   family candidate; GM55 Orchestra Hit / GM54 Synth Voice also remain
   unclaimed from the original probe list.
