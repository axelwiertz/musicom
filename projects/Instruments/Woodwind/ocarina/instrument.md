---
type: instrument
family: Woodwind
name: Ocarina
midi_program: 79
gms: "Ocarina"
range_min: 55
range_max: 96
solo_range: [64, 88]
role: [lead, melody, ornament, accent, countermelody]
synthesis: [phase_mod, additive]
---

# Ocarina

## MIDI / GM

- **Program**: 79 (GM Ocarina)
- **Channel**: melodic channel; monophonic vessel flute, sweet pure tone
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 79 = "Ocarina"
  (TimGM6mb fallback also has preset 79 = "Ocarina"). RenderPipeline stem
  label: GM_PROGRAMS[79] = "Ocarina" → `trackXX_Ocarina.wav` — matches exactly,
  **no quirk**. The ocarina is a unique wind timbre in the GM set (vessel flute,
  not a tube flute), and the GM79 slot is unused by any other registered
  instrument.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 55–96 | G3–C7 | modern 10-hole transverse ocarina (soprano/tenor) |
| Low | 55–67 | G3–G4 | breathy, soft, dark chamber tone |
| Middle | 68–79 | G#4–G5 | sweetest, clearest, main melodic register |
| High | 80–96 | G#5–C7 | brighter, thinner, more blowing effort |

The ocarina's range is inherently limited to about an octave + a fourth
(10-hole) to an octave + a sixth (12-hole) on a single instrument. The GM
patch spans a wider MIDI range via pitch transposition; realistic composition
should keep lines within roughly 55–84 (G3–C6) for the most idiomatic tone.
Bass ocarinas extend down another octave; the soprano/tenor range G3–G5 is
the most common.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 70–85 | full | smooth connected breath, sweet pure tone |
| Staccato | 60–75 | 1/5 | tongue-stop, clean cut — clay vessel cuts fast |
| Accent | 85–100 | 4/5 | sharp tongue puff, brighter attack transient |
| Breath | 45–60 | full | soft low-velocity, airy, intimate |
| Trill | 65–80 | 1/3 | finger trill — fast pitch oscillation of chamber |
| Portamento | 65–75 | 1.2× | breath-slurred glide (partial-tone bending) |

## Timbre DNA

- **Harmonic content**: near-sinusoidal fundamental with extremely weak upper
  partials (the globular closed chamber suppresses overblowing and high-mode
  resonance unlike any tube flute). Second partial typically 15–30 dB below
  fundamental — the purest tone in the woodwind family.
- **Attack**: 40–80 ms (fipple mouthpiece fills the chamber gradually; no reed
  transient, no tongue strike)
- **Decay**: moderate — 0.8–1.5 s breath-sustained; immediate stop on breath cut
- **Release**: near-instant when breath stops (no sympathetic resonance)
- **Vibrato**: breath-induced pitch dip (not amplitude — the Zelda vibrato is
  produced by diaphragm pulsations that dip the pitch 3–8 cents)
- **Character**: sweet, pure, flute-like but rounder and darker; instantly
  recognizable as "Zelda's Lullaby" / Enya / Legend of Zelda series

## Role in Arrangement

- Lead melody (mid register) — pure, singing folk/ethnic lines
- Ornamentation (trills, grace notes, portamento)
- Countermelody — pairs well with harp, strings, flute
- Accent — short pure-note punctuation in folk/ethnic arrangements
- NOT a harmony/pad instrument — monophonic by nature (single breath line);
  NOT a bass voice (chamber is too small for fundamental below ~200 Hz)
- Signature role: solo melodic color in pastoral, fantasy, folk, or Celtic
  arrangements (the "Zelda ocarina" cultural association is a strength)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **primary**. Sine
   carrier + sine modulator at ratio 1.0, shallow depth 0.8 = the near-sine
   vessel flute tone. Attack 0.06 s = gradual chamber fill. No reed or
   edge-tone transient — this is the correct physical model for a vessel
   fipple flute.

2. **Additive** — alternative. Strong fundamental (0.9 weight), weak rapidly
   falling harmonics (4 partials: 0.9, 0.3, 0.1, 0.03). Simulates the
   chamber filter. Same attack/release as PhaseModSynth.

3. **ModalSynth** — not recommended (vessel flute has no resonant body to
   model with modal banks; the chamber is the resonator and it's a single
   3D Helmholtz mode, not a struck-bar/string partial stack).

## Production

- **Reverb**: chamber 1.4–1.8 s — ocarina is an intimate instrument; a hall
  tail longer than 2.0 s washes out its pure tone (unlike the larger flute)
- **EQ**: cut ~500 Hz for clay mid-boxiness; boost ~3 kHz for fipple breath
  clarity; gentle 8 kHz shelf for air shimmer (NOT shrill — the ocarina's
  high end is naturally soft)
- **Pan**: center solo; ±0.1–0.15 spread in ensemble
- The ocarina's cultural association with fantasy/folk (Zelda) makes it a
  signature melodic color in game-music and Celtic-style compositions

## Verification

- GM79 → stem `trackXX_Ocarina.wav` (label matches, no quirk)
- FluidR3 preset 79 = "Ocarina" (verified from phdr chunk)
- Pure-tone spectral profile: 4–8 kHz buzz is naturally very low (near-sine
  fundamental); the spectral gate (≤20%) easily passes for a solo render
- Zero-drift: unit events end flush at BAR (terminal landmark)