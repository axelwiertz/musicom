# REPORT HC-087 — Znamenny Chant Popevka (Kokiza) Formula Assembly

**Job:** `daily-human-composition-research` · **Date:** 2026-11-08 · **Layer:** `concrete (target when implemented)`
**Detail file:** `human_method_HC-087_znamenny-popevka-formula-assembly.md`
**DB row added to:** `human_methods_db.md` → *Human Composition Methods Framework* table
**Next free ID:** **HC-088**

---

## 1. Method name, tradition, layer

**Znamenny Chant Composition by Popevka (Kokiza) Formula Assembly** —
*знаменное пение / знаменный распев*, main redaction *столповой распев* (stolpovoy chant).

- **Tradition:** Russian Orthodox and Old Believer liturgical monody. Kievan Rus' (earliest notated
  kryuki manuscripts 11th c.) → Novgorod → Muscovy; system elaborated through the 16th c., codified in
  the 1660s, then sidelined in the official church after Patriarch Nikon's reforms (Westernised
  polyphony, pejoratively "Latin" singing), and preserved by the Old Believers to the present.
  Related branches: Ruthenian *Prostopinije*, Pomorsky, Kievan, Demestvenny, and the early polyphonic
  *strochnoy* chant built on znamenny material.
- **Layer classification:** human-craft knowledge → tagged **`human (→concrete)`**, target layer
  **concrete** when implemented. The method realises material (degrees, tick-vectors, formula IDs) into
  the UnitMatrix; it supplies *selection and assembly rules*, which is exactly what the concrete layer
  needs.
- **Forces:** unison unaccompanied voices; no instruments; no metre; no dynamics; no rests.

**Why this method this round:** Russia/Ruthenia was absent from the DB (grep for
`znamenny|popevka|kryuki` → 0 hits), and this is the one major European sacred craft whose composition
engine is a **named formula dictionary locked to a mode-tone and to a syllable count**, with a class of
signs (фиты) that are *deliberately* unreadable at sight. Rotation: last eight IDs ran Trinidad, Japan,
Greece, Mexico, China, Morocco, France, France — a Slavic sacred entry is a clean break.

---

## 2. The craft procedure in detail (how the human actually does it)

### 2.1 Build the formula memory before composing anything

Training happens inside a chant school. The singer learns the neume ABC (sign names, shapes, interval
meaning), drills the **eight glasy** until each is recognisable *by its typical turns*, and memorises the
**кокизник** (dictionary of popevki: name, contour, syllable count, incipit and terminal degree) and the
**фитник** (dictionary of fity with their razvody). The 17th c. produced the pedagogical genre:
*азбуки*, *кокизники*, *фитники*. Literacy in this system means *recognising formulas*, not decoding
pitches — which is why a trained singer with an unknown manuscript in hand may still be unable to sing it.

### 2.2 Fix the liturgical brief

1. **Book & genre** — Обиход (daily), Октоих (eight-tone cycle), Минея (fixed feasts), Триодь
   (Lent/Pascha), Ирмологий; genre стихира / тропарь / ирмос / кондак / величание.
2. **Глас 1–8** — selects the *closed* bank. Critically, the glas is **not a scale**: as A. V.
   Preobrazhensky observed, the singer identified the glas "by the presence in the melody of typical
   turns, found only in that glas, which he called *popevki*"; Russian chant theory never formed a
   Western concept of *звукоряд* (scale).
3. **Text** — split into phrases (*строки*) at syntactic/cadential punctuation, count syllables, and mark
   the words the tradition melismatises: "Господи", "аллилуиа", the doxastic *славник*, the end of a
   stichera.

### 2.3 The three formula classes

| Class | Size | Notation status | How the singer uses it |
|---|---|---|---|
| **Кокиза / попевка** | 2–6 neumes | written out as neumes | the workhorse unit: chosen for syllable count + splice fit; glas-bound, never transposed |
| **Лицо (litso)** | extended phrase | written out, memorised whole | announces the glas; used at openings and structural seams |
| **Фита** | 20–40 notes | **one composite cryptic sign** (*тайнозамкненность*, "secret-closed") | a melismatic explosion at a doxological word; must be sung from the memorised **развод** (razvod) |

### 2.4 Assemble the phrase

1. **Open** with a diagnostic formula (a лицо or signature popevka) so the glas is audible immediately.
2. **Chain** popevki under the *splice* (`сцепление`) rule: terminal degree of formula *n* equals, or is
   within a step of, the incipit of *n+1*; wide leaps and tritone outlines are rejected at the seam.
3. **Close** on a cadential formula that lands on the glas final (*утверждение*), so the phrase is
   audibly complete.
4. **Respect the register bands.** The chant ladder (*обиходный звукоряд*) is conceived as stacked
   registral areas — in the standard modern account four *согласия* of three steps each (простое,
   мрачное, светлое, тресветлое; the count/naming is debated). A подъём (ascent) must be answered by a
   descent before the cadence.
5. **Insert the fita verbatim.** Only at traditionally melismatic words, only from the canonical razvod.
   This is the one place where the notation's unreadability is intentional: it protects the oral school's
   authority and prevents the untrained from "improvising" the tradition's most sacred melismas.
6. **Add аненайки** — non-semantic vocable insertions (the Russian relative of Byzantine *kratimata*),
   where the local redaction allows. They consume no text syllables.

### 2.5 Repair the relative notation (17th-c. pitch fixing)

Because stolp signs are adiastematic:

- **c. 1600 — Иван Шайдуров** adds *киноварные пометы* ("cinnabar marks"): small red letters before a
  sign giving **the highest note of that sign**. Regarded as the first step toward simplification — an
  early relative→absolute annotation layer.
- **1660s — Александр Мезенец** and the commission of six didaskals codify **признаки** (qualifying
  marks) + **пометы** (pitch letters) and fix model redactions. Manuscripts before this are
  *беспометные* (unmarked). His *Извещение о согласнейших пометах* is the fullest statement of the theory.

### 2.6 Perform, correct, transmit

Sing beside the головщик: continuous, no pauses, natural voice (no conservatory production, sometimes
close to folk timbre), "so that the sound astonishes the ear"; all voices should fuse into one. Corrections
are by ear against the elder's canonical *образец*. Transmission = copying the kryuki manuscript +
memorising the named formulas. The composition is never "finished" on paper; manuscript + school memory
*is* the piece.

---

## 3. Practitioner examples

- **Фёдор Крестьянин** (Fyodor Krestyanin), mid-16th c. Moscow — the outstanding named master of the
  Vasily III / Ivan IV era; composed stichera using both znamenny and demestvenny chant.
- **Савва Рогов, Иван Нос, Маркелл Безбородый, Стефан Голыш** — the 16th-c. generation whose redactions
  constitute the classical stolpovoy repertoire.
- **Фаддей Субботин** (Usolsk school) — worked on Nikon's reform commission; the regional school behind
  the codification.
- **Александр Мезенец** (didaskal, 1657–1668) — chaired the six-didaskal commission; author of the
  *Извещение*; the theorist of пометы/признаки.
- **Иван Шайдуров** (c. 1600) — cinnabar pitch marks.
- **Old Believer choirs** (e.g. the Rogozhskoe community, Moscow) — kept kryuki singing, кокизники and
  razvody alive after the reforms; the living practice today.
- **Stepan Smolensky** (1888, *Азбука знаменного пения*) — the scholarly edition of Mezenets that opened
  the system to modern research.
- **Reception, explicitly *not* this method:** Kastalsky, Rachmaninoff (All-Night Vigil, 1915),
  Grechaninov, Steinberg, Martynov harmonised znamenny melodies as cantus firmi. That is a 19th–20th-c.
  cantus-firmus harmonisation craft; do not let its triads into an HC-087 realisation.

---

## 4. UnitMatrix mapping

### 4.1 Voices (rows) — monody forces a design decision

The matrix's rows normally mean simultaneous polyphony; znamenny has **one sounding line**. Two layouts:

**(A) Antiphonal layout — the one to render.** Grounded in real practice: the головщик intones alone, the
choir answers, and in cathedral use the two choirs (*два лика*) alternate.

| Row | Role | Program | Content |
|---|---|---|---|
| V0 | Головщик (head cantor) | 52 Choir Aahs | Intones the зачин, exposes fita razvody; padded silent cells elsewhere |
| V1 | Первый лик | 52 Choir Aahs | The popevka-assembled unison body |
| V2 | Второй лик | 52 Choir Aahs | Antiphonal answer on alternate verses; silent elsewhere |

**Monophony invariant:** at any tick **at most one row sounds**. Rows are time-exclusive. Silent rows are
padded with zero-velocity events (never a shortened cell) so every row still terminates on the section
landmark → `validate()` stays green.

**(B) Analytical layout — analysis only, never rendered.** Four descriptive rows (text spine / popevka
skeleton / fita expansion / anenayki) that are *sequential strata* of one line. Requires a
*monophony-collapse* renderer that flattens rows into one stream and asserts no temporal overlap. Useful
for studying formula distribution; useless (and wrong) as polyphony.

### 4.2 Sections (columns)

Free, uneven phrase lengths — znamenny has no metre, so `BAR = 1920` is a container only and onsets are
never quantised to the beat grid.

| Col | Section | Content |
|---|---|---|
| S0 | Зачин | Cantor alone; states the glas with its diagnostic formula |
| S1 | Стихира, verse 1 | Первый лик; 3–5 popevki; cadence on glas final |
| S2 | Verse 2 | Второй лик (antiphony); same bank, different order |
| S3 | Verse 3 | Первый лик; may climb (подъём) then return |
| S4 | Славник | Doxastic, most melismatic: 1–2 фиты + лица; density maximum |
| S5 | Конечное утверждение | Cadential formula only; final on tonic; no ornament |

### 4.3 Rules to encode

1. **Glas lock** — formulas only from the section's glas bank; no transposition (transposition destroys
   formula identity, unlike HC-009 motives).
2. **Splice rule** — `end_deg(n) == start_deg(n+1)` or ±1 step; reject leaps > 4th and tritone outlines.
3. **Syllable lock** — `Σ syllables == phrase syllables`; on mismatch swap a formula (small exhaustive
   search), never stretch the text.
4. **Cadence rule** — every phrase ends on a cadential formula on the glas final; S5 unornamented.
5. **Glas-identity rule** — a diagnostic formula within the first two formulas.
6. **Registral (согласие) rule** — stay in the band set; every подъём answered by a descent.
7. **Fita rule** — 1 sign → 20–40 notes, canonical razvod only, S4/doxology only.
8. **Non-mensural rule** — durations come from the formula's tick vector; no beat quantisation, no
   downbeat accent.
9. **Continuity rule** — no rests inside a phrase; phrase boundary = breath gap, not a notated rest.
10. **Monophony invariant** — ≤ 1 sounding row per tick.
11. **Repetition-avoidance** — no formula more than twice consecutively; vary by *подобен* substitution.
12. **Prosody rule** — stress on the formula's weighty neume; melisma only on open vowels; anenayki never
    consume text syllables.
13. **Antiphony rule** — V0/V1/V2 alternate by section, exclusively.

### 4.4 Data shape

```python
GLAS_BANK[glas] = {
  "finalis_deg": 0,
  "diagnostic": ["litso_A", "popevka_koleso"],
  "popevki": {"popevka_koleso": {"degrees":[0,+1,0,-1], "rhythm":[480,480,480,960],
                                 "syllables":2, "start":0, "end":-1, "band":"простое"}},
  "fity":    {"fita_B":        {"razvod_degrees":[...], "razvod_rhythm":[...],
                                "syllables":1, "start":2, "end":0}},
  "litsa":   {...},
}
```

Pitch = integer scale-degree offsets from the finalis, mapped to MIDI through the chant ladder; band =
degree-range filter. Rhythm = integer tick vectors per formula. Text = per-phrase syllable counts, the
hard constraint that drives backtracking.

### 4.5 Realisation path

`UnitMatrixComposer(bpm≈66, tpb=480, beats_per_bar=4)` → `create_matrix(3, 6)` → `add_voice` ×3
(program 52) → `add_section` with uneven lengths → assemble S1–S5 by bank lookup + splice + syllable
constraints → fity at S4 → `validate()` → `to_midi()` → humanize **very tight** (σ 2–4 ms, zero layback,
no swing) → FluidSynth `-g 1.2` → `provenance.json` (+ record the chosen finalis and redaction) → grid
visualisation.

---

## 5. Table row added to `human_methods_db.md`

```
| **HC-087** | human (→concrete) | Znamenny Chant Popevka (Kokiza) Formula Assembly — Osmoglasie Formula-Bank Composition with Syllable-Locked Splicing, Cryptic Fity & Razvod Expansion (столповой распев) | Russian Orthodox & Old Believer liturgical monody — znamenny/stolpovoy chant, Kievan Rus' → Novgorod → Muscovy, 11th–17th c. (canon fixed mid-17th c. after Nikon's reforms; preserved by Old Believers to the present); Ruthenian Prostopinije, Pomorsky/Kievan/Demesvenny branches; didaskals Alexander Mezenets, Ivan Shaidurov; masters Savva Rogov, Fyodor Krestyanin, Ivan Nos, Markell Bezborody, Stefan Golysh, Faddey Subbotin (Usolsk school); scholarship Smolensky (1888), Preobrazhensky, Gardner, Kholopov | PITCH, STRUCTURE, RHYTHM, TEXTURE (+ TEXT as first-class constraint) | Build the formula memory first (neume ABC → drill the eight glasy until each is known by its typical turns → memorise the кокизник/фитник dictionaries; literacy = recognising formulas, not decoding pitches) → fix the liturgical slot (book: Обиход/Октоих/Минея/Триодь/Ирмологий; genre: стихира/тропарь/ирмос/кондак; глас 1–8, which selects the closed formula bank) → divide the text into phrases (строки) at cadential punctuation, count syllables, mark traditionally melismatic words → recall that glas's inventory: кокизы/попевки (2–6 neumes, each with name, incipit degree, contour, syllable count, terminal degree), фиты (long melismas hidden behind ONE cryptic composite sign — тайнозамкненность, 20–40 notes, known only by their развод/razvod), лица (extended phrases that announce the glas) → assemble: open with a diagnostic formula that states the glas → chain middle popevki under the splice rule (terminal degree of n = incipit of n+1, ±1 step, no wide leaps/tritone outline) → close on a cadential formula landing on the glas final (утверждение) → keep within the registral bands (обиходный звукоряд as stacked согласия; подъём must be answered by descent) → insert the фита verbatim from its razvod at the melismatic climax (never invented) → add аненайки vocable ornaments → fix pitch by the 17th-c. apparatus (Shaidurov's cinnabar пометы mark the highest note of a sign, c. 1600; признаки+пометы codified by Mezenets' commission, 1660s) → sing beside the головщик continuously, no rests, natural voice, correct by ear against the canonical образец → transmit by copying the kryuki manuscript + memorising the named formulas | Voices (monody! rows must be TIME-EXCLUSIVE): V0 = Головщик (intones зачин, sings fita razvody exposed; else padded silent cell), V1 = Первый лик (choir Aahs; popevka-assembled unison body), V2 = Второй лик (antiphonal answer on alternate verses); alternative analytical 4-row layout with monophony-collapse renderer. Sections = S0 Зачин → S1 verse 1 → S2 verse 2 (second choir) → S3 verse 3 (may climb register) → S4 Славник (doxastic; 1–2 фиты + лица, density max) → S5 Конечное утверждение; free/uneven lengths, BAR=1920 container only. Rules: glas lock (never transposed); splice rule; syllable lock (swap formula, never stretch text); cadence on glas final; glas-identity formula in first 2; registral-согласие with подъём→descent; fita = canonical razvod only; non-mensural (no beat quantisation, no downbeat accent); continuity (no rests in phrase); monophony invariant (≤1 sounding row/tick); repetition-avoidance; prosody rule; antiphony exclusivity. Humanize very tight (σ 2–4 ms, no swing). | Александр Мезенец (1668 commission; Извещение о согласнейших пометах), Иван Шайдуров (c. 1600 cinnabar marks), Фёдор Крестьянин (mid-16th c. stichera), Савва Рогов / Иван Нос / Маркелл Безбородый / Стефан Голыш, Фаддей Субботин (Usolsk school), Old Believer choirs (Rogozhskoe, Moscow), Stepan Smolensky (Азбука 1888); 19th–20th-c. reception is a different craft (Kastalsky/Rachmaninoff/Grechaninov/Steinberg/Martynov harmonisations) | ✅ Documented |
```

*(The row as written into the DB also keeps the italic markers on *by its typical turns*; the DB is the
authoritative copy.)*

---

## 6. Verification

```
grep HC-087 human_method_HC-087_znamenny-popevka-formula-assembly.md   → present
grep HC-087 human_methods_db.md                                       → 1 occurrence (the table row)
column count of HC-087 row                                            → 10 pipes = 9 columns (matches HC-085/HC-086)
duplicate check                                                       → HC-087 appears once; no prior HC-087 file
```

**Highest ID now HC-087 → next free ID: HC-088.**

---

## 7. Quirks & pitfalls

1. **Monody vs matrix rows.** Rows imply polyphony. Use the antiphonal (time-exclusive) layout and assert
   the monophony invariant. Three simultaneous choir rows is not chant, it is a mistake.
2. **No absolute pitch.** Stolp notation is adiastematic; you must choose and record an anchor finalis.
   Saying a kryuk "is" a particular MIDI note is a modern transcription decision, not the source.
3. **Fity cannot be generated.** They are looked up. Inventing melismas under a fita sign produces a
   non-traditional object; ship razvody as data.
4. **Popevka ≠ motive.** A popevka is a closed, named, glas-bound formula with a fixed syllable count.
   HC-009 operators (inversion, augmentation) do not apply — you *substitute*. Conversely, do not treat
   popevki as free cells: incipit/terminal degrees restrict chaining hard.
5. **Syllable lock forces backtracking.** The metrically pretty formula often does not fit the text. Do
   the search; never fudge syllable counts or split a word.
6. **No metre, no barlines, no dynamics.** No crescendos, no rubato, no downbeat accent. "Continuous,
   fluent, without pauses" *is* the performing rule.
7. **Redaction matters.** Old Believer / Synodal / Kievan / Pomorsky / Prostopinije differ audibly. Pick
   one per project and record it; mixing yields a chimera.
8. **Harmonisation is another method.** Do not let 19th-c. four-part chant arrangements contaminate an
   HC-087 realisation.
9. **Аненайки are vocables** (Byzantine kratimata relatives), not words — exclude from syllable counting.
10. **Согласия count is debated** (three vs four register bands in the literature) — keep the band map a
    parameter, not a hard-coded truth.
11. **Zero-drift:** a silent row still needs a cell terminating exactly on the section landmark — pad with
    a zero-velocity event, never a shortened cell.
12. **Expression lives in formula choice**, not in timing. A tight humanisation is the correct one; a
    swung or heavily jittered znamenny reads as a mistake.

---

## 8. Sources consulted

- Wikipedia (EN), "Znamenny chant" — stolp/adiastematic notation, kryuki, Shaidurov's cinnabar marks,
  Nikon-era decline, performance practice (unison, no pauses, natural voice), branches and Unicode block.
- Wikipedia (RU), "Знаменное пение" — столповой распев built from попевки (кокизы), фиты and лица;
  per-glas formula sets; кокизники/фитники/азбуки; the Preobrazhensky quotation on glas-as-formula;
  named masters; Mezenets and the 1668 commission; признаки/пометы; демественный/путевой branches.
- В. С. Смоленский, *Азбука знаменного пения* (Kazan, 1888) — edition/reconstruction of Mezenets'
  *Извещение о согласнейших пометах* (cited in the above).
- Ю. Холопов, *Гармония. Теоретический курс* (2003) — theoretical framing of Russian chant monody.
- J. von Gardner, *Russian Church Singing*, vol. 1 (1980) — standard Western-language account of the
  system and its notation.
- А. В. Преображенский — the "the glas is known by its popevki" formulation.
