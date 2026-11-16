# -*- coding: utf-8 -*-
"""Inspect FluidR3 preset 117 structure: zones, generators, samples."""
import struct

SF2 = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
data = open(SF2, "rb").read()


def chunk(name):
    i = data.find(name)
    if i < 0:
        return None
    size = struct.unpack("<I", data[i + 4:i + 8])[0]
    return data[i + 8:i + 8 + size], i


def cstr(b):
    return b.split(b"\x00")[0].decode("latin1")


# --- preset header
phdr, _ = chunk(b"phdr")
n = len(phdr) // 38
presets = {}
for i in range(n):
    off = i * 38
    nm = cstr(phdr[off:off + 20])
    pnum, bank = struct.unpack("<HH", phdr[off + 20:off + 24])
    link = struct.unpack("<H", phdr[off + 24:off + 26])[0]
    presets[(bank, pnum)] = (nm, link, i)
print("preset 117:", presets.get((0, 117)))
print("preset 116:", presets.get((0, 116)))
print("preset 118:", presets.get((0, 118)))

# --- preset bag (zone list) for preset 117
pbag, _ = chunk(b"pbag")
pgen, _ = chunk(b"pgen")
pmod, _ = chunk(b"pmod")
# zones of preset 117 = pbag rows [idx, next_idx)
p117 = presets[(0, 117)]
p116 = presets[(0, 116)]
print("\npbag rows per preset: 116:", p116[2], "->", p116[2] + 1, " 117:", p117[2], "->", p117[2] + 1)
# global zone is shared; preset zones start after the terminal row
# count rows for 117's range
for name, pr in [("116", p116), ("117", p117)]:
    row0 = pr[2]
    # find end: next preset's first zone row (terminal row of this preset)
    # rows are sequential: preset i occupies rows [i, i+1) with global zone in row i
    print(f"preset {name}: zone rows {row0}..{row0 + 1} (pbag len {len(pbag) // 4})")

# Print pbag rows around preset 117 with their generator counts
nrows = len(pbag) // 4
print("\npbag rows (idx, gen_index, mod_index):")
for i in range(max(0, p116[2] - 1), min(nrows, p117[2] + 3)):
    gen_idx, mod_idx = struct.unpack("<HH", pbag[i * 4:i * 4 + 4])
    print(f"  row {i}: gen@ {gen_idx} mod@ {mod_idx}")

# generators for preset 117 zones
print("\npreset generators (zone rows of 117):")
for row in range(p117[2] + 1, nrows):
    gen_idx, mod_idx = struct.unpack("<HH", pbag[row * 4:row * 4 + 4])
    if gen_idx >= len(pgen) // 4:
        break
    # read until terminal generator
    j = gen_idx
    gens = []
    while j < len(pgen) // 4:
        op, val = struct.unpack("<HH", pgen[j * 4:j * 4 + 4])
        if op == 0:  # end of list
            break
        gens.append((op, val))
        j += 1
    print(f"  zone row {row}: {gens}")

# instrument header
inst_chunk, _ = chunk(b"inst")
ninst = len(inst_chunk) // 22
insts = {}
for i in range(ninst):
    off = i * 22
    nm = cstr(inst_chunk[off:off + 20])
    link = struct.unpack("<H", inst_chunk[off + 20:off + 22])[0]
    insts[i] = (nm, link)
# sample header
shdr, _ = chunk(b"shdr")
nsmp = len(shdr) // 46
samples = []
for i in range(nsmp):
    off = i * 46
    nm = cstr(shdr[off:off + 20])
    start, end = struct.unpack("<II", shdr[off + 20:off + 28])
    samples.append((nm, start, end))
print("\ninst count", ninst, "samples", nsmp)
