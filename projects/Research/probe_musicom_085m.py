# -*- coding: utf-8 -*-
"""Abstract dev probe: score = weight + |tension diff|; with low triads and
high 7ths (0.5-2.5 vs 5-7) the score diff ~0 is enough for ties; the pool of
3 best could include 7ths at peaks. Check manually step-by-step for seed 31."""
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

def step_scores(cur, target):
    scored = []
    for e in net.neighbors(cur):
        t = net.patterns[e.b].tension
        scored.append((round(e.weight + abs(t - target), 2), e.b, round(e.weight,2), t))
    scored.sort()
    return scored[:8]

cur = "min5"
for step in range(1, 6):
    target = curve[step] if step < len(curve) else None
    print("step", step, "cur", cur, "target", target)
    if target is not None:
        for s in step_scores(cur, target):
            print("   ", s)
    cur = "min5"  # placeholder; manual walk later
    break
