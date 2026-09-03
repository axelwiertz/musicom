# -*- coding: utf-8 -*-
"""Abstract layer dev probe: build F-minor-flavored pop network walk.

Plans:
- tonic pc 5 (F minor-ish anchor for the groove piece; bridge root Eb pc 3,
  subdominant Bb pc 10)
- Diatonic minor-ish field on F natural minor: Fm min5, Gm dim7, Ab maj8,
  Bbm min10, Cm min0, Db maj1, Eb maj3
- Pop anchor in F minor: Fm(5) Ab(8) Eb(3) Bbm(10)  [i VI VII iv]
- Home = Fm = min5 (subset contains pc 5 and pc 0? min5 = [5,8,0] -> root pc 5, 3rd pc 8, 5th pc 0 yes)
- Network + tension-curve walk for a 6-section form; print resulting walk.
"""
from rules.subset_network import PatternNetwork, standard_patterns, tension
import random

lib = {p.id: p for p in standard_patterns()}

# diatonic triads of F natural minor (F G Ab Bb C Db Eb) -> pc roots 5,7,8,10,0,1,3
field = ["min5", "dim7", "maj8", "min10", "min0", "maj1", "maj3"]
# add a couple of tetrad colors for tension curve freedom
field += ["min75", "maj78", "dom73", "min710"]  # min7 Fm, maj7 Ab, dom7 Eb, m7b5 Gm7b5? check ids exist
field = [f for f in field if f in lib]
print("field:", [(f, sorted(lib[f].subset), round(lib[f].tension, 1)) for f in field])

net = PatternNetwork([lib[f] for f in field])
# tension curve for intro->verse->chorus->verse2->chorus2->outro
curve = [0.4, 0.7, 1.2, 0.8, 1.4, 0.3]
for seed in (1, 2, 3, 4, 5, 6, 7, 8):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    print(f"seed {seed}:", w)
