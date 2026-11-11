#!/usr/bin/env python3
"""Byte-level check: count literal backslashes in the SP-139 row (line 351)."""
BS = chr(92)
with open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8") as f:
    lines = f.read().split("\n")
row = lines[350]
n = row.count(BS)
print("total literal backslashes in row:", n)
print("double-pairs:", row.count(BS + BS))
print("expected (LaTeX cmds: mathrm, ,, Delta, rho, times = 5):", 5)
# show each LaTeX token with its surrounding chars
import re
for m in re.finditer(r"\$[^$]*\$", row):
    s = m.group(0)
    if BS in s:
        print("token:", s[:80])
