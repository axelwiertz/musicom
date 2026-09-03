# -*- coding: utf-8 -*-
"""Abstract dev probe: simulate a full 6-section walk with richer anchors.

F-minor groove field, tension curve forces dom7 at peak; print + sanity.
"""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}
roots = [5, 7, 8, 10, 0, 1, 3]
field = []
for r in roots:
    field += [f"maj{r}", f"min{r}", f"dim{r}", f"maj7{r}", f"min7{r}", f"dom7{r}"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])

curve = [2.2, 3.5, 6.0, 4.0, 7.0, 2.0]
results = []
for seed in range(50, 80):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    results.append(w)
# print unique
seen = set()
for w in results:
    k = tuple(w)
    if k not in seen:
        seen.add(k)
        print("seed", results.index(w) + 50, w)
print("unique walks:", len(seen))
