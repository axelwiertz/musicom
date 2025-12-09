"""Tests for transformers module."""
from typing import List
from transformers.base import FunctionGenerator
from structures.unit import MusicUnit
from transformers.embellishment import stream_transform_random
from transformers.canon import CanonTransformator
from music21 import stream, scale


def test_functions():
    unit = MusicUnit(0, "Test Unit",
                     [60, 62, 64, 65, 67],
                     [1, 1, 1, 1, 1])
    def add_one(unit_: MusicUnit) -> List[MusicUnit]:
        _unit = MusicUnit(0, "Added One",
                         [p + 1 for p in unit_.pitch_nodes],
                         unit_.onset_intervals,
                         unit_.durations,
                         unit_.volumes)
        return [_unit]
    trans = FunctionGenerator(function=add_one)
    trans_units = trans.produce()
    print (trans_units)

    main_stream = stream.Stream()
    scl = scale.ConcreteScale()
    new_stream = stream_transform_random(main_stream, scl)

def test_canon():
    unit = MusicUnit(0, "Test Unit",
                     [60, 62, 64, 65, 67],
                     [1, 1, 1, 1, 1])
    trans = CanonTransformator(unit, number_of_voices=3, timesteps_delay=2, transpositions=[0, 12, -12])
    canon = trans.produce()

def main():
    test_canon()
    test_functions()

if __name__ == "__main__":
    main()