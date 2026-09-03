# -*- coding: utf-8 -*-
"""Random pick probe: style pick — sample a few draws."""
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
        cands.append(d)
r = random.SystemRandom()
from collections import Counter
c = Counter(r.choice(cands) for _ in range(5))
print(c)
