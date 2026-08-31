---
type: instrument
family: Woodwind
name: Alto Saxophone
midi_program: 65
gms: "Alto Sax"
range_min: 49
range_max: 88
solo_range: [54, 82]    # F#3-Ab6 practical, sax solo focus Db4-F5
role: [lead, countermelody, accent, harmony]
synthesis: [phase_mod, additive]
---

# Alto Saxophone

## MIDI / GM

- **Program**: 65 (0-indexed MIDI program = strict GM #66 "Alto Sax"). NOT in
  `structures/instrument.py` `MidiInstrument` enum (only 10 instruments exposed);
  use raw `program=65` in `add_voice`.
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: prefers FluidR3_GM.sf2 (preset 65 = `Alto Sax`) over
  TimGM6mb.sf2 (`AltoSax (TB) v2.3`). `discover_soundfont()` picks FluidR3
  automatically when present. TimGM6mb sax is TimBrasse "TB" — bright, reedy,
  breathy; FluidR3 sax is rounder/fuller.
- **Stem label**: pipeline `GM_PROGRAMS[65] = "Alto Sax"` → sanitized to
  `trackXX_Alto_Sax.wav`. NOTE: the stem label is "Alto_Sax", NOT "Saxophone"
  and NOT "Tenor Sax" — match on the ACTUAL label "Alto_Sax" in any stem-aware
  code, not the family name.
- **Program family note**: GM 64=Soprano, 65=Alto, 66=Tenor, 67=Baritone. Alto
  (65) is the default pop/jazz sax; tenor (66) is the deeper alternative. This
  entry covers 65.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 49–88 | Db3–E6 | concert alto sax (written range Db3-Ab5 ≈ sounding F#3-F5 plus altissimo) |
| Sweet spot | 61–79 | C4–G5 | the sax's singing solo register, full round tone, pop/jazz leads |
| Low | 49–60 | Db3–C4 | dark, husky, breathy — fat but less projection |
| Mid | 61–70 | C4–B4 | warm, vocal, "vocal fry" edge — ballad territory |
| High | 71–88 | C5–E6 | bright, cutting, altissimo scream — piercing lead/ornament |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 75–90 | full note | smooth, vocal, breathy — the sax default |
| Tenuto | 65–80 | ~0.9 note | slight separation, expressive |
| Staccato | 60–75 | 1/8–1/4 note | short, crisp, articulated (single/double tongue) |
| Accent/marcato | 88–105 | full note, strong onset | sharp reed attack, punchy |
| Bending/falloff | 60–75 | glissando/slide (pitch bend) | lip slide, growl tail (soul/r&b signature) |
| Growl | 70–85 | full note | reed growl/overblow, dirty blues/rock |
| Vibrato (wide) | 70–85 | sustained | deliberate wide vibrato — the sax hallmark |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich even AND odd harmonics
  (conical bore, single reed) — brighter and more overtone-dense than clarinet,
  nasal reed core. Characteristic "honk" presence 1–3 kHz, breathy air above 5 kHz
- **Attack**: 20–60 ms (reed/breath onset) — the classic GM sax has a fast,
  slightly breathy attack; softer than double-reed oboe, more punch than flute
- **Decay**: sustained (breath-driven, no natural decay while blowing)
- **Release**: 40–120 ms (reed/breath stop)
- **Noise component**: breath hiss (continuous, low level) + reed buzz transient
  at attack; growl is reed overblow
- **Vibrato**: natural 4–6 Hz, WIDE (±0.3–0.6 semitone) — the saxophone's
  trademark vibrato is much wider than flute/clarinet; typically pitch-bend in
  synth or a slow LFO

## Role in Arrangement

- Lead melody (sweet spot C4-G5 — pop, jazz, funk, soul leads; the default
  "sexy sax" voice)
- Countermelody (fills behind vocals, call-and-response)
- Accent/ornament (falls, bends, screams at the top; horn-section hits)
- Harmony (sax section — unison/3rds with tenor, doubling in horn stabs)
- NOT bass (low register too weak/reedy; baritone sax covers bass role in a
  sax section, not alto)
- NOT rhythm (sustained melodic voice; occasional rhythmic horn stabs aside)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — best match
   - Saw carrier + mod → even+odd harmonic single-reed conical spectrum; boost
     mod_depth higher than clarinet for the brighter sax reed honk
   - `freq = midi_to_freq(pitch)`; attack 0.03–0.06 s (breathy reed onset),
     release 0.10 s; wide vibrato via slow LFO on pitch (not in the FM engine —
     add as post LFO or pitch bend)
2. **Additive** (`sound/synthesis/additive.py`) — explicit even+odd partials,
   boost 1–3 kHz partials for the sax honk, add breath-noise floor
3. ModalSynth: avoid (better for strings/percussion)

## Production

- **Reverb**: hall/room, 1.2–2.0 s tail (solo); keep articulation clarity, less
  than strings — sax cuts on its own
- **EQ**: cut 300–500 Hz boxiness/honk; boost ~2 kHz presence (reed core);
  gentle high shelf above 6 kHz for breathy air; low-pass 10–12 kHz to tame
  synthetic harshness
- **Delay**: dotted 8th echo for pop ballad leads; slapback for rockabilly
- **Pan**: center (solo lead) or +0.2..0.35 in horn section (duck out of lead)

## Verification

- GM65 renders as `trackXX_Alto_Sax.wav` in RenderPipeline stems — pipeline
  `GM_PROGRAMS[65] = "Alto Sax"` (label is "Alto_Sax", not "Saxophone"; SF2
  preset 65 = "AltoSax (TB) v2.3"). Match on "Alto_Sax".
- PhaseModSynth: check even+odd harmonic spectrum (fundamental + 2nd/3rd
  prominent, honk presence 1–3 kHz)
