---
type: instrument
family: Woodwind
name: Blown Bottle
midi_program: 76
gms: "Blown Bottle"
range_min: 48
range_max: 96
solo_range: [60, 84]
role: [lead, melody, ornament, accent, texture]
synthesis: [phase_mod, additive]
---

# Blown Bottle

## MIDI / GM

- **Program**: 76 (GM Blown Bottle — 0-indexed; the 77th entry of the GM
  list, inside the woodwind flute/whistle block 73–80: 73 Flute, 74 Recorder,
  75 Pan Flute, **76 Blown Bottle**, 77 Shakuhachi, 78 Whistle, 79 Ocarina).
  NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=76` in `add_voice`.
- **Channel**: melodic channel (0-9) — blown aerophone, NOT channel 9 percussion.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 76 =
  "Bottle Chiff" (phdr-verified — **quirk**: FluidR3's SF2 spelling is
  "Bottle Chiff", NOT "Blown Bottle"; cosmetic only, no routing impact).
  RenderPipeline stem label: GM_PROGRAMS[76] = "Blown Bottle" →
  `trackXX_Blown_Bottle.wav` — the pipeline label matches the GM name
  exactly, **no stem quirk**.
- GM neighbors: 75 Pan Flute (World), 77 Shakuhachi (World), 78 Whistle, 79
  Ocarina — the "simple flute / vessel" block. The bottle is the odd one:
  a Helmholtz cavity resonance, not a tube.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 48–96 | C3–C7 | GM patch writing band (patch plays 24–108, trimmed to usable tone) |
| Sweet spot | 65–79 | G4–G5 | cleanest Helmholtz tone, moderate breath |
| Solo range | 60–84 | C4–C6 | attack ≤ ~1 s, pitch identity cleanest |
| Low | 48–59 | C3–B3 | deep, slow swell (0.5–2.2 s attack), sub-octave layer heavy — roots/drone colour, write sparingly |
| Mid | 60–71 | C4–B4 | primary melody zone, attack ≤ ~1 s |
| High | 72–96 | C5–C7 | fast attack (40–500 ms), breathy sparkle; 84+ (C6+) noisy — accents only |

Empirical FluidR3 sweep (RMS, notes 24–108): preset 76 audible across the
whole span, no gaps, level flat within 7.9 dB. The writing band is trimmed to
48–96 because of tone quality, not audibility. Real physics: a blown bottle
is a Helmholtz resonator — pitch is set by cavity volume + neck geometry
(typical soda bottle ≈ 100–300 Hz = G2–E4; bigger bottles lower, small
bottles higher); a single bottle is ONE pitch, the GM patch transposes
chromatically. Dense chords are NOT idiomatic — the bottle is a monophonic
breath line (like shakuhachi, pan flute, ocarina).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Blow (sustain) | 72–85 | full note | steady sustained blow, near-pure cavity tone |
| Swell | 80–95 | full, ≥ 1–2 s | long swelling blow — THE idiomatic gesture; the patch's slow attack IS the sound |
| Puff (staccato) | 60–75 | 1/8–1/16 | short re-blown puff; reads as a blip — the slow attack smears anything shorter than ~1/8 at 120 bpm |
| Breath (airy) | 45–60 | full | half-blown, near-silent breath colour |
| Accent (hard blow) | 90–105 | 3/4–full | louder blow — still swells; no tongue exists, re-articulate for rhythm |
| Ghost | 30–45 | 1/16 | breath click, no real pitch |
| Flutter | 65–80 | 1/8 | rapid re-tongued re-blows (re-articulated puffs) |

## Timbre DNA

- **Harmonic content**: near-sinusoidal — the Helmholtz cavity resonance
  suppresses harmonics (measured: dominant component at the expected f0 for
  mid/high notes; strong SUB-OCTAVE layer on low notes 48–60). The purest
  tone of the flute block, even purer than the ocarina.
- **Attack**: two-stage — initial breath onset ~80–120 ms, but the FULL swell
  takes register-dependent 40 ms (C6+) to 500 ms (C5) to 0.5–2.2 s (C3–B4).
  Low notes are slow swells; high notes speak fast. **This is the identity**.
- **Sustain**: weak — the note "breathes": envelope swells to ~0.2 peak,
  dips, re-swells at ~0.5 s, then decays to ~0.1 with a slow ~1 Hz amplitude
  wobble (sample-loop breathing). Not a flat sustain like a flute.
- **Noise**: real breath turbulence — measured 4–8 kHz band = 4–7% of energy
  at low/mid notes, ~16% at 84+ (C6+). Higher register = breathier.
- **Vibrato**: none inherent; the ~1 Hz wobble is amplitude, not pitch.
  Pitch-bend can imitate the slight pitch rise of a harder blow.
- **Character**: hollow, pure, breathy, slightly goofy — instantly "bottle".
  Darker and rounder than the whistle (open tube), less piercing than the
  ocarina, with far more breath than either.

## Role in Arrangement

- Lead melody (mid zone 60–71) — novelty/folk/psychedelic colour lines, the
  "nature" melody voice (think cartoon soundtrack, folk trio, kids' music)
- Ornament (puffs, swells, breath ghosts, re-blown flutter)
- Color/texture (long swelling single notes, slow breath beds, "wind in a
  bottle" ambience)
- Countermelody (answers a whistle/ocarina/recorder from below, in octaves)
- NOT a harmony/pad instrument — monophonic breath line, no dense chords
  (double-stops are physically impossible on one bottle)
- NOT a bass voice (the low register is sub-octave rumble with a > 1 s swell;
  it cannot anchor rhythm)
- NOT a rhythmic voice — the slow attack smears fast gestures; re-articulate
  puffs for rhythm, never expect a percussive onset

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`, SP-002) — **primary**.
   Helmholtz-resonator aerophone (cavity tone excited by a jet): sine carrier
   + sine modulator at ratio 1.0 with mod_depth **0.7** — the shallowest of
   the flute set (ocarina 0.8, whistle 1.5, shakuhachi 2.0) — for the
   near-sinusoidal cavity tone; attack **0.12 s** — the slowest of the set —
   for the blow-in swell; release 0.20 s for the breath tail.

2. **Additive** (`sound/synthesis/additive.py`) — fallback. 4 partials
   (weights 0.9, 0.25, 0.1, 0.04) — the Helmholtz resonator suppresses
   harmonics, so the fundamental dominates harder than the ocarina's 0.9/0.3/
   0.1/0.03 set. Time envelopes: attack 0.12, release 0.20.

3. **ModalSynth** (`sound/synthesis/modal.py`) — struck-resonator ALT for
   short "bloop" puffs only (impulse on a single dominant mode + weak
   inharmonic partners); the bottle is BLOWN, not struck, so this is a
   percussive colour, not the instrument. Karplus-Strong is REJECTED — no
   string, and a KS loop's harmonic series is the wrong partial structure for
   a Helmholtz cavity.

## Production

- **Reverb**: small room 1.6–2.0 s — the bottle is a dry, close "nature"
  sound; big halls smear the breath detail (compare pan flute 2.0, whistle
  1.6, ocarina 1.6)
- **EQ**: cut 300–400 Hz −2.5 dB — the patch's sub-octave layer piles low
  energy fast (deeper than the whistle's 500 Hz −2.0); boost ~2.5 kHz +2 dB
  for the breath edge; gentle 7 kHz shelf +1.5 dB — DO NOT push 8 kHz+, the
  84+ register is already ~16% noisy
- **Delay**: optional dotted-8th at low mix for slow ambient swells; none for
  melody lines
- **Pan**: center solo; ±0.3 for a stereo bottle pair (two bottles, never a
  unison copy of the same pitch — comb-filter rule)

## Verification

- GM76 → stem `trackXX_Blown_Bottle.wav` (label matches, no quirk; FluidR3
  preset 76 = "Bottle Chiff" phdr-verified — cosmetic SF2 spelling quirk)
- Zero-drift: melody units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz)
- Spectral 4–8 kHz buzz well below 20% (breathy but clean at the sweet spot)
- Empirical FluidR3 sweep: audible 24–108, flat within 7.9 dB, chromatic
  pitch tracking confirmed (band-limited peak 0.90–1.10× f0 at every note —
  unlike woodblock/melodic-tom, GM76 really transposes)

## Instrument.md companion

`blown_bottle.py` — importable constants. Registered in
`instrument_registry.py` (2026-11-20) as `Woodwind.blown_bottle.blown_bottle`
→ key `blown_bottle`, constant `BLOWN_BOTTLE`.
