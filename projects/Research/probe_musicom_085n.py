# -*- coding: utf-8 -*-
"""Abstract dev probe: step-by-step walk debug."""
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

rng = random.Random(31)
seq = ["min5"]
cur = "min5"
for step in range(1, 6):
    nbrs = net.neighbors(cur)
    target = curve[step]
    scored = []
    for e in nbrs:
        t = net.patterns[e.b].tension
        scored.append((round(e.weight + abs(t - target), 2), e.b, round(e.weight, 2), t))
    scored.sort()
    top = scored[:8]
    print("step", step, "from", cur, "target", target)
    for s in top:
        print("   ", s)
    pool = [pid for _, pid, _, _ in scored[:3]]
    nxt = rng.choice(pool)
    print("   CHOICE:", nxt)
    seq.append(nxt)
    cur = nxt
print("SEQ:", seq)
