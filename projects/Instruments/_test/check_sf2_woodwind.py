#!/usr/bin/env python
"""Check SF2 preset names for woodwind programs 65-75."""
import struct

sf2 = '/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2'
data = open(sf2, 'rb').read()
phdr_pos = data.find(b'phdr')
phdr_size = struct.unpack('<I', data[phdr_pos + 4:phdr_pos + 8])[0]
for i in range(phdr_size // 38):
    off = phdr_pos + 8 + i * 38
    name = data[off:off + 20].split(b'\x00')[0].decode('latin1')
    preset_num, bank = struct.unpack('<HH', data[off + 20:off + 24])
    if 64 <= preset_num <= 75 and bank == 0:
        print(f'  preset {preset_num}: {name!r}')
