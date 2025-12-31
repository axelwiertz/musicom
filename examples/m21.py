from music21 import roman, key, harmony

# Music21 chords
h = harmony.ChordSymbol('maj7', 'C')
h.romanNumeral = roman.RomanNumeral('I', 'C')
h.romanNumeral = roman.RomanNumeral('IV', 'A')

chords= [harmony.ChordSymbol('sus4', 'D')]
chords[1].romanNumeral = 'III'
chords[1].romanNumeral.key = key.Key('B')
