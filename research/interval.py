from music21 import interval

class IntervalClasses:
    perfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    imperfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                    interval.DiatonicInterval(interval.Specifier.MINOR, 3)]

class IntervalClass:

    # 7 Hepta Interval classes
    perfect_interval_classes = ('P1', 'P4', 'P5', 'P8')
    imperfect_interval_classes = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')
