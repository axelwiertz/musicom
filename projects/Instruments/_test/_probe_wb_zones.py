# -*- coding: utf-8 -*-
"""Dense pitch map of FluidR3 GM115 — detect key zones / sample steps."""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.render.fluidsynth import discover_soundfont  # noqa: E402

sys.path.insert(0, "/opt/data/projects/Instruments")
from structures import MusicEvent, MusicUnit  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402

SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
OUT = "/opt/data/projects/Instruments/_test"
BAR = 1920


def render(pgm, pitch, vel=100):
    comp = UnitMatrixComposer(bpm=90, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("X", program=pgm, channel=0)
    comp.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(pitch, vel, 0, 240))
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    mid = os.path.join(OUT, "_wb3.mid")
    wav = os.path.join(OUT, "_wb3.wav")
    comp.to_midi(mid)
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid], capture_output=True, check=True)
    with wave.open(wav) as w:
        sr = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    d = d.reshape(-1, d.shape[1]).mean(axis=1) if d.ndim > 1 else d
    os.unlink(mid)
    os.unlink(wav)
    return d, sr


def fundamental(d, sr):
    seg = d[:int(0.10 * sr)]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    # strongest peak below 3 kHz (the block body)
    mask = freqs < 3000
    i = np.argmax(spec * mask)
    return float(freqs[i])


print("note  f_expect   f_peak   ratio")
prev = None
for pitch in range(50, 99, 2):
    d, sr = render(115, pitch)
    f = fundamental(d, sr)
    exp = 440.0 * 2 ** ((pitch - 69) / 12)
    print(f"{pitch:4d} {exp:8.1f} {f:8.1f} {f/exp:7.3f}")
