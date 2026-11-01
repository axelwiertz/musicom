# Report HC-080 — Notre-Dame Organum & Rhythmic-Mode Composition

**Job:** daily-human-composition-research (nightly cron, 2026-10-31)
**Method ID:** HC-080
**Detail file:** `human_method_HC-080_notre-dame-organum-rhythmic-modes.md`
**Next free ID:** HC-081

---

## 1. Method name & tradition

**Notre-Dame Organum & Rhythmic-Mode Composition — Cantus-Firmus Elaboration & Discant Clausula Craft** (Organum Purum → Discantus → Copula; the Six Rhythmic Modes; Tenor-Pedal Tripla/Quadrupla).

- **Tradition / Culture:** Western Classical — Notre-Dame school of Paris (Ars Antiqua), c. 1160–1250. Roots in 9th-c. parallel organum (*Musica enchiriadis*, c. 895) and Aquitanian St. Martial polyphony (Codex Calixtinus). Central figures: **Léonin** (fl. 1150s–d. c. 1201), **Pérotin** (fl. c. 1200), chronicled by **Anonymous IV** (c. 1275); theory by **Johannes de Garlandia** (*De mensurabili musica*, c. 1240–80) and **Franco of Cologne**.
- **Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix (this is human-craft knowledge: how a medieval composer took a chant and built polyphony by hand).

## 2. Why this method, why now

ID rotation check: recent entries were HC-077 Kulintang (Philippines), HC-078 Tin Pan Alley AABA (American pop), HC-079 Musique Concrète (French electroacoustic). HC-080 returns to Western Classical but fills a **historical gap**: existing Western entries cover partimento (HC-001), species counterpoint (HC-021), orchestration (HC-011), motivic development (HC-009), sonata process (HC-038), fugue (HC-055), chorale harmonization (HC-071), isorhythmic motet (HC-074), bel canto aria (HC-075). Nothing covers the **earliest written polyphony** — the method that invented measured rhythm and seeded the motet (which HC-074 later systematized as isorhythmy). No duplicate found (grep for `organum|rhythmic mode|discant|Léonin|Pérotin|Magnus Liber` in the CompositionMethods dir returned only incidental mentions in other files; `methods_db.md` is the separate algorithmic DB, untouched).

## 3. The craft procedure in detail (how the human executes it)

### Stage 0 — chant source & allocation
1. Pick a high-feast chant (Gradual like *Viderunt omnes*, Alleluia like *Nativitas*, Responsory, *Benedicamus Domino*). The chant is quoted verbatim as the **cantus firmus** — never invented.
2. Allocate phrases: **organaliter** (polyphonic, solo cantors) vs **choraliter** (monophonic choir). In the Alleluia only the opening is composed; the long *Jubilus* stays monophonic. This decides the outer form.

### Stage 1 — organum purum (florid organum)
3. Each tenor chant note → one long unmeasured pedal point.
4. Compose the **duplum** (vox organalis): florid, free-rhythm melisma in ligatures, up to ~40 notes per tenor note (Anonymous IV: "had to be sung fast … the text progressed very slowly" — why Pérotin later abbreviated).
5. Vertical rule: phrases begin/end on consonance (unison, 5th, 8ve); approach cadential consonances from above (7–8, 5–8); 4th consonant only as compound (8ve+4th); octave doubling (magadization) allowed.
6. Duplum "explores the harmonious interplay with the tenor, building up to a change of harmony at the end of a melisma."

### Stage 2 — discantus & clausulae
7. Where the chant becomes melismatic, **both** voices become measured/modal: tenor in mode 5 (all longs ×3), duplum in mode 1 (long–short).
8. Modal sections = **clausulae** (puncta) — rhythmic heart; modal rhythm freed music "from its ties to text."
9. Close each discant section with a **copula**: tenor sustains penultimate tone, duplum runs a florid cadence (Garlandia: copula "is between organum and discant").
10. Alternate purum/copula/discant through the text; final phrase choraliter. Model: *Benedicamus Domino* ("Benedicamus" florid over sustained tenor; "Domino" discant in modes, finalized by florid cadence).

### Stage 3 — the six rhythmic modes (notation craft)
11. Rhythm encoded by **ligature grouping** (not note shapes); the singer infers the mode and continues to the cadence:
    - Mode 1 trochee L–S (groups 3,2,2,2…; ♩.♪ in 3/8–6/8) — most common
    - Mode 2 iamb S–L (2,2,2…3)
    - Mode 3 dactyl L–S–S (1,3,3,3…; ♩.♪♩ in 6/8)
    - Mode 4 anapaest S–S–L (3,3,3…1; rare)
    - Mode 5 spondee L–L (3,3,3,3…; **tenor only**, groups of three)
    - Mode 6 tribrach S–S–S (4,3,3,3…; **upper voice**)
12. Ternary principle (subdivisions divisible by 3).
13. Density operators: *fractio modi* (break longs), *extensio modi* (merge units); ornaments: *plica* (weak-beat neighbor/fill breve), *climacus/currentes* (rapid descending figure).
14. **Ordines**: modal phrases ending in rests; perfect ordines (first note + rest) predominate.

### Stage 4 — Pérotin's expansion
15. Replace purum passages with **discant clausulae** (*abbreviavit* the Magnus Liber; ~154 attributed to Pérotin; 462 clausulae in MS F, many as substitutable variants).
16. **Tripla/quadrupla**: 3–4 voices ⇒ all parts modal. *Viderunt omnes* (Christmas 1198) & *Sederunt principes* (St Stephen 1199): tenor mode-5 pedals + three upper voices in mode 1, voice-exchange/repetition (*colores armonicae artis*), "massive pedal points sustain swings between consecutive harmonies."
17. **Conductus** (new texts, note-against-note; *cum littera / sine littera*).
18. **Motet birth**: text the upper part of a clausula → *motellus* (polytextuality; tenor holds one chant syllable).

### Stage 5 — the working loop
19. Compose → perform in the liturgy → re-edit/substitute/diffuse (MS F, W1, W2; modern eds. Waite 1954, Tischler, Roesner 1993–2009).

## 4. Practitioner examples

- **Léonin** — *optimus organista*; Magnus Liber Organi de Gradali et Antiphonario (first corpus attributable to one composer); 2-voice *Viderunt omnes*; *Benedicamus Domino*.
- **Pérotin** — *optimus discantor*; quadrupla *Viderunt omnes* (1198) & *Sederunt principes* (1199); tripla *Alleluia Nativitas*, *Alleluia Posui adiutorium*; ~154 clausulae; conducti *Salvatoris hodie*, *Dum sigillum summi Patris*, *Beata viscera*; lyrics by Philippe le Chancelier; commissioned via Bishop Odo de Sully's 1198–99 edicts.
- **Anonymous IV** — primary chronicler ("the tenor pauses if a dissonance appears").
- **Johannes de Garlandia** — three-species theory (organum, copula, discant) + modal system.
- **Parallel traditions**: *Musica enchiriadis* parallel organum; English discant (3-voice parallel 1st-inversion — distinct from fauxbourdon); Aquitanian St. Martial.
- **Modern performance practice**: Hilliard Ensemble, Deller Consort, Tonus Peregrinus; Kronos Quartet (string-quartet *Viderunt*).

## 5. UnitMatrix mapping

### Voices
- **V0 = Tenor cantus-firmus spine** — invariant chant quotation; purum cells = whole-section pedals; discant cells = mode-5 all-long groups. Identity anchor; never composed.
- **V1 = Duplum / vox organalis** — the composed voice: florid melismas (purum), mode-1 cells (discant), copula flourishes.
- **V2 = Triplum** — second organal voice (tripla/quadrupla), upper register, mode 1/6, voice-exchange partner of V1.
- **V3 = Quadruplum** — highest voice, modal, completes consonant swings.
- **V4 = metadata/performance layer** — per-column tags: purum/copula/discant/choraliter, mode number, syllable underlay, ordo/rest positions.

### Sections
Columns = chant textual units (tenor syllables/words), sequenced as:
S0 organaliter (purum) → S1 discant clausula → S2 copula → S3 next chant word (purum) → S4 discant → … → Sn choraliter close (V0 alone / unison).
Columns double as **substitution-friendly clausula slots** (the historical *abbreviavit* workflow) — clausula library keyed per tenor syllable.

### Rules to encode
1. Cantus-firmus pitch vector: each section's terminal landmark = its tenor chant note.
2. Consonance gate at every column boundary: unison/5th/8ve/(8ve+4th); 7–8 & 5–8 cadence approach; tenor pauses on dissonance (pedal suspension logic).
3. Mode assignment: V0 = mode 5 (discant) / longa pedal (purum); upper voices = mode 1/3/6; ternary 6/8 grids (3-divisible quantization at 480 tpb).
4. Density contrast: purum 20–40:1, discant 2–3:1, choraliter 1:0 — implemented as cell density per voice per column; V0 pedals padded to full column length (zero-drift invariant safe).
5. Operators: fractio (subdivide cell), extensio (merge cells), plica (weak-beat neighbor insertion), ordo (phrase cell + trailing rest).
6. Voice-exchange permutations of V1/V2/V3 content between adjacent columns (quadrupla colores).
7. Clausula substitution = section replacement from a clausula library.

### Realization path
Framework row → `UnitMatrixComposer` (5 voices × M chant-syllable sections) → `fill_voice_section` per mode-tagged cell → `validate()` (zero-drift: pad V0 pedals) → `to_midi` → `humanize` (purum rubato, discant strict) → FluidSynth render (vocal/organ timbre) → `provenance.json` + grid visualization.

## 6. Table row added (human_methods_db.md)

Appended after HC-079 as one aligned row (9 columns, bold-ID style matching HC-068+):

`| **HC-080** | human (→concrete) | Notre-Dame Organum & Rhythmic-Mode Composition — Cantus-Firmus Elaboration & Discant Clausula Craft (Organum Purum → Discantus → Copula; Six Rhythmic Modes; Tenor-Pedal Quadrupla) | Western Classical — Notre-Dame school of Paris (Ars Antiqua), c. 1160–1250; roots: parallel organum (Musica enchiriadis c. 895), Aquitanian St. Martial; Léonin (fl. 1150s–d. c. 1201), Pérotin (fl. c. 1200), Anonymous IV (c. 1275), Johannes de Garlandia (De mensurabili musica) | STRUCTURE, PITCH, RHYTHM, TEXTURE (HARMONY emergent) | … | V0 = Tenor cantus-firmus spine … | Léonin …, Pérotin …, Anonymous IV, Garlandia, … | ✅ Documented |`

(Full text in the DB; identical content mirrored in this report's sections 3–5.)

## 7. Verification

- `grep HC-080 human_method_HC-080_notre-dame-organum-rhythmic-modes.md` → present (title + body).
- `grep HC-080 human_methods_db.md` → present (one table row, last line).
- Duplicate check pre-write: max existing ID = HC-079 in both files and DB → HC-080 was free. No row with HC-080 existed before this run.
- **Next free ID: HC-081.**

## 8. Quirks & pitfalls

- Purum rhythm is genuinely unmeasured — Waite's 1954 strict-modal transcriptions are now rejected by scholarship (Jeffery); treat purum as rubato (humanize layer), discant as strict.
- Mode 5 = tenor only; mode 6 = upper only; mode 4 near-theoretical.
- Modal notation breaks on fast syllable changes (Anonymous IV reported difficulty) — one syllable per column.
- Perfect 4th is dissonant except as compound above the tenor; parallel 4ths forbidden — the historical escape is "tenor pauses on dissonance."
- Quadrupla melismas render the text nearly incomprehensible — fine as theatre, but keep the V4 syllable layer aligned for engine use.
- Do NOT touch `methods_db.md` (algorithmic DB, owned by another job) — only `human_methods_db.md` was modified.
