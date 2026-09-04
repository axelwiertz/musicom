# -*- coding: utf-8 -*-
"""Deeper pitch verification: autocorrelation frames + failing window debug."""
import json
import sys
import wave
from pathlib import Path

import mido
import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.synthesis.karplus_strong import midi_to_freq

SRC = Path("/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid")
WAV = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Audio/SP011-jazz-swing-karplus-strong.wav")

with wave.open(str(WAV), "rb") as wf:
    sr = wf.getframerate()
    nch = wf.getnchannels()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
mono = raw.reshape(-1, nch).mean(axis=1)
dur = len(mono) / sr

mid = mido.MidiFile(str(SRC))
tempo = 500000
for m in mid.tracks[0]:
    if m.type == "set_tempo":
        tempo = m.tempo


def t2s(tick):
    return tick * tempo / mid.ticks_per_beat / 1_000_000


expected = []
for track in mid.tracks[1:]:
    abstick = 0
    active = {}
    for m in track:
        abstick += m.time
        if m.type == "note_on" and m.velocity > 0 and m.channel != 9:
            active[m.note] = abstick
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if m.note in active:
                expected.append((t2s(active.pop(m.note)), m.note))
expected.sort()

# ---- autocorrelation pitch per 0.5s frame ----
win = int(0.5 * sr)
hop = int(0.25 * sr)
frames = []
for w0 in range(0, len(mono) - win, hop):
    seg = mono[w0:w0 + win]
    seg = seg - seg.mean()
    energy = np.sum(seg ** 2)
    if energy < 1e-8:
        frames.append({"t": round(w0 / sr, 2), "f0": None, "conf": 0.0, "exp": None})
        continue
    ac = np.correlate(seg, seg, "full")[win - 1:]
    ac /= ac[0]
    lo, hi = int(sr / 1000), int(sr / 50)  # 50-1000 Hz
    region = ac[lo:hi]
    lag = lo + int(np.argmax(region))
    f0 = sr / lag
    conf = float(region.max())
    t0 = w0 / sr
    near = [n for s, n in expected if abs(s - t0) < 0.6]
    exp = sorted(near)
    frames.append({"t": round(t0, 2), "f0": round(f0, 1), "conf": round(conf, 3), "exp": exp})

detected = [f for f in frames if f["f0"] and f["conf"] > 0.35]
print(f"frames={len(frames)} detected_pitch={len(detected)} ({100*len(detected)/max(1,len(frames)):.0f}%)")
# frame f0 vs nearest expected midi note
match = 0
for f in detected:
    if f["exp"]:
        expf = [midi_to_freq(n) for n in f["exp"]]
        best = min(expf, key=lambda x: abs(x - f["f0"]))
        if abs(best - f["f0"]) / best < 0.08:
            match += 1
print(f"detected_matching_expected={match} ({100*match/max(1,len(detected)):.0f}%)")

# ---- debug failing FFT windows ----
win2 = int(0.5 * sr)
freqs = np.fft.rfftfreq(win2, 1 / sr)
debug = []
for w0 in range(0, len(mono) - win2, hop):
    t0 = w0 / sr
    if t0 > 15.0:
        break
    seg = mono[w0:w0 + win2] * np.hanning(win2)
    spec = np.abs(np.fft.rfft(seg))
    mask = (freqs >= 50) & (freqs <= 1000)
    f_peak = freqs[mask][np.argmax(spec[mask])]
    near = [n for s, n in expected if abs(s - t0) < 0.6]
    expf = [midi_to_freq(n) for n in near]
    best = min(expf, key=lambda x: abs(x - f_peak)) if expf else None
    ok = best is not None and abs(f_peak - best) / best < 0.06
    if not ok:
        # top 3 peaks
        idx = np.argsort(spec[mask])[::-1][:3]
        peaks = [round(freqs[mask][i], 1) for i in idx]
        debug.append({"t": round(t0, 2), "f_peak": round(f_peak, 1),
                      "exp_notes": near, "top3": peaks})

print("failing windows sample:")
for d in debug[:12]:
    print(json.dumps(d))

# ---- harmonic energy, normalized properly (fraction of band energy in harmonics) ----
# use band 50-2000 Hz as reference; harmonics of lowest f0 (98 Hz): 98..784
band_mask = (freqs_full if False else freqs)  # placeholder
# recompute on full segment
t0s, t1s = int(0.2 * dur) * sr, int(0.8 * dur) * sr
seg = mono[t0s:t1s]
seg = seg * np.hanning(len(seg))
spec = np.abs(np.fft.rfft(seg))
ff = np.fft.rfftfreq(len(seg), 1 / sr)
f0min = midi_to_freq(min(n for _, n in expected))
band = (ff >= 50) & (ff <= 2000)
band_energy = float(np.sum(spec[band]))
h_energy = 0.0
for h in range(1, 9):
    m = (ff >= f0min * h * 0.97) & (ff <= f0min * h * 1.03)
    if m.any():
        h_energy += float(np.sum(spec[m]))
print(f"harmonic_energy_vs_band = {100*h_energy/max(band_energy,1e-12):.1f}% (band 50-2000 Hz)")
print(f"band_energy={band_energy:.1f} h_energy={h_energy:.1f}")

# music-region silence (0-16s) vs tail
mus = mono[:int(16.0 * sr)]
tail = mono[int(16.0 * sr):]
for name, segm in (("music(0-16s)", mus), ("tail(16-19s)", tail)):
    sil = np.sum(np.abs(segm) < 0.001) / len(segm)
    print(f"silence {name}: {100*sil:.1f}%")

res = {
    "frames": len(frames),
    "detected_pitch": len(detected),
    "detected_pct": round(100 * len(detected) / max(1, len(frames)), 1),
    "detected_matching_expected": match,
    "detected_match_pct": round(100 * match / max(1, len(detected)), 1),
    "harmonic_energy_vs_band_50_2000_pct": round(100 * h_energy / max(band_energy, 1e-12), 1),
    "silence_music_pct": round(100 * np.sum(np.abs(mus) < 0.001) / len(mus), 1),
    "silence_tail_pct": round(100 * np.sum(np.abs(tail) < 0.001) / len(tail), 1),
}
Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/verify_pitch2.json").write_text(json.dumps(res, indent=2))
print("DEEP VERIFY DONE")
