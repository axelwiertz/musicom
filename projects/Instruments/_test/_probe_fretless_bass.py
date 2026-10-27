# -*- coding: utf-8 -*-
"""Empirical FluidR3 pitch sweep for GM35 Fretless Bass.

Renders one 1-bar solo note per pitch through the same UnitMatrixComposer +
discover_soundfont path as the verify script, and reports RMS. Confirms the
patch is audible across the documented 24–72 span (no silent samples) and
that there is no unexpected hole in the low/mid register.
"""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

import wave
import numpy as np
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from _test.render_audio import render_midi

BAR = 1920
NOTES = [24, 28, 33, 40, 45, 50, 55, 60, 62, 67, 72]

for note in NOTES:
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("FB", program=35, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(note, 90, 0, BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    mp = f"/opt/data/projects/Instruments/_test/_fb_sweep_{note}.mid"
    wp = f"/opt/data/projects/Instruments/_test/_fb_sweep_{note}.wav"
    c.to_midi(mp)
    render_midi(mp, wp, solo=0)
    with wave.open(wp, "rb") as f:
        sr = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    rms = float(np.sqrt(np.mean(mono ** 2)))
    print(f"note {note:3d}: rms={rms:8.1f}")
