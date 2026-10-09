#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-roll method selection (2026-10-09) to avoid exact source+method duplicate.

First draw (seed 20261009) picked SP-074 on Blues/blues-delta-daily-2026-06-24,
which is the EXACT pair already produced as Production/SP074-drummachine-delta-blues
(2026-09-15). Re-roll method only; keep the well-formed source.
"""
import json
import random
import re
import time
from pathlib import Path

SEED = 20261010  # bumped seed for a fresh draw
DATE = "2026-10-09"
random.seed(SEED)

ROOT = Path("/opt/data/repos/musicom/projects/Styles")
prod = ROOT / "Production"

SOURCE_REL = "Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid"
SOURCE_ABS = ROOT / SOURCE_REL

from workflows.musicom_workflow import SP_METHODS  # noqa: E402

all_methods = sorted(SP_METHODS.keys())

# methods used in last 7 days (Production dir mtimes)
recent = set()
now = time.time()
for d in prod.iterdir():
    if not d.is_dir():
        continue
    m = re.match(r"SP-?(\d+)", d.name)
    if not m:
        continue
    if (now - d.stat().st_mtime) / 86400.0 <= 7.0:
        recent.add("SP-" + m.group(1))

# methods already applied to THIS exact source (scan REPORT.md bodies)
already_on_source = set()
for d in prod.iterdir():
    rp = d / "REPORT.md"
    if not rp.exists():
        continue
    try:
        if "blues-delta-daily-2026-06-24" in rp.read_text(errors="ignore"):
            m = re.match(r"SP-?(\d+)", d.name)
            if m:
                already_on_source.add("SP-" + m.group(1))
    except Exception:
        pass

baseline_excluded = {"SP-001"}
excluded = recent | baseline_excluded | already_on_source
pool_methods = [m for m in all_methods if m not in excluded]
if len(pool_methods) < 4:
    pool_methods = [m for m in all_methods if m not in (baseline_excluded | already_on_source)]
if not pool_methods:
    pool_methods = [m for m in all_methods if m not in baseline_excluded]

method = random.choice(pool_methods)
method_module, method_desc = SP_METHODS[method]

out = {
    "job": "random-style production (SP) layer-aligned",
    "date": DATE,
    "seed": SEED,
    "re_roll": True,
    "re_roll_reason": "first draw SP-074 x blues-delta-daily-2026-06-24 == existing "
                      "Production/SP074-drummachine-delta-blues (exact source+method dup)",
    "method": method,
    "method_module": method_module,
    "method_desc": method_desc,
    "source_midi": str(SOURCE_ABS),
    "source_project": SOURCE_REL,
    "registry_size": len(all_methods),
    "recent_excluded": sorted(recent),
    "already_on_source": sorted(already_on_source),
    "baseline_excluded": sorted(baseline_excluded),
    "pool_methods": pool_methods,
}

sel_file = prod / ".selection_cron.json"
sel_file.write_text(json.dumps(out, indent=2))

print("SELECTED_MIDI=" + str(SOURCE_ABS))
print("SELECTED_PROJECT=" + SOURCE_REL)
print("SELECTED_METHOD=" + method)
print("METHOD_MODULE=" + method_module)
print("METHOD_DESC=" + method_desc)
print("REGISTRY_SIZE=" + str(len(all_methods)))
print("RECENT_EXCLUDED=" + ",".join(sorted(recent)))
print("ALREADY_ON_SOURCE=" + ",".join(sorted(already_on_source)))
print("POOL_SIZE=" + str(len(pool_methods)))
