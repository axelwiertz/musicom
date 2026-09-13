#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Narrow-band kick check: the 25-120 Hz band used in verify_final also carries
the thumb-bass tine line (MIDI 40-57 = 82-220 Hz), which dilutes the stomp
onset contrast.  Re-score the stomp in 25-55 Hz only, so the metric cannot be
contaminated by the bass voice.
"""
import json
import wave
from pathlib import Path

import numpy as np
import mido
from scipy.signal import butter, sosfilt

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
stomps = []
for m in mid.tracks[4]:
    t += m.time
    if m.type == 'note_on' and m.velocity and m.note == 36:
        stomps.append(t * spt)
print('stomp hits:', len(stomps))

out = {}
for label, path in (
        ('full mix', ROOT / 'SP073-musicbox-delta-blues.wav'),
        ('isolated perc stem', ROOT / 'Audio/stems_wet/track_Percussion_tines.wav'),
        ('isolated bass stem', ROOT / 'Audio/stems_wet/track_Thumb_Bass_sub.wav'),
        ('dry full mix', ROOT / 'dry_full_mix.wav')):
    x = load(path)
    nyq = SR / 2.0
    sos = butter(2, [25.0 / nyq, 55.0 / nyq], btype='band', output='sos')
    y = sosfilt(sos, x).astype(np.float32)
    del x
    w = int(0.060 * SR)
    p = np.square(y).astype(np.float64)
    del y
    cs = np.concatenate([[0.0], np.cumsum(p)])
    del p
    n = len(cs) - 1
    a = np.clip(np.arange(n) - w // 2, 0, max(n - w, 0))
    e = np.sqrt((cs[a + w] - cs[a]) / float(w))
    del cs, a
    WIN, BASE = int(0.060 * SR), int(0.300 * SR)
    ok = n_s = 0
    ratios = []
    for st in stomps:
        c = int(st * SR)
        a0, b0 = max(0, c - WIN), min(len(e), c + WIN)
        if a0 >= b0 or b0 + 30 >= len(e):
            continue
        pk = float(e[a0:b0].max())
        base = float(np.median(np.concatenate([
            e[max(0, c - BASE):max(0, c - WIN)],
            e[min(len(e), c + WIN):min(len(e), c + BASE)]])))
        r = pk / max(base, 1e-9)
        n_s += 1
        ok += int(r >= 2.0)
        ratios.append(r)
    out[label] = {'slots': n_s, 'hits': ok,
                  'rate': round(ok / max(n_s, 1), 4),
                  'median_rise': round(float(np.median(ratios)), 2)
                  if ratios else 0.0}
    print('%-20s 25-55 Hz  %3d/%3d (%.1f%%)  median rise %.2fx  (env rms %.4f)'
          % (label, ok, n_s, 100 * ok / max(n_s, 1),
             float(np.median(ratios)) if ratios else 0.0,
             float(np.sqrt(np.mean(e ** 2)))))
    del e
out['band_hz'] = [25.0, 55.0]
out['note'] = ('the 25-120 Hz band used in verify_final also carries the '
               'thumb-bass tine line (MIDI 40-57 = 82-220 Hz); narrow-banding '
               'to 25-55 Hz isolates the stomp transposition (MIDI 24 = '
               '32.7 Hz)')
(ROOT / 'Analysis' / 'kick_narrowband.json').write_text(json.dumps(out, indent=2))
print('->', ROOT / 'Analysis' / 'kick_narrowband.json')
