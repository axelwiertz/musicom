# -*- coding: utf-8 -*-
"""Randomly select SP method + source composition for tonight's production job."""
import json
import random
import subprocess
from pathlib import Path

random.seed()  # no fixed seed - true nightly randomness

# ---- 1. Pick method from implemented registry, excluding last-7-days usage ----
sys_path = "/opt/data/repos/musicom"
import sys
sys.path.insert(0, sys_path)
from workflows.musicom_workflow import SP_METHODS

RECENT = {
    "SP-034",  # 2026-09-03
    "SP-032",  # 2026-09-02
    "SP-024",  # 2026-09-01
    "SP-017",  # 2026-08-31 + 2026-08-28
    "SP-014",  # 2026-08-29
}
pool = sorted(set(SP_METHODS.keys()) - RECENT)
method = random.choice(pool)
print(f"METHOD={method}")
print(f"METHOD_MODULE={SP_METHODS[method][0]}")
print(f"METHOD_DESC={SP_METHODS[method][1]}")

# ---- 2. Pick source composition: numbered projects under Styles, not Production ----
styles = Path("/opt/data/projects/Styles")
candidates = []
for mid in styles.rglob("*.mid"):
    rel = mid.relative_to(styles)
    parts = rel.parts
    if "Production" in parts:
        continue
    if "phase1" in mid.name or "daily" in mid.name or "candidates" in parts:
        continue
    if mid.stat().st_size < 40:
        continue
    candidates.append(str(mid))

candidates.sort()
src = random.choice(candidates)
print(f"SOURCE={src}")
print(f"POOL_SIZE={len(candidates)}")

# Also list all eligible pool for the report
print("POOL=" + json.dumps(pool))
