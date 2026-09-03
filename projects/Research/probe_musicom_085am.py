# -*- coding: utf-8 -*-
"""Random pick probe: 3 independent style+method picks (concrete weights).

Exclude methods used in last 7 days: 040, 048, 011/025/032/018 (from
078-084 reports) plus 075/084 used latest. We'll do a wide exclusion of
ids used in projects 077-084: 022 (077 Klezmer), 025 (080), 032 (079),
018 (081), 040 (082), 048 (083), 011 (084). Also any method used in 078?
078 report not found; 078-soul-voiceleading method? skip — 078 bugfix
soul; exclude 048/040/etc anyway + method 073's 048 and 084's 011, 076
Reggae 019? unknown. Simple robust exclusion set: {019, 011, 018, 022,
025, 032, 040, 048}. 
"""
import os, random, re

methods = []
txt = open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8").read()
for m in re.finditer(r"^\|\s*\*\*(\d{3})\*\*\s*\|\s*concrete\s*\|", txt, re.M):
    methods.append(int(m.group(1)))
print("concrete methods:", len(methods), sorted(methods))
EXCL = {11, 18, 19, 22, 25, 32, 40, 48}
pool = [m for m in methods if m not in EXCL]
print("pool after 7-day exclusion:", len(pool), sorted(pool))

# unused pick: use SystemRandom
r = random.SystemRandom()
for _ in range(3):
    print("pick:", r.choice(pool))
