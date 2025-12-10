"""
Musicom analysis module
Module for analyzing musical scores using Music21 and MusicPy.
"""
from music21 import chord, roman, analysis, stream

def score_analyze(score: stream.Score):
    # Analyze score

    score.plot('3d')
    score.plot('histogram','pitch')
    score.show('abc')
    # Key
    key01 = score.analyze('key')
    print('Score :')
    print(score)
    print(' with key ' + str(key01))

    # m21 Chord analysis
    chord_set = score.chordify()
    # Check for specific chords
    for chd01 in chord_set.recurse().getElementsByClass(chord.Chord):
        if chd01.isDominantSeventh():
            print(chd01.measureNumber, chd01.beatStr, chd01)

    # All chords
    for chd01 in chord_set.recurse().getElementsByClass(chord.Chord):
        # Put chord in closed position
        chd01.closedPosition(forceOctave=4, inPlace=True)
        # Annotate chord intervals
        chd01.annotateIntervals(inPlace=True)
        # Add Roman numerals in lyrics
        rn = roman.romanNumeralFromChord(chd01, key01)
        chd01.addLyric(str(rn.figure))

    chord_set.partName = "Chord analysis"
    score.append(chord_set)
    score.makeMeasures(inPlace=True)
    # Music21 analysis
    result = analysis.metrical.labelBeatDepth(score)
    print('Metrical analysis: beat depth' + str(result))

