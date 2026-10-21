# Report HC-070 — Carnatic Kriti Composition: Sangati-Built Sahitya Architecture

**Date:** 2026-10-20
**Job:** daily-human-composition-research (autonomous cron)
**Method ID:** HC-070 (resolved dynamically: max existing was HC-069; detail files and DB table agreed; no duplicate)
**Layer:** `concrete (target when implemented)` — human craft resolving directly into UnitMatrix cells
**Status:** ✅ Documented

---

## 1. Method identity

| Field | Value |
|---|---|
| Name | Carnatic Kriti Composition — Sangati-Built Sahitya Architecture |
| Subtitle | Pallavi–Anupallavi–Charanam form with progressive phrase variation (sangati) |
| Tradition | South Indian Carnatic classical — Tamil Nadu / Andhra Pradesh |
| Historical span | 15th c. (Purandara Dasa) → Trinity (Tyagaraja 1767–1847, Dikshitar 1776–1835, Syama Sastri 1762–1827) → living tradition |
| Primary elements | STRUCTURE, PITCH, RHYTHM, TEXTURE |
| Secondary | HARMONY only as drone (Sa–Pa), no functional progression |
| Language | Telugu, Sanskrit, Tamil, Kannada, Manipravalam |
| Rotation check | Not previously covered. HC-004 covers *improvised* raga-tala architecture (alapana/niraval/kalpana svara); HC-070 is the composed, taught artifact and its variation engine. Nearest neighbours: HC-015 (shape-note), HC-065 (Thai thang elaboration) — different mechanism, different culture. |

---

## 2. Layer classification and rationale

Tagged `layer: concrete (target when implemented)`.

Carnatic kriti composition is not an abstract schema that must be realised by a separate theory layer: the composer works directly in **named raga phrases × named tala cycles × fixed syllables**, and the output is concrete pitch-and-duration material per section. The UnitMatrix is therefore the natural target — rows for the ensemble, columns for form units, cells holding svara events. The "abstract" content (raga grammar, tala hierarchy, prosody) lives as *rules* over those cells, not as a separate layer object.

---

## 3. The craft procedure (full)

### 3.1 Frame selection (before any melody)
1. **Raga** chosen for devotional affect (*bhava*) and for what it lets the composer display: ascent/descent, characteristic *sanchāras*, *jeeva svaras*, gamaka habits.
2. **Tala**: Adi (8 aksharas, 4+2+2), Rupaka (6, 2+4), Misra Chapu (7, 3+4), Khanda Chapu (5, 2+3), Ata (14).
3. **Eduppu** (start point relative to the cycle):
   - *Samam* — on beat 1. Example: *Vatapi Ganapatim* (Dikshitar, Hamsadhwani, Rupaka).
   - *Atita / atheetha* — starts before beat 1, in the previous cycle's last aksharas. Example commonly cited: *Sivakama Sundari* (Mukhari), one beat early.
   - *Anagata* — starts after beat 1, a deliberate delayed entry.
4. **Tempo**: chowka (very slow) / vilamba / madhya. Dikshitar's kritis are characteristically chowka kala.
5. **Language + text source + mudra** (Tyagaraja, Guruguha, Syama Krishna).

### 3.2 Sahitya (text) first
- Pallavi: 1–2 lines, self-contained refrain/thesis.
- Anupallavi: 2 lines, heightening or contrast, often a question.
- Charanam: longer, 2–4 lines, narrative/accumulative, **mudra on the last line**.
- Prosody enforced: **prasa** (second-syllable rhyme), **anuprasa** (alliteration), **yati** (caesura aligned to the tala's internal divisions). Syllable budget is fixed by the tala; a line that fights the caesura is rewritten.

### 3.3 Pallavi core phrase
Sing the line until a core phrase exists that (a) opens on a raga-identifying note, often a jeeva svara; (b) arcs to a **landing note on a strong akshara = arudi**; (c) fits the syllables; (d) leaves headroom above and below for variants.

### 3.4 Sangati chain — the compositional engine
Repeat the **same words**; change **one dimension per pass**; keep the **arudi** and the **span** fixed.

Operators: **RANGE↑/↓**, **DENSITY** (double svara count per syllable; first→second speed), **PATH** (vakra zig-zag or alternate sanchara to the same landing), **START-SHIFT** (begin on a different akshara, e.g. anagata), **EMPHASIS** (move gamaka weight to another jeeva svara, lengthen a syllable), **REGISTER** (octave displacement, usually reserved for anupallavi).

Discipline: 2–6 passes typical (exceptionally 10–11); cumulative order; final pass most elaborate and must deliver a clean arudi; always tested against a clapped tala.

**Hard invariants:** same lyric, same arudi (svara + metric position), same span in aksharas, same raga, same section function. Violating the arudi turns the passage into *niraval* (improvisation), not sangati.

### 3.5 Anupallavi
Same procedure one register up: higher tessitura, often broader phrasing (fewer syllables per akshara), new sancharas, open/half-cadential ending that makes the pallavi return feel necessary. Omitted in samashti-charanam kritis (Dikshitar, Venkata Kavi).

### 3.6 Charanam
Longer lines; register settles mid/low for relief; often a rhythmic reset (fresh eduppu feel); builds to the mudra line set memorably. Optional **madhyamakala sahitya**: same tala, syllables delivered at double speed. Multiple charanams possible; each returns to the pallavi.

### 3.7 Chittaswara (optional)
Textless solfa passage in the same raga and tala, normally second speed, built from signature sancharas; a fixed cadential flourish after anupallavi or charanam, then pallavi resumes.

### 3.8 Whole-form audit
1. Raga fidelity: legal sancharas, jeeva svaras touched and ornamented.
2. Tala arithmetic: whole āvartanas (or declared eduppu), arudi placement, madhyamakala does not disturb the cycle.
3. Text underlay: singable at tempo, caesura correct, prasa intact.
4. Register arch: pallavi mid → anupallavi high → charanam mid/low → mudra close.
5. Return path: each section's last note leads back to the pallavi's first.
6. Invention scale: enough sangatis to teach the raga, not so many it becomes an etude.

### 3.9 Notation and transmission
Svara notation with sahitya written beneath, plus lineage-specific gamaka shorthand (oscillation/slide marks). Notation is deliberately incomplete: gamaka, phrasing, tempo nuance pass orally. The fixed skeleton is the frame for performance-time niraval and kalpana svara.

---

## 4. Practitioner examples

- **Tyagaraja** — credited with making sangati structural in the kriti's sahitya; graded chains of variants always returning to the same landing. Corpus: *Endaro Mahanubhavulu* (Sri, Adi), Pancharatna kritis (*Jagadanandakaraka* Nata; *Dudukugala* Gowla; *Saadhinchene* Arabhi; *Kana Kana Ruchira* Varali; *Endaro*). His *Nadhasudha* text ("sarasa sangati sandarbhamu…") frames sangati as apt, occasioned modulation — rhetorical, not mechanical.
- **Muthuswami Dikshitar** — chowka kala, veena-style gamaka, Sanskrit; charanam closing with madhyamakala sahitya; mudra "Guruguha"; *Vatapi Ganapatim* (Hamsadhwani, Rupaka, samam) as the standard form lesson; *Kamalamba Navavarna* cycle as architectural planning; frequent samashti charanam (no anupallavi).
- **Syama Sastri** — slower/denser, tala-foregrounding; swarajatis studied for phrase-to-cycle discipline.
- **Oothukkadu Venkata Kavi** — formal experiment: multiple charanams, speed/gati contrast, sahitya-sangati (variation carried by words as well as tune), sectional partitioning.
- **Purandara Dasa** — graded pedagogy (svaravali → alankara → geete → kriti); the kriti as teaching vehicle.
- **Modern** — M. Balamuralikrishna (kritis in self-created ragas), Lalgudi Jayaraman (varnams; eduppu and second-speed architecture).

---

## 5. UnitMatrix mapping

### Voices (rows)
| Row | Voice | Role | Rule |
|---|---|---|---|
| 0 | Sahitya (voice/venu/veena) | all composed melody | kriti lines + sangatis + chittaswara |
| 1 | Anusvarana (violin/sarangi) | unison shadow | same pitches, slight onset delay; **not** harmony |
| 2 | Tambura | drone | Sa+Pa (or Sa+Ma), repeated per āvartana, invariant |
| 3 | Mridangam | percussion (ch 9) | tala theka; denser pattern in charanam allowed |
| 4 | Chittaswara (optional) | textless solfa | second speed, designated columns only |

No functional-harmony row. Any production pad stays on the drone.

### Sections (columns)
```
P0 | P1 | P2 | P3 | AP0 | AP1 | C1 | C2 | C3 | C4(mudra) | CS | RET
```
Each column = k × avartana_ticks. `RET` is a literal reprise of `P0`. Every row, including the drone, must carry a terminal landmark at `section_len` (zero-drift invariant).

### Rules to encode
```
RAGA      : allowed_pc_set + directed ascent/descent paths + vakra paths
            + jeeva_svaras + nyasa_svaras   (phrase grammar, NOT a scale filter)
ARUDI     : (svara_degree, tick_offset mod avartana); every cell's final event
EDUPPU    : e ∈ {0, +k, −k}; cell_start = section_start + e (mod avartana)
TALA      : avartana_ticks (Adi 8, Rupaka 6, Misra Chapu 7) + beat hierarchy
SANGATI   : ops {RANGE±1, DENSITY×2, PATH(vakra), START_SHIFT(±1 akshara),
                 EMPHASIS(svara), REGISTER±12}; invariants: lyric_id, arudi, span
TEXT      : fixed syllables/line; ≥1 event per syllable;
            madhyamakala doubles EVENTS not syllables
REGISTER  : pallavi mid / anupallavi upper / charanam mid-low / mudra close
MUDRA     : required token in final charanam cell metadata
DRONE     : invariant pitch set spanning every column exactly
```

### Engine hookup
```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

c = UnitMatrixComposer(bpm=84, ticks_per_beat=480, beats_per_bar=4)
c.create_matrix(num_voices=5, num_sections=12)
c.add_voice("Sahitya",     program=73, channel=0)   # GM 73 flute (or 53 voice oohs)
c.add_voice("Anusvarana",  program=40, channel=1)   # GM 40 violin
c.add_voice("Tambura",     program=104, channel=2)  # GM 104 sitar (plucked drone)
c.add_voice("Mridangam",   program=0,  channel=9)   # percussion channel
c.add_voice("Chittaswara", program=73, channel=3)
# one section per form unit; length = k * avartana_ticks
c.add_section("P0", bars=2)   # Adi, 8 aksharas -> 2 avartanas
...
ok, msg = c.validate()        # MUST be True
c.to_midi(out)
```
Voice 0 fills every column; voice 1 mirrors voice 0's events (onset +small humanized offset); voice 2 fills every column with the drone unit padded to full length; voice 3 fills tala patterns; voice 4 fills only `CS`.

### Schematic sangati chain (illustrative, not a quotation)
Mohanam (S R G P D), Adi, 8 aksharas, samam eduppu, arudi = P on akshara 8:

| Pass | Degrees | Operator |
|---|---|---|
| S0 | S R G R S R G **P** | base |
| S1 | S R G P G R G **P** | RANGE↑ / PATH |
| S2 | S R G P D P G **P** | RANGE↑ (upper limit D) |
| S3 | G R S R G P D **P** | START-SHIFT + vakra |
| S4 | S R G P D P G R G P D **P** (2nd speed) | DENSITY ×2 |

All passes: same words, arudi P on akshara 8, span 8 aksharas.

### Validation gate
1. `validate()` True, equal-length rows.
2. No out-of-raga pitch; legal phrase transitions only.
3. Cell-final event == arudi `(svara, offset)`.
4. Column lengths exact multiples of `avartana_ticks`; madhyamakala same length, doubled events.
5. Drone covers all columns.
6. `export_dual` (perfect + humanized) — humanizer micro-timing is a crude gamaka stand-in, not gamaka.

---

## 6. Table row added to `human_methods_db.md`

```
| HC-070 | human (→concrete) | Carnatic Kriti Composition — Sangati-Built Sahitya Architecture (Pallavi–Anupallavi–Charanam with Progressive Phrase Variation) | South Indian Carnatic classical — Tamil Nadu/Andhra (Purandara Dasa; the Trinity: Tyagaraja, Muthuswami Dikshitar, Syama Sastri; Oothukkadu Venkata Kavi), 15th c.–present | STRUCTURE, PITCH, RHYTHM, TEXTURE | [craft process column — see file] | [UnitMatrix column — see file] | Tyagaraja, Dikshitar, Syama Sastri, Venkata Kavi, Purandara Dasa | ✅ Documented |
```

(The stored row carries the full craft-process and UnitMatrix text; abbreviated here only for readability. Verify with `grep HC-070 human_methods_db.md`.)

---

## 7. DB hygiene performed (disclosed)

While appending, four pre-existing malformed rows were repaired in place (leading `||`/`|||` normalised to `|`). Rows touched: HC-054, HC-056, HC-057, HC-058. HC-057 also received its missing terminating status cell, and a literal `[truncated]` artefact was trimmed. A stray blank line between HC-067 and HC-068 was removed. Backup of the pre-edit file: `/tmp/hmdb.bak`.

**Known remaining defect (not introduced tonight, not fixed):** ten older rows are content-truncated — they end mid-cell with `... [truncated]` and therefore parse with 6–7 columns instead of 9: HC-006, HC-009, HC-011, HC-015, HC-016, HC-022, HC-023, HC-034, HC-036, HC-051. Repairing them needs the original research text (re-research), which is out of scope for an append-only nightly job; flagged here for a dedicated backfill pass. The new HC-070 row is complete with all 9 columns (11 pipe fields) and was verified by field count.

`methods_db.md` (algorithmic DB) was NOT touched.

---

## 8. Quirks and pitfalls

1. **Sangati ≠ ornament.** Gamaka decorates a note; sangati restructures a whole phrase across passes. If the words change → new line; if the arudi moves → niraval.
2. **Arudi vs eduppu confusion is widespread** — several online study guides define arudi as the *starting* point. Correct: eduppu/graha = start, arudi = landing/cadence. Encode separately.
3. **Tala is cyclic, not additive.** Anagata pieces start inside the cycle; the engine must offset or pad the first cell or every arudi shifts.
4. **Raga ≠ scale.** Pitch-class whitelists produce ungrammatical lines; directed phrase paths and jeeva-svara weighting are mandatory.
5. **Gamaka carries raga identity.** 12-TET MIDI loses it. Encode grace/oscillation hints as metadata; do not claim performance equivalence.
6. **Madhyamakala is in-tala speed doubling**, not a tempo/metre change; must revert exactly at the column boundary.
7. **Prosody is a hard constraint** (syllable count, yati/caesura, prasa). Wrong underlay = unsingable.
8. **Lineage variance** in sangati counts is normal; do not "correct" one school against another.
9. **Mudra must be set musically**, not tagged on afterwards.
10. **Register arch** is what makes the form audible without harmony — all sections in one tessitura flattens the piece.

---

## 9. Verification

- Detail file: `human_method_HC-070_carnatic-kriti-sangati-architecture.md` (grep `HC-070` → 5 hits)
- DB: `human_methods_db.md` (grep `HC-070` → 1 hit, table row, 11 fields)
- Max ID in DB: HC-070 → **next free ID: HC-071**
- No duplicate IDs; HC-070 was unused in both the table and the file set.

---

## 10. Sources

1. Wikipedia: *Kriti (music)*; *Carnatic music*; *Varnam*; *Tyagaraja*; *Muthuswami Dikshitar*; *Glossary of Carnatic music* (accessed 2026-10-20).
2. Robert Morris, "Variation and Process in South Indian Music: Some *Kritis* and their *Sangatis*", *Music Theory Spectrum* 23/1 (2001): 74–89, doi:10.1525/mts.2001.23.1.74.
3. Swara Ragaalaya, "Eduppu or Graham: Samam, Atheetha, Anagatha" (Feb 2026).
4. Medha Vidyabhushan, "Sangati in Carnatic Music: How a Kriti Line Grows Through Variation" (2026).
5. karnatik.com glossary (sama/atita/anagata eduppu); rasikas.org sangati threads.
6. Source-quality caveat: (2) is the analytic authority; (3)–(5) supply terminology and standard examples only. One guide inverted arudi/eduppu and was discarded.
