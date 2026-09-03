# -*- coding: utf-8 -*-
"""Abstract dev probe: chord-tone derivation from walked subset per section.

Given a walked pattern per section (subset of pcs), derive per-bar chord
tones for voices (lead pool, comp, bass root) in absolute MIDI pitches.

Seed 41 walk: [min5 Fm, maj5 ? pc {0,5,9}=F? root pc 5 = F major {0,5,9},
maj71 Abmaj7? pc {1,4,8,11} wait maj71 = {1,4,8,11} root pc 1 = Db? check,
dim5 G? {0,6,9}? , dom71, min5]
"""
from rules.subset_network import standard_patterns
lib = {p.id: p for p in standard_patterns()}
for pid in ("min5", "maj5", "maj71", "dim5", "dom71", "min0", "maj3", "min10", "maj8"):
    p = lib.get(pid)
    if p:
        print(pid, sorted(p.subset), "T=", p.tension)
