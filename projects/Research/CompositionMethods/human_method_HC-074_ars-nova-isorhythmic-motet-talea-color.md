# HC-074 — Isorhythmic Motet Composition: Talea & Color Cyclic Architecture (Ars Nova Pre-Compositional Planning)

**Method ID:** HC-074
**Layer:** `concrete (target when implemented)` — the method's two engines are note-level: the *color* is a fixed pitch vector (a chant melisma) and the *talea* is a fixed duration vector (a rhythmic pattern); the tenor cell in the UnitMatrix is literally the color vector rhythmized by the talea vector. A cell = one talea statement; a section = one color statement (integer number of taleae). Upper voices are concrete note streams constrained to range strata. The "harmony" is an *emergent vertical property* of voice-leading against the tenor — no chord layer is composed.
**Tradition:** Western Classical — Medieval Ars Nova and its aftermath (14th–early 15th century): Paris, Roman de Fauvel interpolations (c. 1316); Philippe de Vitry (d. 1361) and Guillaume de Machaut (c. 1300–1377); late-14th-c. English/French composers (Johannes Alanus, Pycard, Old Hall MS); 15th-c. panisorhythm in Dunstable, Ciconia and Guillaume Du Fay (d. 1474).
**Primary elements:** STRUCTURE, RHYTHM, PITCH, TEXTURE (HARMONY as emergent sonority — deliberately non-functional).
**Related but distinct methods:** HC-062 (twelve-tone serialism — pitch-row *permutation* system; isorhythm is a *chant-sourced* melody rhythmized by an independent cycle, no pitch transformations), HC-055 (fugue — free counterpoint, no cyclic pre-composition), HC-066 (ground bass — a repeating bass as *harmonic* foundation; the isorhythmic tenor repeats as a *rhythmicized melodic* cycle and its repetition is structural, not continuo), HC-002 (Balinese kotekan — interlock as elaboration of a fixed melody; hocket is its medieval cousin), HC-008 (minimalist phasing — the 20th-c. descendant of cyclic misalignment: Reich's phase = two colores drifting against each other), HC-021 (species counterpoint — pedagogical voice-leading, no cyclic scaffold), HC-073 (sutartinės — staggered canonic entry but *no* independent pitch/rhythm cycles).

---

## 1. What the method is

**Isorhythm** (from Greek, "the same rhythm"; the term was coined in 1904 by musicologist Friedrich Ludwig) is the organizing principle of the most ambitious music of the 14th century: a composition built on **two independent repeating cycles applied to one voice** — a repeating *rhythm* pattern (the **talea**) and a repeating *melody* pattern (the **color**). The cycles are deliberately of **different lengths**, so the melody is heard again and again under *different* rhythmic disguises, and the whole architecture rotates against itself until the two cycles realign.

Three structural facts make it a genuine **human composition method** rather than a curiosity:

1. **The melody is borrowed, the rhythm is invented.** The color is a pre-existing Gregorian chant melisma (antiphon, introit, gradual, alleluia — e.g. *Terribilis est locus iste*, *In omnem terram*, the "David" melisma). The composer's melodic invention is minimal; the *craft* is deciding how to cut the chant into a color, how to pattern time into a talea, and how many statements to build before the cycles realign.
2. **The form is arithmetic before it is sound.** The number of sections = the number of color statements; each section carries an integer number of talea repetitions (Machaut's Kyrie: color 28 pitches ÷ talea 4 durations = 7 statements per color). With unequal cycles (color 9, talea 5), the schemes realign only after the least common multiple — the composer *plans* the piece's length by choosing the ratio.
3. **Diminution is written once, heard many times.** Later color statements re-read the *same notation* under new mensuration signs, so each statement is proportionally shorter (Alanus: 9/8 → 6/8 → 4/8; Dufay: 6:4:2:3). The composer writes the tenor once; the signs are the speed changes.

The result sounds nothing like a loop: a slow, chant-like tenor in long notes, with one or two rapid, independent, *differently-texted* upper voices weaving around it, converging at structural seams on perfect sonorities — the medieval motet, the most intellectually organized music before the Renaissance.

---

## 2. Why this is not an algorithm

- **The ratio is a choice, not a computation.** Nothing forces 28:4 or 6:4:2:3; those were *decisions* (Dufay's 6:4:2:3 encodes Solomon's Temple dimensions from 1 Kings 6 — numerology, not math). An algorithm can emit the cycles; only a composer chooses what the ratio *means*.
- **The upper voices are free until panisorhythm.** For most of the 14th century the triplum and motetus were composed by ear against the tenor, not cycled. The craft is *constraint + freedom*, not full determinism.
- **The term is an analyst's label, not a composer's rule.** Medieval theorists spoke of *talea* and *color*; "isorhythm" is Friedrich Ludwig's 1904 coinage for 13th-c. practice, later extended to Machaut. Composers did not "apply isorhythm" — they cut a chant and patterned time.
- **The music is pre-tonal.** There is no harmonic progression to generate: vertical sonorities emerge from voice-leading (thirds/sixths mid-phrase, perfect at cadence). This is a *listening contract* different from functional harmony.
- **Text and structure are independent.** Upper-voice poetry (e.g. Dufay's 4 strophes × 7 lines) deliberately ignores the tenor's structural seams — the poet-composer composed two time grids at once.

---

## 3. The craft procedure, step by step

### Step 0 — Select the cantus firmus
Choose a pre-existing plainchant melisma from the liturgy — the tenor's material. Standard choices: an introit (*Terribilis est locus iste* — Dufay), an antiphon (*In omnem terram exivit sonus eorum* — Alanus), a melisma on a liturgical word ("David" — Machaut's *Hoquetus David*), Office antiphons for Marian feasts (Machaut's motets). Transposition is normal (Alanus set the chant a fifth higher than the original).

### Step 1 — Carve the color (the pitch cycle)
Take a segment of the melisma as the **color** — the exact ordered pitch sequence that will recur. Its length is the composer's first decision: Machaut's Kyrie color = 28 pitches; Dufay used 14 notes of *Terribilis* (the late-medieval Florentine reading; the modern version has 17). The color is the piece's *pitch identity*.

### Step 2 — Compose the talea (the rhythm cycle)
Write the **talea** — a short pattern of note values *and rests* (longa, breve, semibreve, minima in mensural notation). Rests are structural: Dufay's tenor alternates 14 sounding longae with 14 rests (28 total). Machaut's Kyrie talea = 4 durations. The talea is the piece's *rhythm identity*.

### Step 3 — Fix the ratio and the alignment schedule (the central craft decision)
Decide how color and talea interlock:
- **Equal division:** color divisible by talea (28 ÷ 4 = 7) → each color statement carries exactly 7 talea statements and the alignment repeats identically (Machaut's Kyrie).
- **Unequal cycles (panisorhythmic drift):** color 9, talea 5 → the same melody recurs under ever-shifting rhythms; realignment after 5 color statements (LCM 45). The composer chooses how many statements to write *before* realignment — the piece's whole duration.
- **Double tenor:** two tenor voices share one color but carry different interlocking taleae (Dufay: two tenors a fifth apart, taleae totaling 28 longae each).

### Step 4 — Lay out the macro-structure
Common plan: a free **introitus** (one or two un-isorhythmic phrases), then the isorhythmic core — color statement 1 (k₁ taleae), statement 2 (k₂), … Each statement is one large section. Dufay's four statements × two sub-sections each (bicinium, then full ensemble) = eight parts.

### Step 5 — Rhythmize the tenor
Notate the color's pitches against the talea's durations: color note 1 = talea value 1, etc. With unequal lengths the talea overruns into the next color statement, so the chant audibly *slips* against the rhythm; talea rests silence the tenor at the same cycle point every time.

### Step 6 — Plan diminution (the acceleration scheme)
Decide how later statements re-read the *same written tenor* under new mensurations — the same notation performed with shorter note values. Alanus: three statements under 9/8 → 6/8 → 4/8 (threefold diminution, 3 taleae per color = nine-part structure). Dufay: 6:4:2:3 (tempus perfectum → imperfectum → imperfectum diminutum → perfectum diminutum). Diminution is a *proportional operator* written as mensuration signs, not as new notes.

### Step 7 — Compose the upper voices
- **Triplum + motetus** (the two upper texted voices), each with its **own text** (polytextuality — the motet's signature: Latin chant in the tenor, independent sacred *and/or* secular French texts above). Range strata: motetus ≈ a fifth above the tenor, triplum ≈ an octave to a twelfth above.
- **Contratenor** (4th voice, from Vitry's generation): a free filler voice between tenor and motetus, sometimes sharing the tenor's cyclic organization.
- **Vertical style:** imperfect consonances (thirds, sixths) preferred mid-phrase; cadences converge on perfect sonorities (unison/octave/fifth), often with a decorated approach (lower-neighbor ornament in the top voice).
- **Panisorhythm** (late 14th–15th c.): upper voices receive their *own* taleae — Pycard's Old Hall mass runs four different upper-voice taleae against one recurring lower color+talea, with a 4:9 rhythmic ratio that desynchronizes the parts, then a Pythagorean contraction (12:9:8:6) that pulls them back into alignment.

### Step 8 — Apply hocket (optional texture operator)
Split a line into single notes or two-note groups and trade them rapidly between voices (hocket = "hiccup"). Machaut's *Hoquetus David* is a whole three-voice piece built on this; inside motets, hocket passages punctuate phrase ends and climaxes. This is the textural foreground that makes the cyclic structure audible.

### Step 9 — Fit text underlay
Syllable counts govern upper-voice phrase rhythm; melismas sit on penultimate or cadential syllables. The poetry is deliberately *not* aligned with the tenor's structural sections — the two grids coexist (Dufay's 4 strophes of 7 lines × 7–8 syllables run across the 6:4:2:3 tenor statements).

### Step 10 — Notate in mensural notation and copy
Everything is written in mensural notation with tempus/prolatio signs; the signs double as diminution instructions. Machaut unusually supervised the copying of his complete-works manuscripts, curating his own output — the composer's manuscript *is* the score, and modern editions transcribe it into bar-lines with the color/talea structure diagrammed on top.

---

## 4. Practitioner examples

| Practitioner / body | Role in the craft |
|---|---|
| **Roman de Fauvel manuscript** (Paris, BN fr. 146, c. 1316–17) | 169 interpolated pieces spanning Ars Antiqua→Ars Nova; among the earliest works organized around isorhythm; several pieces linked to Philippe de Vitry. |
| **Philippe de Vitry** (1291–1361) | The Ars Nova's theorist-composer; four-voice isorhythmic motets (*Garrit Gallus / In nova fert* and the Fauvel motets) with contratenor; the generation that made talea/color the defining motet feature. |
| **Guillaume de Machaut** (c. 1300–1377) | The master poet-composer. *Messe de Nostre Dame* (c. 1360): the Kyrie's isorhythmic tenor uses a **color of 28 pitches with a talea of 4 durations repeated 7 times** (28 ÷ 4 = 7) — the canonical textbook example. His second motet, *De souspirant / Tous corps qui bien amer / Suspiro*, typifies 14th-c. use; motets M1–M23 combine sacred tenor texts with secular French upper voices. *Hoquetus David*: an untexted three-voice piece, the classic composed-out **hocket** on a chant melisma. |
| **Johannes Alanus** (late 14th c.) | *Sub arturo plebs / Fons citharizantium / In omnem terram*: tenor = the antiphon *In omnem terram* transposed a fifth higher; **threefold isorhythmic diminution** — three mensuration signs (9/8, 6/8, 4/8) over three color statements × three taleae = nine-part structure. |
| **Pycard** (early 15th c., Old Hall MS) | Panisorhythmic mass: lower parts share one recurring color+talea; upper parts run **four different taleae**; a 4:9 rhythmic ratio desynchronizes the parts, then a Pythagorean contraction 12:9:8:6 pulls them back into alignment — the period's most complex cyclic planning. |
| **John Dunstable, Johannes Ciconia** (early 15th c.) | Panisorhythmic motets and Mass movements — all voices cyclically organized, with unequal color/talea lengths producing the characteristic drift-and-realign. |
| **Guillaume Du Fay** (c. 1397–1474) | *Nuper rosarum flores* (1436, consecration of Florence Cathedral): **double tenor** — two tenors a fifth apart, both on the 14-note color of *Terribilis est locus iste*, with interlocking taleae (28 longae, first 14 rests); the pair stated **four times** under 6:4:2:3 proportions. Craig Wright showed the proportions encode **Solomon's Temple** dimensions (1 Kings 6: 60×40×20×30 cubits); Charles Warren's earlier "Brunelleschi's dome" claim is refuted. Each section splits bicinium→full ensemble (eight-part structure). |
| **20th-c. afterlife** | Isorhythm is used analytically for non-Western cyclic musics (peyote songs, Indian and African traditions) and returns as a compositional reference in cyclic/minimalist planning (e.g. the phasing of Steve Reich is the same misalignment idea in a new idiom). |

**Canonical repertory examples:** Machaut *Messe de Nostre Dame* (Kyrie, Sanctus, Agnus — the Agnus is the teoria.com tutorial example), *De souspirant / Tous corps / Suspiro* (M2), *Hoquetus David*; Vitry *Garrit Gallus / In nova fert*; Alanus *Sub arturo plebs*; Pycard Old Hall mass; Dufay *Nuper rosarum flores*, *Ecclesie militantis* (1431, first double-tenor motet).

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. The grid is filled with actual sounding parts: tenor cells = one talea statement each (color pitch vector × talea duration vector); sections = color statements; upper voices = free or panisorhythmic note streams in fixed range strata.

**Voices (rows):**
- **V0 — Tenor (cantus firmus spine).** The piece identity: a *color* pitch vector (fixed ordered pitches from the chant, optional transposition per statement) rhythmized by a *talea* duration vector (fixed note values incl. rests). Long note values, lowest register.
- **V1 — Contratenor (optional, 4-voice texture).** Free filler between tenor and motetus; may carry its own cyclic organization in panisorhythmic writing.
- **V2 — Motetus (upper texted voice).** Independent text and rhythm; range ≈ a fifth above V0.
- **V3 — Triplum (highest texted voice).** Independent text; participates in hocket alternation with V2.
- *(Performance practice: tenor/contratenor often doubled or replaced by instruments — sackbut/curved trumpet/organ; a V4 instrumental doubling row can mirror V0.)*

**Sections (columns):**
- **S0 — Introitus:** free, un-isorhythmic opening (1–2 phrases), no cyclic constraint.
- **S1…SN — Color statements:** one per section; each section contains k talea repetitions (k = color_len ÷ talea_len when equal, or the planned LCM segment when unequal). Section lengths scale by the diminution proportions (Alanus 9:8→6:8→4:8; Dufay 6:4:2:3), so later sections are tick-shorter at the same base tempo.

**Rules to encode:**
1. **Color lock:** V0's pitch sequence per section = the fixed color vector (transposition allowed per statement, e.g. Alanus +5th); pitch order never permuted.
2. **Talea lock:** V0's duration vector = the fixed talea repeated k times per section; section tick-length = k × talea-length; with unequal cycles, LCM(color_len, talea_len) governs the full span and the piece ends at (or deliberately before) realignment.
3. **Diminution operator:** per-section tick-scale factor pᵢ (6:4:2:3); the *same* duration vector is reinterpreted — implement as section-length scaling, not new note values.
4. **Range strata:** motetus ∈ [tenor+3, tenor+7], triplum ∈ [tenor+8, tenor+14], contratenor between tenor and motetus; no voice crosses.
5. **Cadence gate:** section-final sonority = perfect (unison/octave/fifth) with decorated upper-voice approach; mid-section verticals prefer imperfect consonances (thirds/sixths). No functional progression — HARMONY is emergent from voice-leading (same philosophy as HC-073 / HC-061).
6. **Hocket operator:** split one voice's note stream into 1–2-note fragments alternated across two voices on the subdivision grid (pure case: *Hoquetus David*).
7. **Polytextuality:** V2 and V3 carry independent text grids with independent syllable budgets; their phrase seams need not coincide with section seams.
8. **Talea rests are silence cells:** explicit rest units in the duration vector (Dufay: 14 rests of 28 longae) — a cell type, not a gap.
9. **Zero-drift:** all voices' cells end at the section terminal landmark (section_len from the diminution proportion); validate() must pass; the introitus cells fill S0 exactly.
10. **Emergent harmony check:** vertical interval classes constrained only (imperfect mid-phrase, perfect at cadence), never a composed chord layer.

**Distinct from adjacent HC methods in engine terms:** HC-062 serialism permutes a pitch row (P/R/I/RI matrix); HC-074 repeats a chant color *unaltered* while an independent rhythm cycle rotates beneath it. HC-066 ground bass repeats a *harmonic* bass; HC-074's tenor is a *rhythmicized melody* whose repetition is structural. HC-002 kotekan interlocks as *elaboration* of a fixed pokok; HC-074's hocket fragments an *independent* line between voices. HC-008 minimalism is the same LCM-misalignment idea realized in the 20th century — HC-074 is its medieval ancestor, with chant, polytextuality and mensural diminution.

---

## 6. Quirks & pitfalls

- **"Isorhythm" is a 20th-c. analyst's term** (Friedrich Ludwig, 1904), not a medieval one; composers thought in *talea* and *color*. Margaret Bent has argued the label overstates the technique's unity — describe the two cycles, don't reify the ism.
- **"Color" here ≠ timbre.** In this repertory *color* means repetition/embellishment of a melody (the medieval Latin sense), not orchestral color. Do not confuse the two in a music-AI context.
- **Rests are structural, not expressive.** Dufay's tenor is silent for half its talea; an engine that treats rests as optional gaps destroys the architecture.
- **Diminution is proportional, not recomposed.** The tenor is written once; mensuration signs encode the speed changes. In a tick grid, implement as per-section duration scaling (6:4:2:3), not by rewriting note values.
- **The 6:4:2:3 numerology:** Craig Wright (1994) refuted Warren's "Brunelleschi's dome" reading of *Nuper rosarum flores*; the proportions match Solomon's Temple (1 Kings 6:1–20). Cite Wright, not Warren.
- **Chant source versions differ:** Dufay's 14-note *Terribilis* is the late-medieval Florentine reading, not the modern 17-note version — transcribe from the period source.
- **Mensural arithmetic is counterintuitive** (tempus perfectum/imperfectum, prolation, alteration) — transcribe via established modern editions rather than recomputing from raw manuscript.
- **Upper voices are not generated.** Until panisorhythm, the triplum/motetus are composed freely against the tenor; an implementation that cycles them automatically produces *panisorhythm*, a late style — legitimate, but not the 14th-century default.
- **Text independence is the point.** Aligning the upper-voice poetry to the tenor's sections would destroy the polytextual counterpoint of two time-grids — a common mistake when "cleaning up" the form.
