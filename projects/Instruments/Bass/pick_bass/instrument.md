---
type: instrument
family: Bass
name: Electric Bass (pick)
midi_program: 34
gms: "Electric Bass (pick)"
range_min: 21
range_max: 84
solo_range: [36, 57]
role: [bass, rhythm, groove, countermelody, accent]
synthesis: [karplus, modal, phase_mod]
---

# Electric Bass (pick)

## MIDI / GM

- **Program**: 34 (GM "Electric Bass (pick)", 0-indexed — matches
  `GM_PROGRAMS[34]` in the RenderPipeline; FluidR3 bank-0 preset 34 =
  **"Picked Bass"**, phdr-verified — cosmetic spelling only, no routing
  impact). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only)
  — use raw `program=34` in `add_voice`.
- **Channel**: any melodic channel (0–9). Monophonic in practice — a pick
  plays one note at a time (double-stops on adjacent strings are possible but
  not idiomatic; chords are not).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 34 =
  "Picked Bass". RenderPipeline stem label: `GM_PROGRAMS[34]` =
  "Electric Bass (pick)" → sanitized `trackXX_Electric_Bass_pick.wav` —
  matches, **no quirk** (parens stripped, inner word kept, same convention as
  GM33 `Electric_Bass_finger`).
- **Identity**: the PLECTRUM voice of the solidbody electric bass — the same
  body/strings/pickups as GM33 (Electric Bass (finger)), a different
  right-hand tool. A hard plastic/nylon pick strikes the string at a sharper
  angle with a stiffer contact than a fingertip: a bright broadband CLICK,
  leaner fundamental, more even note-to-note dynamics, and palm muting as a
  first-class articulation (the heel of the hand rests on the bridge
  saddles). Canonical players: Chris Squire (Yes — the Rickenbacker pick
  tone), Paul McCartney (post-1966), Carol Kaye (felt pick), Dee Dee Ramone,
  Mike Dirnt (Green Day), Peter Hook (Joy Division/New Order — the melodic
  pick-bass hook), Justin Chancellor (Tool), Lemmy (pick + distortion),
  Kim Deal, Krist Novoselic.
- Sibling patches in the Bass block: GM32 Acoustic Bass (upright), GM33
  Electric Bass (finger — same instrument, flesh attack), GM35 Fretless,
  GM36 Slap Bass 1 / GM37 "Pop Bass", GM38/39 Synth Bass 1/2. GM34 is the
  only PICKED electric-bass patch in the GM set.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 21–84 | A0–C6 | Empirical patch span (audible 21–84, silent ≥87) |
| Sub | 21–35 | A0–B1 | Sub-bass fundamental: felt > heard, single notes only |
| Groove (primary) | 36–50 | C2–D3 | Pick 8ths/16ths, root-fifth pocket, palm-mute chug |
| Mid | 51–64 | D#3–E4 | Melodic fills, pick-bass hooks, D/G-string cut-through |
| High | 65–84 | F4–C6 | Thin aggressive treble: accents and exposed fills only |

Practical 4-string bass tuned E1–G4: 28–67. Standard tuning E1–A1–D2–G2 =
28, 33, 38, 43. Sweet spot 40–55 (E2–G3) is the groove pocket; the patch is
essentially flat in RMS from 21 to 84 (empirical FluidR3 sweep at velocity
90: RMS 0.067–0.099) and hard-silent from 87 up — no usable treble above C6.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pick (default) | 76–92 | 0.85–1.0 | Plectrum stroke: bright click, even dynamics |
| Alternate pick | 72–88 | 0.80–0.90 | Strict alternating 16ths — the rock/punk engine |
| Downstroke | 88–100 | 0.70–0.85 | Down-only aggressive stroke, punk/metal weight |
| Palm mute | 36–60 | 0.15–0.30 | Hand on saddles: choked chug, no sustain |
| Staccato | 80–94 | 0.25–0.35 | Tight gated pick note — stabs |
| Ghost | 28–45 | 0.10–0.20 | Muted filler tick between accents |
| Slide | 58–72 | note + glide | Pick attack + fretboard zip into target |
| Accent | 90–105 | 0.65–0.80 | Hard downstroke dig on the downbeat |

## Timbre DNA

- **Harmonic content**: strong fundamental with a **brighter partial
  balance** than the fingered bass — measured spectral centroid on the same
  notes: E2 593 → 796 Hz (+34%), A2 697 → 1309 Hz (+88%), D3 738 → 1119 Hz
  (+52%). The pick's stiff contact injects more 2–6 kHz energy; the
  roundwound top end survives because the plectrum does not cushion the
  attack the way a fingertip does.
- **Attack**: the defining feature — a short broadband click. In the FluidR3
  "Picked Bass" patch the sample envelope reaches ~90% of peak at 50–80 ms
  (the fingered patch gets there at ~30 ms), i.e. the SAMPLE is slightly
  softer-edged than the real gesture; write staccato/palm-mute notes ≥
  100 ms so the patch has time to speak.
- **Decay**: 1–2.5 s on held notes; slightly shorter than fingerstyle in
  practice because pick players palm-rest and mute more. The FluidR3 patch's
  late-window (0.6–1.2 s) RMS/peak ≈ 0.22–0.26, steady loop, no collapse.
- **Noise**: plectrum scrape and pick click are PART of the idiom — the EQ
  preset boosts 1.2 kHz (click) and shelves 6 kHz (scrape/sizzle). Fret buzz
  is lower than fingerstyle only when action is high; aggressive players get
  more of it.
- **Character**: tight, punchy, articulate, mid-forward. Where the finger
  bass is round and blooming, the pick bass is focused and clicky — it
  occupies the same fundamental space but claims more 1–2 kHz, which is why
  it cuts through distorted guitars (Squire, Chancellor) and busy new-wave
  arrangements (Hook).

## Role in Arrangement

- **Bass** (primary): root-fifth driving 8ths/16ths, pedal tones, the
  harmonic foundation. Locks with the kick; the pick's even dynamics make
  machine-tight rock/punk grooves easy.
- **Rhythm**: palm-muted chug patterns (the metal/nu-metal engine), strict
  alternate-picked 16ths, octave-displacement riffs.
- **Groove**: new-wave/post-punk melodic grooves (Peter Hook's high-register
  hooks are the reference), ska/reggae pick lines, pop-rock eighth-note
  pulses.
- **Countermelody**: pick-bass hooks in the 51–64 zone that answer the vocal
  an octave below — the New Order/Joy Division signature.
- **Accent**: downstroke digs, pick scrapes, palm-mute stops.
- NOT a lead voice (solos exist but are rare and effect-laden).
- NOT a harmony/pad voice — one note at a time; chords are not idiomatic.
- NOT a high-register sustain voice — above ~C4 the patch is thin and
  aggressive; use it for accents and hooks, not sustained melody.

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. The plucked waveguide is the exact physical model; the PICK
   is the excitation. `loop_gain` 0.9965 (slightly shorter ring than
   fingerstyle 0.9970, longer than slap 0.9955 — the ordering
   harp 0.9985 > acoustic 0.9975 > finger 0.9970 > **pick 0.9965** > slap
   0.9955 is the KB damping ladder), `lowpass_hz` 5600 (brighter than finger
   5000), `width` 0.5 (DI bass is mixed mono), `excitation` "pick" (stiffer,
   brighter burst than "pluck").
2. **ModalSynth** (`sound/synthesis/modal.py`) — fallback, `MODAL_PRESET`
   `'string'`. Harmonic stack approximates the string but carries no
   magnetic-pickup colour and no pick click.
3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — weak alternative.
   Saw carrier + ratio 1.0, depth 2.4, 3 ms attack: a cheap bright bass
   emulation, usable for chiptune/synthwave beds, not idiomatic.

## Production

- **Reverb**: small room 1.2 s — DRIER than the finger patch's 1.4 s. Pick
  bass is tracked DI or amp close-mic; the click must stay upfront, and verb
  on a picked bass smears the attack that defines it.
- **EQ**: cut 200 Hz −2.5 dB (low-mid box resonance — less bloom than
  fingers, so cut lower and deeper); boost 1.2 kHz +3 dB (the pick click —
  higher and stronger than the finger growl at 800 Hz); 6 kHz air shelf
  +2 dB (plectrum scrape + roundwound sizzle). High-pass below 35–40 Hz in
  a dense mix.
- **Compression**: 1176-style fast attack — the pick's transients are the
  loudest peaks in the rhythm section; 4:1 with a fast release keeps the
  click while taming the spikes. Mix-stage decision, not baked in.
- **Pan**: center (100% mono). Bass is universally centred; width belongs to
  the harmonic tail only (KS `width` 0.5).
- **Track**: DI + amp sim (Ampeg SVT, Orange, Rickenbacker-style bright
  channel). Distorted pick bass (Lemmy, Chancellor) is a valid colour but a
  different production path.

## Verification

- GM34 → stem `trackXX_Electric_Bass_pick.wav` (label matches, no quirk;
  FluidR3 preset 34 = "Picked Bass" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark on drum units)
- Solo render only (no unison doubling — comb-filtering buzz rule: never
  double the same pick-bass line with a second melodic patch)
- Spectral 4–8 kHz buzz well below the 20% gate (low instrument; the
  6 kHz shelf is for pick scrape, not harmonic content)
- Karplus-Strong smoke: plucked waveguide produces a click-then-ring
  transient with a shorter tail than the finger patch at equal `dur`
- Empirical pitch sweep: preset 34 audible 21–84, silent ≥87 (patch ceiling)
