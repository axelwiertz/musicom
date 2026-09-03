# -*- coding: utf-8 -*-
"""Random pick probe: concrete rolls."""
import re, random
methods = []
txt = open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8").read()
for m in re.finditer(r"^\|\s*\*\*(\d{3})\*\*\s*\|\s*concrete\s*\|", txt, re.M):
    methods.append(int(m.group(1)))
EXCL = {11, 18, 19, 22, 25, 32, 40, 48}
pool = [m for m in methods if m not in EXCL]
r = random.SystemRandom()
print(r.choice(pool))
