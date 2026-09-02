---
type: instrument
family: World
name: Sitar
midi_program: 104
gms: "Sitar"
range_min: 55
range_max: 96
solo_range: [60, 89]
role: [lead, melody, ornament, drone, countermelody]
synthesis: [karplus, phase_mod, modal]
---

# Sitar

## MIDI / GM

- **Program**: 104 (GM1 Sitar)
- **Channel**: melodic channel; monophonic plucked lute, long ringing decay
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 104 = "Sitar"
  (TimGM6mb fallback also has preset 104 = "Sitar"). RenderPipeline stem
  label: GM_PROGRAMS[104] = "Sitar" → `trackXX_Sitar.wav` — matches exactly,
  **no quirk**. Prior art: IndianClassical/018 (GM104 melody + tanpura drone)
  and SP050 (GM104 melody + GM33 bass) both use 104.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | concert sitar (Kharaj Pancham setup) |
| Low (kharaj) | 55–61 | G3–B3 | bass strings — dark, long meend slides |
| Middle (jod/baaj) | 62–77 | D4–G5 | primary melodic register |
| High (chikari) | 78–96 | G#5–C7 | drone + high melody — bright, thin, cutting |

Practical melodic ceiling ~C6 (84) on most instruments; 78–96 zone is
chikari drone strings + very high melody. Meend (bend) extends any note up
~7 semitones (Vilayat Khan gayaki ang).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pluck (mizrab) | 70–90 | full decay | standard stroke, metallic twang + jawari buzz |
| Meend (bend) | 65–80 | 1.5–2× | pitch glide across fret — vocal melisma |
| Gamak (hammer) | 80–95 | 1/4–1/3 | fast oscillation, ornamental |
| Chikari stroke | 55–70 | 1/8 | drone string, rhythmic punctuation |
| Mute (damp) | 40–55 | 1/8 | choked stroke, dry percussive |

## Timbre DNA

- **Harmonic content**: dense inharmonic-ish partial stack (plucked string);
  strong mid partials, sustained ringing (low damping); bridge geometry
  (jawari) shapes the overtone spectrum into a subtle buzz
- **Attack**: 1–5 ms (mizrab strike) — very fast, percussive onset
- **Decay**: long — 3–6 s sustain of ringing partials; no sustain pedal
- **Release**: natural string decay; sympathetic strings (tarb) ring on
- **Vibrato**: meend-based (pitch bend), not amplitude vibrato
- **Character**: metallic, nasal, twangy, buzzing; instantly "Indian"

## Role in Arrangement

- Lead melody (mid register) — raga/sa-re-ga lines
- Ornamentation (gamak, meend, fast tans)
- Drone layer (chikari strings + tanpura doubling an octave below)
- Countermelody / call-response with voice or flute
- NOT a harmony/pad instrument — monophonic by design (play one line)

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide = the correct physical model. High
   `loop_gain` (~0.9975) = low damping = ringing partials = sitar-like
   sustain; `width` ~0.45 for a touch of spread.
2. **PhaseModSynth** — cheap sitar: saw carrier, mod ratio 2.0, depth 4,
   attack 0.002 (instant), release 0.25. Twangy, less authentic.
3. **ModalSynth** `'string'` preset — generic plucked-string resonator;
   usable fallback, loses the buzz character.

## Production

- **Reverb**: hall 2.0–2.5 s — darbar-hall space; tail supports the ring
- **EQ**: cut 300–400 Hz gourd boxiness; boost ~2.5 kHz for jawari buzz +
  pluck clarity; gentle 9 kHz shelf for sympathetic shimmer
- **Delay**: dotted-8th echoes are idiomatic (SP050 spectral-delay approach)
- **Pan**: center solo; 0.2–0.35 spread in ensemble writing

## Verification

- GM104 → stem `trackXX_Sitar.wav` (label matches, no quirk)
- FluidR3 preset 104 = "Sitar" (verified from phdr chunk)
- Buzz check: rendered sitar WAV is *supposed* to have twangy partial
  energy — the 4–8 kHz spectral gate (≤20%) still passes for a solo pluck
- Zero-drift: plucked units end flush at BAR (terminal landmark)
