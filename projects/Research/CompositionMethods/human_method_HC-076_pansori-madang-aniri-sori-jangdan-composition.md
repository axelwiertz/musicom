# HC-076 — Pansori Madang Composition: Text-First Narrative Scene Building over Jangdan Cycles (Sori / Aniri / Ballim Architecture)

**Method ID:** HC-076
**Layer:** `concrete (target when implemented)` — every element is note-level or stroke-level: one voice row carries the singer's pitches against a syllable grid; one percussion row carries the drummer's *buk* cycle; scene tags (jangdan, jo, aniri-ratio) are cell attributes. There is no abstract harmonic layer: pitch content is a mode (*jo*) plus melodic formulae, and "harmony" is absent by design (single melodic line + drum).
**Tradition:** Korean narrative sung-story (판소리), Honam/Jeolla region, 17th c. → present. Twelve *madang* codified by the 18th c.; five survive (Chunhyangga, Simcheongga, Heungbuga, Sugungga, Jeokbyeokga). Golden age 19th c. under patron-editor **Shin Jae-hyo** (1812–1884); schools (*je*) — Dongpyeonje, Seopyeonje, Junggoje; National Intangible Cultural Heritage No. 5 (1964); UNESCO Masterpiece 2003 / Representative List 2008.
**Primary elements:** STRUCTURE (madang → daemok scene chain, tempo-cycle ladder), RHYTHM (jangdan cycles, buchimsae text placement), PITCH (jo mode + melodic formulae + sigimsae ornaments), TEXTURE (solo voice + drum + shouts; extreme textural scarcity used as contrast), TEXT (saseol/changbon syllable grid — the generating layer).
**Related but distinct methods:** HC-017 (Korean *sanjo* jangdan improvisation — instrumental, no text, no narrative, no aniri/ballim, no madang), HC-070 (Carnatic kriti — text-first but fully notated with sangati variation and a violin/tambura ensemble), HC-056 (qawwali — devotional, harmonium, cyclic escalation), HC-044 (isicathamiya — a cappella choral blocks), HC-022 (twelve-bar blues — harmonic cycle, not a narrative scene chain), HC-067 (call-and-response antiphony — two-group alternation; pansori's *chuimsae* is interjection, not alternation), HC-004 (raga/tala — tala is a beat cycle without the gak-function dramaturgy and without a libretto).

---

## 1. What the method is

Pansori is a **three-to-eight-hour one-person musical drama**: a single singer (*sorikkun*) and a single drummer (*gosu*) with a barrel drum (*soribuk*), plus the audience's shouts (*chuimsae*). The singer does everything — narration, dialogue, every character, comedy, grief — by switching between three registers of delivery:

- **sori** — sung, measured by a *jangdan* cycle, carrying the emotional weight;
- **aniri** — spoken narration at speech pace, unmeasured, carrying plot and jokes;
- **ballim** — gesture/acting, timed to the rhythm;
- with **doseop** (also *dosa*) as the hybrid speech-song used for formal address, letters, and solemn pronouncements.

The **composition** — historically done by master singers, with literati patrons editing the text — is not "writing a tune." It is:

1. **Text first.** A libretto (*saseol*, in a singer's manuscript called a *changbon*) exists before the music. Yu Jin-han transcribed *Chunhyangga*'s text as early as 1754; Shin Jae-hyo rewrote and expanded texts in the 19th c. (Chunhyangga grew from roughly a three-hour evening to eight-plus hours).
2. **Scene architecture.** The story is cut into *daemok* (large scenes/anak). Each daemok gets a delivery mode (sori / aniri / doseop / ballim), an emotional function, and a **jangdan**.
3. **Rhythm assigns emotion, not just tempo.** Jangdan is chosen by dramatic state: *jinyangjo* for the vast, solemn or grieving; *jungmori* for narration and lyric reflection; *jungjungmori* for joy or keening; *jajinmori* for urgency and climax; *hwimori* for the frantic finish; *eotmori* for a monk, a general, a Taoist — special characters get an asymmetric 10-beat cycle.
4. **Mode assigns colour.** *Jo* is the melodic framework and, inseparably, the vocal timbre and affect: *ujo* (bright, do-centred) vs *gyemyeonjo* (plaintive, la-centred, defined by its descending slides).
5. **Melody is formula + ornament.** The singer works from phrase-formulae over the cycle and makes the line individual through *sigimsae* (jeonseong upper grace, toeseong descending slide, chuseong ascending slide, yoseong vibrato, kkekneun-eum pressed/breaking tone). In this tradition the ornament **is** the melody's identity.
6. **Words are fitted by buchimsae** — the craft of setting syllables against the drum cycle: *daemadi-daejangdan* (syllable squarely on the beat, "big joint, big rhythm") vs *eotbuchim* (deliberately displaced, syllables crossing the cycle's accents).
7. **Transmission is oral and one-to-one.** An apprentice learns a whole madang by ear from one master (*deureum*), imitates that master's *je* (school/style) exactly, and only later diverges into a personal style. The *changbon* is "famous" (tied to a named singer) or anonymous.

So the human method is: **libretto → scene cut → jangdan/jo assignment → phrase-formula melody with prescribed ornaments → syllable fitting (buchimsae) → deoneum insertions → rehearsal with the drummer → oral transmission with drift**.

---

## 2. Why this is not an algorithm

- **The text is the source, not the output.** An algorithm that generates notes and then bolts syllables on produces the opposite workflow.
- **Tempo cycles encode character and emotion.** There is no rule that says the monk's entrance must be *eotmori*; the tradition's practitioners decided, and the choice is the craft.
- **The melody's identity lives in micro-timing and timbre** (slides, vibrato width, pressed tone, husky *sori-seong*). Removing them leaves a correct-but-dead skeleton — the Korean objection to staff-notation-only transcriptions.
- **Ornament is not optional decoration.** In *gyemyeonjo*, the descending *toeseong* onto the cadential tone *is* what makes the mode that mode.
- **The drummer co-composes.** *Gosu* stroke choice and *chuimsae* shouts are improvised support; "one gosu, two master singers" is the proverb.
- **There is no single score.** Different singers' *changbon* differ substantially; the "work" is a family of versions.
- **Pitch is not fixed 12-TET.** Jo intonation is flexible and closer to just/pentatonic tuning than to equal temperament.

---

## 3. Craft procedure, step by step

### Step 0 — Choose (or inherit) the story and its text
Pick a madang from the repertoire or, historically, compose a new one (twelve existed; extra ones were lost when their changbon vanished). Obtain a *changbon*, or write/adapt the *saseol* in verse-and-prose mix. Mark which lines are singable verse and which are prose narration.

### Step 1 — Cut the story into daemok (scenes)
Break the madang into 6–12 large scenes, each with a dramatic function: exposition, journey, encounter, lament, trick, recognition, climax, denouement. Each scene gets a **target emotional state** and a **delivery mode**. Decide the sori/aniri ratio for the scene and for the whole madang — this ratio is a style marker (see Step 8).

### Step 2 — Assign a jangdan to each daemok
- **jinyangjo** — 24 beats per cycle = 4 *gak* × 6 beats; slowest. The four gak have grammatical functions: 1st *mineun sori* (pushing/opening), 2nd *daneun sori* (hanging/suspending), 3rd *maetneun sori* (binding/tying the phrase), 4th *puneun sori* (untying/releasing). The number of gak can expand when a phrase needs more room to bind and release. Used for the vast, solemn, or grieving (Chunhyangga "Jeokseongga", "Okjungga"; Simcheongga "Beompijungnyu").
- **jungmori** — 12 beats (notated 12/4), medium. Narrative and lyric reflection (Chunhyangga "Ssukdaemeori"; Heungbuga "Ganan-taryeong").
- **jungjungmori** — 12 beats, faster/heavier; joy, dance, or full-throated wailing (Simcheongga "Sim Bongsa tonggok"; Heungbuga "Jebi nojeonggi").
- **jajinmori** — 12 subdivisions grouped in threes = **4 beats per cycle**; fast, urgent, climactic (Chunhyangga "Eosa chuldo"; Simcheongga "Indangsu baram"; Jeokbyeokga "fire").
- **hwimori** — 4 beats (4/4 or 12/8), fastest; big first beat, hard stroke on the second half of beat 3. Frantic endings (Chunhyangga end of "Sinyeon maji"; Heungbuga "Heungbo bak taneun dae").
- **eotmori** — asymmetric **10 beats** (3+3+2+2): for special characters — the monk descending, the general, the Taoist (Simcheongga, Heungbuga, Jeokbyeokga, Sugungga each have one).
- **eotjungmori** — 6 beats, medium: formal address to a superior and closing scenes.

Plan the **cycle ladder** across the madang so that the drum's cycle shortens as tension rises; keep eotmori/eotjungmori as local character inserts, not rungs of the ladder.

### Step 3 — Assign jo and the phrase-formulae
Choose *ujo* (bright: sol–la–do–re–mi, cadencing on do or sol) or *gyemyeonjo* (plaintive: la–do–re–mi–sol, cadencing on la, with descending slides) per scene — or per emotional turn within a scene. Recall the melodic formulae appropriate to the jo and the jangdan (each jangdan has characteristic phrase shapes: jinyangjo's long arch with a suspension in gak 2, jajinmori's driving repeated-tone declamation).

### Step 4 — Compose the melodic line against the cycle
Sing the phrase over the drum cycle: place the phrase's structural tones on the cycle's functional beats, let the line bind at gak 3 and release at gak 4 (jinyangjo), and end on the jo's cadence tone. Use repetition of a short motif for narrative lists and accumulating action; vary the cadential formula to mark paragraph ends.

### Step 5 — Fit the words (buchimsae) — the signature craft step
Two settings, used deliberately in alternation:
- **daemadi-daejangdan** — one syllable lands squarely on each beat/anchor; clear, declamatory, typical of Dongpyeonje and of narrative drive.
- **eotbuchim** — syllables are displaced across the cycle (onset before or after the drum's accent, words straddling beats), producing a cross-rhythm between text and drum; typical of lyrical, ornamented Seopyeonje singing.

Check the prosody: Korean phrase-final syllables lengthen; long vowels carry the ornament; consonant clusters force a rhythmic break. A word split across a cycle boundary is a deliberate expressive device, not an error.

### Step 6 — Apply sigimsae and seong-eum
Write in the ornaments as required events, not as taste: *jeonseong* (upper grace before the main tone), *toeseong* (slide down into a tone from above — the gyemyeonjo marker), *chuseong* (slide up), *yoseong* (vibrato, width by emotion), *kkekneun-eum* (pressed/breaking tone at peaks). Decide vocal production: resonant *tongseong*, husky *sori-seong* (Song Man-gap's signature), or the "mok" colour appropriate to the character — the same line sung with a different mok is a different character.

### Step 7 — Insert deoneum (the singer's own additions)
Add signature phrases, extra descriptive passages, or a newly composed run — the part that makes a version belong to one singer. Historically these accretions are how madang grew from three hours to eight.

### Step 8 — Choose the je (school) and let it set the defaults
- **Dongpyeonje** (east of the Seomjingang: Unbong, Gurye, Sunchang) — vigorous, powerful, syllabic (*daemadi*), little aniri elaboration, straight natural volume; Song Man-gap, Park Dong-jin.
- **Seopyeonje** (Naju, Haenam, Boseong) — ornate, sorrowful, colourful, heavy ornament and much aniri; Kim So-hee, Ahn Sook-sun.
- **Junggoje** — middle register start, plain and clear, monotone-simple tune.

### Step 9 — Rehearse with the gosu
Sit with the drummer: fix the stroke pattern per jangdan (low *deong*, *kung*, *deok*, *ddak* — e.g. jungmori "deong gung ddak gung ddak ddakddak gung gung ddak guung gung"; jajinmori "deong kung kungdeokkung"; hwimori "deong deong kungdeok kung"), agree where the *chuimsae* shouts fall ("eolssigu!", "jotta!", "eolssu"), and how the drummer follows breath and tempo drift. Tempo is led by the singer's breath and the drummer's hand together — never by a metronome.

### Step 10 — Perform, and let the version drift
Full madang (3–8 h, sometimes ~10) or an excerpt set of famous numbers. Each performance is a state of a mutable object; the version stabilizes only when a changbon is written down or recorded.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Shin Jae-hyo** (1812–1884), patron-editor | The 19th-c. editorial mind of pansori: reworked and expanded the *saseol*, consolidated/created madang (notably *Jeokbyeokga*), fitted the repertoire to elite taste, and trained the first celebrated female master, **Jin Chae-seon**. Proof that pansori composition includes *literary* authorship. |
| **Song Man-gap** (1865–1939), Dongpyeonje | The canonical *sori-seong* (rough, powerful) voice; his 1934 recording of "Jingukmyeongsan" is a primary document of the style — syllabic, drum-locked, minimal ornament. |
| **Park Dong-jin** (1893–1970), Dongpyeonje | Carrier of the vigorous eastern school; the reference for *daemadi* setting and unadorned volume. |
| **Kim So-hee** (1917–1995), Seopyeonje | The 20th-c. Seopyeonje standard-bearer (*Simcheongga*); ornaments and aniri proportion at their most refined; designated human cultural asset. |
| **Ahn Sook-sun** (b. 1949), Seopyeonje | Living master of *Chunhyangga*; demonstrates the sori↔aniri switch as a single continuous dramatic instrument, and how a singer's *deoneum* personalizes inherited material. |
| **Jeong Jeong-ryeol, Kim Yeon-su, Park Nok-ju, Kim Soo-yeon** | Generational chain of designated holders — the oral-transmission mechanism itself: each version is a named changbon, not an edition. |
| **"Ssukdaemeori"** (*Chunhyangga*, jungmori) | Textbook jungmori lament: 12-beat cycle, descending gyemyeonjo formulae, syllable-anchored sobbing declamation. |
| **"Sim Bongsa tonggok"** (*Simcheongga*, jungjungmori) | Wailing at full voice — jungjungmori used for grief, not only joy; a check against tempo↔emotion shortcuts. |
| **"Eosa chuldo"** (*Chunhyangga*, jajinmori) | 4-beat-per-cycle urgency: the ladder's fast rung used for dramatic arrival, with text declaimed on repeated tones. |
| **The monk's entrance** (*Simcheongga* / *Heungbuga*, eotmori) | The asymmetric 10-beat cycle as *characterization*: a special figure gets a special metre, not a special melody. |
| **The gosu** (e.g. Kim Myung-hwan; historically Song Gwang-rok, Joo Duk-gi, Han Sung-jun) | Co-composer of the performance: stroke pattern, tempo support, and *chuimsae*. |
| **Audience chuimsae** | The third participant; shouts at cadences are part of the composed texture of a live pansori. |

**Listening:** Song Man-gap 1934 "Jingukmyeongsan"; Kim So-hee *Simcheongga* excerpts; Ahn Sook-sun *Chunhyangga* ("Sarangga", "Ssukdaemeori", "Eosa chuldo"); any complete *Heungbuga* for the jajinmori/hwimori finish.

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. Cells are real events: singer pitches on a syllable grid; drum strokes on a cycle grid. Tags (jangdan, jo, mode of delivery) are cell attributes; no harmonic layer is invented (a drone/octave doubling row is optional and non-structural).

**Voices (rows):**
- **V0 — Sorikkun (solo voice).** Monophonic line + syllable grid; per-section jo, register band (low chest ↔ high wailing), production tag (*tongseong* / *sori-seong*); ornaments as explicit grace/slide events (pitch-bend or short adjacent-tone pairs).
- **V1 — Buk (gosu drum).** One repeated cycle pattern per section: stroke accents on the cycle's functional beats (jinyangjo gak 1–4; jajinmori beat 3; hwimori beat 1 and beat-3 second half), with subdivision fills. Channel 9 percussion, low drum program.
- **V2 — Chuimsae (shouts).** Sparse short interjections at cadence tones/cycle boundaries: gosu ("eolssu", "jotta") and audience. Encoded as brief high-register pitched exclamations or a percussion/short-vocal row; density-capped.
- **V3 — Text/prosody metadata row (non-sounding).** Saseol syllables, buchimsae type per phrase, delivery tag (sori / aniri / doseop / ballim), scene function, jo, jangdan. This is the audit trail that makes the form readable.
- **V4 (optional) — changgeuk/arrangement expansion:** daegeum/piri doubling of V0, or a chorus for staged versions. Never required.

**Sections (columns)** = one *daemok* each, grouped into madang arcs:

| Cell | Scene function | Delivery | Jangdan | Jo |
|---|---|---|---|---|
| S0 | exposition / journey | aniri + doseop | free (no cycle) or eotjungmori | speech band |
| S1 | lyric reflection | sori | jinyangjo (24 = 4×6) | gyemyeonjo |
| S2 | encounter / dialogue | aniri ↔ sori alternation | jungmori (12) | ujo |
| S3 | comic/trick scene | aniri + ballim | jungjungmori (12) | ujo |
| S4 | lament | sori | jungjungmori or jinyangjo | gyemyeonjo |
| S5 | special character entrance | doseop → sori | **eotmori (10 = 3+3+2+2)** | ujo/gyemyeonjo mix |
| S6 | climax | sori | jajinmori (4 beats = 12 subdivisions) | ujo |
| S7 | denouement / finish | sori → aniri | hwimori (4) → eotjungmori (6) | ujo |

**Rules to encode:**
1. **Text-first gate:** every sounding cell must resolve to a syllable count from the saseol; sung events ≤ syllables except at cadence melisma; aniri cells must be marked non-metrical.
2. **Cycle lock:** section length = integer × cycle length (jinyangjo 24 beats, jungmori 12, jungjungmori 12, jajinmori 12 subdivisions = 4 beats, hwimori 4, eotmori 10, eotjungmori 6). No section may end mid-cycle.
3. **Gak-function rule (jinyangjo):** phrase opens on gak 1 (pushing), suspends at gak 2, binds at gak 3, releases at gak 4; a long phrase may occupy 2+ cycles but must bind/release at the cycle's gak 3/4.
4. **Tempo ladder gate:** within a madang, cycle duration decreases monotonically (jinyang → jungmori → jungjungmori → jajinmori → hwimori); jumps backwards only at scene boundaries and only with a new jo or a new character.
5. **Special-character rule:** eotmori (10-beat asymmetric) sections are permitted **only** when tagged with a special-character entrance; never used as a general fast tempo.
6. **Jo rule:** pitch set fixed per section — ujo {sol, la, do, re, mi} cadencing do/sol; gyemyeonjo {la, do, re, mi, sol} cadencing la. Any jo change must coincide with a section boundary or a tagged dramatic turn.
7. **Sigimsae rule (mode-defining, not decorative):** every gyemyeonjo cadence requires a *toeseong* descending slide into the cadential tone and ≥1 *kkekneun-eum* at the section peak; ujo phrases prefer *jeonseong* upper graces; *yoseong* width is a per-section parameter.
8. **Buchimsae rule:** alternate settings must be tagged. *daemadi* = syllable onsets on cycle anchors (±1/8 beat); *eotbuchim* = onsets offset 1/3–1/2 beat against the drum accent, with the drum unshifted (the cross-rhythm is the point). Require ≥1 eotbuchim passage per lyrical scene.
9. **Aniri proportion rule:** each scene declares an aniri:sori ratio; enforce it by tick budget (Dongpyeonje ≈ sori-dominant and syllabic; Seopyeonje ≈ more aniri and more ornament). Aniri maps to a narrow reciting band (2–3 pitches) with sparse or silent drum.
10. **Deoneum = declared open cells:** singer-added phrases are left unfilled by the composer pass and filled by a separate seeded "performer pass" (provenance recorded) — the oral-tradition equivalent of a cadenza slot.
11. **Chuimsae rule:** interjections only at cycle boundaries or immediately after a cadential tone; never over the attack of a sustained note; ≤1 per cycle.
12. **Zero-drift:** all rows end at the section terminal landmark; V0's final event is the cadence tone at the boundary; V1's cycle repeats to fill exactly; `validate()` must pass.

**Distinct in engine terms:** HC-017 (sanjo) runs the same jangdan vocabulary but as instrumental improvisation with no text row, no aniri, no scene narrative. HC-070 (kriti) is text-first but notated and ensemble-doubled with structured sangati variation. HC-076's distinguishing engine feature is the **three-way text/drum/voice grid** (syllables, cycle accents, melodic formulae) with a *declared mismatch* (eotbuchim) as a compositional value.

---

## 6. Quirks & pitfalls

- **Jangdan ≠ time signature.** It is a cycle with functionally named beats (gak) and genre-specific stroke patterns; 12 beats of jungmori and 12 subdivisions of jajinmori are not the same grid.
- **Jinyangjo is 24 beats = 4 gak × 6**, not a uniformly accented 24/4 bar. The gak functions (push/hang/bind/release) are the compositional grammar.
- **Eotmori is 10 beats, asymmetric (3+3+2+2)** — quantizing it to 4/4 destroys the character cue.
- **Aniri is not recitative.** It is speech at speech pace and its *proportion* is a school marker, not filler.
- **Jo is not a Western mode.** It bundles pitch set, ornament behaviour, timbre and affect; extracting only the scale yields a dead line.
- **Sigimsae are structural.** Removing slides/vibrato/pressed tones to "clean up" the MIDI removes the mode.
- **Tuning is not 12-TET.** jo intonation is flexible; document the approximation when rendering with a GM soundfont.
- **Pansori is not one style.** Dongpyeonje/Seopyeonje/Junggoje imply different aniri ratios, ornament density, and vocal production; pick a *je* and declare it.
- **No urtext.** Changbon differ by singer; cite the named version ("Song Man-gap changbon"), never "the score".
- **The drummer is a co-author.** A fixed drum loop is a reduction; leave the stroke-choice/chuimsae layer parameterized.
- **Scale of the form:** a madang is 3–8+ hours. Model a scene or a 3–5 scene arc in the engine; do not attempt a whole madang as a test.
- **Historical loss:** twelve madang existed; five survive. Do not present the five as the tradition's full extent.
- **Ballim is choreography** — it has no note events; keep it as a metadata tag rather than faking it with percussion.

---

## 7. References & verification

- Wikipedia, *Pansori* (raw wikitext fetched 2026-10-26): five style elements (jo, jangdan, buchimsae, je, vocal production); components aniri/ballim/chuimsae/doseop; twelve madang → five surviving; Yu Jin-han's 1754 Chunhyangga transcription; Shin Jae-hyo's editorial role and Jin Chae-seon; Dongpyeonje/Seopyeonje/Junggoje descriptions; Song Man-gap's 1934 "Jingukmyeongsan" recording; UNESCO 2003; Heritage No. 5 (1964).
- Korean Wikipedia, *장단* (raw wikitext fetched 2026-10-26): jinyangjo 24 beats = 4 gak × 6 with the four gak functions and variable gak count; jungmori 12/4 with gugum; jungjungmori 12; jajinmori 12/8 grouped as 4 beats with gugum; hwimori 4/4 or 12/8 with the beat-3 offbeat accent; eotmori 10 beats (3+2 mix) for monk/general/Taoist entrances; eotjungmori 6; buk gugum strings.
- Wikipedia, *Pansori gosu*: soribuk (shallow barrel drum, pine body, cowhide heads), chuimsae role, historical drummers.
- `HC-017` (sanjo) and `HC-024`/`HC-032` consulted for dedup.
