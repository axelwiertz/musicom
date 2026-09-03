# -*- coding: utf-8 -*-
"""Probe: random style pick from allowed genres (folder dirs under Styles).

Allowed: genre folders with at least one numbered project and not in the
exclude list. List candidates with counts to weight evenly.
"""
import os, random
STYLES = "/opt/data/projects/Styles"
EXCLUDE = {"016-genre-pattern-dataset", "_Comparison", "_Data_Patterns",
           "Research", "Poetry", "Production", "Percussion", "Other"}
cands = []
for d in sorted(os.listdir(STYLES)):
    p = os.path.join(STYLES, d)
    if not os.path.isdir(p) or d in EXCLUDE:
        continue
    n = [x for x in os.listdir(p) if x[:3].isdigit() and os.path.isdir(os.path.join(p, x))]
    if n:
        cands.append((d, len(n)))
for c in cands:
    print(c)
print("TOTAL candidates:", len(cands))
r = random.SystemRandom()
print("pick:", r.choice(cands))
