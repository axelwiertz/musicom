#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer-aligned production job: select composition + SP method."""
import json
import random
import re
from pathlib import Path

random.seed(20260925)  # date-based, reproducible like prior cron

ROOT = Path("/opt/data/repos/musicom/projects/Styles")

# 1. candidate MIDI files: not Production outputs, not phase1 drafts
candidates = []
for p in ROOT.rglob("*.mid"):
    s = str(p)
    if "/Production/" in s:
        continue
    if "phase1" in p.name:
        continue
    candidates.append(p)

assert candidates, "no candidate midi files"

# prefer source projects that have a compose.py / src near the midi
def has_source(p):
    d = p.parent
    # look up to project root for compose.py
    cur = p
    for _ in range(3):
        if (cur.parent / "compose.py").exists() or (cur.parent / "src").exists():
            return True
        cur = cur.parent
    return False

with_src = [p for p in candidates if has_source(p)]
pool = with_src if len(with_src) >= 5 else candidates
selected = random.choice(pool)

# 2. SP method selection from registry (read SP_METHODS via import)
import sys
sys.path.insert(0, "/opt/data/repos/musicom")
from workflows.musicom_workflow import SP_METHODS

all_methods = sorted(SP_METHODS.keys())

# methods used in last 7 days (from Production dir mtimes)
prod = ROOT / "Production"
recent = set()
if prod.exists():
    import time
    now = time.time()
    for d in prod.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"SP-?(\d+)", d.name)
        if not m:
            continue
        age_days = (now - d.stat().st_mtime) / 86400.0
        if age_days <= 7.0:
            recent.add("SP-" + m.group(1))

# baseline excluded (SP-001 is the trivial fallback; keep variety)
baseline_excluded = {"SP-001"}

pool_methods = [m for m in all_methods if m not in recent and m not in baseline_excluded]
if len(pool_methods) < 4:
    pool_methods = [m for m in all_methods if m not in baseline_excluded]
if not pool_methods:
    pool_methods = ["SP-001"]

method = random.choice(pool_methods)
method_module, method_desc = SP_METHODS[method]

out = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-25",
    "seed": 20260925,
    "method": method,
    "method_module": method_module,
    "method_desc": method_desc,
    "source_midi": str(selected),
    "source_project": str(selected.relative_to(ROOT)),
    "all_methods": all_methods,
    "recent_excluded": sorted(recent),
    "baseline_excluded": sorted(baseline_excluded),
    "pool_methods": pool_methods,
}

sel_file = prod / ".selection_cron.json"
sel_file.write_text(json.dumps(out, indent=2))

print("SELECTED_MIDI=" + str(selected))
print("SELECTED_METHOD=" + method)
print("METHOD_MODULE=" + method_module)
print("METHOD_DESC=" + method_desc)
print("RECENT_EXCLUDED=" + ",".join(sorted(recent)))
print("POOL_SIZE=" + str(len(pool_methods)))
