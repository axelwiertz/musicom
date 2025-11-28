from music21 import stream, scale

from structures.unit import MusicUnit
from transformators.embellishment import stream_transform_random
from transformators.canon import stream_transform_canon


def test_transformators():

    main_stream = stream.Stream()
    unit = MusicUnit(1,"TestUnit1")
    scl = scale.ConcreteScale()
    new_stream = stream_transform_random(main_stream, scl)

    canon_stream = stream_transform_canon(main_stream)

def main():
    test_transformators()

if __name__ == "__main__":
    main()