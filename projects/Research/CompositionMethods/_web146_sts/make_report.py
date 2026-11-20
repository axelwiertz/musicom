p = "/opt/data/projects/Research/CompositionMethods/report_SP-146.md"
db = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
lines = open(db, encoding="utf-8").read().split("\n")
start = next(i for i, s in enumerate(lines) if s.startswith("# Sound Production Method SP-146"))
section = "\n".join(lines[start:]).rstrip("\n")
rep = open(p, encoding="utf-8").read()
rep = rep.replace("<!-- SECTION-START -->\n<!-- SECTION-END -->", section)
open(p, "w", encoding="utf-8").write(rep)
print("section lines:", section.count("\n") + 1, "report bytes:", len(rep))
