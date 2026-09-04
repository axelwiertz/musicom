# -*- coding: utf-8 -*-
"""Pitch verification + silence/RMS profile for SP-011 jazz-swing render.

Per skill contract: FFT dominant peak per 0.5s window in 50-1000 Hz, compare
against expected MIDI note frequencies; harmonic energy in 8 harmonics of the
lowest fundamental >= 30% (noise = single digits); silence ratio + per-second
RMS map (mid-track gaps > 30% silence = suspect).
"""
import json
import sys
from pathlib import Path

import mido
import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.synthesis.karplus_strong import midi_to_freq

SRC = Path("/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid")
WAV = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Audio/SP011-jazz-swing-karplus-strong.wav")

# --- load wav (stereo -> mono) ---
import wave
with wave.open(str(WAV), "rb") as wf:
    sr = wf.getframerate()
    nch = wf.getnchannels()
    n = wf.getnframes()
    raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32) / 32767.0
mono = raw.reshape(-1, nch).mean(axis=1) if nch == 2 else raw
dur = len(mono) / sr
print(f"wav: {sr} Hz, {nch} ch, {dur:.2f}s, peak={np.max(np.abs(mono)):.3f}")

# --- silence ratio + per-second RMS ---
silent = np.sum(np.abs(mono) < 0.001) / len(mono)
print(f"silence_ratio={silent*100:.1f}%")
sec_rms = []
for s in range(int(dur)):
    seg = mono[s * sr:(s + 1) * sr]
    sec_rms.append(float(np.sqrt(np.mean(seg ** 2))))
print("per_sec_rms=" + json.dumps([round(v, 4) for v in sec_rms]))

# --- expected pitch classes from source MIDI (comp+lead+bass, skip drums) ---
mid = mido.MidiFile(str(SRC))
tick_map = {}
at = 0
tempo = 500000
for m in mid.tracks[0]:
    at += m.time
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
print(f"expected_notes={len(expected)}")

# --- FFT per 0.5s window: dominant peak 50-1000 Hz ---
win = int(0.5 * sr)
hop = int(0.25 * sr)
freqs = np.fft.rfftfreq(win, 1 / sr)
found = []
for w0 in range(0, len(mono) - win, hop):
    seg = mono[w0:w0 + win] * np.hanning(win)
    spec = np.abs(np.fft.rfft(seg))
    mask = (freqs >= 50) & (freqs <= 1000)
    if mask.sum() == 0:
        continue
    f_peak = freqs[mask][np.argmax(spec[mask])]
    t0 = w0 / sr
    # nearest expected note at that time
    near = [n for s, n in expected if abs(s - t0) < 0.6]
    exp_f = [midi_to_freq(n) for n in near] if near else []
    match = min(exp_f, key=lambda f: abs(f - f_peak)) if exp_f else None
    ok = match is not None and abs(f_peak - match) / match < 0.06
    found.append({"t": round(t0, 2), "f_peak": round(f_peak, 1),
                  "exp": round(match, 1) if match else None, "ok": bool(ok)})

n_ok = sum(1 for f in found if f["ok"])
print(f"windows={len(found)} matched={n_ok} ({100*n_ok/max(1,len(found)):.0f}%)")

# --- harmonic energy: 8 harmonics of lowest expected fundamental ---
f0_min = midi_to_freq(min(n for _, n in expected))
t0 = int(dur * 0.2) * sr
t1 = int(dur * 0.8) * sr
seg = mono[t0:t1]
seg = seg * np.hanning(len(seg))
spec = np.abs(np.fft.rfft(seg))
freqs_full = np.fft.rfftfreq(len(seg), 1 / sr)
harms = []
for h in range(1, 9):
    m = (freqs_full >= f0_min * h * 0.97) & (freqs_full <= f0_min * h * 1.03)
    harms.append(float(spec[m].max()) if m.any() else 0.0)
total = float(np.sum(spec))
he = 100.0 * sum(harms) / max(total, 1e-12)
print(f"lowest_f0={f0_min:.1f} Hz, harmonic_energy_8h={he:.1f}%")
print(f"harmonics={[round(h,2) for h in harms]}")

res = {
    "silence_ratio_pct": round(silent * 100, 1),
    "per_sec_rms": sec_rms,
    "fft_windows": len(found),
    "fft_matched": n_ok,
    "fft_match_pct": round(100 * n_ok / max(1, len(found)), 1),
    "harmonic_energy_8h_pct": round(he, 1),
    "peak": float(np.max(np.abs(mono))),
}
Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/verify_pitch.json").write_text(json.dumps(res, indent=2))
print("VERIFY DONE")
