""" Twelve-Tone Equal Temperament tuning system. """

class Constants:
    # General twelve-tone equal temperament constants
    TWELVE = 12  # Number of pitch classes 0-11
    CENTS : float = 100  # Cents in semitone
    A4_FREQ = 440.0  # Frequency of A4
    OCTAVES = 9  # Number of octaves in the pitch set

class PitchClass:
    # Pitch class numbers and names
    C = 0
    C_SHARP = D_FLAT = 1
    D = 2
    D_SHARP = E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = G_FLAT = 6
    G = 7
    G_SHARP = A_FLAT = 8
    A = 9
    A_SHARP = B_FLAT = 10
    B = 11
    NUMBERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NAMES_FLATMAP = {'D': 'C#', 'E': 'D#', 'F': 'E', 'G': 'F#', 'A': 'G#', 'B': 'A#', 'C': 'B'}



