---
type: instrument
family: Strings
name: String Ensemble 2
midi_program: 49
gms: "String Ensemble 2"
range_min: 28
range_max: 96
solo_range: [53, 89]
role: [pad, harmony, texture, melody, countermelody, accent]
synthesis: [string_ensemble, polysynth, additive, phase_mod]
---

# String Ensemble 2

## MIDI / GM

- **Program**: 49 (GM1 String Ensemble 2 — the SLOW-ATTACK string ensemble,
  the analog "string machine" patch; GM48 String Ensemble 1 is the
  fast-attack orchestral section — see `Strings/string_ensemble/`)
- **Channel**: melodic channel (0–9); sustained ensemble PAD
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 49 =
  "Slow Strings" (the SF2 name IS the character; TimGM6mb fallback preset
  49 = "String Ensemble 2"). RenderPipeline stem label: GM_PROGRAMS[49] =
  "String Ensemble 2" → `trackXX_String_Ensemble_2.wav` — matches exactly,
  **no quirk** (SF2 name "Slow Strings" is cosmetic only, no routing
  impact).
- **Enum note**: `structures/instrument.py` `MidiInstrument.STRING_ENSEMBLE =
  49` — the legacy enum's string-ensemble constant happens to equal GM49
  (the Slow Strings patch). The registry is the full KB; use
  `by_name('string ensemble 2')` / `by_program(49)` / `STRING_ENSEMBLE_2`.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 28–96 | C1–C7 | GM patch span (empirical: audible 12–96, SILENT at 108+) |
| Low | 28–47 | C1–B2 | divide-down rumble — roots, drone bottom (write sparingly) |
| Mid | 48–71 | C3–B4 | primary chord-pad body — the workhorse band |
| High | 72–96 | C5–C7 | ensemble top — melody/countermelody, cutting but warm |

Empirical FluidR3 pitch sweep (RMS, notes 12–108 step 12): preset 49
audible 12–96 (9/9 notes, essentially flat 0.09–0.18 RMS — no rolloff, no
gaps), SILENT at 108 (C8, noise floor). The SF2 patch plays the full GM
span at full level, so it never clips a composition. Real-instrument note:
the archetypal ARP Solina String Ensemble is a 49-key divide-down keyboard
≈ C2–C6 (MIDI 36–84); below C2 the machine's low register is rumble, not
music — keep chord roots at C3+ in dense writing.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 65–80 | full | slow-swelling pad — the default gesture |
| Legato | 65–75 | full | seamless voice crossfade — chord changes |
| Swell | 78–88 | full | crescendo swell — whole-bar build (ballad trick) |
| Staccato | 60–72 | 1/4 | short pad "blip" — rhythmic filter-pulse motif |
| Marcato | 80–90 | 0.85× | attack override — plucked onset (machine has no pluck; rhythmic accents only) |
| Drone | 55–68 | full | static sustained harmony — ambient bed |
| Accent | 84–92 | 0.9× | hard entrance — downbeat hit, then bloom |
| Bloom | 62–74 | 1.25× | extra-long swell — the slow-strings signature tail (feeds verb) |

## Timbre DNA

- **Harmonic content**: dense saw-derived stack (3 detuned sub-oscillators
  per note at 8'/4'/2' octaves — the divide-down architecture); strong
  fundamental + full mid harmonics, band-limited top (the filter rolls the
  saw hiss off)
- **Attack**: 0.5–1.0 s slow swell — THE identity (the patch is literally
  named "Slow Strings"); never expect a pluck
- **Decay/sustain**: continuous while the key is down — sustain pedal on,
  no natural decay; release = the machine blooms 1–1.5 s into the reverb
- **Vibrato/chorus**: the ensemble chorus (3 modulated delay taps,
  Streichfett/Solina style) — wide animated shimmer, NOT solo vibrato
- **Character**: warm, swelled, slightly nasal (saw) with a slow bloom;
  the 70s string-machine bed (Solina/Mellotron/Elka/Crumar/RS-202)

## Role in Arrangement

- **Pad** (primary) — slow-attack sustained chords; the 70s/80s ballad,
  lofi, synthwave, ambient bed
- Harmony — sustained chords under a lead (the machine comping voice;
  dense 4–6 note voicings are idiomatic — divide-down machines love fat
  chords)
- Texture — slow-blooming washes, whole-bar swells under sparse leads
- Melody / countermelody — high register (72–96) cuts warm but distinct
  from the bowed section (no bow attack, chorus sheen)
- Accent — marcato/accent entrances only (the slow attack smears fast
  rhythm)
- NOT a bass voice — the divide-down low register is rumble (roots at C3+
  in dense writing; pair with a real bass below)
- NOT a rhythm voice — the 0.8 s attack blurs 16ths; staccato "blips" at
  1/4 are the fastest idiomatic gesture

## Synthesis Engines (musicom)

1. **StringEnsembleVoice** (`sound/synthesis/string_ensemble.py`) —
   **primary**. The dedicated divide-down string-machine model: per note, N
   detuned saw sub-oscillators at 8'/4'/2' octave mix, slow random-walk
   drift (the ensemble "swell"), A/R envelope, and a Streichfett-style
   3-tap ensemble chorus. Use `STRING_ENSEMBLE_DEFAULTS` (n_voices 3,
   octave_mix (0.6, 0.35, 0.15), detune_cents 8, attack_s 0.8 — the slow
   swell, release_s 1.5, layer_mix 0.2, flavour 0.35).
2. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — **secondary**.
   The classic subtractive string machine: 3 detuned SAWS through a
   band-limiting low-pass. `POLYSYNTH_DEFAULTS` (3 saws ±8c, cutoff 2200 Hz
   — between warm_pad 1400 and synth_brass_1 2800, resonance 0.3, env
   attack 0.8/sustain 0.85/release 0.8).
3. **Additive** (`sound/synthesis/additive.py`, SoundWave) — **tertiary**
   pad fallback. `ADDITIVE_HARMONICS["slow_strings"]` [1.0, 0.85, 0.62,
   0.42, 0.28, 0.18, 0.11] — saw-ish stack, brighter than warm_pad's
   rolloff; `SYNTHESIS_DEFAULTS` attack 0.8, detune ±0.010, stack 3,
   **decay_S 1e-4** (the pad-hold recipe — 0.005 collapses the chord).
4. **PhaseModSynth** — the cheap FM string machine alt (saw carrier, ratio
   1.0, depth 1.8 — the string_ensemble FM recipe).

## Production

- **Reverb**: hall 2.6–3.0 s — REVERB_TAIL 2.8 s (between string_ensemble
  2.6 and warm_pad 3.0): the machine blooms in a hall but keeps more body
  than the new-age shimmer
- **EQ**: cut ~300 Hz (the saw stack + octave mix piles the low-mid fast);
  boost ~2.8 kHz (ensemble clarity / chorus edge — the machine speaks in
  the upper-mid, not the 3.8 kHz new-age shimmer); gentle 8 kHz shelf air
- **Pan**: center for the composed stem; ±0.4 L/R spread on wide stereo
  swells (the ensemble chorus widens in production; the Solina's ensemble
  output is already stereo)
- **Layering**: the idiomatic doubling is octaves or a low sustained bass
  BELOW — NEVER unison with another melodic patch on the same pitches
  (2026-09-01 comb-filter rule; a slow-strings pad + unison bowed strings
  is a beating wash). It layers beautifully UNDER a lead as a harmony bed.

## Verification

- GM49 → stem `trackXX_String_Ensemble_2.wav` (label matches, no quirk)
- FluidR3 preset 49 = "Slow Strings" (verified from phdr chunk; SF2 uses
  the character name, cosmetic only)
- Empirical pitch sweep: 9/9 notes audible 12–96, silent at 108+ —
  full-keyboard patch, never clips a composition
- Buzz check: solo render passes the 4–8 kHz spectral gate (≤20%) — no
  comb-filtering (single voice)
- Zero-drift: sustained units end flush at BAR (terminal landmark)
- Engine test: StringEnsembleVoice + polysynth smoke renders sustain
  (slow swell, no collapse)

## Stem label / quirks

- GM_PROGRAMS[49] = "String Ensemble 2" → stem `String_Ensemble_2` — exact
  match, **no quirk**
- FluidR3 preset 49 = "Slow Strings" vs pipeline "String Ensemble 2" —
  cosmetic only, no routing impact
- `MidiInstrument.STRING_ENSEMBLE = 49` — the legacy enum's value equals
  GM49 (Slow Strings), NOT GM48; the registry (GM48 string_ensemble /
  GM49 string_ensemble_2) is the truth
- Channel quirk: melodic channel (0–9) with program 49 — channel 9 would
  trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0
  fallback label (timpani lesson)
