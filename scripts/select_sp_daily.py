import os
import glob
import json
import random
from pathlib import Path
from workflows.musicom_workflow import SP_METHODS

print(f"Total SP_METHODS registered: {len(SP_METHODS)}")

recent_7d = ["SP-080", "SP-083", "SP-084", "SP-072", "SP-074", "SP-036", "SP-073"]
print("Recent 7d:", recent_7d)

eligible_methods = [m for m in sorted(SP_METHODS.keys()) if m not in recent_7d]
print(f"Eligible methods count: {len(eligible_methods)}")

SEED = 20260921
rng = random.Random(SEED)
chosen_method = rng.choice(eligible_methods)
print(f"Chosen method: {chosen_method} -> {SP_METHODS[chosen_method]}")

styles_dir = Path("/opt/data/repos/musicom/projects/Styles")
all_mids = []
for p in styles_dir.rglob("*.mid"):
    p_str = str(p)
    if "/Production/" in p_str:
        continue
    if "phase1" in p.stem:
        continue
    if "/candidates/" in p_str:
        continue
    if p.stat().st_size > 40:
        all_mids.append(p)

all_mids = sorted(all_mids)
print(f"Usable MIDI candidates: {len(all_mids)}")
chosen_midi = rng.choice(all_mids)
print(f"Chosen MIDI: {chosen_midi}")
