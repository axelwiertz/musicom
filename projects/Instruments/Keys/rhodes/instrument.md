---
type: instrument
family: Keys
name: Rhodes
midi_program: 4
gms: "Electric Piano 1"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [harmony, melody, bass, accent, color]
synthesis: [modal, karplus, phase_mod]
---

# Rhodes (Electric Piano 1)

## MIDI / GM

- **Program**: 4 (GM1 "Electric Piano 1" — the Rhodes piano / Wurlitzer electric
  piano; GM program numbers are 0-based, so 4 is the 5th entry, "Electric Piano
  1"). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) — use
  raw `program=4` in `add_voice`.
- **Channel**: any melodic channel (0-9). Channel 9 with program 4 would trigger
  the drum-kit map and the program-0 fallback label `Acoustic_Grand_Piano` (ch9
  quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 4 =
  "Electric Piano 1" (phdr-verified — labels match exactly, no routing impact).
- **Pipeline stem label**: `GM_PROGRAMS[4]` = "Electric Piano 1" → disk stem
  `trackXX_Electric_Piano_1.wav` — labels match exactly, **no quirk** (but the
  "Electric Piano 1" name is the GM generic, not the specific "Rhodes" brand;
  STEM_LABEL in rhodes.py matches the pipeline's real label so stem-file lookups
  work).

## Identity

The Rhodes (originally the Harold Rhodes Piano, later Fender Rhodes, then
Rhodes Mark I/II) is an **electromechanical piano**: each key strikes a
tuning fork-like **tine** (a hardened steel reed clamped at one end, with a
stiff spring coil at the base — the "spring-tine" assembly), which vibrates
in a magnetic field of a **pickup bar** (a passive electromagnetic pickup,
one per note, similar to an electric guitar pickup). The pickup signal goes
through a **preamp** and into an amplifier/speaker.

The defining elements:

- **Tine + resonator**: the tine is a struck cantilever (not a piano string,
  not a free-free bar). Its partials are inharmonic — the fundamental is
  dominant, and higher modes are compressed (the spring-coil base adds
  nonlinear stiffness). The **tone arm resonator** (the aluminium bar that
  holds the pickup) adds a broad resonance centred around 800-1200 Hz, the
  "bark" or "growl" zone.
- **Electromagnetic pickup**: soft clipping, compression of dynamics
  (electric guitar pickup character — the tine displacement converts to
  voltage nonlinearly, giving the classic Rhodes "bell tone" compression).
  Harder keystrokes saturate the pickup, producing the signature "bite" or
  "snarl" on accents (the "Rhodes bark").
- **Amplifier + speakers**: the Rhodes as heard was never the raw tine
  sound — it went through a tube amp (Fender Twin / JC-120 / SVT) and
  speakers (12" or 15" Jensen/JBL). This adds midrange colouration, speaker
  breakup on loud notes, and the iconic "tremolo" (amp vibrato).
- **Sustain pedal**: lifts all dampers from the tines. Unlike a piano,
  the Rhodes tines ring only ~2-6 s (much shorter than a piano string) but
  the pickup keeps amplifying until the tine stops. Heavy pedal blurs into
  the classic "watery" Rhodes chord wash.

Consequences for composition:

- **Bell-like fundamental tone**: the Rhodes is richer than a pure sine but
  not as bright as a piano; it blends into a mix without piercing. The
  "bell" character lives at the partials 2× and 3× (compressed relative to
  a piano string).
- **Dynamics are COMPRESSED compared to piano**: velocity 40 and 120 differ
  far less in perceived volume than on an acoustic piano (pickup
  compression). Phrase with REGISTRATION (open/closed voicing, two-hand
  spacing) and STRUM (arpeggiation speed) as much as with velocity.
- **The "bark" zone**: accented notes in the 60–72 MIDI range (C4–C5) at
  high velocity (≥95) trigger the pickup saturation — the note "growls" or
  "barks". This is the Rhodes' signature expression technique (Herbie
  Hancock "Chameleon" intro, Stevie Wonder "Superwoman" solo).
- **Tremolo is THE effect**: the Rhodes is inseparable from its vibrato/
  tremolo amp — an amplitude modulation at 4-7 Hz. Many parts get their
  entire feel from the left-right panning tremolo of the speaker (Fender
  Vibratone / rotary speaker emulation).
- **Line + harmony voice**: fully polyphonic (10 fingers, electric bass
  can join). Can be the sole harmony instrument in a trio (Rhodes+bass+
  drums) or a colour layer in a full arrangement. Works as a bass voice
  only through the left-hand zone (below E3); the tone gets too tinkly
  below C3 (36 = C2) for bass role — use piano/organ/electric bass for
  sub-C3 foundations.

## Range

| Zone | MIDI | Pitches | Keys | Register |
|---|---|---|---|---|
| Full range | 36–96 | E1–C7 | ~40–76 | 88-key Rhodes Mark I 73/88 (E2–E6 sweet) |
| Sweet spot | 48–84 | C3–C6 | ~13–49 | primary melodic + harmonic register |
| Low | 36–47 | E1–B2 | 1–12 | bass zone: dark, rumbly, the "bottom" |
| Mid | 48–71 | C3–B4 | 13–36 | bell-like principal register: melody + chords |
| High | 72–96 | C5–C7 | 37–61/88 | bright, tinkly, thin solo; compresses into the pad layer |

The classic 73-note Rhodes Mark I covers E2–E6 (40–88). The 88-note version
extends up to C8 (108). The GM patch (program 4) generally plays across the
full GM span (36–96 in our range), and FluidR3 preset 4 is audible from
E1–C7 with no gaps.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato (pedal) | 40–60 | full sustain, 2–6 s ring | soft bell, clean fundamental, the "water" |
| Touch (finger) | 60–75 | release when key lifts | mid-weight bell, clear attack |
| Accent | 85–95 | full, with bite | pickup saturation, the "bark" at C4–C5 |
| Hard accent | 100–115 | full, with snarl | speaker breakup, aggressive edge |
| Staccato | 70–80 | 0.2–0.3× | damped crisp, the Wurlitzer-ish short stab |
| Tremolo (amp) | 50–70 | sustained | amplitude modulation 4-7 Hz, left-right pan |
| Muted | 30–45 | short 0.15× | light felt-muted tine, delicate |
| Comping chop | 60–85 | 0.5× | rhythmic chord stab, funk/pop comping |

## Timbre DNA

- **Harmonic content**: fundamental dominant, with moderate 2nd and 3rd
  partials; higher partials (>5×) are compressed by the pickup transfer
  function. The "bell" is the 2nd partial (~50-70% of f0 amplitude, vs a
  piano's ~30%).
- **Attack**: 3-8 ms tine strike — soft felt hammer on steel, faster than
  acoustic piano felt on strings (~10 ms), slower than a harpsichord quill
  (~1-2 ms). The "clank" is a transient buzz (1-3 kHz) from the tine's
  higher modes excited by the hammer.
- **Decay**: 0.5-2.0 s bright ring, 2-6 s total tail (tine keeps vibrating
  but pickup loses sensitivity). Shorter than piano (~10 s in bass).
  Sustain pedal merges notes into a wash.
- **Release**: dampers stop the tine within ~100-300 ms; release is
  cleaner than a harpsichord (felt rests on the tine vs cloth on string).
- **Vibrato**: none inherent — MUST add the Fender Vibratone or BOSS/Roland
  tremolo pedal (amplitude modulation, not pitch vibrato). Rate 4-7 Hz,
  depth 30-70%.
- **Character**: warm, bell-like, compressed, "watery" in chord washes;
  aggressive bite at high velocity in the mid zone; blends into a mix
  without cutting like a piano.

## Role in Arrangement

- **Harmony filler**: chordal pad/comping in the middle register (the
  classic "Rhodes pad" — sustain pedal down, soft velocity, chord washes
  under a vocal/solo); the Rhodes' most famous role.
- **Melody**: bell-like single-note lines in the mid register, especially
  in jazz/R&B/pop ballads; can carry a solo over a rhythm section.
- **Bass**: left-hand bass line in the low zone (E2–B2) for trio/small
  ensemble; for modern pop with a bass player, the Rhodes plays above C3.
- **Accent/solo**: the "bark" zone (C4–C5, velocity ≥95) — the Rhodes'
  most iconic expression, used for solo punctuation and rhythmic hits.
- **Color/sparkle**: high register (C5–C7) for long bell-like notes,
  arpeggiated chord jangles, and sparse two-hand tracer lines.

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**. The tine is a
   struck clamped cantilever with a spring-coil base — an inharmonic
   metal-bar modal bank captures the partial structure accurately. The
   `'string'` preset is the closest stock bank (harmonic stack), but a
   custom `RHODES_MODES` bank is recommended for the compressed inharmonic
   tine ratios 1.0 : 2.3 : 4.1 : 6.8 (compressed relative to harmonic
   1:2:3:4) with moderate decay rates (0.8–3.0). Add a pickup-saturation
   soft clip (tanh) on the output for the bell compression.

2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) — the
   tine IS a struck waveguide (clamped steel reed). `loop_gain` **0.9965**
   between clavi 0.9960 and accordion-harmonic — the steel tine rings
   1-3 s, shorter than a guitar or harp string. A low-pass filter at
   ~2000 Hz and noise_component ~0.015 for the hammer "tick" transient.

3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM synthesis for
   the bell-like tone: sine carrier + sine modulator, mod_freq_ratio 2.3
   (the 2× partial emphasis = the "bell"), mod_depth 1.8 (moderate — Rhodes
   is less nasal than harpsichord 2.2, less buzzy than reed 3.2+), attack
   0.004 s, release 1.5 s.

## Production

- **Reverb**: hall 1.8–2.5 s (the Rhodes lives in the hall reverb — the
  "watery" chord wash is the sustain + room bloom). A room/hall with
  moderate pre-delay keeps the attack definition; digital/monster verbs
  (DX7, Lexicon Hall) are the classic 80s Rhodes sound.
- **EQ**: cut ~350 Hz (body boxiness/tine-mount resonance bloom); boost
  ~2.5 kHz for bell articulation; high shelf 8 kHz for air but not too much
  (pickup buzz lives 6-10 kHz). A low cut at 100 Hz when in a full mix
  (the low-pedal was rumbles), but keep 100–200 Hz for solo.
- **Tremolo**: the defining Rhodes effect. Apply as part of the Instrument
  chain: amplitude modulation sine LFO at ~5.5 Hz with depth 0.3–0.5 and
  stereo pan spread. This is the "Fender Vibratone" / rotary speaker
  simulation.
- **Compression**: the Rhodes is already compressed by the pickup; a fast
  Opto (LA-2A style) at 3:1 ratio smooths the dynamic range further,
  especially for comping parts. DO NOT over-compress — kills the attack bite.
- **Delay**: dotted 8th or slap (120-200 ms) for solo lines; ambient trails
  for pads (long 1/4-note delays with feedback).
- **Pan**: center in solo; in a stereo mix, the classic setup is the Rhodes
  panned slightly left with the left-hand bass centred, or spread across
  stereo with the tremolo panning the whole signal.
- **FluidSynth note**: FluidR3 preset 4 is a decent Rhodes patch. For the
  authentic "bell" + "bark" character, use the ModalSynth RHODES_MODES bank
  with clipped output — the SF2 patch is a sampled tine, but it lacks the
  pickup saturation and amp breakup that make the Rhodes expressive.

## Verification

- GM4 → stem `trackXX_Electric_Piano_1.wav` (label = "Electric Piano 1",
  no quirk — the GMPROGRAMS index 4 = "Electric Piano 1")
- FluidR3 preset 4 = "Electric Piano 1" (verified from phdr chunk — exact
  match)
- Solo render passes 4–8 kHz spectral gate (tine bell, no comb buzz)
- Zero-drift: struck/piano-style units end flush at BAR (terminal landmark)
- **Pickup compression quirk**: velocity range is narrower in perceived
  dynamics — keep velocities in 60-100 band for normal expression, use
  articulation/density for dynamic contour (not a piano).
- **Empirical FluidR3 pitch sweep** (RMS, notes 36–96): preset 4 audible
  across full span, no gaps — SF2 never clips a composition (see
  `_test/verify_rhodes.py`)

## Instrument.md companion

`rhodes.py` — importable constants. Registered in
`instrument_registry.py` (2026-10-06) as `Keys.rhodes.rhodes` →
key `rhodes`, constant `RHODES`.