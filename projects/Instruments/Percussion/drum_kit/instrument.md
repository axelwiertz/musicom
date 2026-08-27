---
type: instrument
family: Percussion
name: Drum Kit
midi_program: 0
gms: "Channel 10 (percussion)"
range_min: 35
range_max: 81
role: [rhythm, groove, accent]
synthesis: [noise, phase_mod, modal, additive]
---

# Drum Kit (GM Percussion)

## MIDI / GM

- **Channel**: 9 (0-indexed) = GM Channel 10 percussion
- **Program**: any (channel 9 overrides); use program 0
- **Mapping**: MidiPercussion enum in `structures/instrument.py`

## Drum Map (MIDI note → part)

| MIDI | Part | MidiPercussion constant |
|---|---|---|
| 35 | Acoustic Bass Drum | `BASS_DRUM` |
| 38 | Acoustic Snare | `ACOUSTIC_SNARE` |
| 39 | Hand Clap | `HAND_CLAP` |
| 42 | Closed Hi-Hat | `CLOSED_HI_HAT` |
| 45 | Low Tom | `LOW_TOM` |
| 47 | Mid Tom | `MID_TOM` |
| 49 | Crash Cymbal | `CRASH_CYMBAL` |
| 50 | High Tom | `HIGH_TOM` |
| 51 | Ride Cymbal | `RIDE_CYMBAL` |
| 56 | Cowbell | `COWBELL` |
| 70 | Maracas | `MARACAS` |
| 75 | Claves | `CLAVES` |
| 76 | Woodblock | `WOODBLOCK` |

## Kit Function Map

| Role | Part | Pattern | Velocity |
|---|---|---|---|
| Downbeat | Kick | beats 1, 2, 3, 4 (four-on-floor) | 95–110 |
| Backbeat | Snare | beats 2 & 4 | 85–100 |
| Pulse | Closed hat | 8th or 16th notes | 55–75 |
| Fill | Toms | bar-end fills | 70–90 |
| Accent | Crash | section starts | 90–105 |
| Shimmer | Ride | sustained pulse | 60–80 |

## Timbre DNA

| Part | Attack | Decay | Spectral |
|---|---|---|---|
| Kick | 1–5 ms | 100–400 ms | 40–120 Hz fundamental + click 2–4 kHz |
| Snare | 1–3 ms | 100–250 ms | noise 1–8 kHz + 180–250 Hz tone |
| Hat | 1–2 ms | 30–80 ms | noise 4–12 kHz |
| Toms | 1–3 ms | 150–400 ms | 80–300 Hz pitch drop |
| Crash | 1–2 ms | 1–3 s | noise broadband |
| Ride | 1–2 ms | 300–800 ms | 4–8 kHz ping |

## Role in Arrangement

- Rhythm foundation (groove, pulse)
- Accent (section transitions)
- Dynamics (fills, build-ups)
- NOT melodic (except tuned toms)

## Synthesis Engines (musicom)

1. **DrumMachine** (`sound/effects/tape_delay.py`) — LM-7 style; default
   synthesized kick/snare/hat samples; `play_pattern(pattern, bars=, volume=)`
2. **ModalSynth** preset `drum` — low resonant modes, fast decay
3. **PhaseModSynth** — kick: carrier sine with pitch drop (150→40 Hz)
4. **Noise + filter** — hat/snare via highpassed noise

## Production

- **Compression**: MultibandCompressor per-band (punch) — 2–3 dB reduction
- **EQ**: kick boost 60–100 Hz; snare 200 Hz + 3 kHz; hat high shelf
- **Reverb**: minimal (room 0.3–0.5 s) or none; snares love a touch
- **Pan**: hats slight R, toms L-R, kick/snare center

## Verification

- Channel 9 stem renders as `trackXX_Acoustic_Grand_Piano.wav` in
  RenderPipeline (program-0 fallback label quirk — the stem is drums, not piano)
- Rhythm alignment: onsets must be on grid (`x % step16 == 0`); see
  genre-composition-patterns pitfall on EuclideanCore phase shift
