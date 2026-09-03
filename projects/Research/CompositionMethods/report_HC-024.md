# Report — HC-024: Graphic Score & Indeterminate Notation Practice

- **Method ID:** HC-024
- **Method Name:** Graphic Score & Indeterminate Notation Practice (Open-Form / Mobile-Form Composition)
- **Tradition / Culture:** Western Classical — experimental & avant-garde (New York School: Cage, Brown, Feldman, Wolff; European: Cardew, Crumb, Penderecki, Logothetis), ~1950s–present. Ancestors: Ars subtilior "eye music" (~1400, Baude Cordier's heart-shaped *Belle, Bonne, Sage*) and 18th-c. musical dice games (*Musikalisches Würfelspiel*, Mozart/Kirnberger).
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix.
- **Date researched:** 2026-09-02 (nightly `daily-human-composition-research` job)
- **Status:** ✅ Documented

---

## 1. Method overview

Graphic-score practice is the **human craft of leaving a score deliberately open** so the
performer co-composes. Instead of fixing every pitch and rhythm, the composer draws a
*visual instruction* — a shape, a field, a mobile, a set of numbered modules, a page with no
clefs — and the performer translates that image into sound in real time. The score is a
**map, not a territory**: it constrains *what kind* of sound to make while freeing *which
specific notes* are played.

Two distinct human-craft families (neither is algorithmic generation):

1. **Indeterminacy of performance** (Cage, Brown, Feldman, Cardew, Logothetis): the score
   is fixed as an *image or rule-set*, but the realization varies every performance. The
   composer designs a **generative contract** with the performer.
2. **Mobile / open form** (Brown, Stockhausen, Boulez, Pousseur): fully notated *modules*
   whose *order* is free — the performer/conductor assembles the piece live, like Alexander
   Calder's hanging mobiles.

The composer's craft is therefore **meta-composition**: designing the freedom, bounding the
possibilities, and judging whether the *range* of possible realizations still all "read" as
one piece (identity retention).

## 2. Craft procedure (how a human does it)

1. **Decide what to free and what to fix.** The first act is a design decision: *which
   parameter stays composed and which is handed to the performer?* Freedom axes: (a) note
   order, (b) note choice within a pitch field/register, (c) tempo, (d) duration/proportion,
   (e) instrumentation. Everything not freed is nailed down. Feldman's grid scores fix *when
   and how many* but not *which*; Brown's *Twenty-Five Pages* fixes the notes but frees order
   and orientation; Cage's *Concert for Piano and Orchestra* frees almost everything.

2. **Draw / notate the instruction.** Translate an intended sound-world into a non-standard
   notation: a graphic (lines, shapes, densities, colours), a grid with boxes and numbers,
   an instruction text, or "time/proportional notation" (horizontal length = duration,
   vertical position = register). Crumb bent staves into circles and arches; Logothetis drew
   pure visual scores; Brown notated symmetrically without clefs so pages were reversible.

3. **Bound the freedom with a legend / rule-set.** Almost always the score carries a written
   key: "play these notes in any order", "higher on the page = higher pitch", "density of
   marks = density of notes", "the conductor points to a page and cues a downbeat". The
   legend is what keeps the piece from collapsing into pure improvisation — it is the
   *generative contract*.

4. **For open/mobile form: compose self-contained modules.** Each module (an "event", a
   "page", a "paragraph", a "group") is fully notated and internally coherent, but the
   *sequence* is chosen live. Brown's *Available Forms* and *Twenty-Five Pages* (1–25
   pianists, pages re-orderable, top/bottom reversible); Stockhausen's *Klavierstück XI*
   (19 groups on one sheet, any order); Cardew's *The Great Learning* "Paragraphs".

5. **For graphic/indeterminate scores: compose a field of possibilities.** Instead of
   modules, draw a bounded space of sound: a pitch cluster to sustain, a register band to
   wander in, a text prompt to react to (Cardew's *Treatise*, a 193-page abstract drawing
   with no legend — performers must invent their own mapping). The craft is *choosing the
   field's boundaries* so any point inside sounds like "the piece".

6. **Stress-test for identity retention.** The composer's hardest question: *is it the same
   piece on every run?* The answer lies in what was fixed. If enough is pinned (a register, a
   density curve, a pitch set, a module vocabulary), two performances differ yet recognizably
   share a "face". If too much is freed, the piece has no identity.

7. **Notate the performer's role explicitly.** Amateur/collective vs virtuoso: the Scratch
   Orchestra (Cardew, Skempton, Parsons) wrote graphic/text scores playable by non-musicians,
   turning the audience into co-composers. Brown's open-form pieces assume a conductor who
   *directs* assembly live. The composer must specify the *agency model*.

## 3. Real practitioner examples

- **Earle Brown** — *December 1952* (purely graphic: horizontal and vertical lines, no
  legend); *Twenty-Five Pages* (1953, 25 unbound pages, 1–25 pianists, order + orientation
  free); *Available Forms I & II* (1961–62, "open form": conductor cues numbered events via
  placard — left hand = which event, right hand = downbeat, speed/intensity of downbeat =
  tempo/dynamics). Calder mobiles + Pollock action painting as explicit models.
- **John Cage** — *Concert for Piano and Orchestra* (1957–58, notation "E" gives the
  performer a choice of clefs); *Variations* series; *4'33"* as the limiting case (score =
  instruction, no fixed notes at all).
- **Morton Feldman** — grid notation: specifies *how many* notes and *when* but not *which*;
  *Projection* and *Intersection* series; his signature quiet, floating, asymmetric-pattern
  sound emerged *from* the notational freedom.
- **Cornelius Cardew** — *Treatise* (1963–67, 193-page abstract graphic score, no legend);
  *The Great Learning* (7 "Paragraphs" after Confucius via Ezra Pound, text scores → founding
  repertoire of the Scratch Orchestra, playable by non-musicians).
- **Karlheinz Stockhausen** — *Klavierstück XI* (1956, 19 notated groups on one sheet, played
  in any order, stop when any group is played a third time = mobile form).
- **Krzysztof Penderecki** — *Threnody to the Victims of Hiroshima* (1960): graphic
  "time-box" notation for 52 strings — pitch blocks, thick lines, symbols for highest
  note/cluster/glissando; a graphic score that is nonetheless *precisely* timed.
- **George Crumb** — *Makrokosmos*, *Black Angels*, *Vox Balaenae*: circular/bent staves,
  facsimile manuscripts, pictorial symbols carrying specific extended-technique instructions.
- **Anestis Logothetis** — Greek-Austrian pioneer of the *pure visual score* (Polymorphia),
  where the drawing alone is the music.

## 4. UnitMatrix mapping (Musicom engine)

The graphic/open-form craft maps cleanly onto the UnitMatrix because the engine's Voices &
Sections grid is *exactly* the "fixed scaffold" a human composer designs, and the freedom the
composer grants becomes the *realization rules* the engine applies.

**Voices (the composer's freedom partition):**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Fixed spine (the composed invariant) | The parameter(s) the composer *keeps*: a register band, a density curve, a pitch set, an accent grid. Never randomized — this is what preserves piece identity. | STRUCTURE (anchor) |
| V1 | Realization layer 1 | Performer/engine fills the freed axis: note choice within the field, module order. | PITCH |
| V2 | Realization layer 2 / second field | A second independent freedom (e.g. proportional duration vs register placement). | RHYTHM |
| V3 | Texture/gesture field | Density-of-marks → density-of-events mapping; cluster/glissando/noise gestures (Penderecki's thick lines). | TEXTURE |

**Sections = mobile-form modules or graphic fields:**

```
S0 Module A (statement) → S1 Module B (contrast) → S2 Module C (return/apex) → ...
   — order chosen by conductor/engine per performance (open form)
   OR
S0 Field "low register cluster" → S1 Field "mid wandering" → S2 Field "high shimmer"
   — each section = one graphic field, its internal notes free (indeterminate)
```

**Rules that encode the craft (deterministic scaffold + bounded stochastic realization):**

- `freedom-partition`: declare per voice which parameter is fixed (FIX) vs freed (FREE); FIX set is non-empty (identity guarantee).
- `identity-retention`: realization must keep the FIX parameters invariant; a candidate event violating a FIX bound is rejected (this is the "same piece every time" judgement).
- `module-composition`: mobile form = N fully-notated modules, order permuted; each module internally coherent.
- `module-permutation`: order chosen by a selector (conductor cue = seed), optionally constrained (no immediate repeat, first = opener, last = closer).
- `field-bounds`: for graphic fields, define pitch register [lo, hi], density range, and gesture vocabulary; events sampled within bounds.
- `density-from-marks`: density of notation marks → event density (Feldman's grid: how many, not which).
- `proportional-notation`: horizontal length ∝ duration, vertical position ∝ register (Brown's time notation).
- `orient-invariance`: reversible/uncleffed pages → register can be inverted without breaking identity (*Twenty-Five Pages*).
- `legend-as-contract`: the score's key text is compiled into the rule set verbatim — no rule, no legend, no realization.
- `agency-model`: amateur (text/graphic prompt, any instrument) vs conductor-directed (placard/event cueing) vs virtuoso (precise extended technique) — determines realization strictness.

## 5. Table row added

```
| HC-024 | human (→concrete) | Graphic Score & Indeterminate Notation Practice (Open-Form / Mobile-Form Composition) | Western Classical — experimental & avant-garde (New York School: Cage, Brown, Feldman, Wolff; European: Cardew, Crumb, Penderecki, Logothetis), ~1950s–present; ancestors Ars subtilior "eye music" (~1400) + 18th-c. musical dice games | STRUCTURE, TEXTURE, PITCH, RHYTHM | Decide what to free vs fix (order/note-choice/tempo/duration/instrumentation) → draw the instruction (shape/grid/time-proportional notation/text) → bound the freedom with a legend/rule-set → for mobile form compose self-contained notated modules (order free) → for graphic fields compose a bounded possibility space (register band, density, gesture vocabulary) → stress-test identity retention (same piece every performance?) → notate the performer's agency model (amateur text score / conductor-cued / virtuoso) | Voice 0 = fixed spine ... agency-model | Earle Brown (December 1952; Twenty-Five Pages 1953; Available Forms 1961–62 ...), John Cage (...), Morton Feldman (...), Cornelius Cardew (...), Karlheinz Stockhausen (...), Krzysztof Penderecki (...), George Crumb (...), Anestis Logothetis (...) | ✅ Documented |
```

(Full untruncated row is in `human_methods_db.md` line 31.)

## 6. Verification

- `HC-024` present in detail file `human_method_HC-024_graphic-score-indeterminate-notation.md` ✅
- `HC-024` present in `human_methods_db.md` framework table ✅
- No duplicate HC-024 rows in the table ✅
- **Next free ID: HC-025**

## 7. Quirks / pitfalls

- **Identity collapse.** Free too much and the piece becomes anonymous improvisation; free
  too little and it is just a scored piece. The whole craft is *calibrating* the FIX/FREE
  partition. Brown's rule of thumb: keep enough fixed that no two performances are the same,
  yet each is recognizably the work.
- **No-legend trap.** A pure drawing with no key (Cardew's *Treatise*) is maximally open but
  risks *arbitrary* realization — the performer may invent a mapping the composer never
  imagined. The composer accepts this or writes a legend.
- **Legend IS the score.** For text/graphic scores the *written instruction* is the piece —
  losing or misreading the key text loses the work. In the engine the rule set must be
  versioned with the score.
- **"Indeterminate" ≠ "random".** Human graphic practice is *bounded choice by a thinking
  performer*, not a dice roll. The engine's realization must be *constrained sampling within
  a field*, not uniform noise — otherwise it sounds aleatoric (dice-game) rather than
  open-form.
- **Timing precision vs freedom.** Penderecki's Threnody looks free but is *exactly timed* in
  time-boxes; Brown's open form is free *in order* but exact *in content*. Do not conflate
  which axis is freed.

## Source

Wikipedia — "Graphic notation (music)", "Indeterminacy (music)", "Aleatoric music",
"Earle Brown", "Morton Feldman", "Cornelius Cardew", "Krzysztof Penderecki", "George Crumb".
Retrieved for this entry (2026-09-02).
