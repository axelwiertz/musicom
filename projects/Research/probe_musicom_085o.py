# -*- coding: utf-8 -*-
"""Abstract dev probe: score = weight + (tension-target)**2 — makes high
tension target reach 7ths (score 1.5+25=~26 too big? No: (7-1.4)^2=31).

The real fix: walk() scores against CURVE but only edges to TRIAD
neighbors ever make the top-3 because 7th chords need weight 1.0-2.5 +
(7-target) which still beats triad 0.5+(2-target) when target >= 3. Let's
verify: target 1.4: triad score 0.5+0.6=1.1; dom7(7.0) 1.5+5.6=7.1. No.
Walk() can never choose 7ths with targets 0.4-1.4 since ALL tensions are
2.0+; to reach 7ths the TARGET must be ~6-7 AND the top-3 pool must include
them. Set curve = [2.2, 3.5, 6.0, 4.0, 7.0, 2.0] (absolute tension targets).
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
# absolute tension targets: intro ~2 (triad), verse ~3.5, chorus 6 (7th),
# verse2 4, chorus2 7 (dom7 peak), outro 2 (resolve home)
curve = [2.2, 3.5, 6.0, 4.0, 7.0, 2.0]
for seed in (41, 42, 43, 44, 45, 46):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    print(f"seed {seed}:", w, "T:", [round(lib[x].tension, 1) for x in w])
