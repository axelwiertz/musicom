---
type: instrument
family: Synth
name: Synth Strings 1
midi_program: 50
gms: "Synth Strings 1"
range_min: 36
range_max: 96
solo_range: [52, 88]
role: [pad, harmony, texture, drone, lead, countermelody, accent]
synthesis: [polysynth, additive, phase_mod]
---

# Synth Strings 1

## MIDI / GM

- **Program**: 50 (GM1 "Synth Strings 1")
- **Channel**: melodic channel; polyphonic (the patch plays full chords)
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 50 =
  **"Synth Strings 1"** (TimGM6mb fallback also carries preset 50).
  RenderPipeline stem label: GM_PROGRAMS[50] = **"Synth Strings 1"** →
  `trackXX_Synth_Strings_1.wav` — sanitizer only rewrites spaces/parens/slashes,
  so label matches exactly, **no quirk** (verified on disk in
  `_test/stems_synth_strings_1/`).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  programs and has **no** synth-strings constant — use the raw GM number 50;
  the registry is the full KB.

## Identity — what this patch actually is

GM50 is not "strings played on a synthesizer" in the modern sample-replay
sense; it is the **divide-down string machine**, the 1972–1982 keyboard class:
Eminent 310 Unique (1972), ARP Solina String Ensemble (1974), ARP Omni,
Roland RS-202, Korg Poly-Ensemble, Elka Rhapsody, Logan String Melody,
Crumar Performer.

Architecture (this drives every playing decision):

- **Divide-down oscillator bank** — one master oscillator chain divided down to
  produce all 12 pitches per octave, borrowed across octaves. The tone is a
  bright, buzzy **square/saw hybrid** band-limited by the divider chain.
- **One shared filter + one shared LFO** for the entire keyboard. The machine is
  **paraphonic, not truly polyphonic**: every held note is modulated by the same
  chorus/vibrato phase. You cannot give one note vibrato and leave another
  still. (In musicom this is modelled with a *static* per-voice detune — never
  per-note vibrato.)
- **Triple BBD (bucket-brigade) ensemble chorus** — three delay lines modulated
  by phase-shifted LFOs (~0.3–1.5 Hz). This is the signature "string machine
  swirl": a slow, wide, slightly out-of-tune shimmer across the whole chord.
  It is pitch modulation and comb coloration, not amplitude tremolo.
- **No velocity sensitivity, no bow noise, no rosin, no body resonance.**
  Attack is a fast-but-soft 20–40 ms (capacitor envelope), not the 300 ms swell
  of a bowed section; sustain is **infinite while a key is held** (no natural
  decay, unlike a sampled string ensemble's loop with breath/decay); release is
  a short 100–300 ms capacitor fade.

Records: Pink Floyd "Shine On You Crazy Diamond" (Eminent 310), Jean-Michel
Jarre *Oxygène* (Eminent/Solina), Air "Sexy Boy", Goldfrapp, Tame Impala,
disco-era string pads, and countless 70s/80s film and TV cues.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM patch span (original machines were 4-octave, 49-key) |
| Low | 36–55 | C2–G3 | cello-ish body; pad roots — gets muddy below C2 fast |
| Middle | 56–79 | G#3–G5 | primary pad/harmony band — the workhorse |
| High | 80–96 | G#5–C7 | violin-top sheen; above ~C7 the divider tone thins to fizz |

SOLO_RANGE 52–88 (E3–E6) is the idiomatic string-machine writing band: the
chorus has enough partials to swirl and the buzz stays musical.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 70 | 1.0 (held) | default pad chord — infinite hold, chorus swirl |
| Legato | 68 | 1.0 | overlapping chord change, no re-attack click |
| Swell | 82 | 1.0 | slow crescendo build — the machine's only "expression" |
| Staccato | 66 | 0.25 | short chord stab — disco/synth-pop chop |
| Marcato | 86 | 0.85 | hard downbeat chord, chorus blooms after |
| Drone | 58 | 1.0 | static held harmony — ambient bed |
| Accent | 90 | 0.9 | unison hit, then sustain |

Note: velocity has little effect on a real string machine (no velocity
sensing). In musicom, velocity mainly scales loudness; do **not** expect the
GM patch to change timbre with velocity — write dynamics as arrangement
(density, register, doubling), not as hard/soft playing.

## Timbre DNA

- **Harmonic content**: dense, slightly buzzy square/saw partial stack; strong
  2nd–6th partials, band-limited top (BBD bandwidth rolls off ~6–8 kHz — no
  real 10 kHz air, unlike a sampled section)
- **Attack**: 20–40 ms soft capacitor onset — fast but not percussive
- **Decay/sustain**: **none/sustained** — flat while held, no natural decay
- **Release**: 100–300 ms capacitor fade
- **Modulation**: whole-ensemble chorus, ~±8–15 cents at 0.3–1.5 Hz, wide
  stereo; never a single-note vibrato
- **Character**: lush, swirling, slightly detuned, "cheap but glorious";
  instantly 70s/80s

## Role in Arrangement

- **Pad / harmony** — sustained chords under lead or vocal; the default use
- **Texture** — wide chorus bed, dense mid-register cluster
- **Drone** — static held root/fifth for ambient or modal writing
- **Lead** — unison (all three chorus voices on one note) string-machine lead
  lines, e.g. disco/synth-pop hooks
- **Countermelody** — sustained line under a moving lead
- **Accent** — swell hit at a section boundary
- NOT a bass foundation (bottom is thin and chorused — use a bass patch)
- NOT a realistic orchestral section (that is GM48 String Ensemble 1 / GM49
  String Ensemble 2). GM50 is the *synthetic* sibling: brighter, wider, more
  obviously processed.

## Synthesis Engines (musicom)

1. **PolySynth** (`sound/synthesis/polysynth.py`) — **primary**. The subtractive
   architecture *is* the physical model: divide-down saw/square bank → shared
   low-pass filter → BBD ensemble chorus. Use 3 detuned unison voices
   (±7–10 cents) for the chorus, filter ~3000 Hz, attack 0.03 s, sustain 1.0,
   release 0.25 s. This is the only engine that reproduces the constant
   swirl-and-filter character.
2. **Additive** (`sound/synthesis/additive.py`) — secondary. Detuned harmonic
   stack with slow swell; cheaper for dense arrangements, loses the BBD
   comb coloration. Same engine family as string_ensemble/synth_pad.
3. **PhaseModSynth** — tertiary cheap approximation: saw carrier, ratio 1.0,
   depth ~1.2 (gentle — this is not a brass patch), attack 0.03, release 0.3.

## Production

- **Reverb**: hall 2.6–3.0 s (REVERB_TAIL 2.8) — the chorus already supplies
  width; the hall supplies depth
- **EQ**: cut 250 Hz −2.5 dB (chord mass piles up in the low-mid); boost
  3.2 kHz +2.0 dB (the divider buzz articulation); gentle 8 kHz +1.5 dB shelf
  (BBD top is dull — a little air restores it, but do not chase sampled-string
  sparkle)
- **Pan**: center for the composed stem; the patch itself is wide, so ±0.2 L/R
  is enough when doubling for a bigger bed (the chorus does the rest)
- **Doubling discipline**: doubling with GM48/49 on the SAME pitches adds level
  but thickens into mush; if used together, put the synth strings an octave up
  or on a different chord tone (never unison-double melodic patches — the
  2026-09-01 comb-filter rule)

## Verification

- GM50 → stem `trackXX_Synth_Strings_1.wav` (label matches, no quirk)
- FluidR3 preset 50 = "Synth Strings 1" (verified from phdr chunk)
- Zero-drift: sustained chord units end flush at BAR (terminal landmark)
- Solo render (no unison doubling): spectral 4–8 kHz buzz gate ≤20% passes —
  the patch is *supposed* to be bright, but the gate catches real
  comb-filtering
