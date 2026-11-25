import inspect, re, struct, sys
from sound.render.pipeline import RenderPipeline
src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]
print("len labels", len(labels))
for i in (50, 51, 52, 62, 88):
    print(i, repr(labels[i]))

from sound.render.fluidsynth import discover_soundfont
sf2 = discover_soundfont()
print("sf2:", sf2)
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos+4:phdr_pos+8])[0]
names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i*38
    name = data[off:off+20].split(b"\x00")[0].decode("latin1")
    pn, bank = struct.unpack("<HH", data[off+20:off+24])
    names[(bank, pn)] = name
for p in (48, 49, 50, 51, 90):
    print("preset", p, "->", repr(names.get((0, p), "MISSING")))
