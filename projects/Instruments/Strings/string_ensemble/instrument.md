---
type: instrument
family: Strings
name: String Ensemble 1
midi_program: 48
gms: "String Ensemble 1"
range_min: 28
range_max: 96
solo_range: [53, 89]
role: [harmony, pad, melody, countermelody, accent]
synthesis: [additive, bowed, phase_mod, modal]
---

# String Ensemble 1

## MIDI / GM

- **Program**: 48 (GM1 String Ensemble 1)
- **Channel**: melodic channel (0–9); sustained bowed string SECTION
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 48 = "Strings"
  (TimGM6mb fallback preset 48 = "String Ensemble 1"). RenderPipeline stem
  label: GM_PROGRAMS[48] = "String Ensemble 1" → `trackXX_String_Ensemble_1.wav`
  — matches exactly, **no quirk** (SF2 one-word name "Strings" is cosmetic
  only, no routing impact).
- **Enum note**: `structures/instrument.py` `MidiInstrument.STRING_ENSEMBLE =
  49` is the legacy off-by-one — 49 is actually String Ensemble 2 (FluidR3
  "Slow Strings"). The registry is the full KB; use GM48 (String Ensemble 1,
  the universal section pad), NOT the enum's 49.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 28–96 | E1–C7 | whole string section (contrabass → violin top) |
| Low | 28–47 | E1–B2 | contrabass/cello — pad bottom, weight, roots |
| Mid | 48–71 | C3–B4 | viola/cello — primary harmonic pad body |
| High | 72–96 | C5–C7 | violin top — melody, filigree, cutting accents |

Empirical FluidR3 pitch sweep (RMS, notes 24–108 step 6): preset 48 audible
24–96 (13/13 notes, RMS 0.048–0.089, no gaps), SILENT at 102+ (patch
ceiling — never write above C7=96). The SF2 patch plays the full GM span,
so it never clips a composition.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 75–90 | full | long section bow — the pad default |
| Legato | 70–80 | full | portato overlap, seamless melodic line |
| Marcato | 85–95 | 0.8× | heavy accented bow — downbeat emphasis |
| Staccato | 60–75 | 1/4 | short separated bows — rhythmic section |
| Spiccato | 65–80 | 1/8 | bouncing bow — light rhythmic texture |
| Tremolo | 65–80 | 1/16th | rapid bow changes — tension/underscore staple |
| Sforzando | 90–100 | 0.9× | fp accent — hit then settle |
| Accent | 88–96 | 0.9× | hard bow dig — punch |

## Timbre DNA

- **Harmonic content**: dense near-harmonic stack (section mass = many
  slightly-detuned bowed strings per note); strong lower-mid body, smooth
  harmonic rolloff — a "wall of sound" pad, not a single line
- **Attack**: 0.3–0.6 s (section bows take time to speak) — the slow onset
  IS the pad identity; staccato/marcato override it
- **Decay/sustain**: continuous while bowed — sustain pedal on, no natural
  decay; release = bows lift (~0.3–0.4 s)
- **Vibrato**: section-wide, ensemble detune (±0.3–0.6%) rather than
  solo vibrato depth
- **Character**: warm, massive, smooth, slightly "shimmering"; the default
  Hollywood/cinematic pad voice

## Role in Arrangement

- **Pad** (primary — orchestration.md's "Strings (sustained)" for the Pad
  role, previously a documented role with NO instrument behind it)
- Harmony — sustained chords under a lead (the section comping voice)
- Melody / countermelody — high register (72–96) cuts like solo violin
  without the solo personality
- Accent — marcato/sforzando downbeats, cinematic hits
- Bass — low register (28–47) as a bowed-section bass alternative (cello/
  contrabass mass); thinner than dedicated bass but valid for pads
- NOT a rhythm voice — use pizzicato_strings (GM45) for plucked rhythm

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py`, SoundWave) — **primary**.
   The section IS a detuned harmonic stack; the organ entry proved the
   engine on a sustained keyboard voice. Use `ADDITIVE_HARMONICS`
   `section_full` [1.0, 0.9, 0.7, 0.5, 0.35, 0.25, 0.18] with slow attack
   (0.35 s) and 3 detuned voices per note (±0.006) for the section chorus.
2. **BowedString** (`sound/synthesis/bowed.py`, SP-024) — single-string
   alternative. Models ONE bowed string, so it gives a solo-string tone,
   not section mass; stack 4–8 detuned renders for a section approximation
   (BOWED_DEFAULTS: bow_velocity 0.2, bow_force 1.5, noise 0.01).
3. **PhaseModSynth** — cheap string-machine: saw carrier, ratio 1.0,
   depth 1.8, attack 0.05 — the 70s ensemble-synth pad.
4. **ModalSynth** `'string'` preset — section pizzicato fallback.

## Production

- **Reverb**: hall 2.4–2.8 s — longest tail in the Strings family (violin
  2.0, harp 2.2); the section pad blooms in space. REVERB_TAIL 2.6 s
- **EQ**: cut ~250 Hz low-mid mud (section mass piles up 200–400 Hz);
  boost ~3.2 kHz for bow articulation; gentle 8.5 kHz shelf — a wall of
  9k+ shimmer is a production artifact, keep it warm
- **Pan**: center for the composed stem; ±0.3 L/R spread when doubling as
  two sections (violins L, cellos R)
- **Layering**: the idiomatic doubling is octaves (violin + cello 8va),
  NOT unison with another melodic patch — unison doubles on the same
  pitches comb-filter (the 2026-09-01 lesson); the section already IS
  many unison strings

## Verification

- GM48 → stem `trackXX_String_Ensemble_1.wav` (label matches, no quirk)
- FluidR3 preset 48 = "Strings" (verified from phdr chunk; one-word SF2
  spelling, cosmetic)
- Empirical pitch sweep: 13/13 notes audible 24–96, silent at 102+
- Buzz check: solo render passes the 4–8 kHz spectral gate (≤20%) — no
  comb-filtering (single voice)
- Zero-drift: sustained units end flush at BAR (terminal landmark)
- Engine test: additive smoke render sustains (pad), no collapse

## Stem label / quirks

- GM_PROGRAMS[48] = "String Ensemble 1" → stem `String_Ensemble_1` — exact
  match, **no quirk**
- FluidR3 preset 48 = "Strings" (one word) vs pipeline "String Ensemble 1"
  — cosmetic only, no routing impact
- `MidiInstrument.STRING_ENSEMBLE = 49` is an enum off-by-one (that's GM49
  String Ensemble 2, "Slow Strings"); use registry GM48
- Channel quirk: melodic channel (0–9) with program 48 — channel 9 would
  trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0
  fallback label (timpani lesson)