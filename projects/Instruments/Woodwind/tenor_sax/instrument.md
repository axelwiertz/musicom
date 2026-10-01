---
type: instrument
family: Woodwind
name: Tenor Saxophone
midi_program: 66
gms: "Tenor Sax"
range_min: 44
range_max: 88
solo_range: [48, 82]    # D3-Ab6 practical, sax solo focus F3-F5
role: [lead, countermelody, accent, harmony]
synthesis: [phase_mod, additive]
---

# Tenor Saxophone

## MIDI / GM

- **Program**: 66 (0-indexed MIDI program = strict GM #67 "Tenor Sax"). NOT in
  `structures/instrument.py` `MidiInstrument` enum (only 10 instruments exposed);
  use raw `program=66` in `add_voice`.
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: prefers FluidR3_GM.sf2 (preset 66 = `Tenor Sax`) over
  TimGM6mb.sf2. `discover_soundfont()` picks FluidR3 automatically when present.
- **Stem label**: pipeline `GM_PROGRAMS[66] = "Tenor Sax"` → sanitized to
  `trackXX_Tenor_Sax.wav`. NOTE: the stem label is "Tenor_Sax", NOT "Saxophone"
  and NOT "Alto_Sax" — match on the ACTUAL label "Tenor_Sax" in any stem-aware
  code.
- **Program family note**: GM 64=Soprano, 65=Alto, 66=Tenor, 67=Baritone. Tenor
  (66) is the B♭ tenor — the most famous sax voice (Coleman Hawkins, Lester
  Young, John Coltrane, Sonny Rollins). This entry covers 66.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 44–88 | A♭2–E6 | concert tenor (written B♭2–F♯6 with altissimo) |
| Sweet spot | 53–78 | F3–F5 | the tenor's singing solo register, full round warm tone, jazz/blues leads |
| Low | 44–53 | A♭2–F3 | dark, husky, breathy bottom — fat but less projection |
| Mid | 54–68 | F♯3–C5 | warm, vocal, husky core — the "tenor wall" money register |
| High | 69–88 | C♯5–E6 | bright, cutting, altissimo scream — piercing lead/ornament |

Written range (treble clef, transposed): B♭2–F♯6. The tenor sounds an octave
and a major second LOWER than written (B♭ transposition). Most published
parts stay in the written range D3–C6 (concert A2–B♭4). Altissimo above
written F♯6 is specialist territory.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 75–90 | full note | smooth, vocal, breathy — the tenor default |
| Tenuto | 65–80 | ~0.9 note | slight separation, expressive |
| Staccato | 60–75 | 1/8–1/4 note | short, crisp, articulated (heavier reed than alto) |
| Accent/marcato | 88–105 | full note, strong onset | sharp reed attack, punchy |
| Subtoned | 50–65 | full note | breathy, whispery, covered — classic jazz ballad voice |
| Bending/falloff | 60–75 | glissando/slide (pitch bend) | lip slide, growl tail (soul/r&b signature) |
| Growl | 70–85 | full note | reed growl/overblow, dirty blues/rock yell |
| Vibrato (wide) | 70–85 | sustained | deliberate wide vibrato — the sax hallmark; tenor vibrato is slightly wider and slower than alto (~4.5 Hz, ±0.4 semitone) |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich even AND odd harmonics
  (conical bore, single reed) — darker/warmer than alto (lower fundamental
  presence), huskier reed texture. Characteristic "honk" presence 1.5–3 kHz,
  breathy air above 5 kHz. The tenor has a thicker, "sticky" overtone
  spectrum — roll off above 8 kHz compared to alto's sparkle.
- **Attack**: 30–60 ms (reed/breath onset) — heavier reed than alto, slightly
  slower response. Classic GM tenor has a fast but weighty attack.
- **Decay**: sustained (breath-driven, no natural decay while blowing)
- **Release**: 50–120 ms (reed/breath stop)
- **Noise component**: breath hiss (continuous, low level) + reed buzz
  transient at attack; growl is reed overblow, subtones reduce hiss
- **Vibrato**: natural 4–5 Hz, WIDE (±0.3–0.6 semitone) — the tenor sax
  vibrato is the widest in the sax family; typically deeper and slower than
  alto, with more pitch bend than amplitude modulation

## Role in Arrangement

- Lead melody (sweet spot F3–F5 — the classic jazz/blues/rock tenor lead; the
  "Coltrane" shout, the "Rollins" wit, the "Hawkins" swagger)
- Countermelody (fills behind vocals, call-and-response, tenor battle)
- Accent/ornament (falls, bends, screams at the top; horn-section hits)
- Harmony (sax section — 3rds/6ths with alto, unison with soprano, horn stabs)
- NOT bass (baritone sax covers bass role in a sax section, not tenor)
- NOT rhythm (sustained melodic voice; occasional rhythmic horn stabs aside)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — primary
   - Saw carrier + mod → even+odd harmonic single-reed conical spectrum; boost
     mod_depth higher than alto (3.0 vs 2.8) for the huskier tenor reed honk
   - `freq = midi_to_freq(pitch)`; attack 0.04–0.06 s (breathy reed onset,
     slightly slower than alto for the heavier reed), release 0.10 s
   - Wide vibrato via slow LFO on pitch (not in the FM engine — add as post
     LFO or pitch bend); subtones via lower mod_depth (1.5–2.0) with noise
     floor
2. **Additive** (`sound/synthesis/additive.py`) — explicit even+odd partials
   with stronger fundamental relative to alto (for the darker tenor tone),
   boost 1.5–2.5 kHz partials for the reed honk, add breath-noise floor at
   a slightly lower cutoff than alto (warmer)

## Production

- **Reverb**: hall/room, 1.2–2.0 s tail (solo); keep articulation clarity, less
  than strings — tenor cuts on its own; longer verb (2.0 s) for ballad, shorter
  (1.2 s) for uptempo jazz
- **EQ**: cut 300–500 Hz boxiness/honk; boost ~2.2 kHz presence (reed core —
  lower than alto's 2.5 kHz for the darker tenor); gentle high shelf above
  5.5 kHz for breathy air (lower than alto's 6 kHz); low-pass 10–11 kHz
- **Delay**: dotted 8th echo for ballad leads; slapback for rockabilly; analog
  tape echo for vintage jazz
- **Pan**: center (solo lead) or +0.25..0.35 in horn section (between alto and
  baritone in typical 4-part sax section L–R spread)

## Verification

- GM66 renders as `trackXX_Tenor_Sax.wav` in RenderPipeline stems — pipeline
  `GM_PROGRAMS[66] = "Tenor Sax"` (label is "Tenor_Sax", not "Saxophone"; SF2
  preset 66 = "Tenor Sax" — labels match exactly, **no quirk**).
- PhaseModSynth: check even+odd harmonic spectrum (fundamental + 2nd/3rd
  prominent, husky honk presence 1.5–3 kHz, warmer rolloff above 8 kHz vs
  alto)