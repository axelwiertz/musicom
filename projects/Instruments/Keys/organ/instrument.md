---
type: instrument
family: Keys
name: Organ
midi_program: 19
gms: "Church Organ"
range_min: 36
range_max: 96
solo_range: [48, 84]    # C3-C6 playable, solo sweet spot G3-G5
role: [harmony, pad, bass, rhythm, accent]
synthesis: [additive, phase_mod]
---

# Organ (Church)

## MIDI / GM

- **Program**: 19 (GM1 Church Organ)
- **Channel**: any melodic channel (0-9); polyphonic chord instrument
- **FluidSynth**: TimGM6mb.sf2 renders GM19 → Church Organ (preset name matches
  exactly); FluidR3_GM.sf2 preset 19 also "Church Organ"
- **Pipeline stem label**: `GM_PROGRAMS[19]` = "Church Organ" → `trackXX_Church_Organ.wav` (no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | 61-key manuals; 32' rank extends to C1=24, 2' rank to G7=103 |
| Sweet spot | 55–79 | G3–G5 | full chorus + solo stops speak best, cuts through |
| Low | 36–47 | C2–B2 | pedal/foundation 16'+8', ground the bass |
| Mid | 48–66 | C3–G#4 | diapason/principal chorus, comping + pad |
| High | 67–96 | A4–C7 | solo reed/mixture, bright, cutting |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 70–90 | full note | continuous wind, no decay while key held |
| Legato | 60–80 | full note, overlapped | seamless, pipe organ ideal |
| Staccato | 55–70 | 1/8–1/4 note | key release — pipe stops near-instantly |
| Accent/marcato | 85–100 | full note, strong onset | swell-pedal emphasis, full drawbars |
| Pulse (vamp) | 60–75 | 1/2–1/4 note | rhythmic chord stab, gospel/Hammond |
| Trill | 55–70 | very short, fast | two-note trill, 16th/32nd repeats |

## Timbre DNA

- **Harmonic content**: static harmonic series from drawbars/ranks — partials at
  1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0× fundamental (8', 5⅓', 4', 2⅔', 2', 1⅗', 1⅓');
  no inharmonicity, no pitch drift
- **Attack**: 1–10 ms key-on (pipe chiff transient; Hammond key click) — effectively instant
- **Decay**: NONE while key held — wind sustains indefinitely (sustain level 1.0)
- **Release**: 10–50 ms key-off cut (pipe stops; no reverb of its own)
- **Noise component**: pipe chiff (attack transient, low level); key click (Hammond);
  no breath, no mechanical noise in synth
- **Vibrato**: NOT native — Hammond leslie sim (rotary 6–7 Hz chorus/Doppler) is an
  external effect; pipe organ is steady-state

## Role in Arrangement

- Harmony/comping (mid register, sustained or pulsing chords)
- Pad (sustained chords, church/Hammond wash — orchestrator pad secondary)
- Bass (low register pedal notes, 16' foundation)
- Rhythm (pulsed vamps, gospel stabs, rock organ)
- Accent (big sustained chords, high register reeds)
- NOT lead in mixes with vocals (steady tone fights voice — use 8'+4' solo stops sparingly)

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py` SoundWave) — best match
   - `apply_overtones(factor=[1.0, 0.8, 0.6, 0.5, 0.35, 0.25, 0.15])` — drawbar mix
     (8', 4', 2⅔', 2', 1⅗', 1⅓' partials; optionally 5⅓' at 0.5×)
   - `get_adsr_weights(length=[0.01, 0.0, 0.95, 0.04], sustain_level=1.0)` —
     near-zero attack, full sustain, short release
   - Factor amplitudes must sum to 1.0 (engine assertion)
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — DX7-style FM organ
   - `carrier_shape='sine'`, `mod_freq_ratio=2.0`, `mod_depth=2.5`, `attack=0.005`,
     `release=0.05` — or `harmonics=[(1,1.0),(2,0.8),(3,0.5)]` via `_build_harmonic_wavetable`
3. **PolySynth** (`sound/synthesis/polysynth.py`) — organ-flavored drawbar pad
   (osc1 saw + osc2 square detuned, slow filter) — more electric/rock than church
4. **Avoid** ModalSynth (percussive decay presets — organ has no decay)

## Production

- **Reverb**: cathedral/church, 2–4 s tail (the organ's natural habitat);
  plate for gospel/Hammond
- **EQ**: cut 250–400 Hz mud; presence 2–3 kHz for chiff/reed; high shelf subtle —
  organ is mid-heavy, don't over-brighten
- **Leslie/rotary**: chorus/Doppler LFO 6–7 Hz on slow, ~0.5 Hz on fast for Hammond
- **Pan**: center (church); split manuals L/R for wide pad
- **Compression**: gentle — organ has no transients; heavy compression is pointless

## Verification

- GM19 renders as `trackXX_Church_Organ.wav` in RenderPipeline stems (label
  matches, no quirk — see REGISTRY quirks table)
- Additive synth: check STATIC harmonic spectrum (partials stay fixed over time,
  no pitch drift) and sustain level 1.0 (no decay)
- PhaseModSynth: check 2nd-partial-pair FM spectrum (DX7 organ signature)
- Church Organ = GM **19** (0-indexed). `MidiInstrument.CHURCH_ORGAN = 20` is
  the 1-indexed GM number — use raw 19 for pipeline/SF2 (same class of off-by-one
  as trumpet 57→56; piano.py=1 → Bright_Acoustic_Piano)
