---
type: instrument
family: World
name: Kalimba
midi_program: 108
gms: "Kalimba"
range_min: 48
range_max: 96
solo_range: [60, 84]    # C3-C7 playable, solo sweet spot C4-C6
role: [lead, melody, ornament, drone, harmony]
synthesis: [karplus, modal]
---

# Kalimba

## MIDI / GM

- **Program**: 108 (GM2 Kalimba)
- **Channel**: any melodic channel (0-9) — melodic lamellophone, NOT channel 9
- **FluidSynth**: FluidR3_GM.sf2 renders GM108 → "Kalimba" (preset name matches
  exactly, verified from phdr chunk)
- **Pipeline stem label**: `GM_PROGRAMS[108]` = "Kalimba" → `trackXX_Kalimba.wav` (no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–96 | C3–C7 | extended/treble kalimbas; 17-note core C4–E6 |
| Sweet spot | 62–81 | D4–A6 | primary melodic register, fullest tine ring |
| Low | 48–59 | C3–B3 | extended bass tines — dark, long wooden-box ring |
| Mid | 60–76 | C4–E6 | the classic 17-note body — lead voice |
| High | 77–96 | F6–C7 | treble tines — bright, thin, plinky, fast decay |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Pluck (sustain) | 65–85 | full note | standard thumb stroke, tine ring + box resonance |
| Roll (tremolo) | 60–72 | 16th/32nd repeats | rapid alternating thumbs, sustained illusion |
| Double/triple stroke | 68–80 | 1/8–1/4 note | repeated plucks, rhythmic figure (mbira style) |
| Damped (muted) | 40–55 | very short | thumb rests on tine, choked dry attack |
| Accent | 90–105 | full note, strong attack | hard nail strike, bright sparkle |

## Timbre DNA

- **Harmonic content**: strong fundamental + high inharmonic partials — struck
  metal tines (like a small music-box/marimba hybrid). Fundamental-dominant,
  upper partials die fastest.
- **Attack**: 1–3 ms (thumb/nail strike) — soft, rounder than marimba, no
  mallet click
- **Decay**: exponential, 0.8–3.0 s — low tines ring long (resonator box),
  high tines dry fast
- **Release**: natural decay (no sustain); note ends = tine stops ringing
- **Noise component**: thumb/nail transient, very low; the wooden resonator
  box adds warmth
- **Vibrato**: NONE native — any vibrato is rolled notes, not pitch bend

## Role in Arrangement

- Lead melody (C4–C6 sweet spot — kalimba repertoire, thumb-piano ensembles)
- Ornament (high-register plinky fills, rolls, melodic ostinati)
- Drone/pulse (repeated thumb patterns, interlocking parts à la mbira)
- Harmony (2–4 note chords possible — kalimbas are often played chordally;
  keep voicings in the mid register)
- NOT bass (low tines too soft/boxy to anchor a mix; use double bass/tuba)
- NOT rhythm-section groove (no kit-like attack; rolls substitute for sustain)

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — best match
   - Plucked-waveguide loop with the kalimba's moderate damping:
     `loop_gain=0.9940` — rings clearly (above the dull 0.990 control) but
     shorter than sitar (0.9975) / koto (0.9970): metal tines decay faster
     than sympathetic-string instruments.
   - `width=0.40` — narrow stereo spread, intimate solo voice.
   - `karplus_strong(pitch, dur, vel, loop_gain)` renders the tine strike
     (2-sample noise burst = thumb transient) + decaying partials.
2. **ModalSynth** (`sound/synthesis/modal.py`) — fallback, `preset('bell')`
   - Struck metal bar = inharmonic modes: the 'bell' preset (fundamental +
     inharmonic partials) approximates kalimba tines; scale mode
     frequencies by the played note. 'marimba' is the softer wooden-box
     variant.
3. **Avoid** PhaseModSynth for the primary patch (FM reads synthetic);
   the FM_DEFAULTS cheap patch (sine carrier, 3.7× ratio) is a distant
   alternative only.

## Production

- **Reverb**: room/hall 1.5–2.0 s tail (wooden-box warmth; keep the tine
  attack clear — shorter than sitar's 2.2 s darbar hall)
- **EQ**: cut 400–500 Hz boxiness; presence boost 3–4 kHz for tine sparkle;
  air shelf 7–9 kHz subtle (high tines already bright)
- **Pan**: center (solo); slight L/R spread for ostinato layers/duos
- **Compression**: light 2:1 — keep the transient, tame the decay tail

## Verification

- GM108 renders as `trackXX_Kalimba.wav` in RenderPipeline stems (label matches
  exactly, no quirk — see registry quirks table)
- Karplus-Strong with `loop_gain=0.9940` (vs dull 0.990 control): ring tail
  clearly audible, shorter than sitar/koto — matches metal-tine physics
- Melodic lamellophone: channel 0-9 with program 108 — NOT channel 9 (ch9
  would trigger the program-0 fallback label "Acoustic_Grand_Piano")
- FluidR3 preset 108 = "Kalimba" (verified from phdr chunk)
