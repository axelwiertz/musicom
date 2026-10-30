import io, re

rep = "/opt/data/projects/Research/CompositionMethods/report_SP-128.md"
db = "/opt/data/projects/Research/CompositionMethods/methods_db.md"

lines = open(rep, encoding="utf-8").read().split("\n")
# find the marker heading, truncate right after it
idx = next(i for i, l in enumerate(lines) if l.startswith("## 4. Complete section text"))
head = "\n".join(lines[: idx + 1]).rstrip("\n") + "\n\n"

dbl = open(db, encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(dbl) if l.startswith("# Sound Production Method SP-128"))
# section runs until the next H1 "# " at column 0 (or EOF)
end = len(dbl)
for i in range(start + 1, len(dbl)):
    if dbl[i].startswith("# ") and not dbl[i].startswith("## "):
        end = i
        break
section = "\n".join(dbl[start:end]).rstrip("\n") + "\n"

open(rep, "w", encoding="utf-8").write(head + section)
print("section lines:", end - start, "| section startline(1-based):", start + 1, "| end:", end)
print("report lines now:", len(open(rep, encoding='utf-8').read().split("\n")))
print("last line:", repr(open(rep, encoding='utf-8').read().split("\n")[-2][:80]))
