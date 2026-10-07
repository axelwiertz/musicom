---
type: instrument
family: Keys
name: Reed Organ
midi_program: 20
gms: "Reed Organ"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [harmony, pad, melody, drone, ornament]
synthesis: [phase_mod, modal, additive]
---

# Reed Organ (Harmonium)

The reed organ (also called pump organ, harmonium, or cabinet organ) is a free-reed aerophone keyboard instrument — the 19th century's domestic alternative to the pipe organ. Air from foot-pumped (or hand-pumped) bellows flows past brass free reeds mounted in a wooden wind chest. Unlike the pipe organ (GM19), the reed organ has **one reed per pitch**, no pipes, and a characteristic warm/nasal/buzzy tone shaped by the cabinet resonator.

The instrument comes in three main traditions:
- **American Reed Organ** (suction): air is drawn *through* the reeds by vacuum bellows (foot-treadle operated). Softer, sweeter tone. McTammany, Estey, Mason & Hamlin.
- **European Harmonium** (pressure): air is blown *past* the reeds by pressure bellows (foot-operated). Louder, more articulate, with stronger attack. Debussy's *Prélude à l'après-midi d'un faune* opening, Franck's organ replacement.
- **Indian Harmonium**: hand-pumped pressure harmonium, ubiquitous in North Indian classical music (gharana tradition), Qawwali/Sufi devotional, Bollywood, and folk. Drone stops (Sa-Pa) built in. The most widely played harmonium in the world today.

The reed organ is **fully polyphonic** — capable of sustained chords, melody + accompaniment, or drone + melody simultaneously. Unlike the accordion (GM21), there is no separate bass/treble system — the entire keyboard plays through one unified set of reeds.

## MIDI / GM

- **Program**: 20 (GM1 Reed Organ, 0-indexed; 1-indexed GM #21)
- **Channel**: Melodic channel (0–8, 10–15)
- **RenderPipeline stem label**: `trackXX_Reed_Organ.wav` ✓ (GM_PROGRAMS[20] = "Reed Organ", FluidR3 preset 20 = "Reed Organ" — exact match, no quirk)
- **SoundFont (FluidR3_GM.sf2)**: Preset 20 "Reed Organ" provides the classic cabinet harmonium sound across the full velocity and pitch range.

## Range

Standard full-size 5-octave reed organ: **C2–C7** (MIDI 36–96). The sweet spot is C4–C6 (MIDI 60–84) — the middle 2 octaves where the cabinet resonance is fullest and the reed tone is most characteristic.

| Zone | MIDI | Pitches | Character & Register |
|---|---|---|---|
| Bass | 36–47 | C2–B2 | 8' bass reeds: dark, rumbling, drone foundation, muddy in dense chords |
| Low (tenor) | 48–59 | C3–B3 | Warm, reedy, cello-like; the bass end of solo melody; pedal-point drone zone |
| Middle | 60–76 | C4–E5 | Primary melodic register: richest, sweetest cabinet tone, the "singing" reed |
| High | 77–89 | F5–F6 | 4' treble register: bright, cutting, accordion-like; doubles melody at +12 |
| Extended | 90–96 | G6–C7 | Thin/piercing, lowest reed density at top; occasional upper-extension notes |

- **Sweet Spot**: 60–84 (C4–C6, ~262–1008 Hz) — middle two octaves, the voice-like reed core.
- **Solo Range**: 48–84 (C3–C6) — the full expressive compass of a standard 49-key instrument.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Sustain | 70–78 | 1.0 | Steady bellows, held chord — the default reed organ sound |
| Legato | 64–72 | 1.0 | Smooth connected notes, minimal bellows articulation |
| Staccato | 74–82 | 0.2 | Short bellows pulse; crisp chordal release for hymn/accompaniment |
| Marcato | 82–90 | 0.85 | Hard bellows accent; strong cabinet resonance bloom |
| Sforzando | 90–96 | 0.80 | Sudden forceful bellows push for dramatic accent |
| Tremolo | 66–74 | 0.60 | Bellows shake — amplitude vibrato via foot-pump wobble (used in gospel) |

## Timbre DNA

- **Harmonic spectrum**: Free-reed tone: strong fundamental and a full set of even+odd harmonics (sawtooth-like wave). The cabinet resonator acts as a bandpass filter, emphasizing the 250–800 Hz body region and rolling off above ~6 kHz. The result is a warm, nasal, "reedy" tone — brighter than pipe organ but darker than accordion.
- **Envelope**: Moderate attack (30–50 ms) — the bellows must fill the wind chest before the reed speaks. The attack is slower than a handheld free-reed (accordion 15 ms, harmonica 10 ms) but faster than a pipe organ. Release is similarly moderate — the wind chest gives a brief sustain after the bellows stop.
- **Tremolo**: Bellows shake (foot-pump wobble) produces an amplitude vibrato at ~4–6 Hz, used expressively in Indian and gospel playing.

## Role in Arrangement

- **Harmony / Pad**: The reed organ's primary role — sustained hymn-style chords, gospel pads, ambient drone beds. The sawtooth-rich tone fills the midrange without competing with the bass.
- **Melody**: Single-note melody in the sweet spot (C4–C6) cuts through a mix. The nasal tone is distinct from both strings and brass.
- **Drone**: The 8' bass reeds (C2–B3) excel at drone notes. In Indian-style writing, set a Sa (tonic) pedal and play melody above.
- **Ornament**: Bellows shake tremolo, quick chord jabs for gospel accents, rolled chord arpeggios for hymn introductions.
- **NOT a bass voice**: The 8' bass reeds are warm but lack sub-bass weight. Do not use for sub-60 Hz bass lines (leave those to tuba, double bass, or synth bass).

## Synthesis Engines (musicom)

1. **PhaseModSynth (`phase_mod`)** — **PRIMARY**:
   - Carrier: saw, Modulator: sine
   - Mod ratio: 1.0, Mod depth: 3.5
   - Saw carrier = full even+odd harmonic set (the free reed's signature)
   - Attack: 0.04 s (wind chest fill time), Release: 0.06 s
   - Mod depth 3.5 is the highest among the free-reed set (accordion 3.2, harmonica 2.5) — the cabinet resonator amplifies the reed buzz

2. **ModalSynth (`modal`)** — FALLBACK:
   - Use stock `'string'` preset for a clean sustained harmonic stack
   - Models the body resonance of the cabinet as a 1D string-like filter (not physically accurate but produces useful chord pads)

3. **AdditiveSynth (`additive`)** — ALT:
   - Saw wave modeled as fundamental (1.0), even harmonics 0.45/0.25/0.12..., odd harmonics 0.50/0.28/0.14...
   - Bandpass at 250–6000 Hz with 6 dB/oct rolloff below/above for cabinet-body shaping

## Production Defaults

- **Reverb Tail**: 1.6 s (chamber/small hall — harmonium is naturally dry but cabinet resonance gives a small bloom; too much reverb washes out the reed character)
- **EQ**:
  - Body: −2.5 dB at 250 Hz (peaking cut — tame the cabinet "honk" / wind chest boxiness)
  - Presence: +2.5 dB at 2200 Hz (peaking boost — reed definition and cut through the mix)
  - Air: +1.5 dB shelf at 7.5 kHz (subtle reed buzz sparkle)
  - High-pass: 18 dB/oct rolloff below 90 Hz (eliminate foot-pump rumble)
- **Pan**: 0.0 (center for solo); ±0.15–0.25 for stereo harmonium layering

## FluidSynth & Pipeline Behavior

- **GM Program**: 20
- **RenderPipeline Stem**: `trackXX_Reed_Organ.wav` (pipeline `GM_PROGRAMS[20] == "Reed Organ"`)
- **FluidR3_GM.sf2**: Preset 20 is named `"Reed Organ"` with full velocity and pitch range verified.
- **GM_PROGRAMS[20]** = "Reed Organ" — labels match exactly, **no quirk**.
- **Channel quirk**: MUST use a melodic channel (0–8, 10–15) with program 20 — channel 9 would trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback label.
- **Polyphonic capacity**: Unlike line/lead instruments (clarinet, fiddle), the reed organ is a true harmony instrument — write full chords with 3–5 notes. The free reeds sound simultaneous pitches without intermodulation distortion.