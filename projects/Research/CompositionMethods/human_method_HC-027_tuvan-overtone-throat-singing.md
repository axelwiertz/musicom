# Human Method HC-027 — Tuvan Overtone Throat Singing (Khöömei / Sygyt / Kargyraa — One-Body Drone + Harmonic-Series Melody)

- **Method ID:** HC-027
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix. Human methods carry the tag `human (→concrete)`.
- **Tradition / Culture:** Tuvan (Tyva) & Mongolian throat singing — Inner Asian steppe pastoral nomad culture (Tuva, Siberia; Mongolia; Altai), centuries-old oral animist craft; UNESCO Representative List of the Intangible Cultural Heritage of Humanity (2009).
- **Primary Elements:** PITCH, TEXTURE, STRUCTURE, RHYTHM (harmony is *incidental* — the vertical sonority is the harmonic series itself, never functional chords).

---

## 1. What the human actually does

A throat singer produces **two pitches at once from a single body**: a low, held
**fundamental** (the drone, `khorekteer` "chest voice") and a higher, moving
**overtone melody** formed by isolating individual **harmonic partials** of that
fundamental. There is no second instrument and no second performer — the drone
and the melody are one breath, separated by resonant filtering in the mouth.

This is the purest human realization of the principle the engine's "hidden
spine" already encodes (cf. HC-002 gamelan pokok, HC-005 Ewe timeline, HC-026
pibroch drone): **an invariant low reference that is always present but is not
the melody, and a melodic layer that is strictly constrained by that
reference.** Here the constraint is physical, not stylistic: the melody may
only take pitches that are **integer multiples of the drone's frequency**.

## 2. The three base styles (one mechanism, three registral characters)

| Style | Fundamental register | Melody character | Mechanism |
|---|---|---|---|
| **Khöömei** (хөөмей, "throat") | low-mid to midrange, soft | 2–3 harmonics, 1–2 octaves above, gentle | relaxed abdomen, low larynx tension; lips/tongue/jaw shape vowels to select partials |
| **Sygyt** (сыгыт, "whistling") | midrange | strong flute-like/piercing high partials (6th–13th) | tongue seals behind teeth, small opening near molars; sound directed through bell-shaped lips ("ee" vowel) |
| **Kargyraa** (каргыраа, growl) | deep | **undertone** exactly ½ the vocal-fold frequency | vestibular folds ("false cords") adduct and vibrate at half rate, adding a sub-octave — the only *subharmonic* style |

Sub-styles combine the base types: **chylandyk** = simultaneous sygyt + kargyraa
(high whistle melody *and* low undertone at once — literally two melodic layers
from one throat); **borbangnadyr** (rolling, water-brook effect), **ezengileer**
(horse-stirrup trot rhythm), **dumchuktaar** (nasal humming). `dag` (mountain)
vs `xovu` (steppe) kargyraa describe darker vs raspier regional timbres.

## 3. Craft procedure (how a singer composes a piece, step by step)

1. **Fix the fundamental.** Choose the drone pitch (typically E–G below middle
   C). Lower fundamentals make high partials easier to reach; the chosen
   fundamental fixes the entire available pitch universe for the piece.
2. **Sustain the drone.** Establish continuous `khorekteer` chest resonance —
   the drone must not stop, waver, or change pitch. There are no rests and no
   dynamic swell; the drone is a held invariant (the "spine").
3. **Select the melody register/style.** Choose sygyt (bright, high) or khoomei
   (soft, mid) or kargyraa (undertone). This sets the *filter band* the melody
   will live in.
4. **Trace a melody by shaping the oral cavity.** The lips, tongue, jaw, and
   throat act as a **continuously tunable band-pass filter** over the drone's
   harmonic series. Moving the formant selects partial 6 → 7 → 8 → 9 → 10 →
   12 → 13 in sequence. The singer "sings" by walking this filter, not by
   changing vocal-fold pitch.
5. **Compose against the series.** The available melodic scale is the partial
   ladder above the fundamental. If the fundamental is C3, the melody draws from
   partial 6=G5, 7=B♭5, 8=C6, 9=D6, 10=E6, 12=G6, 13=A6. **Partial 11 (F♯6,
   the tritone) is avoided** — it is ~49 cents flat of 12-TET and sounds
   out-of-tune to the ear (the "wolf" of the series).
6. **Walk adjacent partials for contour.** Moving between *neighbouring*
   partials produces stepwise-*sounding* motion at the top of the series (small
   frequency gaps) but wide leaps at the bottom (octave/5th gaps). Melodic
   contour is therefore an emergent property of *which* partial is selected, not
   of an independent scale.
7. **Add rhythmic/ornamental sub-style.** Apply borbangnadyr (rolling pulse
   from lip flutter), ezengileer (trot rhythm imitating a horse stirrup), or
   chylandyk (add the undertone layer) for texture and rhythm. Ornament is
   layer-mask, not pitch change — the drone never moves.
8. **Shape the form as an arch.** A typical performance arches: drone enters
   alone → overtone melody emerges slowly from low partials → climbs the series
   to a peak → subsides back toward the fundamental → drone releases. The
   macro-form mirrors the pastoral environment the craft grew from (wind over
   steppe, river, bird calls) — the melody *imitates landscape*, not a harmonic
   scheme.

## 4. Practitioner examples

- **Kongar-ool Ondar** — canonical khoomei master (brought Tuva global attention
  via the film *Genghis Blues*, 1999); sygyt whistle precision over a steady
  drone.
- **Huun-Huur-Tu** — Tuvan ensemble, four-voice arrangements of the single-singer
  technique (each member takes a register); *Ancestors Call*.
- **Albert Kuvezin / Yat-Kha** — kargyraa undertone fused with rock; the growl
  sub-octave as a bass instrument.
- **Sainkho Namtchylak** — pioneering female throat singer (technique was
  historically discouraged for women); extended-technique overtone work.
- **Chirgilchin**, **Alash Ensemble** — contemporary keepers of khoomei/sygyt/
  kargyraa pedagogy.
- Mongolian parallel tradition (**khöömii**) and Sardinian **canto a tenore**
  (the `bassu` voice uses the same vestibular-fold subharmonic mechanism as
  kargyraa) — evidence the mechanism is a shared human vocal discovery, not a
  single-culture artefact.

## 5. UnitMatrix mapping

| UnitMatrix role | What fills it |
|---|---|
| **Voice 0** | Fundamental drone (the `khorekteer` spine). A single held pitch, invariant for the whole piece/section. |
| **Voice 1** | Overtone melody — pitches drawn from the harmonic series of Voice 0, selected by formant filter. |
| **Voice 2** (optional) | Second melodic layer via chylandyk (kargyraa undertone = ½ fundamental) or a sygyt counter-layer. |
| **Voice 3** (optional) | Rhythmic/ornamental mask — borbangnadyr lip-roll pulse or ezengileer trot figure (adds onset density without new pitches). |

**Sections** = the arch form: Drone-alone → Melody-emergence (low partials) →
Series-climb (peak) → Subsidence (return down the series) → Drone-release.
Each section is a *filter-band region* of the harmonic series, not a new chord.

### Rules that would encode it

- **fundamental-invariance** — Voice 0 pitch constant; never restarts, never transposes within a section.
- **partial-constraint** — Voice 1 pitch ∈ { n·f0 | n ∈ harmonic series }; quantize to 12-TET or just-intonation grid.
- **partial-11-avoidance** — exclude the tritone partial (n=11, −49¢) from the melody set.
- **microtonal-offset** — partials deviate from 12-TET: n=7 (−31¢), n=11 (−49¢), n=13 (+41¢); keep these when just-intonation grid is active.
- **adjacent-partial-walking** — contour built by ±1 partial steps (stepwise-sounding at top, leaping at bottom of series).
- **subharmonic-layer** — kargyraa/chylandyk Voice 2 = ½·f0 (undertone), the only sub-harmonic source.
- **no-functional-harmony** — vertical sonority is the series itself; no chord changes, no cadences.
- **no-rests / continuous-sound** — drone and melody are unbroken; texture changes only via filter-band movement and ornament masks.
- **ornament-as-layer-mask** — borbangnadyr/ezengileer add rhythmic density without changing pitch material (same principle as HC-026 pibroch ornamentation).

### Distinct from HC-023 (Spectral Listening / Orchestration)

HC-023 is Western-Classical, *instrumental*: analyze a source sound's spectrum,
then orchestrate each partial across an ensemble (ensemble = additive synth).
HC-027 is folk-vocal, *single-body*: the singer **is** the spectrum — one throat
generates the fundamental and the isolated partial simultaneously. Both draw
pitch from the harmonic series, but HC-023 distributes the series across many
instruments while HC-027 realizes it inside one performer. That distinction is
the reason HC-027 is a new method, not a duplicate.

## 6. Quirks / pitfalls

- **The melody is not freely scalable.** Only integer multiples of the drone are
  reachable; you cannot modulate or change key without moving the fundamental
  (which singers avoid — the drone is fixed for a whole piece). This is a hard
  pitch-constraint, not a style preference.
- **Partial 11 is a trap.** The tritone partial is genuinely flat; naive
  equal-temperament encoding of "any partial" would include an out-of-tune note.
- **No silence.** There are no rests — empty cells in the UnitMatrix would be
  wrong for this method (contrast HC-020 drop architecture, which is all about
  silence).
- **Register↔partial reach coupling.** Lower fundamental ⇒ higher partials
  easier; higher fundamental ⇒ only lower partials reachable. Melody tessitura
  and drone pitch are coupled, not independent.

## Verification

- `HC-027` present in this detail file ✅
- `HC-027` present in `human_methods_db.md` framework table (exactly 1 row) ✅
- No duplicate HC-027 rows ✅
- Highest existing ID confirmed HC-026 before write; new ID = 027 (max+1) ✅
- **Next free ID: HC-028**
