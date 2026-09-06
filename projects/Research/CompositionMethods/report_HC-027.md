# Report — HC-027: Tuvan Overtone Throat Singing (Khöömei / Sygyt / Kargyraa — One-Body Drone + Harmonic-Series Melody)

- **Method ID:** HC-027
- **Tradition:** Tuvan (Tyva) & Mongolian throat singing — Inner Asian steppe pastoral nomad culture (Tuva, Siberia; Mongolia; Altai), centuries-old oral animist craft; UNESCO Representative List of the Intangible Cultural Heritage of Humanity (2009).
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix. Human methods carry the tag `human (→concrete)`.
- **Primary Elements:** PITCH, TEXTURE, STRUCTURE, RHYTHM (harmony incidental — the vertical sonority is the harmonic series itself, never functional chords).
- **Detail file:** `human_method_HC-027_tuvan-overtone-throat-singing.md`
- **Next free ID:** HC-028

---

## Rationale for selection

Rotation check — the DB has **no Inner-Asian vocal / overtone entry** and no
single-body drone + harmonic-series method. Nearest neighbours are HC-003
makam (microtonal monophony), HC-013 Georgian vocal polyphony (drone +
contrasted parts), HC-023 spectral listening (Western instrumental
orchestration of spectra), HC-026 pibroch (drone + ornamented theme). None of
these is a **single performer producing drone and melody simultaneously from
one sound source via resonant filtering of the harmonic series**. This fills a
genuine gap: the "hidden invariant spine + constrained melodic layer" family
(HC-002/005/014/025/026) has been realized by *ensembles* or *instruments*,
never by one human throat where the constraint is **physical law** (only
integer multiples of the drone frequency are producible), not style.

## What the human actually does

A throat singer produces two pitches at once from a single body: a low held
**fundamental** (drone, `khorekteer` chest voice) and a higher moving **overtone
melody** formed by isolating individual harmonic partials of that fundamental.
The drone and the melody are one breath, separated by resonant filtering in the
mouth (lips, tongue, jaw, throat = a continuously tunable band-pass filter).

## The three base styles (one mechanism, three registral characters)

| Style | Fundamental register | Melody character | Mechanism |
|---|---|---|---|
| **Khöömei** | low-mid to midrange, soft | 2–3 harmonics, 1–2 octaves up, gentle | relaxed abdomen, low larynx tension; vowel shaping selects partials |
| **Sygyt** | midrange | strong flute-like/piercing high partials (6th–13th) | tongue seals behind teeth, small molar opening; bell-shaped lips ("ee") |
| **Kargyraa** | deep | **undertone** exactly ½ the vocal-fold frequency | vestibular folds ("false cords") adduct & vibrate at half rate |

Sub-styles: **chylandyk** (simultaneous sygyt + kargyraa — two melodic layers at
once), **borbangnadyr** (rolling water-brook pulse), **ezengileer** (horse-trot
rhythm), **dumchuktaar** (nasal). `dag`/`xovu` kargyraa = darker vs raspier
regional timbres.

## Craft procedure (step by step)

1. **Fix the fundamental** (drone pitch, E–G below middle C). The fundamental
   fixes the entire available pitch universe for the piece.
2. **Sustain the drone unbroken** — no rests, no waver, no dynamic swell. It is
   a held invariant (the spine).
3. **Select the melody style/register** (sygyt high / khoomei mid / kargyraa
   undertone) — sets the filter band the melody lives in.
4. **Trace the melody by shaping the oral cavity** — moving the formant selects
   partial 6 → 7 → 8 → 9 → 10 → 12 → 13 in sequence (not by changing
   vocal-fold pitch).
5. **Compose against the series** — if the fundamental is C3, the melody draws
   from partial 6=G5, 7=B♭5, 8=C6, 9=D6, 10=E6, 12=G6, 13=A6. **Partial 11
   (F♯6, the tritone) is avoided** — ~49¢ flat of 12-TET, sounds out-of-tune.
6. **Walk adjacent partials for contour** — stepwise-sounding at the top of the
   series (small gaps), wide leaps at the bottom (octave/5th gaps). Contour is
   emergent from *which* partial is selected.
7. **Add rhythmic/ornamental sub-style** (borbangnadyr roll, ezengileer trot,
   chylandyk undertone layer). Ornament is layer-mask, not pitch change.
8. **Shape the arch form** — drone alone → melody emergence (low partials) →
   series climb (peak) → subsidence → drone release. The melody imitates the
   pastoral landscape (wind, river, bird calls), not a harmonic scheme.

## Practitioner examples

- **Kongar-ool Ondar** — canonical khoomei master (*Genghis Blues*, 1999); sygyt whistle precision over steady drone.
- **Huun-Huur-Tu** — Tuvan ensemble, four-voice arrangements of the single-singer technique; *Ancestors Call*.
- **Albert Kuvezin / Yat-Kha** — kargyraa undertone fused with rock; the sub-octave growl as a bass instrument.
- **Sainkho Namtchylak** — pioneering female throat singer; extended-technique overtone work.
- **Chirgilchin**, **Alash Ensemble** — contemporary keepers of khoomei/sygyt/kargyraa pedagogy.
- Mongolian **khöömii** parallel + Sardinian **canto a tenore** (`bassu` voice uses the same vestibular-fold subharmonic as kargyraa) — a shared human vocal discovery, not a single-culture artefact.

## UnitMatrix mapping

| UnitMatrix role | What fills it |
|---|---|
| **Voice 0** | Fundamental drone (`khorekteer` spine) — single held pitch, invariant for the whole piece/section. |
| **Voice 1** | Overtone melody — pitches from the harmonic series of Voice 0, selected by formant filter. |
| **Voice 2** (optional) | chylandyk / kargyraa undertone (½·f0) or sygyt counter-layer. |
| **Voice 3** (optional) | Rhythmic/ornament mask — borbangnadyr lip-roll pulse or ezengileer trot figure (onset density, no new pitches). |

**Sections** = the arch form: Drone-alone → Melody-emergence → Series-climb →
Subsidence → Drone-release. Each section is a *filter-band region* of the
harmonic series, not a new chord.

### Rules that would encode it

- **fundamental-invariance** — Voice 0 pitch constant; never restarts/transposes within a section.
- **partial-constraint** — Voice 1 pitch ∈ { n·f0 | n harmonic }.
- **partial-11-avoidance** — exclude tritone partial (n=11, −49¢).
- **microtonal-offset** — partials deviate from 12-TET: n=7 (−31¢), n=11 (−49¢), n=13 (+41¢).
- **adjacent-partial-walking** — contour by ±1 partial steps.
- **subharmonic-layer** — kargyraa/chylandyk Voice 2 = ½·f0 (only sub-harmonic source).
- **no-functional-harmony** — sonority is the series; no chords, no cadences.
- **no-rests / continuous-sound** — texture changes only via filter-band movement + ornament masks.
- **ornament-as-layer-mask** — borbangnadyr/ezengileer add density without new pitch material (cf. HC-026).
- **register↔partial-reach coupling** — lower drone ⇒ higher partials reachable; melody tessitura and drone pitch are coupled.

### Distinct from HC-023 (Spectral Listening / Orchestration)

HC-023 = Western instrumental: analyze a source spectrum, orchestrate each
partial across an ensemble (ensemble = additive synth). HC-027 = folk vocal,
single-body: the singer **is** the spectrum — one throat generates the
fundamental and the isolated partial simultaneously. Both draw pitch from the
harmonic series, but HC-023 distributes it across instruments while HC-027
realizes it inside one performer. That distinction makes HC-027 a new method,
not a duplicate.

## Quirks / pitfalls

- **Melody not freely scalable** — only integer multiples of the drone are reachable; no modulation/key-change without moving the fundamental (which singers avoid). Hard pitch-constraint, not style.
- **Partial 11 is a trap** — the tritone partial is genuinely flat; naive 12-TET encoding would include an out-of-tune note.
- **No silence** — no rests; empty UnitMatrix cells would be wrong for this method (contrast HC-020 drop architecture, all about silence).
- **Register↔partial-reach coupling** — drone pitch and melody tessitura are not independent.

## Table row added (human_methods_db.md)

| HC-027 | human (→concrete) | Tuvan Overtone Throat Singing (Khöömei / Sygyt / Kargyraa — One-Body Drone + Harmonic-Series Melody) | Tuvan (Tyva) & Mongolian throat singing — Inner Asian steppe pastoral nomad culture (Tuva, Siberia; Mongolia; Altai), centuries-old oral animist craft; UNESCO Intangible Cultural Heritage (2009) | PITCH, TEXTURE, STRUCTURE, RHYTHM | Fix the fundamental drone (khorekteer chest voice, E–G below middle C, invariant) → sustain it unbroken (no rests/dynamics) → choose melody style (khoomei soft-mid / sygyt bright-high / kargyraa undertone) → trace the overtone melody by shaping the oral cavity as a tunable band-pass filter (lips/tongue/jaw select partial 6→7→8→9→10→12→13, avoid partial 11 tritone) → walk adjacent partials for contour → add rhythmic/ornamental sub-style (borbangnadyr roll, ezengileer trot, chylandyk sygyt+kargyraa) → shape arch form (drone-alone → melody emergence → series climb → subsidence → drone release) | Voice 0 = fundamental drone (khorekteer spine, invariant, piece identity). Voice 1 = overtone melody (partials of Voice 0, formant-selected). Voice 2 = optional chylandyk/kargyraa undertone (½·f0 subharmonic layer). Voice 3 = rhythmic/ornament mask (borbangnadyr/ezengileer onset density, no new pitches). Sections = arch form (Drone-alone → Emergence → Climb → Subsidence → Release). Rules: fundamental-invariance, partial-constraint (pitch ∈ n·f0), partial-11-avoidance (tritone −49¢), microtonal-offset (n=7 −31¢, n=13 +41¢), adjacent-partial-walking, subharmonic-layer (½·f0), no-functional-harmony (sonority = series), no-rests/continuous-sound, ornament-as-layer-mask, register↔partial-reach coupling | Kongar-ool Ondar (Genghis Blues 1999), Huun-Huur-Tu, Albert Kuvezin / Yat-Kha (kargyraa rock), Sainkho Namtchylak, Chirgilchin, Alash Ensemble; Mongolian khöömii parallel + Sardinian canto a tenore bassu (same vestibular-fold subharmonic) | ✅ Documented |

## Verification

- `HC-027` present in detail file `human_method_HC-027_tuvan-overtone-throat-singing.md` ✅
- `HC-027` present in `human_methods_db.md` framework table (exactly 1 row) ✅
- No duplicate HC-027 rows ✅
- Highest existing ID confirmed HC-026 before write; new ID = 027 (max+1) ✅
- **Next free ID: HC-028**
