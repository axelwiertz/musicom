# -*- coding: utf-8 -*-
"""Empirical FluidR3 audibility sweep for Glockenspiel preset 9."""
import os
import subprocess
import sys
import tempfile
import wave
import numpy as np

sys.path.insert(0, "/opt/data/projects/Instruments")

from mido import MidiFile, MidiTrack, Message
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# Probing full sounding range (79-108) and lower transposed range (55-78)
notes = [55, 60, 67, 72, 79, 84, 88, 91, 96, 100, 103, 108]
results = {}

with tempfile.TemporaryDirectory() as td:
    for midi_note in notes:
        f = 440.0 * 2.0 ** ((midi_note - 69) / 12.0)
        mid = MidiFile(ticks_per_beat=480)
        tr = MidiTrack()
        tr.append(Message("program_change", program=9, channel=0, time=0))
        tr.append(Message("note_on", note=midi_note, velocity=90, channel=0, time=0))
        tr.append(Message("note_off", note=midi_note, velocity=0, channel=0, time=960))
        mid.tracks.append(tr)
        mpath = os.path.join(td, f"n{midi_note}.mid")
        wpath = os.path.join(td, f"n{midi_note}.wav")
        mid.save(mpath)
        r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wpath, sf2, mpath],
                           capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        w = wave.open(wpath, "rb")
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        w.close()
        seg = data[:int(0.6 * sr)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        results[midi_note] = (f, rms)
        print(f"note {midi_note:3d} ({f:7.1f} Hz) -> RMS {rms:.4f} {'OK' if rms > 0.005 else 'SILENT?'}")

audible = all(rms > 0.005 for _, rms in results.values())
print(f"\nSweep: {sum(1 for _, r in results.values() if r > 0.005)}/{len(notes)} notes audible")
print("ALL AUDIBLE" if audible else "GAPS FOUND")
assert audible
