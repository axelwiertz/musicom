---
type: instrument
family: Keys
name: Dulcimer
midi_program: 15
gms: "Dulcimer"
range_min: 48
range_max: 96
solo_range: [60, 89]    # C3-C7 playable, solo sweet spot C4-A6
role: [lead, melody, ornament, rhythm, harmony]
synthesis: [modal, karplus, phase_mod]
---

# Dulcimer

> **Instrument identity note**: GM15 "Dulcimer" is the **hammered dulcimer**
> (also called *cimbalom* in Eastern Europe, *santur* in Persia/India, *yangqin*
> in China) — NOT the Appalachian lap dulcimer. The hammered dulcimer is a
> struck-string zither: a trapezoidal soundboard with many wire courses
> (often doubled/quadrupled) played with small hand-held hammers. This is the
> timbre the SF2 preset and the synth presets below target. The genre-style
> KB references it under "Cimbalom (hammered dulcimer)" (Klezmer), santur
> (Middle East / Indian Classical), yangqin (Chinese), and the FM-style
> hammered-dulcimer idiom of European folk dance bands.

## MIDI / GM

- **Program**: 15 (GM1 Dulcimer — the hammered-dulcimer family; 0-indexed GM
  number matching pipeline GM_PROGRAMS[15] and FluidR3 preset 15)
- **Channel**: any melodic channel (0-9) — struck-string zither, NOT channel 9
- **MidiInstrument enum**: not exposed (enum only has 10) — use raw 15
- **FluidSynth**: FluidR3_GM.sf2 renders GM15 → `Dulcimer` (verified from phdr
  chunk; a bright hammered-dulcimer sample set)
- **Pipeline stem label**: `GM_PROGRAMS[15]` = "Dulcimer" → `trackXX_Dulcimer.wav` (no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–96 | C3–C7 | chromatic hammered dulcimer + MIDI-keyboard extension |
| Sweet spot | 62–86 | D4–D6 | primary melodic register, fullest body ring |
| Low | 48–59 | C3–B3 | bass courses — dark, long wooden-body ring |
| Mid | 60–77 | C4–F5 | melody courses — lead voice |
| High | 78–96 | F#5–C7 | treble courses — bright, thin, fast decay |

Real concert hammered dulcimers are laid out chromatically (3 octaves C3–C6
typical, 4-octave instruments to C7). The classic folk repertoire lives in
C4–C6 — the solo range above. Composition jobs can write the full 48–96
span, but keep melodic lines in the sweet spot and treat below C4 as dark
accompaniment/bass, above D6 as sparkle.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Hammer (sustain) | 68–88 | full note | standard hammer stroke, course ring + body |
| Roll (tremolo) | 60–75 | 16th/32nd repeats | fast alternating hammers, sustained illusion |
| Double/triple stroke | 70–82 | 1/8–1/4 note | repeated hammers, rhythmic figure |
| Damped (muted) | 38–52 | very short | palm/chord damp, choked dry attack |
| Accent | 90–108 | full note, strong onset | hard hammer, bright cutting emphasis |

## Timbre DNA

- **Harmonic content**: near-harmonic struck-string partials — strong
  fundamental + prominent 2nd–6th harmonics, slightly stretched on the bass
  courses (real hammered dulcimers are inharmonic at the bottom). The doubled
  courses add a subtle chorus/beating sheen.
- **Attack**: 1–3 ms (wooden hammer strike) — harder and brighter than
  marimba's soft mallet; the hammer click is part of the tone.
- **Decay**: exponential, 0.5–3.0 s — bass courses ring long over the
  soundboard, treble courses dry fast (same physics as kalimba but with
  string-like harmonic partials instead of metal-bar inharmonic ones).
- **Release**: natural decay (no sustain); note ends = string stops ringing.
- **Noise component**: hammer transient (light); the soundboard adds a warm
  wooden body — quieter body than piano.
- **Vibrato**: NONE native — any vibrato is a rolled note or a slight
  pitch-bend effect on a sustained course, not a bowed/reed wobble.

## Role in Arrangement

- Lead melody (C4–D6 sweet spot — hammered-dulcimer repertoire, folk/dance
  tunes, Klezmer cimbalom lines)
- Ornament (fast treble runs, rolls, melodic ostinati)
- Rhythm/accompaniment (repeated-note figures, "strummed" rolled chords)
- Harmony (2–4 note chords possible — dulcimers are played chordally in folk
  styles; keep voicings in the mid register)
- NOT bass (low courses too soft/boxy to anchor a mix; use double bass/tuba)
- NOT a kit/groove voice (no drum-like attack; rolls substitute for sustain)
- Doubling role: the cimbalom doubles the Klezmer violin/clarinet line an
  octave below or provides off-beat chordal punches — see the Klezmer
  freylekhs pattern KB (alternative instrument for violin lead + secunda).

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — best match (impulse excitation)
   - `ModalSynth().render_preset('string', duration, excitation='impulse')` is
     the stock approximation (harmonic series 1–8, moderate decay 4–11).
   - Refined struck-string patch (add via `render_custom`): scale the mode
     frequencies from the played note and use fast-decaying partials with a
     hard 2 ms excitation, e.g. relative modes at
     `(1.00, 1.0, 3.0), (2.00, 0.55, 5.0), (3.00, 0.30, 7.0),
      (4.00, 0.18, 9.0), (5.00, 0.12, 11.0), (6.00, 0.08, 13.0)` —
     struck string, brighter than marimba, cleaner than bell.
2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — alternative
   - Plucked-waveguide with `loop_gain=0.9975`: models the bright ring of the
     doubled treble courses (sitar-class sustain). Slightly duller attack than
     real hammers, acceptable for sustained passages.
3. **Avoid** PhaseModSynth for the primary patch (FM reads synthetic); the
   FM_DEFAULTS cheap patch (triangle carrier, 2.0× ratio) is a distant
   alternative only.

## Production

- **Reverb**: room/plate 1.0–1.5 s tail — bright folk box; keep the hammer
  attack clear (shorter than koto's 1.4 s and sitar's 2.2 s hall).
- **EQ**: cut 300–400 Hz soundboard boxiness; presence boost 3–3.5 kHz for
  hammer click + string sparkle; air shelf 8 kHz subtle (treble courses
  already bright).
- **Pan**: center (solo); slight L/R spread for ostinato/duo parts.
- **Compression**: light 2:1 — keep the transient, tame the decay tail.

## Verification

- GM15 renders as `trackXX_Dulcimer.wav` in RenderPipeline stems (label matches
  exactly, no quirk — GM_PROGRAMS[15] and FluidR3 preset 15 both "Dulcimer").
- Struck-string zither: channel 0-9 with program 15 — NOT channel 9 (ch9 would
  trigger the program-0 fallback label "Acoustic_Grand_Piano").
- FluidR3 preset 15 = "Dulcimer" (verified from phdr chunk).
- ModalSynth 'string' preset + custom struck-string modes verified in
  `_test/verify_dulcimer.py`.
