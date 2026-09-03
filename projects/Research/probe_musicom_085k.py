# -*- coding: utf-8 -*-
"""Abstract layer dev probe: correct ids — tetrads = maj7R/min7R/dom7R."""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}
roots = [5, 7, 8, 10, 0, 1, 3]
field = []
for r in roots:
    field += [f"maj{r}", f"min{r}", f"dim{r}", f"maj7{r}", f"min7{r}", f"dom7{r}"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])
curve = [0.4, 0.7, 1.2, 0.8, 1.4, 0.3]
for seed in (31, 32, 33, 34, 35, 36):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    print(f"seed {seed}:", w, "T:", [round(lib[x].tension, 1) for x in w])
