import sys
print("python:", sys.executable)
try:
    import numpy; print("numpy", numpy.__version__)
except Exception as e:
    print("numpy MISSING:", e)
try:
    import scipy; print("scipy", scipy.__version__)
except Exception as e:
    print("scipy MISSING:", e)
try:
    import mido; print("mido", mido.__version__)
except Exception as e:
    print("mido MISSING:", e)
import glob
hits = []
for pat in ["/opt/data/**/*.sf2", "/usr/share/**/*.sf2", "/opt/**/*.sf2"]:
    hits += glob.glob(pat, recursive=True)
print("sf2 files:", hits[:10])
try:
    import sound
    print("sound pkg at:", sound.__file__)
except Exception as e:
    print("sound import fail:", e)
