"""
Musicom analysis module
Module for analyzing musical scores using Music21 and MusicPy.
"""
from structures import MusicComposition
from music21 import chord, roman, analysis
from musicpy import musicpy as mp

def analyze(comp: MusicComposition):
    # Analyze score

    # comp.score.plot('3d')
    # comp.score.plot('histogram','pitch')
    # comp.score.show('abc')
    # Key
    key01 = comp.score.analyze('key')
    print('Score :')
    print(comp.score)
    print(' with key ' + str(key01))

    # m21 Chord analysis
    chordset = comp.score.chordify()
    # Check for specific chords
    for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
        if chd01.isDominantSeventh():
            print(chd01.measureNumber, chd01.beatStr, chd01)

    # All chords
    for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
        # Put chord in closed position
        chd01.closedPosition(forceOctave=4, inPlace=True)
        # Annotate chord intervals
        chd01.annotateIntervals(inPlace=True)
        # Add Roman numerals in lyrics
        rn = roman.romanNumeralFromChord(chd01, key01)
        chd01.addLyric(str(rn.figure))

    chordset.partName = "Chord analysis"
    comp.score.append(chordset)
    comp.score.makeMeasures(inPlace=True)
    # Music21 analysis
    result = analysis.metrical.labelBeatDepth(comp.score)
    print('Metrical analysis: beat depth' + str(result))
    # MusicPy analysis
    str1 = mp.algorithms.detect(comp.piece)
    str2 = mp.algorithms.chord_analysis(comp.piece)
    str3 = mp.analyze_rhythm(comp.piece)
    print('MusicPy analysis:')
    print(str1)
    print(str2)
    print(str3)
