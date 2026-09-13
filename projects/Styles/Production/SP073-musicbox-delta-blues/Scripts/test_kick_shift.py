#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is the stomp tine audible?  Compare transposition choices.

Confound: the 25-120 Hz band carries the continuous thumb-bass tine line, so a
stomp onset cannot stand out against a +-300 ms baseline that already contains
bass energy.  Measure the stomp on its ISOLATED class bus instead, and test
shift = -12 (MIDI 24, 32.7 Hz) vs 0 (MIDI 36, 65.4 Hz = the source kick's own
fundamental) vs +12 (MIDI 48, 130.8 Hz).
"""
import json
from pathlib import Path

import numpy as np
import mido
from scipy.signal import butter, sosfiltfilt

from sound.synthesis.music_box import TwinCombMusicBox

SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb
t = 0
hits = []
for m in mid.tracks[4]:
    t += m.time
    if m.type == 'note_on' and m.velocity:
        hits.append((t * spt, m.note, m.velocity))
stomp = [h for h in hits if h[1] == 36]
print('stomp hits:', len(stomp))


def band_env(x, lo, hi, win_ms):
    nyq = SR / 2.0
    sos = butter(2, [max(1e-4, lo / nyq), min(0.999, hi / nyq)],
                 btype='band', output='sos')
    y = sosfiltfilt(sos, np.asarray(x, dtype=np.float64))
    w = max(8, int(win_ms * 0.001 * SR))
    return np.sqrt(np.convolve(y * y, np.ones(w) / w, mode='same'))


def vel_gain(vel, ref=90.0, lo=0.22, hi=1.30):
    return float(np.clip((vel / ref) ** 1.5, lo, hi))


results = {}
for shift in (-12, 0, 12):
    for decay in (0.12, 0.22, 0.45):
        mb = TwinCombMusicBox(sample_rate=SR, detune_cents=10.0, decay=decay,
                              pan=0.0)
        mb.comb_a.brightness = 0.55
        mb.comb_b.brightness = 0.53
        mb.mechanics = 0.30
        mb.jitter_cents = 4.0
        n = int((hits[-1][0] + 2.0) * SR)
        b = np.zeros(n, dtype=np.float64)
        for i, (st, note, vel) in enumerate(stomp):
            seg = mb.render_note(note + shift, duration=2.6 * decay, seed=i)
            seg = seg.mean(axis=1) * vel_gain(vel) * 0.95
            s = int(st * SR)
            e = min(n, s + seg.shape[0])
            b[s:e] += seg[:e - s]
        note_pitch = 36 + shift
        f0 = 440.0 * 2 ** ((note_pitch - 69) / 12.0)
        lo, hi = max(20.0, f0 * 0.7), min(12000.0, f0 * 1.6)
        e = band_env(b, lo, hi, 60.0)
        W, B = int(0.060 * SR), int(0.300 * SR)
        n_ok = 0
        ratios = []
        for (st, note, vel) in stomp:
            c = int(st * SR)
            a, b1 = max(0, c - W), min(len(e), c + W)
            if a >= b1 or b1 + 30 >= len(e):
                continue
            pk = float(e[a:b1].max())
            m0, m1 = max(0, c - B), max(0, c - W)
            m2, m3 = min(len(e), c + W), min(len(e), c + B)
            base = float(np.median(np.concatenate([e[m0:m1], e[m2:m3]])))
            ratios.append(pk / max(base, 1e-9))
            n_ok += int(pk / max(base, 1e-9) >= 2.0)
        key = 'shift%+d_decay%.2f' % (shift, decay)
        results[key] = {'midi': note_pitch, 'f0_hz': round(f0, 1),
                        'hits': n_ok, 'slots': len(ratios),
                        'rate': round(n_ok / max(len(ratios), 1), 3),
                        'median_rise': round(float(np.median(ratios)), 2)
                        if ratios else 0.0,
                        'iso_rms': round(float(np.sqrt(np.mean(b ** 2))), 4)}
        print('%-22s MIDI %-3d f0 %7.1f Hz  %3d/%3d (%.0f%%)  rise %.2fx  '
              'iso_rms %.4f' % (key, note_pitch, f0, n_ok, len(ratios),
                                100 * n_ok / max(len(ratios), 1),
                                float(np.median(ratios)) if ratios else 0.0,
                                float(np.sqrt(np.mean(b ** 2)))))
        del b, e
Path('/tmp_kick').parent  # no-op
(Path('/opt/data/repos/musicom/projects/Styles/Production/'
      'SP073-musicbox-delta-blues/Analysis/kick_shift_test.json')
 ).write_text(json.dumps(results, indent=2))
