# -*- coding: utf-8 -*-
"""Probe FluidR3 preset 28 (Electric Guitar muted): name + range sweep."""
import os
import struct
import subprocess
import sys
import wave

sys.path.insert(0, "/opt/data/projects/Instruments")

from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
print("soundfont:", SF2)
print("size:", os.path.getsize(SF2))

# --- preset name from phdr ---
data = open(SF2, "rb").read()
pos = data.find(b"phdr")
size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
names = {}
for i in range(size // 38):
    off = pos + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pn)] = nm
for p in (26, 27, 28, 29, 30):
    print(f"preset {p}: {names.get((0, p))!r}")

# --- range sweep with a tiny MIDI ---
import mido

def sweep(program, notes, out_wav):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    tr.append(mido.Message("program_change", program=program, channel=0, time=0))
    for n in notes:
        tr.append(mido.Message("note_on", note=n, velocity=100, channel=0, time=0))
        tr.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=480))
    tr.append(mido.MetaMessage("end_of_track", time=0))
    mid.save("/tmp/probe.mid")
    subprocess.run([
        "/opt/data/micromamba/envs/musicom/bin/fluidsynth",
        "-ni", "-g", "1.2", "-F", out_wav, SF2, "/tmp/probe.mid",
    ], check=True, capture_output=True)
    w = wave.open(out_wav, "rb")
    sr, nf = w.getframerate(), w.getnframes()
    raw = w.readframes(nf)
    w.close()
    import numpy as np
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    # 480 ticks @120bpm = 0.5 s per note
    seg = int(0.5 * sr)
    rms = []
    for i in range(len(notes)):
        chunk = a[i * seg:(i + 1) * seg]
        if len(chunk) == 0:
            rms.append(0.0)
        else:
            rms.append(float(np.sqrt(np.mean(chunk ** 2))))
    for n, r in zip(notes, rms):
        print(f"  note {n:3d}: rms {r:.4f}")
    return rms

notes = [28, 33, 38, 40, 43, 45, 48, 52, 55, 59, 62, 64, 67, 71, 74, 76, 79, 84]
print("\nsweep program 28:")
rms = sweep(28, notes, "/tmp/probe28.wav")
print("zero/quiet notes:", [n for n, r in zip(notes, rms) if r < 0.001])
