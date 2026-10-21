md = open("/opt/data/projects/Instruments/Keys/drawbar_organ/instrument.md", encoding="utf-8").read()
parts = md.split("---")
print("segments:", len(parts))
fm = parts[1].strip().splitlines()
keys = [ln.split(":")[0] for ln in fm]
print("frontmatter keys:", keys)
required = ["type", "family", "name", "midi_program", "gms", "range_min",
            "range_max", "solo_range", "role", "synthesis"]
assert keys == required, keys
for ln in fm:
    print(" ", ln)
