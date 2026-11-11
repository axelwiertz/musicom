# -*- coding: utf-8 -*-
"""Empirical FluidR3 pitch sweep for GM49 (String Ensemble 2 / Slow Strings)."""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.render.fluidsynth import discover_soundfont

PGM = 49
BAR = 1920
sf2 = discover_soundfont()
fs = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
print("SF2:", sf2)


def render_note(note, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=PGM, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    end = int(BAR * 0.9)
    u.add_event(MusicEvent(note, vel, 0, end))
    if u.len_ticks() < BAR:
        u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    fd, mp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    c.to_midi(mp)
    fd2, wv = tempfile.mkstemp(suffix=".wav"); os.close(fd2)
    os.unlink(wv)
    r = subprocess.run([fs, "-ni", "-g", "1.2", "-F", wv, sf2, mp], capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wv):
        return None
    with wave.open(wv, "rb") as f:
        sr = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    os.unlink(wv)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    return float(np.sqrt(np.mean(mono ** 2)))


def n_to_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[n % 12]}{n // 12 - 1}"


print("Sweep (RMS, velocity 90):")
audible = 0
for n in list(range(12, 110, 12)):
    r = render_note(n)
    if r is not None and r > 0.0:
        audible += 1
    print(f"  note {n:3d} ({n_to_name(n):>4s})  rms={r if r is None else round(r, 4)}")
print(f"audible: {audible}")
