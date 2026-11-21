---
type: instrument
family: Keys
name: Electric Grand Piano
midi_program: 2
gms: "Electric Grand Piano"
range_min: 21
range_max: 108
solo_range: [48, 84]
role: [harmony, melody, bass, rhythm, accent, color]
synthesis: [karplus, modal, phase_mod]
---

# Electric Grand Piano (Yamaha CP-70 / CP-80)

## MIDI / GM

- **Program**: 2 (GM1 "Electric Grand Piano" — the amplified/electrified grand
  piano, the Yamaha CP-70/CP-80 family; GM program numbers are 0-based, so 2
  is the 3rd entry). NOT in `structures/instrument.py` `MidiInstrument` enum
  (10 only) — use raw `program=2` in `add_voice`.
- **Channel**: any melodic channel (0-9). Channel 9 with program 2 would
  trigger the drum-kit map and the program-0 fallback label
  `Acoustic_Grand_Piano` (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 2 (phdr-
  verified; see Verification section for the exact SF2 spelling).
- **Pipeline stem label**: `GM_PROGRAMS[2]` = "Electric Grand Piano" → disk
  stem `trackXX_Electric_Grand_Piano.wav` — sanitizer only rewrites
  spaces/parens/slashes, so the label matches exactly, **no quirk**;
  STEM_LABEL in electric_grand.py matches the pipeline's real label so
  stem-file lookups work.

## Identity

The **Yamaha CP-70** (1974) and **CP-80** are *real acoustic grand pianos*
sold without a soundboard: full-size strings, real hammers, real dampers, and
a grand action — but each string group sits over a **magnetic pickup**
(electric-guitar style, one pickup per note) wired to a built-in preamp and
then to an external amplifier. The Kawai EP-608 and Helpinstill retrofit
systems share the same idea.

The defining elements:

- **Real piano string, no soundboard**: the string is struck by a felt
  hammer exactly like a grand piano, but the soundboard (the main energy sink
  of an acoustic piano — it converts string vibration into radiated air
  pressure) is absent. The string keeps vibrating with very low damping, so
  the **sustain is long and clean** (3-8 s), and the tone is captured
  *directly* by the pickup.
- **Magnetic pickup**: the pickup senses the moving steel string in a
  magnetic field. This colours the tone bright and glassy — the attack
  transient (hammer on wound steel, captured close) is metallic and
  cutting, the fundamental is strong and clean, and there is no soundboard
  "bloom"/body resonance under the note. High partials are bounded by the
  pickup's bandwidth (~5-6 kHz roll-off).
- **Amplifier + speakers**: as heard on records the CP went through a
  keyboard amp / PA / console — midrange colouration and, on loud notes,
  gentle preamp edge. No tube breakup character like an overdriven Rhodes;
  the CP stays clean.
- **Dynamics**: between the acoustic grand and the Rhodes. No tine-pickup
  compression (the CP's magnetic pickup is less lossy), so velocity 40-120
  spans a usable pp-ff — but the tone stays bright at every level (the
  attack never gets as "soft" as a felt hammer on a soundboard piano).

Consequences for composition:

- **Glassy attack is the identity**: the first ~10-50 ms is a bright
  metallic hammer strike, then the clean fundamental takes over. This is why
  the CP cuts through a rock/funk band where an acoustic grand would get
  buried — the close-mic'd attack has no room to soften.
- **Long clean sustain**: sustained chords and melodies ring without the
  acoustic piano's warm bloom. The "electric grand pad" (sustain pedal,
  mid-register chords) is a signature 70s texture (Supertramp, 10cc,
  Steely Dan).
- **Huge clear bass**: the low register is round and *present* (the pickup
  captures the full string vibration). The CP-80 bass is a usable
  left-hand foundation — firmer than the Rhodes' soft sub.
- **Line + harmony voice**: fully polyphonic (10 fingers). Can be the sole
  harmony instrument in a rock trio (Supertramp's two-keyboard rig used the
  CP-80 for the piano parts against the Rhodes for the electric parts) or a
  bright lead layer over an arrangement.
- **Famous voice**: Supertramp "The Logical Song" and "Goodbye Stranger"
  (CP-80), Billy Joel "My Life" (CP-70), Toto "Africa" intro (CP-80), Queen
  "You're My Best Friend" (John Deacon, CP-80), Peter Gabriel
  "Sledgehammer" (CP-80), Journey "Don't Stop Believin'" (CP-70). The
  records usually double it with a real acoustic grand or strings — but
  NEVER a second melodic patch on the same pitches (comb-filter rule).

## Range

| Zone | MIDI | Pitches | Keys | Register |
|---|---|---|---|---|
| Full range | 21–108 | A0–C8 | 88 | CP-80 full 88-key compass (CP-70: 73 keys, E1–E7 = 28–100) |
| Sweet spot | 60–84 | C4–C6 | 40–64 | the glassy attack zone, the CP signature |
| Sub | 21–35 | A0–B1 | 1–15 | huge clear sub — the pickup bass is BIG |
| Bass | 36–47 | C2–B2 | 16–27 | left-hand bass zone, round and present |
| Mid | 48–71 | C3–B4 | 28–51 | primary melody + chord body |
| High | 72–96 | C5–C7 | 52–76 | glassy bell lead, cuts without harshness |
| Top | 97–108 | C#7–C8 | 77–88 | thin sparkle, accents only |

The GM patch (program 2) plays the full keyboard 21-108 (empirical FluidR3
sweep, see Verification). The CP-70's 73-key compass (E1–E7) covers the
writing band comfortably; the CP-80 matches the full 88.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato (pedal) | 40–60 | full sustain, 3–8 s ring | soft attack, clean long ring, the "water" |
| Touch (finger) | 60–75 | release when key lifts | mid-weight, clear glassy attack |
| Accent | 85–95 | full, with edge | bright hammer strike, the attack IS the voice |
| Hard accent | 100–115 | full, preamp edge | maximum attack, slight harmonic foldover |
| Staccato | 70–80 | 0.2–0.3× | damped crisp, pop/funk chop |
| Glassy | 80–95 | 0.9× | the signature bright-attack hook (The Logical Song) |
| Tremolo (amp/chorus) | 50–70 | sustained | the 70s stage-piano effect (chorus/phaser era) |
| Muted | 30–45 | short 0.15× | felt-damped strings, delicate |
| Comping chop | 60–85 | 0.5× | rhythmic chord stab, rock/funk comping |

## Timbre DNA

- **Harmonic content**: near-harmonic string partials (1:2:3:4:5 with slight
  inharmonic stretch), fundamental strong and clean. The octave (2×) is
  prominent — the pickup loves the string's even partials. No soundboard
  resonance under the fundamental (contrast acoustic piano's body bloom).
- **Attack**: 3-8 ms hammer strike captured close by the pickup — the
  brightest, most metallic attack of the electric pianos (Rhodes tine is a
  softer clank, FM EP2 is synthetic). The attack transient is broadband
  (hammer noise + string ping) and is THE reason the CP cuts.
- **Decay**: slow and linear-ish — 3-8 s clean ring with no soundboard to
  absorb it. Longer than acoustic piano in the mid register, comparable in
  the bass. Release: dampers stop the strings within ~100-300 ms, cleaner
  than a Rhodes (felt on steel tine).
- **Vibrato**: none inherent. The 70s stage effect is a mild chorus/phaser
  (not the Rhodes' amp tremolo, which is rarer on CP parts).
- **Character**: bright, glassy, clean, long-ringing; a real piano tone
  with the room taken out and the attack pushed forward.

## Role in Arrangement

- **Harmony filler**: sustained mid-register chords under a lead — the
  "electric grand pad" (sustain pedal + soft velocity). The 70s pop/rock
  ballad bed (Supertramp, 10cc, ELO).
- **Melody**: single-note glassy lines in the sweet spot (C4–C6) — the
  instrument's most famous role ("The Logical Song" intro hook). Cuts
  through a full rock band.
- **Bass**: left-hand bass in the 36–47 zone — firm and present, usable as
  a rock trio foundation (better than the Rhodes, not as sub-heavy as a
  real bass guitar).
- **Accent/rhythm**: bright staccato chops and comping hits — the CP attack
  gives funk/pop chords a glassy edge.
- **Color**: high register (C5–C7) bell-like single notes and arpeggios.

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. A plucked string waveguide IS the physical model: a real
   piano string struck by a hammer and read by a magnetic pickup.
   `loop_gain` **0.9982** — high, above sitar 0.9975 and near harp 0.9985,
   because the missing soundboard removes the grand piano's main energy
   sink (the string rings 3-8 s, almost undamped). `lowpass_hz` 5500 models
   the pickup bandwidth (bright attack, bounded top), `noise_component`
   0.02 the hammer-felt tick, `width` 0.8 the keyboard spread.

2. **ModalSynth** (`sound/synthesis/modal.py`) — **secondary**. The string
   is a struck resonator: a custom `ELECTRIC_GRAND_MODES` bank at
   near-harmonic ratios 1 : 2 : 3 : 4 : 5 (piano strings are near-harmonic,
   unlike the Rhodes tine's compressed inharmonic set) with SLOW decay rates
   (0.9–2.2) for the long soundboard-less ring. The stock `'string'` preset
   is the closest built-in bank.

3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM alternative:
   sine carrier + sine modulator, mod_freq_ratio 2.0 (the strong octave
   partial), mod_depth 2.0 (bright but not nasal — the DX EP2 uses 2.8 for
   its bell), attack 0.003 s, release 1.2 s.

## Production

- **Reverb**: stage/hall 2.0–2.5 s. The CP was DI + amp + room; a hall
  makes the long clean ring bloom. Keep the pre-delay short (~30-50 ms) so
  the glassy attack stays defined. (Rhodes 2.2 s precedent; shorter than
  the pad family 3.2 s.)
- **EQ**: cut ~300 Hz (cabinet/body boxiness), boost ~3.5 kHz — the glassy
  attack band, THE CP move (higher than the Rhodes' 2.5 kHz bark), gentle
  8.5 kHz air shelf (pickup noise lives 6-10 kHz, don't over-boost). A low
  cut at ~80-100 Hz in a dense mix (the sub is big).
- **Chorus**: a mild 70s stage chorus/phaser is the period effect; the CP
  parts on records are usually dry + hall, unlike the Rhodes' tremolo.
- **Compression**: light — the CP has more natural dynamics than the Rhodes;
  a gentle 2:1 with slow attack preserves the transient.
- **Pan**: center for solo; slightly left in a stage mix (classical
  keyboard seating, same convention as the Rhodes).
- **FluidSynth note**: FluidR3 preset 2 is a decent electric-grand patch
  (sampled CP-style instrument). For the authentic glassy attack + long
  ring, the Karplus-Strong waveguide with loop_gain 0.9982 is the closer
  model — the SF2 sample's sustain is looped, not a physical ring.

## Verification

- GM2 → stem `trackXX_Electric_Grand_Piano.wav` (label = "Electric Grand
  Piano"; sanitizer only rewrites spaces/parens/slashes — no quirk)
- FluidR3 preset 2 — see `_test/verify_electric_grand.py` output for the
  phdr-verified SF2 name
- Solo render passes 4–8 kHz spectral gate (glassy attack, no comb buzz —
  rendered SOLO, no unison doubling)
- Zero-drift: piano-style units end flush at BAR (terminal landmark)
- **Empirical FluidR3 pitch sweep** (RMS, notes 21–108): preset 2 audible
  across the full keyboard, no gaps — SF2 never clips a composition (see
  `_test/verify_electric_grand.py`)

## Instrument.md companion

`electric_grand.py` — importable constants. Registered in
`instrument_registry.py` (2026-11-21) as `Keys.electric_grand.electric_grand`
→ key `electric_grand`, constant `ELECTRIC_GRAND`. Completes the piano block:
GM1 Acoustic, **GM2 Electric Grand**, GM3 Honky-tonk, GM4 Rhodes, GM5 FM EP2.
