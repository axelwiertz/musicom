# -*- coding: utf-8 -*-
"""Nightly selection 2026-09-15: random style + method (seeded, auditable).

Pool logic mirrors night_2026-09-14.json: style pool = genre folders minus
exclusions minus last-6 nightly styles; method pool = cron-ready registry
code minus last-7-day methods; tonight = concrete (6th, cadence rule).
"""
import json
import os
import random

SEED = 20260915
random.seed(SEED)

STYLES_ROOT = "/opt/data/repos/musicom/projects/Styles"
EXCLUDE_DIRS = {"_Comparison", "_Data_Patterns", "Research", "Poetry",
                "Production", "Percussion", "Other",
                "016-genre-pattern-dataset", "Celtic "}
RECENT_STYLES = {"Celtic", "Baroque", "Disco", "Rock", "African", "Klezmer"}

pool = sorted(d for d in os.listdir(STYLES_ROOT)
              if os.path.isdir(os.path.join(STYLES_ROOT, d))
              and d not in EXCLUDE_DIRS)
eligible_styles = [d for d in pool if d not in RECENT_STYLES]
style = random.choice(eligible_styles)

CRON_POOL = ["001", "010", "012", "018", "023", "040", "079",
             "ABS-001", "ABS-002", "ABS-003", "ABS-004", "ABS-005", "HC-012"]
LAST7 = {"ABS-002", "003", "018", "012", "010", "079"}
CONCRETE = {"001", "023", "040", "HC-012"}
eligible_methods = [m for m in CRON_POOL
                    if m in CONCRETE and m not in LAST7]
method = random.choice(eligible_methods)

rec = {
    "run_date": "2026-09-15",
    "seed": SEED,
    "style_pool_n": len(pool),
    "style_eligible_n": len(eligible_styles),
    "style": style,
    "layer": "concrete",
    "cadence": ("concrete (prior abstract runs 085/087/089/090; "
                "091/092/093/094/095 concrete)"),
    "candidate_pool": [m for m in CRON_POOL if m not in LAST7],
    "excluded_recent": sorted(LAST7),
    "method": method,
}
out = os.path.join("/opt/data/repos/musicom/projects/Research/selection",
                   "night_2026-09-15.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(rec, f, indent=2)
print(json.dumps(rec, indent=2))
print("wrote", out)
