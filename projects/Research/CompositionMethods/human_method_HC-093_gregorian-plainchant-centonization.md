# HC-093 — Gregorian Plainchant Composition (Psalmody & Centonization)

**Layer:** human (→concrete) — target layer **concrete** when realized through the UnitMatrix
**Tradition:** Western Christian liturgical monody — Carolingian Frankish synthesis of Roman chant (8th–9th c.); theorized by Aurelian of Réôme (*Musica disciplina*, c. 850), Hucbald, Guido d'Arezzo (*Micrologus*, c. 1026); composed practice 9th–13th c. (Hildegard of Bingen, Notker Balbulus); Solesmes restoration & semiology (Dom Eugène Cardine, 20th c.)

---

## 1. What it is

Gregorian chant is **formula-bank composition**: a mode is not a scale but a *melody type* — a collection of appropriate melodic formulas, ornaments, and recitation patterns (the same concept as Arab *maqam*, Indian *raga*, Indonesian *pathet*). The composer works by **centonization** (from Latin *cento* = patchwork; term applied to chant by Dom Paolo Ferretti, 1934): assembling pre-existing motivic units from the mode's formula bank into a new whole. Originality lies in **how the formulas are linked, ordered, and elaborated** — not in inventing new pitch material. Two complementary crafts:

1. **Psalmody** — the fixed recitation formulas (8 psalm tones, one per mode) used for singing psalms/canticles in the Office: each tone = intonation + reciting tone (tenor/tuba/dominant) + mediant + termination.
2. **Centonate melisma** — the free-formula assembly of the great solo chants (graduals, alleluias, tracts) from mode-locked melisma cells.

Plus the frame genres (antiphon, respond, hymn) that are syllabic-to-neumatic and cadence on the mode's final, designed to connect smoothly into the recitation formulas.

## 2. The craft procedure (how the human does it)

1. **Choose the text and genre.** Liturgical proper text (antiphon, psalm verse, gradual respond, alleluia, tract, sequence, hymn). Genre dictates text-setting density: syllabic (hymns, most antiphons) → neumatic (responsories) → melismatic (graduals, alleluias — the *jubilus*).
2. **Assign the mode.** The mode is chosen by the text's festal rank and by which formula family it belongs to. Each mode = final (cadence pitch), tenor/repercussio (recitation pitch), ambitus (authentic vs plagal range). Modes 1/3/5/7 authentic, 2/4/6/8 plagal (pairs share a final: D/D, E/E, F/F, G/G).
3. **For psalmody: set the psalm-tone formula.** Pick the tone matching the antiphon's mode so the antiphon's termination connects smoothly into the tone's intonation. The tone is a fixed skeleton:
   - **Intonation**: the first 2–3 syllables, a short rising figure (omitted after the first verse — only the opening verse and the doxology get the full intonation);
   - **Reciting tone (tenor/tuba)**: a held pitch, one note per syllable for the bulk of the verse;
   - **Mediant**: a cadence figure at the mid-verse colon (often descending to a secondary pitch, then back up to the tenor);
   - **Termination**: the final cadence figure landing on the mode's final.
   - (Special case: *tonus peregrinus* = "wandering tone", reciting on A then G, used for Psalm 113/114.)
4. **Compose the antiphon frame.** A short, syllabic-to-neumatic melody in the same mode, ending on the final, whose last notes are chosen to lead into the psalm tone. Antiphon–Psalm–Doxology–Antiphon repeat = the Office psalm cycle; Introit/Communio of the Mass = Antiphon–verse–Gloria Patri–Antiphon.
5. **Centonate the melismatic chants.** For graduals, alleluias, tracts (soloist + choir responds):
   - draw melisma cells from the mode's formula bank (cadential figures to the final, upper-zone melodic turns, descending stepwise chains);
   - assemble them over the text, one cell per phrase or per stressed syllable;
   - order cells so each phrase's end prepares the next phrase's beginning;
   - the *jubilus* (alleluia melisma) is the archetype — a long neumatic/melismatic outpouring fixed per mode.
6. **Apply melodic-motion rules.** Stepwise motion predominates; leaps are balanced and small (3rds common, 4ths/5ths at structural points); each phrase approaches its cadence via the mode's characteristic formula (e.g., Mode 1 cadence figure la–sol–fa–mi). No chromatic alteration, no vertical harmony — monody in octave unison.
7. **Set the text correctly.** Latin word accent (stress) is honored: accented syllables get the higher/ornamented notes; melismas fall on accented syllables or final syllables of phrase words.
8. **Teach and transmit.** Solmization (ut–re–mi–fa–sol–la, later *si*) and the Guidonian hand give singers a spatial map of the mode; neumes (→ square notation) record the gesture. A tonary (catalogue of antiphons by mode + their psalm-tone connections) is the composer's reference tool.
9. **Performance practice.** Cantor sings solo intonations/melismas; schola answers (responsorial) or two half-choirs alternate (antiphonal); free rhythm (prose rhythm of the text, not isochronous meter).

## 3. Practitioner examples

- **Hildegard of Bingen** (1098–1179) — ~77 chants: sequences, antiphons, responsories; *Ordo Virtutum* (morality play). Highly individual melodic style built on the mode-formula grammar (wide ranges, melsimatic flights on key words) — the medieval "composer" par excellence.
- **Notker Balbulus** (c. 840–912, St. Gall) — *Liber Hymnorum*: the sequence genre, paired-strophe construction (each pair of strophes sung to the same repeated melody) — a compositional template used for centuries.
- **Guido d'Arezzo** (c. 991–1033) — *Micrologus* (c. 1026), solmization, the Guidonian hand: codified how chant melody is learned and composed; the pedagogy that made the formula system teachable.
- **Anonymous Carolingian cantors** (8th–9th c.) — the repertory itself: *Graduale Romanum* introit/gradual/alleluia/tract/offertory families; the Roman–Frankish synthesis.
- **Aurelian of Réôme** (*Musica disciplina*, c. 850) — earliest surviving chant treatise; documents the modes/formulas in use.
- **Solesmes monks / Dom Eugène Cardine** (20th c.) — restored chant rhythm and *semiology* (reading the neumes as composed gesture); the modern performance/reconstruction reference.

## 4. UnitMatrix integration (Musicom engine)

### Voices
- **Voice 0 = Cantor solo spine** — intonation cells, solo melisma lines (gradual verse, alleluia jubilus), verse incipits; the only voice active in solo passages.
- **Voice 1 = Schola choir** — antiphon/respond melodies, syllabic-to-neumatic; answers Voice 0 (responsorial) or alternates (antiphonal); octave-unison monody.
- **Voice 2 = Psalm-tone recitation formula** — the fixed skeleton: reciting tone held across verse syllables (invariant pitch), intonation cell (first verse only), mediant cell at the colon, termination cell landing on the final. This is a *rule-generated* voice (formula template, not hand-composed).
- **Voice 3 = Centonate melisma bank** — mode-locked formula cells drawn for graduals/alleluias/tracts; each cell is a concrete MusicUnit (pitch vector over a syllable/sustain).

### Sections
- S0 Antiphon/Respond (frame melody, schola) → S1 Psalm verse 1 (intonation + recitation + mediant + termination, cantor) → S2 Doxology (Gloria Patri formula) → S3 Antiphon repeat (frame return) — the Office psalm cycle / Mass Introit-Communio shape.
- For proper chants: S0 Respond → S1 Verse (melismatic, cantor) → S2 Respond repeat; Alleluia: S0 Alleluia+jubilus → S1 Verse → S2 Alleluia+jubilus repeat.
- Sequence: paired-strophe sections (S0 pair 1, S1 pair 2, …) each pair reusing one melody cell.

### Rules (encoder sketch)
- **Mode-lock**: pitch field = final + tenor + ambitus of the assigned mode; no chromatic pitches; notes outside ambitus forbidden.
- **Formula-bank membership**: every melisma cell must belong to the mode's cell family (centonization constraint — no foreign cells).
- **Recitation invariance**: Voice 2's tenor pitch constant across the verse; only intonation/mediant/termination deviate.
- **Colon rule**: mediant cell fires at the mid-verse colon; termination at verse end; intonation only on verse 1 + doxology.
- **Cadence rule**: phrase/section ends on the final via the mode's characteristic cadential formula.
- **Text-setting caps**: syllable count per cell per genre (syllabic ≤ 1 note/syllable, neumatic ≤ ~4, melismatic unbounded on accented/final syllables).
- **Accent alignment**: higher pitch/ornament on Latin stressed syllables.
- **Monophony invariant**: single line at any tick (Voice 0 XOR Voice 1 XOR Voice 2 active), octave unison if doubled — no vertical chords; "harmony" is emergent modal color only.
- **Zero-drift**: every voice padded to section terminal landmark (validate gate).

### Musical Elements Framework mapping
- **PITCH**: mode as melody-type — formula banks, final/tenor hierarchy, stepwise motion, cadence figures (the engine's pitch rules ARE the mode).
- **RHYTHM**: free prose rhythm derived from text accent; no metered pulse; long-note recitation vs melisma density contrast.
- **HARMONY**: none composed (monophony) — only emergent modal color; the framework row marks HARMONY as intentionally absent/emergent.
- **STRUCTURE**: formula chain (intonation–recitation–mediant–termination), responsorial/antiphonal alternation, strophe pairing.
- **TEXTURE**: solo/schola two-layer responsorial texture; octave-unison doubling.
