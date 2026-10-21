import os
import sys

sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
import instrument_registry as R

print("instruments:", len(R.ALL_INSTRUMENTS))
print("keys:", [k for k in R.ALL_INSTRUMENTS if R.ALL_INSTRUMENTS[k].family == "Keys"])
i = R.by_name("drawbar organ")
print("row:", i, "| humanize:", i.humanize_dna)
print("synthesis:", i.synthesis, "motor:", i.motor_defaults)
print("table has row:", any("Drawbar Organ" in l for l in R.registry_table().splitlines()))
for p in ["/opt/data/projects/Instruments/Keys/drawbar_organ/instrument.md",
          "/opt/data/projects/Instruments/Keys/drawbar_organ/drawbar_organ.py",
          "/opt/data/projects/Instruments/Keys/drawbar_organ/REPORT.md",
          "/opt/data/projects/Instruments/_test/drawbar_organ_test.mid",
          "/opt/data/projects/Instruments/_test/drawbar_organ_test.wav",
          "/opt/data/projects/Instruments/_test/stems_drawbar_organ/track00_Drawbar_Organ.wav"]:
    print(os.path.getsize(p), p)

# YAML frontmatter parse
import yaml
md = open("/opt/data/projects/Instruments/Keys/drawbar_organ/instrument.md", encoding="utf-8").read()
fm = md.split("---")[1]
print("frontmatter:", yaml.safe_load(fm))
