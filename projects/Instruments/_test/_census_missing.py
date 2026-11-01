import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R

progs = sorted(i.midi_program for i in R.ALL_INSTRUMENTS.values())
print("instrument count:", len(R.ALL_INSTRUMENTS))
print("missing GM programs:", [p for p in range(128) if p not in progs])
print("families:", sorted(set(i.family for i in R.ALL_INSTRUMENTS.values())))
