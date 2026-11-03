"""Repair: move the SP-132 summary row from the ZRNC pitfalls tail into the
Sound Production summary table, immediately after the SP-131 row."""
import io

P = "/opt/data/repos/musicom/projects/Research/CompositionMethods/methods_db.md"
s = io.open(P, encoding="utf-8").read()

# 1. cut the misplaced row out of wherever it landed
i = s.index("| **SP-132** |")
j = s.index("\n", i)
ROW = s[i:j]
assert "\n" not in ROW
s = s[:i] + s[j:]
# the char now at position i should be a newline (blank line before the header)
assert s[i:i+3] == "\n\n#", repr(s[i-40:i+20])

# 2. insert it after the SP-131 table row
k = s.index("| **SP-131** |")
assert "Vocal Fold" in s[k:k+120]
e = s.index("\n", k)
s = s[:e+1] + ROW + "\n" + s[e+1:]

io.open(P, "w", encoding="utf-8").write(s)

# 3. report
lines = s.split("\n")
for n, ln in enumerate(lines, 1):
    if ln.startswith("| **SP-131** |") or ln.startswith("| **SP-132** |"):
        print(f"line {n}: {ln[:110]}")
    if "gating.|" in ln or "|| **SP-" in ln:
        print(f"BAD line {n}: {ln[:110]}")
print("total lines:", s.count("\n"))
