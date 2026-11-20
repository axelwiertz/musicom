# -*- coding: utf-8 -*-
"""Probe GM76 Blown Bottle — FluidR3 patch behaviour.

Measures: pitch sweep RMS (24..108), pitch tracking (dominant partial vs
expected f0), attack time, spectral centroid, velocity response.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, "/opt/data/projects/Instruments")
sys.path.insert(0, "/opt/data/repos/musicom")

import numpy as np
import wave
from numpy.fft import rfft

from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
print(f"SF2: {SF2}")

BAR = 480 * 4
NOTE_LEN = 480 * 3   # 1.5 s at 120 bpm (3 beats)
GAP = 480            # 0.5 s silence between notes

notes = list(range(24, 109, 6))  # 24,30,...,108
import mido
mid = mido.MidiFile(ticks_per_beat=480)
tr = mido.MidiTrack()
tr.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
mid.tracks.append(tr)
tr = mido.MidiTrack()
prev = 0
abs_t = 0
tr.append(mido.Message("program_change", program=76, time=0))
for n in notes:
    tr.append(mido.Message("note_on", note=n, velocity=100, time=abs_t - prev))
    prev = abs_t
    abs_t += NOTE_LEN
    tr.append(mido.Message("note_off", note=n, velocity=0, time=NOTE_LEN))
    prev = abs_t
    abs_t += GAP
mid.tracks.append(tr)

mid_path = "/opt/data/projects/Instruments/_test/_probe_blown_bottle/sweep.mid"
os.makedirs(os.path.dirname(mid_path), exist_ok=True)
mid.save(mid_path)
wav_path = mid_path.replace(".mid", ".wav")
r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav_path, SF2, mid_path],
                   capture_output=True)
if r.returncode != 0:
    print(r.stderr.decode()[-800:])
    sys.exit(1)

w = wave.open(wav_path, "rb")
sr = w.getframerate()
n = w.getnframes()
data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
w.close()
print(f"render: {wav_path} sr={sr} frames={n} dur={n / sr:.2f}s")

# per-note segment analysis (tempo 120 bpm: 480 ticks = 0.5 s)
seg_len = int(1.5 * sr)   # NOTE_LEN = 1440 ticks = 1.5 s
step = int(2.0 * sr)      # note + GAP = 2.0 s per slot
print(f"\n{'note':>4} {'exp_f0':>7} {'rms':>7} {'peak_freq':>9} {'centroid':>8} {'attack_ms':>9}")
results = {}
for i, n in enumerate(notes):
    s0 = i * step
    seg = data[s0:s0 + seg_len]
    rms = float(np.sqrt(np.mean(seg ** 2)))
    exp_f0 = 440.0 * 2 ** ((n - 69) / 12)
    spec = np.abs(rfft(seg[: int(0.5 * sr)]))
    freqs = np.fft.rfftfreq(int(0.5 * sr), 1 / sr)
    # band-limited peak search ±10% around f0
    lo, hi = exp_f0 * 0.9, exp_f0 * 1.1
    band = (freqs >= lo) & (freqs <= hi)
    pk = float(freqs[band][np.argmax(spec[band])]) if band.any() else 0.0
    # global peak
    gpk = float(freqs[np.argmax(spec)])
    # spectral centroid (50-16k)
    aud = (freqs >= 50) & (freqs < 16000)
    cent = float(np.sum(freqs[aud] * spec[aud]) / max(np.sum(spec[aud]), 1e-9))
    # attack: time to reach 80% of peak in first 300 ms
    head = seg[: int(0.3 * sr)]
    env = np.abs(head)
    peak_v = env.max()
    thr = 0.8 * peak_v
    idx = np.argmax(env >= thr) if np.any(env >= thr) else len(env)
    attack_ms = idx / sr * 1000
    results[n] = dict(rms=rms, peak_freq=pk, global_peak=gpk, centroid=cent,
                      attack_ms=attack_ms, exp_f0=exp_f0)
    print(f"{n:>4} {exp_f0:7.1f} {rms:7.4f} {gpk:9.1f} {cent:8.0f} {attack_ms:9.1f}")

print("\nPitch tracking (band-limited peak vs expected f0):")
for n in notes:
    r = results[n]
    ratio = r["peak_freq"] / r["exp_f0"] if r["exp_f0"] else 0
    ok = "OK" if 0.9 <= ratio <= 1.1 else ("OCTAVE" if 1.8 <= ratio <= 2.2 else "MISMATCH")
    print(f"  note {n:>3}: expected {r['exp_f0']:7.1f} Hz, peak {r['peak_freq']:7.1f} Hz "
          f"({ratio:4.2f}x) {ok}")

# level flatness
rms_vals = [results[n]["rms"] for n in notes]
mx = max(rms_vals)
print(f"\nLevel flatness: min {min(rms_vals):.4f} max {mx:.4f} "
      f"span {20 * np.log10(max(rms_vals) / max(min(rms_vals), 1e-9)):.1f} dB")
quiet = [n for n in notes if results[n]["rms"] < mx * 0.02]
print(f"Silent/quiet notes (< 2% of max): {quiet if quiet else 'none'}")
