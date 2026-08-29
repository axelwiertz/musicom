---
type: instrument
family: Woodwind
name: Oboe
midi_program: 68
gms: "Oboe"
range_min: 52
range_max: 92
solo_range: [58, 84]    # Bb3-C6 playable, solo sweet spot Bb4-F5
role: [lead, countermelody, harmony, accent]
synthesis: [phase_mod, additive]
---

# Oboe

## MIDI / GM

- **Program**: 68 (0-indexed MIDI program = strict GM #69 "Oboe"). NOT in
  `structures/instrument.py` `MidiInstrument` enum (only 10 instruments
  exposed); use raw `program=68` in `add_voice`.
- **Channel**: any melodic channel (0-9); solo instrument
- **FluidSynth**: TimGM6mb.sf2 preset 68 = `Oboe (Orch)` (verified from phdr
  chunk) → renders a usable oboe; the "(Orch)" suffix is cosmetic, no routing
  impact
- **Stem label**: pipeline `GM_PROGRAMS[68] = "Oboe"` ✓ → `trackXX_Oboe.wav`
  (no quirk — exact label match)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 52–92 | Bb3–G6 | concert oboe, sounding pitch |
| Sweet spot | 71–83 | Bb4–B5 | oboe's characteristic plaintive singing register, projects through orchestra |
| Low | 52–67 | Bb3–G4 | dark, thick, reedy, softer (some call it "frog-like") |
| Mid | 68–76 | G#4–C5 | throat register, thinner, transitional |
| High | 77–92 | C#5–G6 | piercing, bright, cutting — the oboe's trademark top |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 70–90 | full note | smooth, singing, reedy — the oboe default |
| Tenuto | 60–75 | ~0.9 note | slight separation, cantabile |
| Staccato | 55–70 | 1/8–1/4 note | short, crisp, double-tongue capable |
| Accent/marcato | 85–100 | full note, strong onset | sharp reed attack |
| Flutter-tongue | 60–75 | full note | buzzy, rough, rare effect |
| Sforzando | 90–100 | full note, instant loud | explosive attack, decays to piano |

## Timbre DNA

- **Harmonic content**: strong fundamental + rich even AND odd harmonics
  (conical bore, double reed) — brighter and more nasal than clarinet;
  characteristic "piercing" presence 2–4 kHz
- **Attack**: 30–80 ms (reed onset) — the most distinct double-reed attack of
  the woodwinds; oboe is the orchestra's tuning reference (A4=440) because the
  attack is so clear
- **Decay**: sustained (breath-driven, no natural decay)
- **Release**: 50–120 ms (reed/breath stop)
- **Noise component**: reed buzz transient at attack; breath hiss low level;
  key clacks rare in synth
- **Vibrato**: natural 4–6 Hz, narrow (±0.1–0.3 semitone) — the reed vibrato,
  less than voice but always present in expressive playing

## Role in Arrangement

- Lead melody (sweet spot Bb4-F5 — the plaintive solo voice)
- Countermelody (against flute or strings, Baroque obbligato)
- Harmony (doubling 3rds/6ths, woodwind blend, tutti unison)
- Accent/ornament (trills, fast passage work; tuning reference A4)
- NOT bass (low register too weak/dark)
- NOT rhythm (sustained melodic voice)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — best match
   - Saw carrier + mod → even/odd harmonic double-reed spectrum (saw is
     brighter than clarinet's odd-only saw; bassoon uses triangle)
   - `freq = midi_to_freq(pitch)`; attack 0.05 s, release 0.10 s
2. **Additive** (`sound/synthesis/additive.py`) — explicit even+odd partials,
   boost 2–4 kHz partials for the piercing oboe presence
3. ModalSynth: avoid (better for strings/percussion)

## Production

- **Reverb**: hall/room, 1.5–2.5 s tail (solo); keep articulation clarity
- **EQ**: cut 300–500 Hz boxiness/nasality; boost ~3 kHz reed presence;
  gentle high shelf above 7 kHz for air
- **Delay**: none for classical; dotted 8th echo for pop/jazz solo lines
- **Pan**: center (solo) or slight off-center in section

## Verification

- GM68 renders as `trackXX_Oboe.wav` in RenderPipeline stems — pipeline
  `GM_PROGRAMS[68] = "Oboe"` ✓ (no quirk; SF2 preset is "Oboe (Orch)" —
  cosmetic only)
- PhaseModSynth: check even+odd harmonic spectrum (fundamental + 2nd/3rd
  prominent, presence boost 2–4 kHz)
