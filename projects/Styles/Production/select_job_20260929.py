#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer-aligned production job: select composition + SP method (2026-09-29)."""
import json
import random
import re
import time
from pathlib import Path

random.seed(20260929)  # date-based, reproducible

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


def has_source(p):
    cur = p
    for _ in range(4):
        if (cur.parent / "compose.py").exists() or (cur.parent / "src").exists():
            return True
        cur = cur.parent
    return False


with_src = [p for p in candidates if has_source(p)]
pool = with_src if len(with_src) >= 5 else candidates
selected = random.choice(pool)

# 2. SP method selection from registry
from workflows.musicom_workflow import SP_METHODS  # noqa: E402

all_methods = sorted(SP_METHODS.keys())

prod = ROOT / "Production"
recent = set()
if prod.exists():
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
    "date": "2026-09-29",
    "seed": 20260929,
    "method": method,
    "method_module": method_module,
    "method_desc": method_desc,
    "source_midi": str(selected),
    "source_project": str(selected.relative_to(ROOT)),
    "registry_size": len(all_methods),
    "all_methods": all_methods,
    "recent_excluded": sorted(recent),
    "baseline_excluded": sorted(baseline_excluded),
    "pool_methods": pool_methods,
    "n_candidates": len(candidates),
}

sel_file = prod / ".selection_cron.json"
sel_file.write_text(json.dumps(out, indent=2))

print("SELECTED_MIDI=" + str(selected))
print("SELECTED_PROJECT=" + str(selected.relative_to(ROOT)))
print("SELECTED_METHOD=" + method)
print("METHOD_MODULE=" + method_module)
print("METHOD_DESC=" + method_desc)
print("REGISTRY_SIZE=" + str(len(all_methods)))
print("RECENT_EXCLUDED=" + ",".join(sorted(recent)))
print("POOL_SIZE=" + str(len(pool_methods)))
print("N_CANDIDATES=" + str(len(candidates)))
