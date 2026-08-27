# HC-013 — Georgian Vocal Polyphony (Drone & Contrasted Part-Weaving)

**Tradition / Culture:** Georgian (Caucasus) folk vocal polyphony — Kakheti (East) and Guria/Svaneti (West). UNESCO Intangible Cultural Heritage of Humanity (proclaimed 2001, inscribed 2008). One of the oldest living polyphonic traditions in the Christian world, predating 4th-century Christianization.

**Primary Musical Elements:** TEXTURE, PITCH, STRUCTURE, RHYTHM (HARMONY is emergent, not functional — no chord-progression grammar).

---

## 1. What the method is

Georgian singers build music as a **stack of independent vocal layers**, not as melody-plus-accompaniment. The texture IS the composition. Two regional archetypes dominate:

- **Eastern (Kakheti) — drone polyphony ("polyphonic dialogue over a bass background"):** a long pedal drone (or rhythmic ostinato formula) in the bass, with **two highly ornamented solo voices** developing rhythmically free on top. *Chakrulo* is the canonical example.
- **Western (Guria/Svaneti) — contrasted/contrapuntal polyphony:** three or four **highly individualized** melodic lines weave simultaneously, each with its own contour, partially improvised in performance. Guria adds the **krimanchuli** yodel (male falsetto "cockerel's crow").

The harmonic language is deliberately **dissonant**: seconds, fourths, sevenths, and ninths are normal, not passing. The signature sonority is the **"Georgian Triad"** — a fourth with a second stacked on top (C–F–G), named by ethnomusicologist Dimitri Arakishvili.

Tuning is **non-tempered**: a slightly compressed major second, a **neutral third**, a stretched fourth, and an **augmented octave** in fifth-based scales. Scales split into **fourth-based** (Eastern) and **fifth-based** (Western) diatonic systems.

---

## 2. Craft process — how the human actually does it

Oral transmission, village singers (mostly farmers), learned by ear across generations. The workflow:

1. **Internalize the mode by ear.** Singers absorb the regional scale (fourth-based East / fifth-based West) with its non-tempered intervals — neutral third, compressed major second, stretched fourth. No notation; the tuning lives in the throat and ear.
2. **Lay the foundation first.** Bass singers (Georgian *bam*) establish the drone or ostinato formula. In East Georgian table songs this is a long pedal drone; in work songs it is a rhythmic ostinato. The bass can be **massed** — dozens or even hundreds of singers on one part — while top parts stay individual.
3. **Assign the top parts.** Eastern style: two soloists ornament the melody over the drone (one leads, one responds). Western style: three or four singers each take a **contrasted, individualized** line; no part merely doubles another.
4. **Weave the dissonances deliberately.** Singers tune vertical clashes (2nds, 4ths, 7ths, 9ths) as stable sonorities, often landing on the Georgian Triad (C–F–G). The "wrong" intervals are the point — they are sung with confidence, not resolved.
5. **Add the krimanchuli (West).** A male falsetto voice yodels above the texture — wide leaps, register flips, the "cockerel's crow" figure. It is a timbre/register layer, not a melodic lead.
6. **Shape the macro-form by function.** The song's architecture comes from its social job: *supra* table song (toast sequence), *naduri* work song (which folds the sounds of physical effort into the music), healing song, lullaby, round dance. Section boundaries follow the ritual or work cycle.
7. **Converge at cadence.** All parts snap together — unison or octave — at phrase and section ends, then re-open into the next weave.

Key craft constraint: **voice independence is the skill.** A good singer never tracks another part; each line must stand alone while the vertical result stays intentional. Partially improvised — the framework is fixed, the ornamentation is live.

---

## 3. Real practitioner examples

- **Chakrulo** (Kakheti) — 3-part table song, two ornamented solo voices over a choral drone foundation; chosen for the **Voyager Golden Record** (1977) as a prime example of Georgian polyphony.
- **Naduri** (Guria) — complex 3–4 part work song that incorporates the sounds of physical labor into the texture.
- **Anzor Erkomaishvili** — founder of the **Rustavi Ensemble**; recovered and reissued early 20th-century gramophone recordings of village singers, restoring the improvisatory small-ensemble tradition after Soviet-era massed-choir homogenization.
- **Georgian Voices, Mtiebi, Anchiskhati** — ensembles that revived non-tempered tuning and small-group improvisation from the 1980s onward.
- **Edisher Garaqanidze** — ethnomusicologist who classified 16 regional "musical dialects."
- **Dimitri Arakishvili** — founding father of Georgian ethnomusicology; named the "Georgian Triad" (C–F–G).

---

## 4. UnitMatrix integration (Musicom)

This method is **TEXTURE-first**: the UnitMatrix voice/section grid is literally the medium. It fills the matrix as a stack of independent, simultaneously-active voices — the opposite of the call-and-response alternation in HC-005/HC-006.

### Voice assignment

| Voice | Role | Behavior |
| :--- | :--- | :--- |
| Voice 0 | **Bam — drone/ostinato foundation** | Pedal drone (East) or rhythmic ostinato formula (West). Invariant pitch or looping formula. Massed density (many events, low register). |
| Voice 1 | **Mtkmeli — first top voice (lead)** | Ornamented melody, free rhythm over drone. Highest ornamentation density. |
| Voice 2 | **Modzakhili — second top voice (responder)** | Contrasted, individualized line; partial improvisation; never doubles Voice 1. |
| Voice 3 | **Krimanchuli yodel (West) / third contrasted line** | Falsetto register, wide leaps, yodel articulation. Timbre/register layer. |

### Section mapping

- East (drone style): sections = **stanza/toast blocks**, each opening from the drone and closing with cadential convergence (all voices → unison/octave).
- West (contrasted style): sections = **polyphonic weave blocks** (work refrain, dance cycle), each a self-contained 3–4 voice texture.

### Rules to encode

1. **Drone invariance** — Voice 0 holds one pitch class (or loops one ostinato formula) for the whole section.
2. **Non-tempered pitch set** — scale uses neutral third, compressed major second, stretched fourth; fifth-based scales may include augmented octave. (Musicom: custom scale/pitch-class set, not 12-TET equal temperament.)
3. **Dissonance allowance** — vertical 2nds, 4ths, 7ths, 9ths are legal and stable; the Georgian Triad (root + P4 + M2 above root, e.g. C–F–G) is a preferred sonority anchor.
4. **Voice independence** — no two top voices may double each other in parallel unison/octave; each keeps a distinct contour (West). Enforced as a constraint, not a suggestion.
5. **Cadential convergence** — at every phrase/section end, all voices land on unison or octave.
6. **Krimanchuli register constraint** — Voice 3 restricted to falsetto register with leap-heavy, yodel articulation (West only).
7. **Ornamentation density gradient** — Voice 1 > Voice 2 > Voice 0 (drone has zero ornamentation).
8. **Massed bass** — Voice 0 event density/amplitude may exceed top voices (many singers on one part).
9. **No functional harmony** — no chord-progression grammar; vertical sonorities are emergent from independent lines.

### Musicom method pairing

- **Drone layer** → sustained pad / 026 DPSM phase-shifted drone, or 048 RBMPD reflective-boundary bass.
- **Ornamented top voices** → 002 Markov transitions or 053 Lévy Flight (heavy-tailed pitch leaps suit the yodel/ornamentation profile).
- **Cadential convergence** → 033 WFCGS or 050 OTVL constraint propagation forcing unison/octave at section boundaries.
- **Non-tempered scale** → custom pitch-class set (neutral third etc.) instead of 12-TET.

### Why it matters for Musicom

Most Musicom methods generate Western-functional harmony (HC-001 partimento, HC-006 jazz) or monophonic/heterophonic textures (HC-003, HC-004). Georgian polyphony supplies a **texture-first, dissonance-tolerant, non-tempered** model: the UnitMatrix becomes a weave of independent voices over an invariant drone, with cadential convergence as the only global constraint. It is the strongest available counterweight to "melody + chords" thinking, and its voice-independence rule maps directly onto Musicom's multi-voice grid.
