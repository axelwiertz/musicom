---
type: instrument
family: Synth
name: Synth Brass 1
midi_program: 62
gms: "Synth Brass 1"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [lead, harmony, accent, stab, pad, countermelody]
synthesis: [polysynth, phase_mod, additive]
---

# Synth Brass 1 (GM62)

## MIDI / GM

- **Program**: 62 (GM1 "Synth Brass 1"; Roland GS "Synth Brass 1", Yamaha XG
  "SynthBrass1"). The classic analog synth brass: a stack of slightly-detuned
  sawtooth oscillators through a resonant low-pass filter with a fast attack
  and punchy ADSR — the "brassy stab" voice of funk/disco/synth-pop/film.
  GM program numbers are 0-based, so 62 is the 63rd entry.
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments and has NO synth-brass constant (it has SYNTH_PAD=88, the one
  exact GM match). Use the raw GM number 62 — the registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 62 would trigger
  the drum-kit map and the program-0 fallback label `Acoustic_Grand_Piano`
  (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 62 =
  **"Synth Brass 1"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[62] = "Synth Brass 1" → sanitized
  `trackXX_Synth_Brass_1.wav` — matches STEM_LABEL "Synth_Brass_1" exactly,
  **no quirk** (FluidR3 preset 62 = "Synth Brass 1" — same label; GM63
  "Synth Brass 2" is the softer/darker sibling).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM-patch idiomatic writing band |
| Low | 36–55 | C2–G3 | brass-pad root zone — sustained chord bottoms, drone stabs (mud below C2) |
| Mid | 56–71 | B3–C5 | workhorse band — stab chords, horn-call figures, ensemble punches |
| High | 72–84 | C5–C6 | lead/unison brass — piercing synth top line, octave-doubled stabs |
| Top extension | 85–96 | C6–C7 | thin sparkle stabs, risers |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24–108 step 6): preset
62 audible **15/15 notes, no gaps** (RMS 1409–2503 across the whole span;
bottom 24 the loudest at 2503, mid/treble flat ~1400–1700). GM synth patches
are full-keyboard: **no patch ceiling** — SF2 never clips a composition.
Range 36–96 is the idiomatic *writing* band (mud below C2, squeak above C7),
NOT a physical limit.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Stab | 90–100 | 0.3× | THE signature — fast attack, short gate, the funk/disco horn punch |
| Sustain | 70–85 | full | brass-pad swell — held chord, filter opens |
| Swell | 65–80 | 1.15× | crescendo swell — whole-bar build (synth-pop move) |
| Legato | 70–80 | full | seamless lead crossfade — unison synth brass |
| Marcato | 85–95 | 0.7× | accented entrance — downbeat punch |
| Staccato | 65–75 | 0.25× | short gated 8ths — rhythmic comp stabs |
| Sforzando | 95–105 | 0.35× | hard accent then cut — the "hit" |
| Rip | 88–98 | 0.2× | rising gliss stab — film brass rip (pitch-bend in MIDI; fast chromatic run in SF2) |

## Timbre DNA

- **Harmonic content**: sawtooth stack with slight detune (the "section"
  width), strong fundamental + rich odd/even harmonics rolled off by the
  low-pass filter (typical cutoff 2–5 kHz); brassy mid "honk" around
  2–3 kHz. Measured (FluidR3, solo): spectral centroid C4 = 1744 Hz,
  C6 = 3626 Hz — brightness rises with pitch, edge is in the 2.8 kHz band
- **Attack**: 1–20 ms — the fastest family onset (a stab must punch); the
  attack transient IS the articulation (contrast: acoustic brass attacks
  30–60 ms)
- **Decay/sustain**: indefinite while held (synthesizer — no physical
  decay); release 0.2–0.5 s, medium — stabs tail cleanly, pads breathe
- **Vibrato**: LFO on filter/pitch (0.5–1.0 Hz, subtle), not player vibrato —
  usually absent on stabs, gentle on sustained pads
- **Character**: bright, brassy, punchy, synthetic; the electronic "horn
  section" of funk/disco/synth-pop (EW&F "Shining Star" stab, Gary Numan,
  Depeche Mode, film-score synth brass swells)

## Role in Arrangement

- **Lead** — unison synth-brass leads (doubled at the octave for width);
  piercing high-register top lines (72–84)
- **Harmony** — brass-pad sustained chords; stab-chord comping (the funk
  "horn hit" on the 1 and the "and")
- **Accent** — sfz hits, marcato downbeats, riser swells — the punctuation
  voice of synth arrangements
- **Stab** — short gate punches are the identity: rhythmic stab patterns
  (8th/16th), call-and-response horn licks
- **Pad** — sustained brass swells (swell articulation) under a lead
- **NOT** a bass voice (use Synth Bass 1 GM38 / Electric Bass GM33), NOT an
  acoustic-brass substitute (no physical articulation — keep stabs/staccato
  short, no real brass fall/rip without pitch-bend)
- Polyphonic: 3–5 note stab chords and brass-pad harmony are fully
  idiomatic (contrast: the monophonic acoustic brass leads)

## Synthesis Engines (musicom)

1. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — **primary**.
   The polyBLEP subtractive architecture IS the analog brass: saw osc stack
   (osc2 detuned +7 cents for section width, thin square sub for body),
   24dB multimode low-pass (cutoff ~2800 Hz, resonance 0.45, per-note
   filter env 0.35), ADSR attack 0.015 s / decay 0.18 / sustain 0.75 /
   release 0.25, 2 unison voices. POLYSYNTH_DEFAULTS carries the recipe.
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — the FM brass of the
   acoustic Brass family (brass_section precedent): saw carrier, sine
   modulator ratio 1.0, depth **3.2** (between brass_section 2.8 and
   overdriven 4.0 — the synth brass is edgier than acoustic), attack
   0.02 s, release 0.25 s, sustain 0.75 (FM_DEFAULTS).
3. **Additive** (`sound/synthesis/additive.py`) — harmonic-stack fallback
   with brass-like rolloff: weights [1.0, 0.9, 0.7, 0.5, 0.35, 0.2, 0.12,
   0.08] (ADDITIVE_DEFAULTS).

## Production

- **Reverb**: hall/plate 2.0–2.4 s — REVERB_TAIL 2.2 s; shorter than
  brass_section 2.5 (synth stabs want a drier punch than a real brass
  tutti), longer than synth_bass 1.0 (stabs bloom, pads breathe)
- **EQ**: cut ~300 Hz (saw stack + square sub crowd the low-mid); boost
  ~2.8 kHz presence (the brassy bite band); gentle 8 kHz air shelf —
  bright by design but not a cymbal
- **Pan**: center for the composed stem; ±0.3 L/R spread on wide
  unison-stab doubles (the synth "section" width trick)
- **Layering**: idiomatic doubling is octaves (synth brass + same patch 8vb,
  or + brass_section for the hybrid analog/acoustic wall) — NEVER unison
  with another melodic patch on the same pitches (comb-filtering — the
  2026-09-01 lesson). Synth brass + synth bass root-octave below is the
  classic electronic brass-section stack

## Verification

- GM62 → stem `trackXX_Synth_Brass_1.wav` (GM_PROGRAMS[62] = "Synth Brass 1",
  FluidR3 preset 62 = "Synth Brass 1" — labels match exactly) — **no quirk**
- `by_name('synth brass 1')` → Synth Brass 1, `by_program(62)` → Synth
  Brass 1, `in_sweet_spot(67)` = True, `in_sweet_spot(24)` = False
- Empirical pitch sweep: preset 62 audible 15/15 notes (24–108), no gaps
- Buzz check: solo chord render passes the 4–8 kHz spectral gate (single
  voice + single patch, no comb-filtering)
- Zero-drift: stab chord ends flush at BAR (terminal landmark)
- Engine smoke: polysynth saw-stack brass note renders (peak > 0, sustain
  holds); PhaseModSynth saw-brass note renders

## Stem label / quirks

- GM_PROGRAMS[62] = "Synth Brass 1" → sanitized stem `Synth_Brass_1`
  (space → underscore) — matches STEM_LABEL, **no routing quirk**
- FluidR3 preset 62 = "Synth Brass 1" — exact match (contrast: GM74 Flute →
  "Recorder", GM109 → "Bag pipe", GM111 → "Shanai" quirks)
- GM63 "Synth Brass 2" is the softer/darker sibling (a future candidate —
  same family, rounder filter)
- Enum `MidiInstrument` has NO synth-brass constant (10-instrument legacy
  enum) — use raw GM 62; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 synth-brass presets are full-keyboard patches (no per-note
  ceiling like timpani/pizzicato) — never clips; keep stabs short (≤ 0.3
  bar) so the punch stays a punch
