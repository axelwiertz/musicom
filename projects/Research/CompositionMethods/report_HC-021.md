# Report — HC-021: Species Counterpoint (Strict Counterpoint / Cantus Firmus Study)

**Job:** daily-human-composition-research
**Date:** 2026-08-30
**Method ID:** HC-021
**Next free ID:** HC-022

---

## 1. Method name & tradition

**Method Name:** Species Counterpoint (Strict Counterpoint / Cantus Firmus Study)

**Tradition / Culture:** Western Classical — the European contrapuntal school. Lineage: Gioseffo Zarlino (*Le institutioni harmoniche*, 1558) → Giovanni Maria Lanfranco (*Scintille di musica*, 1533) → Lodovico Zacconi (*Prattica di musica*, 1619, first codified form) → **Johann Joseph Fux, *Gradus ad Parnassum* (1725)** (the modern five-species system) → the 19th–20th c. conservatory. This is *the* pedagogical method by which most canonical Western composers learned to write polyphony.

**Why it qualifies as *human craft* (not algorithm, not AI, not DSP):** Species counterpoint is a **craft procedure a human physically executes at a desk** — write a fixed melody, then add independent lines against it one note at a time, checking interval, motion, and line-shape rules at every step, rejecting and retrying until every rule holds. It is a *constraint-satisfaction workflow*, not a generation algorithm (the human chooses each note) and not sound production. It is also the human-side mirror of the master-map's algorithmic Method 056 (SCCC) — the same rule-stack described as a craft, not a solver.

---

## 2. Craft procedure in detail (how a human executes it)

A composer does not invent a chord progression and harmonize it. They take a **fixed pre-existing melody** (the **cantus firmus**, "fixed song") and **add one or more independent melodies against it**, obeying a ladder of interval/motion rules that get progressively harder. The goal is **line independence**: melodies that each sound complete and singable alone, yet combine into correct consonance at every moment.

Two governing ideas:

1. **The cantus firmus is sacred.** It never changes. All the composer's freedom is in the *added* voices — this is what makes it both a study and a generator (one fixed spine, many possible counter-melodies).
2. **Species = a difficulty ladder.** The same cantus firmus is worked five times, each time with a denser rhythmic relationship between the added voice and the fixed one.

### Stage 0 — Build the cantus firmus
- Write a slow, wholly-conjunct (or near-conjunct) modal melody in whole notes — usually Dorian, Phrygian, Lydian, or Mixolydian, spanning roughly an octave.
- It must **begin and end on the final** (the mode's tonic), move mostly by step, have a single high point (climax) mid-line, and avoid outlining a tritone or a seventh.
- Freeze it. Everything after is about what is added *against* it.

### Stage 1 — Choose the species (the difficulty rung)

| Species | Added-voice rhythm vs. CF | New things to handle |
| :--- | :--- | :--- |
| **1st** | one note per CF note (whole notes) | consonances only, motion rules |
| **2nd** | two notes per CF note (half notes) | passing/neighbor tones on the off-beat |
| **3rd** | four notes per CF note (quarter notes) | *nota cambiata*, double neighbors |
| **4th** | syncopated (tied) half notes | suspensions: dissonance on the beat, resolved down |
| **5th** (florid) | free mix of all four | all of the above, balanced so no one species dominates |

### Stage 2 — Write the counter-melody note by note
For every added note, check a stack of rules (the shared strict core across all species, from Fux and the Palestrina style):

**Melodic (line) rules — every added voice must itself be a good melody:**
- Permitted melodic intervals: unison, octave, 4th, 5th, major/minor 2nd, major/minor 3rd, ascending minor 6th (which must then fall by step).
- Conjunct motion preferred; after a skip, move by step in the opposite direction.
- No more than two skips in the same direction, and the second must be smaller than the first.
- Avoid outlining a tritone (e.g. F–A–B) or a seventh within three notes in one direction.
- Exactly one climax (high point), on a strong beat, somewhere mid-line.
- The final note must be approached **by step**.

**Vertical (interval) rules — each simultaneous pair must be correct:**
- Counterpoint begins and ends on a **perfect consonance** (unison, octave, or 5th; if the added part is *below* the CF, only unison or octave).
- **Consonances** (1, 3, 5, 6, 8) are stable; **dissonances** (2, 4, 7, augmented/diminished) are allowed *only* as passing/neighbor/suspension figures — and only where the species permits.
- A dissonance must resolve **by step** (usually downward).

**Motion rules — between any two adjacent parts:**
- **Contrary motion should dominate.**
- **Perfect consonances must be approached by oblique or contrary motion** (never similar motion — that would be "hidden" parallel 5ths/8ves).
- **Parallel 5ths and parallel 8ves are forbidden** (they destroy line independence — the two voices fuse into one timbre).
- Parallel 4ths avoided (especially involving the bass).
- Adjacent parts stay within a tenth.
- Don't use the same interval more than three times in a row; prefer up to three parallel 3rds/6ths.

### Stage 3 — Add more voices
Once two parts work, add a **third**, then a **fourth**, stacking species (e.g. bass = CF, middle = 2nd species, top = florid). The same rule-stack is checked **pairwise** between every adjacent pair ("build from the bass upward").

### Stage 4 — Graduate to free counterpoint, then imitative forms
With strict counterpoint mastered, the composer relaxes the rules (**free counterpoint**: any dissonance if it resolves, chromaticism allowed, dissonance free on the accented beat), then applies the **contrapuntal derivations** — inversion, retrograde, retrograde-inversion, augmentation, diminution — to build **canon** and **fugue**.

---

## 3. Practitioner examples (how real composers used it)

- **Johann Joseph Fux — *Gradus ad Parnassum* (1725).** The codifier. Wrote the method as a dialogue between master (Aloysius, standing in for **Palestrina**) and student (Josephus). His five-species system is still the universal conservatory text.
- **Giovanni Pierluigi da Palestrina (16th c.).** The *style model* behind the rules — Fux distilled Palestrina's polyphonic practice into teachable constraints. The "Palestrina style" remains the benchmark.
- **J.S. Bach.** The supreme practitioner. His 2- and 3-part Inventions and 48 fugues of the *Well-Tempered Clavier* are free counterpoint on this strict foundation; the G♯-minor fugue (WTC II) is cited as textbook "the counterpoint sheds new light on the subject."
- **Joseph Haydn → Ludwig van Beethoven.** Haydn taught the young Beethoven from Fux's *Gradus*. Beethoven's late works return to it — the counterpoint in the first movement of Op. 90, the "wonderful counterpoint" added to a theme in the E-minor sonata, and the first orchestral variation of the *Ode to Joy* in the 9th Symphony finale.
- **W.A. Mozart.** Studied strict counterpoint (Fux's book annotated in his own hand); the five-voice finale of the "Jupiter" Symphony No. 41 combines five themes simultaneously — the apotheosis of trained line independence.
- **Schubert, Schumann, Brahms, Bruckner.** All educated in strict counterpoint before writing freely; Brahms's "developing variation" and Bruckner's contrapuntal masses are direct descendants.
- **Pedagogical lineage (András Schiff).** Bach's counterpoint documented as the common thread influencing both Mozart's and Beethoven's inner-voice writing.

---

## 4. UnitMatrix mapping (Voices & Sections, rules)

The method maps naturally onto a **Voices × Sections** grid, because the composer literally thinks "one fixed line + N added lines, worked at increasing rhythmic density."

### Voices (lines = voices)

| Voice | Role | Elements |
| :--- | :--- | :--- |
| Voice 0 | **Cantus firmus** (slow conjunct modal whole notes, begins/ends on final) | PITCH — invariant spine, the reference every other voice is checked against |
| Voice 1 | **1st added counter-melody** (species rhythm vs CF) | PITCH + TEXTURE — conjunct, single-climax, obeys interval/motion rules vs Voice 0 |
| Voice 2 | **2nd added counter-melody** (higher species, or free) | PITCH + TEXTURE — checked pairwise vs Voice 0 *and* Voice 1 |
| Voice 3 | **Bass / lower added voice** (or 4th free line) | STRUCTURE + TEXTURE — "build from the bass upward" |

### Sections (species = sections)

`Species 1 → Species 2 → Species 3 → Species 4 → Species 5 (florid) → Free/Imitative`

Each section is the **same cantus firmus (Voice 0)** but the added voices get **rhythmically denser** (1:1 → 2:1 → 4:1 → syncopation → mixed). A monotonic "density ramp" over a fixed spine.

### Rules to encode

1. **Cantus firmus invariance** — Voice 0 read-only; all freedom is in Voices 1–3.
2. **Interval-validity table** — each vertical interval must be in the allowed set for its beat-position (consonance on strong beats in species 1–3; dissonance only as passing/neighbor/suspension, resolving by step).
3. **Motion-type constraint** — perfect consonances (1, 5, 8) approached by oblique/contrary motion; parallel 5ths/8ves forbidden; contrary motion dominates.
4. **Species rhythm mask** — Voice 1's note count per CF note = {1, 2, 4, syncopated, mixed} by section.
5. **Melodic-conjunct rule** — each added voice prefers stepwise motion, max two same-direction skips (second smaller), no tritone/7th outline, single climax on a strong beat.
6. **Cadence convergence** — all voices approach the final by step, land on a perfect consonance, leading tone raised in minor (except Phrygian).
7. **Registral spacing** — adjacent parts within a tenth; no crossing.
8. **Line-independence scalar** — measure parallel unison/octave/5th between voices; enforce a low ceiling (the texture signature of the whole method).
9. **Density ramp** — section-to-section note-density increases monotonically (Species 1 → 5), then "releases" into free/imitative counterpoint.

### Why it belongs in Musicom

Species counterpoint is the **canonical PITCH + TEXTURE constraint method** — the exact inverse of the harmonic-realization methods (HC-001 partimento is bass→harmony; this is melody→lines). It is the master-map's **056 SCCC** viewed from the *human* side: the same rule-stack described as the craft procedure a composer physically executes, not the backtracking solver. It pairs cleanly with the engine's constraint methods (033 WFCGS, 050 OTVL, 051 SGLM) as a *voicing-and-line post-filter*, and its species-ladder is a ready-made **section generator** (density ramp over a fixed CF spine).

---

## 5. Table row added

Appended to `human_methods_db.md`:

```
| HC-021 | Species Counterpoint (Strict Counterpoint / Cantus Firmus Study) | Western Classical — European contrapuntal school (Zarlino 1558 → Zacconi 1619 → Fux Gradus ad Parnassum 1725 → modern conservatory) | PITCH, TEXTURE, STRUCTURE, RHYTHM | Build cantus firmus (slow conjunct modal whole-note melody, begins/ends on final, single climax) → freeze it (invariant spine) → choose species rung (1st=note-against-note, 2nd=2:1, 3rd=4:1, 4th=syncopated suspensions, 5th=florid mix) → write added voice note-by-note checking melodic rules (conjunct, max 2 same-direction skips, no tritone/7th outline, single climax, stepwise cadence) + vertical rules (consonances 1/3/5/6/8, dissonances only as passing/neighbor/suspension resolving by step) + motion rules (contrary motion dominant, no parallel 5ths/8ves, perfect consonances by oblique/contrary motion) → add 3rd/4th voice checking pairwise → graduate to free counterpoint → apply derivations (inversion/retrograde/augmentation/diminution) → canon/fugue | Voice 0 = cantus firmus (invariant modal spine, PITCH anchor). Voice 1 = 1st added counter-melody (species rhythm vs CF, conjunct + single climax). Voice 2 = 2nd added counter-melody (higher species, pairwise-checked vs V0 & V1). Voice 3 = bass/lower line (structure foundation, build-from-bass-up). Sections = Species 1→2→3→4→5→Free/Imitative (same CF, monotonically denser added voices). Rules: CF invariance, interval-validity table (beat-position-dependent dissonance), motion-type constraint (no parallel 5ths/8ves), species rhythm mask (1:1/2:1/4:1/syncopated/mixed), melodic-conjunct rule, cadence convergence on final, registral spacing ≤10th, line-independence scalar, density ramp | Johann Joseph Fux (Gradus ad Parnassum 1725), Giovanni Pierluigi da Palestrina (style model), J.S. Bach (2/3-part Inventions, WTC fugues), W.A. Mozart (Jupiter Symphony finale, 5-voice), Joseph Haydn→Ludwig van Beethoven (Op. 90, Symphony 9 finale), Schubert/Schumann/Brahms/Bruckner (strict→free counterpoint lineage) | ✅ Documented |
```

---

## 6. Quirks / pitfalls

- **Frozen-spine discipline.** Beginners want to "fix" the cantus firmus when a rule won't hold. The craft is to change the *added* voice instead — the CF is the invariant, and violating that defeats the exercise. (Encode as: Voice 0 read-only.)
- **Parallel 5ths/8ves sneaking in.** The classic failure — two voices moving in similar motion into a 5th or octave "fuse" into one timbre and the texture collapses. The single most important rule to enforce (the "line independence" scalar).
- **Sparse/mechanical output.** If the added voice is written rule-by-rule without listening, it sounds like a row of legal intervals, not a melody. The *melodic* rules (conjunct motion, single climax, stepwise cadence) are what make it sing — exactly the "sparse → add flow" principle in the master map (a florid 5th-species line is the continuous fill that keeps it flowing).
- **Dissonance placement.** Dissonances are *positional* — legal on the off-beat (passing/neighbor) in species 2–3, legal on the beat only as suspensions (species 4). Encoding dissonance without beat-position context produces illegal (or ugly) output.
- **MIDI tail truncation.** If the final cadence leaves a voice resting before the global track end, append the silent padding event at `total_section_ticks - 1` (master-map pitfall).
- **Overlap with HC-001 (partimento).** Partimento gives an *unfigured bass* and realizes *harmony* upward; species counterpoint gives a *fixed melody* and adds *independent lines*. Same family (voice-leading craft), different spine and different primary element (HARMONY vs PITCH/TEXTURE). Do not merge them.

---

## 7. Files & verification

- Detail file: `/opt/data/projects/Research/CompositionMethods/human_method_HC-021_species-counterpoint.md`
- DB file: `/opt/data/projects/Research/CompositionMethods/human_methods_db.md`
- Report file: `/opt/data/projects/Research/CompositionMethods/report_HC-021.md` (this file)
- `HC-021` present in detail file: ✅ (title + status + next-ID)
- `HC-021` present in DB table: ✅ (appended row)
- No duplicate `HC-021` pre-existed: ✅ (highest prior ID was HC-020)
- **Next free ID:** HC-022

**Status:** ✅ Documented
