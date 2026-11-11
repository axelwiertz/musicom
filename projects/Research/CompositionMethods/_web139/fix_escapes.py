#!/usr/bin/env python3
"""Fix double-escaped LaTeX backslashes in the SP-139 summary row (line 351).
Uses chr(92) so no backslash literals appear in this source (escaping-proof)."""
import sys

path = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
BS = chr(92)                 # single backslash
PAIR = BS + BS               # two backslashes

with open(path, encoding="utf-8") as f:
    lines = f.read().split("\n")

row = lines[350]
assert "SP-139" in row, "line 351 is not the SP-139 row"
n_pairs = row.count(PAIR)
lines[350] = row.replace(PAIR, BS)

with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"line 351: collapsed {n_pairs} backslash pairs to single backslashes")
sys.exit(0)
