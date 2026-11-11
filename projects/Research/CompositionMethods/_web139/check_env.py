#!/usr/bin/env python3
"""Check numpy + candidate paths of neighbouring SP entries."""
import subprocess, re

# numpy version
r = subprocess.run(["/opt/data/micromamba/envs/musicom/bin/python", "-c",
                    "import numpy; print(numpy.__version__)"], capture_output=True, text=True)
print("numpy:", r.stdout.strip() or r.stderr.strip())

# candidate paths of neighbors
db = open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8").read()
for tag in ["SP-023", "SP-065", "SP-066", "SP-124", "SP-134", "SP-138", "SP-074", "SP-042"]:
    for m in re.finditer(r"Candidate: `([^`]+)`", db):
        # find which SP section this appears in: nearest preceding '# Sound Production Method SP-XXX'
        start = db.rfind("# Sound Production Method", 0, m.start())
        sec = re.search(r"SP-(\d+)", db[start:m.start()])
        if sec and sec.group(1) == tag.split("-")[1]:
            print(tag, "->", m.group(1))
            break
    else:
        # fallback: search summary row
        row = re.search(r"\*\*" + re.escape(tag) + r"\*\*[^|]*\|[^|]*\|[^|]*\|[^|]*\|([^|]*)$", db, re.M)
        if row:
            c = re.search(r"`([^`]+)`", row.group(1))
            if c:
                print(tag, "->", c.group(1))
