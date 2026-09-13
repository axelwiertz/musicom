#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Why does the strict per-note pitch check miss on the lead tine?

Hypothesis: the pluck/mechanics click is broadband for the first ~2-3 ms plus
render_note() applies a 2 ms noise transient of amplitude 0.35*brightness, so a
30 ms window that starts AT the onset is dominated by click noise, not by the
tine fundamental.  Diagnostic: re-measure the same slots with the window
delayed 10 ms and 20 ms past the onset and compare hit rates.
"""
import json
from pathlib import Path

import numpy as np
import mido

from sound.synthesis.music_box import midi_to_freq

ROOT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
            'SP073-musicbox-delta-blues')
SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100


def load(path):
    import wave
    with wave.open(str(path), 'rb') as wf:
        n, ch, r = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        a = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            np.float32) / 32768.0
    return a.reshape(-1, ch).mean(axis=1) if ch == 2 else a


def dom_peak(win, lo=50.0, hi=1000.0):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    fr = np.fft.rfftfreq(len(win), 1.0 / SR)
    a, b = np.searchsorted(fr, lo), np.searchsorted(fr, hi)
    return float(fr[np.argmax(spec[a:b]) + a])


mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb


def parse(tr):
    tt = 0
    o = {}
    out = []
    for m in mid.tracks[tr]:
        tt += m.time
        if m.type == 'note_on' and m.velocity:
            o.setdefault(m.note, []).append(tt)
        elif m.type == 'note_off' or (m.type == 'note_on' and not m.velocity):
            if o.get(m.note):
                st = o[m.note].pop(0)
                out.append((st * spt, (tt - st) * spt, m.note, m.velocity))
    return sorted(out)


notes = parse(1)
stem = load(ROOT / 'Audio/stems_wet/track_Resonator_Guitar_lead.wav')
ons = np.array([n[0] for n in notes])
print('lead notes %d  stem rms %.4f' % (len(notes),
                                        float(np.sqrt(np.mean(stem ** 2)))))

for delay_ms in (0.0, 10.0, 20.0, 40.0):
    ok = n = amb = 0
    ratios = []
    for (st, dur, note, vel) in notes:
        nxt = ons[ons > st + 1e-6]
        gap = float(nxt.min() - st) if len(nxt) else 9.9
        wl = min(max(dur, 0.030), 0.15, max(0.030, 0.8 * gap))
        i0 = int((st + delay_ms * 0.001) * SR)
        i1 = i0 + int(wl * SR)
        if i1 >= len(stem):
            continue
        win = stem[i0:i1]
        if len(win) < 1024 or float(np.abs(win).max()) < 0.004:
            continue
        if delay_ms * 0.001 + wl > gap:
            amb += 1
            continue
        d = dom_peak(win)
        f0 = midi_to_freq(note)
        hit = any(abs(d - f0 * h) / (f0 * h) < 0.02 for h in (1, 2, 3, 4))
        n += 1
        ok += int(hit)
        ratios.append(d / f0)
    r = np.array(ratios)
    print('delay %4.1f ms: strict %4d/%4d (%.1f%%)  ambiguous %d  '
          'dom/f0 median %.3f  pct on harmonic 2/3/4: %.0f%%/%.0f%%/%.0f%%' % (
              delay_ms, ok, n, 100 * ok / max(n, 1), amb,
              float(np.median(r)) if len(r) else 0,
              100 * float(np.mean((np.abs(r - 2) < 0.04))) if len(r) else 0,
              100 * float(np.mean((np.abs(r - 3) < 0.06))) if len(r) else 0,
              100 * float(np.mean((np.abs(r - 4) < 0.08))) if len(r) else 0))
    del r

# For the MISSES, is the dominant peak the fundamental of a NEIGHBOURING note
# that is still ringing (tonal overlap in a dense monophonic line) rather than
# noise?  Classify each strict slot as: self / prev_ring / next_ring / other.
his = np.array([n[2] for n in notes])
print('\nmiss classification on strict slots (delay 0 ms):')
tally = {'self': 0, 'prev_ring': 0, 'next_ring': 0, 'other': 0}
other_hz = []
for i, (st, dur, note, vel) in enumerate(notes):
    nxt = ons[ons > st + 1e-6]
    gap = float(nxt.min() - st) if len(nxt) else 9.9
    wl = min(max(dur, 0.030), 0.15, max(0.030, 0.8 * gap))
    i0 = int(st * SR)
    win = stem[i0:i0 + int(wl * SR)]
    if len(win) < 1024 or float(np.abs(win).max()) < 0.004:
        continue
    if wl > gap:
        continue
    d = dom_peak(win)
    f0 = midi_to_freq(note)
    if any(abs(d - f0 * h) / (f0 * h) < 0.02 for h in (1, 2, 3, 4)):
        tally['self'] += 1
        continue
    prev = his[max(0, i - 4):i]
    if any(abs(d - midi_to_freq(p) * h) / (midi_to_freq(p) * h) < 0.02
           for p in prev for h in (1, 2, 3, 4)):
        tally['prev_ring'] += 1
        continue
    nxtn = his[i + 1:i + 3]
    if any(abs(d - midi_to_freq(p) * h) / (midi_to_freq(p) * h) < 0.02
           for p in nxtn for h in (1, 2, 3, 4)):
        tally['next_ring'] += 1
        continue
    tally['other'] += 1
    if len(other_hz) < 15:
        other_hz.append((note, round(d, 1), round(f0, 1)))
print(tally)
print('unexplained examples (note, dom_hz, self_f0):', other_hz)
tot = sum(tally.values())
print('explained tonal content: %.1f%% of strict slots' % (
    100 * (tally['self'] + tally['prev_ring'] + tally['next_ring']) /
    max(tot, 1)))
