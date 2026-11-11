#!/usr/bin/env python3
"""Inspect raw bytes of line 351 around the LaTeX."""
with open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8") as f:
    lines = f.read().split("\n")
row = lines[350]
i = row.find("p_m^")
print("raw segment:", repr(row[i:i+140]))
