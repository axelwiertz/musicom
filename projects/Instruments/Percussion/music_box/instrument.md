---
type: instrument
family: Percussion
name: Music Box
midi_program: 10
gms: "Music Box"
range_min: 60
range_max: 96
solo_range: [60, 84]
role: [lead, melody, ornament, accent, color]
synthesis: [modal, karplus, phase_mod]
---

# Music Box

The mechanical lamellophone — a pinned brass/steel cylinder plucking a tuned steel
comb (lamellae). The iconic wind-up toy and jewellery-box sound: the delicate
tinkle of mechanical teeth that defined 19th-century domestic music, from Swiss
snuff-box carillons to the Polyphon disc machines and the Sankyo 72-note
movements. The tiniest orchestration colour in the percussion family.

## MIDI / GM

- **Program**: 10 (GM1 Music Box — 0-based GM 10)
- **Channel**: melodic channel (0–9). NOT channel 9 — channel 9 triggers
  the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem
  label (timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 10 =
  "Music Box" (verified from phdr chunk). RenderPipeline stem label:
  GM_PROGRAMS[10] = "Music Box" → `trackXX_Music_Box.wav`
  — matches exactly, **no quirk**.
- GM neighbours: 9 Glockenspiel, 10 Music Box, 11 Vibraphone, 12 Marimba,
  13 Xylophone — the keyboard-metallophone block. Music Box is the only
  CYLINDER-DRIVEN mechanical instrument here, distinct from the manually
  struck mallet percussion.

## Range

Music box movements come in two standard sizes. The most common 18-note
movement spans C5–A6 (72–93). Larger 30/50/72-note movements extend down
to C4 (60) or even G3 (55). The GM patch covers the full span.

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Full range | 60–96 | C4–C7 | mechanical movement compass (30-to-72-note boxes) |
| Low (bass) | 60–71 | C4–B4 | dark, delicate, soft — the mechanical bass, thin but sweet |
| Middle (sweet) | 72–84 | C5–C6 | bell-like singing, the idiomatic music-box tinkle |
| High (tinkle) | 85–96 | C#6–C7 | bright, thin, short-ring — the fairy-dust octave |

The practical sweet spot is C5–C6 (72–84). Above C6 the tines shorten and
the tone becomes increasingly glassy. Below C4 the tines lengthen and become
mushy (some large 72-note Reuge/Sankyo boxes reach G3=55 with acceptable
tone).

Real music boxes are NOT chromatic in the lower range — 18-note boxes play
a single diatonic tune (usually C5–A6). Chromatic 72-note movements exist
(Reuge, Sankyo, Orpheus) and cover the full chromatic span C4–C7. The GM
patch is fully chromatic across the whole range.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Pluck | 80–90 | full | standard pin strike — the default, clean mechanical tooth |
| Soft | 55–70 | full | gentle pin — delicate, pillow-soft |
| Accent | 95–108 | 0.9× | harder pin emphasis — brighter, more upper partials |
| Staccato | 65–75 | 0.2× | short pluck — abrupt tinkle cut-off |
| Roll | 70–80 | 0.06× | rapid tine repetition (composer's illusion of sustain) |

Real music boxes have NO velocity control — the pin always plucks at the
same displacement. The velocity mapping above is a creative affordance for
compositional dynamics, not a physical reality. The mechanical escapement
also means the tempo is fixed (governor-regulated); a music-box composition
should not expect tempo variation.

## Timbre DNA

- **Harmonic content**: near-harmonic steel-tine stack — fundamental
  dominant (the tuned tooth resonates at its designed pitch), with modest
  2nd–4th partials giving a sweet, unaggressive bell tone. The steel comb
  produces a purer sound than a wound-string lamellophone (kalimba's
  overtones are richer). The overall spectrum is closer to a glockenspiel
  with the treble rolled off — no aggressive attack spike, no inharmonic
  bell clang.
- **Attack**: ~3–8 ms — the pin lifts and releases the tine. Softer than a
  mallet strike (xylophone 1–2 ms), gentler than a kalimba thumb-pluck.
  The mechanical nature gives it a consistent, almost sampled quality.
- **Decay**: 0.3–1.2 s depending on tine length — long tines (bass) ring
  longer than short tines (treble). The tine has no damper; it rings until
  its energy dissipates through the comb block into the wooden case.
- **Release**: natural mechanical ring — there is NO damping mechanism on
  a music box (unlike the piano's felt damper or the vibraphone's pedal).
  A note "stops" when the next pin re-plucks the same tine or when the
  cylinder rotation moves the pin past it; the tine continues resonating
  silently. In MIDI, note-off means "stop the audio" but the real acoustic
  never stops instantly.
- **Vibrato / Tremolo**: NONE native. The only amplitude variation is the
  natural beat between slightly detuned unison tines on some movements
  (the "celeste" effect in vintage Reuge boxes — intentionally detuned
  pairs for warmth).
- **Noise component**: negligible — the mechanism is quiet (no breath,
  no mallet click, no bow scrape). The faintest mechanical tick from the
  pin engagement is audible only in an anechoic room.

## Role in Arrangement

- **Lead / Melody**: the default role — a music box plays a single-line
  tune (the cylinder encodes one melody). In an arrangement, the music box
  is the nostalgic/toy/sweet melody voice. Limited compass (~2 octaves for
  idiomatic writing) but instantly recognisable.
- **Ornament / Embellishment**: turn figures, passing tones, the "wind-up"
  start pattern. The mechanical tick-tock of a music box is its own
  ornament.
- **Accent / Color**: specific "music box" effect — a single C5 tinkle as
  a colour accent in a sparse texture. The unexpected appearance of a
  music-box line is a powerful orchestration gesture (the "flashback"
  / "magical" trope).
- **NOT** a harmony voice — music boxes are overwhelmingly monophonic
  (single-tine, one note at a time). Writing two-handed chords on a music
  box is physically impossible on real movements. Use the patch for
  single-line melody ONLY. Two notes simultaneously on the same tine
  would require two pins striking it at once — mechanically impossible.
- **NOT** a bass voice — the bass tines are too weak/soft to anchor a
  mix. The music box functions as a DECORATIVE soprano/alto voice above
  the rest of the arrangement.
- **NOT** a continuous pad — the mechanical pin-pluck mechanism produces
  discrete notes, each with its own attack-decay. There is no sustain
  pedal, no legato slur across notes.

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank. The stock `'bell'` preset is the closest match (metallic
   inharmonic resonator, moderate decay). A custom `MUSIC_BOX_MODES` bank
   should model a near-harmonic steel-tine stack (ratios 1 : 2.0 : 3.0 : 4.0,
   slightly inharmonic due to the fixed-end tine boundary condition, with
   fast decay rates 3–12 — much faster than tubular bells' 0.5–2.0). The tine
   is clamped at one end (the comb block) and free at the other — a
   cantilever, not a free-free beam. Cantilever modes follow ratios
   approximately 1 : 6.27 : 17.5 : 34.4 for an ideal rectangular cantilever,
   but the short stubby tine of a music box is better approximated by a
   near-harmonic 1 : 2 : 3 : 4 stack with very fast decay.

2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   secondary. The tine IS plucked (the pin lifts and releases it), so a
   waveguide model fits the physical excitation. loop_gain 0.9950 gives a
   moderately short steel-tine ring (~0.5–1.0 s). The short delay line
   (small tine = high pitch) limits the richness of the KS model; KS
   excels at longer, lower-pitched strings.

3. **PhaseModSynth** — FM bell alternative: sine carrier, mod ratio 2.0
   (first overtone), depth 1.2, attack 0.002 (near-instant pin release),
   release 0.3. A clean but sterile bell substitute.

## Production

- **Reverb**: room/plate 1.2–1.8 s — a music box needs intimate ambience,
   NOT a cathedral (the mechanical tick is part of the charm). Too much
   reverb turns the tinkle into an anonymous bell sound. REVERB_TAIL 1.5 s
   is the default.
- **EQ**: cut ~500 Hz to remove boxy case resonance; boost ~4 kHz for the
   characteristic tinkle "zing"; a subtle 8 kHz shelf for air. The music
   box is already a bright instrument — too much 4–8 kHz boost makes it
   sound like an alarm clock.
- **Pan**: center (solo) or slight L/R offset for a duet box effect. The
   real instrument sits on a table/dresser; it is inherently a mono source.
- **Compression**: unnecessary — the dynamic range is narrow (consistent
   pin velocity) and compression would only bring up the mechanical noise.
- **Layering**: a single music box line layered with a glockenspiel (same
   pitches) creates a classic "music box + glock" sound popular in film
   scoring. Never double a music box with a piano at the same pitch —
   the attack transients clash.

## Verification

- GM10 → stem `trackXX_Music_Box.wav` (label matches, no quirk)
- FluidR3 preset 10 = "Music Box" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (clean tinkle, no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Identity quirk: music box is a MONOPHONIC mechanical instrument —
  composition jobs MUST write single-note lines, not chords. Two notes
  at the same time on a real music box is mechanically impossible.

## Instrument.md companion

`music_box.py` — importable constants. Registered in
`instrument_registry.py` as `Percussion.music_box.music_box` → key
`music_box`, constant `MUSIC_BOX`.