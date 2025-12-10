from pypianoroll import Multitrack, Track
import numpy as np

def create_sample_pianoroll():
    """Create a sample pianoroll with two tracks."""
    pianoroll = np.ndarray()
    # Create a piano track
    piano_track = Track(
        name='Piano',
        program=0,  # Acoustic Grand Piano
        is_drum=False,
        pianoroll=np.ndarray(
            [[0]*128 for _ in range(96)])

    )
    # Create a drum track
    drum_track = Track(
        name='Drums',
        program=0,
        is_drum=True,
        pianoroll=[
            [0]*128 for _ in range(96)
        ]
    )

def create_sample_pianoroll_with_notes():
    """Create a sample pianoroll with two tracks and some notes."""
    # Create a piano track
    piano_track = Track(
        name='Piano',
        program=0,  # Acoustic Grand Piano
        is_drum=False,
        pianoroll=[
            [0]*128 for _ in range(96)
        ]
    )

    # Add some notes to the piano track
    piano_track.pianoroll[0][60] = 100  # C4
    piano_track.pianoroll[4][62] = 100  # D4
    piano_track.pianoroll[8][64] = 100  # E4
    piano_track.pianoroll[12][65] = 100 # F4

    # Create a drum track
    drum_track = Track(
        name='Drums',
        program=0,
        is_drum=True,
        pianoroll=[
            [0]*128 for _ in range(96)
        ]
    )

    # Add some drum hits
    drum_track.pianoroll[0][36] = 127  # Bass Drum
    drum_track.pianoroll[4][38] = 127  # Snare Drum
    drum_track.pianoroll[8][42] = 127  # Closed Hi-Hat
    drum_track.pianoroll[12][46] = 127 # Open Hi-Hat

    # Create a multitrack object
    multitrack = Multitrack(
        name='Sample Pianoroll',
        resolution=24, # ticks per quarter note
        downbeat=False,
        tempo=120, # BPM
        tracks=[piano_track, drum_track],
    )

    # Save the pianoroll to a MIDI file
    multitrack.write('sample_pianoroll.mid')

    print("Sample pianoroll created and saved as 'sample_pianoroll.mid'.")

def main():
        create_sample_pianoroll_with_notes()


if __name__ == "__main__":
    main()