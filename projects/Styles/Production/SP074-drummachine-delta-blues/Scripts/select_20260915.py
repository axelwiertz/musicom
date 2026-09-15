# -*- coding: utf-8 -*-
"""Selector for 2026-09-15 nightly production job."""
import random
import json
from pathlib import Path

from workflows.musicom_workflow import SP_METHODS

seed = 20260915
rng = random.Random(seed)

all_methods = sorted(SP_METHODS)
print("ALL_METHODS:")
for k in all_methods:
    print(f"  {k}: {SP_METHODS[k]}")

recent_7d = ["SP-036", "SP-073", "SP-071", "SP-011", "SP-024", "SP-001", "SP-037"]
eligible = [m for m in all_methods if m not in recent_7d]
print(f"RECENT_7D={recent_7d}")
print(f"ELIGIBLE={eligible}")

method = rng.choice(eligible)
print(f"METHOD_PICK={method}")
print(f"MODULE={SP_METHODS[method]}")

roots = Path("/opt/data/repos/musicom/projects/Styles")
mids = [p for p in roots.rglob("*.mid") if "phase1" not in p.name and "Production" not in str(p)]
print(f"N_CANDIDATES={len(mids)}")
usable = [p for p in mids if p.stat().st_size > 40]
print(f"N_USABLE={len(usable)}")
usable_sorted = sorted(str(p) for p in usable)
for s in usable_sorted[:20]:
    print(f"  cand: {s}")
midi_pick = rng.choice(usable_sorted)
print(f"MIDI_PICK={midi_pick}")

out = {
    "seed": seed,
    "all_methods": all_methods,
    "recent_7d": recent_7d,
    "eligible": eligible,
    "method": method,
    "module": SP_METHODS[method][0],
    "desc": SP_METHODS[method][1],
    "midi_pick": midi_pick,
    "n_raw": len(mids),
    "n_usable": len(usable),
}
Path("/opt/data/select_20260915.json").write_text(json.dumps(out, indent=2))
print("WROTE /opt/data/select_20260915.json")
