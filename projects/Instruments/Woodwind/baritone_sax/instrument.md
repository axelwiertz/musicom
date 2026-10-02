---
type: instrument
family: Woodwind
name: Baritone Saxophone
midi_program: 67
gms: "Baritone Sax"
range_min: 36
range_max: 80
solo_range: [42, 72]    # F2-C5 — solo repertoire focus
role: [bass, harmony, accent, lead, countermelody]
synthesis: [phase_mod, additive]
---

# Baritone Saxophone

## MIDI / GM

- **Program**: 67 (0-indexed MIDI program = strict GM #68 "Baritone Sax"). NOT
  in `structures/instrument.py` `MidiInstrument` enum (only 10 instruments exposed);
  use raw `program=67` in `add_voice`.
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: prefers FluidR3_GM.sf2 (preset 67 = `Baritone Sax`) over
  TimGM6mb.sf2. `discover_soundfont()` picks FluidR3 automatically when present.
- **Stem label**: pipeline `GM_PROGRAMS[67] = "Baritone Sax"` → sanitized to
  `trackXX_Baritone_Sax.wav`. The stem label is "Baritone_Sax" — NOT "Saxophone"
  and NOT the GM name "Baritone Sax" as one word — match on the ACTUAL label.
- **Program family note**: GM 64=Soprano, 65=Alto, 66=Tenor, **67=Baritone**.
  Baritone (67) is the E♭ baritone — the low anchor of the sax family. This
  entry covers 67.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–80 | C2–G5 | concert baritone (written Eb2–B5 with altissimo); GM patch covers wider than acoustic |
| Sweet spot | 48–65 | C3–F4 | warm singing solo register, deep round tone, the "bari bark" |
| Low | 36–47 | C2–B2 | dark, fat, rumbling bottom — tuba-like depth, massive chest wall |
| Mid | 48–60 | C3–C4 | warm, vocal, woody core — the money register (Gerry Mulligan, Leo Parker) |
| High | 61–80 | C#4–G5 | bright, cutting, altissimo — punchy accent, scream territory |

Sounding range (concert pitch). The baritone is an E♭ transposing instrument:
written note sounds an octave and a major 6th lower. Standard horn with low A
key goes to concert C2 (MIDI 36). Without low A, low B♭ = concert D♭2 (MIDI 37).
Most published parts stay in the written range D3–D5 (concert B♭1–B♭4).
Altissimo above written E5 (concert C#5 = MIDI 61) is specialist territory.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 72–88 | full note | smooth, breathy, vocal — the bari default |
| Tenuto | 68–80 | ~0.85 note | slight separation, expressive |
| Staccato | 60–72 | 1/8–1/4 note | short, crisp, articulated (heaviest reed in the sax family) |
| Accent/marcato | 88–104 | full note, strong onset | sharp reed attack, punchy "bari bark" |
| Subtoned | 50–65 | full note | breathy, whispery, covered — classic jazz ballad voice (Gerry Mulligan) |
| Growl | 70–85 | full note | reed growl/overblow, dirty R&B yell |
| Vibrato (wide) | 70–85 | sustained | deliberate wide vibrato — slightly slower than alto (~3.5–4.5 Hz), deeper pitch modulation |
| Slap tongue | 80–95 | very short (~0.05) | percussive reed slap — extended technique, works best on bari |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich even AND odd harmonics
  (conical bore, single reed) — the darkest/warmest in the sax family. The
  "bari bark" lives in the 800 Hz–2 kHz presence zone. Compared to tenor:
  lower fundamental mass, thicker reed texture, fuller overtones in the low-mid
  band. Characteristic "honk" at ~1.5 kHz with a rich tuba-like body below.
- **Attack**: 40–80 ms (reed/breath onset) — the heaviest reed in the sax
  family (size of a bass clarinet reed), naturally slower attack than tenor/alto.
- **Decay**: sustained (breath-driven, no natural decay while blowing)
- **Release**: 60–140 ms (reed/breath stop) — slightly longer than tenor due to
  the massive resonating column
- **Noise component**: breath hiss (continuous, low level) + reed buzz
  transient at attack; growl is reed vibration breakup; subtone playing reduces
  buzz and increases breathiness
- **Vibrato**: natural 3.5–4.5 Hz, WIDE (±0.3–0.6 semitone) — slightly slower
  than alto/tenor due to the mass of air needed, with a pitch-dominant wobble

## Role in Arrangement

- **Bass** anchor of the sax section — the bari is the bottom voice, covering
  the bass role in a standard 4-part sax section (soprano/alto/tenor/bari).
  In big band, the bari doubles the bass trombone line or plays independent bass
  figures. In smaller combos, it walks bass lines, holds pedal tones, and
  provides the low-end body.
- **Harmony** (3rds/6ths/10ths with tenor, chordal stabs, horn-section pads)
- **Accent** (falls, bends, scoops, horn hits; the bari bark is the punchiest
  accent in the sax section)
- **Lead** (rare but iconic — Gerry Mulligan, Serge Chaloff, Pepper Adams,
  Leo Parker, Ronnie Cuber — the baritone CAN lead with its distinctive
  fat-and-grassy voice; sweet spot F3–C5)
- **Countermelody** (fills behind soloists, bass counterlines, dark harmony
  motion)
- **NOT rhythm-section groove** (the bari is a sustained lead/bass voice, not
  percussive — occasional horn stabs aside)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — primary
   - Saw carrier + mod → even+odd harmonic single-reed conical spectrum; boost
     mod_depth higher than tenor (3.2 vs 3.0) for the even heavier bari reed
     honk and thicker body
   - `freq = midi_to_freq(pitch)`; attack 0.06–0.08 s (slowest reed onset in
     the sax family — heaviest reed), release 0.12 s (massive air column)
   - Wide vibrato via slow LFO on pitch; subtones via lower mod_depth (1.8–2.2)
     with added noise floor

2. **Additive** (`sound/synthesis/additive.py`) — explicit even+odd partials
   with strong fundamental dominance (darkest in the sax family), boost
   800–2000 Hz partials for the bari bark, add breath-noise floor; roll off
   above 7 kHz (darkest/warmest rolloff in the set)

## Production

- **Reverb**: hall/room, 1.2–2.2 s tail (solo); keep articulation clarity,
  but the bari benefits from a slightly longer verb than tenor/alto to bloom
  its low end (2.0 s for ballad, 1.2 s for uptempo)
- **EQ**: cut 300–500 Hz boxiness; boost 1.2–2.0 kHz presence (bari bark —
  lower than tenor 2.2 kHz for the darker bari voice); gentle high shelf above
  5 kHz for breathy air (lower than tenor 5.5 kHz for warmth); gentle low shelf
  at 100 Hz for body
- **Pan**: center (solo), or -0.2..-0.35 in horn section (far left in typical
  4-part sax section L–R spread: bari left, tenor L-center, alto R-center,
  soprano right)

## Verification

- GM67 renders as `trackXX_Baritone_Sax.wav` in RenderPipeline stems — pipeline
  `GM_PROGRAMS[67] = "Baritone Sax"` (label is "Baritone_Sax", SF2 preset 67 =
  "Baritone Sax" — labels match exactly, **no quirk**).
- PhaseModSynth: check even+odd harmonic spectrum (fundamental dominant with
  2nd/3rd prominent, bari bark presence 800 Hz–2 kHz, warm rolloff above 7 kHz).
- Solo render: 4–8 kHz buzz check must pass (<20% gate).