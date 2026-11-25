p = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
lines = open(p).read().split("\n")
row = next(l for l in lines if l.startswith("| **SP-150** |"))
i0 = next(i for i, l in enumerate(lines) if l.startswith("# Sound Production Method SP-150"))
sec = "\n".join(lines[i0:])

print("row: single-backslash \\frac:", row.count("\\frac"), " double \\\\frac:", row.count("\\\\frac"))
print("row: '||' present:", "||" in row, " pipe count:", row.count("|"))
print("section: double-backslash occurrences:")
for n, l in enumerate(sec.split("\n"), 1):
    if "\\\\" in l:
        print("  ", n, l[:100])
print("section headers:", [l for l in sec.split("\n") if l.startswith("### ")])
print("section lines:", sec.count("\n"))
import os
for f in ["report_SP-150.md", "sound_method_SP-150_HCRS.md"]:
    fp = "/opt/data/projects/Research/CompositionMethods/" + f
    print(f, os.path.getsize(fp), "B")
