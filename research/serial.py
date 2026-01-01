from structures import MusicPitchClass, MusicTimeGrid
from converters.music21_stream import stream_to_unit
from transformers import PitchSequenceTransformer

# Music21 modules: music notation and analysis
from music21 import serial

# Music 21 serial ToneRow
chromatic_row = serial.TwelveToneRow(MusicPitchClass.NUMBERS)
tone_row_unit = stream_to_unit(chromatic_row, time=MusicTimeGrid(ticks_per_cycle=12, beats_per_cycle=12))
ps_trans = PitchSequenceTransformer (tone_row_unit,'Prime', 0 )
ps_trans.set_method(ps_trans.PRIME)
units = ps_trans.transform ()
matrixobj = chromatic_row.matrix()
print(matrixobj)

