# Orchestra Hit (GM55) — Nightly Instrument Research Report

**Job**: nightly-algorithmic-composition-production — Instruments layer
**Date**: 2026-11-09
**Status**: REGISTERED + VERIFIED (registry proof + solo audio render)

---

## 1. Instrument

| Field | Value |
|---|---|
| Name | Orchestra Hit (a.k.a. Orchestral Hit) |
| Family | Synth |
| GM program | **55** (0-based; GM2 "Orchestra Hit"; Roland GS "Orchestra Hit", Yamaha XG "Orchestra Hit") |
| GM label | "Orchestra Hit" |
| Stem label | `Orchestra_Hit` |
| FluidR3 preset 55 | "Orchestra Hit" (verified from phdr) |
| Identity | Iconic ONE-SHOT ensemble stab: dense layered brass + strings + choir stack fired with a razor attack + fast exponential decay. The punctuation of 80s pop, hip-hop, film trailers and game scores (Yes "Owner of a Lonely Heart", MTV/network ident stabs, beat drops). |

Selection rationale: GM55 was explicitly listed as a remaining candidate in
the two most recent registry entries (synth_voice 2026-10-31, honky_tonk
2026-11-07) and was collision-free — `by_program(55)` had no owner and the
stem `Orchestra_Hit` was unclaimed (54 Synth Voice / 56 Trumpet / 62 Synth
Brass 1 all distinct). The FluidR3 preset name matches the GM label exactly
→ **no stem quirk**.

## 2. Range

| Zone | MIDI | Pitches | Notes |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM-patch idiomatic writing band |
| Low | 36–47 | C2–B2 | sub-hit thump — riser bottoms, drop punctuation |
| Mid | 48–71 | C3–B4 | workhorse stab band — downbeat hits, syncopated punctuation |
| High | 72–84 | C5–C6 | bright top hits — cinematic stabs |
| Top extension | 85–96 | C6–C7 | thin sparkle hits, riser ticks |

Sweet spot 55–79 (G3–G5), solo range 48–84 (C3–C6).

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36/48/60/72/84/96):
**6/6 audible, no gaps** — 1345 / 1235 / 927 / 757 / 527 / 374 (smooth
rolloff, loudest at the bottom, ~3.6× quieter at the top). Full-keyboard
patch, no ceiling — SF2 never clips a composition.

## 3. Role

accent, stab, rhythm, punctuation, texture, lead — the punctuation voice:
downbeat hits, drop stabs, sfz smashes, rhythmic hit patterns, riser
bottoms. NOT a pad/harmony voice (no sustain), NOT a bass voice. Polyphonic
patch but idiomatically MONOPHONIC (one hit at a time).

## 4. Synthesis engine (musicom)

| Priority | Engine | Recipe |
|---|---|---|
| 1 (primary) | **Additive** (`sound/synthesis/additive.py`) | `ADDITIVE_HARMONICS["orchestra_hit"]` = [1.0, 0.88, 0.75, 0.60, 0.45, 0.32, 0.20, 0.12]; SYNTHESIS_DEFAULTS attack 0.005 s, decay_S 0.002 (FAST collapse = one-shot), sustain_level 0.35, release 0.35, detune ±0.008, stack 3 |
| 2 | **PhaseModSynth** (`sound/synthesis/phase_mod.py`) | saw carrier, sine mod ratio 1.0, depth 3.5, attack 0.005, release 0.40, sustain 0.30 |
| 3 | **Polysynth** (`sound/synthesis/polysynth.py`) | saw stack (+6c detune, thin square sub), low-pass 3500 Hz, razor gate 0.005, decay 0.4, sustain 0.3, 3 unison |

Smoke tests: Additive stack peak 113.8 (weights normalized to sum 1.0);
PhaseModSynth stab peak 0.750.

## 5. All constants (`Synth/orchestra_hit/orchestra_hit.py`)

```python
MIDI_PROGRAM = 55
GM_NAME = "Orchestra Hit"
STEM_LABEL = "Orchestra_Hit"
RANGE_MIN = 36
RANGE_MAX = 96
SOLO_RANGE = (48, 84)
SWEET_SPOT = (55, 79)
ZONES = {"low": (36, 47), "mid": (48, 71), "high": (72, 84), "top_extension": (85, 96)}
ARTICULATIONS = {"hit": (96, 0.20), "accent": (104, 0.10), "stab": (90, 0.15),
                 "sfz": (100, 0.12), "repeat": (85, 0.25), "swell": (78, 0.5),
                 "light": (70, 0.20), "tick": (60, 0.10)}
SYNTHESIS = "additive"
ADDITIVE_HARMONICS = {"orchestra_hit": [1.0, 0.88, 0.75, 0.60, 0.45, 0.32, 0.20, 0.12]}
SYNTHESIS_DEFAULTS = {"instrument": "orchestra_hit", "attack": 0.005, "release": 0.35,
                      "sustain_level": 0.35, "decay_S": 0.002, "detune": 0.008, "stack": 3}
FM_DEFAULTS = {"carrier_shape": "saw", "mod_shape": "sine", "mod_freq_ratio": 1.0,
               "mod_depth": 3.5, "attack": 0.005, "release": 0.40, "sustain_level": 0.30}
POLYSYNTH_DEFAULTS = {"osc1_waveform": "saw", "osc2_waveform": "saw", "osc2_detune_cents": 6.0,
                      "osc3_waveform": "square", "osc3_level": 0.25, "filter_cutoff": 3500.0,
                      "filter_resonance": 0.3, "filter_env_amount": 0.3, "env_attack": 0.005,
                      "env_decay": 0.4, "env_sustain": 0.3, "env_release": 0.3, "unison_voices": 3}
REVERB_TAIL = 1.8
EQ_BODY = (300, -2.5)
EQ_PRESENCE = (2500, 2.5)
EQ_AIR = (9000, 1.0)
PAN = 0.0
midi_to_freq(midi) = 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## 6. Registration proof

`instrument_registry.py` changes:
- `_INSTRUMENT_MODULES["Synth.orchestra_hit.orchestra_hit"] = "orchestra_hit"`
- `ORCHESTRA_HIT = ALL_INSTRUMENTS["orchestra_hit"]` convenience constant
- `registry_table()` role row for "orchestra hit"
- `__main__` verification block

Registry run (`/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`,
exit 0 — full table + verification):

```
| Synth | Orchestra Hit | 55 | 36–96 | accent, stab, rhythm, punctuation, texture, lead |
...
=== Orchestra Hit (GM55) ===
  ORCHESTRA_HIT.midi_program = 55 (should be 55)
  by_name('orchestra hit') = <Instrument Orchestra Hit (family=Synth, program=55, range=36-96)>
  by_program(55) = <Instrument Orchestra Hit (family=Synth, program=55, range=36-96)>
  ORCHESTRA_HIT.in_sweet_spot(67) = True
  ORCHESTRA_HIT.in_sweet_spot(24) = False
  ORCHESTRA_HIT.range_min = 36 ORCHESTRA_HIT.range_max = 96
  ORCHESTRA_HIT.stem_label = 'Orchestra_Hit'
  ORCHESTRA_HIT.synthesis = 'additive'
  ORCHESTRA_HIT.synthesis_defaults = {'instrument': 'orchestra_hit', 'attack': 0.005,
  'release': 0.35, 'sustain_level': 0.35, 'decay_S': 0.002, 'detune': 0.008, 'stack': 3}
```

Full output archived: `_test/registry_out_orchestra_hit.txt` (91-table rows incl. new row).

## 7. Verification results (end-to-end)

Script: `_test/verify_orchestra_hit.py` (registry-import pattern; SOLO render).
Output archived: `_test/verify_orchestra_hit_out.txt`.

| Check | Result |
|---|---|
| Registry import | `by_name('orchestra hit')` ✓, `by_program(55)` ✓, `ORCHESTRA_HIT is ALL_INSTRUMENTS['orchestra_hit']` ✓ |
| Composition | UnitMatrixComposer, 1 bar × 1 section, 104 bpm, Orchestra Hit SOLO ch0 + Drums ch9 context |
| Zero-drift | **True (OK)** |
| MIDI | `_test/orchestra_hit_test.mid` — **205 bytes** (> 40 ✓) |
| WAV (solo, FluidR3 via discover_soundfont) | `_test/orchestra_hit_test.wav` — **851,500 bytes** (> 40 ✓) |
| Spectral buzz 4–8 kHz | **2.4%** (OK, no comb-filtering — single voice, single patch) |
| Stem label | `GM_PROGRAMS[55]` = "Orchestra Hit" → `track00_Orchestra_Hit.wav` on disk (851,500 B) + `track01_Drums.wav` (835,628 B) |
| SF2 preset | FluidR3 preset 55 = "Orchestra Hit" (exact match, **no quirk**) |
| Engine smoke | Additive stack peak 113.8; PhaseModSynth stab peak 0.750 |
| Pitch sweep | 6/6 notes audible (36–96), no gaps, smooth rolloff 1345 → 374 RMS |

## 8. Quirks found

1. **One-shot quirk (the big one)**: the FluidR3 patch is a sample — it
   fires once per note-on and decays; a long MIDI note does NOT sustain
   (the muted-guitar lesson, GM28). Composition jobs must write short
   strikes (≤ 0.2 bar) and let the decay + reverb work. Verified: the
   sweep renders are all audible regardless of gate length, but the tone
   collapses after the sample's natural decay (~0.5–1.5 s).
2. **Stem label**: GM_PROGRAMS[55] = "Orchestra Hit" → `Orchestra_Hit` —
   matches STEM_LABEL and FluidR3 preset exactly, **no routing quirk**
   (contrast GM74 Flute → "Recorder", GM109 → "Bag pipe", GM111 →
   "Shanai").
3. **by_name spelling**: the GM2 alternate name "Orchestral Hit" does NOT
   resolve via `by_name` (GM_NAME is the canonical "Orchestra Hit");
   either spelling is documented, but lookups use "orchestra hit".
4. **Channel quirk**: melodic channel (0–9) with program 55 — channel 9
   triggers the drum-kit map + `Acoustic_Grand_Piano` program-0 fallback
   label (timpani lesson).
5. **Enum**: `MidiInstrument` has NO orchestra-hit constant (10-instrument
   legacy enum) — use raw GM 55; the registry is the full KB.
6. **Idiomatic monophony**: the patch is polyphonic but the instrument is
   one tutti strike at a time — stacked simultaneous hits smear into
   noise. Sparse use = maximum impact.
7. **No unison doubling**: layering with another melodic patch on the same
   pitches = comb-filter buzz (2026-09-01 lesson). Octave doubling or
   hard L/R double-hit of the SAME patch is the width trick.

## 9. Files

- `Synth/orchestra_hit/instrument.md` — full research reference
- `Synth/orchestra_hit/orchestra_hit.py` — importable constants
- `Synth/orchestra_hit/REPORT.md` — this report
- `instrument_registry.py` — registered (module dict + ORCHESTRA_HIT + role row + verification)
- `registry.md` — changelog entry + Registry table row + stem-label quirks row
- `_test/verify_orchestra_hit.py`, `_test/verify_orchestra_hit_out.txt`,
  `_test/registry_out_orchestra_hit.txt`, `_test/orchestra_hit_test.mid`,
  `_test/orchestra_hit_test.wav`, `_test/stems_orchestra_hit/` — proof artifacts
