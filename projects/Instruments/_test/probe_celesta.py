# -*- coding: utf-8 -*-
"""Probe Celesta (GM 8) on FluidR3."""
import os
import mido
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline

sf = discover_soundfont()
print("SF:", sf)

mid = mido.MidiFile(ticks_per_beat=480)
track = mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
track.append(mido.Message('program_change', program=8, channel=0, time=0))

# Test notes C4 to C8: 60, 72, 84, 96, 108
notes = [60, 65, 72, 77, 84, 89, 96, 101, 108]
for p in notes:
    track.append(mido.Message('note_on', note=p, velocity=90, time=0))
    track.append(mido.Message('note_off', note=p, velocity=0, time=480))

test_mid = "/opt/data/projects/Instruments/_test/probe_celesta.mid"
test_wav = "/opt/data/projects/Instruments/_test/probe_celesta.wav"
mid.save(test_mid)

import subprocess
cmd = [
    "/opt/data/micromamba/envs/musicom/bin/fluidsynth",
    "-ni", "-g", "1.2", "-F", test_wav, sf, test_mid
]
subprocess.run(cmd, check=True)
print("WAV rendered, size:", os.path.getsize(test_wav))

# Check sweep audio
import wave
w = wave.open(test_wav, 'rb')
frames = w.readframes(w.getnframes())
samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
w.close()
rms = np.sqrt(np.mean(samples**2))
print(f"Overall RMS: {rms:.4f}, max: {np.max(np.abs(samples)):.4f}")
