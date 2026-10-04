---
type: instrument
family: Woodwind
name: Whistle
midi_program: 78
gms: "Whistle"
range_min: 62
range_max: 93
solo_range: [67, 86]
role: [lead, melody, ornament, accent]
synthesis: [phase_mod, additive]
---

# Whistle

## MIDI / GM

- **Program**: 78 (GM1 Whistle — 0-indexed; the 79th entry of the GM1 list).
  NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=78` in `add_voice`.
- **Channel**: melodic channel (0-9) — flue aerophone, NOT channel 9 percussion.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 78 =
  "Whistle" (phdr-verified). RenderPipeline stem label: GM_PROGRAMS[78] =
  "Whistle" → `trackXX_Whistle.wav` — matches exactly, **no quirk**.
- GM neighbors: 77 Shakuhachi, 78 Whistle, 79 Ocarina — the "simple flute"
  block of GM1.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 62–93 | D4–A6 | tin whistle (standard D whistle 2 octaves + overblow) |
| Sweet spot | 67–86 | G4–D6 | brightest, clearest, most projecting whistle tone |
| Low | 62–69 | D4–A4 | 1st octave — round, flute-like, breathy at edges |
| Mid | 70–79 | A#4–G5 | 2nd octave start — bright, sweet, primary folk melody zone |
| High | 80–93 | G#5–A6 | 2nd octave top + overblow — piercing, thin, whistle squeal |

The standard D tin whistle (penny whistle) has a two-octave compass from
D4 (62) to D6 (86). Skilled players overblow to G6 (91) or higher. The
GM patch (FluidR3 "Whistle") audibly supports 62–93 with a clean, bright
tone. The sweetest folk-melody register is G4–D6 (67–86). Low whistles in
D3 exist but use the same GM patch transposed. Dense chords are NOT
idiomatic — the whistle is a monophonic breath-line instrument (like
shakuhachi, pan flute, ocarina).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato (slur) | 72–85 | full note | smooth breath, connected notes, natural whistle tone |
| Staccato (tongue) | 62–75 | 1/8–1/16 | quick tongue stop, clean articulation |
| Cut (grace) | 70–85 | 1/32 | finger grace — a quick higher-note dab between same pitches |
| Roll | 68–80 | 1/8 | long grace pattern (cran on low D) — rhythmic ornament |
| Breath (airy) | 50–60 | full | half-blown, breathy, soft tone |
| Accent (hard tongue) | 88–100 | full, percussive | aggressive tongue strike — piercing, driving folk tune |

## Timbre DNA

- **Harmonic content**: bright fundamental + strong 2nd partial (open tube
  = all harmonics present, unlike stopped-pipe pan flute). Upper partials
  are moderately strong — the whistle is brighter and simpler than a
  concert flute.
- **Attack**: 3–10 ms (breath onset on the fipple) — very fast; the blade
  (fipple) produces an immediate edge tone with minimal transient noise.
- **Decay**: sustains while breath flows; cut-off is clean and near-instant
  (breath release or tongue stop).
- **Noise**: minimal — the clean fipple edge produces far less breath noise
  than a shakuhachi or pan flute; some chiff at the attack.
- **Vibrato**: optional — finger vibrato (wavery pitch on long notes) or
  diaphragmatic vibrato; not inherent like the pan flute's jaw vibrato.
- **Character**: bright, pure, piercing — instantly "Celtic/Irish" the
  moment the first note sounds. Simpler and reedier than a concert flute,
  brighter than a recorder, less breathy than a shakuhachi.

## Role in Arrangement

- Lead melody (mid register 67–86) — Irish jigs, reels, hornpipes, folk
  melodies, Celtic film scoring
- Ornament (cuts, rolls, crans, grace notes) — the idiomatic soul of Irish
  traditional music; a whistle without ornaments is a beginner whistle
- Accent (hard-tongued downbeats, short punctuations)
- Countermelody above fiddle, accordion, guitar — Irish session pairing
- NOT a harmony/pad instrument — monophonic breath line, no chords;
  double-stops are physically impossible on a single tube
- NOT a bass voice (the lowest note is D4 on a standard D whistle)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`, SP-002) — **primary**.
   Open-tube flue tone (fipple-edge whistle, all harmonics present): sine
   carrier + sine modulator with low-moderate depth (1.5 — between flute 1.5
   and shakuhachi 2.0) for the bright fundamental + moderate upper partials;
   attack 0.04 s for the fast fipple onset (faster than flute 0.08, same as
   piccolo 0.04); release 0.10 s for natural breath cutoff.

2. **Additive** (`sound/synthesis/additive.py`) — fallback. Full harmonic
   stack (1, 2, 3, 4, 5, 6) with weights 0.9, 0.6, 0.4, 0.2, 0.1, 0.05 —
   the open-tube whistle has a stronger 2nd partial than the closed-tube pan
   flute (odd-only). Time envelopes: attack 0.04, release 0.10.

## Production

- **Reverb**: room 1.4–1.8 s — whistle is a dry, clean folk instrument;
  large reverbs smear its cutting articulation (compare ocarina 1.6, pan
  flute 2.0)
- **EQ**: cut 400–600 Hz honk/boxiness; boost ~3 kHz for the bright fipple
  edge; gentle 7 kHz shelf for air (the whistle already has strong upper
  harmonics — too much 8 kHz+ sounds shrill)
- **Delay**: optional dotted-8th at low mix for slow airs; none for dance
  tunes (reels/jigs)
- **Pan**: center solo; ±0.2 in ensemble (stereo whistle pair for twin-line
  counterpoint)

## Verification

- GM78 → stem `trackXX_Whistle.wav` (label matches, no quirk; FluidR3
  preset 78 = "Whistle" phdr-verified)
- Zero-drift: melody units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz)
- Spectral 4–8 kHz buzz well below 20% (bright but clean open-tube tone)

## Instrument.md companion

`whistle.py` — importable constants. Registered in
`instrument_registry.py` (2026-10-04) as `Woodwind.whistle.whistle` → key
`whistle`, constant `WHISTLE`.