# REPORT — Synth Voice (GM54) added 2026-10-31

Nightly instrument research job. New instrument added to the musicom
Instruments reference library, fully registered in `instrument_registry.py`.

## Instrument

- **Name**: Synth Voice (GM54)
- **Family**: Synth (third member — alongside synth_pad GM88, synth_brass_1 GM62)
- **GM**: 54 "Synth Voice" (GM1 spec; Roland GS "Synth Voice", Yamaha XG
  "SynthVoice"). The classic analog/digital synthesizer "choir": detuned
  saw/square oscillator stack through a vowel (formant) filter, slow breathy
  attack, delayed LFO vibrato. VP-330 choir / CS-80 "voice" / Korg M1 voice
  programs; Vangelis *Blade Runner*, Jarre *Oxygène*, synthwave leads.
- **Why this one**: remaining candidate from the Oct-26 probe sweep
  (`_test/_cand_54.mid/.wav` exists; GM52 Choir Aahs + GM62 Synth Brass 1
  were already added from that sweep, 54/55/82–87 remained). GM54 fills the
  Synth family's melodic-lead gap (Synth family was pad + brass only) and is
  free in the KB — no `by_program` collision (choir.py docstring confirms
  "GM54 = Synth Voice ... No by_program collision").
- **Choice rationale vs alternatives**: GM55 Orchestra Hit (one-shot stab —
  less useful for sustained composition jobs), GM82–87 leads (8 near-duplicate
  lead patches; Synth Voice is the most distinct/iconic). World sitar/koto/
  shamisen already exist — World family is done.

## Files

| File | Purpose |
|---|---|
| `Synth/synth_voice/instrument.md` | full research (YAML frontmatter + sections) |
| `Synth/synth_voice/synth_voice.py` | importable constants |
| `Synth/synth_voice/REPORT.md` | this report |
| `_test/verify_synth_voice.py` | verification script (SOLO render) |
| `_test/synth_voice_test.mid/.wav`, `_test/stems_synth_voice/` | artifacts |
| `_test/_sv_sweep_*.mid/.wav` | empirical pitch sweep artifacts |

## Program / Range / Role

- **Program**: 54 (raw GM; `MidiInstrument` enum has NO synth-voice constant —
  legacy 10-instrument, 1-based enum — use raw 54; registry is the full KB)
- **Range**: 36–96 (C2–C7 idiomatic writing band; patch plays full keyboard —
  empirical sweep 8/8 notes audible 24–108, no gaps, RMS 1308–2067)
- **Sweet spot**: 55–79 (G3–G5 — vocal-register heart)
- **Solo range**: 60–84 (C4–C6 — the "singing" band)
- **Zones**: low 36–55 (dark pad bottom), mid 56–71 (workhorse), high 72–84
  (voice-lead top), top_extension 85–96 (shimmer)
- **Role**: lead, melody, harmony, pad, countermelody, accent — NOT bass,
  NOT a real-choir substitute (GM52), NOT a stab patch (slow attack)

## Constants (synth_voice.py)

```python
MIDI_PROGRAM = 54
GM_NAME = "Synth Voice"
STEM_LABEL = "Synth_Voice"
RANGE_MIN = 36
RANGE_MAX = 96
SOLO_RANGE = (60, 84)
SWEET_SPOT = (55, 79)
ZONES = {"low": (36, 55), "mid": (56, 71), "high": (72, 84), "top_extension": (85, 96)}
ARTICULATIONS = {"ah": (72, 1.0), "legato": (70, 1.0), "swell": (60, 1.15),
                 "marcato": (85, 0.85), "staccato": (74, 0.30), "vibrato": (76, 1.0),
                 "accent": (88, 0.9), "decay_fade": (58, 1.0)}
SYNTHESIS = "phase_mod"
FM_DEFAULTS = {"carrier_shape": "saw", "mod_shape": "sine", "mod_freq_ratio": 1.0,
               "mod_depth": 2.6, "attack": 0.25, "release": 0.35, "sustain_level": 0.85}
SYNTHESIS_DEFAULTS = {"instrument": "synth_voice", **FM_DEFAULTS}
ADDITIVE_DEFAULTS = {"harmonic_count": 8,
                     "harmonic_weights": [1.0, 0.78, 0.62, 0.55, 0.40, 0.28, 0.18, 0.10],
                     "attack": 0.25, "release": 0.35}
POLYSYNTH_DEFAULTS = {"osc1_waveform": "saw", "osc2_waveform": "saw",
                      "osc2_detune_cents": 6.0, "osc3_waveform": "square",
                      "osc3_level": 0.2, "filter_cutoff": 3200.0,
                      "filter_resonance": 0.6, "filter_env_amount": 0.4,
                      "env_attack": 0.25, "env_decay": 0.3, "env_sustain": 0.85,
                      "env_release": 0.35, "unison_voices": 3}
REVERB_TAIL = 2.8
EQ_BODY = (350, -2.5)
EQ_PRESENCE = (2400, 2.0)
EQ_AIR = (8500, 1.5)
PAN = 0.0
```

## Synthesis engine

1. **PhaseModSynth** (primary) — saw carrier + sine modulator ratio 1.0,
   depth 2.6 (between synth_pad 2.0 and synth_brass_1 3.2: voice is softer
   than a horn, edgier than a pad), attack 0.25 s (the breath), release
   0.35 s, sustain 0.85. Smoke: G4 peak 0.768, sustain/peak 0.282 (holds).
2. **Additive** (secondary) — formant-weighted harmonic stack (choir.py
   precedent), weights normalized to sum 1.0 for `apply_overtones`. Smoke:
   envelope peak 1.000.
3. **Polysynth** (tertiary) — saw+square stack, 6-cent detune, low-pass
   3200 Hz res 0.6 (vowel peak), slow gate, 3 unison voices. Smoke: peak
   1.439.

## Registration proof (instrument_registry.py)

`_INSTRUMENT_MODULES` += `"Synth.synth_voice.synth_voice": "synth_voice"`;
convenience constant `SYNTH_VOICE`; `registry_table()` role mapping
`synth voice → lead, melody, harmony, pad, countermelody, accent`; `__main__`
verification block. Registry run (`python instrument_registry.py`, exit 0):

```
| Synth | Synth Voice | 54 | 36–96 | lead, melody, harmony, pad, countermelody, accent |

=== Synth Voice (GM54) ===
  SYNTH_VOICE.midi_program = 54 (should be 54)
  by_name('synth voice') = <Instrument Synth Voice (family=Synth, program=54, range=36-96)>
  by_name('SYNTH VOICE') = <Instrument Synth Voice (family=Synth, program=54, range=36-96)>
  by_program(54) = <Instrument Synth Voice (family=Synth, program=54, range=36-96)>
  SYNTH_VOICE.in_sweet_spot(67) = True
  SYNTH_VOICE.in_sweet_spot(24) = False
  SYNTH_VOICE.range_min = 36 SYNTH_VOICE.range_max = 96
  SYNTH_VOICE.stem_label = 'Synth_Voice'
```

Full table + verification output: `_test/registry_out_synth_voice.txt` (397
lines, 81 instruments, 76 unique programs now covered).

## Verification results (verify_synth_voice.py — ALL CHECKS PASSED)

| Check | Result |
|---|---|
| Registration (by_name / by_program / SYNTH_VOICE) | ✓ `SYNTH_VOICE is by_name("synth voice")`, `by_program(54)` |
| Zero-drift (UnitMatrixComposer, 1 bar × 1 section, 2 voices) | ✓ `True (OK)` |
| MIDI export | 155 bytes (> 40) |
| SoundFont | FluidR3_GM.sf2 via `discover_soundfont()` |
| WAV (SOLO voice 0 — no unison doubling) | 971,052 bytes (> 40) |
| Spectral 4–8 kHz buzz | 15.7% — OK (≤ 20% gate; bright patch, real formant energy) |
| Stem label (pipeline GM_PROGRAMS[54]) | "Synth Voice" — matches STEM_LABEL, **no quirk** |
| FluidR3 preset 54 (phdr) | "Synth Voice" — exact match, **no quirk** |
| RenderPipeline stems | `track00_Synth_Voice.wav` (971,052 B) + `track01_Drums.wav` (706,092 B) |
| Engine smoke (PhaseMod / Additive / Polysynth) | peaks 0.768 / 1.000 / 1.439, sustain holds |
| Empirical pitch sweep (24–108) | 8/8 audible, no gaps (RMS 1308–2067) |
| Spectral centroid | C4 = 4626 Hz, C6 = 6068 Hz (genuinely bright voice) |

## Quirks found

- **Stem label**: NO quirk — GM_PROGRAMS[54] = "Synth Voice" and FluidR3
  preset 54 = "Synth Voice" match exactly (contrast GM74 Flute → "Recorder",
  GM109 → "Bag pipe", GM111 → "Shanai").
- **Enum**: `MidiInstrument` has NO synth-voice constant (10-instrument
  legacy enum, 1-based) — raw GM 54 required; registry is the full KB.
- **Channel**: melodic channel 0–9; ch9 with program 54 → drum map + program-0
  fallback label `Acoustic_Grand_Piano` (known ch9 quirk).
- **Brightness**: spectral centroid C4 = 4626 Hz — much brighter than the
  sampled choir (GM52); the 4–8 kHz buzz band carries real formant energy
  (15.7% vs synth brass 2.6%) but passes the 20% gate. EQ_AIR is a gentle
  +1.5 dB shelf — never a 8 kHz cut (that would dull the vowel).
- **Slow attack**: staccato notes bloom into the next — write stabs with a
  gap (documented in instrument.md + changelog).
- **Additive API**: `apply_overtones` requires weights summing to 1.0
  (normalized in the verify script; documented choir/synth_pad precedent).
- **GM54 is free in the KB**: GM53 (human_voice stand-in) and GM55 (future
  candidate) are distinct — no collisions.
