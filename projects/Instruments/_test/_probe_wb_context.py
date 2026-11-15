# -*- coding: utf-8 -*-
"""Context measurements for the woodblock write-up.

1. Spectral centroid of GM115 vs neighbouring percussion patches (same note).
2. Channel-9 GM percussion woodblocks (76 Hi / 77 Low) — do they differ in pitch?
"""
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


def render(pgm, pitch, vel=100, channel=0, bars=1):
    comp = UnitMatrixComposer(bpm=90, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("X", program=pgm, channel=channel)
    comp.add_section("A", bars=bars)
    u = MusicUnit()
    u.add_event(MusicEvent(pitch, vel, 0, 240))
    u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR * bars))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    mid = os.path.join(OUT, "_ctx.mid")
    wav = os.path.join(OUT, "_ctx.wav")
    comp.to_midi(mid)
    subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid], capture_output=True, check=True)
    with wave.open(wav) as w:
        sr = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    d = d.reshape(-1, d.shape[1]).mean(axis=1) if d.ndim > 1 else d
    os.unlink(mid)
    os.unlink(wav)
    return d, sr


def centroid(d, sr, secs=0.12):
    seg = d[:int(secs * sr)]
    spec = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    return float(np.sum(freqs * spec) / np.sum(spec))


print("=== centroid at note 72 (C5), vel 100, first 120 ms ===")
for pgm, label in [(115, "Woodblock"), (113, "Agogo"), (12, "Marimba"), (13, "Xylophone"),
                   (114, "Steel Drums")]:
    d, sr = render(pgm, 72)
    print(f"  GM{pgm:3d} {label:12s} centroid={centroid(d, sr):7.0f} Hz "
          f"peak={float(np.max(np.abs(d))):.3f}")

print("\n=== channel-9 GM percussion woodblocks ===")
for note, label in [(76, "Hi Wood Block"), (77, "Low Wood Block"),
                    (75, "Claves"), (37, "Side Stick")]:
    d, sr = render(0, note, channel=9)
    seg = d[:int(0.10 * sr)]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1 / sr)
    i = np.argmax(spec)
    top = [round(float(freqs[j])) for j in np.argsort(spec)[-4:]]
    print(f"  ch9 note {note:3d} {label:14s} f0={freqs[i]:7.0f} Hz peak={float(np.max(np.abs(d))):.3f} "
          f"centroid={centroid(d, sr):6.0f} Hz top_bins={sorted(top)}")
