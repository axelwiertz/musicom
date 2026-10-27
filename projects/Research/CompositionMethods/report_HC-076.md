# report_HC-076 — Pansori Madang Composition: Sori / Aniri / Ballim Scene Architecture over Jangdan Cycles

**Job:** `daily-human-composition-research` · **Date:** 2026-10-26 · **Method ID:** HC-076
**Detail file:** `human_method_HC-076_pansori-madang-aniri-sori-jangdan-composition.md`

---

## 1. Header

| Field | Value |
|---|---|
| **Method name** | Pansori Madang Composition — Sori / Aniri / Ballim Scene Architecture over Jangdan Cycles (text-first narrative craft with *buchimsae* word-setting and *sigimsae* ornament) |
| **Tradition** | Korean pansori (판소리), Honam/Jeolla region, late 17th c. → present. Twelve *madang* codified by the 18th c.; five survive: **Chunhyangga, Simcheongga, Heungbuga, Sugungga, Jeokbyeokga**. Golden age 19th c. under patron-editor **Shin Jae-hyo** (1812–1884). Schools (*je*): **Dongpyeonje** (vigorous, syllabic, sori-dominant), **Seopyeonje** (ornate, sorrowful, aniri-rich), **Junggoje** (plain, middle-register). National Intangible Cultural Heritage No. 5 (1964); UNESCO Masterpiece of Oral and Intangible Heritage (2003), Representative List (2008). |
| **Layer** | `concrete (target when implemented)` — cells hold real events: singer pitches on a syllable grid, drum strokes on a cycle grid; jangdan/jo/delivery-mode are cell attributes. No harmonic layer is composed (a single melody + one drum is the whole texture). |
| **Primary elements** | STRUCTURE (madang → daemok scene chain, tempo-cycle ladder), RHYTHM (jangdan cycles, buchimsae word placement), PITCH (jo mode + formulae + sigimsae), TEXTURE (voice/drum/shout scarcity as contrast), TEXT (saseol syllable grid — the generating layer) |
| **Why human craft, not algorithm** | The libretto precedes the music; jangdan choice encodes *character and emotion*, not tempo arithmetic; the melody's identity resides in micro-timing/timbre (slides, vibrato width, pressed tone) rather than pitch selection; the drummer *co-composes*; there is no urtext — each version is a named *changbon*. |
| **Research sources (fetched 2026-10-26)** | Wikipedia *Pansori* (raw wikitext): five style elements — *jo*, *jangdan*, *buchimsae*, *je*, vocal production; components *sori/aniri/ballim/chuimsae/doseop*; twelve→five madang; Yu Jin-han's 1754 Chunhyangga transcription; Shin Jae-hyo and Jin Chae-seon; Dongpyeonje/Seopyeonje/Junggoje descriptions; Song Man-gap's 1934 "Jingukmyeongsan" recording; Heritage No. 5 / UNESCO dates. Korean Wikipedia *장단* (raw wikitext): jinyangjo = 24 beats = 4 *gak* × 6 with named gak functions and variable gak count; jungmori 12/4 with gugum; jungjungmori 12; jajinmori 12/8 grouped as 4 beats with gugum; hwimori 4/4 or 12/8 with the beat-3 offbeat accent; eotmori 10 beats (3+2 mix) for monk/general/Taoist entrances; eotjungmori 6; buk stroke syllables. Wikipedia *Pansori gosu*: soribuk construction and chuimsae role. |

**Distinct from existing HC methods:**
- **HC-017 (sanjo jangdan improvisation)** — same jangdan vocabulary, but instrumental, untexted, non-narrative, no aniri/ballim, no madang scene chain. (Checked first; this is the closest neighbour and the reason the dedup note below exists.)
- **HC-070 (Carnatic kriti)** — text-first composition, but fully notated, ensemble-doubled, with structured *sangati* variation.
- **HC-056 (qawwali)** — devotional escalation with harmonium and cyclic intensification; narrative drama absent.
- **HC-044 (isicathamiya)** — a cappella choral block craft; no solo narrator, no drum cycle.
- **HC-022 (twelve-bar blues)** — a *harmonic* cycle; pansori has no chord layer at all.
- **HC-067 (call-and-response)** — two-group alternation; pansori's *chuimsae* is interjection, not antiphony.
- **HC-004 (raga/tala)** — tala is a beat cycle; it lacks the gak-function dramaturgy (push/hang/bind/release) and the libretto.
- **HC-075 (solita forma)** — set-piece chain driven by a character's emotional state, but tonal-harmonic, orchestral, and notated; pansori's chain is driven by *narrative scene function* and realized with one voice plus one drum.

**Deduplication note:** the obvious Korean candidates were checked before writing. HC-017 covers *sanjo* (instrumental jangdan cycles), so the pansori draft was kept strictly on the **narrative, text-first, sung-story** side (aniri/sori ratio, buchimsae, madang scene cutting) rather than on jangdan improvisation as such. HC-017's jangdan/jo vocabulary is cited as shared context, not re-documented.

---

## 2. What the method is

Pansori is a one-person musical drama lasting three to eight hours (occasionally ~10): a singer (*sorikkun*) and a drummer (*gosu*) with a barrel drum (*soribuk*), plus audience shouts (*chuimsae*). The singer narrates, portrays every character, and switches between three delivery registers:

- **sori** — sung, measured against a *jangdan* cycle, carrying the emotional load;
- **aniri** — spoken narration at speech pace, unmeasured, carrying plot and comedy;
- **ballim** — gesture/acting, timed to the rhythm;
- with **doseop** (*dosa*) as the speech-song hybrid for formal address, letters, and solemn pronouncements.

Composition in this tradition means, in order: **text → scene cut → jangdan/jo assignment → formula-based melody with prescribed ornaments → syllable fitting → personal insertions → rehearsal with the drummer → oral transmission.** Historically master singers composed, with literati patrons editing: Yu Jin-han transcribed *Chunhyangga*'s text in 1754; Shin Jae-hyo rewrote and expanded the *saseol* in the 19th c., and *Chunhyangga* grew from roughly a three-hour evening to eight-plus hours.

The five codified style elements (per the National Gugak Center formulation) are *jo* (melodic framework incl. timbre and affect), *jangdan* (rhythmic cycle), *buchimsae* (how words are joined to melody), *je* (school/style), and vocal production (*seong-eum*, *mok*).

**The central insight for a composition engine:** pansori's "form" is a **scene chain plus a tempo-cycle ladder**, its "melody" is a **formula dressed in obligatory micro-ornament**, and its "rhythm" is a **three-way grid** — syllables, drum accents, melodic phrasing — that is *deliberately allowed to disagree* (*eotbuchim*).

---

## 3. Craft procedure in detail

### Step 0 — Choose or inherit the story; secure a text
Pick a surviving madang or compose a new one (twelve existed; madang were lost when their changbon vanished). Obtain a *changbon*, or write/adapt the *saseol* (verse-and-prose mix). Distinguish singable verse from prose narration before any music exists.

### Step 1 — Cut the story into daemok (scenes)
Six to twelve large scenes, each with a dramatic function: exposition, journey, encounter, lament, trick/recognition, climax, denouement. Each scene gets a **target emotional state**, a **delivery mode** (sori / aniri / doseop / ballim), and an **aniri:sori ratio** — a school marker in itself.

### Step 2 — Assign a jangdan per scene (rhythm chooses the emotion)
- **jinyangjo** — 24 beats per cycle = **4 *gak* × 6 beats**; slowest. The gak carry grammatical functions: 1st *mineun sori* (pushing/opening), 2nd *daneun sori* (hanging/suspending), 3rd *maetneun sori* (binding/tying), 4th *puneun sori* (untying/releasing). The gak count may expand when a phrase needs more room to bind and release. For the vast, solemn, grieving (Chunhyangga "Jeokseongga", "Okjungga"; Simcheongga "Beompijungnyu").
- **jungmori** — 12 beats (12/4), medium; narration and lyric reflection (Chunhyangga "Ssukdaemeori"; Heungbuga "Ganan-taryeong"). Buk gugum: "deong gung ddak gung ddak ddakddak gung gung ddak guung gung".
- **jungjungmori** — 12 beats, heavier/faster; joy, dance, or full-throated keening (Simcheongga "Sim Bongsa tonggok"; Heungbuga "Jebi nojeonggi").
- **jajinmori** — 12 subdivisions grouped in threes = **4 beats per cycle**; driving, urgent, climactic (Chunhyangga "Eosa chuldo"; Simcheongga "Indangsu baram"; Jeokbyeokga fire scene). Gugum: "deong kung kungdeokkung".
- **hwimori** — 4 beats (4/4 or 12/8), fastest; big first beat, hard stroke on the second half of beat 3; frantic finishes (Heungbuga "Heungbo bak taneun dae"). Gugum: "deong deong kungdeok kung".
- **eotmori** — asymmetric **10 beats (3+3+2+2)**: exclusively for special characters — the monk descending, the general, the Taoist (one each in Simcheongga, Heungbuga, Jeokbyeokga, Sugungga).
- **eotjungmori** — 6 beats, medium: formal address to a superior, and closing scenes.

Plan a **cycle ladder** across the madang: the drum's cycle shortens as tension rises. eotmori/eotjungmori are *local inserts*, never rungs of the ladder.

### Step 3 — Assign jo and its phrase formulae
*Ujo* = bright, sol–la–do–re–mi, cadencing on do or sol. *Gyemyeonjo* = plaintive, la–do–re–mi–sol, cadencing on la, and defined by descending slides. Each jangdan has characteristic phrase shapes (jinyangjo's long arch with a suspension in gak 2; jajinmori's repeated-tone declamation).

### Step 4 — Compose the line against the cycle
Structural tones on the cycle's functional beats; in jinyangjo the phrase **binds at gak 3 and releases at gak 4**; cadence on the jo's tone. Repetition of a short motif for lists and accumulating action; varied cadential formula to mark paragraph ends.

### Step 5 — Fit the words (buchimsae) — the signature step
- **daemadi-daejangdan** — one syllable squarely on each beat/anchor; declamatory, narrative drive; characteristic of Dongpyeonje.
- **eotbuchim** — syllables displaced across the cycle (onsets before or after the drum accent; words straddling beats), producing a text–drum cross-rhythm; characteristic of lyrical, ornamented Seopyeonje singing.

Prosody gate: Korean phrase-final syllables lengthen; long vowels carry the ornament; consonant clusters force a rhythmic break. A word split across a cycle boundary is expressive, not an error.

### Step 6 — Apply sigimsae and choose seong-eum
Ornaments are written as **required events**, because they define the mode: *jeonseong* (upper grace before the main tone), *toeseong* (slide down into a tone from above — the gyemyeonjo marker), *chuseong* (ascending slide), *yoseong* (vibrato, width set by emotion), *kkekneun-eum* (pressed/breaking tone at peaks). Then choose the timbre: resonant *tongseong*, husky *sori-seong* (Song Man-gap's signature), or a character's *mok*. The same line in a different mok is a different character.

### Step 7 — Insert deoneum
The singer's own added phrases and descriptive passages — how the madang grew from three hours to eight, and how one singer's version becomes identifiable.

### Step 8 — Let the je set the defaults
Dongpyeonje: vigorous, powerful, syllabic, little aniri elaboration, straight natural volume (Song Man-gap, Park Dong-jin). Seopyeonje: ornate, sorrowful, colourful, heavy ornament with much aniri (Kim So-hee, Ahn Sook-sun). Junggoje: middle-register start, plain and clear, simple tune.

### Step 9 — Rehearse with the gosu
Fix the stroke pattern per cycle and the *chuimsae* points; agree how the drummer follows breath and tempo drift. Tempo is led by breath and hand together — never by a metronome. The proverb "one gosu, two master singers" states the drummer's co-authorship.

### Step 10 — Perform; let the version drift
Full madang (3–8 h) or an excerpt programme of famous numbers. The version stabilizes only when a changbon is written down or a recording fixes it.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Shin Jae-hyo** (1812–1884) | The 19th-c. editorial mind: reworked and expanded the *saseol*, consolidated madang (notably *Jeokbyeokga*), fitted the repertoire to elite taste, and trained **Jin Chae-seon**, the first celebrated female master. Proves the method includes literary authorship. |
| **Song Man-gap** (1865–1939), Dongpyeonje | Canonical *sori-seong* (rough, powerful) voice; 1934 recording of "Jingukmyeongsan" — syllabic, drum-locked, minimal ornament. |
| **Park Dong-jin** (1893–1970), Dongpyeonje | Reference for *daemadi* setting and unadorned natural volume. |
| **Kim So-hee** (1917–1995), Seopyeonje | 20th-c. Seopyeonje standard (*Simcheongga*); ornament and aniri proportion at their most refined; designated human cultural asset. |
| **Ahn Sook-sun** (b. 1949), Seopyeonje | Living master of *Chunhyangga*; the sori↔aniri switch as one continuous dramatic instrument, and *deoneum* as personalization of inherited material. |
| **Jeong Jeong-ryeol, Kim Yeon-su, Park Nok-ju, Kim Soo-yeon** | The generational chain — the oral-transmission mechanism itself: each version is a named changbon, not an edition. |
| **"Ssukdaemeori"** (Chunhyangga, jungmori) | Textbook lament: 12-beat cycle, descending gyemyeonjo formulae, syllable-anchored sobbing declamation. |
| **"Sim Bongsa tonggok"** (Simcheongga, jungjungmori) | Full-voice wailing — jungjungmori for *grief*, not only joy; blocks tempo↔mood shortcuts. |
| **"Eosa chuldo"** (Chunhyangga, jajinmori) | The ladder's fast rung used for dramatic arrival; text declaimed on repeated tones over a 4-beat cycle. |
| **The monk's entrance** (Simcheongga / Heungbuga, eotmori) | Asymmetric 10-beat cycle as *characterization*: a special figure gets a special metre, not just a special melody. |
| **The gosu** (Kim Myung-hwan; historically Song Gwang-rok, Joo Duk-gi, Han Sung-jun) | Co-composer: stroke pattern, tempo support, *chuimsae*. |
| **Audience chuimsae** | Third participant; shouts at cadences are part of the composed texture of live pansori. |

**Listening:** Song Man-gap 1934 "Jingukmyeongsan"; Kim So-hee *Simcheongga* excerpts; Ahn Sook-sun *Chunhyangga* ("Sarangga", "Ssukdaemeori", "Eosa chuldo"); a complete *Heungbuga* for the jajinmori→hwimori finish.

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. Cells are real events; tags ride on cells. No chord layer is invented.

**Voices (rows):**
- **V0 — Sorikkun (solo voice).** Monophonic line + syllable grid; per-section jo, register band, production tag (*tongseong* / *sori-seong*); ornaments as explicit grace/slide events (pitch-bend or short adjacent-tone pairs).
- **V1 — Buk (gosu drum).** One repeated cycle pattern per section with accents on the cycle's functional beats (jinyangjo gak 1–4; jajinmori beat 3; hwimori beat 1 and the beat-3 second half) plus subdivision fills. Channel 9 percussion, low drum.
- **V2 — Chuimsae (shouts).** Sparse short interjections at cadence tones/cycle boundaries (gosu: "eolssu", "jotta"; audience). Brief high-register events or a percussion row; density-capped.
- **V3 — Text/prosody metadata row (non-sounding).** Saseol syllables, buchimsae type per phrase, delivery tag, jo, jangdan, scene function — the audit trail.
- **V4 (optional) — arrangement/changgeuk expansion:** daegeum/piri doubling or chorus. Never required; the method is complete with V0+V1.

**Sections (columns)** = one *daemok* each, grouped into madang arcs:

| Cell | Scene function | Delivery | Jangdan | Jo |
|---|---|---|---|---|
| S0 | exposition / journey | aniri + doseop | free (no cycle) or eotjungmori | speech band |
| S1 | lyric reflection | sori | jinyangjo (24 = 4×6) | gyemyeonjo |
| S2 | encounter / dialogue | aniri ↔ sori | jungmori (12) | ujo |
| S3 | comic / trick scene | aniri + ballim | jungjungmori (12) | ujo |
| S4 | lament | sori | jungjungmori or jinyangjo | gyemyeonjo |
| S5 | special-character entrance | doseop → sori | **eotmori (10 = 3+3+2+2)** | mixed |
| S6 | climax | sori | jajinmori (12 subdivisions = 4 beats) | ujo |
| S7 | denouement / finish | sori → aniri | hwimori (4) → eotjungmori (6) | ujo |

**Rules to encode:**
1. **Text-first gate** — every sounding cell resolves to a syllable count from the saseol; sung events ≤ syllables except cadence melisma; aniri cells flagged non-metrical.
2. **Cycle lock** — section length = integer × cycle length (24 / 12 / 12 / 12-subdiv / 4 / 10 / 6 beats); no section may end mid-cycle.
3. **Gak-function rule (jinyangjo)** — open (push) on gak 1, suspend on gak 2, bind on gak 3, release on gak 4; long phrases may span 2+ cycles but must bind/release at gak 3/4.
4. **Tempo ladder gate** — cycle duration decreases monotonically within a madang arc (jinyang → jungmori → jungjungmori → jajinmori → hwimori); reversals only at scene boundaries with a new jo or new character.
5. **Special-character rule** — eotmori only on cells tagged with a special-character entrance; never a general fast tempo.
6. **Jo lock** — ujo {sol, la, do, re, mi} cadencing do/sol; gyemyeonjo {la, do, re, mi, sol} cadencing la; jo changes only at section boundaries or tagged dramatic turns.
7. **Sigimsae rule (mode-defining)** — every gyemyeonjo cadence requires a *toeseong* slide into the cadential tone and ≥1 *kkekneun-eum* at the section peak; ujo prefers *jeonseong*; *yoseong* width is a per-section parameter.
8. **Buchimsae rule** — settings are tagged. *daemadi*: onsets on cycle anchors (±1/8 beat). *eotbuchim*: onsets offset 1/3–1/2 beat against the unshifted drum accent. Require ≥1 eotbuchim passage per lyrical scene.
9. **Aniri-proportion rule** — each scene declares an aniri:sori tick budget (Dongpyeonje sori-dominant; Seopyeonje aniri-rich); aniri maps to a 2–3-pitch reciting band with sparse or silent drum.
10. **Deoneum = declared open cells** — left unfilled by the composer pass, filled by a separate seeded performer pass with provenance.
11. **Chuimsae rule** — only at cycle boundaries or immediately after a cadential tone; never over a sustained note's attack; ≤1 per cycle.
12. **Zero-drift** — every row ends at the section terminal landmark; V0's last event is the cadence tone at the boundary; V1's cycle repeats to fill exactly; `validate()` must pass.

**Distinct in engine terms:** HC-017 runs the same jangdan vocabulary as *instrumental improvisation* with no text row, no aniri, no narrative. HC-070 is text-first but notated and ensemble-doubled. HC-076's unique engine feature is the **three-way grid** (syllables / drum accents / melodic formulae) with a *declared mismatch* (eotbuchim) treated as compositional value.

---

## 6. Table row added to `human_methods_db.md`

```markdown
| HC-076 | human (→concrete) | Pansori Madang Composition — Sori / Aniri / Ballim Scene Architecture over Jangdan Cycles (Text-First Narrative Craft with Buchimsae Word-Setting and Sigimsae Ornament) | Korean pansori — Honam/Jeolla, 17th c.→present; twelve *madang* codified by the 18th c., five survive (Chunhyangga, Simcheongga, Heungbuga, Sugungga, Jeokbyeokga); 19th-c. golden age under patron-editor Shin Jae-hyo (1812–1884); schools Dongpyeonje (vigorous, syllabic) / Seopyeonje (ornate, sorrowful) / Junggoje (plain, middle-register); National Intangible Heritage No. 5 (1964), UNESCO Masterpiece 2003 | STRUCTURE, RHYTHM, PITCH, TEXTURE, TEXT (prosody) | Text first (obtain/write the *saseol* libretto, a singer's copy = *changbon*) → cut the story into *daemok* scenes and tag each with a delivery mode (sori sung / aniri speech / doseop speech-song / ballim gesture) and an emotional function → assign a **jangdan** cycle per scene by affect (jinyangjo 24 beats = 4 *gak* × 6 with push/hang/bind/release functions, for the vast and grieving; jungmori 12 for narration and lyric; jungjungmori 12 for joy or keening; jajinmori 12 subdivisions grouped as 4 beats for urgency and climax; hwimori 4 for the frantic finish; **eotmori 10 (3+3+2+2)** only for special characters — monk, general, Taoist; eotjungmori 6 for formal address and endings), planning a **tempo ladder** that shortens the cycle as tension rises → assign **jo** (ujo bright, sol–la–do–re–mi cadencing do/sol; gyemyeonjo plaintive, la–do–re–mi–sol cadencing la) and its phrase formulae → compose the line over the cycle: structural tones on functional beats, phrase binds at gak 3 / releases at gak 4, cadence on the jo's tone → fit syllables by **buchimsae** (daemadi-daejangdan = syllable squarely on the beat; eotbuchim = onsets displaced across the drum accent, text–rhythm cross-accent as an expressive value) → apply **sigimsae** as required, mode-defining events (jeonseong upper grace, toeseong descending slide at gyemyeonjo cadences, chuseong ascending slide, yoseong vibrato, kkekneun-eum pressed tone at peaks) and choose vocal production (*tongseong* resonant vs *sori-seong* husky) → insert **deoneum** (the singer's own added phrases — how madang grew from ~3 to 8+ hours) → rehearse with the **gosu** drummer: fix the buk stroke pattern per cycle and the *chuimsae* shout points, tempo led by breath and hand, not metronome → transmit orally 1:1 (learn a whole madang by ear, imitate the master's *je*, diverge later); no urtext, each version is a named changbon | One singer row (V0: melody + syllable grid, per-section jo, register band, ornament events) + one drum row (V1: buk cycle pattern, accents on gak/beat function, channel 9) + sparse chuimsae row (V2: shouts only at cycle boundaries or after cadence tones) + non-sounding text/metadata row (V3: syllables, buchimsae type, delivery tag, jo, jangdan, scene function); sections = daemok columns (S0 aniri exposition → S1 jinyangjo lament → S2 jungmori dialogue → S3 jungjungmori comic → S4 gyemyeonjo lament → S5 eotmori special-character entrance → S6 jajinmori climax → S7 hwimori finish); rules: text-first gate (every event resolves to a syllable; aniri marked non-metrical), cycle lock (section = integer × cycle; no mid-cycle ending), jinyangjo gak-function rule, monotonic tempo ladder, eotmori only for tagged special characters, jo pitch-set lock with boundary-only changes, mode-defining ornament rule, buchimsae tags with required eotbuchim passage, aniri:sori tick-budget ratio per *je*, deoneum as declared open cells filled in a separate seeded performer pass, chuimsae ≤1/cycle, zero-drift validate() | Shin Jae-hyo (1812–1884, reworked/expanded the saseol, consolidated Jeokbyeokga, trained Jin Chae-seon, the first celebrated female master); Song Man-gap (1865–1939, Dongpyeonje, *sori-seong* rough voice; 1934 recording "Jingukmyeongsan"); Park Dong-jin (1893–1970, Dongpyeonje, *daemadi* setting); Kim So-hee (1917–1995, Seopyeonje standard, *Simcheongga*); Ahn Sook-sun (b. 1949, Seopyeonje *Chunhyangga*, sori↔aniri as one instrument); repertoire: "Ssukdaemeori" (Chunhyangga, jungmori lament), "Sim Bongsa tonggok" (Simcheongga, jungjungmori grief), "Eosa chuldo" (Chunhyangga, jajinmori urgency), the monk's entrance in eotmori; the gosu (Kim Myung-hwan; historically Song Gwang-rok, Joo Duk-gi) as co-composer | ✅ Documented |
```

---

## 7. Verification & next free ID

- Detail file: `human_method_HC-076_pansori-madang-aniri-sori-jangdan-composition.md` — 22,980 bytes, contains `HC-076` ✓ (3 occurrences)
- DB table: `human_methods_db.md` — row `| HC-076 |` appended as line 82 (81 → 82 lines); `grep -c '^| HC-076 '` = **1** (no duplicate) ✓
- Row shape: line 82 splits into **11 `|`-fields = 9 cells**, matching the header `| Method ID | Layer | Method Name | Tradition / Culture | Primary Elements | Craft Process | UnitMatrix Mapping | Real Practitioner Example | Status |` ✓
- Report: this file, `report_HC-076.md` ✓
- Max existing ID after append = **HC-076** → **Next free ID: HC-077**

```bash
grep -c "HC-076" human_method_HC-076_pansori-madang-aniri-sori-jangdan-composition.md   # 3 ✓
grep -c '^| HC-076 ' human_methods_db.md                                                 # 1 ✓
awk 'NR==82' human_methods_db.md | awk -F'|' '{print NF}'                               # 11 (9 cells) ✓
```

---

## 8. Quirks & pitfalls

- **Jangdan ≠ time signature.** It is a cycle with functionally named beats (*gak*) and genre-specific stroke patterns; 12 beats of jungmori and 12 subdivisions of jajinmori are different grids.
- **Jinyangjo is 24 beats = 4 gak × 6**, not a uniformly accented 24/4 bar. The gak functions (push/hang/bind/release) are the compositional grammar — and the gak count varies with the phrase, so the cycle is not rigid.
- **Eotmori is 10 beats, asymmetric (3+3+2+2).** Quantizing it to 4/4 destroys a character cue.
- **Aniri is not recitative.** It is speech at speech pace, unmeasured, and its *proportion* is a school marker — not filler to be minimized.
- **Jo is not a Western mode.** Pitch set + ornament behaviour + timbre + affect travel together; extracting the scale yields a dead line.
- **Sigimsae are structural.** Stripping slides/vibrato/pressed tones to "clean" the MIDI removes the mode itself.
- **Tuning is not 12-TET.** Jo intonation is flexible; document the approximation when rendering with a GM soundfont.
- **Pansori is not one style.** Dongpyeonje (vigorous, syllabic, sori-dominant), Seopyeonje (ornate, aniri-rich), Junggoje (plain) change aniri ratio, ornament density, and vocal production. Declare the *je*.
- **No urtext.** Changbon differ by singer; cite the named version ("Song Man-gap changbon"), never "the score".
- **The drummer is a co-author.** A fixed drum loop is a reduction; keep stroke choice and chuimsae parameterized.
- **Scale:** a madang runs 3–8+ hours. Model a scene or a 3–5 scene arc; never a whole madang as an engine test.
- **Historical loss:** twelve madang existed, five survive — do not present five as the tradition's full extent.
- **Ballim has no note events.** Keep it a metadata tag; don't fake it with percussion.
- **Dedup lesson:** the closest neighbour is HC-017 (*sanjo*), which shares jangdan/jo vocabulary but not the text-first narrative method; state the boundary explicitly in any future Korean-music entry.
