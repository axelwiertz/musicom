# -*- coding: utf-8 -*-
"""Abstract layer dev probe: debug why walk stays on triads."""
from rules.subset_network import PatternNetwork, standard_patterns, voice_leading_distance
from rules.subset_network import PatternNetwork as _PN
_relations = _PN._relations
import random

lib = {p.id: p for p in standard_patterns()}
field = ["min5", "maj8", "min10", "min0", "maj1", "maj3", "dim7",
         "min75", "min710", "maj78", "dom73", "dom71"]
net = PatternNetwork([lib[f] for f in field])

# what neighbors does min5 have, sorted by weight?
for e in net.neighbors("min5"):
    print("min5 ->", e.b, e.rel, round(e.weight, 2), "T=", round(lib[e.b].tension, 1))

print("---")
# relations of min5 vs dom71 and min5 vs min710
for b in ("dom71", "min710", "maj78", "min75"):
    print("min5 vs", b, _relations(lib["min5"], lib[b]))
