import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import ALL_INSTRUMENTS, CLEAN_ELECTRIC
print(f"Total instruments: {len(ALL_INSTRUMENTS)}")
print(f"CLEAN_ELECTRIC: {CLEAN_ELECTRIC}")
guitars = [k for k,v in ALL_INSTRUMENTS.items() if v.family == "Guitar"]
print(f"Guitar family: {guitars}")