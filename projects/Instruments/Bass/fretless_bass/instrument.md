---
type: instrument
family: Bass
name: Fretless Bass
midi_program: 35
gms: "Fretless Bass"
range_min: 24
range_max: 72
solo_range: [28, 60]
role: [bass, melody, countermelody, groove, slide, color]
synthesis: [karplus, bowed, modal]
---

# Fretless Bass

## MIDI / GM

- **Program**: 35 (GM1 Fretless Bass; 0-indexed — matches FluidR3 preset 35
  and the RenderPipeline `GM_PROGRAMS[35]`). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=35` in `add_voice`.
- **Channel**: any melodic channel (0–9). Monophonic in practice — one note
  per string, one string bowed/plucked at a time; double-stops only on
  adjacent strings, and chords are NOT idiomatic (a fretless bass "chord" is
  a thumb-position dyad at most, usually a studio overdub).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 35 =
  **"Fretless Bass"** (phdr-verified). RenderPipeline stem label:
  `GM_PROGRAMS[35] = "Fretless Bass"` → sanitized
  `trackXX_Fretless_Bass.wav` — matches exactly, **no quirk**.
- **Identity**: the fretless electric bass — a solidbody bass with the
  frets pulled out and the fingerboard filled/sanded smooth (Jaco Pastorius
  famously did this to a 1962 Fender Jazz Bass with a pair of pliers and
  wood filler). The string stops on bare fingerboard, so pitch is set by
  finger POSITION, not by a fret crown: this gives (a) continuous
  portamento/glissando — the signature "slide", (b) the nasal, vocal
  "mwah" midrange from the softer fingerboard contact, (c) no fretwire
  click on attack, replaced by a rounder, more contrabass-like thump.
  It is the bass cousin of the cello and of the Chinese *erhu* in
  expressive intent, but with magnetic pickups and an amp.
  Iconic players: Jaco Pastorius, Pino Palladino, Mick Karn, Sting,
  Tony Franklin, Gary Willis, Percy Jones.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 24–72 | C1–C5 | GM patch span; 5-string low B = MIDI 23 extends one semitone lower |
| Sub / low E | 24–35 | C1–B1 | Open E1 (28) and 5-string B0 (23): fundamental weight, chest thump |
| Groove (root pocket) | 36–50 | C2–D3 | Primary rhythm register — root–fifth lines, walking bass |
| Singing mid | 51–62 | D#3–D4 | The "mwah" zone: long slides, vibrato, melodic fills |
| Upper (thumb position) | 63–72 | D#4–C5 | Thin, cello-like; exposed solos only, not for sustained support |

Standard 4-string tuning is **E1–G3 = MIDI 28–55** (E1 28, A1 33, D2 38,
G2 43; 24-fret fingerboard reaches ~G4 67 on the G string); a 5-string adds
low B0 = MIDI 23. The GM patch (FluidR3) speaks cleanly across 24–72 and
gets thin above C5 (72). The **sweet spot is 28–55** (E1–G3) — the four-string
pocket where the fingerboard tone has full body and the slide is most
audible. Below E1 the patch rolls off fast; above C4 the tone turns nasal
and loses fundamental.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain (pizzicato long) | 62–78 | full note | Round fingerboard pluck, long ringing "mwah" |
| Staccato / muted | 70–85 | 0.2–0.4 | Palm or fingerboard damping — tight, dry, no ring |
| Slide (glissando) | 65–80 | full, connecting | The signature: finger drags along the board between two pitches |
| Portamento (legato slide) | 58–72 | full, smooth | Continuous pitch bend into the target note — vocal, fretless-only |
| Vibrato | 70–85 | full note | Finger-roll vibrato, 5–6 Hz, widens on long notes |
| Harmonic (natural) | 55–70 | 0.8–1.5 | Bell-like node touch at 12th/7th/5th positions |
| Double-stop | 72–88 | 0.5–1.0 | Two adjacent strings, usually a third/sixth — thumb position |
| Ghost (dead note) | 30–45 | 0.1–0.2 | Percussive fingerboard tap, no pitch — groove filler |
| Arco (bowed) | 60–80 | full note | Double-bass bow on the electric string: sustained, reedy, cello-like |

## Timbre DNA

- **Harmonic content**: fundamental plus a full but quickly-rolling-off
  harmonic series; the bare fingerboard damps the upper partials faster
  than a fretted string, so the spectrum is **mid-forward and nasal**
  (the 300–900 Hz "mwah" formant) with a soft top end above ~4 kHz.
  Dead spots at the fingerboard's resonant nulls are part of the character.
- **Attack**: no fret click. The transient is a soft, round thump — the
  flesh of the finger stopping a string against wood, plus a little
  fingerboard squeak as the finger slides.
- **Decay**: long, even sustain (a plucked fretless rings like a fretless
  because the fingerboard contact is compliant, not a hard fret edge).
  Bowed notes sustain indefinitely at constant amplitude.
- **Pitch instability**: the defining trait. No frets = no fixed pitch;
  players approach notes from below with a slide, overshoot, and settle.
  Microtonal drift and blue-note bends are idiomatic, not mistakes.
- **Noise**: fingerboard squeak on slides, string squeal on position
  shifts, breathy bow noise when arco.
- **Character**: vocal, mournful, "singing", liquid. Jaco's "Portrait of
  Tracy", Pino's fretless on "Wherever I Lay My Hat", Mick Karn's
  rubbery Japan lines, Sting's "Fragile".

## Role in Arrangement

- **Bass** (primary): root–fifth support with slide-based approach notes.
  Sits exactly where the electric bass sits, but with a rounder, more
  vocal attack — it fills the gap between electric bass and cello.
- **Melody** (rare but real): fretless is the one bass that can carry a
  melody — "Portrait of Tracy", "Teen Town" lines. Keep it in the singing
  mid zone 51–62 and give it space.
- **Countermelody**: answers the lead in the same register as a cello or
  trombone; excellent under a vocal.
- **Groove**: slides into downbeats, ghost notes, long glissandi as fills.
- **Color**: ballads, jazz fusion, sophisti-pop, world music, film score.
- NOT a chord/pad voice; NOT a high-register lead above C4; NOT a
  slapping voice (slap needs frets — the "pop" transient is fretwire).

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. A plucked string waveguide is the correct physical model:
   the delay line's low-pass loss term IS the fingerboard damping, and a
   long `loop_gain` gives the fretless ring. `KARPLUS_DEFAULTS`: loop_gain
   0.9975 (longer sustain than the fretted 0.9970 — bare fingerboard damps
   less at the top), width 0.55, role "bass". The fingerboard's soft stop
   is approximated by a darker lowpass than the fretted bass.
2. **BowedString** (`sound/synthesis/bowed.py`) — for the **arco**
   articulation only. Stick–slip excitation with slow attack and a
   cello-like formant; not the default voice.
3. **ModalSynth** (`sound/synthesis/modal.py`) — weak fallback. Preset
   `'string'` gives a generic plucked-body harmonic stack, no pickup
   colour; usable only as a pad double in dense mixes.

## Production

- **Reverb**: room/plate 1.6 s — slightly longer than the fretted bass
  (the vocal quality wants air); still mostly a mix decision, never baked
  into a bass DI.
- **EQ**: cut 250 Hz (low-mid box resonance), **boost 700–900 Hz** (the
  "mwah" formant — the single most important fretless EQ move), gentle
  5 kHz shelf for fingerboard squeak and string detail. High-pass at
  ~35 Hz in a dense mix (the fundamental is 41 Hz at E1).
- **Compression**: gentle (2:1–4:1) to even out the slide dynamics; the
  expressive slides swing 10+ dB otherwise.
- **Pan**: center (100% mono). Bass is universally centered.
- **Chorus/delay**: a touch of chorus is the classic 80s fretless sound
  (Pino); keep it off the sub register.
- **FluidSynth/SF2**: FluidR3 preset 35 is a real multi-sampled fretless
  with slides baked into some velocity layers; the patch does NOT respond
  to portamento (CC5/CC65) — write slides as fast chromatic runs of short
  notes, not as a single long note with pitch-bend, unless the renderer
  supports pitch-bend explicitly.

## Verification

- GM35 → stem `trackXX_Fretless_Bass.wav` (label matches, no quirk;
  FluidR3 preset 35 = "Fretless Bass" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — the 2026-09-01 comb-filter rule)
- Karplus-Strong smoke test: bass-register render is audible and decays
- Spectral 4–8 kHz buzz well below 20% (dark, mid-forward voice)
