#!/usr/bin/env python
"""Fix double-escaped LaTeX backslashes in the method 141 summary row.

The patch tool double-escaped every '\\' -> '\\\\' in the inserted table row
(the known methods_db pitfall). This rewrites ONLY the '| **141** |' line,
normalizing any run of backslashes to a single backslash, then verifies.
"""
import re
path = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
lines = open(path, encoding="utf-8").read().split("\n")
fixed = 0
for i, l in enumerate(lines):
    if l.startswith("| **141** |"):
        new = re.sub(r"\\+", r"\\", l)
        lines[i] = new
        fixed += 1
        # report
        print("line", i + 1, "backslash runs before:", len(re.findall(r"\\+", l)),
              "after:", len(re.findall(r"\\+", new)))
open(path, "w", encoding="utf-8").write("\n".join(lines))
print("fixed lines:", fixed)
