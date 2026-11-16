# Report HC-093 — Gregorian Plainchant Composition (Psalmody & Centonization)

**Date:** 2026-11-15 (nightly human-composition-research run)
**Method ID:** HC-093 (next free ID after this: **HC-094**)
**Layer:** `human (→concrete)` — human-craft knowledge; target layer **concrete** when realized through the UnitMatrix (psalm-tone recitation formulas, antiphon frames, and centonate melisma cells all realize directly as concrete MusicUnits; the recitation voice is rule-generated from a formula template rather than hand-composed, but every emitted cell is concrete pitch data)

---

## 1. Method name & tradition

**Gregorian Plainchant Composition — Psalmody & Centonization (Modal Formula-Bank Craft)**
(Psalm-tone recitation formulas × centonate melisma cells; mode-as-melody-type assembly; antiphon–psalm–doxology cycle; gradual/alleluia respond–verse architecture)

- **Tradition / Culture:** Western Christian liturgical monody. The repertory took its basic forms between the 6th and early 9th centuries; the Carolingian Frankish synthesis (c. 8th–9th c.) fused Roman cantus with Gallican practice, and the **eight-mode system** was attached to it by c. 800 (likely from the Byzantine *oktōēchos*). Theory: Aurelian of Réôme (*Musica disciplina*, c. 850), Hucbald, Guido d'Arezzo (*Micrologus*, c. 1026 — solmization, Guidonian hand). Composed practice peaked 9th–13th c.: **Hildegard of Bingen** (c. 1098–1179), **Notker Balbulus** (c. 840–912, sequences). Modern restoration: Solesmes monks, **Dom Eugène Cardine** (semiology, 20th c.).
- **Primary elements (Musical Elements Framework):** PITCH (mode as melody type: final/tenor hierarchy, formula banks, cadence figures), STRUCTURE (formula chain: intonation–recitation–mediant–termination; responsorial/antiphonal alternation), RHYTHM (free prose rhythm from Latin accent; no metered pulse; recitation vs melisma density contrast), TEXTURE (solo/schola two-layer monody, octave unison), HARMONY (intentionally absent — monophony; harmonic color is emergent modal field only).

## 2. Why this method, why now (rotation & overlap check)

- **Rotation:** recent entries — African-American gospel arranging (HC-092), Mongolian urtiin duu (HC-091), Finnic rune song (HC-090), Western Classical canon (HC-089), bebop contrafact (HC-088), Russian znamenny chant (HC-087), Trinidad steelband (HC-086), Japanese koto danmono (HC-085), Greek rebetiko (HC-084), Mexican mariachi (HC-083), Chinese jingju (HC-082), Moroccan gnawa (HC-081), Notre-Dame organum (HC-080). HC-093 adds **Western plainchant** — the single most influential monophonic composition system in European history, and the foundational medieval formula-craft that Western notation, solmization pedagogy, and the mode concept all grew out of.
- **Overlap check:** grep of the CompositionMethods tree for `gregorian|plainchant|psalm tone|centon|Guido|Hildegard|Solesmes` returns **no dedicated entry**. Nearest neighbors are distinct: **HC-087 znamenny** is the *Eastern* Slavonic formula-bank tradition (popevki/kokizy, different formulas, different notation, different liturgy); **HC-080 Notre-Dame organum** is *polyphonic* elaboration *over* chant tenors (the chant itself is pre-composed material, not the method); **HC-074 isorhythmic motet** and **HC-089 canon** are later polyphonic crafts. The monodic psalmody/centonization composition craft itself — mode = formula bank, psalm-tone skeletons, centonate melisma assembly — is unique in the DB.

## 3. The craft procedure in detail (how the human does it)

1. **Choose the text and genre.** A liturgical proper text (antiphon, psalm verse, gradual respond, alleluia, tract, sequence, hymn). The genre fixes the text-setting density: **syllabic** (hymns, most antiphons: ~1 note/syllable), **neumatic** (responsories: small groups of 2–4 notes), **melismatic** (graduals, alleluias: long vocalises, the alleluia *jubilus* being the archetype).
2. **Assign the mode.** The mode is a *melody type*, not a scale — a collection of appropriate melodic formulas, ornaments, and recitation patterns (parallel to Arab maqam, Indian raga, Indonesian pathet). Each mode = **final** (cadence pitch), **tenor/repercussio** (recitation pitch), **ambitus** (range; authentic modes 1,3,5,7 vs plagal modes 2,4,6,8 — pairs share a final: D/D, E/E, F/F, G/G).
3. **Psalmody: set the psalm-tone formula.** Eight psalm tones, one per mode, each a fixed skeleton used to sing psalms/canticles in the Office:
   - **Intonation** — a short rising figure over the first 2–3 syllables; sung only on the first verse and on the doxology, omitted on subsequent verses;
   - **Reciting tone (tenor/tuba)** — a held pitch, one note per syllable for the bulk of the verse;
   - **Mediant** — a cadence figure at the mid-verse colon (often dipping below the tenor, then returning to it);
   - **Termination** — the final cadence figure landing on the mode's final.
   - Special case: *tonus peregrinus* ("wandering tone"), reciting on A then G (Psalm 113/114 in the Office).
4. **Compose the antiphon frame.** A short syllabic-to-neumatic melody in the same mode, ending on the final, whose closing notes are chosen so the antiphon's termination connects smoothly into the psalm tone's intonation. Cycle: **Antiphon → Psalm verses → Doxology (Gloria Patri) → Antiphon repeat**. The same A–P–D–A shape governs Mass Introit and Communio.
5. **Centonate the melismatic chants.** Graduals, alleluias, and tracts (soloist + choir responds):
   - draw melisma cells from the mode's formula bank (cadential figures to the final, upper-zone turns, descending stepwise chains);
   - assemble the cells over the text, one cell per phrase or per stressed syllable;
   - order cells so each phrase's ending prepares the next phrase's beginning (formula *linkage* is where the composer's originality lives);
   - the *jubilus* (alleluia melisma) is the model: a long fixed per-mode melismatic outpouring.
   - This is **centonization** (Latin *cento* = patchwork; term applied to chant by Dom Paolo Ferretti, 1934).
6. **Apply melodic-motion rules.** Stepwise motion predominates; leaps are balanced and small (3rds common; 4ths/5ths only at structural points); each phrase approaches its cadence via the mode's characteristic figure (e.g., Mode 1 cadence la–sol–fa–mi). No chromatic alteration, no vertical harmony.
7. **Set the text correctly.** Latin word stress is honored: accented syllables get higher or more ornamented notes; melismas fall on accented syllables or the final syllable of phrase-words.
8. **Teach and transmit.** Solmization (ut–re–mi–fa–sol–la) and the **Guidonian hand** give singers a spatial map of the mode (Guido's pedagogical invention); neumes (later square notation) record the gesture. A **tonary** — the catalogue of antiphons by mode with their psalm-tone connections — is the composer's reference tool.
9. **Performance practice.** Cantor sings solo intonations and melismas; schola answers (responsorial), or two half-choirs alternate (antiphonal). Rhythm is free, prose-based — never isochronous meter.

## 4. Practitioner examples

- **Hildegard of Bingen** (1098–1179) — ~77 chants (sequences, antiphons, responsories) and the morality play *Ordo Virtutum*; a highly individual melodic voice built strictly on the mode-formula grammar (wide ambitus, melismatic flights on key words). The best-known named chant composer.
- **Notker Balbulus** (c. 840–912, St. Gall) — *Liber Hymnorum*: invented/established the **sequence**, with paired-strophe construction (each pair of strophes sung to one repeated melody) — a reusable compositional template.
- **Guido d'Arezzo** (c. 991–1033) — *Micrologus* (c. 1026), solmization, Guidonian hand: codified how chant is learned and composed; his pedagogy made the formula system teachable and directly enabled notation-based composition.
- **Anonymous Carolingian cantors** (8th–9th c.) — the repertory itself: the *Graduale Romanum* introit/gradual/alleluia/tract/offertory families; the Roman–Frankish synthesis.
- **Aurelian of Réôme** (*Musica disciplina*, c. 850) — earliest surviving chant treatise, documenting modes and formulas in use.
- **Solesmes monks / Dom Eugène Cardine** (20th c.) — rhythm restoration and *semiology* (reading neumes as composed gesture); the modern performance/reconstruction authority.

## 5. UnitMatrix mapping (Musicom engine)

### Voices
- **Voice 0 = Cantor solo spine** — intonation cells, solo melisma lines (gradual verses, alleluia jubilus), verse incipits. Active alone in solo passages.
- **Voice 1 = Schola choir** — antiphon/respond melodies, syllabic-to-neumatic; answers Voice 0 (responsorial) or alternates (antiphonal); octave-unison monody.
- **Voice 2 = Psalm-tone recitation formula** — rule-generated skeleton: reciting tone held across verse syllables (invariant pitch), intonation cell (verse 1 + doxology only), mediant cell at the colon, termination cell landing on the final.
- **Voice 3 = Centonate melisma bank** — mode-locked concrete formula cells drawn for graduals/alleluias/tracts; each cell a pitch vector over a syllable/sustain.

### Sections
- S0 Antiphon/Respond (frame melody, schola) → S1 Psalm verse 1 (intonation → recitation → mediant → termination) → S2 Doxology (Gloria Patri formula) → S3 Antiphon repeat (frame return) — Office psalm cycle / Mass Introit–Communio shape.
- Proper-chant alternates: S0 Respond → S1 Verse (melismatic, cantor) → S2 Respond repeat; Alleluia: S0 Alleluia+jubilus → S1 Verse → S2 Alleluia+jubilus repeat.
- Sequence: paired-strophe sections (S0 pair 1, S1 pair 2, …), each pair reusing one melody cell (Notker template).

### Rules (encoder sketch)
- **Mode-lock**: pitch field = final + tenor + ambitus of the assigned mode; no chromatic pitches; notes outside ambitus forbidden.
- **Formula-bank membership**: every melisma cell must belong to the mode's cell family (centonization constraint — no foreign cells).
- **Recitation invariance**: Voice 2 tenor pitch constant across the verse; only intonation/mediant/termination deviate.
- **Colon rule**: mediant cell fires at the mid-verse colon; termination at verse end; intonation only on verse 1 + doxology.
- **Cadence rule**: phrase/section ends on the final via the mode's characteristic cadential formula.
- **Text-setting caps**: syllable count per cell per genre (syllabic ≤ 1 note/syllable, neumatic ≤ ~4, melismatic unbounded on accented/final syllables).
- **Accent alignment**: higher pitch/ornament on Latin stressed syllables.
- **Monophony invariant**: one melodic voice active per tick (Voice 0 XOR 1 XOR 2), octave-unison doubling allowed — zero vertical chords; "harmony" is emergent modal color only.
- **Zero-drift**: every voice padded to its section terminal landmark (validate gate must pass).

## 6. Table row added (human_methods_db.md)

Appended as line 99 (bold row format matching HC-055+ entries):

```
| **HC-093** | human (→concrete) | Gregorian Plainchant Composition — Psalmody & Centonization (Modal Formula-Bank Craft: Psalm-Tone Recitation Formulas × Centonate Melisma Cells; Mode = Melody Type, Antiphon–Psalm–Doxology Cycle, Gradual/Alleluia Respond–Verse Architecture) | Western Christian liturgical monody — Carolingian Frankish synthesis of Roman chant (8th–9th c.); theory: Aurelian of Réôme (c. 850), Guido d'Arezzo (Micrologus c. 1026); composed practice 9th–13th c. (Hildegard of Bingen, Notker Balbulus); Solesmes/semiology (Cardine) 20th c. | PITCH, STRUCTURE, RHYTHM, TEXTURE (HARMONY emergent — monophony) | …craft process… | Voice 0 = cantor solo spine … Voice 3 = centonate melisma bank … Sections = S0 Antiphon/Respond → … | Hildegard of Bingen …, Notker Balbulus, Guido d'Arezzo, Anonymous Carolingian cantors, Aurelian of Réôme, Solesmes/Cardine | ✅ Documented |
```

## 7. Next free ID

**HC-094** (max existing = HC-093; verified 92 prior human_method files + 1 new = 93, DB last line = HC-093).

## 8. Quirks & pitfalls

- **Mode ≠ scale**: encoding the mode as a plain pitch class set loses the whole method — the formula bank (melody types) IS the mode. The engine should store per-mode cell libraries, not just scales.
- **Free rhythm**: chant has no meter; encoding with ticks_per_beat grid is fine for concrete output, but the *composition* rhythm is accent/prose-driven — do not impose isochronous quantization on the design rules (humanize pass may add rubato).
- **Monophony invariant** is the hardest rule to keep: the UnitMatrix defaults to multi-voice chord stacking; chant must explicitly gate voices to one-at-a-time (V0 XOR V1 XOR V2), else the texture becomes faux-polyphony.
- **Centonization vs plagiarism**: cells are shared across the repertory by design; uniqueness comes from linkage/order — a rule "no two adjacent chants use the same cell order" approximates the human sense of a fresh centonate.
- **Genre density caps** matter: an alleluia must be melismatic, a hymn must stay syllabic — swapping caps across genres produces un-idiomatic chant.
- **Terminology collision**: "tenor" here is the reciting pitch, not a voice; "mode" is not "scale degree system" — keep the chant-specific vocabulary in the encoder docs to avoid confusion with HC-021 species counterpoint / HC-089 canon terms.
- **Verification note**: researched against live web sources (Wikipedia: Centonization, Reciting tone/Psalm tone, Gregorian mode, Hildegard of Bingen, Guido of Arezzo) plus standard chant scholarship (Ferretti 1934, Cardine semiology); sources fetched 2026-11-15.

## 9. Artifacts

- Detail file: `human_method_HC-093_gregorian-plainchant-centonization.md`
- Report: `report_HC-093.md`
- DB: row appended to `human_methods_db.md` (line 99)
