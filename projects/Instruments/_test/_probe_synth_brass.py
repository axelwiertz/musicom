# -*- coding: utf-8 -*-
"""Probe GM62 Synth Brass 1: FluidR3 preset name, RMS/centroid, range sweep."""
import os, sys, struct, wave
sys.path.insert(0, "/opt/data/projects/Instruments")
import numpy as np
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from _test.render_audio import render_midi
from sound.render.fluidsynth import discover_soundfont

sf2 = discover_soundfont()
print("SoundFont:", sf2)

data = open(sf2, "rb").read()
p = data.find(b"phdr")
size = struct.unpack("<I", data[p + 4:p + 8])[0]
names = {}
for i in range(size // 38):
    off = p + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pn)] = nm
for pgm in [62, 63, 55, 54, 82, 83, 84, 85]:
    print(f"  preset {pgm:3d} -> {names.get((0, pgm), 'MISSING')!r}")

BAR = 1920

def render_prog(pgm, note=60, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=pgm, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(note, vel, 0, BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    mp = f"/opt/data/projects/Instruments/_test/_sb_probe_{pgm}_{note}.mid"
    c.to_midi(mp)
    w = f"/opt/data/projects/Instruments/_test/_sb_probe_{pgm}_{note}.wav"
    render_midi(mp, w, solo=0)
    with wave.open(w, "rb") as f:
        sr = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    spec = np.abs(np.fft.rfft(mono[:sr]))
    freqs = np.fft.rfftfreq(sr, 1 / sr)
    cen = float((spec * freqs).sum() / max(spec.sum(), 1e-9))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    return rms, cen

for pgm in [62, 55, 54]:
    r, c = render_prog(pgm, 60)
    r2, c2 = render_prog(pgm, 84)
    print(f"{pgm:3d} {names.get((0,pgm),'?'):20s} rmsC4={r:7.1f} cen={c:7.0f} | rmsC6={r2:7.1f} cen={c2:7.0f}")

# GM62 full pitch sweep (RMS at vel 90, held notes)
print("\nGM62 pitch sweep:")
sweep = {}
for n in range(24, 109, 6):
    rms, cen = render_prog(62, n)
    sweep[n] = rms
    print(f"  note {n:3d}: RMS = {rms:8.1f} {'AUDIBLE' if rms > 100 else 'SILENT'}")
aud = [n for n, r in sweep.items() if r > 100]
print("audible:", aud)
