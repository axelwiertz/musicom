import io

rep = "/opt/data/projects/Instruments/Keys/drawbar_organ/REPORT.md"
src = "/opt/data/projects/Instruments/_test/drawbar_registry_out.txt"

lines = open(src, encoding="utf-8").read().splitlines()
table = [ln for ln in lines if ln.startswith("|")]
assert len(table) == 74, len(table)
assert any("Drawbar Organ" in ln for ln in table)

text = open(rep, encoding="utf-8").read()
marker = "<!--REGISTRY_TABLE-->"
assert marker in text
text = text.replace(marker, "\n".join(table))
open(rep, "w", encoding="utf-8").write(text)
print("inserted", len(table), "table lines;", len(text), "chars")
