---
type: instrument
family: Keys
name: Honky-tonk Piano
midi_program: 3
gms: "Honky-tonk Piano"
range_min: 33
range_max: 96
solo_range: [48, 84]
role: [rhythm, harmony, melody, bass, ornament, color]
synthesis: [modal, additive, phase_mod]
---

# Honky-tonk Piano (Tack Piano / Saloon Piano)

## MIDI / GM

- **Program**: 3 (0-based MIDI program 3 = the 4th GM entry, "Honky-tonk
  Piano"). NOT in `structures/instrument.py` `MidiInstrument` enum (10 only) —
  use raw `program=3` in `add_voice`.
- **Channel**: any melodic channel (0-9). Channel 9 with program 3 would
  trigger the drum-kit map and the program-0 fallback label
  `Acoustic_Grand_Piano` (ch9 quirk).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 bank-0 preset 3 =
  **"Honky Tonk"** (phdr-verified; hyphen dropped and the space kept — purely
  cosmetic, no routing impact).
- **Pipeline stem label**: `GM_PROGRAMS[3]` = "Honky-tonk Piano" → disk stem
  `trackXX_Honky-tonk_Piano.wav`. `RenderPipeline` sanitizes spaces → `_`,
  strips `(`/`)` and `/` — the **hyphen is preserved**, so the stem keeps the
  hyphen. STEM_LABEL = `"Honky-tonk_Piano"` matches that exactly.

## Identity

The honky-tonk piano is a **deliberately detuned, hardened-hammer piano** — the
instrument of the American saloon, the ragtime parlour, the barrelhouse and the
country roadhouse. Two physical things define it:

- **Detuned unison strings.** Each note on an acoustic piano is strung with 2-3
  strings tuned to the same pitch. A honky-tonk piano leaves those unisons
  **out of tune with each other by roughly 10-25 cents**. The two slightly
  different frequencies beat against each other at 1-8 Hz, producing the
  shimmering, "sour", chorus-like wobble that is the instrument's signature.
  (This is why it is sometimes called a "jangle piano".)
- **Hard hammers — the "tack piano".** In the literal tack piano, thumbtacks or
  hardened leather are fitted to the hammer heads, so the hammer strikes the
  string with a metallic click instead of soft felt. The attack becomes a
  bright, percussive **clack** with strong upper partials, closer to a
  harpsichord than to a grand piano. Many honky-tonk recordings use a plain
  upright with simply worn, hardened hammers — same effect, milder.

Historically the detuning was **functional**: in a crowded, noisy bar with no
sound system, a bright clacky attack and a beating, penetrating midrange let the
piano cut through conversation and a room full of people. Sound engineers later
made it an aesthetic — the saloon-piano sound of Westerns, ragtime revivals and
country "honky-tonk" (the genre is named after the bars, and the piano is named
after the genre).

Consequences for composition:

- **The beating is the identity.** A perfectly tuned honky-tonk part is just a
  bad piano part. Write sustained notes and let the 2-8 Hz wobble speak; do not
  fill every beat.
- **Attack is percussive.** The tack clack means the instrument reads as a
  rhythm instrument: short chords, clipped stride off-beats, rolling boogie
  eighths. Long legato lines sound wrong.
- **Midrange-forward, not bass-heavy.** The honky body lives around 1-2 kHz;
  the low end is a small upright cabinet, not a concert grand. Do not use it as
  a sub-bass foundation.
- **Nostalgia / irony are part of the timbre.** It reads instantly as
  ragtime, saloon, vaudeville, Western, or as a knowing lo-fi/indie colour.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 33–96 | A1–C7 | idiomatic writing compass (GM patch spans more, but thins at both ends) |
| Sweet spot | 55–84 | G3–C6 | fullest honky body, the "nasal" bark |
| Bass | 33–47 | A1–B2 | stride/boogie left hand: octaves, tenths, walking bass |
| Mid-low | 48–59 | C3–B3 | chord comping body, the saloon honk |
| Mid | 60–71 | C4–B4 | ragtime melody + right-hand chords |
| High | 72–96 | C5–C7 | ragtime runs, octave tremolo, glissandi |

A real piano is A0–C8 (21–108). The honky-tonk *patch* is a small upright: below
A1 the cabinet thins to mud and the detuning turns to a rattle, above C7 the
tacks dominate and the note loses pitch. Empirical FluidR3 sweep (RMS, velocity
90, notes 24–108 step 12): preset 3 is audible across the whole tested span with
no gaps — A1=968 … C4=469 … C6=167 … C8=100 (RMS ×10⁴); the tail-off is the
patch's natural upright rolloff, not a gap.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Ragtime melody | 80–100 | 0.9–1.0× | crisp syncopated RH line, tack attack |
| Stride bass ("oom") | 85–100 | 0.4–0.6× | short percussive low octave |
| Stride chord ("pah") | 70–85 | 0.25–0.45× | clipped off-beat chord |
| Boogie ostinato | 80–90 | 0.4–0.5× | rolling eighth-note LH figure |
| Comp chop | 70–80 | 0.25–0.35× | country/pop honky stab |
| Octave tremolo | 75–90 | full, repeated | alternating octaves, fast |
| Glissando | 90–105 | 0.9× | white-key rake, one gesture |
| Tack accent | 100–115 | 0.8–0.9× | metallic clack, hard hammer |
| Sustain wash | 50–65 | full | pedal down, chord rings in the room |
| Dead thud | 40–50 | 0.15–0.2× | damped "plunk" — comic saloon note |

## Timbre DNA

- **Beating unisons**: two or three strings per note at 10-25 cents apart →
  amplitude modulation at 1-8 Hz on every sustained note. This is the single
  most important feature; any synthesis recipe MUST include a detuned twin.
- **Attack**: 1-5 ms hammer strike plus a broadband metallic **clack**
  (tack/hardened felt), strongest 2-6 kHz. Much brighter than a grand piano.
- **Partials**: piano-like harmonic series with a small stretch (B ≈ 1e-4);
  the detuned twin doubles each partial, so the spectrum is dense and slightly
  "dirty" rather than clean.
- **Decay**: 1-3 s in the mid register with pedal, faster in the treble; the
  upright's short cabinet gives a quick low-end decay.
- **Body resonance**: small upright cabinet — a boxy low-mid bump around
  200-400 Hz and a nasal peak around 1.5-2.5 kHz.
- **Character**: bright, clacky, slightly sour, nostalgic, percussive,
  mid-forward; never lush, never sub-bass.

## Role in Arrangement

- **Rhythm / comp**: the primary role. Stride left hand (bass note on 1 and 3,
  chord on 2 and 4), boogie rolling eighths, country backbeat chops.
- **Melody**: ragtime right-hand lines (syncopated, octave-heavy, chromatic
  passing tones); also novelty/cartoon "saloon" melodies.
- **Harmony**: block chords and stride comping; keep voicings open (the dense
  detuned spectrum turns thick closed chords to mush).
- **Bass**: left-hand stride/boogie bass only, A1–B2; it is a *rhythmic* bass,
  not a foundation — pair with a real bass instrument for the low end.
- **Ornament / color**: glissandi, octave tremolos, tack accents, dead-thud
  comic notes, saloon-bar atmosphere.
- **Not for**: sustained pads (the beating becomes seasick), legato chorales,
  solo ballads, or any dense 4-5 note close-voiced chord work.

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**. A struck string is
   an inharmonic modal bank; the honky-tonk is that bank with **every partial
   doubled at a detuned twin** (+17 cents, amplitude 0.8). `HONKY_TONK_MODES`
   in `honky_tonk.py` gives the 10 modes (5 partials × 2 strings) with stretched
   ratios and partial-dependent decay. Measured: the twin pair at 440.0/444.3 Hz
   beats at **4.3 Hz**, inside the 1-8 Hz honky window. Stock preset `'string'`
   is the tuned fallback (no beating — use only for clean-piano doubling).
2. **Additive** (`sound/synthesis/additive.py`) — **secondary**. A harmonic
   stack with `stack=2, detune=±0.010` (±17 cents) produces the same beating by
   summing two detuned stacks. Weights `ADDITIVE_HARMONICS["honky_tonk"]` =
   [1.0, 0.62, 0.44, 0.27, 0.16, 0.09, 0.04] (lifted 2nd/3rd = the nasal honk);
   normalize to sum 1.0 before `apply_overtones()` (API asserts sum == 1.0).
   Use `decay_S = 1e-4` for held notes (the additive long-hold quirk).
3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **tertiary**. FM piano:
   sine carrier + sine modulator, ratio 2.01 (stretched 2nd partial), depth 1.6,
   attack 3 ms, release 0.35 s. Clean and controllable; add a short noise burst
   for the tack clack.

## Production

- **Reverb**: small wooden **room**, 1.2–1.6 s, low pre-delay — close-miked bar
  upright. A hall tail smears the tack attack and turns the beating to mud.
- **EQ**: cut ~300 Hz (upright cabinet boom), boost ~1.8 kHz (the nasal honk),
  high shelf ~8 kHz +1.5 dB (tack clack air).
- **Dynamics**: the patch is compressed by design — a hard tack accent is only
  moderately louder than a normal note; carry the contour with articulation and
  register, not with velocity extremes.
- **Layering**: if doubled with a clean/tuned piano, keep them at different
  octaves or pan them apart — two detuned pianos on the SAME pitches multiply
  the beat rate and sound seasick (the general no-unison-doubling rule).
- **FluidSynth note**: FluidR3 preset 3 "Honky Tonk" is a properly detuned
  upright sample — good enough for arrangement demos; for the tack-piano clack
  and controllable beat depth, use the ModalSynth `HONKY_TONK_MODES` bank.

## Verification

- GM3 → stem `trackXX_Honky-tonk_Piano.wav` (GM_PROGRAMS[3] = "Honky-tonk
  Piano"; hyphen preserved by the sanitizer — see registry.md)
- FluidR3 bank-0 preset 3 = "Honky Tonk" (phdr-verified; cosmetic hyphen drop)
- Solo render passes the 4–8 kHz spectral buzz gate (the tack air is at 2-6 kHz,
  the gate catches comb-filter buzz above that)
- Zero-drift: struck/piano-style units must end flush at BAR (terminal landmark
  `MusicEvent(0, 0, len_ticks, BAR)`) or `validate()` fails
- **Beating quirk (measured)**: 440.0 vs 444.3 Hz = 4.3 Hz beat — verify with an
  envelope-AM measurement, not by ear on a short render
- Empirical FluidR3 pitch sweep documented in `_test/verify_honky_tonk.py`

## Instrument.md companion

`honky_tonk.py` — importable constants. Registered in
`instrument_registry.py` (2026-11-07) as `Keys.honky_tonk.honky_tonk` → key
`honky_tonk`, constant `HONKY_TONK`.
