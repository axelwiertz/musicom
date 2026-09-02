# 12TET Subset Theory — Z-relations, Interval Vectors, Parsimonious Voice Leading

Forte/Straus pitch-class set theory applied generatively. Subsets of 12TET
= chords, scales, pitch pools. Pattern = one subset. Chord progression =
a walk through subset space. Tension/resolution = (dis)similarity between
successive subsets.

## Core definitions

- **Pitch class (pc)**: `pitch % 12`. C=0, C#=1, ..., B=11.
- **Subset**: a set of pcs, e.g. major triad `{0,4,7}`, D dorian `{2,4,5,7,9,11,0}`.
- **Interval class (ic)**: unordered interval in semitones, min(d, 12-d), ic ∈ 1..6.
- **Interval-class vector (ICV)**: 6 counts `[ic1, ic2, ic3, ic4, ic5, ic6]`
  of each interval class among all pairs of a subset. Major triad {0,4,7} →
  [0,0,1,1,1,0]. Implementation: `rules/set_theory.py :: interval_vector`.

## Forte names / prime forms

Every subset (up to transposition/inversion) has a canonical **prime form**
(smallest normal form, zero-based, most left-packed) — implementation:
`rules/set_theory.py :: prime_form`. Forte numbers the classes: 3-1 = {0,1,2}
chromatic trichord ... 3-11 = {0,4,7} major triad, 3-10 = {0,3,6} diminished,
4-27 = {0,2,5,8} half-dim/dominant-ish tetrachord, 4-28 = {0,3,6,9}
fully-diminished 7th (the most symmetrical tetrachord, ICV [0,0,0,4,0,4]).

## Z-relations (the key generative idea)

Two subsets are **Z-related** when they share the same ICV but are NOT
transpositionally/inversionally equivalent (different prime form). Forte
Z-pairs among 4-note sets: 4-Z15 {0,1,4,6} / 4-Z29 {0,1,3,7}; 4-Z15A ... see
Forte's list. Among hexachords: 6-Z3/6-Z36, 6-Z4/6-Z37, 6-Z6/6-Z38, 6-Z10/6-Z39,
6-Z11/6-Z40, 6-Z12/6-Z41, 6-Z13/6-Z42, 6-Z17/6-Z43, 6-Z19/6-Z44, 6-Z23/6-Z45,
6-Z24/6-Z46, 6-Z25/6-Z47, 6-Z26/6-Z48, 6-Z28/6-Z49, 6-Z29/6-Z50.

Meaning: Z-partners have the **same interval content** (same "color"/tension
profile) but **different notes**. Generative use: swap a chord for its
Z-partner → same tension, fresh harmony, no resolution change. (Bartók,
Stravinsky, Webern exploited Z/complement relations.)

## Complementation

The **complement** of a k-note subset is the (12-k)-note subset of the
remaining pcs. Complement rule: ICV(complement) = (total_pairs - ICV) with ic6
adjusted by (n-6) — a 6-note set and its complement are always Z-related.
Complement of a chord = maximal-contrast "negative" harmony with a matched
tension profile.

## Consonance / dissonance from ICV (tension model)

Weight each ic by its acoustic consonance: ic3/ic4 (thirds/sixths) consonant,
ic5 (fourth/fifth) neutral, ic1/ic2 (seconds/sevenths) dissonant, ic6
(tritone) most dissonant. Tension of a subset ≈ weighted ICV sum:

    TENSION(ic) = w[ic] · count;  e.g. w = {1: 2.0, 2: 1.5, 3: 0.5, 4: 0.5, 5: 1.0, 6: 3.0}

Scale relative to a triad baseline. A **tension curve** across a form
(intro→verse→chorus→bridge→outro) then becomes: rise into chorus, peak at
bridge, resolve at outro — implemented by choosing successive subsets whose
tension follows the curve.

## Parsimonious voice leading (P/L/R and Tymoczko)

Neo-Riemannian theory (Cohn) for triads:
- **P** (parallel): change only the third, keep root+fifth: C maj ↔ C min.
- **L** (leading-tone): move the top note down a semitone: C maj ↔ E min.
- **R** (relative): move the top note up a whole tone: C maj ↔ A min.
- **N** (Nebenverwandt), **S** (Slide), **H** (hexatonic pole): other single/multi moves.

General principle (Tymoczko, "A Geometry of Music"): smooth voice leading =
minimal total semitone motion between two subsets; voice-leading distance =
the Euclidean distance between their closest embeddings. A progression feels
resolved when each voice moves ≤ 2 semitones and the subsets share common
tones.

## Pattern = subset; progression = subset walk

Pattern holds the subset for one role/unit. The chord progression is the
sequence of patterns. The **(dis)similarity between consecutive subsets** —
via shared pcs, ICV distance, or z/complement relation — *is* the
tension/resolution logic. No functional labels (I/IV/V) needed: consonance and
dissonance fall out of the set relations.

## Generative recipe

1. Choose form + tension curve (e.g. [0.2, 0.4, 0.6, 0.8, 0.3] over 5 sections).
2. Seed with a home subset (e.g. major triad {0,4,7} or a pentatonic pool).
3. Walk the pattern network: prefer P/L/R moves (≤2 semitone VL) near home;
   allow larger leaps, z-swaps, complements at tension peaks.
4. Realize each unit: pitches = subset transposed into the voice register;
   rhythm = the unit's onset pattern; bass = roots of the subset.

## References

- Forte, A. (1973). *The Structure of Atonal Music*. Yale UP. — prime forms, ICV, Z-relations.
- Straus, J. (2016). *Introduction to Post-Tonal Theory* (4th ed.). Norton.
- Cohn, R. (2012). *Audacious Euphony: Chromaticism and the Triad's Second Nature*. — P/L/R.
- Tymoczko, D. (2011). *A Geometry of Music*. Oxford UP. — voice-leading distance, orbifolds.
- Rahn, J. (1980). *Basic Atonal Theory*.
