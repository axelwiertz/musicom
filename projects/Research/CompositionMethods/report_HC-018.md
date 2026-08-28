# Report — HC-018: Clave-Guided Montuno Construction (Cuban Son Layering)

**Job:** daily-human-composition-research
**Date:** 2026-08-27
**Method ID:** HC-018
**Detail file:** `human_method_HC-018_clave-guided-montuno.md`
**DB file:** `human_methods_db.md` (Human Composition Methods Framework table)
**Next free ID:** HC-019

---

## 1. Method name & tradition

**Clave-Guided Montuno Construction (Cuban Son Layering)** — the Afro-Cuban craft by which a *sonero* and *tresero* build a Cuban *son* song outward from the *clave* guide-pattern, layering bass *tumbao*, tres *guajeo*, vocal *canto*, and the *montuno* call-and-response section so that all parts interlock.

**Tradition:** Afro-Cuban — Cuban *son* (son cubano), born in the highlands of eastern Cuba (Oriente, ~late 19th c.), migrated to Havana ~1909–1917, flowering through the *sexteto* (1920s), *septeto* (1930s), and *conjunto* (1940s) ensemble formats. Direct ancestor of salsa, songo, and timba. Inscribed on the UNESCO Intangible Cultural Heritage list (2025). A syncretic genre: Hispanic components (vocal style, Spanish lyric metre, tres/guitar, parallel-thirds duets from the contradanza/danzón) fused with Bantu/Central-African rhythmic structure (clave, call-and-response, bongo/maracas percussion).

**Why chosen now:** Rotation check — the DB has no Cuban/Hispanic-Caribbean entry. Nearest neighbors are Ewe drumming (HC-005) and Gamelan kotekan (HC-002), both African/Balinese. The prior two entries were Korean sanjo (HC-017) and American drumband (HC-016); this fills the Caribbean/Afro-Latin gap. Not a duplicate of any existing row.

## 2. The craft procedure (how a human actually does it)

The full step-by-step is in the detail file. Summary of the workflow a working sonero/tresero follows:

1. **Fix the clave** — choose son or rumba clave, and 3–2 vs 2–3 orientation (which side the harmony/phrase begins on). The clave is a 5-stroke, two-cell period: three-side (3 strokes) + two-side (2 strokes). Son clave = beats 1, 2&, 4 | 2, 3. Rumba clave displaces the third stroke to the last 16th of beat 2 (2a).
2. **Lay the rhythm-section spine** — claves (key pattern), maracas (continuous pulse), bongó martillo, marímbula/botija or double bass foundation. Never stops, never varies.
3. **Write the bass tumbao** — syncopated root/5th ostinato that *anticipates* beat 1 (strong tone on the "& of 2" / "& of 4"). The "anticipated bass" is the defining Afro-Cuban harmonic-rhythmic signature.
4. **Write the tres/guitar guajeo** — arpeggiated chord-tone ostinato on offbeats, repeating every 1–2 bars, re-voiced per chord. Two stock alignments: *clave motif* (decorates the three-side) or *offbeat/onbeat motif* (offbeats at the end of the two-side as pick-ups).
5. **Write the canto (verse/cuerpo)** — composed strophic melody, often a duet in parallel thirds; Spanish lyric metre.
6. **Optional diana** — melismatic vocal flourish opening the tune.
7. **Build the montuno** — the collective heart of the son: coro (chorus) sings a fixed looped phrase while the sonero improvises *soneos* (pregón calls) in the gaps; guajeo + tumbao + clave loop underneath. Repeats and **escalates** (more soneos → solos → brass → tutti).
8. **Cross the clave as a structural device** — flip 3–2 ↔ 2–3 to shift groove without changing harmony/tempo.
9. **Check the interlock** — reject any voice "playing against" (*cruzado*) the clave; the clave is never altered to fit a voice.
10. **Close** — coda on a held chord or single clave stroke.

## 3. Practitioner examples

| Practitioner | Work / role | Craft significance |
| :--- | :--- | :--- |
| Miguel Matamoros | Trío Matamoros — *"Son de la Loma"* | Codified the trio form; distributed son layers across 3 voices + 2 guitars + maracas |
| Sindo Garay | trova → son, early 1900s | Canto craft + Spanish lyric metre |
| Ignacio Piñeiro | Septeto Nacional — *"Échale Salsita"*, *"Suavecito"* | Codified **son montuno** form (verse → montuno with coro + soneos) |
| Arsenio Rodríguez | Conjunto Arsenio Rodríguez — *"Bruca Maniguá"*, *"Dundunbanza"* | Expanded sexteto → conjunto (congas, piano, trumpets); tres master |
| Beny Moré | "El Bárbaro del Ritmo" — *"Castellano que bueno baila usted"* | Peak soneo improvisation + pregón craft |
| Compay Segundo / Eliades Ochoa | Buena Vista Social Club — *"Chan Chan"* | The son's pure minimal form (clave + tumbao + guajeo + canto) |
| Roberto Faz | Conjunto Roberto Faz | Conjunto-era sonero, trumpet sonora |

## 4. UnitMatrix mapping (Voices & Sections)

**6-voice matrix (sexteto/septeto template):**

| Voice | Role | Content | Rules |
| :--- | :--- | :--- | :--- |
| Voice 0 | Clave (guide pattern) | 5-stroke two-cell period, invariant | Boolean stroke mask; 3:2 cross-rhythm anchor |
| Voice 1 | Bass (tumbao) | Root/5th ostinato, anticipated (offbeat) | Chord-following; strong tone on "& of 2/4"; never on beat 1 |
| Voice 2 | Tres/Guitar (guajeo) | Arpeggiated chord-tone ostinato, offbeat | Re-voice per chord; clave-motif or offbeat/onbeat motif |
| Voice 3 | Lead sonero | Canto in verse (parallel 3rds); soneo in montuno | Conjunct; parallel-thirds doubling; soneo bounded to scale + clave gaps |
| Voice 4 | Coro (response) | Fixed looped chorus phrase in montuno | Call-response: fills the gap after coro |
| Voice 5 | Percussion + brass | Martillo + continuous pulse + brass riffs | Continuous fill; brass on clave-aligned accents; escalates |

**4-section matrix:**

| Section | Bars | Content | Density |
| :--- | :--- | :--- | :--- |
| S0 Diana/Intro | 2–8 | Melismatic vocal + clave + light tumbao | low |
| S1 Cuerpo (verse) | 8–16 (strophic) | Canto melody in 3rds + guajeo + tumbao | medium |
| S2 Montuno | 16–64 (looped, escalating) | Coro loop + soneo call-response + full percussion + brass | rising → high |
| S3 Coda | 4–8 | Final coro repeat / held chord / clave stroke | resolves |

**Encodable rule set:** `clave_invariant` (V0 constant), `clave_align` (accented onsets ∈ clave strokes ∪ complement; reject cruzado), `orientation_lock` (3–2/2–3), `anticipated_bass`, `guajeo_arpeggio`, `parallel_thirds`, `montuno_call_response`, `harmonic_loop` (2 chords per clave cycle), `density_escalation`, `continuous_fill`.

**Framework fit:** the clave layer is **Rules-Based (deterministic)** — a fixed boolean stroke mask, exactly the same class as the Ewe timeline (HC-005) and Gamelan interlock masks (HC-002). The montuno escalation maps naturally onto the master-map hybridization rule (sparse rhythmic guide + continuous fill layer). No stochastic or AI generation required — a human arranger builds it all from fixed cells.

## 5. Table row added

Appended to the `Human Composition Methods Framework` table in `human_methods_db.md`:

```
| HC-018 | Clave-Guided Montuno Construction (Cuban Son Layering) | Afro-Cuban — Cuban son (son cubano), eastern Cuba → Havana, late 19th c.–1950s; sexteto/septeto/conjunto; ancestor of salsa/songo/timba; UNESCO Intangible Heritage 2025 | RHYTHM, HARMONY, STRUCTURE, PITCH, TEXTURE | Fix clave (son/rumba, 3–2 or 2–3 orientation) → lay rhythm-section spine → write bass tumbao (anticipated offbeat) → write tres/guitar guajeo (arpeggiated ostinato) → write canto verse (parallel 3rds) → optional diana → build montuno (coro loop + soneo call-response + escalation) → cross clave as structural device → close | Voice 0 = clave ... Voice 5 = percussion+brass ... | Miguel Matamoros, Sindo Garay, Ignacio Piñeiro, Arsenio Rodríguez, Beny Moré, Compay Segundo/Eliades Ochoa, Roberto Faz | ✅ Documented |
```

## 6. Quirks / pitfalls

- **Clave is felt, not written** — the #1 craft failure is getting 3–2 vs 2–3 orientation wrong; every syncopation lands on the "wrong" side.
- **Anticipated bass sounds wrong to classical ears** — the tumbao plays *ahead* of beat 1; "correcting" it to downbeats destroys the groove.
- **The montuno is the real song** — verse is short; the repeated montuno is where the son lives. Euro-pop-trained composers over-build the verse and under-build the montuno.
- **Rumba clave's displaced third stroke** (2a) floats between duple and triple grids and is frequently mis-notated by outsiders.
- **Sparse-vs-flowing link:** the son solves the sparse-guide-pattern problem *inherently* by always layering continuous fill (maracas pulse + martillo + guajeo + anticipated bass) — the master-map hybridization rule is the genre's default texture, not an add-on.
- **No single voice plays the full clave** — the two-cell period is distributed across the ensemble's accents.
- **Instrument roles ARE the score** — the oral tradition encodes the arrangement in who-plays-what-layer, exactly the UnitMatrix voice-role abstraction.

## 7. Verification

- `HC-018` present in detail file: ✅ (`human_method_HC-018_clave-guided-montuno.md`)
- `HC-018` present in DB table: ✅ (`human_methods_db.md`, row appended after HC-017)
- `methods_db.md` (algorithmic) untouched: ✅ (only `human_methods_db.md` modified)
- **Next free ID: HC-019**

## 8. Sources consulted

- Wikipedia: "Son cubano" (genre history, instrumentation, tres guajeo, Trío Matamoros, sexteto/septeto/conjunto evolution)
- Wikipedia: "Clave (rhythm)" (son vs rumba clave stroke positions, 3–2/2–3 concept, clave motif / offbeat-onbeat guajeo alignments, anticipated bass)
