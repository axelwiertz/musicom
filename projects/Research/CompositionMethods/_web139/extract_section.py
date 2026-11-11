#!/usr/bin/env python3
"""Extract the appended SP-139 section (lines 31103-31198) into the report part 3."""
with open("/opt/data/projects/Research/CompositionMethods/methods_db.md", encoding="utf-8") as f:
    lines = f.read().split("\n")
sec = lines[31102:31198]          # 0-based [31102, 31198) == lines 31103..31198
with open("/opt/data/projects/Research/CompositionMethods/_report_sp139_p3.md", "w", encoding="utf-8") as f:
    f.write("\n".join(sec) + "\n")
print("extracted", len(sec), "lines")
