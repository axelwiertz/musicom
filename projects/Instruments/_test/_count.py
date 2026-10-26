import sys
sys.path.insert(0,".")
from instrument_registry import ALL_INSTRUMENTS
print("load count:", len(ALL_INSTRUMENTS))
print([k for k in ALL_INSTRUMENTS if "choir" in k])
