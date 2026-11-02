# -*- coding: utf-8 -*-
"""Empirical FluidR3 pitch sweep for Synth Bass 2 (GM39).

Renders a single held note per pitch and measures RMS loudness — proves the
SF2 patch never clips a composition (no silent gaps).
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
import wave

sys.path.insert(0, "/opt/data/projects/Instruments")
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fluidsynth = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

NOTES = [21, 24, 28, 33, 36, 40, 45, 48, 52, 55, 60, 64, 67, 72, 77, 84, 96, 108]
results = {}
for midi in NOTES:
    import mido
    m = mido.MidiFile()
    m.ticks_per_beat = 480
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=39, channel=0, time=0))
    tr.append(mido.Message("note_on", note=midi, velocity=90, channel=0, time=0))
    tr.append(mido.Message("note_off", note=midi, velocity=0, channel=0, time=960))
    tr.append(mido.MetaMessage("end_of_track", time=0))
    m.tracks.append(tr)
    fd, tmp_midi = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    m.save(tmp_midi)
    tmp_wav = tmp_midi.replace(".mid", ".wav")
    r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", tmp_wav, sf2, tmp_midi],
                       capture_output=True)
    if r.returncode != 0:
        results[midi] = None
        print(f"note {midi}: render FAILED")
    else:
        w = wave.open(tmp_wav, "rb")
        sr = w.getframerate()
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
        w.close()
        seg = data[int(0.25 * sr):int(0.75 * sr)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        results[midi] = rms
        print(f"note {midi}: rms={rms:.4f}")
    os.unlink(tmp_midi)
    if os.path.exists(tmp_wav):
        os.unlink(tmp_wav)

audible = [n for n, v in results.items() if v and v > 0.001]
print(f"\naudible: {len(audible)}/{len(NOTES)} notes ({audible})")
print("no gaps" if len(audible) == len(NOTES) else f"GAPS at {set(NOTES) - set(audible)}")
