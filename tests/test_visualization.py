from visualization import Helix, Cycle
from structures import MusicPitch, MusicPitchClass, MusicTimeGrid

def test_visualization():
    # Show helix
    h = Helix()
    print(h)
    p = MusicPitches()
    p.show()
    # Test functions
    # Show rhythm in circle
    rc = Cycle(4, ['Down', 'Up', 'Down', 'Up'])
    rc.show()

    time = MusicTimeGrid(timesteps=8, beats_in_measure=4, beat_note=4, bpm=120)
    time.show()

    # Show pitch class circle
    pc_circle = Cycle(MusicPitchClass.TWELVE, MusicPitchClass.NAMES_SHARP)
    pc_circle.show()


def main():
    test_visualization()

if __name__ == '__main__':
    main()