---
type: instrument
family: World
name: Shamisen
midi_program: 106
gms: "Shamisen"
range_min: 45
range_max: 89
solo_range: [57, 84]
role: [lead, melody, ornament, drone, countermelody]
synthesis: [karplus, modal, phase_mod]
---

# Shamisen

## MIDI / GM

- **Program**: 106 (GM1 Shamisen — GM program numbers are 0-based; 106 is
  the 107th entry, "Shamisen")
- **Channel**: melodic channel; 3-string plucked lute, punchy twang + sharp
  decay
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 106 =
  "Shamisen" (TimGM6mb fallback also has preset 106 = "Shamisen").
  RenderPipeline stem label: GM_PROGRAMS[106] = "Shamisen" →
  `trackXX_Shamisen.wav` — matches exactly, **no quirk**. (Confirmed from
  GM_PROGRAMS list source + FluidR3 phdr chunk + audible sweep.)
- GM neighbors: 104 Sitar, 105 Banjo, 106 Shamisen, 107 Koto, 108 Kalimba —
  all in the same "World plucked" block of GM1.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 45–89 | A2–F6 | practical shamisen |
| Low | 45–56 | A2–G#3 | niagari (thick 1st) string — dark, gut thump |
| Middle | 57–75 | A3–D5 | primary melodic register (middle string) |
| High | 76–89 | D#5–F6 | third string — bright, thin, cutting |

FluidR3 preset 106 sounds audibly across **24–96** (empirical RMS sweep,
no gaps), so the SoundFont never clips a composition. The physical
instrument's 3 strings span ~2 octaves (A2–D4 open on a niagari shamisen);
the classical *honchoshi* open tuning is D-A-D (D3-A3-D4 = MIDI 50-57-62).
Practical melodic focus is A3 (57) – C6 (84). Dense chords are NOT
idiomatic — the shamisen is a line instrument (sawari buzz + bachi attack).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Bachi pluck (standard) | 72–92 | sharp decay | wooden plectrum stroke, percussive snap |
| Tsubushi (slap) | 88–100 | 1/3 | hard bachi strike on the skin head — percussive thump |
| Suzume (grace) | 80–95 | 1/4 | fast ornamental grace notes, chirping |
| Uchijime (damp) | 50–70 | 1/8 | left-hand damp after pluck — short, dry |
| Hikiyose (bend) | 65–85 | 1.5× | pitch bend up ~1–3 semitones, vocal |
| Tremolo (suki) | 70–85 | 2.0× | fast repeated strokes, sustained tension |

## Timbre DNA

- **Harmonic content**: strong fundamental + bright mid/high partials;
  the *sawari* (sympathetic buzz near the nut, like the koto's) adds a
  subtle metallic rattle
- **Attack**: 1–5 ms (bachi strike) — very fast, percussive, wood-on-skin
  transient; sharper and drier than sitar's mizrab
- **Decay**: short-to-medium — 1–2.5 s; third string shorter and thinner
  than the koto's 2.5–3.5 s ring
- **Release**: natural string decay; uchijime palm damp for dry stops
- **Vibrato**: left-hand pitch wobble (hikiyose), not amplitude vibrato
- **Character**: punchy, nasal, twangy — the kabuki/min'yo "country banjo
  of Japan"; between a banjo (drier) and a koto (rounder)

## Role in Arrangement

- Lead melody (mid register) — folk/min'yo and theatre lines
- Ornamentation (suzume grace snaps, uchijime accents)
- Rhythmic ostinato / groove plucks — its percussive attack locks with taiko
- Drone layer (open honchoshi D-A-D strings)
- Countermelody / call-response with koto, shakuhachi, or voice
- NOT a harmony/pad instrument — monophonic line voice by design

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide = the correct physical model. `loop_gain`
   ~0.9955 (shorter, punchier ring than koto 0.9970 / sitar 0.9975) —
   dry, attacking, folk-min'yo bite; `width` ~0.4 for tight focus.
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — the
   "clean shamisen" fallback (harmonic stack, loses the sawari rattle).
3. **PhaseModSynth** — cheap shamisen: saw carrier, mod ratio 2.5, depth
   3.0, attack 0.002 (instant), release 0.2. Twangy, less authentic.

## Production

- **Reverb**: room/short hall 0.9–1.4 s — shamisen is dry and rhythmic;
  long halls smear the bachi attack (contrast koto 1.4 / sitar 2.2)
- **EQ**: cut 250–350 Hz body boxiness; boost ~2.8 kHz for the bachi snap +
  sawari rattle; gentle 8 kHz shelf for air (keep the twang, avoid harsh)
- **Delay**: not idiomatic; if used, short 1/8 or dotted-8th at low mix
- **Pan**: center solo; 0.2–0.3 spread in ensemble writing

## Verification

- GM106 → stem `trackXX_Shamisen.wav` (label matches, no quirk)
- FluidR3 preset 106 = "Shamisen" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (≤20% — percussive pluck, no
  comb buzz)
- Zero-drift: plucked units end flush at BAR (terminal landmark)
- FluidR3 preset 106 audible across 24–96 (empirical RMS sweep, no gaps)

## Instrument.md companion

`shamisen.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-04) as `World.shamisen.shamisen` → key
`shamisen`, constant `SHAMISEN`.
