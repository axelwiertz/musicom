---
type: instrument
family: Woodwind
name: Recorder
midi_program: 74
gms: "Recorder"
range_min: 60
range_max: 100
solo_range: [72, 89]
role: [lead, melody, ornament, countermelody, accent]
synthesis: [phase_mod, air_pipe, additive]
---

# Recorder

The Renaissance and Baroque duct flute (fipple flute), the most prominent
end-blown flute in Western art music from the 14th to the 18th century.
The GM74 patch is modelled on the soprano/descant recorder in C, but the
instrument family spans eight sizes from great bass in F2 to sopranino in F5.

After near-total disuse in the Classical and Romantic periods (replaced by
the transverse flute), the recorder was revived in the 20th c. as part of
the historically informed performance movement and became the most popular
educational woodwind worldwide.

## MIDI / GM

- **Program**: 74 (GM1 Recorder, 0-indexed; GM #75 1-indexed)
- **Channel**: Melodic channel (0–8, 10–15)
- **RenderPipeline stem label**: `trackXX_Recorder.wav` ✓
  (GM_PROGRAMS[74] = "Recorder" — exact match, no quirk)
- **FluidR3_GM.sf2**: Preset 74 "Recorder" provides a clear, sweet
  fipple-flute tone with quick attack and moderate sustain.

## Range

The recorder family includes eight sizes; the GM74 patch is generic but
maps most closely to the soprano/descant recorder (C5–D7, sounding pitch).
Pitches below C5 are reachable by the alto/treble or tenor instruments.

| Zone | MIDI | Pitches | Character & Register |
|---|---|---|---|
| Full range | 60–100 | C4–E7 | Playable GM patch compass |
| Low | 60–74 | C4–D5 | Breathy, soft, hollow; authentic bass/alto register |
| Middle | 75–84 | D#5–C6 | Sweet, clear, liquid — the classic recorder voice |
| High | 85–93 | C#6–D7 | Bright, piercing, sharp articulation, Baroque brilliance |
| Altissimo | 94–100 | D#7–E7 | Thin, shrill, extreme overblown register |

- **Sweet Spot**: 76–84 (E5–C6, ~659 Hz – ~1047 Hz) — pure, sweet singing
  register with optimal projection and articulation clarity.
- **Solo Range**: 72–89 (C5–C7) — the full two-octave soprano compass,
  spanning the entire solo baroque repertoire (Handel sonatas, Telemann
  fantasias, Vivaldi concertos).

## Articulations

The recorder's key strength is articulation variety — the fipple edge
responds instantly, making single, double, triple, and flutter tonguing
all clearly audible.

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Legato | 60–75 | 1.0 | Smooth slurred phrases, minimal tonguing |
| Staccato | 55–70 | 0.2 | Crisp single-tongue "tu-tu-tu", dry point |
| Accent | 85–100 | 0.85 | Sharp sforzando tongue attack |
| Double tongue | 65–78 | 0.07 | Rapid "tu-ku-tu-ku", Baroque fast passage |
| Triple tongue | 65–78 | 0.06 | "tu-tu-ku" pattern, Vivaldi concertos |
| Flutter tongue | 60–72 | 1.0 | Guttural rolled-R "frullato" |
| Breath/soft | 45–55 | 0.85 | Airy pianissimo, delicate, ethereal |
| Trill | 65–75 | 0.5 | Rapid finger trill (adjacent holes) |

## Timbre DNA

- **Harmonic spectrum**: Odd-harmonic dominant (1f, 3f, 5f, 7f) when the
  fipple edge sits in the centre of the airjet — giving the characteristic
  hollow, sweet, "pure" recorder tone. Even harmonics emerge when the
  edge is off-centre (the Baroque "voicing" adjustment).
- **Envelope**: Near-instant attack (10–30 ms) — the fipple speaks the
  instant air pressure reaches the labium, faster than any reed or flute
  embouchure. No transient noise — the fipple produces the tone directly.
- **Fundamental purity**: The recorder's tone is acoustically cleaner than
  the flute — the fipple generates a purer sine-like waveform at low
  dynamic levels, with harmonics increasing with breath pressure.
- **No vibrato**: Baroque recorder uses finger vibrato (flattement) or
  breath vibrato (flauto vibrato) — not diaphragm vibrato as in modern
  flute; GM patch includes natural modulation.

## Role in Arrangement

- **Lead / Melody**: Solo baroque sonata lines, pastoral and bird-like
  melodies (Handel "Acis and Galatea", Purcell, Bach Brandenburg 2 & 4).
- **Ornamentation**: Trills, mordents, turns, appoggiaturas, and
  divisions — the instrument's agility is its greatest asset.
- **Countermelody**: Descant lines above strings or voices, Renaissance
  consort part (SATB recorder consort uses four sizes).
- **Accent**: High-register piercing notes, Baroque fanfares.
- **NOT harmony**: Monophonic wind instrument — no chords.
- **NOT bass**: Alto/bass recorders exist but the GM patch is soprano.

## Synthesis Engines (musicom)

1. **PhaseModSynth (`phase_mod`) — PRIMARY**:
   - Carrier: sine, Modulator: sine
   - Mod ratio: 1.0, Mod depth: 1.5
   - Fast attack (0.03 s), short release (0.08 s)
   - Produces the pure, sweet, fipple-flute tone with clean articulation.

2. **AirPipe (`air_pipe`) — PHYSICAL MODEL**:
   - Cylindrical open pipe aerophone (`stopped=False`)
   - `length_scale=0.45` (soprano recorder ~33 cm)
   - Moderate wind pressure (`pressure=0.60`) — fipple generates tone at
     low pressure, unlike the high jet pressure of the transverse flute.
   - Best match for idiomatic recorder physics.

3. **AdditiveSynth (`additive`)**:
   - Odd-harmonic stack: f0 (1.0), 3f (0.40), 5f (0.22), 7f (0.10)
   - Near-instant attack (0.02 s), fast release (0.06 s)

## Production Defaults

- **Reverb Tail**: 1.6 s (intimate chamber/room — the intimate Baroque
  sound benefits from close clarity; avoid large hall reverb that would
  blur the pure fipple tone).
- **EQ**:
  - Body: −1.5 dB at 600 Hz (reduce slight duct/body box resonance)
  - Presence: +2.5 dB at 3 kHz (articulation clarity)
  - Air: +1.5 dB shelf at 9 kHz (fipple breath shimmer)
  - High-pass: 18 dB/oct rolloff below 300 Hz (out-of-range rumble)
- **Pan**: −0.1 (slightly left — standard classical woodwind section
  seating; Baroque consorts place the instrument centre).

## FluidSynth & Pipeline Behavior

- **GM Program**: 74
- **RenderPipeline Stem**: `trackXX_Recorder.wav` (pipeline
  GM_PROGRAMS[74] = "Recorder" — exact match, no quirk)
- **FluidR3_GM.sf2**: Preset 74 is named "Recorder" with sweet clear
  fipple tone across the full velocity range.

## Quirks

- **Monophonic line instrument**: The recorder is a mono-line wind
  instrument — NO chords or harmony; all compositions should write
  single-note melodic lines. The only multi-note possibility is the
  historic "four-part consort" using four different sizes.
- **Pitch standard**: The soprano recorder sounds at pitch (C5–D7).
  Alto recorder is in F (transposing, sounds F4–G6) but the GM patch
  maps to soprano — all MIDI is written at sounding pitch.
- **No dynamics by breath**: The fipple flute has limited dynamic range
  — it cannot play truly loud (overblows) or truly soft (fipple cuts
  off). Velocity simulation substitutes as a creative affordance.