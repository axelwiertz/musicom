---
type: instrument
family: Bass
name: Synth Bass 2
midi_program: 39
gms: "Synth Bass 2"
range_min: 21
range_max: 96
solo_range: [48, 72]
role: [bass, rhythm, groove, accent, lead]
synthesis: [mono_synth, phase_mod, karplus]
---

# Synth Bass 2

## MIDI / GM

- **Program**: 39 (GM Synth Bass 2; 0-indexed — matches FluidR3 preset 39
  and the RenderPipeline `GM_PROGRAMS[39]`). NOT in
  `structures/instrument.py` `MidiInstrument` enum (10 only) — use raw
  `program=39` in `add_voice`.
- **Channel**: any melodic channel (0–9). Monophonic in practice — one note
  at a time (the TB-303 is a true monophonic instrument; chords are NOT
  idiomatic).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 39 =
  **"Synth Bass 2"** (phdr-verified). RenderPipeline stem label:
  `GM_PROGRAMS[39] = "Synth Bass 2"` → sanitized
  `trackXX_Synth_Bass_2.wav` — matches exactly, **no quirk**.
- **Identity**: the RESONANT analog synth bass — the TB-303 acid voice.
  Roland's 1981 TB-303 Bass Line (the box whose quirky, screeching filter
  birthed acid house in 1985-87 Chicago: Phuture "Acid Tracks", DJ Pierre,
  Armando, Adonis) and the acid sound of techno, electro, and synthwave.
  A pulse oscillator through a self-oscillating 24 dB/oct low-pass filter,
  with the two gesture buttons that ARE the idiom: **accent** (velocity
  re-triggers the filter envelope) and **slide** (portamento). Distinct from
  Synth Bass 1 (GM38, the Minimoog-ish analog bass): SB2 is the squelch —
  higher resonance, brighter filter envelope, more aggressive accent. GM39
  is the one that screams. Cousins: GM32 acoustic (plucked wood), GM33/34
  electric (pickups), GM35 fretless (frets pulled), GM36/37 slap (funk).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 21–96 | A0–C7 | Extended / GM patch (empirical sweep) |
| Sub (pedal) | 21–35 | A0–E2 | Chest thump, felt > heard, single notes only |
| Groove (primary) | 36–50 | C2–D3 | Acid 16th-note sequences, root-fifth pocket, the squelch band |
| Mid (melodic) | 51–62 | D#3–D4 | Octave-displacement riffs, melodic fills, singing tone |
| High (acid lead) | 63–96 | D#4–C7 | Cutting resonance, thin; solos and accents only |

The real TB-303 keyboard spans only 2 octaves (C2–C4 = MIDI 36–60); the GM
patch (FluidR3 preset 39) plays far wider — the empirical sweep measured
audible output from A0 (21, RMS 0.2533 — the sub band is LOUD) to C7 (96,
RMS 0.1268) with a remarkably even rolloff and no gaps (C8 silent). The
idiomatic writing band is 28–72 (E1–C5), with the sweet spot at 36–55
(C2–G3) — the groove pocket. (Empirical FluidR3 pitch sweep in REPORT.md.)

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Accent (default gesture) | 95–105 | 0.5–0.7 | Filter-env re-trigger — the squelch burst, THE acid voice |
| Staccato (acid 16ths) | 72–82 | 0.2–0.35 | Tight gated 16ths — the sequence default |
| Slide (portamento) | 60–72 | note + glide | 303 slide — pitch glides into the next note |
| Squelch | 85–95 | 0.4–0.5 | High-resonance attack — filter peak "wow" |
| Legato (sustained) | 64–72 | full | Pad-like held bass, gate open |
| Octave jump | 78–88 | 0.3–0.5 | Octave-displacement riff — house/electro signature |
| Ghost | 36–45 | 0.1–0.2 | Closed-gate tick — rhythmic filler, no pitch |

## Timbre DNA

- **Harmonic content**: pulse-wave harmonics through a resonant 4-pole
  low-pass. The filter IS the instrument — the resonance peak (near
  self-oscillation) creates the characteristic hollow, screaming "squelch"
  band; when the envelope re-opens the cutoff, the tone sweeps from sub
  thump to nasal mid. Fundamental strong below ~200 Hz (the sub oscillator
  adds weight); a pronounced ~1 kHz peak when the env is open.
- **Attack**: near-instant (the gate click) — sub-5 ms. The 303 has no
  pluck transient; the "attack" IS the filter sweep.
- **Decay**: gate-controlled — the note ends when the gate closes (that is
  why the 16th-note staccato is the idiom: the gate is the rhythm).
- **Noise**: none by design — the 303 is a pure oscillator + filter
  (the analog circuit hiss is negligible; no string, no scrape, no breath).
- **Character**: squelchy, nasal, hollow, aggressive — the acid voice.
  A 16th-note sequence with accents on the offbeats and an occasional slide
  is the most recognizable bass sound in electronic music (Phuture,
  Josh Wink "Higher State of Consciousness", Daft Punk "Da Funk" bass
  lineage). It is the OPPOSITE of the acoustic bass: no body, no wood, no
  warmth — the resonance is everything.

## Role in Arrangement

- **Bass** (primary): acid bass lines, root-fifth sequences, sub-octave
  pedals — the harmonic foundation of house/techno/electro/synthwave.
  Locks with the kick; the filter sweep IS the phrase.
- **Rhythm**: 16th-note acid sequences — the pattern is the melody; ghost
  ticks and accents build the groove.
- **Groove**: the offbeat accent is the acid rhythm signature (the
  "Phuture 16th" — accents on the offbeat 16ths over a 4-on-the-floor
  kick).
- **Accent**: squelch stabs, octave-jump hits on the downbeat.
- **Lead**: acid-lead solos in the high register (63–84) — the screaming
  resonant line (the "acid lead" of later acid techno).
- NOT a harmony/pad voice (monophonic — one note at a time, chords are
  NOT idiomatic); NOT a sub-only voice (the resonance is the identity,
  sub is just the bottom); NOT a warm/fat voice (that is Synth Bass 1).

## Synthesis Engines (musicom)

1. **MonoSynth** (`sound/synthesis/mono_synth.py`) — **primary**. The
   subtractive architecture IS the 303: VCO (pulse wave) → 24 dB ladder
   low-pass → ADSR VCA. `SYNTHESIS_DEFAULTS` run it HOT: `waveform
   "pulse"` (the 303's oscillator), `filter_resonance 0.85` (near
   self-oscillation — the squelch), `filter_env_amount 0.8` (the per-note
   re-open = the accent), `filter_cutoff 2400` (brighter than synth_bass_1
   1800 — the acid voice lives higher so the sweep is audible). Same engine
   family as synth_bass_1 — with resonance and env amount pushed to the
   acid extreme.

2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — FM acid
   alternative. Saw carrier + sine modulator ratio 1.0, depth 2.8 (edgier
   than SB1 2.5 — the squelch), fast attack 0.004 s. The "rubber 303" /
   DX-style acid patch.

3. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`) — tertiary
   fallback. `loop_gain 0.9955` (snappier than SB1 0.9960 — acid is
   punchier/tighter), `lowpass_hz 1800`. Not the physical model (there is
   no string), but a usable string-free bass approximation.

4. **ModalSynth** (`sound/synthesis/modal.py`) — weak fallback only
   (`'string'` preset, no resonant filter character).

## Production

- **Reverb**: small room / plate 0.9 s — the DRIEST bass in the library.
  The 303 is a direct-inject voice; the resonance IS the effect, verb
  smears 16th-note sequences (synth_bass_1 1.0 s precedent, minus a tick).
- **EQ**: cut 220 Hz (−3 dB, bigger than SB1 — the resonance pushes more
  energy into the low-mid mud against the kick); boost 1.1 kHz (the
  squelch band — where the filter peak lands when the env opens, the acid
  "growl"); gentle 6.5 kHz air shelf (the 303 has a natural top roll-off,
  keep it musical). High-pass below ~40 Hz in a dense mix.
- **Compression**: minimal or none — the accent dynamics ARE the
  performance; heavy compression flattens the acid groove. Mix-stage
  decision, not baked into the defaults.
- **Pan**: center (100% mono). Synth bass is universally centered.
- **Track**: the classic acid chain is 303 → mixer with the filter
  resonance pushed — no amp, no room, no mic. The dry signal is the sound.

## Verification

- GM39 → stem `trackXX_Synth_Bass_2.wav` (label matches, no quirk;
  FluidR3 preset 39 = "Synth Bass 2" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies)
- Spectral 4–8 kHz buzz checked (a resonant acid patch is genuinely bright
  in the 1–4 kHz squelch band, but the 4–8 kHz buzz gate still applies)
- MonoSynth smoke test: pulse + resonance 0.85 renders an audible acid
  note with the expected gate envelope
- Empirical FluidR3 pitch sweep: preset 39 audible 21–96, no gaps — SF2
  never clips a composition (REPORT.md)
