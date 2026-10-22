# HC-071 — Chorale Harmonization: Four-Part Chorale Setting (Given-Melody Harmony & Voice-Leading Craft)

**Method ID:** HC-071
**Layer:** `concrete (target when implemented)` — a human craft procedure that resolves straight into UnitMatrix cells (SATB = four voices, phrase = section, chord = cell); no abstract/theory intermediate layer is required.
**Tradition:** Western Classical — German Lutheran chorale tradition (Luther, Crüger, Gerhardt hymnody) → the Bach four-part chorale canon (Leipzig, 1723–50) and its pedagogical codification (Kirnberger → Riemenschneider → modern conservatory harmony courses).
**Primary elements:** HARMONY, PITCH, TEXTURE, STRUCTURE, RHYTHM.
**Related but distinct methods:** HC-001 (partimento schemata — *bass-driven* schema improvisation; chorale is *melody-driven* functional chord syntax), HC-021 (species counterpoint — linear/modal, no functional harmony; chorale is harmonic-functional with chord grammar), HC-055 (fugue — imitative polyphony; chorale is homophonic-harmonic), HC-015 (shape-note dispersed harmony — non-functional voice-leading). HC-071 is the canonical **harmonization of a given melody** craft — the single most-taught composition exercise in Western pedagogy.

---

## 1. What the method is

A **chorale** is the congregational hymn of the German Lutheran church. The **four-part chorale setting** (chorale harmonisation) is the standard compositional form of that hymn: the melody sits in the **soprano** (sung by the congregation), and three lower composed voices — **alto, tenor, bass** — realize a functional harmony beneath it. Each phrase of the tune is set to a cadence, and the whole is a short closed piece of 4–10 phrases.

The method is the **human craft of harmonizing a given tune**: choosing chords, composing a bass, filling two inner voices, and obeying a strict voice-leading discipline. It is a *setting* craft — the melody is fixed (usually given, sometimes newly composed), everything else is the composer's work. The 371 four-part chorales of J.S. Bach (Riemenschneider edition, 1941; first published by C.P.E. Bach for Breitkopf, 1784–87 — 348 independent settings, several tunes set twice) are the canonical corpus; the same collection is the standard teaching text of tonal harmony worldwide and the classic benchmark for "style" in computational musicology.

This is human craft in the strict sense: the melody is untouchable, the harmony plan is a series of taste judgments made phrase-by-phrase and cadence-first, and the voice-leading rules are a *checklist applied by ear and eye*, not a generation recipe. Bach set the same tune multiple times with completely different harmonizations — the rules constrain, they do not decide.

---

## 2. Why this is not an algorithm

- The **melody is given and invariant**; the composition is a constrained *response* to it. Choice of chord for each melody note is underdetermined: the legality table admits several chords per scale degree, and the human chooses for continuity, cadence strategy, and expressive contour.
- **Cadence-first planning** means the composer works backwards from phrase ends; chord choice is goal-directed (each phrase must land on an approved cadence type), which is a planning problem, not a local rule.
- The **inner voices are completed for singability and smoothness** — common-tone retention, stepwise fill, range — with an aesthetic of *minimal motion*. Two different humans produce two different (both correct) settings of the same phrase.
- **Rules are negative filters, not generators**: "no parallel fifths" tells you what not to do; it never tells you what note to write next.
- **Texture matters**: a setting must sound like four *singing* parts, not a chord sequencer. Range, tessitura, and melodic independence per voice are judged by singing the line.

---

## 3. The craft procedure, step by step

### Step 1 — Take the tune; parse it
Take the given chorale melody (e.g. "Herzlich tut mich verlangen", "O Haupt voll Blut und Wunden", "Nun danket alle Gott", "Wachet auf"). Sing it. Mark:
- **Phrase structure** — the tune divides at rests / long notes into 4–10 phrases; each phrase is an independent section ending in a cadence.
- **Key & mode** — major or minor; Baroque chorales keep modal survivals (Phrygian E endings, dorian inflections) that the harmonization must honor.
- **Final of each phrase** — the cadence target note in the melody.

### Step 2 — Plan the harmony, cadence-first
For each phrase, decide its **cadence type** first (authentic V–I, half V, plagal IV–I, deceptive V–vi; in minor, Phrygian half cadence iv⁶–V). Then choose a chord for **every melody note** from the soprano-chord legality table:

| Soprano degree | Legal chords (typical) |
|---|---|
| ^1 | I, I⁶, vi⁶ (rare), V⁷ (as suspension resolution) |
| ^2 | V, V⁷, ii, ii⁶, vii°⁶ |
| ^3 | I, I⁶, vi, iii (rare), V⁶ (rare) |
| ^4 | IV, I⁶₄ (cadential), ii⁶, vii°⁶ (rare) |
| ^5 | V, V⁷, I⁶₄ (cadential 6/4 over V), vii°⁶, ii (rare) |
| ^6 | IV⁶, vi, ii (over dominant pedal) |
| ^7 | V, V⁷, vii°⁶ (leading tone — always over a dominant-function chord) |

Use inversions for smoother bass; add 7ths (V⁷, ii⁷, vii°⁷), secondary dominants (V⁷/V, V⁷/ii, V⁷/vi, V⁷/IV), and the cadential 6/4 (I⁶₄–V–I) as the standard Baroque cadence formula. Rule of thumb: prefer circle-of-fifths root motion (I–IV–vii°–iii–vi–ii–V–I) and functional I–IV–V–I pillars; chromaticism is inflection, not foundation.

### Step 3 — Compose the bass
The bass is the second-composed line and the harmonic foundation:
- Place the **root (or bass note) of each chosen chord** on the harmony rhythm (typically 1–2 chords per bar, aligned with the melody's note rhythm).
- **Contrary motion with the soprano is the norm**; at cadences the bass approaches the final tonic by leap (^5→^1 or ^3→^1 below) or by step (^2→^1), and approaches the half-cadence dominant by ^4→^5 or ^7→^5.
- No skip larger than an octave; keep bass within its range (roughly C2–C4); avoid repeating a bass note on successive chords unless the harmony is the same.

### Step 4 — Fill the inner voices (alto, tenor)
- Complete each chord (triad or seventh): every chord must be **complete** (all its tones present) — this is what forces the inner voices.
- **Common-tone retention**: keep shared chord tones in the same voice from chord to chord; move other voices by step where possible.
- Keep the texture in **close position** (voices within an octave of each other, alto under the soprano, tenor under the alto, no gaps) — spread voicing only when the bass leaps.
- Respect **ranges**: alto ≈ G3–E5, tenor ≈ C3–G4, bass ≈ C2–C4; never write a part outside its range.

### Step 5 — Check voice-leading pairwise (the famous checklist)
Check **every pair** (S–A, S–T, S–B, A–T, A–B, T–B) and the outer pair especially:
- **No parallel perfect 5ths or octaves** between any two voices (the cardinal rule — Bach's corpus is the proof that it can always be avoided).
- **No hidden (direct) 5ths/octaves** between soprano and bass when the soprano moves by leap.
- **No voice crossing** (alto below tenor, etc.) and **no overlapping** (a voice sounding above/below the previous note of the voice above/below it).
- **No augmented 2nds or leaps > octave** in any single voice; no outlining of a tritone in one melodic line.
- **Tendency tones resolve**: leading tone (^7) rises to ^1 (in the same voice unless it is in an inner voice doubled elsewhere); chordal 7th falls by step; the cadential 6/4's ^4 resolves to ^3 over the dominant.

### Step 6 — Doubling rules
In each chord, the **root is doubled by preference**; the **3rd is doubled only sparingly** (never the leading tone; in first-inversion chords double the root or 5th); the 5th is doubled when needed to complete voicing; **never double the leading tone**, never omit the 3rd of a major/minor chord.

### Step 7 — Add the cadence formulas & suspensions
Set each phrase end with a cadence formula; the richest Bachian device is the **suspension chain** over the dominant: 4–3, 7–6, 9–8 suspensions in soprano/alto/tenor resolving into the final chord (e.g. the famous "sleepers wake" cadences of BWV 140). Add **non-chord tones** (passing tones, neighbor tones, anticipations, appoggiaturas) to animate inner voices and avoid static repeated chords — always on weak beats or as prepared dissonances.

### Step 8 — Sing, play, revise
Sing every part; play the whole; check that the setting is *singable* (no awkward leaps, tessitura lies well) and that the phrase cadences "tell" — each phrase end is audible as a punctuation. Compare against Bach's own settings of the same tune (he set several tunes 2–5 times; e.g. five stanzas of "O Haupt voll Blut und Wunden" in the St Matthew Passion get four different harmonizations). Revise until the setting has the Bachian profile: smooth bass, active-but-not-noisy inner voices, unmistakable cadence hierarchy.

### Step 9 — Notate
Write the four parts in **open score** (SATB), one staff per voice, with the melody in the soprano; add a figured bass line below if the setting will be realized at the keyboard (Bach's own chorale manuscripts were often notated as melody + figured bass — the four-part setting being the realized version).

---

## 4. Practitioner examples

- **J.S. Bach (1685–1750)** — the corpus: **371 four-part chorales** (Riemenschneider 1941; Breitkopf ed. by C.P.E. Bach 1784–87, 348 independent settings). In the **St Matthew Passion** he sets five stanzas of "O Haupt voll Blut und Wunden" in **four different harmonizations** — the canonical demonstration that the rules constrain but never determine. The closing chorale of **BWV 140 "Wachet auf"** (Zion hört die Wächter singen) is the archetypal setting: soprano tune, rising bass, suspension chains. His **Orgelbüchlein** chorale preludes (BWV 599–644) are the *elaborated* cantus-firmus counterpart — the tune embedded in an imitative organ texture — and his **chorale cantata cycle (1724/25)** wraps each chorale stanza in recitative/aria commentary with the chorale as the closing movement.
- **C.P.E. Bach (1714–1788) & Johann Philipp Kirnberger (1721–1783)** — Bach's sons/pupils who edited and published the 371; Kirnberger's *Die Kunst des reinen Satzes* (1771–79) turned the practice into codified pedagogy (the direct ancestor of every modern harmony textbook).
- **Albert Riemenschneider (1878–1957)** — his 1941 *371 Harmonized Chorales and 69 Chorale Melodies with Figured Bass* is the standard teaching edition; the book (and its rules) is still the conservatory gateway to tonal harmony.
- **Heirs** — Mendelssohn, Bruckner, Brahms (the German Requiem's chorale-derived moments), Max Reger (chorale fantasias) carry the craft into the 19th/20th centuries; the Bach chorales also serve as the standard benchmark corpus for computational style studies (the rules here are the same ones such systems try to learn — the human craft predates and defines them).

---

## 5. UnitMatrix integration

### Voices & Sections
| Voice | Role | Content |
|---|---|---|
| **Voice 0 — Soprano** | **spine** | The given chorale melody — invariant cantus firmus, piece identity, never altered. One event per melody note; carries phrase-final cadence notes. |
| **Voice 1 — Bass** | harmonic foundation | Composed: roots/bass notes of the harmony plan, contrary motion to V0, cadence leaps. |
| **Voice 2 — Alto** | inner filler | Composed: completes chords, common-tone retention, stepwise motion, suspension 4–3/7–6 in its register. |
| **Voice 3 — Tenor** | inner filler | Composed: completes chords, stepwise motion, suspension 9–8/7–6 in its register, sits below Alto. |

**Sections = chorale phrases.** Each phrase is one section (irregular length: 2–10 bars; 4–10 sections per chorale). Every section ends on an approved cadence (the cadence type is the section's "terminal landmark" in harmonic terms). **Cells inside a section = chords** at the harmony rhythm (1–2 chords per bar); each cell is a `create_chord_unit` (or a chord-event cluster) holding the four voices' simultaneous notes. Zero-drift is natural: every voice's events span the full section length by construction (each cell fills the same tick window in all four rows).

### Rules to encode
1. **Melody invariance** — Voice 0 cells are frozen inputs; the engine never re-writes them.
2. **Soprano-chord legality table** — each soprano degree → whitelist of chords (Step 2 table); the harmony plan must map every melody note to a legal chord.
3. **Cadence grammar** — section-final cell must be an approved cadence type (PAC / IAC / HC / plagal / deceptive / Phrygian HC in minor); bass-final approach constrained (^5→^1, ^3→^1, ^2→^1, ^4→^5, ^7→^5).
4. **Chord completeness** — every cell contains all tones of its chord (triad or 7th); doubling per rules (root preferred, 3rd sparing, never leading tone).
5. **Pairwise voice-leading checks** — for each adjacent-chord cell pair and each voice pair: no parallel perfect 5ths/8ves, no hidden 5ths/8ves (S–B with soprano leap), no crossing/overlap, no augmented 2nd, no leap > octave, no tritone outline.
6. **Tendency-tone resolution** — ^7 → ^1 up, chordal 7th → down by step, cadential-6/4 ^4 → ^3, all within the next cell.
7. **Suspension templates** — 4–3 / 7–6 / 9–8 chains allowed only over dominant-function cells; preparation = common tone, resolution = step down (the suspension is a two-cell pattern).
8. **Non-chord-tone masks** — passing/neighbor/anticipation/appoggiatura only on weak beats (or as prepared dissonances); never on the downbeat of a cadence cell except the suspension.
9. **Range table** — per-voice pitch bounds (S: C4–A5, A: G3–E5, T: C3–G4, B: C2–C4).
10. **Contrary-motion bias** — S–B move in contrary motion at cadences; elsewhere at least one voice moves by step per chord change.
11. **Final convergence** — last section ends on tonic; soprano on ^1 or ^3; optional Picardy third in minor.
12. **Validate** — `composer.validate()` → True (equal-length rows, terminal landmarks at section length).

### Schematic (invented illustration, not a quotation)
"Ach bleib bei uns" style phrase, C major, 4 chords:

| Cell | Chord | S (given) | A | T | B |
|---|---|---|---|---|---|
| 1 | I | E4 (^3) | C4 | G3 | C3 |
| 2 | IV⁶ | D4 (^2) | A3 | F3 | D3 |
| 3 | V⁷ | D4 (^2, 7th) | C4 | F3 | G2 |
| 4 | I (PAC) | C4 (^1) | E4 | G3 | C3 |

Check: no parallels (B: C→D→G→C, S: E→D→D→C), 7th F resolves down to E in tenor... (schematic only — a real setting would be worked by the rules above, cell by cell, cadence-first.)

---

## 6. Pitfalls and quirks

1. **The rules forbid, they don't generate.** Encoding the voice-leading checks gives a *validator*, not a composer. The human judgment (cadence-first plan, taste in chord choice, bass profile) lives outside the rule system — the engine fills cells from a harmony plan the composer supplies or approves.
2. **Parallel fifths are the trap of traps** — they appear between *any* voice pair and across *non-adjacent* chords if a voice is silent; the checker must scan all six pairs, not just S–B.
3. **The 6/4 is a status, not a chord.** The cadential I⁶₄ is a decorated dominant; treating it as a tonic-pedal chord breaks resolution logic. Same for passing/neighbor 6/4s — encode them as dominant/embellishment functions.
4. **Soprano-degree legality is directional.** A melody note can be legal over two different *functions*; the *next* chord constrains the *previous* choice (chord sequences are evaluated as progressions, not per-note lookups).
5. **Modal survivals.** Baroque chorales contain phrygian endings and dorian inflections; a strict major/minor filter will mis-harmonize them. The cadence whitelist must include the Phrygian half cadence (iv⁶–V) and allow modal final treatment.
6. **Irregular phrase lengths** break naive section grids — sections must be per-phrase (variable bars), not per fixed bar count; zero-drift padding still applies per voice within each phrase-section.
7. **One tune, many settings.** Bach harmonized several melodies 2–5 times; there is no single "correct" setting. Do not evaluate an engine setting against a database as if one answer existed — evaluate against the *rules*.
8. **Suspensions are two-cell patterns** — a suspension's preparation (common tone) and resolution (step down) span adjacent cells; a cell-local validator will reject them as "unprepared dissonance" unless the pattern is modeled across the cell boundary.
9. **Inner voices are singable lines, not chord spackle** — a setting passes only if each part can be sung as a melody (range, leap profile, contour); grid-filling chords without part-writing produces voicing, not a chorale.
10. **Bass doubles as the congregation's anchor.** The bass is heard as strongly as the tune; a dull bass (all roots, no inversions, no approach leaps) is the fastest tell of an amateur setting. Bach's basses move, leap, and cadence like melodies.

---

## 7. Sources

- Wikipedia: *Lutheran chorale*; *List of chorale harmonisations by Johann Sebastian Bach*; *Chorale cantata*; *Orgelbüchlein* (accessed 2026-10-21). Key facts: four-part SATB setting with melody in soprano = "chorale harmonization"; C.P.E. Bach's Breitkopf edition 1784–87 = 371 items / 348 independent settings (No. 283 duplicated, No. 156 = No. 307); Riemenschneider 1941 = same 371; Terry 1929 = 405 settings + 95 melodies with figured bass; St Matthew Passion sets five stanzas of "O Haupt voll Blut und Wunden" in four different ways; chorale-cantata cycle 1724/25; Orgelbüchlein chorale preludes.
- Johann Philipp Kirnberger, *Die Kunst des reinen Satzes* (1771–79) — the codifying pedagogy.
- Albert Riemenschneider, *371 Harmonized Chorales and 69 Chorale Melodies with Figured Bass* (G. Schirmer, 1941) — the standard teaching edition.
- Standard conservatory harmony texts in the same lineage (Kitson; Aldwell & Schachter, *Harmony and Voice Leading*; Piston) — the rule set above (parallels, tendency tones, doubling, cadence formulas, soprano-chord legality) is their common content, cross-checked across these.
- Source-quality note: Wikipedia used for corpus/edition facts; the craft steps and rule table are standard conservatory pedagogy (Kirnberger → Riemenschneider lineage), stated here as the common doctrine of that lineage.

---

## 8. Registry status

- Detail file: `human_method_HC-071_chorale-harmonization-four-part-setting.md`
- DB row: appended to `human_methods_db.md` → Human Composition Methods Framework
- Report: `report_HC-071.md`
- **Next free ID: HC-072**
