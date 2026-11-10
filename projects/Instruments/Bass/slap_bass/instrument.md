---
type: instrument
family: Bass
name: Slap Bass 1
midi_program: 36
gms: "Slap Bass 1"
range_min: 24
range_max: 84
solo_range: [36, 60]
role: [bass, rhythm, groove, accent, ornament, lead]
synthesis: [karplus, phase_mod, modal]
---

# Slap Bass 1

## MIDI / GM

- **Program**: 36 (GM "Slap Bass 1", 0-indexed — matches the RenderPipeline
  `GM_PROGRAMS[36]`; FluidR3 preset 36 = **"Slap Bass"** — the SF2 drops the
  number, cosmetic only, **no routing impact**). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=36` in `add_voice`.
- **Channel**: any melodic channel (0–9). Monophonic in practice — one note
  at a time (slap/pop alternation is a single-note technique; double-stops
  and chords are NOT idiomatic).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 36 =
  **"Slap Bass"** (phdr-verified). RenderPipeline stem label:
  `GM_PROGRAMS[36] = "Slap Bass 1"` → sanitized
  `trackXX_Slap_Bass_1.wav` — matches, **no quirk** (STEM_LABEL =
  `Slap_Bass_1`).
- **Identity**: the thumb-slap + finger-pop technique on the electric bass
  guitar — the most percussive, mid-forward bass in the library. **Slap** =
  strike the string with the thumb so it smacks against the fretboard
  (bright percussive thump + fretboard clack); **pop** = pull the string
  away and release it so it snaps back (harmonic-rich bright click, usually
  on the D/G strings). On the double bass the technique goes back to New
  Orleans jazz bands in the early 1900s (spread via western swing,
  rockabilly); on the electric bass it is credited to **Larry Graham** (Sly
  and the Family Stone, late 1960s — "Thank You (Falettinme Be Mice Elf
  Agin)" is the canonical slap record), then funk/disco — Bootsy Collins,
  Verdine White, Louis Johnson, Mark King (Level 42), Stanley Clarke, Victor
  Wooten, Flea, Les Claypool.
- The same instrument as Electric Bass (finger) GM33 — same body/strings/
  pickups, DIFFERENT performance technique (high action + aggressive right
  hand). GM35 Fretless is the frets-pulled electric; GM38/39 are the
  oscillator voices; GM37 "Slap Bass 2" (FluidR3 "Pop Bass") is the rounder
  sibling patch.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 24–84 | C1–C6 | Patch span (plays 21+, hard ceiling at 84) |
| Sub (open/pedal) | 24–35 | C1–E2 | Low thumb thump, felt > heard, single notes only |
| Slap zone (primary) | 36–55 | C2–G3 | Thumb slaps on E/A/D strings — the funk 16th-note groove |
| Pop zone | 56–72 | G3–C5 | Popped harmonics on D/G strings — bright snap, octave pops |
| High | 73–84 | C#5–C6 | Thin treble, exposed fills only (patch ceiling at 84) |

Practical 4-string bass tuned E1–G4: 28–67. Standard tuning
E1–A1–D2–G2 = 28, 33, 38, 43. The GM patch (FluidR3) sounds convincingly
across 21–84 (A0–C6) — empirical sweep in REPORT.md: RMS 1322 at A0,
smooth rolloff to 423 at C6, **SILENT at 86+** (D6) — the patch ceiling is
C6=84, never write above it. The money zone is 33–55 (A1–G3) — the E/A/D
strings where the thumb slap speaks (the funk/disco/r&b groove pocket);
pops add the 56–72 sparkle.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Slap (thumb) | 85–105 | 0.2–0.4 | String smacks fretboard — bright percussive thump + clack (the signature) |
| Pop (finger) | 90–110 | 0.15–0.3 | String snapped back — harmonic-rich bright click, D/G strings |
| Fingerstyle | 65–80 | 0.8–1.0 | Normal pluck — connecting/ballad notes |
| Ghost / dead note | 30–50 | 0.1–0.2 | Left-hand damp — no pitch, the groove filler |
| Hammer-on | 55–75 | 0.5–0.7 | Left-hand hammer — connected 16th runs |
| Pull-off | 55–75 | 0.4–0.6 | Left-hand pull-off — descending 16th runs |
| Double-thumb | 95–110 | 0.15–0.25 | Wooten technique — two slaps per stroke, 32nd texture |
| Staccato | 60–80 | 0.2–0.3 | Tight damped pluck — dry, cutting |
| Accent | 95–110 | 0.3–0.4 | Emphatic downbeat slap — the "1" lands hard |

## Timbre DNA

- **Harmonic content**: two-layer voice — (1) the low thump: strong
  fundamental in the 60–200 Hz band (the string is slapped DOWN into the
  fretboard, maximum string-to-body energy transfer); (2) the snap: a
  broadband fretboard clack with strong 2–4 kHz energy and a bright
  harmonic transient (the pop adds octave+ partials). The mid-forward
  character is why slap bass cuts through a full funk band without
  distortion.
- **Attack**: the fastest, most percussive in the bass family — the slap
  attack is ~1–3 ms (string against steel fret = mechanical click), the pop
  attack is the string snapping back (2–5 ms). Contrast fingerstyle
  electric bass ~10–20 ms.
- **Decay**: SHORT ring — the slap idiom is tight; players mute
  aggressively (0.3–1.0 s). This is the key difference from the fingerstyle
  electric bass's 1–3 s ring: `loop_gain` 0.9955 sits between muted_guitar
  0.9850 and electric bass 0.9970.
- **Noise**: fretboard clack, string smack, thumb knuckle thump — these are
  NOT artifacts, they ARE the voice (the EQ preset adds a gentle 8 kHz air
  shelf, never a low-pass).
- **Character**: punchy, percussive, mid-forward — the rhythm-section
  punctuation of funk/disco/r&b/rock. A 16th-note slap groove in the
  C2–G3 pocket with offbeat pops is the most recorded bass sound in funk
  (Bootsy, Louis Johnson on "Just What I Needed", Mark King's "Lessons in
  Love").

## Role in Arrangement

- **Bass** (primary): slap bass lines, root-fifth groove, the rhythmic
  foundation — locks with the kick and DEFINES the subdivision (the pattern
  IS the melody).
- **Rhythm**: 16th-note funk grooves, octave-pop fills, ghost-note
  subdivisions — the bass as percussion.
- **Groove**: syncopated offbeat pops + muted 16ths — the funk engine.
- **Accent**: hard downbeat slaps, sfz hits, phrase punctuation.
- **Ornament**: hammer-on/pull-off 16th runs, double-thumb flurries,
  ghost-note chattering.
- **Lead** (rare, idiom): slap solos in the 56–72 pop zone (Stanley Clarke,
  Victor Wooten) — exposed, virtuosic, NOT a sustained lead voice.
- NOT a harmony/pad voice (monophonic — one note at a time, never ask the
  composer for a 3-note "slap chord"); NOT a warm fingerstyle voice (that
  is GM33); NOT a sub-only voice (the snap IS the identity, sub is just the
  bottom).

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide is the exact physical model: the string
   vibration of a slapped electric-bass string. `loop_gain` 0.9955 (SHORT
   ring — the slap idiom is tight, muted-hand damping; the most damped
   ring in the Bass family, between muted_guitar 0.9850 and electric bass
   0.9970), `lowpass_hz` 5500 (BRIGHTER than fingerstyle electric bass
   5000 — the fretboard clack top-end IS the identity), `excitation`
   "slap" with `noise_component` 0.05 (the clack transient). Same engine
   family as electric bass, acoustic bass, sitar, harp — with the
   shortest loop_gain of the plucked basses.

2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — secondary. Sine
   carrier + sine modulator, ratio 2.0 (the pop's octave-ish snap
   sideband), depth 2.2, attack 0.003 s (razor pluck). A cheap bright
   pluck approximation; not idiomatic for the thump.

3. **ModalSynth** (`sound/synthesis/modal.py`) — weak fallback. `'string'`
   preset (harmonic stack, no string/fretboard physics).

## Production

- **Reverb**: tight room 1.2 s — the slap voice is DI-injected and dry;
  long tails smear the 16th-note snap (synth_bass_1 1.0 / electric bass
  1.4 bracket — the slap sits at the dry end; funk tracks often run it
  bone-dry + a slap-back delay instead).
- **EQ**: cut 250 Hz (low-mid mud against the kick — the thump itself is
  LOWER, ~100 Hz, keep that); boost 2.8 kHz (**THE slap EQ move** — the
  2–3 kHz snap/click band where the string meets the fretboard); gentle
  8 kHz shelf (string clack — never low-pass a slap bass). High-pass
  below ~40 Hz in a dense mix.
- **Compression**: aggressive — the slap transient is 20–30 dB hotter than
  the ring; a fast FET/optical comp (1176/LA-2A, 4:1, fast attack) tames
  the spikes and glues the 16ths. Mix-stage decision, not baked into the
  defaults.
- **Pan**: center (100% mono). Bass is universally centered.
- **Track**: direct injection (DI) is the classic slap chain — the pickup
  signal IS the sound; amp/DI blends and a touch of chorus are the 80s
  production moves.

## Verification

- GM36 → stem `trackXX_Slap_Bass_1.wav` (label matches; FluidR3 preset 36 =
  "Slap Bass" — SF2 drops the number, cosmetic, no routing impact)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies)
- Spectral 4–8 kHz buzz well below 20% (slap is mid-forward; the 4–8 kHz
  band carries clack, not comb buzz — verified single voice)
- Karplus-Strong smoke test: plucked waveguide produces audible low-
  frequency output with the expected "hard strike then tight ring"
  transient
- Empirical FluidR3 pitch sweep: preset 36 audible across 21–84, hard
  ceiling at C6=84 (silent at 86+) — SF2 never clips a composition within
  the documented range (REPORT.md)
