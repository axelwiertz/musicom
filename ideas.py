"""
Musicom
Composition and Analysis Framework
"""
from constants import TwelveTET
from converters import *


from generators.pitchsequence import PitchSequence

# Music21 modules: music notation and analysis
from music21 import roman, key, harmony, serial



def music21_snippets():
    # Music 21 ToneRow
    chromatic_row = serial.TwelveToneRow(TwelveTET.PITCH_CLASS_NUMBERS)
    ps = PitchSequence (TwelveTET.PITCH_CLASS_NUMBERS)
    ps.transform (ps.PRIME, 0)
    matrixobj = chromatic_row.matrix()
    print(matrixobj)
    unit = MusicUnit()
    unit.pitch_nodes = ps.pitch_nodes

    ps.transform (ps.PRIME, 0)

    # Music21 Harmony
    h = harmony.ChordSymbol('maj7', 'C')
    h.romanNumeral = roman.RomanNumeral('I', 'C')
    h.romanNumeral = roman.RomanNumeral('IV', 'A')

    chords= [harmony.ChordSymbol('sus4', 'D')]
    chords[1].romanNumeral = 'III'
    chords[1].romanNumeral.key = key.Key('B')


def main():
    pass

if __name__ == '__main__':
    main()