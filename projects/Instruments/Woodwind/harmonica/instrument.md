---
type: instrument
family: Woodwind
name: Harmonica
midi_program: 22
gms: "Harmonica"
range_min: 48
range_max: 96
solo_range: [60, 84]
role: [lead, melody, ornament, accent, harmony]
synthesis: [phase_mod, additive, modal]
---

# Harmonica

## MIDI / GM

- **Program**: 22 (GM1 Harmonica)
- **Channel**: melodic channel (0-9); monophonic lead but capable of
  limited chords via tongue-blocking (octave splits, doublestops
  across adjacent holes)
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 22 =
  "Harmonica" (TimGM6mb fallback also has preset 22 = "Harmonica").
  RenderPipeline stem label: GM_PROGRAMS[22] = "Harmonica" →
  `trackXX_Harmonica.wav` — matches exactly, **no quirk**.
- **GM1 identity**: program 22 covers both the 10-hole diatonic
  (blues/folk/rock, C4-C6) and the 12-16 hole chromatic (classical/jazz,
  C3-C7). The GM patch is a chromatic harmonica — all notes are available.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–96 | C3–C7 | chromatic harmonica (16-hole Hohner Super 64x) |
| Low | 48–59 | C3–B3 | chromatic bass reeds — dark, breathy, soft projection |
| Middle | 60–76 | C4–E5 | primary melodic register — diatonic core, strongest reeds |
| High | 77–89 | F5–F6 | bright, cutting — blues/wailing territory, overblow zone |
| Extreme | 90–96 | G6–C7 | thin, piercing — low reed response, chromatic top |

The sweet spot is 64–79 (E4–G6): the richest reed projection with
the most expressive bend and timbre control. Diatonic harps typically
cover 60–84 (C4–C6) in a single key; chromatic harps cover the full
48–96 span.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Blow (exhale) | 65–80 | full note | standard exhaled note — default attack, full reed |
| Draw (inhale) | 60–75 | full note | inhaled note — slightly softer onset, different reed |
| Staccato (tongue-stop) | 70–85 | 1/8–1/4 | tongue articulates a short pulse — percussive, clean |
| Shakes (hand tremolo) | 78–92 | 1/4–1/2 | rapid hand cupping/un-cupping — wah-wah amplitude mod |
| Bend (pitch drop) | 58–70 | 1–2× | draw-bend down 1-3 semitones — blues soul, vocal cry |
| Overblow | 85–100 | 1/4–1/3 | forced draw reed raises pitch 3-4 semitones — piercing |
| Tongue block chord | 70–80 | 1/2–full | blocked across 3-4 holes produces a split octave/fifth chord |

### Bend technique note

Diatonic harmonica bends are limited to specific notes on draw and blow:
- Draw bends (holes 1-6): drop pitch 1-3 semitones
- Blow bends (holes 7-10): drop pitch 1-2 semitones
- Overblows/overdraws: raise pitch for notes NOT in the diatonic scale

For composition: write bend notes at their target pitch with velocity in
the 58-70 range and duration 1.5-2× normal. The bend is NOT instantaneous
— allow ~200-400 ms for the full bend descent. The GM patch may not
articulate bends authentically (most SF2 patches are clean chromatic).
Use PhaseModSynth with pitch-bend modulation for authentic bends.

## Timbre DNA

- **Harmonic content**: rich even+odd harmonic spectrum (free reed =
  symmetric oscillating tongue — same physics as accordion, sax, oboe).
  Cupped hands create a resonant cavity with variable EQ (wah effect).
  Bass reeds (low register) are thicker with more odd harmonics.
- **Attack**: 1–3 ms (reed speaks instantly on breath) — fastest attack
  in the Woodwind family, tied with accordion. No breath transient.
  The breath onset has a subtle hiss at very low velocities.
- **Sustain**: breath-limited — 5-15 seconds depending on lung capacity.
  The tone is constant under steady breath pressure. Vibrato via throat
  modulation (diaphragm) or hand tremolo (wah).
- **Release**: near-instant — reeds stop immediately on breath reversal.
  Cupped hands can create a longer release if the player opens the hands
  slowly while stopping breath.
- **Noise component**: low-to-moderate — clean reed tone. Breath noise
  at the edges of the reed slot at low dynamics. Hand-rustle when
  cupping/un-cupping.
- **Vibrato**: two mechanisms:
  1. Throat/diaphragm vibrato (pitch + amplitude wobble, ~5-7 Hz) —
     classical chromatic style
  2. Hand tremolo (wah-wah amplitude modulation, ~3-8 Hz) — blues
     and folk style, via cupped hands opening/closing
- **Character**: reedy, breathy, warm, vocal — instantly evokes blues,
  folk, country, and gospel; the most vocal-like of the free reeds
  (closer to the human voice than any other reed instrument)

## Role in Arrangement

- Lead melody (mid register, 60-79) — single-note lines, blues riffs,
  folk melodies, vocal doublings
- Ornamentation (fast tongue-stops, trills, bends, shakes) — fills and
  breaks between vocal phrases
- Accent (staccato punches, overblow shrieks) — rhythmic punctuation
- Harmony (limited tongue-block chords, octave splits on adjacent holes)
  — NOT a primary chord/comping voice; use sparse doublestops / octaves
- Call-and-response with voice, guitar, or harmonica's own low/high
  register in duet
- NOT a bass/pad voice (short sustain, breathy tone, midrange-heavy)
- NOT a high-tessitura lead above G6 (79) — extreme register is thin

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**
   - A free reed is a self-sustained oscillator: a saw carrier (even+odd
     harmonics) with moderate phase modulation reproduces the reed's
     characteristic buzzy-warm tone.
   - `mod_depth: 2.5` — between flute (1.5, clean) and accordion (3.2,
     thick); reflects the harmonica's slightly softer reed buzz (smaller
     reeds, lower air pressure).
   - `attack: 0.010` — near-instant; the reed speaks on the first
     molecule of breath. Slightly faster than accordion (0.015) because
     small reeds have lower inertia.
   - `release: 0.04` — extremely fast; the reed stops on breath
     reversal. No natural decay tail.
   - **Bend simulation**: use a pitch-bend envelope during the note
     (bend = bend down 2-3 semitones over ~300 ms, then hold; unbend
     optional). The PhaseModSynth doesn't naturally bend like a real
     reed, so pitch-bend MIDI events are the practical path.

2. **Additive** (`sound/synthesis/additive.py`) — alternative
   - A harmonic stack with strong even+odd partials (free reed symmetry).
     Use ~6-8 partials with a slight amplitude wobble (LFO ~5-7 Hz) for
     the throat vibrato effect. For bend simulation, shift the partial
     frequencies down proportionally.

3. **ModalSynth** (`sound/synthesis/modal.py`) — fallback
   - Preset `'string'` gives a generic sustained tone. Loses the reedy
     buzz and breath character. Use only when PhaseModSynth is unavailable.

4. Karplus-Strong / BowedString / DrumMachine — WRONG. The harmonica
   is not plucked (no string) and not bowed (no friction). It's a
   free-reed aerophone.

### Bend simulation for composition jobs

The GM patch (FluidSynth) produces a clean chromatic sound with NO
natural bend — the GM harmonica plays all notes equally. For authentic
blues/folk harmonica parts:

- Write melodic lines in the diatonic scale of the harp key (e.g., C
  harp = C, D, E, F, G, A, B, C). Use bend notes (Eb, F#, G#, Bb)
  sparingly as passing tones.
- Pitch-bend down 1-3 semitones on draw notes (holes 1-6) or blow
  notes (holes 7-10). Use `pitchwheel` events in MIDI with a gradual
  ramp (~200-400 ms curve).
- Velocity 58-70 = bent note (breath pressure decreases as the reed
  bends down). Velocity 74+ = unbent (full pressure = sounding pitch).

## Production

- **Reverb**: room/hall 1.0–1.5 s — harmonica is a dry, close-mic'd
  instrument. The breathy reed loses definition with heavy reverb.
  A small room ambience or plate keeps the blues/folk intimacy.
  **NOTE**: REVERB_TAIL = 1.2 s is the shortest in the Woodwind family
  (next shortest: clarinet 1.5 s) — intentional, for dryness.
- **EQ**: cut 400–600 Hz (cupped-hand boxiness); presence boost 1.8–2.5
  kHz for reed clarity + bite; air shelf 6–8 kHz for breath shimmer
  and overblow sizzle.
- **Pan**: center for solo; ±0.2 for dual harmonica layering (left-right
  hand separation, or two harps in stereo).
- **Compression**: moderate to heavy — harmonica dynamics vary wildly
  with breath pressure (blow vs draw, bend vs unbend). A 4:1 ratio
  with fast attack smooths the breath transients.
- **Microphone style**: bullet mic (Shure 520) with slight overdrive /
  distortion IS the blues harmonica sound. The GM/FluidSynth sound is
  clean; composition jobs targeting authentic blues should route
  through an amp sim or mild distortion.

## Verification

- GM22 → stem `trackXX_Harmonica.wav` — pipeline label "Harmonica",
  matches exactly, **no quirk**.
- FluidR3 preset 22 = "Harmonica" (verified from phdr chunk).
- Solo render must pass the 4–8 kHz spectral gate — harmonica has a
  moderate high-frequency reed buzz (naturally bright in the high
  register) but should stay well under the 20% threshold.
- Zero-drift: sustained/articulated units end flush at BAR (terminal
  landmark).
- FluidR3 preset 22 audible across the full span (empirical RMS sweep,
  no gaps — the SF2 never clips a composition).
- Bend simulation: pitch-bend events produce a glissando effect in
  FluidSynth (no real reed model), so bends written for GM playback
  sound like a pitch wheel slide, not a reed drop. This is an accepted
  GM compromise.