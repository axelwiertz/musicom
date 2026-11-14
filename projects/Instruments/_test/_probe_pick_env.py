# -*- coding: utf-8 -*-
"""Envelope probe: GM34 picked vs GM33 fingered, note 40, 2 s hold."""
import os, subprocess, tempfile, wave
import numpy as np, mido
from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
FS = os.environ.get("MUSICOM_FLUIDSYNTH", "/opt/data/micromamba/envs/musicom/bin/fluidsynth")


def render(pitch, program, vel=90, dur=1920):
    m = mido.MidiFile(); m.ticks_per_beat = 480
    t0 = mido.MidiTrack(); m.tracks.append(t0)
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    t0.append(mido.MetaMessage("end_of_track", time=2 * dur))
    t1 = mido.MidiTrack(); m.tracks.append(t1)
    t1.append(mido.Message("program_change", program=program, channel=0, time=0))
    t1.append(mido.Message("note_on", note=pitch, velocity=vel, channel=0, time=0))
    t1.append(mido.Message("note_off", note=pitch, velocity=0, channel=0, time=dur))
    t1.append(mido.MetaMessage("end_of_track", time=dur))
    fd, mid = tempfile.mkstemp(suffix=".mid"); os.close(fd); m.save(mid)
    wav = mid.replace(".mid", ".wav")
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid], capture_output=True)
    assert r.returncode == 0, r.stderr[-300:]
    w = wave.open(wav, "rb"); sr = w.getframerate()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    w.close(); os.unlink(mid); os.unlink(wav)
    return sr, d.astype(np.float32) / 32768.0


for prog in (33, 34):
    sr, a = render(40, prog, 90, 1920)
    print(f"\nprogram {prog} dur={len(a)/sr:.2f}s")
    for ms in (2, 5, 10, 20, 30, 50, 80, 120, 200, 400, 800, 1200, 1500, 1900):
        i = int(ms / 1000 * sr)
        seg = a[max(0, i - 200):i + 200]
        print(f"  t={ms:5d}ms  env={np.max(np.abs(seg)):.4f}")
