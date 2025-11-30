"""Diatonic patterns: intervals, scales, modes, chords"""
from music21 import interval
from structures.pattern import MusicPattern

class IntervalClasses:
    perfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    imperfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                    interval.DiatonicInterval(interval.Specifier.MINOR, 3)]


class Scale7Triad:
    def __init__(self):
        self.pattern_major = MusicPattern(Diatonic.TRIA, Diatonic.MAJOR)
        self.pattern_minor = MusicPattern(Diatonic.TRIA, Diatonic.MINOR)