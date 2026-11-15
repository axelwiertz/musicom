# -*- coding: utf-8 -*-
"""Check whether FluidR3 GM115 pitch-tracks: dominant spectral peaks per note."""
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
    mid = os.path.join(OUT, "_wb2.mid")
    wav = os.path.join(OUT, "_wb2.wav")
    comp.to_midi(mid)
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid], capture_output=True, check=True)
    with wave.open(wav) as w:
        sr = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    d = d.reshape(-1, d.shape[1]).mean(axis=1) if d.ndim > 1 else d
    os.unlink(mid)
    os.unlink(wav)
    return d, sr


def peaks(d, sr, n=6):
    seg = d[:int(0.12 * sr)]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    # local maxima
    idx = [i for i in range(2, len(spec) - 2)
           if spec[i] > spec[i - 1] and spec[i] > spec[i + 1] and spec[i] > 0.05 * spec.max()]
    idx = sorted(idx, key=lambda i: -spec[i])[:n]
    return sorted((round(freqs[i]), round(float(spec[i] / spec.max()), 2)) for i in idx)


for pgm, label in [(115, "Woodblock")]:
    print(f"=== GM{pgm} {label} ===")
    for pitch in (48, 60, 72, 84, 96):
        d, sr = render(pgm, pitch)
        f_expect = 440.0 * 2 ** ((pitch - 69) / 12)
        print(f" note {pitch} (expect {f_expect:.0f} Hz): peaks {peaks(d, sr)}")
