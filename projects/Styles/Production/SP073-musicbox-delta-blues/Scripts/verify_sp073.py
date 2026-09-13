#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent verification of the finished SP-073 render.

Re-measures the delivered WAV (not the in-memory buffers):
  1. rhythmic-grid preservation -- for every source percussion onset, is there
     a local energy peak in the mix within +/-40 ms?  (This is the metric a
     waveform correlation CANNOT give for a synthesis-layer swap.)
  2. tine tone similarity -- spectral centroid measured AFTER the click
     transient (20-150 ms) vs on the click (0-20 ms).
  3. band balance dry vs wet.
  4. pitch: strict onset-slot FFT re-check on the isolated wet stems.
"""
import json
import wave
from pathlib import Path

import numpy as np
import mido

from sound.synthesis.music_box import midi_to_freq

ROOT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
            'SP073-musicbox-delta-blues')
SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/'
           '027-delta-blues-shack/MIDI/027_delta_blues.mid')
SR = 44100
SRC_SR = 44100


def load_wav(path):
    with wave.open(str(path), 'rb') as wf:
        n, ch, rate = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        a = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            np.float32) / 32768.0
    assert rate == SR, rate
    if ch == 2:
        return a.reshape(-1, 2)
    return np.column_stack([a, a])


def midi_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


# ---------------------------------------------------------- source onsets
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = [m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'][0]
spt = tempo / 1e6 / tpb
drum_onsets = []
t = 0
for m in mid.tracks[4]:
    t += m.time
    if m.type == 'note_on' and m.velocity:
        drum_onsets.append((t * spt, m.note, m.velocity))
print('source percussion onsets:', len(drum_onsets))

mix = load_wav(ROOT / 'SP073-musicbox-delta-blues.wav')
mono = mix.mean(axis=1)
del mix
print('mix: %.2f s  peak %.4f  rms %.4f' % (
    len(mono) / SR, float(np.abs(mono).max()),
    float(np.sqrt(np.mean(mono ** 2)))))

# 1. rhythmic grid: local energy peak within +-40 ms of each onset
hop = 64
n_fr = len(mono) // hop
env = np.abs(mono[:n_fr * hop]).reshape(-1, hop).max(axis=1)
w = 8
win_tol = int(0.040 * SR / hop)
hits = 0
misses = []
for (st, note, vel) in drum_onsets:
    c = int(st * SR / hop)
    lo, hi = max(0, c - win_tol), min(n_fr, c + win_tol + 1)
    if lo >= hi:
        continue
    local = env[lo:hi]
    base = float(np.median(env[max(0, c - 40):c - win_tol])) if c > win_tol else 0.0
    pk = float(local.max())
    if pk > max(4.0 * base, 0.02):
        hits += 1
    else:
        misses.append(round(st, 3))
grid_rate = hits / len(drum_onsets)
print('rhythmic-grid preservation: %d/%d onsets have a local energy peak '
      'within +-40 ms (%.1f%%); misses %s' % (
          hits, len(drum_onsets), 100 * grid_rate, misses[:12]))

# 2. percussive timbre: centroid on the click vs the tine body
def centroid(x):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1.0 / SR)
    s = float(np.sum(spec))
    return float(np.sum(fr * spec) / s) if s > 0 else 0.0


perc_wet = load_wav(ROOT / 'Audio/stems_wet/track_Percussion_tines.wav')
pw = perc_wet.mean(axis=1)
click_win = int(0.020 * SR)
body_win = int(0.150 * SR)
click_c, body_c = [], []
for (st, note, vel) in drum_onsets:
    i0 = int(st * SR)
    a = pw[i0:i0 + click_win]
    b = pw[i0 + click_win:i0 + click_win + body_win]
    if len(a) > 256 and float(np.abs(a).max()) > 0.01:
        click_c.append(centroid(a))
    if len(b) > 256 and float(np.abs(b).max()) > 0.01:
        body_c.append(centroid(b))
print('percussion centroid: click(0-20ms) median %.0f Hz   '
      'tine body(20-170ms) median %.0f Hz' % (
          float(np.median(click_c)), float(np.median(body_c))))
del perc_wet, pw

# 3. band balance dry vs wet
def bands(x):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    fr = np.fft.rfftfreq(len(x), 1.0 / SR)
    edges = [20, 60, 120, 500, 2000, 8000, 20000]
    tot = float(np.sum(spec))
    return [round(100 * float(np.sum(spec[np.searchsorted(fr, a):np.searchsorted(fr, b)])) / tot, 2)
            for a, b in zip(edges[:-1], edges[1:])]


dry = load_wav(ROOT / 'dry_full_mix.wav').mean(axis=1)
print('bands dry (20-60,60-120,120-500,500-2k,2-8k,8k+):', bands(dry))
print('bands wet (20-60,60-120,120-500,500-2k,2-8k,8k+):', bands(mono))
del dry

# 4. strict pitch re-check from the delivered wet stems
def fft_dom(win, lo=50.0, hi=1000.0):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    fr = np.fft.rfftfreq(len(win), 1.0 / SR)
    a, b = np.searchsorted(fr, lo), np.searchsorted(fr, hi)
    return float(fr[np.argmax(spec[a:b]) + a])


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


STEM_MAP = {1: 'track_Resonator_Guitar_lead.wav',
            2: 'track_Acoustic_Slide_harmony.wav',
            3: 'track_Thumb_Bass_sub.wav'}
pitch_res = {}
for tr, fn in STEM_MAP.items():
    notes = parse(tr)
    stem = load_wav(ROOT / 'Audio/stems_wet' / fn).mean(axis=1)
    ons = np.array([n[0] for n in notes])
    ok = amb = 0
    for (st, dur, note, vel) in notes:
        wl = min(max(dur, 0.05), 0.15)
        i0 = int(st * SR)
        win = stem[i0:i0 + int(wl * SR)]
        if len(win) < 1024 or float(np.abs(win).max()) < 0.004:
            continue
        if np.any((ons > st + 1e-6) & (ons < st + wl)):
            amb += 1
            continue
        dom = fft_dom(win)
        f0 = midi_freq(note)
        ok += int(any(abs(dom - f0 * h) / (f0 * h) < 0.02 for h in (1, 2, 3, 4)))
    pitch_res[fn] = {'strict_ok': ok, 'strict_slots': ok + amb,
                     'ambiguous': amb,
                     'rate': round(ok / max(ok + amb, 1), 4)}
    print('%-40s strict %d/%d (%.1f%%), ambiguous %d' % (
        fn, ok, ok + amb, 100 * ok / max(ok + amb, 1), amb))
    del stem

out = {'duration_s': round(len(mono) / SR, 3),
       'peak': round(float(np.abs(mono).max()), 4),
       'rms': round(float(np.sqrt(np.mean(mono ** 2))), 4),
       'percussion_onsets': len(drum_onsets),
       'grid_peak_hits_within_40ms': hits,
       'grid_hit_rate': round(grid_rate, 4),
       'grid_misses_s': misses,
       'perc_centroid_click_hz': round(float(np.median(click_c)), 1),
       'perc_centroid_body_hz': round(float(np.median(body_c)), 1),
       'bands_wet': bands(mono),
       'pitch_strict': pitch_res}
(ROOT / 'Analysis' / 'verify_independent.json').write_text(
    json.dumps(out, indent=2))
print('->', ROOT / 'Analysis' / 'verify_independent.json')
