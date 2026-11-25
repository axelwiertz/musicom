"""Envelope/register probe for FluidR3 presets 50 vs 51."""
import os, sys, wave
import numpy as np
sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/projects/Instruments/_test")
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from _test.render_audio import render_midi

BAR = 1920
OUT = "/opt/data/projects/Instruments/_test/probe_50_51"
TIMES = [0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 3.8]


def build(program, chord, path, bars=2, vel=76):
    comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("Pad", program=program, channel=0)
    comp.add_section("A", bars=bars)
    u = MusicUnit()
    for p in chord:
        u.add_event(MusicEvent(p, vel, 0, BAR * bars))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    comp.to_midi(path)
    return path


def mono_of(wav):
    w = wave.open(wav, "rb"); sr = w.getframerate(); ch = w.getnchannels()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    if ch > 1:
        d = d.reshape(-1, ch).mean(axis=1)
    return d, sr


for pgm in (50, 51):
    for label, chord in (("mid", [60, 64, 67, 71]), ("low", [36, 43, 48, 52]), ("high", [72, 76, 79, 83])):
        mid = build(pgm, chord, f"{OUT}/e_{pgm}_{label}.mid")
        wav = render_midi(mid, f"{OUT}/e_{pgm}_{label}.wav", solo=0)
        d, sr = mono_of(wav)
        peak = float(np.abs(d).max())
        pts = []
        for t in TIMES:
            s = d[int(t*sr): int((t+0.02)*sr)]
            pts.append(np.sqrt(np.mean(s**2)) / max(peak, 1e-9))
        spec = np.abs(np.fft.rfft(d[:int(1.5*sr)]))
        fr = np.fft.rfftfreq(int(1.5*sr), 1/sr)
        cen = float((spec*fr).sum()/max(spec.sum(), 1e-9))
        print(f"GM{pgm} {label:4s} peak={peak:.3f} centroid={cen:7.0f}Hz env=" +
              " ".join(f"{t}:{v:.2f}" for t, v in zip(TIMES, pts)))
