---
type: instrument
family: Percussion
name: Marimba
midi_program: 12
gms: "Marimba"
range_min: 45
range_max: 96
solo_range: [60, 84]    # A2-C7 playable, solo sweet spot C4-C6
role: [lead, melody, accent, countermelody, harmony]
synthesis: [modal, additive]
---

# Marimba

## MIDI / GM

- **Program**: 12 (GM1 Marimba)
- **Channel**: any melodic channel (0-9) — melodic percussion, NOT channel 9
- **FluidSynth**: TimGM6mb.sf2 renders GM12 → "Marimba" (preset name matches
  exactly, verified from phdr chunk)
- **Pipeline stem label**: `GM_PROGRAMS[12]` = "Marimba" → `trackXX_Marimba.wav` (no quirk)

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 45–96 | A2–C7 | standard 5-octave marimba (4.3-octave A2–C7 common) |
| Sweet spot | 60–84 | C4–C6 | middle octaves, warm round tone, best projection |
| Low | 45–59 | A2–B3 | dark woody bass bars, long decay, soft attack |
| Mid | 60–71 | C4–B4 | warm, round, singing — the classic marimba voice |
| High | 72–96 | C5–C7 | bright, dry, cutting; short decay, mallet click prominent |

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Single stroke (sustain) | 70–90 | full note | mallet strike, natural decay |
| Roll (tremolo) | 60–75 | 16th/32nd repeats | rapid alternating mallets, sustained illusion |
| Double stroke | 65–80 | 1/8–1/4 note | two quick strikes, rhythmic figure |
| Staccato | 60–70 | 1/8–1/16 note | short, dry, separated |
| Accent/marcato | 90–105 | full note, strong attack | hard mallet emphasis |
| Dead stroke (muted) | 40–55 | very short | mallet held on bar, choked |
| Glissando | — | sweep across bars | chromatic/scale sweep, fast |

## Timbre DNA

- **Harmonic content**: strong fundamental + odd partials; 4th mode is
  INHARMONIC (~4× fundamental) — the marimba's characteristic tuning
  (fundamental, 4×, 10×, 20× overtones); lower bars are purer
- **Attack**: 1–5 ms (mallet strike) — percussive, softer than xylophone
- **Decay**: exponential, 0.5–2.5 s — lower bars ring longer, high bars dry fast
- **Release**: natural decay (no sustain control); note ends = bar stops ringing
- **Noise component**: mallet click / attack transient (yarn vs. hard mallet)
- **Vibrato**: NONE native — any vibrato is rolled notes (tremolo), not pitch

## Role in Arrangement

- Lead melody (C4–C6 sweet spot — solo marimba repertoire, mallet ensembles)
- Accent/ornament (high register runs, glissandi, fills)
- Countermelody (interlocking lines, Steve Reich-style phase patterns)
- Harmony (mallets play 2–4 note chords; ostinato accompaniment)
- NOT bass (low bars too soft/wooden to anchor a mix; use vibraphone/double bass)
- NOT rhythm-section groove (no kit-like attack; rolls substitute for sustain)

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — best match, dedicated preset
   - `ResonatorBank.preset('marimba')`: fundamental + 2nd/3rd/4th/5th modes,
     decays 8–20 (fast) — the fixed preset is tuned at A4=440; pitch-shift the
     rendered note or scale mode frequencies by the played note
   - `ModalSynth.render_preset('marimba', duration, excitation='impulse')` —
     mallet strike is an impulse; 'noise' excitation approximates a hard mallet
   - Fast exponential decay is inherent to the preset (no ADSR needed)
2. **Additive** (`sound/synthesis/additive.py`) — decaying harmonic stack,
   fundamental-dominant with odd partials + 4× inharmonic mode, fast attack
3. **Avoid** PhaseModSynth (FM is for reed/brass/synth timbres, not struck bars)

## Production

- **Reverb**: room/plate 0.8–1.2 s tail (intimate; too much hall muddies the
  attack — contrast with vibraphone's 2 s+)
- **EQ**: cut 300–500 Hz boxiness; presence boost 2–4 kHz for mallet clarity;
  air shelf 6–8 kHz subtle (high bars already bright)
- **Pan**: center (solo); slight L/R spread for mallet sections/ostinati
- **Compression**: light 2:1 — keep the transient, tame the decay tail

## Verification

- GM12 renders as `trackXX_Marimba.wav` in RenderPipeline stems (label matches
  exactly, no quirk — see registry quirks table)
- ModalSynth 'marimba' preset: check strong fundamental + fast exponential
  decay, no sustain plateau
- Melodic percussion: channel 0-9 with program 12 — NOT channel 9 (ch9 would
  trigger the program-0 fallback label "Acoustic_Grand_Piano")
