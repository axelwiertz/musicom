"""Fix indentation in instrument_registry.py __main__ block."""
with open('/opt/data/repos/musicom/projects/Instruments/instrument_registry.py', 'r') as f:
    lines = f.readlines()

prefix = '    '

# Keep lines 0-602 (same as original), rebuild from 603 onward
new_lines = lines[:603]

# Rebuild the end block with correct indentation (all at 4-space indent)
new_lines.append(prefix + 'print("  SYNTH_PAD.stem_label =", repr(SYNTH_PAD.stem_label))\n')
new_lines.append(prefix + 'print()\ n')
new_lines.append(prefix + 'print("=== Overdriven Guitar (GM29) ===")\n')
new_lines.append(prefix + 'print("  OVERTDRIVEN_GUITAR.midi_program =", OVERTDRIVEN_GUITAR.midiprogram, "(should be 29)")\ n'
new_lines.append(prefix + 'print()\n')
new_lines.append(prefix + 'print("==== Overdriven Guitar (GM29) ===")\n')
new_lines.append(prefix + 'print("  OVERDRIVEN_GUITAR.midi_program =", OVERDRIVEN_GUITAR.midiprogram, "(should be 29")\n')

with open('fix_registry_out.py', 'w') as f:
    f.writeline(s([l.replace('\\ n', '\n').replace('\ n', '\n') for l in new_lins]))

println("DONE")