#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Select random SP method (excluding last-7-days) + source composition."""
import os, random, sys

sys.path.insert(0, "/opt/data/repos/musicom")
PROD = "/opt/data/projects/Styles/Production"

recent = set()
for name in os.listdir(PROD):
    p = os.path.join(PROD, name)
    if os.path.isdir(p):
        recent.add(name)

from workflows.musicom_workflow import SP_METHODS
pool = sorted(SP_METHODS)
recent_prefix = {n[:6] for n in recent if n.startswith("SP")}
avail = [m for m in pool if m not in recent_prefix]
if len(avail) < 4:
    avail = ["SP-001"]

rng = random.SystemRandom()
method = rng.choice(sorted(avail))
print("recent_prefixes:", sorted(recent_prefix))
print("pool:", pool)
print("available:", sorted(avail))
print("CHOSEN_METHOD:", method)

cands = []
for root, dirs, files in os.walk("/opt/data/projects/Styles"):
    dirs[:] = [d for d in dirs if d != "Production"]
    if "compose.py" in files:
        mids = [f for f in files if f.endswith(".mid")]
        if mids:
            cands.append(root)
cands = sorted(cands)
print("n_candidates:", len(cands))
for c in cands:
    print("  ", c)
if cands:
    src = rng.choice(cands)
    print("CHOSEN_SRC:", src)
