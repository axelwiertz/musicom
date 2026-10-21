# -*- coding: utf-8 -*-
"""Probe: FluidR3 preset 16 (Drawbar Organ) name + empirical pitch sweep."""
import os
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")

from sound.render.fluidsynth import discover_soundfont
from utilities.env import fluidsynth_bin

sf2 = discover_soundfont()
print("soundfont:", sf2)
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bank, pnum)] = name
print("SF2 preset 16 ->", repr(presets.get((0, 16), "MISSING")))

import mido
from mido import Message, MidiFile, MidiTrack

# one-note-per-file sweep across the claimed range and slightly beyond
for pitch in [20, 24, 29, 36, 43, 48, 55, 60, 67, 72, 79, 84, 89, 93, 96]:
    mid = MidiFile(ticks_per_beat=480)
    t0 = MidiTrack()
    t0.append(Message("program_change", program=0, channel=0, time=0))
    mid.tracks.append(t0)
    t = MidiTrack()
    t.append(Message("program_change", program=16, channel=0, time=0))
    t.append(Message("note_on", note=pitch, velocity=90, channel=0, time=0))
    t.append(Message("note_off", note=pitch, velocity=0, channel=0, time=960))
    mid.tracks.append(t)
    fd, mp = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    mid.save(mp)
    fd, wp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    r = subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-F", wp, sf2, mp],
                       capture_output=True)
    import wave
    import numpy as np
    w = wave.open(wp, "rb")
    n = w.getnframes()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    sr = w.getframerate()
    w.close()
    rms = float(np.sqrt(np.mean(a[: int(0.4 * sr)] ** 2))) if len(a) else 0.0
    peak = float(np.max(np.abs(a))) if len(a) else 0.0
    print(f"pitch {pitch:3d} ({mido.MidiFile and pitch}): rms={rms:.4f} peak={peak:.4f} bytes={os.path.getsize(wp)}")
    os.unlink(mp)
    os.unlink(wp)
print("done")
