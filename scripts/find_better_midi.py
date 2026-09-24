import os
from pathlib import Path

styles_dir = Path("/opt/data/repos/musicom/projects/Styles")
candidates = []
for p in styles_dir.rglob("*.mid"):
    p_str = str(p)
    if "/Production/" in p_str:
        continue
    if "phase1" in p.stem:
        continue
    if "/candidates/" in p_str:
        continue
    if "native_render" in p.stem:
        continue
    if p.stat().st_size > 500:
        candidates.append(p)

print("Longer/richer candidates (>500B):", len(candidates))
# Let's see what random choice with SEED=20260921 gives on this proper pool
import random
rng = random.Random(20260921)
chosen = rng.choice(sorted(candidates))
print("Chosen robust MIDI:", chosen, f"({chosen.stat().st_size} bytes)")
