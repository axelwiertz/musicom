import struct, sys

sf2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
data = open(sf2, "rb").read()
phdr_pos = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr_pos + 4:phdr_pos + 8])[0]
preset_names = {}
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    preset_num, bank = struct.unpack("<HH", data[off + 20:off + 24])
    preset_names[(bank, preset_num)] = name

for p in (32, 33, 34, 35, 36, 37, 38, 39, 62, 63, 88, 54):
    print(f"preset {p:3d} -> {preset_names.get((0, p), 'MISSING')!r}")
