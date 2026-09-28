---
type: instrument
family: World
name: Pan Flute
midi_program: 75
gms: "Pan Flute"
range_min: 55
range_max: 100
solo_range: [62, 89]
role: [lead, melody, ornament, drone, accent]
synthesis: [phase_mod, additive, airpipe]
---

# Pan Flute

## MIDI / GM

- **Program**: 75 (GM1 Pan Flute; 0-indexed — the 76th entry of the GM1
  list). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) —
  use raw `program=75` in `add_voice`.
- **Channel**: any melodic channel (0-9); line voice — one melodic line per
  breath, no dense chords.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 75 =
  "Pan Flute" (phdr-verified). RenderPipeline stem label: GM_PROGRAMS[75] =
  "Pan Flute" → `trackXX_Pan_Flute.wav` — matches exactly, **no quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–100 | G3–E7 | large zampoña/siku set (18–30 tubes) |
| Low (zankha) | 55–61 | G3–B3 | bass zampoña — deep, airy, breathy |
| Middle (malta) | 62–78 | D4–F5 | primary melodic register — warm, round, fluty |
| High (chuli) | 79–100 | F#5–E7 | siku chuli — bright, piercing, whistle-like |

Practical melodic core is C4–C6 (60–84). Standard 1.5-octave siku (arqa/ira
complementary pair) covers D4–A5 on each row; larger 3-octave chromatic
zampoñas extend to C7. The sweet, round tone lives in the malta register
(62–78 / D4–F5).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain (breath) | 70–90 | full note | steady breath flow, pure tone |
| Staccato | 60–75 | 1/8–1/4 | short breath cutoff, quick tongue |
| Accent (blow) | 85–100 | full, aggressive onset | breathy burst, slight pitch bend up |
| Legato (slur) | 72–85 | full, connected | smooth breath transitions between tubes |
| Trill | 65–75 | 16th–32nd | fast alternation between adjacent tubes |
| Grace | 60–70 | tiny | quick breath pulse before main note |
| Vibrato (jaw) | 70–80 | full, wide | jaw vibrato — characteristic Andean quaver |
| Airy (soft) | 45–60 | full, breathy | wind-only tone, half-pitch harmonics |

## Timbre DNA

- **Harmonic content**: predominantly fundamental + odd harmonics 3, 5, 7
  (stopped-pipe acoustic — only odd partials present, unlike open flute).
  Upper partials are weak; the tone is hollow, pure, and round.
- **Attack**: 5–15 ms breath onset — gentle blow transient, no reed/tongue
  snap, some air hiss at the tube opening.
- **Decay**: sustains while breath flows; cutoff is near-instant (breath
  release).
- **Noise component**: breath hiss at attack + tube-tone turbulence, part of
  the idiom (Andean panpipes ARE breathy).
- **Vibrato**: jaw vibrato (slow, wide, ~3–4 Hz) — the characteristic Andean
  quaver.
- **Character**: warm, hollow, breathy, pure — instantly "Andean" the moment
  the first note sounds. The stopped-pipe acoustics give it a darker, rounder
  tone than a concert flute (open pipe with all partials).

## Role in Arrangement

- Lead melody (malta zone D4–F5) — Andean folk melodies, pentatonic lines,
  kantu dance suites
- Ornament (grace notes, trills, descending scales/glissando)
- Drone layer (low held notes under the melody — the zankha bass zampoña
  holds a tonic pedal)
- Accent (short punctuated breaths on downbeats)
- Countermelody with kena/quena (Andean notched flute), charango, guitar
- NOT harmony (line voice — each tube gives one pitch, so chords require
  either a second row/musician or arpeggiated break)
- NOT bass (zankha bass range is breathy and short; use a separate bass
  instrument)
- NOT background pad — breath changes create rhythmic boundaries

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`, SP-002) — **primary**.
   Stopped-pipe flue tone: sine carrier + sine modulator with low depth
   (1.2 — between ocarina 0.8 and shakuhachi 2.0) for the pure fundamental
   dominance; attack 0.05 s for gentle breath onset; release 0.15 s for
   natural breath cutoff. The low mod depth suppresses upper harmonics,
   matching the stopped-pipe's odd-only partial preference.
2. **Additive** (`sound/synthesis/additive.py`) — fallback. 4 partials at
   odd-only ratios (1, 3, 5, 7) with weights 0.9, 0.35, 0.15, 0.05 — the
   strongest fundamental dominance of the World wind instruments. Time
   envelopes: attack 0.05, release 0.15.
3. **AirPipe** (`sound/synthesis/airpipe.py`) — physical aerophone model.
   Stopped tube (`stopped=True`), `length_scale=0.85`, `pressure=0.55`,
   `noise=0.15` for the breath component.

## Production

- **Reverb**: hall 2.0 s — panpipes love mountain-valley space (soft, long
  decay); shorter 1.4 s for dance music
- **EQ**: cut 250–350 Hz tube resonance boxiness; gentle +2 dB at 2.2 kHz
  for breath presence; 0 dB at 8 kHz (roll off the sibilance — panpipes are
  naturally rolled off above ~8 kHz due to the stopped-pipe cut)
- **Delay**: dotted-8th echo for melodic lines; none for dance tunes
- **Pan**: center solo; 0.1–0.2 for siku arqa/ira stereo pair

## Verification

- GM75 → stem `trackXX_Pan_Flute.wav` (label matches, no quirk; FluidR3
  preset 75 = "Pan Flute" phdr-verified)
- Zero-drift: melody units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz)
- Spectral 4–8 kHz buzz well below 20% (breathy, not bright — the sto
pped-pipe roll-off)