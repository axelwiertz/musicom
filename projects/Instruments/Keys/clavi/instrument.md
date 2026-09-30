---
type: instrument
family: Keys
name: Clavi
midi_program: 7
gms: "Clavi"
range_min: 29
range_max: 89
solo_range: [29, 89]
role: [lead, rhythm, accent, ornament, countermelody]
synthesis: [karplus, modal, phase_mod]
---

# Clavinet (Hohner Clavinet D6)

The electric clavichord — a struck-string keyboard instrument where a
rubber-tipped hammer strikes a steel string, with a rubber mute pressing
against the string at the bridge. Invented by Ernst Zacharias for Hohner in
1964 (C-series, followed by the iconic D6 in 1971). The funkiest keyboard
ever built: Stevie Wonder's "Superstition", Billy Preston's "Outa-Space",
Herbie Hancock's "Chameleon", Led Zeppelin's "Trampled Under Foot".

## MIDI / GM

- **Program**: 7 (GM1 Clavi — 0-based GM 7; pipeline GM_PROGRAMS[7] = "Clavi")
- **Channel**: melodic channel (0–9). NOT channel 9 — channel 9 triggers
  the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem
  label.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 7 =
  "Clavinet" (verified from phdr chunk). RenderPipeline stem label:
  GM_PROGRAMS[7] = "Clavi" → `trackXX_Clavi.wav`
  — label is "Clavi" (pipeline) vs "Clavinet" (SF2), cosmetic only, **no
  routing impact** (the MIDI program number 7 selects the preset).
- **Stem quirk**: STEM_LABEL = "Clavi" matches the pipeline's real label
  (GM_PROGRAMS[7] = "Clavi") so stem-file lookups work. The FluidR3
  preset name "Clavinet" is a cosmetic expansion of the GM abbreviation.
- GM neighbours: 6 Harpsichord, 7 Clavi, 8 Celesta, 9 Glockenspiel — the
  historical keyboard block. Clavinet is the only STRUCK-STRING keyboard
  here (harpsichord = plucked string, celesta = struck steel plate).

## Range

Standard 60-key Hohner Clavinet D6: F1–F6 (MIDI 29–89). Some early models
had 54 keys (C1–F6 = 24–89). The GM patch spans the full 60-key compass.

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Full range | 29–89 | F1–F6 | standard 60-key Clavinet compass |
| Low (bass) | 29–47 | F1–B2 | thumpy, percussive, rubbery — the funk bass zone |
| Middle (sweet) | 48–72 | C3–C5 | the funky rhythm guitar register — the iconic clavinet voice |
| High (treble) | 73–89 | C#5–F6 | bright, clucky, nasal — solo/single-note lines |

The practical sweet spot is C3–C5 (48–72) — the same register as a guitar,
which is exactly what the clavinet was designed to emulate (a clavichord
that sounds like an electric guitar). Above C5 the rubber mute dominates,
producing a thin "clucky" tone. Below C3 the bass notes are thick and
percussive, often used for funky bass lines.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Pluck | 75–85 | full | standard rubber-hammer strike — the neutral clavinet |
| Hard chord | 95–108 | 0.8× | accented funk chord stab — the "Superstition" chop |
| Soft | 55–70 | full | gentle touch — rounder, less percussive |
| Staccato | 70–85 | 0.2× | short percussive note — tight funk cut |
| Muted | 60–75 | 0.4× | hand-damped — nasal, choked, the "wah" pedal target |
| Accent | 90–105 | 0.9× | sforzando — brighter hammer attack, more string noise |
| Wah | 80–95 | 0.6× | velocity-swept note (requires wah pedal simulation) |

Real clavinet has NO velocity sensitivity — the rubber hammer strikes at
fixed displacement regardless of key speed. The velocity mapping above is
a creative affordance for compositional dynamics and articulation
variation. The clavinet's dynamic expression comes from the external
signal chain (wah pedal, envelope filter, phaser), not from key velocity.

## Timbre DNA

- **Harmonic content**: strong harmonic series (1:2:3:4:5:6) — the steel
  string is struck by a rubber-tipped hammer, but the rubber mute against
  the bridge selectively damps certain harmonics, creating the signature
  "clucky" midrange bump. The spectrum peaks in the 1–3 kHz region (the
  "honk" that cuts through a mix) with a steep rolloff above 6 kHz. The
  fundamental is strong in the bass register; in the sweet spot, the 2nd
  and 3rd partials dominate (giving the guitar-like twang).
- **Attack**: ~1–3 ms — the rubber hammer strikes the steel string. The
  rubber mute at the bridge suppresses the initial transient compared to
  a piano hammer, giving a softer, rounder attack — but the string noise
  (the "cluck") adds a percussive edge. The attack is the instrument's
  identity: the rubber-on-steel "thump" followed by the string ring.
- **Decay**: short — ~0.3–1.5 s depending on register. The rubber mute
  at the bridge heavily damps the string, producing the clavinet's
  signature dry, percussive sound. Bass strings ring longer (up to 1.5 s),
  treble strings die in ~0.3 s. The decay is FASTER than a harpsichord
  (cloth damper, 2–5 s) and MUCH faster than a piano (felt damper lifted,
  multi-second sustain).
- **Release**: instant — releasing the key drops the felt damper onto the
  string, stopping it nearly instantly. The clavinet is one of the driest
  keyboard instruments (alongside the harpsichord's key-release damping).
- **Noise component**: significant — the rubber mute creates a distinctive
  "cluck" or "thump" at note onset, especially in the mid-register. This
  noise is an INTEGRAL part of the clavinet sound (the reason it sounds
  funky rather than like a clean electric piano). String buzz and
  mechanical key noise contribute to the percussive character.
- **Vibrato**: none native (the clavinet has no built-in modulation). The
  Hohner D6 has a mute switch that changes the tone (hard/soft position),
  not a vibrato. External effects (phaser, chorus, wah) are the norm.

## Role in Arrangement

- **Rhythm / Comping**: the clavinet's PRIMARY role — rhythmic chord chops
  in the C3–C5 sweet spot, the "funky rhythm guitar" part of the keyboard
  section. Staccato chords with a wah pedal or envelope filter are the
  idiom. Single-note rhythmic patterns (the "Superstition" riff) sit here.
- **Lead / Melody**: single-note melodic lines in the C4–C6 register,
  often through a wah pedal for the classic "talking" clavinet sound.
- **Bass**: the low register (F1–B2) works as a percussive bass voice,
  especially in clavinet-only trio settings (Herbie Hancock's
  "Chameleon" bass line). The rubber thump gives it a distinctive
  "plucked upright bass" character when used as a bass voice.
- **Accent / Ornament**: short percussive stabs, mordents, grace notes —
  the fast decay makes it ideal for accent punctuation.
- **Countermelody**: a second clavinet line in a different register
  (often higher, through a wah) can function as a countermelody voice.
- **NOT** a sustain/pad voice — the fast decay and lack of sustain make
  it unsuitable for held chords or ambient textures.
- **NOT** a piano substitute — the clavinet's sound is fundamentally
  different: percussive, dry, midrange-focused, with no dynamic range
  and no sustain pedal.
- **NOT** a harmony voice for dense chords — 3–4 note chords in the
  sweet spot are fine (the funk "chop"), but large cluster voicings
  turn to mud due to the fast decay and strong midrange.

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**, struck waveguide with rubber mute. The clavinet IS a
   struck string with a damping element at the bridge — the waveguide
   model fits the physics exactly. The rubber mute is modelled by a
   high loop_gain damping factor (0.9960 — SHORTER than harpsichord
   0.9980 and guitar 0.9970) plus an explicit noise component for the
   rubber "cluck" at note onset. The KS delay line length corresponds
   to the string length for each pitch.

   Key KS parameters for clavinet:
   - `loop_gain`: 0.9960 — short ring, rubber-muted decay (~0.3–1.5 s)
   - `noise_component`: 0.03 — rubber "cluck" at note onset (the
     instrument's signature attack noise, higher than any other KS
     instrument in the KB)
   - `width`: 0.3 — focused mono-like stereo (the clavinet is a
     compact keyboard, not a spread grand piano)

2. **ModalSynth** (`sound/synthesis/modal.py`) — secondary, impulse-excited
   resonator bank. The stock `'string'` preset is the closest match
   (harmonic resonator, moderate decay). A custom `CLAVI_MODES` bank
   should model a near-harmonic struck-string stack (ratios 1:2:3:4:5:6)
   with FAST decay rates (6–25 — much faster than harpsichord 0.35–0.90)
   and an explicit noise component for the rubber mute.

3. **PhaseModSynth** — FM electric piano alternative: saw carrier
   (the string's richer harmonic content), mod ratio 2.0, depth 1.5,
   attack 0.002, release 0.3. A thinner but usable clavinet substitute.

## Production

- **Reverb**: room/plate 0.8–1.2 s — the clavinet is a DRY instrument.
   Too much reverb washes out the percussive attack and makes it sound
   like a generic electric piano. A short room reverb gives it the
   "wooden box" acoustic space. REVERB_TAIL 1.0 s is the default.
- **EQ**: cut ~400 Hz to reduce boxy body resonance; boost ~2.5 kHz for
   the midrange "honk" that cuts through a mix (the clavinet's main
   identity zone); gentle shelf above 8 kHz for string shimmer. The
   rubber mute naturally rolls off above 6 kHz, so excessive air boost
   sounds artificial.
- **Pan**: center (solo) or slightly off-center (L 20–30) for a
   rhythm-section placement. The clavinet sits in the keyboard/guitar
   zone in a funk mix.
- **Compression**: light compression (2:1–4:1 ratio) works well to
   even out the naturally wide dynamic range of different registers.
   The clavinet's rubber mute makes the treble quieter than the midrange.
- **Effects chain (idiomatic)**:
  1. Wah pedal (auto-wah or envelope filter) — the classic clavinet
     effect; the "talking" sound
  2. Phaser — subtle phase sweep for the "Herbie Hancock" colour
  3. Envelope filter — auto-wah for funky rhythmic patterns
  4. Compression — tames the uneven register response
- **Layering**: a clavinet line layered with a clean electric guitar at
   the unison creates a classic funk rhythm section sound (Stevie
   Wonder, Tower of Power). Avoid layering with acoustic piano at the
   same pitch — the attacks clash. A clavinet comping against a Rhodes
   pad is the classic 1970s keyboard section.
- **Signal chain note**: the clavinet was designed to be plugged into
   an amplifier (Fender Twin Reverb, Leslie speaker). The DI/amp
   simulation is part of the sound. A dry clavinet without amp
   simulation sounds thin and sterile.

## Verification

- GM7 → stem `trackXX_Clavi.wav` (pipeline label "Clavi", no quirk)
- FluidR3 preset 7 = "Clavinet" (verified from phdr chunk — cosmetic
  expansion of the GM abbreviation, no routing impact)
- Solo render passes 4–8 kHz spectral gate (clean struck-string tone,
  no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Karplus-Strong primary: struck waveguide with rubber mute damping
  (loop_gain 0.9960, noise_component 0.03 for the rubber "cluck")
- Range F1–F6 (29–89) matches the 60-key Hohner Clavinet D6 compass

## Instrument.md companion

`clavi.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-30) as
`Keys.clavi.clavi` → key `clavi`, constant `CLAVI`.
