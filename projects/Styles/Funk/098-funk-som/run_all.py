# -*- coding: utf-8 -*-
"""Runner to generate composition, audit it, render audio, and compute stats."""
import subprocess
import sys
import os

PROJ = "/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som"
PY = "/opt/data/micromamba/envs/musicom/bin/python"

scripts = ["compose.py", "audit.py", "render_audio.py", "audio_stats.py"]
for s in scripts:
    path = os.path.join(PROJ, s)
    print(f"=== Running {s} ===")
    res = subprocess.run([PY, path], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    if res.returncode != 0:
        print(f"Error running {s}, exit code: {res.returncode}")
        sys.exit(res.returncode)
print("=== All scripts completed successfully ===")
