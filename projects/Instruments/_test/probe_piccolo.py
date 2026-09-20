import inspect
import re
from sound.render.pipeline import RenderPipeline
from sound.render.fluidsynth import discover_soundfont
import struct

src = inspect.getsource(RenderPipeline.render_stems)
m = re.search(r"GM_PROGRAMS = \[(.*?)\]", src, re.S)
labels = [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]

sf2 = discover_soundfont()
with open(sf2, "rb") as f:
    data = f.read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name

for p in [72, 73, 75, 76, 77, 78, 79, 14, 10, 8, 21, 22, 23, 115]:
    lbl = labels[p] if p < len(labels) else "OUT_OF_BOUNDS"
    sf2_p = preset_names.get((0, p), "MISSING")
    print(f"GM {p:3d}: pipeline={lbl!r:<25} sf2={sf2_p!r}")
