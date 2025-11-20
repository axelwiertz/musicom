"""
Musicom generators module - random
Module for generating random musical structures.
"""
import random

from analysis.music21 import stream, note

def stream_create_random_from_list(length,
                        pitch_set: list[note.Pitch] = None,
                        duration_set: list[note.Duration] = None) -> stream.Stream:

    # Create a random stream from a list of pitches and durations
    stream_out = stream.Stream()
    for i in range(length):
        stream_out.append(
            note.Note(pitch= random.choice(pitch_set),
                      quarterLength=random.choice(duration_set)
                      )
        )

    return stream_out

