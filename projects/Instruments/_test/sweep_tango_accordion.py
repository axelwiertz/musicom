# -*- coding: utf-8 -*-
"""Empirical FluidR3 audibility sweep for GM23 "Tango Accordion" (Bandoneon).

Renders single held notes across the keyboard and reports RMS per note —
proves the SF2 patch never goes silent inside the documented writing band.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from mido import MidiFile, MidiTrack, Message

sys.path.insert(0, "/opt/data/projects/Instruments")
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
print("SoundFont:", sf2)

notes = [24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108]
results = {}
with tempfile.TemporaryDirectory() as td:
    for midi_note in notes:
        f = 440.0 * 2.0 ** ((midi_note - 69) / 12.0)
        mid = MidiFile(ticks_per_beat=480)
        tr = MidiTrack()
        tr.append(Message("program_change", program=23, channel=0, time=0))
        tr.append(Message("note_on", note=midi_note, velocity=90, channel=0, time=0))
        tr.append(Message("note_off", note=midi_note, velocity=0, channel=0, time=480 * 2))
        mid.tracks.append(tr)
        mpath = os.path.join(td, f"n{midi_note}.mid")
        wpath = os.path.join(td, f"n{midi_note}.wav")
        mid.save(mpath)
        r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wpath, sf2, mpath],
                           capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        with wave.open(wpath, "rb") as w:
            sr = w.getframerate()
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        seg = data[int(0.15 * sr):int(1.6 * sr)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        results[midi_note] = rms
        print(f"note {midi_note:3d} ({f:7.1f} Hz) -> RMS {rms:.4f} "
              f"{'OK' if rms > 0.005 else 'SILENT?'}")

audible = [n for n, r in results.items() if r > 0.005]
print(f"\nSweep: {len(audible)}/{len(notes)} notes audible: {audible}")
print("ALL AUDIBLE" if len(audible) == len(notes) else "GAPS FOUND")
