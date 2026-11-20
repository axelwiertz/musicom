lines = open("methods_db.md", encoding="utf-8").read().split("\n")
idx = [365] + list(range(32348, 32460))
bad = 0
for n in idx:
    s = lines[n - 1]
    if "\\\\" in s:
        bad += 1
        c = s.find("\\\\")
        print(n, "DOUBLE at", c, repr(s[max(0, c - 40):c + 20]))
print("checked", len(idx), "lines; double-backslash lines:", bad)
print("row 365 starts:", repr(lines[364][:12]), "ends:", repr(lines[364][-12:]))
