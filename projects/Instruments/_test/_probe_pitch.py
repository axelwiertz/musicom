"""Pitch sanity: does FluidR3 preset 51 sound at the written octave?"""
import sys, wave
import numpy as np
sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/projects/Instruments/_test")
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from _test.render_audio import render_midi

BAR = 1920
OUT = "/opt/data/projects/Instruments/_test/probe_50_51"


def build(program, pitch, path):
    comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("Pad", program=program, channel=0)
    comp.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(pitch, 80, 0, BAR))
    comp.set_unit(0, 0, u)
    ok, msg = comp.validate()
    assert ok, msg
    comp.to_midi(path)
    return path


for pgm in (50, 51):
    for pitch in (48, 60, 72):
        mid = build(pgm, pitch, f"{OUT}/p_{pgm}_{pitch}.mid")
        wav = render_midi(mid, f"{OUT}/p_{pgm}_{pitch}.wav", solo=0)
        w = wave.open(wav, "rb"); sr = w.getframerate(); ch = w.getnchannels()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
        w.close()
        if ch > 1:
            d = d.reshape(-1, ch).mean(axis=1)
        seg = d[int(0.6*sr):int(1.8*sr)]
        spec = np.abs(np.fft.rfft(seg))
        fr = np.fft.rfftfreq(len(seg), 1/sr)
        band = (fr > 40) & (fr < 4000)
        peak_hz = float(fr[band][np.argmax(spec[band])])
        print(f"GM{pgm} written {pitch} ({440*2**((pitch-69)/12):.1f} Hz) "
              f"-> peak {peak_hz:.1f} Hz")
