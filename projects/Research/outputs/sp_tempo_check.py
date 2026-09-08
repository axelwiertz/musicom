# -*- coding: utf-8 -*-
"""Print tempo + channel/program layout of source MIDI."""
import mido

path = "/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid"
mf = mido.MidiFile(path)
for ti, track in enumerate(mf.tracks):
    t = 0
    metas = []
    for msg in track:
        t += msg.time
        if msg.type == "set_tempo":
            metas.append(f"tempo={msg.tempo}us ({mido.tempo2bpm(msg.tempo):.1f} BPM) at tick {t}")
        elif msg.type == "time_signature":
            metas.append(f"time_sig={msg.numerator}/{msg.denominator} at tick {t}")
        elif msg.type == "program_change":
            metas.append(f"program={msg.program} ch={msg.channel} at tick {t}")
    if metas:
        print(f"track {ti} ({track.name}): {metas}")
print(f"total_len={mf.length:.3f}s")
