import os
import sys
import numpy as np
import wave
from sound.render.fluidsynth import discover_soundfont
import subprocess
import mido

sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

mid = mido.MidiFile(ticks_per_beat=480)
track0 = mido.MidiTrack()
mid.tracks.append(track0)
track0.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

track1 = mido.MidiTrack()
mid.tracks.append(track1)
track1.append(mido.Message('program_change', channel=0, program=8, time=0))

# Celesta sounding range: C4 (60) to C8 (108)
# Also check transposed range C3 (48) to C4 (60)
notes = [48, 53, 60, 65, 72, 77, 84, 89, 96, 101, 108]
for n in notes:
    track1.append(mido.Message('note_on', channel=0, note=n, velocity=85, time=0))
    track1.append(mido.Message('note_off', channel=0, note=n, velocity=64, time=240))

mid_path = "/opt/data/projects/Instruments/_test/celesta_sweep.mid"
wav_path = "/opt/data/projects/Instruments/_test/celesta_sweep.wav"
mid.save(mid_path)

subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wav_path, sf2, mid_path], check=True)
print(f"Rendered {wav_path}, size={os.path.getsize(wav_path)}")

w = wave.open(wav_path, "rb")
sr = w.getframerate()
nframes = w.getnframes()
audio = np.frombuffer(w.readframes(nframes), dtype=np.int16).astype(np.float32) / 32768.0
w.close()

step = int(0.25 * sr)
for i, n in enumerate(notes):
    chunk = audio[i*step:(i+1)*step]
    rms = np.sqrt(np.mean(chunk**2))
    print(f"Note {n:3d} (freq {440*2**((n-69)/12):6.1f} Hz): rms={rms:.4f}")
