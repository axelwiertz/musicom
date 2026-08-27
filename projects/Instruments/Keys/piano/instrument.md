---
type: instrument
family: Keys
name: Piano
midi_program: 1
gms: "Acoustic Grand Piano"
range_min: 21
range_max: 108
solo_range: [36, 96]
role: [harmony, melody, bass, rhythm, solo]
synthesis: [additive, phase_mod, modal]
---

# Piano (Acoustic Grand)

## MIDI / GM

- **Program**: 1 (GM1 Acoustic Grand Piano)
- **Channel**: any channel; percussive attack, sustained decay
- **FluidSynth**: TimGM6mb.sf2 renders GM1 → grand piano

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 21–108 | A0–C8 | concert piano |
| Bass | 21–47 | A0–B3 | left hand, power, rhythm |
| Mid | 48–71 | C4–B4 | chordal comping, melody |
| High | 72–108 | C5–C8 | melody, sparkle, ornaments |

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato (sustained) | 60–85 | full | smooth connection via pedal |
| Staccato | 55–75 | 1/4–1/8 | short, detached |
| Marcato | 85–105 | full, strong attack | emphasized |
| Forte chords | 90–110 | sustained | big, ringing |
| Piano chords | 40–60 | sustained | soft, intimate |
| Tremolo (octave) | 60–80 | 16th/32nd | rapid alternation |
| Glissando | 60–90 | fast run | sweeping |
| Pedal (sustain) | — | extends release | blurred resonance |

## Timbre DNA

- **Harmonic content**: fundamental + inharmonic partials, string stiffness → slight stretch
- **Attack**: 1–10 ms (hammer strike) — FAST, percussive
- **Decay**: exponential, note-dependent (bass 5–20 s, high 1–3 s)
- **Release**: pedal-controlled
- **Noise**: hammer thump (low registers), damper noise
- **Touch**: velocity → hammer velocity → brightness AND loudness (key scaling)

## Role in Arrangement

- Harmony/comping (mid register, chords)
- Melody (high register)
- Bass (low register, walking, stabs)
- Rhythm (rhythmic chords, vamp)
- Solo instrument (any register)

## Synthesis Engines (musicom)

1. **ModalSynth** preset `marimba` (close-ish, percussive decay) or custom 3-mode
   bank with inharmonic partials (freq × 1.00, 2.00, 3.01, 4.07...) — physical
   modeling
2. **PhaseModSynth** — FM piano (DX7-style), carrier sine × mod ratio ~0.5–1.0,
   fast attack
3. **Additive** (SoundWave) — drawbar-like approximation, works for electric

## Production

- **Reverb**: room/plate 1–2 s; concert hall for solo piano
- **EQ**: presence 2–5 kHz; low shelf for warmth
- **Compression**: gentle (2:1) for pop; avoid heavy
- **Pan**: stereo wide for solo, center in band

## Verification

- GM1 renders as `trackXX_Acoustic_Grand_Piano.wav` in RenderPipeline stems
- Program 0 (not 1) = drums channel 9 fallback — check channel before assigning
