# -*- coding: utf-8 -*-
"""Abstract layer dev probe: richer field with 7th chords; tension push to dom7."""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}

field = ["min5", "maj8", "min10", "min0", "maj1", "maj3", "dim7",
         "min75", "min710", "maj78", "dom73", "dom71"]
field = [f for f in field if f in lib]
net = PatternNetwork([lib[f] for f in field])
curve = [0.4, 0.7, 1.2, 0.8, 1.4, 0.3]
for seed in (11, 12, 13, 14, 15, 16):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    print(f"seed {seed}:", w, "tensions:", [round(lib[x].tension, 1) for x in w])
