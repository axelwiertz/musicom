# MusicPy analysis
from musicpy import musicpy as mp, structures, algorithms

def piece_analyze(piece: structures.piece):
    str1 = algorithms.detect(piece)
    str2 = algorithms.chord_analysis(piece)
    str3 = mp.analyze_rhythm(piece)
    print('MusicPy analysis:')
    print(str1)
    print(str2)
    print(str3)
