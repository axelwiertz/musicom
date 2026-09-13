#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Slice tuning for SP-073: decay/density + pitch-check window on 20 s."""
import time

import numpy as np
import mido

from sound.synthesis.music_box import TwinCombMusicBox, midi_to_freq

SRC = ('/opt/data/repos/musicom/projects/Styles/Blues/027-delta-blues-shack/'
       'MIDI/027_delta_blues.mid')
SR = 44100
T0, T1 = 30.0, 50.0


def fft_dom_peak(win, lo=50.0, hi=1000.0):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    fr = np.fft.rfftfreq(len(win), 1.0 / SR)
    a = np.searchsorted(fr, lo)
    b = np.searchsorted(fr, hi)
    return float(fr[np.argmax(spec[a:b]) + a])


mid = mido.MidiFile(SRC)
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb


def parse(tr):
    t = 0
    openn = {}
    out = []
    for m in mid.tracks[tr]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            openn.setdefault(m.note, []).append((t, m.velocity))
        elif m.type == 'note_off' or (m.type == 'note_on' and not m.velocity):
            if openn.get(m.note):
                st, v = openn[m.note].pop(0)
                out.append((st * spt, (t - st) * spt, m.note, v))
    return sorted(out)


LEAD = [n for n in parse(1) if T0 <= n[0] < T1]
print('lead notes in slice: %d (%.2f/s)' % (len(LEAD), len(LEAD) / (T1 - T0)))

FADE_MS = 30.0


def fade(seg):
    k = int(FADE_MS * 0.001 * SR)
    if seg.shape[0] <= k:
        return seg
    w = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, k)))
    out = seg.copy()
    out[-k:] *= w[:, None]
    return out


onsets = np.array([x[0] - T0 for x in LEAD])
for decay in (0.25, 0.32, 0.45, 0.55):
    mb = TwinCombMusicBox(sample_rate=SR, detune_cents=14.0, decay=decay,
                          pan=-0.22)
    mb.comb_a.brightness = 1.0
    mb.comb_b.brightness = 0.97
    mb.mechanics = 0.16
    mb.jitter_cents = 3.0
    n = int((T1 - T0 + 3.0) * SR)
    buf = np.zeros((n, 2), dtype=np.float64)
    t0 = time.time()
    for i, (st, dur, note, vel) in enumerate(LEAD):
        seg = mb.render_note(note, duration=min(dur + 2.6 * decay, 8.0),
                             seed=1000 + i)
        seg = fade(seg) * np.clip((vel / 90.0) ** 1.5, 0.22, 1.3)
        s = int((st - T0) * SR)
        e = min(n, s + seg.shape[0])
        if s >= n or e <= s:
            continue
        buf[s:e] += seg[:e - s]
    mono = buf.mean(axis=1)
    strict_ok = strict_n = 0
    for (st, dur, note, vel) in LEAD:
        rel = st - T0
        wl = min(max(dur, 0.05), 0.15)
        i0 = int(rel * SR)
        win = mono[i0:i0 + int(wl * SR)]
        if len(win) < 1024 or np.abs(win).max() < 0.004:
            continue
        dom = fft_dom_peak(win)
        f0 = midi_to_freq(note)
        hit = any(abs(dom - f0 * h) / (f0 * h) < 0.02 for h in (1, 2, 3, 4))
        clean = not np.any((onsets > rel + 1e-6) & (onsets < rel + wl))
        if clean:
            strict_n += 1
            strict_ok += int(hit)
    pc_src = np.zeros(12)
    for (st, dur, note, vel) in LEAD:
        pc_src[note % 12] += max(dur, 0.05)
    pc_src /= pc_src.sum()
    pc_out = np.zeros(12)
    for j in range(0, len(mono) - 4096, 4096):
        w = mono[j:j + 4096]
        if np.abs(w).max() < 0.004:
            continue
        f = fft_dom_peak(w)
        m = 12 * np.log2(f / 440.0) + 69
        pc_out[int(round(m)) % 12] += 1
    pc_out /= max(pc_out.sum(), 1)
    print('decay %.2f  peak %.2f  comp %.1fs  strict %d/%d (%.0f%%)  '
          'chroma %.3f' % (decay, np.abs(buf).max(), time.time() - t0,
                           strict_ok, strict_n,
                           100 * strict_ok / max(strict_n, 1),
                           float(np.corrcoef(pc_src, pc_out)[0, 1])))
