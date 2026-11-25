p = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
lines = open(p).read().split("\n")
i150 = next(i for i, l in enumerate(lines) if l.startswith("| **SP-150** |"))
i149 = next(i for i, l in enumerate(lines) if l.startswith("| **SP-149** |"))
assert i150 == i149 - 1, (i150, i149)
lines[i150], lines[i149] = lines[i149], lines[i150]
open(p, "w").write("\n".join(lines))
print("swapped lines", i150 + 1, i149 + 1)
print(lines[i149][:60])
print(lines[i150][:60])
