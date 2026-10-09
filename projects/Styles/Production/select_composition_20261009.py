# -*- coding: utf-8 -*-
"""Nightly composition selection: style + method (layered methodology)."""
import os, json, random

STYLES_ROOT = "/opt/data/projects/Styles"
EXCLUDED_STYLES = {"_Comparison", "_Data_Patterns", "Research", "Poetry",
                   "Production", "Percussion", "Other", "Celtic "}

styles = sorted(d for d in os.listdir(STYLES_ROOT)
                if os.path.isdir(os.path.join(STYLES_ROOT, d))
                and d not in EXCLUDED_STYLES and not d.startswith("_"))

# Method ID -> layer (from methods_db.md algorithmic table, IDs 001..110)
ABSTRACT = {95, 99, 104}
ALL_METHODS = list(range(1, 111))
concrete = [m for m in ALL_METHODS if m not in ABSTRACT]

# Exclude methods used in the last 7 days (projects 220..231 + reworks)
EXCLUDE = {7, 10, 11, 12, 19, 25, 39, 40, 41, 50, 94, 95, 104}

concrete_avail = [m for m in concrete if m not in EXCLUDE]
abstract_avail = [m for m in ABSTRACT if m not in EXCLUDE]

seed = 20261009
rng = random.Random(seed)
layer_roll = rng.random()  # ~6/7 concrete, ~1/7 abstract
if layer_roll < 1.0 / 7.0 and abstract_avail:
    layer = "abstract"
    method = rng.choice(abstract_avail)
else:
    layer = "concrete"
    method = rng.choice(concrete_avail)

style = rng.choice(styles)

out = {
    "date": "2026-10-09",
    "seed": seed,
    "layer_roll": layer_roll,
    "layer": layer,
    "method_id": f"{method:03d}",
    "style": style,
    "excluded_last7d": sorted(EXCLUDE),
    "n_styles": len(styles),
    "n_concrete_avail": len(concrete_avail),
}
print(json.dumps(out, indent=2))
with open("/opt/data/projects/Styles/Production/.composition_selection.json", "w") as f:
    json.dump(out, f, indent=2)
