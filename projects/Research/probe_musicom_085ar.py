# -*- coding: utf-8 -*-
"""Random pick probe: use runpy-style separate process for ONE draw."""
import os, random, re, sys
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
txt = open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8").read()
methods = [int(m.group(1)) for m in re.finditer(r"^\|\s*\*\*(\d{3})\*\*\s*\|\s*concrete\s*\|", txt, re.M)]
EXCL = {11, 18, 19, 22, 25, 32, 40, 48}
pool = [m for m in methods if m not in EXCL]
r = random.SystemRandom()
roll = r.randint(1, 7)
layer = "abstract" if roll == 7 else "concrete"
style = r.choice(cands)
m = r.choice(pool) if layer == "concrete" else "ABS-002"
print(f"LAYER={layer}")
print(f"STYLE={style}")
print(f"METHOD={m}")
