import os
import subprocess
import wave
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from mido import MidiFile, MidiTrack, Message

sf2 = discover_soundfont()
print("SF2:", sf2)
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# GM9 = Glockenspiel
notes = [55, 60, 67, 72, 79, 84, 91, 96, 103, 108]
for n in notes:
    mid = MidiFile(ticks_per_beat=480)
    tr = MidiTrack()
    tr.append(Message("program_change", program=9, channel=0, time=0))
    tr.append(Message("note_on", note=n, velocity=100, channel=0, time=0))
    tr.append(Message("note_off", note=n, velocity=0, channel=0, time=960))
    mid.tracks.append(tr)
    mpath = f"/tmp/glock_{n}.mid"
    wpath = f"/tmp/glock_{n}.wav"
    mid.save(mpath)
    subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wpath, sf2, mpath], capture_output=True)
    w = wave.open(wpath, "rb")
    sr = w.getframerate()
    data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    w.close()
    rms = float(np.sqrt(np.mean(data[:int(0.6 * sr)] ** 2)))
    print(f"Note {n}: RMS={rms:.4f}")
