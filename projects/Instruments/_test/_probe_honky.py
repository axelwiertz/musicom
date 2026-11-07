import sys, os, struct, subprocess, tempfile, wave
sys.path.insert(0, "/opt/data/repos/musicom")
import numpy as np
from sound.render.fluidsynth import discover_soundfont
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

sf2 = discover_soundfont()
print("sf2:", sf2)
data = open(sf2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
names = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    nm = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pnum, bank = struct.unpack("<HH", data[off + 20:off + 24])
    names[(bank, pnum)] = nm
for p in (0, 1, 2, 3, 4, 5):
    print("preset", p, "->", names.get((0, p)))

BAR = 1920
fs = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

def render_note(note, vel=90):
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("X", program=3, channel=0)
    c.add_section("A", bars=1)
    u = MusicUnit()
    u.add_event(MusicEvent(note, vel, 0, int(BAR * 0.9)))
    if u.len_ticks() < BAR:
        u.add_event(MusicEvent(0, 0, u.len_ticks(), BAR))
    c.set_unit(0, 0, u)
    assert c.validate()[0]
    fd, mp = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    c.to_midi(mp)
    fd2, wv = tempfile.mkstemp(suffix=".wav"); os.close(fd2); os.unlink(wv)
    r = subprocess.run([fs, "-ni", "-g", "1.2", "-F", wv, sf2, mp], capture_output=True)
    os.unlink(mp)
    if r.returncode != 0 or not os.path.exists(wv):
        print("fail", r.stderr[-300:]); return None
    with wave.open(wv, "rb") as f:
        sr = f.getframerate()
        raw = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64)
    os.unlink(wv)
    mono = raw.reshape(-1, 2).mean(axis=1) if raw.size % 2 == 0 else raw
    return float(np.sqrt(np.mean(mono ** 2)))

for n in range(24, 109, 12):
    print(n, round(render_note(n) or 0, 4))
