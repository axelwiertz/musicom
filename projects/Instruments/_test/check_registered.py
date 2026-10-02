"""Check what instruments are registered vs what exists on disk."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
import instrument_registry as ir

keys = sorted(ir.ALL_INSTRUMENTS.keys())
print(f"Total registered: {len(keys)}")
for k in keys:
    inst = ir.ALL_INSTRUMENTS[k]
    print(f"  {k}: program={inst.midi_program}, family={inst.family}, name={inst.name}")