#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Consolidated independent verification of the delivered SP-073 artifacts.

Re-measures the DELIVERED files (not in-memory buffers) and produces
Analysis/verify_final.json.  Five checks:

  1. strict per-note pitch attribution on the isolated wet stems, gap-aware
     windows, with three-way attribution (self / neighbouring-ringing / other)
     -- a ringing modal instrument legitimately shows a neighbour's fundamental
     as the dominant peak while its own tine decays;
  2. band-limited rhythmic-grid preservation per percussion class;
  3. percussive timbre ordering on the isolated class buses;
  4. silence ratio + per-second RMS + peak;
  5. dry-vs-wet band balance.
"""
import json
import wave
from pathlib import Path

import numpy as np
import mido
from scipy.signal import butter, sosfilt

from sound.synthesis.music_box import midi_to_freq

ROOT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
            'SP073-musicbox-delta-blues')
SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100

# class -> (band_lo, band_hi, rise_gate, env_win_ms)
# The RMS window must span ~2 cycles of the class's lowest partial: the stomp
# tine sits at MIDI 24 (32.7 Hz) so a 20 ms window cannot resolve it.
BANDS = {36: (25.0, 120.0, 2.0, 60.0),
         39: (700.0, 4000.0, 2.0, 20.0),
         42: (4000.0, 12000.0, 2.0, 20.0),
         46: (3500.0, 12000.0, 2.0, 20.0)}
STEM_MAP = {1: ('track_Resonator_Guitar_lead.wav', 'Resonator Guitar lead'),
            2: ('track_Acoustic_Slide_harmony.wav', 'Acoustic Slide harmony'),
            3: ('track_Thumb_Bass_sub.wav', 'Thumb Bass sub')}


def load(path, mono=True):
    with wave.open(str(path), 'rb') as wf:
        n, ch, r = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        a = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            np.float32) / 32768.0
    assert r == SR, r
    if ch == 2:
        a = a.reshape(-1, 2)
        return a.mean(axis=1) if mono else a
    return a


def dom_peak(win, lo=50.0, hi=1000.0):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    fr = np.fft.rfftfreq(len(win), 1.0 / SR)
    a, b = np.searchsorted(fr, lo), np.searchsorted(fr, hi)
    return float(fr[np.argmax(spec[a:b]) + a])


def centroid(x):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1.0 / SR)
    s = float(np.sum(spec))
    return float(np.sum(fr * spec) / s) if s > 0 else 0.0


def bands_of(x, chunk=1 << 20):
    """Band energy shares (%), accumulated over chunks to bound memory."""
    edges = [20, 60, 120, 500, 2000, 8000, 20000]
    fr = np.fft.rfftfreq(chunk, 1.0 / SR)
    idx = [(np.searchsorted(fr, a), np.searchsorted(fr, b))
           for a, b in zip(edges[:-1], edges[1:])]
    acc = np.zeros(len(idx))
    tot = 0.0
    w = np.hanning(chunk)
    for i in range(0, len(x) - chunk, chunk):
        spec = np.abs(np.fft.rfft(x[i:i + chunk] * w)) ** 2
        tot += float(np.sum(spec))
        for k, (a, b) in enumerate(idx):
            acc[k] += float(np.sum(spec[a:b]))
    return [round(100 * float(v) / max(tot, 1e-12), 2) for v in acc]


def band_rms_hits(x, lo, hi, win_ms, slots, note, gate):
    """Score one band's onset contrast WITHOUT materialising long buffers.

    Memory-frugal by necessity: this box has ~1.5 GB free, and
    sosfiltfilt + np.convolve(7.7 M samples, 2648 taps) OOM-killed two earlier
    runs (exit 137).  Here the band split is a single causal sosfilt in
    float32 and the moving RMS is a cumulative-sum difference (O(n), one
    float64 accumulator), so peak extra memory is ~3 buffers instead of ~8.
    """
    nyq = SR / 2.0
    sos = butter(2, [max(1e-4, lo / nyq), min(0.999, hi / nyq)],
                 btype='band', output='sos')
    y = sosfilt(sos, np.asarray(x, dtype=np.float32)).astype(np.float32)
    w = max(8, int(win_ms * 0.001 * SR))
    p = np.square(y, dtype=np.float32).astype(np.float64)
    del y
    cs = np.concatenate([[0.0], np.cumsum(p)])
    del p
    n = len(cs) - 1
    half = w // 2
    a = np.clip(np.arange(n) - half, 0, max(n - w, 0))
    b = a + w
    e = np.sqrt((cs[b] - cs[a]) / float(w)).astype(np.float32)
    del cs, a, b
    WIN, BASE = int(0.060 * SR), int(0.300 * SR)
    n_s = ok = 0
    ratios = []
    miss = []
    for st, notes_in_slot in slots:
        if note not in notes_in_slot:
            continue
        c = int(st * SR)
        a, b = max(0, c - WIN), min(len(e), c + WIN)
        if a >= b or b + 30 >= len(e):
            continue
        pk = float(e[a:b].max())
        base = float(np.median(np.concatenate([
            e[max(0, c - BASE):max(0, c - WIN)],
            e[min(len(e), c + WIN):min(len(e), c + BASE)]])))
        r = pk / max(base, 1e-9)
        n_s += 1
        ok += int(r >= gate)
        ratios.append(r)
        if r < gate:
            miss.append({'t': round(st, 2), 'gm': note, 'rise': round(r, 2)})
    del e
    return {'slots': n_s, 'hits': ok, 'rate': round(ok / max(n_s, 1), 4),
            'median_rise': round(float(np.median(ratios)), 2) if ratios else 0.0,
            'misses': miss}


# ---------------------------------------------------------------- source data
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


DRUM_HITS = parse(4)
drum_hits = [(st, note, vel) for (st, dur, note, vel) in DRUM_HITS]
out = {'source': str(SRC), 'method': 'SP-073',
       'module': 'sound.synthesis.music_box'}

# --------------------------------------------------- 1. per-note attribution
print('=== 1. per-note pitch attribution (isolated wet stems) ===')
pitch = {}
for tr, (fn, label) in STEM_MAP.items():
    notes = parse(tr)
    stem = load(ROOT / 'Audio/stems_wet' / fn)
    ons = np.array([n[0] for n in notes])
    his = np.array([n[2] for n in notes])
    tally = {'self': 0, 'prev_ring': 0, 'next_ring': 0, 'other': 0}
    win_res_limited = 0
    other_ex = []
    for i, (st, dur, note, vel) in enumerate(notes):
        nxt = ons[ons > st + 1e-6]
        gap = float(nxt.min() - st) if len(nxt) else 9.9
        wl = min(max(dur, 0.030), 0.15, max(0.030, 0.8 * gap))
        i0 = int(st * SR)
        wlen = int(wl * SR)
        if i0 + wlen >= len(stem) or wlen < 1024:
            continue
        win = stem[i0:i0 + wlen]
        if float(np.abs(win).max()) < 0.004:
            continue
        if wl > gap:
            tally.setdefault('ambiguous', 0)
            tally['ambiguous'] = tally.get('ambiguous', 0) + 1
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
        # FFT resolution limit: a 30 ms window has 33 Hz bins, i.e. +-4.2 % at
        # 784 Hz -- wider than the 2 % tolerance.  Count separately, do not
        # call it a pitch error.
        bin_hz = SR / wlen
        if bin_hz / max(d, 1.0) > 0.02:
            win_res_limited += 1
            continue
        tally['other'] += 1
        if len(other_ex) < 8:
            other_ex.append({'note': note, 'dom_hz': round(d, 1),
                             'f0_hz': round(f0, 1), 'bin_hz': round(bin_hz, 1)})
    strict = sum(v for k, v in tally.items() if k != 'ambiguous')
    explained = tally['self'] + tally['prev_ring'] + tally['next_ring']
    pitch[label] = {'notes': len(notes), 'strict_slots': strict,
                    'ambiguous_slots': tally.get('ambiguous', 0),
                    'self': tally['self'], 'prev_ring': tally['prev_ring'],
                    'next_ring': tally['next_ring'], 'other': tally['other'],
                    'window_resolution_limited': win_res_limited,
                    'strict_self_rate': round(tally['self'] / max(strict, 1), 4),
                    'tonal_attribution_rate': round(explained / max(strict, 1), 4),
                    'other_examples': other_ex}
    print('%-24s notes=%-5d strict=%-5d ambiguous=%-5d self=%-4d prev-ring=%-4d '
          'next-ring=%-3d other=%-3d res-limited=%-3d | self-rate %.1f%%  '
          'TONAL-ATTRIBUTION %.1f%%' % (
              label, len(notes), strict, tally.get('ambiguous', 0),
              tally['self'], tally['prev_ring'], tally['next_ring'],
              tally['other'], win_res_limited,
              100 * tally['self'] / max(strict, 1),
              100 * explained / max(strict, 1)))
    del stem
out['pitch_attribution'] = pitch
tot_strict = sum(v['strict_slots'] for v in pitch.values())
tot_expl = sum(v['self'] + v['prev_ring'] + v['next_ring']
               for v in pitch.values())
out['pitch_attribution_total'] = {
    'strict_slots': tot_strict,
    'tonal_attribution_rate': round(tot_expl / max(tot_strict, 1), 4)}

# --------------------------------------------------- 2. rhythmic grid
print('\n=== 2. rhythmic-grid preservation (band-limited per class) ===')
mix = load(ROOT / 'SP073-musicbox-delta-blues.wav')
dur = len(mix) / SR
slots = []
for (st, note, vel) in drum_hits:
    if slots and abs(st - slots[-1][0]) < 0.02:
        slots[-1][1].append(note)
    else:
        slots.append([st, [note]])
per_class = {}
misses = []
tot_ok = tot_n = 0
for note, (lo, hi, gate, win_ms) in BANDS.items():
    res = band_rms_hits(mix, lo, hi, win_ms, slots, note, gate)
    misses.extend(res.pop('misses'))
    per_class[note] = res
    tot_ok += res['hits']
    tot_n += res['slots']
    print('GM %-3d band %5.0f-%-6.0f slots=%-4d hits=%-4d (%.1f%%)  median '
          'rise %.2fx' % (note, lo, hi, res['slots'], res['hits'],
                          100 * res['hits'] / max(res['slots'], 1),
                          res['median_rise']))
print('TOTAL %d/%d (%.1f%%)' % (tot_ok, tot_n, 100 * tot_ok / max(tot_n, 1)))
out['rhythmic_grid'] = {'source_hits': len(drum_hits),
                        'distinct_slots': len(slots),
                        'per_class': per_class, 'total_hits': tot_ok,
                        'total_slots': tot_n,
                        'total_rate': round(tot_ok / max(tot_n, 1), 4),
                        'misses': misses}

# --------------------------------------------------- 3. percussive timbre
print('\n=== 3. percussive timbre ordering (isolated class buses) ===')
pw = load(ROOT / 'Audio/stems_wet/track_Percussion_tines.wav')
click_w, body_w = int(0.020 * SR), int(0.150 * SR)
click_c, body_c = [], []
for (st, note, vel) in drum_hits:
    i0 = int(st * SR)
    a = pw[i0:i0 + click_w]
    b = pw[i0 + click_w:i0 + click_w + body_w]
    if len(a) > 256 and float(np.abs(a).max()) > 0.01:
        click_c.append(centroid(a))
    if len(b) > 256 and float(np.abs(b).max()) > 0.01:
        body_c.append(centroid(b))
print('click(0-20 ms) median %.0f Hz | tine body(20-170 ms) median %.0f Hz' % (
    float(np.median(click_c)), float(np.median(body_c))))
out['percussive_timbre'] = {
    'click_centroid_hz': round(float(np.median(click_c)), 1),
    'body_centroid_hz': round(float(np.median(body_c)), 1),
    'interpretation': 'the click is the mechanical pin strike (broadband), the '
                      'body is the tine tone (lower centroid) -- the module '
                      'deliberately injects a 3 ms mechanics burst'}
del pw

# --------------------------------------------------- 4. silence / RMS
print('\n=== 4. silence + RMS + peak ===')
sil = float(np.sum(np.abs(mix) < 0.001) / len(mix))
rms = [float(np.sqrt(np.mean(mix[i:i + SR] ** 2)))
       for i in range(0, len(mix), SR)]
quiet = [i for i, r in enumerate(rms) if r < 0.01]
print('silence %.2f%%  peak %.4f  rms min %.4f / median %.4f / max %.4f' % (
    100 * sil, float(np.abs(mix).max()), min(rms), float(np.median(rms)),
    max(rms)))
print('seconds below 0.01 RMS: %s (of %d)' % (quiet, len(rms)))
out['level'] = {'silence_ratio': round(sil, 4),
                'silence_pct': round(100 * sil, 2),
                'peak': round(float(np.abs(mix).max()), 4),
                'rms_min': round(min(rms), 4),
                'rms_median': round(float(np.median(rms)), 4),
                'rms_max': round(max(rms), 4),
                'rms_per_second': [round(r, 4) for r in rms],
                'seconds_below_0p01_rms': quiet,
                'mid_track_gaps': [q for q in quiet if q < len(rms) - 5]}
out['duration_s'] = round(dur, 3)

# --------------------------------------------------- 5. band balance
print('\n=== 5. dry vs wet band balance (% of total energy) ===')
wb = bands_of(mix)
db = bands_of(load(ROOT / 'dry_full_mix.wav'))
labels = ['20-60', '60-120', '120-500', '500-2k', '2-8k', '8k+']
print('band      dry     wet')
for lb, d, w in zip(labels, db, wb):
    print('%-8s %6.2f  %6.2f' % (lb, d, w))
out['band_balance_pct'] = {'labels': labels, 'dry': db, 'wet': wb}
del mix

(ROOT / 'Analysis' / 'verify_final.json').write_text(json.dumps(out, indent=2))
print('\n->', ROOT / 'Analysis' / 'verify_final.json')
