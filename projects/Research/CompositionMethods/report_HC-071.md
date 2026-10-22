# REPORT HC-071 — Chorale Harmonization: Four-Part Chorale Setting

**Job:** daily-human-composition-research (nightly cron) · **Date:** 2026-10-21
**Method ID:** HC-071 · **Next free ID:** HC-072
**Layer:** `concrete (target when implemented)` — human-craft knowledge that resolves straight into UnitMatrix cells; no abstract intermediate layer. Target layer stated per the HC layer classification.
**Method name:** Chorale Harmonization (Four-Part Chorale Setting) — Given-Melody Harmony & Voice-Leading Craft (SATB Cantus-Firmus Realization)
**Tradition:** Western Classical — German Lutheran chorale tradition (Luther, Crüger, Gerhardt hymnody) → J.S. Bach's 371 four-part chorales and the Orgelbüchlein (Leipzig 1723–50); pedagogy lineage Kirnberger → Riemenschneider → modern conservatory harmony.
**Primary elements (Musical Elements Framework):** HARMONY, PITCH, TEXTURE, STRUCTURE, RHYTHM.

---

## 1. Summary

The four-part chorale setting is the standard Western composition exercise: a given hymn melody (the **chorale**, sung by the congregation) is placed in the **soprano**, and the composer writes three lower voices — **alto, tenor, bass** — realizing a functional tonal harmony beneath it, phrase by phrase, each phrase closing on a cadence. The method is a *setting* craft: the tune is untouchable; everything below it is the composer's judgment governed by a strict voice-leading discipline. Bach's corpus of **371 four-part chorales** (first published by C.P.E. Bach for Breitkopf 1784–87; standard teaching edition by Albert Riemenschneider, 1941) is the canonical demonstration that the rules constrain but never determine: Bach harmonized several tunes 2–5 times, each setting different and each correct.

## 2. Why this is a human method (not an algorithm)

- The melody is **given and invariant**; composition is a constrained response, not generation.
- Chord choice per melody note is **underdetermined** (multiple legal chords per scale degree); the composer chooses for cadence strategy, continuity, and contour — a planning problem solved cadence-first, backwards from each phrase end.
- The voice-leading rules are **negative filters** ("no parallel fifths") that forbid but never dictate the next note; two humans produce two different, equally valid settings.
- Inner voices are judged as **singable lines** (range, leap profile, contour), an aesthetic check no local rule captures.

## 3. Craft procedure (how the human does it, step by step)

1. **Take the tune; parse it.** Sing the given chorale melody ("Herzlich tut mich verlangen", "O Haupt voll Blut und Wunden", "Nun danket alle Gott", "Wachet auf"...). Mark phrase structure (4–10 phrases at rests/long notes), key/mode (major/minor with modal survivals: Phrygian endings, dorian inflections), and each phrase's final note (cadence target).
2. **Plan the harmony, cadence-first.** Decide each phrase's cadence type first (authentic V–I, half V, plagal IV–I, deceptive V–vi; Phrygian half cadence iv⁶–V in minor). Then assign a chord to every melody note from the soprano-chord legality table (^1→I/I⁶; ^2→V/V⁷/ii/ii⁶/vii°⁶; ^3→I/I⁶/vi; ^4→IV/I⁶₄/ii⁶; ^5→V/V⁷/I⁶₄/vii°⁶; ^6→IV⁶/vi; ^7→V/V⁷/vii°⁶). Use inversions, 7ths, secondary dominants, cadential 6/4 (I⁶₄–V–I); prefer circle-of-fifths and I–IV–V–I pillars.
3. **Compose the bass.** Roots/bass notes of the chosen chords on the harmony rhythm (1–2 chords per bar). Contrary motion to the soprano is the norm; cadence approaches by leap (^5→^1, ^3→^1) or step (^2→^1); no skip > octave; range ≈ C2–C4.
4. **Fill alto and tenor.** Complete every chord (triad or 7th — completeness is what forces the inner voices); common-tone retention; stepwise fill; close position (voices adjacent, alto under soprano, tenor under alto); ranges (A: G3–E5, T: C3–G4).
5. **Check voice-leading pairwise.** All six pairs (S–A, S–T, S–B, A–T, A–B, T–B): no parallel perfect 5ths/octaves; no hidden 5ths/octaves in outer voices when soprano leaps; no crossing/overlap; no augmented 2nd, no leap > octave, no tritone outline in a single line.
6. **Resolve tendency tones.** ^7 rises to ^1; chordal 7th falls by step; cadential-6/4 ^4 resolves to ^3.
7. **Doubling.** Double the root; double the 3rd sparingly; never double the leading tone; don't omit the 3rd.
8. **Cadence formulas & suspensions.** Set phrase ends; suspension chains 4–3 / 7–6 / 9–8 over the dominant; non-chord tones (passing, neighbor, anticipation, appoggiatura) on weak beats to animate inner voices.
9. **Sing, play, revise.** Check singability and audible cadence hierarchy; compare with Bach's own alternate settings of the same tune.
10. **Notate.** SATB open score, melody in soprano; optional figured-bass line below (Bach's manuscripts often melody + figured bass, the four-part setting being the realization).

## 4. Practitioner examples

- **J.S. Bach** — 371 four-part chorales (Riemenschneider 1941 / Breitkopf 1784–87, 348 independent settings); **St Matthew Passion**: five stanzas of "O Haupt voll Blut und Wunden" set in four different harmonizations; **BWV 140 "Wachet auf"** closing chorale (rising bass, suspension chains); **Orgelbüchlein** chorale preludes BWV 599–644 (cantus-firmus elaboration craft); **chorale cantata cycle 1724/25** (chorale as closing movement).
- **C.P.E. Bach & J.P. Kirnberger** — editors of the 371 (Breitkopf 1784–87); Kirnberger's *Die Kunst des reinen Satzes* (1771–79) codified the pedagogy that every later harmony textbook descends from.
- **Albert Riemenschneider** — 1941 *371 Harmonized Chorales and 69 Chorale Melodies with Figured Bass*, the standard teaching edition.
- **Heirs** — Mendelssohn, Bruckner, Brahms (German Requiem), Max Reger (chorale fantasias); the Bach chorales also serve as the standard benchmark corpus for computational style studies.

## 5. UnitMatrix mapping

### Voices
| Voice | Role | Content |
|---|---|---|
| V0 Soprano | **spine** | Given chorale melody — invariant cantus firmus, piece identity, never altered; carries phrase-final cadence notes. |
| V1 Bass | harmonic foundation | Composed: roots/bass notes of harmony plan; contrary motion to V0; cadence leaps. |
| V2 Alto | inner filler | Composed: completes chords; common tones; stepwise; suspensions 4-3/7-6. |
| V3 Tenor | inner filler | Composed: completes chords; stepwise; suspensions 9-8/7-6; below Alto. |

### Sections & cells
**Sections = chorale phrases** (one section per phrase, irregular 2–10 bars; cadence at every section end = the section's harmonic terminal landmark). **Cells inside a section = chords** at the harmony rhythm (1–2 per bar); each cell is a four-voice chord event cluster (e.g. `create_chord_unit` per cell) occupying the same tick window in all four rows → equal row lengths by construction, zero drift guaranteed.

### Rules to encode
1. Melody invariance — V0 frozen input, never re-written.
2. Soprano-chord legality table (degree → chord whitelist).
3. Cadence grammar — section-final cell must be an approved cadence type; bass approach constrained (^5→^1, ^3→^1, ^2→^1, ^4→^5, ^7→^5).
4. Chord completeness + doubling constraints (root preferred, 3rd sparing, never leading tone).
5. Pairwise voice-leading checks across all 6 pairs (parallels, hidden 5ths/8ves in S–B, crossing/overlap, augmented 2nd, leap > octave, tritone outline).
6. Tendency-tone resolution within the next cell (^7↑, 7th↓, cadential-6/4 ^4→^3).
7. Suspension templates as two-cell patterns (preparation = common tone, resolution = step down).
8. Non-chord-tone masks (weak beats only, never downbeat of cadence cell).
9. Per-voice range table (S: C4–A5, A: G3–E5, T: C3–G4, B: C2–C4).
10. Contrary-motion bias at cadences; ≥1 voice moves by step per chord change.
11. Final convergence — last section ends on tonic; soprano ^1/^3; optional Picardy third.
12. `composer.validate()` → True (equal-length rows, terminal landmarks).

## 6. Quirks & pitfalls

1. Rules forbid, they don't generate — the engine needs a human-supplied harmony plan; the rule table is a validator, not a composer.
2. Parallel fifths hide between *any* pair and across non-adjacent chords — check all six pairs.
3. Cadential 6/4 is a decorated dominant, not a tonic-pedal chord — encode as dominant function.
4. Chord choice is progression-constrained (next chord constrains previous), not per-note lookup.
5. Modal survivals (Phrygian endings, dorian inflections) need the Phrygian half cadence in the whitelist.
6. Irregular phrase lengths — sections are per-phrase, not fixed bar counts.
7. One tune, many settings — evaluate against rules, never against a single "correct" database answer.
8. Suspensions span two cells — cell-local validation rejects them as unprepared unless modeled across the boundary.
9. Inner voices are singable lines, not chord spackle.
10. Dull all-roots bass = amateur tell — inversions and approach leaps matter.

## 7. Table row appended to human_methods_db.md

`| HC-071 | human (→concrete) | Chorale Harmonization (Four-Part Chorale Setting) — Given-Melody Harmony & Voice-Leading Craft (SATB Cantus-Firmus Realization) | Western Classical — German Lutheran chorale tradition (Luther, Crüger, Gerhardt hymnody) → Bach 371 four-part chorales & Orgelbüchlein (Leipzig 1723–50); pedagogy Kirnberger → Riemenschneider → modern conservatory | HARMONY, PITCH, TEXTURE, STRUCTURE, RHYTHM | Take given chorale melody (cantus firmus in soprano = congregation part) → sing & parse phrase structure + final of each phrase → fix key (major/minor, modal survivals) → plan harmony cadence-first: choose a chord per melody note from soprano-chord legality table (I ii iii IV V vi vii°, inversions, 7ths, secondary dominants), decide each phrase's cadence type first (PAC/IAC/HC/plagal/deceptive, Phrygian HC in minor) → compose bass line (roots/bass notes of plan, contrary motion to soprano, cadence leap approach ^5→^1 / ^3→^1 / ^2→^1, no skip > octave) → fill alto & tenor to complete every chord (common-tone retention, stepwise motion, close position, range table) → check pairwise voice-leading (no parallel 5ths/8ves any pair, no hidden 5ths/8ves outer voices, no crossing/overlap, no augmented 2nd, no tritone outline) → resolve tendency tones (^7 up, chordal 7th down, cadential-6/4 ^4→^3) → apply doubling rules (double root, 3rd sparing, never leading tone) → add suspension chains (4-3/7-6/9-8 over dominant) + non-chord tones (passing/neighbor/anticipation/appoggiatura, weak beats) → sing/play & revise (Bach set same tune 2–5× differently — taste, not algorithm) → notate SATB open score + optional figured bass | Voice 0 = Soprano spine = given chorale melody (invariant cantus firmus, piece identity, never altered; carries phrase-final cadence notes). Voice 1 = Bass (composed harmonic foundation: roots/bass notes, contrary motion to V0, cadence leaps). Voice 2 = Alto (inner filler: completes chords, common tones, stepwise, suspensions 4-3/7-6). Voice 3 = Tenor (inner filler: completes chords, stepwise, suspensions 9-8/7-6, below Alto). Sections = chorale phrases (each section = one phrase, irregular 2–10 bars, cadence at every section end; cells inside = chords at harmony rhythm 1–2 per bar, each cell = 4-voice chord event cluster spanning the same tick window in all rows → zero drift by construction). Rules: melody invariance (V0 frozen input), soprano-chord legality table, cadence grammar (section-final cell = approved cadence type + bass approach), chord completeness + doubling constraints, pairwise voice-leading checks (6 pairs), tendency-tone resolution, suspension templates (two-cell pattern: preparation common tone → step-down resolution), non-chord-tone masks (weak beats only), per-voice range table, contrary-motion bias at cadences, final convergence on tonic (soprano ^1/^3, optional Picardy), zero-drift validate | J.S. Bach (371 four-part chorales, Riemenschneider ed. 1941; St Matthew Passion — five stanzas of "O Haupt voll Blut und Wunden" set four different ways; BWV 140 "Wachet auf" closing chorale with suspension chains; Orgelbüchlein chorale preludes BWV 599–644; chorale cantata cycle 1724/25), C.P.E. Bach & J.P. Kirnberger (Breitkopf 371 ed. 1784–87; Die Kunst des reinen Satzes 1771–79), A. Riemenschneider (1941 teaching edition), heirs Mendelssohn / Bruckner / Brahms (German Requiem) / Max Reger | ✅ Documented |`

## 8. Sources

- Wikipedia: *Lutheran chorale*; *List of chorale harmonisations by Johann Sebastian Bach*; *Chorale cantata*; *Orgelbüchlein* (accessed 2026-10-21). Corpus/edition facts: four-part SATB with melody in soprano = "chorale harmonization"; Breitkopf 1784–87 = 371 items / 348 independent settings; Riemenschneider 1941 = same 371; Terry 1929 = 405 + 95 melodies with figured bass; St Matthew Passion five stanzas of "O Haupt voll Blut und Wunden" set four ways; chorale cantata cycle 1724/25.
- J.P. Kirnberger, *Die Kunst des reinen Satzes* (1771–79).
- A. Riemenschneider, *371 Harmonized Chorales and 69 Chorale Melodies with Figured Bass* (G. Schirmer, 1941).
- Standard conservatory harmony texts in the same lineage (Kitson; Aldwell & Schachter; Piston) — rule content cross-checked.
- Quality note: Wikipedia used for corpus/edition facts only; craft steps and rule table are the common doctrine of the Kirnberger→Riemenschneider pedagogy lineage.

## 9. Files & verification

- Detail: `human_method_HC-071_chorale-harmonization-four-part-setting.md` (this directory)
- DB: row appended to `human_methods_db.md` (Human Composition Methods Framework table)
- Report: `report_HC-071.md` (this file — PRIMARY record)
- **Next free ID: HC-072**
