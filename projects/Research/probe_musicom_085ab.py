# -*- coding: utf-8 -*-
"""Abstract dev probe: verify deterministic walk for chosen seed 90 with
home bias; print pattern/section names + tension to embed in REPORT."""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}
field = ["min5", "dim7", "maj8", "min10", "min0", "maj1", "maj3",
         "min75", "min710", "min77", "maj78", "min70", "maj71"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])
curve = [2.2, 3.5, 5.5, 4.0, 5.5, 2.0]
rng = random.Random(90)
w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
print("walk:", w)
for x in w:
    p = lib[x]
    print(x, sorted(p.subset), "T=", p.tension, "icv=", p.icv)
