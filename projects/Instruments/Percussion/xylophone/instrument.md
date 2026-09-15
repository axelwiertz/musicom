---
type: instrument
family: Percussion
name: Xylophone
midi_program: 13
gms: "Xylophone"
range_min: 53
range_max: 89
solo_range: [60, 84]
role: [lead, melody, ornament, accent, countermelody]
synthesis: [modal, karplus, phase_mod]
---

# Xylophone

## MIDI / GM

- **Program**: 13 (GM1 Xylophone — GM program numbers are 0-based; 13 is the
  14th entry, "Xylophone")
- **Channel**: melodic channel (0–9); struck wooden bars, dry ringing decay.
  NOT channel 9 — channel 9 triggers the drum-kit map and the
  `Acoustic_Grand_Piano` program-0 fallback stem label (timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 13 =
  "Xylophone" (verified from the phdr chunk). RenderPipeline stem label:
  GM_PROGRAMS[13] = "Xylophone" → `trackXX_Xylophone.wav` — matches exactly,
  **no quirk**.
- GM neighbors: 8 Celesta, 9 Glockenspiel, 10 Music Box, 11 Vibraphone,
  12 Marimba, 14 Tubular Bells — the pitched-mallet block. Xylophone is the
  brightest, shortest-ringing member (wood, hard mallets).

## Range

Standard 4-octave concert xylophone, sounding pitch (bars are NOT
transposing — written pitch = sounding pitch, unlike the octave-transposing
glockenspiel).

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 53–89 | F3–F6 | standard 4-octave xylophone |
| Low | 53–64 | F3–E4 | woody knock, weakest ring |
| Middle (melody) | 65–76 | F4–E5 | primary melodic register, balanced cut |
| High | 77–89 | F5–F6 | bright brittle clatter, maximal cut |

Practical ceiling is F6 (89); above that only toys/kalimba-register specials
exist. Rolls (measured tremolo between two mallets) are the only way to
sustain — decay is ~0.4 s, the shortest of the melodic-percussion set.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Single stroke | 75–90 | 1/2 | standard polyball stroke, bright + dry |
| Roll (measured) | 55–75 | 2× | mallet tremolo, the xylophone's only sustain |
| Double stop | 65–80 | 0.8× | two mallets together, dry 2-note chord |
| Glissando | 60–75 | 1/4 | wedge/thumb slide across the bars, ripple |
| Wood block | 85–95 | 1/5 | edge knock, pure click — percussive accent |

## Timbre DNA

- **Harmonic content**: arch-tuned INHARMONIC partial stack **1 : 3 : 6** —
  the fundamental, an octave+fifth (12th) and a compressed near-3-octave
  (17th) partial. The thin bar is ARCH-CUT underneath so the octave partial
  is DISCARDED (tuned away) and the 12th is boosted — the rosewood mirror of
  the vibraphone's 1 : 4 : 10 aluminium arch. Marimba bars (wider, lower
  arch) keep a harmonic 1:2:3 stack instead.
- **Attack**: ~1 ms — hard polyball/rattan on rosewood, the sharpest onset
  in the mallet family
- **Decay**: very short — ~0.3–0.5 s ring mid-register (marimba ~1 s,
  vibraphone pedal-sustained multi-second)
- **Release**: natural bar decay, no damper/pedal (like the harp, the player
  stops sound only by choice of stroke)
- **Vibrato**: none (unlike vibraphone motor tremolo)
- **Character**: bright, hollow, woody, cutting clatter — dry and brittle;
  the "bone" of the mallet family, 1 octave above the marimba

## Role in Arrangement

- Lead melody (mid register) — staccato melodic lines, octave doubling of
  other voices for sparkle (NOT unison same-pitch doubling)
- Ornamentation — glissando ripples, edge-knock accents
- Percussive countermelody against sustained strings/brass
- Accent — edge knocks and high-register clatter punctuations
- Rolls for short legato swells (only sustain mechanism)
- NOT a bass voice (bottom bar F3, weak fundamental, dry); NOT a harmony
  pad — rings too short for chord sustain beyond double-stops

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with a custom `XYLOPHONE_MODES` bank at the arch-tuned
   ratios **1 : 3 : 6** (fundamental, octave+fifth, compressed near-3-octave)
   and decay rates 9/14/20 (rosewood-dry: faster than the marimba preset's
   8–20 on the fundamental, slower on the top partial). The stock `'marimba'`
   preset is the closest bank but has the WRONG partial structure (harmonic
   1:2:3 — xylophone discards the octave) and too-slow decay.
2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   demoted fallback. The bar is struck, not plucked, so a KS waveguide is
   the wrong excitation family; loop_gain 0.9935 gives the bright short ping
   (shortest of the struck/plucked set: below kalimba 0.9940).
3. **PhaseModSynth** — cheap xylophone: sine carrier, mod ratio 7.0,
   depth 1.2, attack 0.001, release 0.25. Clacky, less authentic.

## Production

- **Reverb**: room 0.8–1.0 s — the xylophone is the DRIEST melodic
  instrument in the KB; long tails smear the clatter into wash. Keep it tight
  even in ensemble mixes.
- **EQ**: light 200 Hz clean-up (rosewood body is tight, little boxiness);
  boost ~2.5 kHz for polyball attack + 12th-partial cut; 9 kHz shelf for the
  brittle clatter air (beyond the marimba's 8.5 kHz shelf — xylophone plays
  an octave up)
- **Pan**: center solo; single-row bars pan narrow, +0.15–0.25 spread for
  ensembles (orchestral players sit with marimba/bells in the back-percussion
  arc)
- **Layering**: doubles piano/celesta lines an octave up for sparkle; avoid
  unison same-pitch doubling (comb-filtering buzz — the 2026-09-01 lesson)

## Verification

- GM13 → stem `trackXX_Xylophone.wav` (label matches, no quirk)
- FluidR3 preset 13 = "Xylophone" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (bright clatter, no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Empirical FluidR3 pitch sweep (RMS, notes 53–89): preset 13 audible across
  the full span, no gaps — SF2 never clips a composition

## Instrument.md companion

`xylophone.py` — importable constants. Registered in `instrument_registry.py`
(2026-09-15) as `Percussion.xylophone.xylophone` → key `xylophone`, constant
`XYLOPHONE`.
