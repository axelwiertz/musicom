# -*- coding: utf-8 -*-
"""Abstract dev probe: debug — net.walk scoring bug? neighbors are Triads only?"""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}
roots = [5, 7, 8, 10, 0, 1, 3]
field = []
for r in roots:
    field += [f"maj{r}", f"min{r}", f"dim{r}", f"maj7{r}", f"min7{r}", f"dom7{r}"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])
print("patterns:", sorted(net.patterns))
print("--- neighbors of min5:")
for e in net.neighbors("min5"):
    print(" ", e.b, e.rel, round(e.weight,2), "T=", round(lib[e.b].tension,1))
