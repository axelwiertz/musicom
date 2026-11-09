# HC-087 — Znamenny Chant Popevka (Kokiza) Formula Assembly (Russia)

**Method ID:** HC-087
**Layer:** `human (→concrete)` — human-craft knowledge; target layer **concrete** when realized through the UnitMatrix
**Tradition:** Russian Orthodox & Old Believer liturgical monody — *stolpovoy* znamenny chant (Kievan Rus' → Novgorod → Muscovy, 11th–17th c.; canon fixed mid-17th c., preserved by Old Believers to the present)
**Primary elements:** PITCH, STRUCTURE, RHYTHM, TEXTURE (plus TEXT as a first-class constraint)
**Detail file:** `human_method_HC-087_znamenny-popevka-formula-assembly.md`
**Report:** `report_HC-087.md`

---

## 1. Method name & tradition

**Znamenny chant composition by popevka assembly** — the medieval Russian cantor's craft of building a
liturgical chant by *selecting, ordering and splicing memorised melodic formulas* (попевки / кокизы),
all drawn from the closed inventory belonging to one of the eight **гласы** (glasy, "tones"), and
splicing them onto a fixed liturgical text so that each formula consumes exactly the right number of
syllables.

- **Name:** *знаменное пение* / *знаменный распев*, from *знамя* ("sign, banner") — the neumes; the
  signs themselves are *крюки* ("hooks"). The main redaction is *столповой распев* (stolpovoy), named
  after the *столп* — the eight-week Octoechos cycle.
- **Forces:** unison voices, unaccompanied, no instruments. Ideally "voices become one single voice";
  no pauses, no rests, no classical vocal training — natural voice, sometimes close to folk production.
- **Notation:** *stolp* notation — **adiastematic** neumatic signs that record *melodic transitions and
  expressive gradation*, not fixed pitches or durations. One sign may mean "one sound, half a step down";
  how long, from which pitch, and how far is supplied by the singer's memory of the formula.
- **Where the craft lives:** in *азбуки* (neume ABCs), **кокизники** (popevka dictionaries) and
  **фитники** (fita dictionaries) — the pedagogical corpus of the 16th–17th c.; and in the living
  oral practice of the head cantor (*головщик*) and his choir.

This is a **composition/selection procedure**, not sound production and not an algorithm: the human
composes by *choosing among named formulas he has memorised* and fitting them to a text. It is the
Eastern-Orthodox cousin of partimento schemata (HC-001) — same cognitive move (formula bank → assembly
under constraints), entirely different grammar, and text-locked rather than bass-locked.

## 2. Why this method, why now (rotation & overlap check)

- Recent IDs: HC-086 steelband (Trinidad), HC-085 danmono (Japan), HC-084 rebetiko (Greece),
  HC-083 mariachi (Mexico), HC-082 Jingju (China), HC-081 Gnawa (Morocco), HC-080 Notre-Dame organum
  (France), HC-079 musique concrète (France).
- **Russian/Ruthenian chant is absent from the DB.** Grep before writing: `znamenny|popevka|kryuki|глас`
  → 0 hits in the human table. HC-080 organum covers *Western* sacred polyphony from neumes, but by a
  different mechanism (rhythmic modes + vox principalis/organalis); znamenny is monodic, non-mensural,
  and formula-bank driven.
- Overlap check: HC-001 partimento is bass-driven schema realization with functional harmony;
  HC-009 motivic development *transforms* a motive, whereas popevka assembly *substitutes whole named
  formulas*; HC-021 species counterpoint is interval-by-interval; HC-038 sonata form is tonal drama.
  HC-087's signature is unique: **a closed, glas-bound formula dictionary + a syllable-count lock +
  deliberately cryptic "compressed" signs (фиты) that must be expanded from memory**.

## 3. The craft procedure, step by step (how the human does it)

### 3.1 Formation — build the formula memory before composing

A singer is trained inside a chant school: he learns the neume ABC (names, shapes, intervals), drills the
eight glasy until each is recognisable *by its typical turns*, and memorises the кокизник — the
dictionary of popevki with their names, contours and syllable counts. Only then may he "compose".
The 17th-c. theorist-didaskals formalised this: **Александр Мезенец**'s commission of six didaskals
fixed model redactions of the chants, and his *Извещение о согласнейших пометах* ("Notice on the most
agreeable marks") is the fullest statement of the theory.

### 3.2 Fix the liturgical slot (the "brief")

1. **Book & genre:** Обиход (daily cycle), Октоих (eight-tone cycle), Минея (fixed feasts),
   Триодь (Lent/Pascha), Ирмологий. Genre: стихира, тропарь, ирмос, кондак, величание.
2. **Глас 1–8** — the mode-tone. This is the single hardest constraint: it selects the formula bank.
   Note that *glas* is defined by its formulas, not by a scale: as A. V. Preobrazhensky put it, the
   singer identified the glas "by the presence in the melody of typical turns, found only in that glas,
   which he called *popevki*" — Russian chant theory never developed a concept of a scale (*звукоряд*)
   in the Western sense.
3. **Text:** divide into phrases (*строки*) at syntactic and cadential punctuation; count syllables per
   phrase; mark the words that traditionally carry melisma — doxological words ("Господи",
   "аллилуиа"), the doxastic *славник*, the end of a stichera.

### 3.3 Recall the formula inventory for that glas

Each glas owns a *closed* set of:

- **кокизы / попевки** — short formulas, roughly 2–6 neumes, each with a name, an incipit degree, a
  contour, a syllable count and a terminal degree. Some carry mnemonic names (колесо "wheel",
  кулизма); their identity is inseparable from the glas.
- **фиты** — long melismatic formulas written as **one composite cryptic sign**
  (*тайнозамкненность*, "secret-closed writing"). A single fita may hide 20–40 notes; the singer must
  know its **развод** (razvod, "resolution/unravelling") by heart, or read a фитник.
- **лица** (litso, "faces") — extended melodic phrases, likewise memorised whole; these are the
  formulas that most strongly announce the glas.

### 3.4 Assemble the phrase

1. **Open** with a formula that states the glas — usually one of its diagnostic лица/popevki, so the
   choir and congregation hear which tone is being sung from the first two or three neumes.
2. **Chain** middle popevki: each is chosen to (a) consume the exact remaining syllables and (b) fit the
   previous formula's terminal degree. This is the *splice* (`сцепление`) check: the terminal degree of
   formula *n* must equal, or lie within a step of, the incipit of formula *n+1*; wide leaps and
   tritone outlines are rejected.
3. **Close** with a cadential formula that lands on the glas's final (its *утверждение*), so the phrase
   is audibly finished.
4. **Stay inside the registral areas.** The chant ladder (*обиходный звукоряд*) is conceived as a stack
   of register bands — in the standard modern account four *согласия* of three steps each (простое,
   мрачное, светлое, тресветлое; the number and naming are debated in the literature). A phrase may
   climb (подъём) but must come back down; formulas are chosen partly by which band they sit in.
5. **Insert the фита at the melismatic climax** — never in mid-syntax, always on a word the tradition
   ornaments. Its razvod is looked up, not invented: this is the one place where the notation is
   deliberately unreadable at sight, preserving the authority of the oral school.

### 3.5 Fix the pitch (the "relative → absolute" repair)

Because stolp notation is adiastematic, the 17th century added a pitch-fixing apparatus:

- **~1600, Иван Шайдуров** introduces *киноварные пометы* ("cinnabar marks") — small red letters placed
  before a sign, indicating **the highest note of that sign**. This is usually called the first step
  toward simplification, an early *relative-to-absolute* annotation layer.
- By the 1660s the system of **признаки** (qualifying marks) and **пометы** (pitch letters) is codified;
  manuscripts before this are "unmarked" (*беспометные*). Modern scores print kryuki *and* a staff
  transcription side by side.

### 3.6 Perform and correct against the model

Sing beside the головщик, continuously, no rests, natural voice, "so that the sound astonishes the ear";
correct intonation and splice choice by ear against the elder's canonical *образец*. The composition is
never "finished" on paper: the manuscript plus the school's memory *is* the piece.

### 3.7 Transmit

The pupil copies the kрюковая manuscript, learns the named formulas, and only then reads new chants.
Literacy in this system means *recognising formulas*, not decoding pitches — which is why an untrained
singer cannot sight-read an unknown chant even with the book in hand.

## 4. Practitioner examples

| Cantor / figure | Date | What they did |
|---|---|---|
| **Фёдор Крестьянин** (Fyodor Krestyanin) | mid-16th c., Moscow | One of the great masters of the era of Vasily III / Ivan IV; composed stichera using both znamenny and demestvenny chant — the documented case of a named composer working inside the formula system. |
| **Савва Рогов, Иван Нос, Маркелл Безбородый, Стефан Голыш** | 16th c. | The generation of masters whose redactions define the classic stolpovoy repertoire. |
| **Фаддей Субботин** (Usolsk school) | mid-17th c. | Worked on Patriarch Nikon's commission for the reform of church singing; representative of the regional school that fed the codification. |
| **Александр Мезенец** (didaskal) | 1657–1668 | Head of the commission of six didaskals that fixed model redactions; author of *Извещение о согласнейших пометах*, the most complete exposition of znamenny theory (the pomety/priznaki system). |
| **Иван Шайдуров** | c. 1600 | Introduced cinnabar pitch marks — the first systematic pitch-fixing layer over the neumes. |
| **Old Believer choirs** (e.g. the Rogozhskoe community, Moscow) | 17th c.–present | Kept kryuki singing, the кокизники and the razvody alive after the Nikon reforms pushed the official church toward "Latin" polyphony. |
| **Stepan Smolensky** | 1888 | Published *Азбука знаменного пения* — the scholarly reconstruction/edition of Mezenets that made the system readable to modern research. |
| **A. Kastalsky, S. Rachmaninoff, A. Grechaninov, M. Steinberg, V. Martynov** | 19th–20th c. | **Reception, not this method**: they took znamenny melodies as cantus firmi and harmonised them in Western tonal / part-song style (Rachmaninoff's *All-Night Vigil*, 1915). Keep this separate — see quirks. |

## 5. Musical Elements Framework reading

- **PITCH:** *degrees*, not absolute pitches. A 12-step chant ladder grouped in registral bands
  (*согласия*); formula identity is a contour over degrees relative to the glas final. Microtonal shading
  is *not* the point here (unlike makam/radif) — the point is formula-shaped contour.
- **RHYTHM:** **non-mensural**. Durations are attributes of the formula (the neume's relative weight),
  not of a metre; no barlines, no regular accent. Text stress selects which neume of the formula is
  lengthened; melisma is carried by open vowels.
- **HARMONY:** absent by doctrine — unison monody. Vertical sonorities only as the incidental result of
  many voices on one line.
- **STRUCTURE:** phrase chain (строка) → sticheron/verse → liturgical unit. Macro-form is given by the
  service, not invented: зачин → verses → славник (doxastic, most melismatic) → final cadence.
- **TEXTURE:** unison with *registral* texture: one line, but the formula bank shifts the line between
  register bands; density varies by formula type (kokiza sparse ↔ fita dense).

## 6. UnitMatrix mapping

### 6.1 Voices (rows)

Monody is the hard part: the matrix's rows normally mean simultaneous polyphony, but znamenny has one
sounding line. Two sanctioned layouts:

**(A) Antiphonal layout (recommended, sounding, zero-drift safe).** Real practice sings "на два лика"
(two choirs) in cathedral use, and the головщик intones alone before the choir enters:

| Row | Name | GM program | Role |
|---|---|---|---|
| V0 | Головщик (head cantor) | 52 Choir Aahs (solo-ish, low velocity spread) | Intones the зачин of each chant; sings фита razvody exposed; otherwise silent (padded rest cell). |
| V1 | Первый лик (first choir) | 52 Choir Aahs | Carries the body of the chant — the popevka-assembled unison line. |
| V2 | Второй лик (second choir) | 52 Choir Aahs | Antiphonal answer on alternate verses/refrains; silent elsewhere. |

**Monophony invariant:** at any tick, **at most one row sounds**. V0/V1/V2 are time-exclusive, never
simultaneous. Silent stretches are padded cells (zero-velocity events or a single rest event of the full
section length) so every row still ends on the section's terminal landmark.

**(B) Analytical layout (analysis only, never rendered).** Four descriptive rows — text spine,
popevka skeleton, fita expansion, anenayki — that are *sequential* strata of one line. If you build it,
add a "monophony-collapse" renderer that flattens rows into one stream and asserts no temporal overlap.
Prefer (A) for actual export; use (B) only to study formula distribution.

### 6.2 Sections (columns)

Sections = liturgical phrases/verses. At `ticks_per_beat=480`, `beats_per_bar=4` → `BAR = 1920`, but the
bar is a **container only** — znamenny has no metre, so set free/uneven section lengths and never
quantise onsets to the beat grid.

| Col | Section | Content |
|---|---|---|
| S0 | Зачин (intonation) | Головщик alone, 1 phrase, states the glas with its diagnostic formula. |
| S1 | Стихира, verse 1 | Первый лик; 3–5 popevki, cadence on the glas final. |
| S2 | Verse 2 | Второй лик (antiphony); same glas bank, different formula order. |
| S3 | Verse 3 | Первый лик; may climb register (подъём) then return. |
| S4 | Славник (doxastic) | Most melismatic section; 1–2 фиты + лица; density maximum. |
| S5 | Конечное утверждение | Cadential formula only; final on the tonic degree; no ornament. |

Cell duration = the assembled phrase's tick sum, padded to the section terminal. All arithmetic in
integer ticks — zero drift is preserved because every formula's rhythm is a fixed integer vector.

### 6.3 Data structures to encode

```python
GLAS_BANK = {
  1: {  # per glas: closed inventory
    "finalis_deg": 0,
    "diagnostic": ["litso_A", "popevka_koleso"],       # announces the glas
    "popevki": {
      "popevka_koleso": {"degrees": [+0,+1,+0,-1], "rhythm": [480,480,480,960],
                         "syllables": 2, "start": 0, "end": -1, "band": "простое"},
      ...
    },
    "fity": {"fita_B": {"sign": "FITA_B", "razvod_degrees": [...], "razvod_rhythm": [...],
                        "syllables": 1, "start": 2, "end": 0}},
    "litsa": {...},
  },
  ...
}
```

- **Pitch** = integer scale-degree offsets from the glas finalis, then mapped to MIDI through the chant
  ladder; the *согласие* band is a filter on the degree range.
- **Rhythm** = integer tick vectors, per formula. No global metre.
- **Text** = list of phrases, each a syllable count; a phrase is "covered" when the chosen formulas'
  syllable counts sum exactly to it.

### 6.4 Rules to encode

1. **Glas lock:** a section carries a glas tag; every formula drawn must exist in that glas's bank.
   Cross-glas substitution is rejected (formulas are not transposable — transposition breaks identity).
2. **Splice rule:** `end_deg(n) == start_deg(n+1)` or within ±1 step; reject leaps > 4th and any
   tritone outline at the seam.
3. **Syllable lock:** `Σ syllables(chosen formulas) == syllables(phrase)`. On mismatch, *swap a formula*
   (small exhaustive search over the bank); never stretch or compress the text.
4. **Cadence rule:** the last formula of a phrase must be cadential and must end on the glas final;
   S5 ends on the tonic degree and carries no ornament.
5. **Glas-identity rule:** at least one *diagnostic* formula within the first two formulas of the piece.
6. **Registral rule:** stay inside the glas's band set; a подъём (ascent) must be answered by a descent
   before the cadence.
7. **Fita rule:** a fita expands 1 sign → 20–40 notes; allowed only on traditionally melismatic words;
   use the canonical razvod verbatim (no free invention), and only in S4 or at a doxology.
8. **Non-mensural rule:** durations come from the formula; no beat-grid quantisation; `beats_per_bar` is
   a container only; no downbeat accent rule.
9. **Continuity rule:** no rests inside a phrase; a phrase boundary is a breath gap, not a notated rest
   (the tradition explicitly has "no pauses").
10. **Monophony invariant:** ≤ 1 sounding row per tick; assert `len(set(onsets)) == 1` per onset time.
11. **Repetition-avoidance:** no formula more than twice consecutively; vary by *подобен* substitution
    from the same glas family.
12. **Prosody rule:** the stressed syllable lands on the formula's weighty neume; melisma only on open
    vowels; anenayki (non-semantic vocables) never consume text syllables.
13. **Antiphony rule:** V0/V1/V2 alternate by section; alternation is exclusive, never overlapping.

### 6.5 Realization path

`UnitMatrixComposer(bpm≈66, ticks_per_beat=480, beats_per_bar=4)` → `create_matrix(3, 6)` →
`add_voice` per table (all program 52) → `add_section` with free/uneven lengths → assemble S1–S5 by
bank lookup + splice/syllable constraints → insert fity at S4 → `validate()` (zero-drift, pad cells) →
`to_midi()` → humanize with a **very tight** profile (σ ≈ 2–4 ms, zero layback, no swing: a monastic
unison is precise, its expression is in the formula choice, not in timing) → FluidSynth `-g 1.2` →
`provenance.json` + grid visualisation. Remember: any "expression" added by jitter is *wrong* here.

## 7. Quirks & pitfalls

- **Monody vs the matrix.** The engine's rows imply polyphony. Use the antiphonal layout (time-exclusive
  rows) and assert the monophony invariant; never fill three rows simultaneously and call it "chant".
- **No absolute pitches.** The notation is adiastematic; you must choose an anchor finalis per piece
  (and say so in provenance). Any claim that a specific kryuk "is" a specific MIDI note is a modern
  transcription, not the source.
- **Fity cannot be generated.** They are looked up. A generator that invents melismas under a fita sign
  is producing a different, non-traditional object; ship the razvod as data.
- **Popevka ≠ motive.** A popevka is a *closed, named, glas-bound* formula with a fixed syllable count;
  HC-009-style transformation (inversion, augmentation) does not apply. You *substitute*, you do not
  develop. Conversely don't treat popevki as interchangeable "cells" — their incipit/terminal degrees
  restrict chaining.
- **Text lock causes backtracking.** Syllable counts often force a different formula than the beautiful
  one. Implement the search; do not fudge syllable counts or split a word.
- **No metre, no barlines, no dynamics.** Don't mark crescendos; don't humanise with rubato; don't
  accent downbeats. "Continuous, fluent, no pauses" is the performing rule.
- **Redaction matters.** Old Believer, Synodal, Kievan, Pomorsky, Prostopinije (Carpatho-Rusyn) versions
  differ. Pick one redaction per project and record it; mixing them produces a chimera.
- **Harmonisation is a different method.** Rachmaninoff/Kastalsky four-part settings are 19th–20th-c.
  reception (a cantus-firmus harmonisation craft), not znamenny composition. Do not let tonal chords
  leak into an HC-087 realisation.
- **Anenayki are vocables**, related to Byzantine *kratimata*; they are not words and must not be
  syllable-counted with the text.
- **Согласия count is debated** (three vs four register bands in the literature); encode the band map as
  a parameter, not a hard-coded truth.
- **Zero-drift padding:** a "silent" row still needs a cell that terminates exactly on the section
  landmark — pad with a zero-velocity event, not a shortened cell.

## 8. Sources consulted

- Wikipedia (EN), "Znamenny chant" — neume/adiastematic description, stolp notation, Shaidurov's cinnabar
  marks, Nikon-era decline, performance practice (unison, no pauses, natural voice), Unicode block.
- Wikipedia (RU), "Знаменное пение" — столповой распев built from попевки (кокизы), фиты and лица; the
  eight-glas system and its per-glas formula sets; кокизники/фитники/азбуки as pedagogy; the
  Preobrazhensky quotation on glas-as-formula; masters (Савва Рогов, Фёдор Крестьянин, Иван Нос,
  Маркелл Безбородый, Стефан Голыш, Фаддей Субботин); Mezenets and the 1668 commission; призна́ки/пометы.
- В. С. Смоленский, *Азбука знаменного пения* (Kazan, 1888) — edition/reconstruction of Mezenets'
  *Извещение о согласнейших пометах* (cited in the above).
- Ю. Холопов, *Гармония. Теоретический курс* (2003) — cited for the theoretical framing of Russian
  chant harmony/monody.
- J. von Gardner, *Russian Church Singing*, vol. 1 (1980) — standard Western-language account of the
  chant system and its notation.
- А. В. Преображенский — the "glas is known by its popevki" formulation, quoted via the RU article.
