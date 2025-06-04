import random
from music21 import stream, note, chord, interval, meter

def generate_counterpoint(voice1, voice2):
    # Ensure the voices are of the same length
    if len(voice1) != len(voice2):
        raise ValueError("Voices must be of the same length")

    # Check for parallel perfect intervals
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if intv1.isPerfect and intv2.isPerfect and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if intv1.isPerfect and intv2.isPerfect and intv1.direction == intv2.direction:
            return False

    # Check for crossing voices
    for i in range(len(voice1)):
        if voice1[i].pitch < voice2[i].pitch and voice1[i + 1].pitch > voice2[i + 1].pitch:
            return False

    return True

def create_random_voice(length):
    voice = []
    for _ in range(length):
        pitch = random.choice(range(60, 72))  # C4 to B4
        duration = random.choice([0.5, 1, 2])
        n = note.Note(pitch, quarterLength=duration)
        voice.append(n)
    return voice

def main():
    length = 16  # Length of the counterpoint
    voice1 = create_random_voice(length)
    voice2 = create_random_voice(length)

    while not generate_counterpoint(voice1, voice2):
        voice2 = create_random_voice(length)

    # Create a stream to hold the voices
    s = stream.Stream()
    s.append(voice1)
    s.append(voice2)

    # Show the counterpoint
    s.show('text')

if __name__ == "__main__":
    main()
