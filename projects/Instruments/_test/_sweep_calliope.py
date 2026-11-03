# -*- coding: utf-8 -*-
"""Empirical FluidR3 pitch sweep for GM82 (Lead 3 calliope)."""
import sys, os, wave, subprocess, tempfile
sys.path.insert(0, "/opt/data/projects/Instruments")
import numpy as np
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
fs = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
BAR = 1920

def render_note(note, vel=90, dur_frac=0.9):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=82, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    end = int(BAR * dur_frac)
    u.add_event(MusicEvent(note, vel, 0, end))
    if u.len_ticks() < BAR:
        u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    fd, mp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    c.to_midi(mp)
    fd2, wav = tempfile.mkstemp(suffix=".wav"); os.close(fd2)
    os.unlink(wav)
    r = subprocess.run([fs, "-ni", "-g", "1.2", "-F", wav, sf2, mp], capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wav):
        return None
    with wave.open(wav, "rb") as f:
        sr = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    os.unlink(wav)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    return float(np.sqrt(np.mean(mono ** 2)))

def n_to_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[n % 12]}{n // 12 - 1}"

for n in range(24, 109, 6):
    r = render_note(n)
    print(f"note {n:3d} ({n_to_name(n):>4s})  rms={r if r is None else round(r, 4)}")
