---
type: instrument
family: Strings
name: Pizzicato Strings
midi_program: 45
gms: "Pizzicato Strings"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [rhythm, ostinato, bass, accompaniment, countermelody, accent]
synthesis: [karplus, modal, phase_mod]
---

# Pizzicato Strings

## MIDI / GM

- **Program**: 45 (GM1 Pizzicato Strings — 0-based; the 46th GM entry)
- **Channel**: melodic channel (0–9). NOT channel 9 — ch9 triggers the drum
  map. Program 45 on a melodic channel = the string section plucking.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 45 =
  "Pizzicato Section" (phdr-verified). RenderPipeline stem label:
  GM_PROGRAMS[45] = "Pizzicato Strings" → `trackXX_Pizzicato_Strings.wav` —
  **matches exactly, no quirk**. SF2 internal name "Pizzicato Section" vs
  pipeline "Pizzicato Strings" is cosmetic only (same preset, same sound),
  **no routing impact**. (Confirmed from GM_PROGRAMS list source + SF2 phdr
  chunk.)
- GM neighbors: 44 Tremolo Strings (bowed tremolo), 46 Orchestral Harp —
  the plucked/articulated block of the GM string family (40 Violin, 41
  Viola, 42 Cello, 43 Contrabass are the solo bowed voices).
- GM spec range: C2–C7 (36–96) — the section patch spans the full string
  family from contrabass to violin.

## Range

The patch is the whole SECTION (contrabass + cello + viola + violin playing
together). Real pizzicato behavior differs radically across registers —
longer/thicker strings are louder, fuller, and sustain more; the violin's
high strings barely sustain at all (Tim Davies, deBreved: "the violin
produces only a little sustain in the low register and none from the middle
up"; the highest DECENT violin pizz note is ~C6, above it the tone thins
progressively).

| Zone | MIDI | Pitches | Register | Character |
|---|---|---|---|---|
| Full range | 36–96 | C2–C7 | section span | GM patch, all audible |
| Low (bass) | 36–54 | C2–F#3 | bass/cello | thick, present, SOME sustain — the ostinato/bass-line zone |
| Mid (melody) | 55–76 | G3–E5 | viola/violin | balanced round pluck — accompaniment/countermelody home |
| High | 77–96 | F5–C7 | violin high | dry, thin, NO sustain — sparkle/accent only; >C6 (84) very thin |

Composition rules from the register physics:

- **Bass pizz is the star**: the contrabass/cello pizz has the most presence
  and sustain of the whole section — low ostinato lines and plucked bass
  figures are the instrument's most idiomatic use.
- **Cello→bass hand-off is a big timbre change** (the switch to contrabass
  is "a big change" — continue lines across it with care).
- **High violin pizz is an effect**, not a lead register: short, thin,
  zero sustain — use for sparkle/accent, not for carried melody.
- Write pizz passages as short notes; notate ring (l.v./ring-over) on the
  low strings only. Real section pizz has natural looseness in timing —
  give it a rhythmic lift, don't machine-grid it.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pizz (standard) | 70–80 | 0.3× | fingertip pluck, dry ring, the default |
| Ostinato | 65–75 | 0.2× | repeated rhythmic figure — short, even, lifted |
| Secco / staccato | 55–65 | 0.12× | choked stop — very short, dry tick |
| Bass pizz (l.v.) | 80–90 | 0.9× | low-string pluck let to ring — thick, full |
| Bartók snap | 95–110 | 0.08× | hook-under + slap on fingerboard: loud, percussive, little pitch |
| Left-hand pizz | 50–60 | 0.3× | weak pull-off, descending single notes, pro effect |
| Double-stop | 75–85 | 0.4× | two-string pluck (division); keep small |
| Accent (marcato) | 90–100 | 0.25× | hard pluck — driving downbeat |

Loudness ceiling: the loudest real pizz ≈ a bow's mezzo-forte — do not
balance pizz against full arco/brass at forte and expect realism. Snap
(Bartók) pizz has a large volume jump on cello/bass; a handful of low
strings snapping is plenty.

## Timbre DNA

- **Excitation**: fingertip (flesh) pluck across a bowed string — a soft
  round attack with a tiny fingernail transient; NO bow noise, NO sustain
  bowing.
- **Harmonic content**: full string partial stack (the whole string speaks),
  with the register-dependent brightness of the instruments themselves —
  contrabass = dark fundamental-rich thump; violin high = nearly pure thin
  pitch with almost no body.
- **Decay**: dry and short. Low strings: 0.5–1.5 s (open strings ring
  longest). Mid: 0.3–0.8 s. High violin: near-zero sustain.
- **Ensemble character**: 10+ players plucking together = slight timing
  looseness + natural detune chorus — the "section pizz" glitter. Sample
  libraries often over-sustain and over-compress this; the real sound is
  drier and looser.
- **Character**: rhythmic, articulate, percussive-but-pitched — the string
  family's answer to a guitar/bass pluck, without any fret buzz.

## Role in Arrangement

- Rhythm / ostinato — the #1 use: repeated plucked figures (the "pizzicato
  accompaniment" staple from Tchaikovsky 4 to every film score)
- Plucked bass line (contrabass/cello pizz) — walking bass / root-fifth
  ostinato with the double basses
- Accompaniment — chordal division plucks, arpeggiated fills
- Countermelody / call-response against arco lines, woodwinds, or brass
- Accent — marcato downbeats, snap-pizz punctuation
- NOT a sustain/pad voice and NOT a dense-chord voice — the section sound
  is at its best in 1–4 notes at a time; big dense pizz chords get messy
  (players divide anyway)

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. A plucked waveguide is the exact physical model for a
   finger-plucked string. `loop_gain` 0.9960 (moderate damping = dry
   section ring, 0.3–1.5 s), `excitation` "pluck" (flesh, rounder than a
   pick), `lowpass_hz` 7500 (wood-body warmth — pizz is not glassy),
   `noise_component` 0.03 (finger contact transient), `width` 0.55
   (section spread).
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — harmonic
   stack with impulse excitation: the clean plucked-string fallback.
3. **PhaseModSynth** — cheap pizz: sine carrier, ratio 1.0, depth 1.2,
   attack 0.002, release 0.20. Mellow, less authentic.

## Production

- **Reverb**: hall 2.0 s ceiling — pizz needs the orchestra space but the
  verb must NOT smear the pluck transient; 2.0 s (same as violin) is as
  wet as this instrument should ever get. Dry room 0.8–1.2 s for intimate/
  exposed pizz passages.
- **EQ**: cut ~300 Hz body boxiness; boost ~2.5 kHz for the fingertip
  wood+string attack presence; gentle 8 kHz shelf only — the high violin
  register is already thin, don't hype the air.
- **Delay**: not idiomatic; if used, a dotted-8th at low mix for ostinato
  texture only.
- **Pan**: center solo; -0.15 to -0.25 (stage-left) in classical seating;
  in pop/rock production, double-track the ostinato at ±0.3 for width.

## Verification

- GM45 → stem `trackXX_Pizzicato_Strings.wav` (label matches, no quirk)
- FluidR3 preset 45 = "Pizzicato Section" (phdr-verified; internal name
  differs from pipeline label cosmetically, no routing impact)
- Solo render passes 4–8 kHz spectral gate (single voice, no comb buzz)
- Empirical FluidR3 pitch sweep: preset 45 audible across 36–96, no gaps
- Zero-drift: plucked units end flush at BAR (terminal landmark)

## Instrument.md companion

`pizzicato_strings.py` — importable constants. Registered in
`instrument_registry.py` (2026-10-10) as
`Strings.pizzicato_strings.pizzicato_strings` → key `pizzicato_strings`,
constant `PIZZICATO_STRINGS`.