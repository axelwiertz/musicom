#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Band-limited rhythmic-grid verification for SP-073 (correct metric).

A broadband max-abs envelope cannot judge a percussion grid that lives in
different bands per class (stomp = sub, clap = mid, hats = high) and it also
cannot separate adjacent hits when tines ring.  This script:

  * deduplicates coincident source onsets (the pattern strikes kick+hat, and
    clap/hat, together -- 357 hits collapse to ~180 time slots)
  * for each class, band-limits the mix to that class's register
  * computes a short-window RMS envelope per band
  * tests the envelope at each deduped onset against the LOCAL baseline
    (median of the surrounding +-300 ms excluding +-60 ms around the onset)

Reported per class + total.  Benign miss list included for the report.
"""
import json
import wave
from pathlib import Path

import numpy as np
import mido

ROOT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
            'SP073-musicbox-delta-blues')
SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100

# class -> (band_lo, band_hi, rise_gate, env_win_ms)
# The RMS window must span >= ~2 cycles of the LOWEST partial of that class's
# transposed tine, otherwise a 33 Hz stomp measures as "silent" simply because
# the window is shorter than its period.  Stomp tines land at MIDI 24
# (32.7 Hz) -> 60 ms window; mid/high classes resolve fine at 20 ms.
BANDS = {36: (25.0, 120.0, 2.0, 60.0),      # stomp/kick: sub
         39: (700.0, 4000.0, 2.0, 20.0),    # clap: mid
         42: (4000.0, 12000.0, 2.0, 20.0),  # closed hat
         46: (3500.0, 12000.0, 2.0, 20.0)}  # open hat


def load(path, mono=True):
    with wave.open(str(path), 'rb') as wf:
        n, ch, r = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        a = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            np.float32) / 32768.0
    assert r == SR
    if ch == 2:
        a = a.reshape(-1, 2)
        return a.mean(axis=1) if mono else a
    return a


def band_env(x, lo, hi, win_ms=20.0):
    """Band-limited RMS envelope (zero-phase 2nd-order Butterworth bandpass).

    FFT brick-wall filtering of a 7.7 M-sample buffer OOM-killed this box
    (4 GB), so the band split uses sosfiltfilt in float32 instead.
    """
    from scipy.signal import butter, sosfiltfilt
    nyq = SR / 2.0
    lo_n = max(1e-4, lo / nyq)
    hi_n = min(0.999, hi / nyq)
    sos = butter(2, [lo_n, hi_n], btype='band', output='sos')
    y = sosfiltfilt(sos, np.asarray(x, dtype=np.float64))
    y = np.asarray(y, dtype=np.float32)
    w = max(8, int(win_ms * 0.001 * SR))
    e = np.sqrt(np.convolve(y * y, np.ones(w, dtype=np.float32) / w,
                            mode='same'))
    del y
    return np.asarray(e, dtype=np.float32)


mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb
t = 0
hits_src = []
for m in mid.tracks[4]:
    t += m.time
    if m.type == 'note_on' and m.velocity:
        hits_src.append((t * spt, m.note, m.velocity))
hits_src.sort()

mix = load(ROOT / 'SP073-musicbox-delta-blues.wav')
dur = len(mix) / SR
print('mix %.2f s' % dur)

# dedupe coincident onsets into time slots
slots = []
for (st, note, vel) in hits_src:
    if slots and abs(st - slots[-1][0]) < 0.02:
        slots[-1][1].append(note)
    else:
        slots.append([st, [note]])
print('source hits %d -> %d distinct onset slots' % (len(hits_src), len(slots)))

envs = {note: band_env(mix, lo, hi, win_ms=w)
        for note, (lo, hi, _, w) in BANDS.items()}
print('band envelopes built:', {k: round(float(v.max()), 5)
                                for k, v in envs.items()})

WIN = int(0.060 * SR)      # +-60 ms exclusion around the onset
BASE = int(0.300 * SR)     # +-300 ms local baseline window
per_class = {}
misses = []
total_ok = total_slots = 0
for note, (lo, hi, gate, win_ms) in BANDS.items():
    e = envs[note]
    n = ok = 0
    ratios = []
    for st, notes_in_slot in slots:
        if note not in notes_in_slot:
            continue
        c = int(st * SR)
        a, b = max(0, c - WIN), min(len(e), c + WIN)
        if a >= b or b + 30 >= len(e):
            continue
        pk = float(e[a:b].max())
        m0, m1 = max(0, c - BASE), max(0, c - WIN)
        m2, m3 = min(len(e), c + WIN), min(len(e), c + BASE)
        base = float(np.median(np.concatenate([e[m0:m1], e[m2:m3]])))
        r = pk / max(base, 1e-9)
        n += 1
        ok += int(r >= gate)
        ratios.append(r)
        if r < gate:
            misses.append({'t': round(st, 2), 'gm': note,
                           'ratio': round(r, 2)})
    per_class[note] = {'slots': n, 'hits': ok,
                       'rate': round(ok / max(n, 1), 4),
                       'median_ratio': round(float(np.median(ratios)), 2)
                       if ratios else 0.0,
                       'band_hz': [lo, hi], 'gate': gate}
    total_ok += ok
    total_slots += n
    print('GM %-3d band %5.0f-%-6.0f n=%-4d hits=%-4d (%.1f%%) '
          'median rise %.2fx (gate %.1f)' % (
              note, lo, hi, n, ok, 100 * ok / max(n, 1),
              float(np.median(ratios)) if ratios else 0.0, gate))
print('TOTAL %d/%d (%.1f%%)' % (total_ok, total_slots,
                                100 * total_ok / max(total_slots, 1)))

# silence / RMS profile of the delivered mix
def silence_stats(m):
    sil = float(np.sum(np.abs(m) < 0.001) / len(m))
    rms = [float(np.sqrt(np.mean(m[i:i + SR] ** 2)))
           for i in range(0, len(m), SR)]
    return sil, rms


sil, rms = silence_stats(mix)
rms = [r for r in rms if np.isfinite(r)]
print('silence %.2f%%  peak %.4f  rms min/med/max %.4f/%.4f/%.4f' % (
    100 * sil, float(np.abs(mix).max()), min(rms), float(np.median(rms)),
    max(rms)))
quiet = [i for i, r in enumerate(rms) if r < 0.01]
print('seconds below 0.01 RMS:', quiet)

out = {'duration_s': round(dur, 3),
       'grid_metric': 'band-limited RMS envelope, local baseline '
                      '(median +-300 ms excluding +-60 ms)',
       'source_hits': len(hits_src), 'distinct_onset_slots': len(slots),
       'per_class': per_class,
       'total_hits': total_ok, 'total_slots': total_slots,
       'total_rate': round(total_ok / max(total_slots, 1), 4),
       'misses': misses,
       'silence_ratio': round(sil, 4),
       'rms_per_second': [round(r, 4) for r in rms],
       'rms_seconds_below_0p01': quiet,
       'peak': round(float(np.abs(mix).max()), 4)}
(ROOT / 'Analysis' / 'grid_metrics.json').write_text(json.dumps(out, indent=2))
print('->', ROOT / 'Analysis' / 'grid_metrics.json')
