from pathlib import Path

base = Path(__file__).resolve().parents[1]
(base/'MIDI'/'country-hope-loop-v6.mid').write_bytes(b'MThd\x00\x00\x00\x06\x00\x01\x00\x02\x01\xe0MTrk\x00\x00\x00\x00')
print('regen placeholder')
