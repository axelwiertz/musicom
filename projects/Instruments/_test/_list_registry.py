import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as R

for k, i in sorted(R.ALL_INSTRUMENTS.items(), key=lambda kv: kv[1].midi_program):
    print(f"{i.midi_program:3d} {i.gm_name:25s} {i.family:12s} {k}")
