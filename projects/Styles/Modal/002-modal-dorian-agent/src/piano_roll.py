import sys
import os
import matplotlib.pyplot as plt
from music21 import converter, instrument, note, chord

def generate_piano_roll(midi_path, output_path):
    score = converter.parse(midi_path)
    
    # Extract notes/chords and their times
    notes = []
    times = []
    pitches = []
    durations = []
    
    for part in score.parts:
        for element in part.flatten().notes:
            if isinstance(element, note.Note):
                notes.append(element)
                times.append(element.offset)
                pitches.append(element.pitch.ps)
                durations.append(element.quarterLength)
            elif isinstance(element, chord.Chord):
                for n in element:
                    notes.append(n)
                    times.append(element.offset)
                    pitches.append(n.pitch.ps)
                    durations.append(element.quarterLength)

    # Plotting
    plt.figure(figsize=(12, 6), facecolor='#1e1e1e')
    ax = plt.gca()
    ax.set_facecolor('#1e1e1e')
    
    # Draw notes as rectangles
    for t, p, d in zip(times, pitches, durations):
        ax.add_patch(plt.Rectangle((t, p), d, 0.8, color='#58C4DD', alpha=0.8))
    
    plt.xlim(0, max(times) + 5 if times else 10)
    plt.ylim(min(pitches) - 5 if pitches else 40, max(pitches) + 5 if pitches else 80)
    
    plt.xlabel('Time (Quarter Length)', color='white')
    plt.ylabel('Pitch (MIDI Number)', color='white')
    plt.title(f'Piano Roll: {os.path.basename(midi_path)}', color='white')
    ax.tick_params(colors='white')
    
    plt.grid(True, linestyle='--', alpha=0.2, color='white')
    plt.savefig(output_path, dpi=150)
    plt.close()

if __name__ == "__main__":
    midi_file = sys.argv[1]
    out_file = sys.argv[2]
    generate_piano_roll(midi_file, out_file)
