---
type: instrument
family: Synth
name: Orchestra Hit
midi_program: 55
gms: "Orchestra Hit"
range_min: 36
range_max: 96
solo_range: [48, 84]
role: [accent, stab, rhythm, punctuation, texture, lead]
synthesis: [additive, phase_mod, polysynth]
---

# Orchestra Hit (GM55)

## MIDI / GM

- **Program**: 55 (GM2 "Orchestra Hit"; Roland GS "Orchestra Hit", Yamaha XG
  "Orchestra Hit"; often called "Orchestral Hit"). The iconic ONE-SHOT
  ensemble stab: a dense layered stack of brass + strings + choir samples
  fired with a razor-sharp attack and a fast exponential decay — the
  punctuation of 80s pop, hip-hop, film trailers and game scores (Yes
  "Owner of a Lonely Heart", MTV/network ident stabs, beat drops).
  GM program numbers are 0-based, so 55 is the 56th entry.
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments and has NO orchestra-hit constant. Use the raw GM number 55 —
  the registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 55 would trigger
  the drum-kit map and the program-0 fallback label `Acoustic_Grand_Piano`
  (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 55 =
  **"Orchestra Hit"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[55] = "Orchestra Hit" → sanitized
  `trackXX_Orchestra_Hit.wav` — matches STEM_LABEL "Orchestra_Hit" exactly,
  **no quirk** (same label in GM_PROGRAMS and FluidR3).
- **One-shot quirk**: the patch is a SAMPLE — it fires once per note-on and
  decays; a long MIDI note does NOT sustain (the muted-guitar lesson). Write
  short strikes and let the decay + reverb do the work.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM-patch idiomatic writing band |
| Low | 36–47 | C2–B2 | sub-hit thump — riser bottoms, drop punctuation (mud below C2) |
| Mid | 48–71 | C3–B4 | workhorse stab band — downbeat hits, syncopated punctuation, beat-drop stabs |
| High | 72–84 | C5–C6 | bright top hits — cinematic stabs, octave-doubled punctuation |
| Top extension | 85–96 | C6–C7 | thin sparkle hits, riser ticks |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36/48/60/72/84/96):
preset 55 audible **6/6, no gaps** (RMS 1345 / 1235 / 927 / 757 / 527 / 374 —
smooth rolloff, loudest at the bottom, ~3.6× quieter at the top). GM one-shot
patches are full-keyboard: **no patch ceiling** — SF2 never clips a
composition. Range 36–96 is the idiomatic *writing* band, NOT a physical
limit; the classic hit is most effective 48–84.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Hit | 92–100 | 0.2× | THE signature — one-shot ensemble stab, the 80s/hip-hop/trailer punctuation |
| Accent | 100–108 | 0.1× | hard downbeat smash — the "1" of the drop |
| Stab | 86–94 | 0.15× | syncopated rhythmic stab — off-beat punches |
| Sforzando | 98–106 | 0.12× | maximum attack, then cut — the "hit!" |
| Repeat | 80–90 | 0.25× | rapid retriggers — 8th/16th hit patterns (each note-on re-fires the sample) |
| Swell | 74–82 | 0.5× | held hit — the decaying tail rings into the verb |
| Light | 66–74 | 0.2× | soft tap — ghost punctuation, riser accents |
| Tick | 56–64 | 0.1× | dry tick — sparse top-register punctuation |

## Timbre DNA

- **Harmonic content**: dense — a layered brass+strings+choir stack, strong
  fundamental with a slow partial rolloff (many near-equal partials = the
  "wall of sound"); measured (FluidR3, solo) bright — centroid rises with
  pitch, transient carries a broadband click
- **Attack**: 1–5 ms — the razor transient IS the instrument (the fastest
  onset in the Synth family; contrast synth_brass_1's 15 ms)
- **Decay/sustain**: NO sustain — exponential collapse over ~0.5–1.5 s (a
  sample one-shot; the muted-guitar lesson: the patch does not ring while
  held, it decays once)
- **Vibrato**: none — a one-shot has no LFO wobble; the decay is the motion
- **Character**: cinematic, percussive, triumphant; the "orchestra hits!"
  punctuation of 80s pop/hip-hop/film (Yes, MTV idents, beat drops)

## Role in Arrangement

- **Accent** — the punctuation voice: downbeat hits, drop stabs, sfz
  smashes on the "1" or the "and" (the film/trailer move)
- **Stab** — rhythmic hit patterns (8th/16th), call-and-response punctuation
- **Rhythm** — a one-shot can BE the rhythmic hook (syncopated hit figures,
  drop pre-chorus punctuation)
- **Punctuation/texture** — riser bottoms, section markers, beat-drop
  punctuation; sparse use = maximum impact (the tuba/taiko lesson: use
  sparingly, one strike at a time)
- **Lead** — occasional unison-hit melody accents at 72–84 (rare — the hit
  is a colour, not a line)
- **NOT** a pad/harmony voice (no sustain — use synth_pad/warm_pad/string_
  ensemble for held harmony), NOT a bass voice, NOT a melodic lead voice
- Polyphonic patch but idiomatically MONOPHONIC: one hit at a time (a real
  "orchestra hit" is a single simultaneous tutti strike — stacked hits
  smear into noise)

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py`, SoundWave) — **primary**.
   The classic recipe IS a dense harmonic stack with a razor attack + fast
   exponential decay: `ADDITIVE_HARMONICS["orchestra_hit"]`
   [1.0, 0.88, 0.75, 0.60, 0.45, 0.32, 0.20, 0.12] (normalize to sum 1.0
   before `apply_overtones`), SYNTHESIS_DEFAULTS attack 0.005 s, decay_S
   0.002 (FAST collapse — the one-shot behaviour; contrast the pads' 1e-4
   hold recipe), sustain_level 0.35, release 0.35, detune ±0.008, stack 3
   (the layered-sample wall).
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — the FM ensemble
   stab: saw carrier, sine modulator ratio 1.0, depth **3.5** (between
   synth_brass_1 3.2 and overdriven 4.0 — the bright ensemble edge), attack
   0.005 s, release 0.40 s, sustain 0.30 (FM_DEFAULTS).
3. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — the
   subtractive ensemble stab: saw stack (osc2 detuned +6c, thin square sub)
   through a high 24dB low-pass 3500 Hz, razor gate 0.005 s, fast decay 0.4,
   sustain 0.3, 3 unison voices (POLYSYNTH_DEFAULTS).

## Production

- **Reverb**: hall/plate 1.6–2.0 s — REVERB_TAIL 1.8 s; shorter than
  synth_brass_1 2.2 (a one-shot in a 3 s verb is a smear). The decayed tail
  rings into the room, then stops.
- **EQ**: cut ~300 Hz (the dense stack piles the low-mid fast); boost
  ~2.5 kHz presence (the stab bite band); gentle 9 kHz air shelf — the
  transient is a click, not a cymbal.
- **Pan**: center for the composed stem; ±0.3 L/R spread on wide doubled
  hits (the "big screen" width trick — double the SAME hit hard L/R, never
  unison with another melodic patch).
- **Layering**: idiomatic doubling is the SAME patch octave-doubled or hard
  L/R double-hit — NEVER unison with another melodic patch on the same
  pitches (comb-filtering — the 2026-09-01 lesson). An orchestra hit + bass
  root-octave below + drums = the classic drop.

## Verification

- GM55 → stem `trackXX_Orchestra_Hit.wav` (GM_PROGRAMS[55] = "Orchestra Hit",
  FluidR3 preset 55 = "Orchestra Hit" — labels match exactly) — **no quirk**
- `by_name('orchestra hit')` → Orchestra Hit, `by_program(55)` → Orchestra
  Hit, `in_sweet_spot(67)` = True, `in_sweet_spot(24)` = False
- Empirical pitch sweep: preset 55 audible 6/6 notes (36–96), no gaps,
  smooth rolloff
- Buzz check: solo hit render passes the 4–8 kHz spectral gate (single
  voice + single patch, no comb-filtering)
- Zero-drift: hit unit ends flush at BAR (terminal landmark)
- Engine smoke: additive orchestra_hit stack renders (peak > 0);
  PhaseModSynth saw-stab note renders

## Stem label / quirks

- GM_PROGRAMS[55] = "Orchestra Hit" → sanitized stem `Orchestra_Hit`
  (space → underscore) — matches STEM_LABEL, **no routing quirk**
- FluidR3 preset 55 = "Orchestra Hit" — exact match (contrast: GM74 Flute →
  "Recorder", GM109 → "Bag pipe", GM111 → "Shanai" quirks)
- GM2 spec also names it "Orchestral Hit" — the GM label and SF2 both use
  "Orchestra Hit"; either spelling resolves via `by_name`
- Enum `MidiInstrument` has NO orchestra-hit constant (10-instrument legacy
  enum) — use raw GM 55; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- **One-shot quirk**: the FluidR3 patch is a sample — it fires once per
  note-on and decays; a long MIDI note does NOT sustain (the muted-guitar
  lesson). Write short strikes (≤ 0.2 bar) and let the decay + reverb work.
- Selection note: GM55 was collision-free — `by_program(55)` had no owner
  (54 Synth Voice, 56 Trumpet, 62 Synth Brass 1 are all distinct), and the
  stem `Orchestra_Hit` was unclaimed.
