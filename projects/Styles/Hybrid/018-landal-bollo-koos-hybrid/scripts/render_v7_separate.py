import mido
from mido import Message, MidiFile, MidiTrack
import subprocess
import os

PROJECT_DIR = "/opt/data/projects/018-landal-bollo-koos-hybrid"
MIDI_PATH = f"{PROJECT_DIR}/midi/interwoven_v7_separate.mid"
WAV_PATH = f"{PROJECT_DIR}/audio/interwoven_v7_separate.wav"
OGG_PATH = f"{PROJECT_DIR}/audio/interwoven_v7_separate.ogg"
SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

def create_v7_midi():
    mid = MidiFile(ticks_per_beat=480)
    
    # 1. Foundation: Bass (Pr 35) & Drums (Ch 10)
    # 2. Berendans: Violin (Pr 40)
    # 3. Koos Hook: Synth (Pr 80)
    # 4. Polo Motif: Guitar (Pr 25)
    
    tracks = [MidiTrack() for _ in range(6)]
    for t in tracks: mid.tracks.append(t)
    
    # Pr Changes
    tracks[1].append(Message('program_change', program=35, channel=0, time=0)) # Bass
    tracks[2].append(Message('program_change', program=40, channel=1, time=0)) # Violin
    tracks[3].append(Message('program_change', program=80, channel=2, time=0)) # Synth
    tracks[4].append(Message('program_change', program=25, channel=3, time=0)) # Guitar
    
    # DNA
    berendans = [70, 72, 74, 70]
    koos = [82, 82, 82, 77]
    polo = [70, 74, 77, 75, 72]

    for bar in range(16):
        # DRUMS & BASS - Persistent Foundation
        for b in range(4):
            # Kick & Clap
            tracks[5].append(Message('note_on', note=36, velocity=105, channel=9, time=0))
            if b in [1, 3]: tracks[5].append(Message('note_on', note=39, velocity=95, channel=9, time=0))
            tracks[5].append(Message('note_off', note=36, velocity=0, channel=9, time=240))
            tracks[5].append(Message('note_off', note=39, velocity=0, channel=9, time=0))
            tracks[5].append(Message('note_off', note=36, velocity=0, channel=9, time=240)) # Space
            
            # Bass
            note = 46 if b%2==0 else 53
            tracks[1].append(Message('note_on', note=note, velocity=85, channel=0, time=0))
            tracks[1].append(Message('note_off', note=note, velocity=0, channel=0, time=480))

        # SEPARATED MELODY SECTIONS (V3 Style)
        # Bar 0-4: Berendans Only
        if 0 <= bar < 4:
            for n in berendans:
                tracks[2].append(Message('note_on', note=n, velocity=90, channel=1, time=0))
                tracks[2].append(Message('note_off', note=n, velocity=0, channel=1, time=480))
            # Padding others
            for t in [tracks[3], tracks[4]]:
                for _ in range(4): t.append(Message('note_off', note=0, time=480))
        
        # Bar 4-8: Koos Hook Only
        elif 4 <= bar < 8:
            for n in koos:
                tracks[3].append(Message('note_on', note=n, velocity=95, channel=2, time=0))
                tracks[3].append(Message('note_off', note=n, velocity=0, channel=2, time=480))
            for t in [tracks[2], tracks[4]]:
                for _ in range(4): t.append(Message('note_off', note=0, time=480))
                
        # Bar 8-12: Polo Motif Only
        elif 8 <= bar < 12:
            step = 1920 // len(polo)
            for n in polo:
                tracks[4].append(Message('note_on', note=n, velocity=100, channel=3, time=0))
                tracks[4].append(Message('note_off', note=n, velocity=0, channel=3, time=step))
            for t in [tracks[2], tracks[3]]:
                for _ in range(4): t.append(Message('note_off', note=0, time=480))

        # Bar 12-16: Short Hybrid Finale (Brief Overlay)
        else:
            for n in berendans:
                tracks[2].append(Message('note_on', note=n, velocity=70, channel=1, time=0))
                tracks[2].append(Message('note_off', note=n, velocity=0, channel=1, time=480))
            for n in koos:
                tracks[3].append(Message('note_on', note=n, velocity=75, channel=2, time=0))
                tracks[3].append(Message('note_off', note=n, velocity=0, channel=2, time=480))
            for _ in range(4): tracks[4].append(Message('note_off', note=0, time=480))

    mid.save(MIDI_PATH)

def render_v7():
    subprocess.run(["fluidsynth", "-ni", SOUNDFONT, MIDI_PATH, "-F", WAV_PATH, "-r", "44100"], check=True)
    subprocess.run(["ffmpeg", "-i", WAV_PATH, "-codec:a", "libopus", "-application", "voip", "-b:a", "64k", OGG_PATH, "-y", "-loglevel", "error"], check=True)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(MIDI_PATH), exist_ok=True)
    create_v7_midi()
    render_v7()
    print("V7 Separated Render Complete.")
