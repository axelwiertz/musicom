import sys
print("python", sys.version)
try:
    import select
    print("select ok", select.__file__, hasattr(select,"select"))
except Exception as e:
    print("select ERR", repr(e))
try:
    import numpy
    print("numpy", numpy.__version__)
except Exception as e:
    print("numpy ERR", repr(e))
try:
    import structures
    print("structures OK")
    from structures import MusicUnit, MusicEvent, MidiInstrument
    print("core structs OK")
except Exception as e:
    print("structures ERR", repr(e))
try:
    from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit
    print("composer OK")
except Exception as e:
    print("composer ERR", repr(e))
try:
    from visualization.grid import write_grid_visualization
    print("grid OK")
except Exception as e:
    print("grid ERR", repr(e))
try:
    from workflows.provenance import write_provenance
    print("provenance OK")
except Exception as e:
    print("provenance ERR", repr(e))
try:
    import mido
    print("mido OK")
except Exception as e:
    print("mido ERR", repr(e))