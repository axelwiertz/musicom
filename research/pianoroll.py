from pypianoroll import Multitrack, Track
import numpy as np




def create_sample_pianoroll_with_notes():
    """Create a sample pianoroll with notes and save it as a MIDI file."""
    # Create a pianoroll: 4 beats, 24 steps per beat = 96 time steps (ticks)
    piano_track = Track(name="Melody", program=0, pianoroll=np.zeros((96, 128)))
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
        pianoroll=np.zeros((96, 128))  # 96 time steps, 128 MIDI pitches
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
        # downbeat positions Boolean array that indicates whether the time step contains a downbeat (i.e., the first time step of a bar). Length is the total number of time steps.
        downbeat=np.array([True if i % 96 == 0 else False for i in range(96)]),
        # empo (in qpm) at each time step. Length is the total number of time steps. Cast to float if not of data type float.
        tempo= np.array([120.0 for _ in range(96)]),
        tracks=[piano_track, drum_track],
    )
    # Save the pianoroll to a MIDI file
    multitrack.write('sample_pianoroll.mid')

    print("Sample pianoroll created and saved as 'sample_pianoroll.mid'.")

def main():
    """Main function to create pianorolls."""
    create_sample_pianoroll_with_notes()

if __name__ == "__main__":
    main()