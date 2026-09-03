# -*- coding: utf-8 -*-
"""Abstract layer dev probe: tension-bias walk on full standard lib network.

Build a network from the whole standard library filtered to a key-ish
subset, but include ALL 7th chords on roots of F minor (5,8,10,0,1,3)
plus their triads; let tension-curve scores pull to 7ths at peaks.
"""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}

# roots of F natural minor scale: pc 5(F) 7(G) 8(Ab) 10(Bb) 0(C) 1(Db) 3(Eb)
roots = [5, 7, 8, 10, 0, 1, 3]
field = []
for r in roots:
    field += [f"maj{r}", f"min{r}", f"dim{r}", f"aug{r}",
              f"maj7{r}", f"min7{r}", f"dom7{r}"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])
curve = [0.4, 0.7, 1.2, 0.8, 1.4, 0.3]
for seed in (21, 22, 23, 24, 25, 26):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    print(f"seed {seed}:", w, "T:", [round(lib[x].tension, 1) for x in w])
