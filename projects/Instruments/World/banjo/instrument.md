---
type: instrument
family: World
name: Banjo
midi_program: 105
gms: "Banjo"
range_min: 46
range_max: 93
solo_range: [60, 84]
role: [lead, melody, ornament, rhythm, accent]
synthesis: [karplus, modal, phase_mod]
---

# Banjo

## MIDI / GM

- **Program**: 105 (GM1 Banjo — GM program numbers are 0-based; 105 is the
  106th entry, "Banjo")
- **Channel**: melodic channel (0-9) — plucked string instrument, NOT channel 9
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 105 =
  "Banjo" (TimGM6mb fallback also has preset 105 = "Banjo"). RenderPipeline
  stem label: GM_PROGRAMS[105] = "Banjo" → `trackXX_Banjo.wav` — matches
  exactly, **no quirk**. (Confirmed from GM_PROGRAMS list source + FluidR3
  phdr chunk + audible sweep.)
- GM neighbors: 104 Sitar, 105 Banjo, 106 Shamisen, 107 Koto, 108 Kalimba —
  all in the same "World plucked" block of GM1.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 46–93 | A#2–A6 | practical 5-string banjo |
| Sweet spot | 62–81 | D4–A5 | brightest head snap + string cut |
| Low | 46–59 | A#2–B3 | 4th/5th strings (C & g) — dark, thumpy head |
| Mid | 60–74 | C4–D5 | 3rd/2nd strings (G & B) — primary melodic register |
| High | 75–93 | D#5–A6 | 1st string (D) — bright, thin, cutting |

The 5-string banjo's standard open tuning is **gDGBD** (low to high: g3-D3-G3-B3-D4
= MIDI 55-50-55-59-62). The 5th (drone) string is the short high g, and the
4th string drops to C (C3=48) in "C tuning" — the practical low edge is
A#2 (46). FluidR3 preset 105 sounds audibly across **24–96** (empirical RMS
sweep, no gaps), so the SoundFont never clips a composition. Dense chords
are NOT idiomatic — the banjo is a roll/line instrument (Scruggs
three-finger and clawhammer styles).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pluck (standard) | 72–92 | natural decay | finger/roll stroke, head snap + string cut |
| Roll (Scruggs) | 66–82 | 1/8–1/16 | T-I-M-T-M-I-T-M pattern, rhythmic drive |
| Hammer-on | 82–98 | 1/4 | left-hand hammer, no pick transient, bright |
| Pull-off | 62–78 | 1/3 | softer descending snap |
| Choke (clawhammer) | 42–58 | 1/8 | damped stroke — dry, percussive thump |

## Timbre DNA

- **Harmonic content**: strong fundamental + bright mid/high partials; the
  taut head (Mylar/skin) adds a crisp membrane snap that decays fast
- **Attack**: 1–3 ms (fingerpick strike) — very fast, percussive; sharper
  and drier than the koto's tsume, comparable to the shamisen's bachi
- **Decay**: short-to-medium — 1–2 s; the 4th/5th strings thump and die,
  the 1st string rings brightest
- **Release**: natural string decay; palm choke for dry stops
- **Vibrato**: limited — the bridge floats on the head, so pitch bend is
  subtle; sustain is roll-driven, not bowed
- **Character**: bright, snappy, twangy — the bluegrass/old-time "country
  sitar"; between a shamisen (drier) and a koto (rounder)

## Role in Arrangement

- Lead melody (mid register) — melodic/Scruggs rolls, fiddle-tune lines
- Ornamentation (hammer-ons/pull-offs, drop-thumb accents)
- Rhythmic ostinato / groove rolls — its percussive attack locks with bass
  and mandolin (bluegrass rhythm section)
- Countermelody / call-response with fiddle, mandolin, or voice
- NOT a harmony/pad instrument — roll/line voice by design

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide = the correct physical model. `loop_gain`
   ~0.9960 (shorter, punchier ring than koto 0.9970 / sitar 0.9975) — dry,
   attacking, bluegrass bite; `width` ~0.4 for tight focus.
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — the
   "clean banjo" fallback (harmonic stack, loses the head snap).
3. **PhaseModSynth** — cheap banjo: saw carrier, mod ratio 2.2, depth 3.2,
   attack 0.002 (instant), release 0.18. Twangy, less authentic.

## Production

- **Reverb**: room 0.8–1.2 s — banjo is dry and rhythmic; long halls smear
  the head snap (contrast koto 1.4 / sitar 2.2)
- **EQ**: cut 250–300 Hz head/membrane boxiness; boost ~3 kHz for the head
  snap + string cut; gentle 8 kHz shelf for air (keep the twang, avoid harsh)
- **Delay**: not idiomatic; if used, short 1/8 at low mix
- **Pan**: center solo; 0.2–0.3 spread in ensemble writing

## Verification

- GM105 → stem `trackXX_Banjo.wav` (label matches, no quirk)
- FluidR3 preset 105 = "Banjo" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (≤20% — percussive pluck, no
  comb buzz)
- Zero-drift: plucked units end flush at BAR (terminal landmark)
- FluidR3 preset 105 audible across 24–96 (empirical RMS sweep, no gaps)

## Instrument.md companion

`banjo.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-06) as `World.banjo.banjo` → key
`banjo`, constant `BANJO`.
