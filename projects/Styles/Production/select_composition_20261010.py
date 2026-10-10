# -*- coding: utf-8 -*-
"""Nightly composition selection (2026-10-10): style + method + form."""
import os, json, random, re, time

STYLES_ROOT = "/opt/data/projects/Styles"
EXCLUDED_STYLES = {"_Comparison", "_Data_Patterns", "Research", "Poetry",
                   "Production", "Percussion", "Other", "Celtic "}

styles = sorted(d for d in os.listdir(STYLES_ROOT)
                if os.path.isdir(os.path.join(STYLES_ROOT, d))
                and d not in EXCLUDED_STYLES and not d.startswith("_"))

ABSTRACT = {95, 99, 104}
ALL_METHODS = list(range(1, 111))

# Exclude methods used in the last 7 days (scan recent project REPORT.md mtimes)
now = time.time()
recent_methods = set()
for root, dirs, files in os.walk(STYLES_ROOT):
    if "/Production/" in root or "/_Comparison/" in root or "/_Data_Patterns/" in root:
        continue
    if "REPORT.md" in files:
        rp = os.path.join(root, "REPORT.md")
        try:
            age_days = (now - os.path.getmtime(rp)) / 86400.0
        except OSError:
            continue
        if age_days > 7.0:
            continue
        body = open(rp, errors="ignore").read()
        for m in re.finditer(r"[Mm]ethod[^\n]{0,40}?\b(\d{3})\b", body):
            mid = int(m.group(1))
            if 1 <= mid <= 110:
                recent_methods.add(mid)

seed = 20261010
rng = random.Random(seed)

concrete = [m for m in ALL_METHODS if m not in ABSTRACT]
abstract = [m for m in ALL_METHODS if m in ABSTRACT]
concrete_avail = [m for m in concrete if m not in recent_methods]
abstract_avail = [m for m in abstract if m not in recent_methods]

layer_roll = rng.random()
if layer_roll < 1.0 / 7.0 and abstract_avail:
    layer = "abstract"
    method = rng.choice(abstract_avail)
else:
    layer = "concrete"
    method = rng.choice(concrete_avail)

style = rng.choice(styles)

# form
import sys
sys.path.insert(0, "/opt/data/repos/musicom")
from workflows.musicom_workflow import pick_form, form_to_sections, FORM_PALETTE
form = pick_form(style, rng=rng)
names, bars = form_to_sections(form)

out = {
    "date": "2026-10-10",
    "seed": seed,
    "layer_roll": round(layer_roll, 4),
    "layer": layer,
    "method_id": f"{method:03d}",
    "style": style,
    "form": form,
    "section_names": names,
    "bars_per": bars,
    "recent_methods_excluded": sorted(recent_methods),
    "n_styles": len(styles),
    "n_concrete_avail": len(concrete_avail),
    "n_abstract_avail": len(abstract_avail),
}
print(json.dumps(out, indent=2))
with open("/opt/data/projects/Styles/Production/.composition_selection.json", "w") as f:
    json.dump(out, f, indent=2)
