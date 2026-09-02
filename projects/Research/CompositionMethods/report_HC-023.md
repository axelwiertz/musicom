# Report — HC-023: Spectral Listening & Harmonic-Series Orchestration

- **Method ID:** HC-023
- **Method Name:** Spectral Listening & Harmonic-Series Orchestration (Spectrum-to-Orchestra Transcription)
- **Tradition / Culture:** Western Classical — French spectral school (Ensemble l'Itinéraire, IRCAM, Paris) and its precursors, ~1960s–present
- **Date researched:** 2026-09-01 (nightly `daily-human-composition-research` job)
- **Status:** ✅ Documented

---

## 1. Method overview

Spectral composition is a **human craft of listening**. The composer takes one real,
analyzable sound — a low trombone note, a bell, a boy's voice, a breath — and treats its
internal life (overtone spectrum, noise content, attack–sustain–decay envelope) as the
*entire* model for a piece. The sound is not a theme to vary; it is a structure to unfold.

Core chain of acts:

> **listen → analyze the spectrum → transcribe partials as pitches → rebuild the timbre
> acoustically (additive synthesis by ensemble) → shape time after the sound's envelope.**

Tristan Murail: spectralism is "not a style but an attitude." Gérard Grisey: "it is not a
closed technique but an attitude" — the "renovation, without imitation, of the foundations
of occidental music." Joshua Fineberg's gloss: "music is ultimately sound evolving in time."

This is squarely **human-side craft** (listening, transcribing, orchestrating), NOT an
algorithm. The *algorithmic* spectral twin lives elsewhere in the engine (Method 039 SMA,
"spectral peaks drive pitch…"): HC-023 documents the *human* procedure; 039 is the *engine*
procedure. This report keeps them distinct.

## 2. Craft procedure (how a human does it)

1. **Choose a source sound (the "model").** A concrete, analyzable timbre rich enough that
   its spectrum yields material. Grisey chose a low E2 trombone note for *Partiels*;
   Jonathan Harvey chose the Winchester Cathedral bell + a boy's singing voice for
   *Mortuos Plango, Vivos Voco*.

2. **Analyze the spectrum.** By sonogram/FFT (the IRCAM way) *or* by sustained listening
   (Scelsi's way — he improvised on a single note for hours and simply *heard* its overtone
   activity). Output: a list of partials, each with frequency, amplitude, and its own
   time-envelope. Note which partials are **harmonic** (integer multiples of f0) vs
   **inharmonic** (bell/plate/stiff-string).

3. **Translate frequencies → pitches.** Harmonic partials map to the harmonic series
   (octave, 12th, 15th, 17th…). Choose a quantization grid: round to 12-TET (loses the
   "beats") *or* retain natural microtones / just intonation for partials 7, 11, 13.

4. **Derive the pitch/harmony world from the partials.** The spectrum *is* the chord, the
   mode, the scale. Vertical harmony = simultaneous partials (a "spectral chord" is a frozen
   timbre). Horizontal melody = movement *through* the series. No separate
   melody-and-accompaniment — the whole piece is one timbre unfolding.

5. **Orchestrate additively.** Assign each partial to one or more instruments (flute = one
   sine-like partial, trombone = fundamental + its own partials, strings sul ponticello =
   high shimmer). The ensemble becomes a giant additive synthesizer.

6. **Imitate non-harmonic processes with instruments.** Ring modulation (sum/difference
   tones), FM (sidebands), AM (tremolo/beats) — realized as *notated instrumental
   approximations*: trills, flutter-tonguing, tremolo, beating between two close pitches,
   multiphonics.

7. **Shape macro-form after the life of a sound.** Attack → sustain → decay → noise becomes
   the piece's large form. Grisey's "liminal" writing sits at the threshold of perception.

8. **Let timbre be the structure.** Sections are delimited not by theme or key but by a
   change of spectral model: harmonic → slightly inharmonic → fully inharmonic (bell) →
   noise/breath → return.

9. **Treat instrumentation + extended technique as the score.** Microtonal notation,
   scordatura, overpressure, air/breath sounds, multiphonics — these physically produce the
   required partials/noise.

10. **Listen and re-balance.** Check the composite reads as one living sound, not a pile of
    notes; adjust per-partial amplitudes (loudness ≈ ∝ 1/n) and registers.

## 3. Practitioner examples

- **Giacinto Scelsi** — *Quattro Pezzi su una nota sola* (1959): each movement on a single
  pitch, explored through microtonal deviation, trills, orchestration. Improvised at
  piano/ondiola; assistant Vieri Tosatti transcribed/orchestrated the *listening*. Direct
  influence on Grisey & Murail.
- **Gérard Grisey** — *Les Espaces Acoustiques* (*Périodes*, *Partiels*, 1975): orchestration
  of the spectrum of a low trombone E2; proceeds harmonic → inharmonic → noise → back.
- **Tristan Murail** — *Gondwana* (1980), *Désintégrations* (1982), *Mémoire/Érosion* (1976):
  computer-assisted spectral analysis drives orchestration; ring-mod/FM timbres recreated by
  instruments.
- **Jonathan Harvey** — *Mortuos Plango, Vivos Voco* (1980): bell spectrum + boy's voice,
  tape + live ensemble.
- **Kaija Saariaho** — post-spectral: cello-timbre analysis → *Lichtbogen*, *Amers*.
- **James Tenney** — *Clang* (1972), *Quintext* (1972): computer-analyzed tam-tam/inharmonic
  spectra. **La Monte Young** — *The Well-Tuned Piano*: just intonation from the harmonic
  series.

## 4. UnitMatrix integration (Musicom engine)

**Voices (additive-synthesis reconstruction of ONE spectrum):**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Fundamental spine | Source fundamental held invariant (trombone E2 in *Partiels*; Scelsi's single note). Drone anchor. | PITCH (anchor) |
| V1 | Low harmonic partials | Partials 2, 3, 4 (octave, 12th, 15th) — body of the timbre. | HARMONY |
| V2 | Mid/high partials + microtones | Partials 5, 7, 11, 13 + just-intonation/quarter-tone deviations; string harmonics, flutes. | PITCH + TEXTURE |
| V3 | Inharmonic / noise layer | Air, breath, bow noise, flutter, percussive transients, multiphonics. | TEXTURE |
| V4 | Modulation layer | Trills/tremolo/beats/difference-tones = instrumental ring-mod & FM sidebands. | RHYTHM + TEXTURE |

**Sections = spectral states (envelope of one sound over macro-time):**

```
S0 Harmonic (periodic) → S1 slight inharmonicity → S2 bell-like full inharmonicity
   → S3 noise/breath decay → (optional) S4 return to harmonic
```

**Rules that encode the craft (deterministic, human-authored):**

- `partial-frequency`: harmonic → `f_n = n·f0`; inharmonic → bell/plate/stiff-string formula.
- `quantization grid`: 12-TET (round) *or* just-intonation/microtonal (keep 7, 11, 13).
- `amplitude-from-spectrum`: per-partial loudness follows analysis (≈1/n falloff default).
- `additive-assignment`: each partial → ≥1 instrument; never sound a pitch *not* in the model.
- `envelope-as-form`: global contour mirrors the source sound's attack–sustain–decay.
- `inharmonicity-progression`: harmonic → inharmonic → noise monotonic across sections.
- `fundamental-invariance`: V0 never changes pitch.
- `timbre-as-structure`: section boundary = spectral-model change (no theme/key markers).
- `modulation-approximation`: sideband effects realized as trill/tremolo/beat, never as added
  unrelated notes.

## 5. Table row added

```
| HC-023 | Spectral Listening & Harmonic-Series Orchestration (Spectrum-to-Orchestra Transcription) | Western Classical — French spectral school (Ensemble l'Itinéraire / IRCAM, Paris) & precursors Scelsi→Grisey→Murail→Saariaho, ~1960s–present | PITCH, TEXTURE, HARMONY, STRUCTURE, RHYTHM | Choose a concrete source sound (low trombone E, bell, boy's voice, breath) → analyze its spectrum (FFT/sonogram OR sustained listening à la Scelsi) → translate partial frequencies to pitches (harmonic = integer series; inharmonic = bell/stiff-string, microtonal) → derive entire pitch/harmony world from partials (spectral chord = frozen timbre, no separate melody) → orchestrate additively (each partial → ≥1 instrument; ensemble = additive synth) → imitate non-harmonic processes with instruments (trills/tremolo/beats/multiphonics = ring-mod & FM sidebands) → shape macro-form after the sound's envelope (attack→sustain→decay→noise) → let timbre BE the structure (section change = spectral-model change) | Voice 0 = fundamental spine (source fundamental held invariant, drone). Voice 1 = low harmonic partials (octave/12th/15th = body). Voice 2 = mid/high partials + microtones (partials 5/7/11/13, string harmonics, shimmer). Voice 3 = inharmonic/noise layer (air/breath/bow noise/multiphonics). Voice 4 = modulation layer (trill/tremolo/beats = instrumental sidebands). Sections = spectral states (Harmonic→Slight inharmonic→Bell-like→Noise/decay→Return). Rules: partial-frequency (harmonic n·f0 / inharmonic formula), quantization grid (12-TET round or just-intonation), amplitude-from-spectrum (≈1/n falloff), additive-assignment (only model-spectrum pitches sound), envelope-as-form, inharmonicity-progression monotonic, fundamental-invariance, timbre-as-structure | Giacinto Scelsi (Quattro Pezzi su una nota sola 1959), Gérard Grisey (Partiels/Les Espaces Acoustiques 1975), Tristan Murail (Gondwana 1980, Désintégrations 1982), Jonathan Harvey (Mortuos Plango Vivos Voco 1980), Kaija Saariaho (Lichtbogen), James Tenney (Clang/Quintext 1972) | ✅ Documented |
```

## 6. Next free ID

**HC-024**

## 7. Quirks / pitfalls

- **Quantization kills the "beats".** Rounding partials 7/11/13 to 12-TET erases the
  beating/difference tones that give the timbre life. Keep a microtonal grid or accept beats
  as texture.
- **Additive synthesis, not counterpoint.** No species/motivic rules — "voice leading" here is
  partial-to-partial amplitude balance; a wrong partial is a wrong *frequency*, not a clash.
- **One-sound discipline.** Pitch material outside the model spectrum breaks the reconstruction.
- **Liminal perception.** Grisey's gradual changes read as "nothing happening" if paced wrong;
  change must be perceptible-but-slow.
- **Scope note:** kept distinct from algorithmic Method 039 SMA (engine-side spectral
  analysis); HC-023 is the human craft, 039 is the machine procedure.
