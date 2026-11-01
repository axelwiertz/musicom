import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R
import subprocess
print("ALL_INSTRUMENTS count:", len(R.ALL_INSTRUMENTS))
out = subprocess.run(["bash", "-c", "find /opt/data/projects/Instruments -name instrument.md | wc -l"],
                     capture_output=True, text=True)
print("instrument.md folders:", out.stdout.strip())
