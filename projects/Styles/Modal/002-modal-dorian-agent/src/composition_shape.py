import sys
import os
import matplotlib.pyplot as plt
from music21 import converter, instrument, note, chord

def generate_shape_report(midi_path, output_dir):
    score = converter.parse(midi_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Volume/Velocity Graph (Dynamics)
    times = []
    velocities = []
    
    for element in score.flatten().notes:
        times.append(element.offset)
        # Handle notes and chords for velocity
        if isinstance(element, note.Note):
            velocities.append(element.volume.velocity if element.volume.velocity else 64)
        else:
            velocities.append(element[0].volume.velocity if element[0].volume.velocity else 64)

    plt.figure(figsize=(10, 4), facecolor='#1e1e1e')
    plt.plot(times, velocities, color='#fb7185', linewidth=2, marker='o', markersize=4)
    plt.fill_between(times, velocities, color='#fb7185', alpha=0.2)
    plt.ylim(0, 127)
    plt.title("Composition Shape: Volume/Dynamics", color='white')
    plt.xlabel("Time", color='white')
    plt.ylabel("Velocity", color='white')
    plt.gca().set_facecolor('#0f172a')
    plt.gca().tick_params(colors='white')
    plt.grid(True, alpha=0.1, color='white')
    
    vol_path = os.path.join(output_dir, "volume_graph.png")
    plt.savefig(vol_path, dpi=120)
    plt.close()

    # 2. Score Notation (Simplified text-based staff representation for now or PDF)
    # We will attempt a LilyPond export if path is configured, 
    # but for now we'll create a "Harmonic Flow" map using Mermaid/Text
    
    harmonics = []
    for c in score.chordify().flatten().getElementsByClass('Chord'):
        harmonics.append(c.commonName)
    
    flow_path = os.path.join(output_dir, "harmonic_flow.txt")
    with open(flow_path, 'w') as f:
        f.write(" -> ".join(harmonics[:12]) + "...")

    return vol_path, flow_path

if __name__ == "__main__":
    midi_file = sys.argv[1]
    dist = "/tmp/musicom_report"
    v, f = generate_shape_report(midi_file, dist)
    print(f"REPORT_READY|{v}|{f}")
