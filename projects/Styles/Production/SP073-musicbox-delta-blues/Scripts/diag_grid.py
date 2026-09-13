#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnose the rhythmic-grid metric: percussion stem alone vs full mix."""
import wave
from pathlib import Path

import numpy as np
import mido

ROOT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
            'SP073-musicbox-delta-blues')
SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100


def load(path):
    with wave.open(str(path), 'rb') as wf:
        n, ch, r = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        a = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            np.float32) / 32768.0
    return a.reshape(-1, ch).mean(axis=1) if ch == 2 else a


mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb
t = 0
onsets = []
for m in mid.tracks[4]:
    t += m.time
    if m.type == 'note_on' and m.velocity:
        onsets.append((t * spt, m.note, m.velocity))
onsets.sort()

for label, path in (('perc stem', ROOT / 'Audio/stems_wet/track_Percussion_tines.wav'),
                    ('full mix', ROOT / 'SP073-musicbox-delta-blues.wav')):
    x = load(path)
    a = np.abs(x)
    hop = 32
    nf = len(a) // hop
    env = a[:nf * hop].reshape(-1, hop).max(axis=1)
    tol = int(0.040 * SR / hop)
    per_class = {}
    for (st, note, vel) in onsets:
        c = int(round(st * SR / hop))
        if c - tol < 0 or c + tol >= nf:
            continue
        pk = float(env[c - tol:c + tol + 1].max())
        # local baseline = median of the 60 ms OUTSIDE the tolerance window
        b0, b1 = max(0, c - tol - int(0.06 * SR / hop)), c - tol
        b2, b3 = c + tol + 1, min(nf, c + tol + 1 + int(0.06 * SR / hop))
        base = float(np.median(np.concatenate([env[b0:b1], env[b2:b3]])))
        at = float(env[c])
        ratio = pk / max(base, 1e-6)
        d = per_class.setdefault(note, [0, 0, 0.0, 0.0])
        d[0] += 1
        d[1] += int(ratio > 2.5 or at > 3 * base)
        d[2] += ratio
        d[3] += at / max(base, 1e-6)
    print('==', label, '  env peak %.4f rms %.4f' % (
        float(env.max()), float(np.sqrt(np.mean(x ** 2)))))
    tot_h = tot_n = 0
    for note in sorted(per_class):
        n, h, sr_, sat = per_class[note]
        tot_h += h
        tot_n += n
        print('   GM %-3d n=%-4d peak-vs-base>2.5: %-4d (%.0f%%)  '
              'mean ratio %.2f  mean at/base %.2f' % (
                  note, n, h, 100 * h / n, sr_ / n, sat / n))
    print('   TOTAL %d/%d (%.1f%%)' % (tot_h, tot_n, 100 * tot_h / tot_n))
