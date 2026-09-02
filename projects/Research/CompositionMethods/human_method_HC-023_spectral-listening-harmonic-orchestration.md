# HC-023 — Spectral Listening & Harmonic-Series Orchestration (Spectrum-to-Orchestra Transcription)

- **Tradition / Culture:** Western Classical — French spectral school (Ensemble l'Itinéraire, IRCAM, Paris) and its precursors, ~1960s–present. Rooted in Giacinto Scelsi's single-note meditation, continuing through Gérard Grisey, Tristan Murail, and the post-spectralists (Kaija Saariaho, Jonathan Harvey, Georg Friedrich Haas).
- **Primary Elements:** PITCH, TEXTURE, HARMONY, STRUCTURE, RHYTHM
- **Status:** ✅ Documented

## What it is

Spectral composition is a **human craft of listening**: the composer takes a single real
sound — a trombone's low note, a bell, a boy's voice, a breath — and treats its internal
life (its overtone spectrum, its noise content, its attack–sustain–decay envelope) as the
entire model for a piece. The sound is not a *theme* to vary; it is a *structure to unfold*.

The craft has nothing to do with serial procedures or key centres. It is a chain of
perceptual/technical acts:

> **listen → analyze the spectrum → transcribe partials as pitches → rebuild the timbre
> acoustically (additive synthesis by ensemble) → shape time after the sound's envelope.**

Murail called spectralism "not a style but an attitude" — *music is sound evolving in time*.
Grisey: "The spectral adventure has allowed the renovation, without imitation, of the
foundations of occidental music, because it is not a closed technique but an attitude."

## How a human actually does it — craft steps

1. **Choose a source sound (the "model").** A concrete, analyzable timbre: a low trombone
   E, a bell, a tam-tam, a vowel sung by a boy, bow noise. The model must be *rich* enough
   that its spectrum yields material. Grisey chose a low E2 trombone note for *Partiels*;
   Jonathan Harvey chose the great bell of Winchester Cathedral plus a boy's singing voice
   for *Mortuos Plango, Vivos Voco*.

2. **Analyze the spectrum.** By sonogram/FFT (the IRCAM way) *or* by sustained listening
   (Scelsi's way — he improvised on a single note for hours and simply *heard* its overtone
   activity). Output: a list of partials, each with frequency, amplitude, and its own
   time-envelope (how fast it attacks, sustains, decays). Crucially, note which partials are
   **harmonic** (integer multiples of the fundamental) and which are **inharmonic**
   (bell/plate/string-stiffness partials that don't fit the integer series).

3. **Translate frequencies → pitches.** Harmonic partials map to the harmonic series
   (octave, 12th, 15th, 17th…). The composer decides the quantization grid: round to
   nearest tempered semitone (loses "beats") *or* retain the natural microtones / just
   intonation (quarter-tones, sixth-tones) for partials 7, 11, 13 that don't fit 12-TET.
   Inharmonic partials stay as non-tempered pitches — they *are* the harmony's character.

4. **Derive the pitch/harmony world from the partials.** The spectrum *is* the chord, the
   mode, the scale. Vertical harmony = simultaneous partials (a "spectral chord" is just
   a frozen timbre). Horizontal melody = movement *through* the series (a glissando up the
   partials = the sound "opening up"). There is no separate melody-and-accompaniment — the
   whole piece is one timbre unfolding.

5. **Orchestrate additively.** Rebuild the analyzed timbre acoustically: assign each
   partial to one or more instruments (a flute = one sine-like partial, a trombone = the
   fundamental + its own few partials, strings sul ponticello = high shimmer partials).
   The ensemble becomes a giant additive synthesizer. *Partiels* opens with a trombone's
   low E, and the rest of the ensemble enters instrument-by-instrument playing the higher
   partials of that very E.

6. **Imitate non-harmonic processes with instruments.** Ring modulation (sum/difference
   tones), frequency modulation (sidebands), amplitude modulation (tremolo/beats) are not
   done electronically here — the composer *notates instrumental approximations*: trills,
   flutter-tonguing, tremolo, beating between two close pitches (difference tone),
   multiphonics. These recreate the spectral sidebands of the source.

7. **Shape macro-form after the life of a sound.** A sound has an envelope: attack →
   sustain → decay → noise. The piece's large form mirrors this: it may start with a sharp
   percussive attack, sustain a rich steady state, then thin out into breath/noise. Grisey's
   "liminal" writing sits at the threshold of perception — change is so gradual you notice
   it only after it has happened.

8. **Let timbre be the structure.** Sections are not delimited by theme or key but by a
   *change of spectral model*: harmonic (periodic) → slightly inharmonic → fully inharmonic
   (bell) → noise/breath → return. Harmony, melody, and form all collapse into a single
   dimension: timbre evolving over time.

9. **Treat instrumentation + extended technique as the score.** Microtonal notation,
   scordatura (retuned strings to hit specific partials), overpressure, air/breath sounds,
   multiphonics — these are not decoration; they are how the required partials and noise
   content are physically produced.

10. **Listen and re-balance.** The composer checks the *composite*: does the ensemble, heard
    as a whole, read as one living, breathing sound rather than a pile of notes? Adjust
    amplitudes per partial (loudness usually falls with partial number, roughly ∝ 1/n) and
    registers until the reconstruction is convincing.

## Real practitioner examples

- **Giacinto Scelsi** — *Quattro Pezzi su una nota sola* (1959): each movement built on a
  single pitch, explored through microtonal deviation, trills, and orchestration. Scelsi
  improvised at the piano/ondiola while assistant Vieri Tosatti transcribed and orchestrated
  the *listening* — the purest form of the craft. Massive influence on Grisey & Murail.
- **Gérard Grisey** — *Les Espaces Acoustiques* (*Périodes*, *Partiels*, 1975): the whole
  cycle is an orchestration of the spectrum of a low trombone E2. *Partiels* proceeds from
  harmonic (periodic) timbre toward inharmonicity and noise, then back — the "life of a
  sound" as form.
- **Tristan Murail** — *Gondwana* (1980), *Désintégrations* (1982), *Mémoire/Érosion* (1976):
  computer-assisted spectral analysis drives orchestration; ring-modulation and FM timbres
  recreated by instruments.
- **Jonathan Harvey** — *Mortuos Plango, Vivos Voco* (1980): spectrum of the Winchester
  Cathedral bell + his son's singing voice, realized for tape + live ensemble.
- **Kaija Saariaho** — post-spectral: spectral analysis of cello timbre → *Lichtbogen*,
  *Amers*; timbre-as-harmony carried into orchestral writing.
- **James Tenney** — *Clang* (1972), *Quintext* (1972): computer-analyzed tam-tam/inharmonic
  spectra. **La Monte Young** — *The Well-Tuned Piano*: just intonation derived from the
  harmonic series, sustained-drone spectral listening.

## UnitMatrix integration (Musicom engine)

**Voices (additive-synthesis reconstruction of ONE spectrum):**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Fundamental spine | The source sound's fundamental, held invariant (trombone E2 in *Partiels*; Scelsi's single note). Drone/tonic anchor. | PITCH (anchor) |
| V1 | Low harmonic partials | Instruments doubling partials 2, 3, 4 (octave, 12th, 15th) — the body of the timbre. | HARMONY |
| V2 | Mid/high partials + microtones | Partials 5, 7, 11, 13 and their just-intonation / quarter-tone deviations; string harmonics, flutes. The "shimmer". | PITCH + TEXTURE |
| V3 | Inharmonic / noise layer | Air, breath, bow noise, flutter, percussive transients, multiphonics — the non-periodic content. | TEXTURE |
| V4 | Modulation layer | Trills/tremolo/beats/difference-tones = instrumental ring-mod & FM sideband imitation. | RHYTHM + TEXTURE |

**Sections = spectral states (the envelope of one sound over macro-time):**

```
S0 Harmonic (periodic spectrum) → S1 slight inharmonicity → S2 bell-like full
   inharmonicity → S3 noise/breath decay → (optional) S4 return to harmonic
```

**Rules that encode the craft (deterministic, human-authored):**

- `partial-frequency`: harmonic → `f_n = n·f0`; inharmonic → bell/plate/stiff-string formula.
- `quantization grid`: choose 12-TET (round) *or* just-intonation/microtonal grid (keep 7,11,13).
- `amplitude-from-spectrum`: per-partial loudness follows the analysis (≈1/n falloff default).
- `additive-assignment`: each partial → ≥1 instrument; never sound a pitch that is *not* in the model spectrum.
- `envelope-as-form`: global amplitude/register contour mirrors the source sound's attack–sustain–decay.
- `inharmonicity-progression`: harmonic → inharmonic → noise must be monotonic across sections.
- `fundamental-invariance`: V0 never changes pitch (the drone spine).
- `timbre-as-structure`: section boundary = spectral-model change (no theme/key markers).
- `modulation-approximation`: sideband effects realized as trill/tremolo/beat, never as added unrelated notes.

## Quirks / pitfalls

- **Quantization kills the "beats".** Rounding partials 7/11/13 to 12-TET erases the
  beating/difference tones that give the timbre life. Keep a microtonal grid or accept the
  beats as texture.
- **It is additive synthesis, not counterpoint.** Do NOT apply species/motivic rules —
  "voice leading" here is just partial-to-partial amplitude balance; a "wrong" partial is
  not a clash, it is a wrong *frequency*.
- **One-sound discipline.** If the composer introduces pitch material not present in the
  model spectrum, the reconstruction breaks and the piece stops reading as one sound.
- **Perception limit (liminal writing).** Grisey's gradual changes read as "nothing
  happening" to impatient ears — pace must be chosen so change is perceptible-but-slow.

## Source

Wikipedia — "Spectral music" (definition, French school, Grisey/Murail/Scelsi, Partiels,
Gondwana, notable works, techniques: harmonic series, spectral envelope, ring/FM). Retrieved
for this entry.
