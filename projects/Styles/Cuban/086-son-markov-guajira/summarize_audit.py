#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Summarize audit.json (grid + harmony verdict per voice)."""
import json
import os

with open("/opt/data/projects/Styles/Cuban/086-son-markov-guajira/Analysis/audit.json") as f:
    d = json.load(f)
for rec in d["files"]:
    print(rec["label"])
    for v in rec["voices"]:
        tag = "PERC" if v["percussion"] else "PITCH"
        print("  [%s] %-16s notes=%-4d off16=%-3d off8=%-3d outscale=%-3d outchord=%-3d"
              % (tag, v["gm"], v["note_count"], v["off_grid_16th"],
                 v["off_grid_8th"], v["out_of_scale"], v["out_of_chord"]))
