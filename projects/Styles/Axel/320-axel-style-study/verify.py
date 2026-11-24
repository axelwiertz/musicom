# -*- coding: utf-8 -*-
"""320-axel-style-study — verification (zero-drift, off-grid, out-of-key, spectral).

Reads the exported MIDI (mido = read-only) + the humanized WAV, reports real
numbers: track-length drift, off-grid onsets, out-of-key notes, FFT dominant
peaks, and harmonic-energy ratio.
"""

import json
import os

import numpy as np
import mido

from sound.utils.io import read_wav

BASE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(BASE, "MIDI")
AUDIO = os.path.join(BASE, "Audio")
ANALYSIS = os.path.join(BASE, "Analysis")
os.makedirs(ANALYSIS, exist_ok=True)

E_SCALE_PCS = {4, 6, 8, 9, 11, 1, 3}   # E F# G# A B C# D#


def note_track_maxes(mid):
    maxes = []
    for tr in mid.tracks:
        t = 0
        mx = 0
        has_note = False
        for m in tr:
            t += m.time
            if m.type in ("note_on", "note_off"):
                has_note = True
                mx = max(mx, t)
        if has_note:
            maxes.append(mx)
    return maxes


def onsets(mid):
    on = []
    for tr in mid.tracks:
        t = 0
        ch = 9  # default; overridden by note_on.channel
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                on.append((m.note, t, m.channel))
    return on


results = {}
for tag in ("perfect", "humanized"):
    mid = mido.MidiFile(os.path.join(MIDI, f"320-axel-style-study-{tag}.mid"))
    maxes = note_track_maxes(mid)
    on = onsets(mid)
    pitches = [n for n, _, c in on]
    pitched = [(n, t) for n, t, c in on if c != 9]   # exclude drums (unpitched)
    off_grid = [t for _, t in pitched if t % 120 != 0]
    out_key = [n for n, _ in pitched if n % 12 not in E_SCALE_PCS]
    results[tag] = {
        "note_track_max_tick": maxes,
        "zero_drift": len(set(maxes)) == 1,
        "n_notes": len(on),
        "n_pitched": len(pitched),
        "n_off_grid": len(off_grid),
        "n_out_of_key": len(out_key),
        "out_of_key_notes": sorted(set(out_key))[:10],
    }

# spectral (humanized render)
wav = os.path.join(AUDIO, "320-axel-style-study-humanized.wav")
audio, sr = read_wav(wav)
mono = audio.mean(axis=1).astype(np.float64)
spec = {}

# windowed dominant peak (tonal content check)
win = int(0.5 * sr)
dom = []
for i in range(0, len(mono) - win, win):
    seg = mono[i:i + win]
    if np.abs(seg).max() < 1e-3:
        dom.append(None)
        continue
    sp = np.abs(np.fft.rfft(seg * np.hanning(win)))
    freqs = np.fft.rfftfreq(win, 1 / sr)
    band = (freqs >= 60) & (freqs <= 1200)
    f = freqs[band][np.argmax(sp[band])]
    dom.append(round(float(f), 1))
spec["dominant_peak_hz_per_0.5s"] = dom

# harmonic energy of first 8 harmonics of the median dominant fundamental
full = np.abs(np.fft.rfft(mono)) ** 2
freqs_full = np.fft.rfftfreq(len(mono), 1 / sr)
valid = [f for f in dom if f]
if valid:
    f0 = float(np.median(valid))
    total = float(np.sum(full))
    harm = 0.0
    for h in range(1, 9):
        lo = f0 * h * 0.97
        hi = f0 * h * 1.03
        b = (freqs_full >= lo) & (freqs_full <= hi)
        harm += float(np.sum(full[b]))
    spec["median_dominant_hz"] = round(f0, 1)
    spec["harmonic_energy_ratio_first8"] = round(harm / total, 3) if total > 0 else None
    spec["median_dominant_midi"] = round(69 + 12 * np.log2(f0 / 440.0), 1)

out = {"midi": results, "spectral": spec}
with open(os.path.join(ANALYSIS, "verification.json"), "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
