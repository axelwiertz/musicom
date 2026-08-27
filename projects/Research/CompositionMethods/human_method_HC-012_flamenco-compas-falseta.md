# HC-012 — Flamenco Compás & Falseta Construction

| **Method ID** | HC-012 |
| :--- | :--- |
| **Method Name** | Flamenco Compás & Falseta Construction |
| **Tradition / Culture** | Spanish Flamenco — Andalusia (Calé Roma / gitano + Andalusian), late 18th c.–present; UNESCO Intangible Cultural Heritage (2010) |
| **Primary Elements** | RHYTHM, PITCH, HARMONY, STRUCTURE, TEXTURE |
| **Status** | ✅ Documented |

## 1. What it is

Flamenco is a **palo-based** art form: every piece belongs to a *palo* (form/category), and each palo fixes a bundle of musical features at once — rhythmic cycle (*compás*), mode (flamenco/Phrygian, major, or minor), chord progression, stanza form, tempo, and performance convention. A human flamenco musician does **not** freely invent these parameters; they **select a palo and then compose inside its constraints**. The craft is the disciplined construction of:

- **Compás** — the 12-beat (or binary/ternary) accent cycle, whose accents deliberately fall *off* the Western downbeat;
- **Falsetas** — composed guitar set-pieces (interludes/variations) that punctuate the sung verses;
- **Letras** (coplas/tercios) — the sung verses, built on a narrow, conjunct, descending melodic idiom;
- **Llamada / remate / cierre** — call-and-answer signals that trigger section changes and resolve the form.

This is a **rules-based (deterministic) human craft** — the opposite of free improvisation. The improvisatory surface (variations on traditional songs) is real but bounded: singers ornament a small stock of traditional melodies, and guitarists vary falsetas they already know. The deep structure is fixed by the palo.

## 2. Craft steps — how a human actually does it

1. **Choose the palo.** Pick the form by mood and function: *soleá* (12-beat, Phrygian, solemn), *alegrías* (12-beat, major, bright), *bulerías* (12-beat, fast, festive — the emblematic palo), *seguiriya* (12-beat, Phrygian, tragic, "deep song"/cante jondo), *tangos* (binary 2/4 or 4/4, festive), *sevillanas* (3/4, AAB falseta structure), *fandangos* (3/4 or 6/8, bimodal). The palo choice fixes the compás, mode, tempo, and stanza form in one decision.

2. **Fix the tonality.** Set the flamenco mode (Phrygian with major 3rd, e.g. E–F–G♯–A–B–C–D) and the **Andalusian cadence** Am–G–F–E. Guitarists transpose with a capo and use two basic tonic inversions (open 1st-inversion E, open 3rd-inversion A). Major-mode palos stay limited to I–V or I–IV–V; fandango-family palos are bimodal (guitar intro Phrygian, cante in major, modulate back to Phrygian at stanza end).

3. **Internalize the compás.** Learn the accent layout by clapping *palmas* (or knuckles on table if no guitarist). The 12-beat cycle's accents are **not** on the downbeat:
   - soleá / cantiñas / alegrías / bulerías: **3, 6, 8, 10, 12**
   - seguiriya / serrana / cabales: **12, 2, 4, 7, 10, 12**
   - peteneras / guajiras: **3, 6, 8, 10, 12** with strong accent on 12
   - Bulerías palmas are often grouped in 6s, generating counter-rhythms inside the 12-beat cycle.

4. **Play the guitar intro (falseta de entrada).** Establish tonality, compás, and tempo with a rasgueado/arpeggio figure outlining the Andalusian cadence. Chord changes land on the accented beats.

5. **Compose/sing the letras (verses).** Write each verse in the palo's stanza form. Melodic idiom: **conjunct** (contiguous scale degrees; skips of 3rd/4th rare outside fandango family), **descending tendency** (phrases fall from high to low, forte to piano), **narrow tessitura** (traditional cante spans about a sixth), **microtonal inflection + portamento** (smooth glides between notes, intervals smaller than a semitone), **insistence** on a note and its chromatic neighbors (urgency). In seguiriya the sung rhythm deliberately floats against the metric compás.

6. **Insert falsetas between verses.** Each falseta is a composed guitar set-piece: arpeggio/scale work in the palo's mode, ending on a cadence point of the compás. Sevillanas formalize this as an **AAB** pattern — same falseta twice, second ending altered.

7. **Signal section changes with llamada/remate.** The dancer or singer gives a *llamada* (call — a sharp footwork or vocal figure); the guitarist answers with a *remate* (closing flourish) that resolves on an accented beat. This call-and-answer is the section-break mechanism of the form.

8. **Vary on the spot.** Singers ornament the traditional melody (melodic improvisation = variation on a known song, not free invention); guitarists vary falsetas with rasgueado, golpe (soundboard tap), alzapúa, picado. The palo's constraints stay intact.

9. **Close (cierre).** Resolve to the tonic on a compás accent with a final rasgueado/strum. The piece ends where the cycle's accent pattern says it ends — not on a Western downbeat.

## 3. Practitioner examples

- **Ramón Montoya** (1880–1949) — first concert flamenco guitarist; created the *rondeña* as a solo guitar palo (C♯ scordatura); introduced new tonic positions (F♯ for tarantas, B for granaínas, A♭ for minera).
- **Manolo Sanlúcar** — formalized the Andalusian cadence's harmonic functions: tonic E, dominant F, subdominant Am, mediant G.
- **Sabicas** (Agustín Castellón Campos) — codified modern flamenco guitar technique and falseta repertoire.
- **Paco de Lucía** — falseta construction and rhythmic innovation; *Entre dos aguas* (rumba flamenca), bulerías; pushed compás into flamenco-jazz fusion.
- **Camarón de la Isla** — cante jondo (soleá, siguiriya); the model of narrow-tessitura, microtonal, descending vocal phrasing.
- **Carmen Amaya** — baile (dance); compás realized through footwork (*zapateado*) and contratiempo accents.
- **Tomatito, Vicente Amigo** — contemporary falseta-based toque continuing the Montoya/Sabicas line.

## 4. UnitMatrix integration (Musicom mapping)

The compás cycle is a **non-downbeat accent spine** — a perfect invariant Voice 0, exactly analogous to the Ewe gankogui bell (HC-005) or Gamelan pokok (HC-002), but carrying **harmonic cadence** those traditions lack.

| Voice | Role | Content |
| :--- | :--- | :--- |
| **Voice 0** | Compás spine (invariant) | Palmas/golpe accent grid: 12-beat cycle, accents {3,6,8,10,12} (soleá/bulerías) or {12,2,4,7,10} (seguiriya); binary/ternary for tangos/sevillanas. Never changes. |
| **Voice 1** | Guitar falseta/rasgueado | Andalusian cadence (Am–G–F–E) strummed/arpeggiated; chord changes land on accents; falseta set-pieces between verses. |
| **Voice 2** | Cante (vocal melody) | Conjunct, descending, narrow-tessitura (≤ 6th) line; microtonal/portamento inflection; rhythm floats against metric grid (siguiriyas). |
| **Voice 3** | Baile / contratiempo (optional) | Footwork accents and counter-rhythms against the compás; llamada signals. |

**Sections** = palo form stages: `Intro (falseta entrada) → Letra 1 → Falseta 1 → Letra 2 → Falseta 2 → Llamada/Escobilla → Cierre`. Sevillanas variant: `A → A → B` (same falseta, altered ending).

**Rules to encode:**

1. **Compás invariance** — Voice 0 accent grid constant across all sections; cycle length = 12 (or 2/4, 3/4 per palo).
2. **Accent lock** — melodic/harmonic events target accented beats {3,6,8,10,12} (soleá/bulerías) or {12,2,4,7,10} (seguiriya); never default to downbeat.
3. **Andalusian cadence** — Phrygian chord loop Am–G–F–E; harmonic rhythm on accents; tonic = E, F = dominant, Am = subdominant, G = mediant.
4. **Phrygian pitch set** — E F G♯ A B C D (major 3rd alteration); microtonal inflection allowed on voice 2.
5. **Conjunct melody** — stepwise preference; skips > 4th rejected outside fandango family.
6. **Descending tendency** — phrase contours fall; forte→piano.
7. **Narrow tessitura** — vocal range ≤ 6th.
8. **Falseta alternation** — guitar interludes between every verse; falseta ends on compás cadence point.
9. **Llamada/remate** — call event triggers section break; remate resolves on accent.
10. **Cierre** — final cadence on tonic at accented beat, not downbeat.
11. **Floating cante** — Voice 2 onsets may deviate from metric grid (siguiriyas only).

## 5. Why it matters for Musicom

Flamenco gives the engine something none of HC-001…HC-011 provide: an **asymmetric 12-beat accent cycle that is not aligned to the downbeat**, fused with a **fixed Phrygian harmonic cadence** and a **verse/interlude (letra/falseta) macro-form**. HC-005 (Ewe) has a 12-pulse timeline but no harmony; HC-002 (Gamelan) has stratified elaboration but no cadential harmony; HC-010 (Fanfare) has harmonic-series melody but no cycle. Flamenco = cycle + cadence + form in one palo constraint set — a deterministic rules-based method that maps 1:1 onto UnitMatrix (Voice 0 = invariant compás spine, Sections = palo stages). It also supplies a **call-and-answer section-break mechanism** (llamada/remate) reusable across other methods.

## 6. Sources

- Wikipedia: *Flamenco* (redirect from *Compás*) — Structure, Harmony, Melody, Compás sections. Retrieved 2026-08-21.
- Wikipedia: *Palo (flamenco)* — palo identification and classification. Retrieved 2026-08-21.
- Martínez (2011) via Wikipedia: three fundamental elements — flamenco mode, compás, performer.
- Manuel (2006), Rossy (1998), Torres Cortés (2001) via Wikipedia: Andalusian cadence functions, melodic characteristics, palo harmony.

*ID: HC-012*
