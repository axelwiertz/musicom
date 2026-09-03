# -*- coding: utf-8 -*-
"""Abstract dev probe: final pre-compose sanity for a per-BAR chord grid.

For groove feel the harmony should change per bar or per 2 bars, not hold
one subset for a whole 4-bar section. Approach: keep section-level subset
(pool) but derive 4 distinct bar chords by cycling the subset through
inversions/voicings — roots stay in subset: e.g. Fm section bars = Fm
(same) but bass moves F-C-F-C etc. That keeps audit trivially in-chord and
adds motion.

Better: each section has TWO subsets (walk gives one) - generate bar chords
by choosing for each bar one of: root-position subset, 1st inversion subset
(same pcs), plus a passing dim from scale (in-scale) at bar 4 leading back?
F minor groove (80 sieve) used i III iv V per bar. I will per-bar choose:
for section s with pattern id P, chords = [P, P, P, P] but with different
voicing each bar; if the walk provides an adjacent 7th color for section
peak etc. This is fine — abstract layer designed section-level pools;
per-bar voicing is concrete. Good.

Bass per bar: root octave pattern.
"""
print("ok")
