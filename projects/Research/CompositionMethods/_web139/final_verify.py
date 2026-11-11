#!/usr/bin/env python3
"""Final verification: line counts, SP-139 presence, backslash sanity in section."""
BS = chr(92)
db = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
with open(db, encoding="utf-8") as f:
    txt = f.read()
lines = txt.split("\n")
print("methods_db.md total lines:", len(lines))
print("summary-row line (1-based):", next(i+1 for i, l in enumerate(lines) if "| **SP-139** |" in l))
sec = [i+1 for i, l in enumerate(lines) if l.startswith("# Sound Production Method SP-139")]
print("detailed section at line:", sec)
n_sec = len(sec)
# backslash sanity in the section lines
seg = "\n".join(lines[sec[0]-1:sec[0]-1+96])
print("section backslash pairs:", seg.count(BS+BS), "| singles:", seg.count(BS))
# standalone file
st = "/opt/data/projects/Research/CompositionMethods/sound_method_SP-139_CDRB.md"
with open(st, encoding="utf-8") as f:
    stxt = f.read()
print("standalone lines:", stxt.count("\n")+1, "| backslash pairs:", stxt.count(BS+BS))
# report
rp = "/opt/data/projects/Research/CompositionMethods/report_SP-139.md"
with open(rp, encoding="utf-8") as f:
    rtxt = f.read()
print("report lines:", rtxt.count("\n")+1)
print("SP-139 occurrences in db:", txt.count("SP-139"))
