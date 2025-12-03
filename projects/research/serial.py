from base import PitchClass
from converters import stream_to_unit
from transformers import PitchSequenceTransformer

# Music21 modules: music notation and analysis
from music21 import serial

# Music 21 serial ToneRow
chromatic_row = serial.TwelveToneRow(PitchClass.NUMBERS)
tonerow_unit = stream_to_unit(chromatic_row)
ps_trans = PitchSequenceTransformer (tonerow_unit,'Prime', 0 )
ps_trans.set_method(ps_trans.PRIME)
units = ps_trans.produce ()
matrixobj = chromatic_row.matrix()
print(matrixobj)

