---
type: instrument
family: Bass
name: Synth Bass 1
midi_program: 38
gms: "Synth Bass 1"
range_min: 24
range_max: 84
solo_range: [31, 60]
role: [bass, rhythm, groove, accent]
synthesis: [mono_synth, phase_mod, karplus]
---

# Synth Bass 1

## MIDI / GM

- **Program**: 38 (GM1 Synth Bass 1; 0-indexed — matches FluidR3 preset 38
  and the RenderPipeline `GM_PROGRAMS[38]`). NOT in `structures/instrument.py`
  `MidiInstrument` enum (10 only) — use raw `program=38` in `add_voice`.
- **Channel**: any melodic channel (0-9); monophonic line voice — one note
  at a time (the classic analog synth bass has a single VCO voice;
  "chords" on one patch are a sample-playback artifact, not idiomatic).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 38 =
  "Synth Bass 1" (phdr-verified). RenderPipeline stem label:
  GM_PROGRAMS[38] = "Synth Bass 1" → sanitized `trackXX_Synth_Bass_1.wav` —
  matches exactly, **no quirk**.
- **Identity**: GM38 is the analog synth bass (Roland GS "Synth Bass 1
  (analog)", Yamaha XG "SynthBass1"). Distinct from the plucked Electric
  Bass (finger) GM33 — there is NO string; the tone is an oscillator
  (saw/square) through a resonant low-pass filter with a per-note ADSR
  that re-opens the filter. The TB-303 "acid" squelch, the Minimoog
  "fat" bass, and the MC-202 all live here.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range (GM patch) | 24–84 | C1–C5 | GM patch span (patches play the full keyboard) |
| Sub | 24–35 | C1–E2 | Sub-bass fundamental: chest thump, felt > heard |
| Groove (root pocket) | 36–50 | E2–D3 | Primary rhythm register: root-fifth, filter envelope |
| Mid (riff centre) | 51–62 | D#3–D4 | Octave-displacement riffs (disco), melodic fills |
| High (lead-bass) | 63–84 | D#4–C5 | Bright, cutting: acid squelch, accents, solos |

The GM patch (FluidR3) sounds convincingly across the full span 24–84
(C1–C5); the sweet spot is 38–62 (D2–D4) — the groove zone where
root-fifth pockets and octave-displacement riffs speak with full body.
Above C5 the tone thins to a squeak; below C1 the patch rolls off.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Legato (sustained gate) | 60–75 | full note | Gate held — pad-like sustained bass notes |
| Staccato (gated 16ths) | 70–85 | 0.2–0.4 | Short closed gate — the disco/funk lock groove |
| Accent (filter env) | 90–105 | 0.4–0.7 | Hard filter-envelope accent — the downbeat squelch |
| Glide (portamento) | 60–70 | full, smooth | TB-303 slide — pitch-glide between notes (pitch-bend) |
| Squelch (resonance) | 80–95 | 0.3–0.6 | Resonance peak on attack — the acid squelch |
| Octave jump | 75–90 | 0.3–0.5 | Octave-displacement riff hit — the disco signature |
| Ghost (closed gate) | 35–50 | 0.1–0.2 | Muted gate tick — rhythmic filler, no pitch |

## Timbre DNA

- **Harmonic content**: saw VCO = full harmonic series (1,2,3,4… all
  present) rolled off by the low-pass; square/pulse = odd-dominant. The
  filter position is the timbre: closed (dull sub thump) → open (bright
  buzz). The sub oscillator adds a sine one octave down for fundamental
  weight. Above ~5 kHz there is almost nothing once the filter closes —
  synth bass is a DARK voice by design.
- **Attack**: 1–5 ms gate click — the VCA opens instantly; the audible
  "pluck" is the filter envelope re-opening (0–50 ms sweep), not a
  mechanical transient.
- **Decay**: the note sustains while the gate is open (MIDI note length =
  gate length). Release is fast (10–50 ms) — the voice dies the instant
  the gate closes, which is why staccato synth bass reads so percussive.
- **Noise**: oscillator drift (analog wobble), filter self-oscillation at
  high resonance, and the saturation stage's gentle hiss — all PART of
  the analog idiom (the MonoSynth defaults include `drift_amount` 0.002
  and `saturation` 0.15 for exactly this).
- **Character**: fat, round, rubbery, squelchy — the electronic bass
  foundation of disco ("Good Times", "Le Freak"), funk (P-funk, Zapp),
  synth-pop (Depeche Mode, New Order), house/acid (TB-303), and
  modern pop/R&B (808-style sub-bass programming).

## Role in Arrangement

- **Bass** (primary): root-fifth groove, octave-displacement riffs, pedal
  tones — the electronic harmonic foundation. Locks with the kick drum
  exactly like the electric bass, but with a filtered, synthetic color.
- **Rhythm**: gated 16th-note patterns, staccato lock grooves, ghost-note
  ticks — the rhythm-section engine of dance music.
- **Groove**: the filter envelope IS the articulation — writing varied
  note lengths (gate times) is the main expressive lever, not velocity
  (velocity triggers the filter-envelope amount on many synths, but gate
  time is the signature).
- **Accent**: filter-sweep accents on the downbeat, squelch hits, octave
  jumps at phrase ends.
- NOT a lead voice (lead-bass solos exist — "Birdland", slap-bass synth
  solos — but they are the exception); NOT a harmony/pad voice (one
  oscillator voice = one note at a time).
- NOT a high-register sustain voice (above ~C4 the tone is thin and
  squelchy — use for accents, not carried melody).

## Synthesis Engines (musicom)

1. **MonoSynth** (`sound/synthesis/mono_synth.py`) — **primary**. The
   classic subtractive mono synth: single VCO (saw/pulse/sub/noise) →
   24 dB ladder filter → ADSR → LFO → saturation. This IS the
   architecture of the classic analog bass (MC-202/AD-202 lineage).
   `SYNTHESIS_DEFAULTS`: saw VCO, sub_level 0.3 (fatness), filter_cutoff
   1800, resonance 0.55 (squelch), env_a 0.005 (gate click), env_d 0.18
   (pluck), env_s 0.75 (gate sustain), env_r 0.12 (tight release),
   saturation 0.15 (analog drive).

2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — secondary. FM
   synth-bass patch: saw carrier + sine modulator at ratio 1.0, depth
   2.5 — the DX7-era "Solid Bass" style. `FM_DEFAULTS` above.

3. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   tertiary fallback. Plucked-waveguide "rubber band" approximation:
   loop_gain 0.9960, lowpass 1500 Hz — dark and tight. Not the physical
   model (there is no string) but a usable synthetic-bass color.

4. **ModalSynth** (`sound/synthesis/modal.py`) — weak fallback. 'string'
   preset = generic plucked body; not idiomatic for a filter-based bass.

## Production

- **Reverb**: small room/plate 1.0 s — synth bass is almost always dry
  (DI). Verb is a mix choice, never baked in; too much tail thins the
  low end and smears the gate articulation.
- **EQ**: cut 250 Hz (low-mid mud where the saw + sub pile up against the
  kick); boost 900 Hz (the filter-sweep growl band); gentle 6 kHz shelf
  (air) — the tone is DARK by design, no top-octave sparkle. High-pass
  below ~40 Hz in a dense mix to protect headroom.
- **Compression**: bass NEEDS compression to sit consistently (1176/DBX
  style, or the synth's own saturation); not in the defaults — a
  mix-stage decision.
- **Pan**: center (100% mono). Bass is universally centered.
- **Track**: DI into the console/DAW; analog saturation or a tube preamp
  (NEVE-style) is the classic chain for the "fat analog" sound.

## Verification

- GM38 → stem `trackXX_Synth_Bass_1.wav` (label matches, no quirk;
  FluidR3 preset 38 = "Synth Bass 1" phdr-verified)
- Zero-drift: units end flush at BAR (terminal landmark)
- Solo render only (no unison doubling — comb-filtering buzz rule applies
  if a second melodic patch plays the same bass line)
- Spectral 4–8 kHz buzz well below 20% (synth bass is a LOW instrument
  with little energy above 4 kHz once the filter closes)
- MonoSynth smoke test: subtractive render produces audible low-frequency
  output with the expected "gate click → filter pluck → sustain" shape
- Empirical FluidR3 pitch sweep: preset 38 audible across the full
  24–84 span, no gaps — SF2 never clips a composition
