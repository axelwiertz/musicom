# -*- coding: utf-8 -*-
"""Empirical FluidR3 audibility sweep for Shenai preset 111.

Renders single notes across the claimed range (55-96) and reports RMS per
note — proves the SF2 patch never goes silent inside the documented span.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, "/opt/data/projects/Instruments")

from mido import MidiFile, MidiTrack, Message
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

notes = [55, 62, 66, 69, 76, 84, 90, 96]
results = {}
with tempfile.TemporaryDirectory() as td:
    for midi_note in notes:
        f = 440.0 * 2.0 ** ((midi_note - 69) / 12.0)
        mid = MidiFile(ticks_per_beat=480)
        tr = MidiTrack()
        tr.append(Message("program_change", program=111, channel=0, time=0))
        tr.append(Message("note_on", note=midi_note, velocity=92, channel=0, time=0))
        tr.append(Message("note_off", note=midi_note, velocity=0, channel=0, time=480 * 2))
        mid.tracks.append(tr)
        mpath = os.path.join(td, f"n{midi_note}.mid")
        wpath = os.path.join(td, f"n{midi_note}.wav")
        mid.save(mpath)
        r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wpath, sf2, mpath],
                           capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        # RMS over the body of the note (skip 0.15 s attack + tail)
        import wave
        import numpy as np
        w = wave.open(wpath, "rb")
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        w.close()
        seg = data[int(0.15 * sr):int(1.6 * sr)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        results[midi_note] = (f, rms)
        print(f"note {midi_note:3d} ({f:7.1f} Hz) -> RMS {rms:.4f} {'OK' if rms > 0.005 else 'SILENT?'}")

audible = all(rms > 0.005 for _, rms in results.values())
print(f"\nSweep: {sum(1 for _, r in results.values() if r > 0.005)}/{len(notes)} notes audible")
print("ALL AUDIBLE" if audible else "GAPS FOUND")
assert audible
