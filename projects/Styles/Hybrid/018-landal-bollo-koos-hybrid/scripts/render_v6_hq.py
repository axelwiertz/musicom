import numpy as np
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
import subprocess

# Project Path
PROJECT_DIR = "/opt/data/projects/018-landal-bollo-koos-hybrid"
MIDI_PATH = f"{PROJECT_DIR}/midi/instrumented_hq_v6.mid"
WAV_PATH = f"{PROJECT_DIR}/audio/instrumented_hq_v6.wav"
OGG_PATH = f"{PROJECT_DIR}/audio/instrumented_hq_v6.ogg"
SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

def create_hq_midi():
    mid = MidiFile(ticks_per_beat=480)
    
    # 1. Lead Violin (Berendans) - Ch 1, Pr 40
    # 2. Bright Synth (Koos) - Ch 2, Pr 80 (Ocarina or Lead 1)
    # 3. Steel Guitar (Polo) - Ch 3, Pr 25 (Steel Guitar)
    # 4. Bass - Ch 4, Pr 35 (Fretless/Pick)
    # 5. Percussion - Ch 10
    
    # Common setup
    tracks = {}
    for i in range(1, 11):
        t = MidiTrack()
        mid.tracks.append(t)
        tracks[i] = t
        
    # Program Changes
    tracks[1].append(Message('program_change', program=40, channel=0, time=0)) # Violin
    tracks[2].append(Message('program_change', program=80, channel=1, time=0)) # Synth
    tracks[3].append(Message('program_change', program=25, channel=2, time=0)) # Guitar
    tracks[4].append(Message('program_change', program=35, channel=3, time=0)) # Bass

    # DNA
    berendans = [70, 72, 74, 70]
    koos = [82, 82, 82, 77]
    polo = [70, 74, 77, 75, 72]
    
    # 16 Bars
    for bar in range(16):
        # Percussion (Ch 10) - Kick (35/36) and Claps (39)
        for b in range(4):
            # Kick on every beat
            tracks[10].append(Message('note_on', note=36, velocity=110, channel=9, time=0))
            tracks[10].append(Message('note_off', note=36, velocity=0, channel=9, time=240))
            # Clap on 2 and 4
            if b in [1, 3]:
                tracks[10].append(Message('note_on', note=39, velocity=100, channel=9, time=0))
                tracks[10].append(Message('note_off', note=39, velocity=0, channel=9, time=240))
            else:
                tracks[10].append(Message('note_off', note=39, velocity=0, channel=9, time=240)) # Dummy shift

        # Bass
        for b in range(4):
            note = 46 if b%2==0 else 53
            tracks[4].append(Message('note_on', note=note, velocity=90, channel=3, time=0))
            tracks[4].append(Message('note_off', note=note, velocity=0, channel=3, time=480))

        # Violin (Layer 1)
        for n in berendans:
            tracks[1].append(Message('note_on', note=n, velocity=85, channel=0, time=0))
            tracks[1].append(Message('note_off', note=n, velocity=0, channel=0, time=480))

        # Synth (Layer 2) - Bar 4+
        if bar >= 4:
            for n in koos:
                tracks[2].append(Message('note_on', note=n, velocity=90, channel=1, time=0))
                tracks[2].append(Message('note_off', note=n, velocity=0, channel=1, time=480))
        else:
            # Silence padding
            for _ in koos: tracks[2].append(Message('note_off', note=0, velocity=0, channel=1, time=480))

        # Guitar (Layer 3) - Bar 8+
        if bar >= 8:
            step = 1920 // len(polo)
            for n in polo:
                tracks[3].append(Message('note_on', note=n, velocity=95, channel=2, time=0))
                tracks[3].append(Message('note_off', note=n, velocity=0, channel=2, time=step))
        else:
             for _ in range(4): tracks[3].append(Message('note_off', note=0, velocity=0, channel=2, time=480))

    mid.save(MIDI_PATH)

def render_hq():
    # Fluidsynth render
    cmd_fs = ["fluidsynth", "-ni", SOUNDFONT, MIDI_PATH, "-F", WAV_PATH, "-r", "44100"]
    subprocess.run(cmd_fs, check=True)
    # Opus conversion
    cmd_ffmpeg = ["ffmpeg", "-i", WAV_PATH, "-codec:a", "libopus", "-application", "voip", "-b:a", "64k", OGG_PATH, "-y", "-loglevel", "error"]
    subprocess.run(cmd_ffmpeg, check=True)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(MIDI_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(WAV_PATH), exist_ok=True)
    create_hq_midi()
    render_hq()
    print("HQ Render Complete.")
