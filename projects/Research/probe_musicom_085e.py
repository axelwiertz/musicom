# -*- coding: utf-8 -*-
"""Probe: rules.subset_network usage — walk a network, print patterns."""
from rules.subset_network import (
    PatternNetwork, patterns_from_degrees, standard_patterns,
    tension, complement_pcs, interval_vector,
)
import random

# 1. Check standard library has min7/dom7/maj7 tetrad ids used by prior ABS walk
lib = {p.id: p for p in standard_patterns()}
print("lib ids sample:", sorted(lib)[:20], "... total", len(lib))

# 2. Pop progression on C = 0
prog = patterns_from_degrees(0, ("I", "V", "vi", "IV"))
print("pop prog C:", [(p.id, sorted(p.subset), round(p.tension, 2)) for p in prog])

# 3. Network on the pop set
net = PatternNetwork(prog)
start = prog[0].id
print("start:", start)
walk = net.walk(start, 5, rng=random.Random(7), tension_curve=[0.5, 1.0, 1.5, 2.0, 0.8])
print("walk:", walk)

# 4. Z-pair check
print("z0146 icv:", interval_vector(frozenset({0, 1, 4, 6})),
      "z0137 icv:", interval_vector(frozenset({0, 1, 3, 7})))
print("maj0 icv:", lib["maj0"].icv, "tension:", lib["maj0"].tension)
print("dom7 icv:", lib["dom7" if "dom7" in lib else "maj0"].icv if "dom7" in lib else "no-dom7")

# 5. Explore walk options on a richer set: triads+tetrads of a harmonic field
# check which ids contain a given pc root
for pid in ("min9", "maj5", "maj7", "dom7", "min0", "maj0"):
    if pid in lib:
        print(pid, sorted(lib[pid].subset), "root pc 0 present:", 0 in lib[pid].subset,
              "root pc 7 present:", 7 in lib[pid].subset, "root pc 9:", 9 in lib[pid].subset)
