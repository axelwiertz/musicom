# -*- coding: utf-8 -*-
"""Tonal-content check v2: energy at EXPECTED MIDI-note frequencies.

READING ONLY (analysis). For each 0.5 s window the set of MIDI notes sounding
in that window (from phase-2 MIDI) is turned into frequencies; the fraction of
40-4000 Hz band energy that lands within +-1.5% of those frequencies is the
"note-energy ratio". A correctly rendered tonal piece scores high; broadband
noise scores low. Phase-1 (single raw trumpet voice) is used as a control.
"""
import json
import os
import wave

import numpy as np

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401

PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")


def midi_to_freq(n):
    return 440.0 * 2.0 ** ((n - 69) / 12.0)


def note_timeline(path):
    """[(start_s, end_s, midi_pitch)] from a MIDI file."""
    mid = mido.MidiFile(path)
    tpb = mid.ticks_per_beat
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo":
            tempo = msg.tempo
            break
    tps = 1e6 * tempo / tpb / 1e6 / 1.0       # seconds per tick
    seconds_per_tick = (tempo / tpb) / 1_000_000.0
    out = []
    for i, track in enumerate(mid.tracks):
        if i == 0:
            continue
        t, active = 0, {}
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = t
            elif msg.type == "note_off" or (msg.type == "note_on"
                                            and msg.velocity == 0):
                if msg.note in active:
                    st = active.pop(msg.note)
                    out.append((st * seconds_per_tick,
                                t * seconds_per_tick, msg.note))
    return out


def read_wav(path):
    with wave.open(path, "rb") as wf:
        ch, sw, sr = wf.getnchannels(), wf.getsampwidth(), wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    return x.reshape(-1, ch).mean(axis=1) / 32768.0, sr


def note_energy_ratio(wav, sr, tl, win_s=0.5):
    win = int(win_s * sr)
    ratios, covered = [], 0
    for k in range(0, len(wav) - win, win):
        t0, t1 = k / sr, (k + win) / sr
        seg = wav[k:k + win]
        if np.sqrt(np.mean(seg ** 2)) < 0.005:
            continue
        want = [midi_to_freq(p) for (s, e, p) in tl
                if e > t0 and s < t1 and p > 0]
        want = [f for f in want if 40 <= f <= 2000]
        if not want:
            continue
        covered += 1
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 40) & (freqs <= 4000)
        tot = float(np.sum(spec[band] ** 2))
        mask = np.zeros(len(freqs), dtype=bool)
        for f in want:
            for fm in (f, f * 2, f * 3):
                if fm < 4000:
                    mask |= np.abs(freqs - fm) <= max(2.0, 0.015 * fm)
        acc = float(np.sum(spec[mask] ** 2))
        ratios.append(acc / tot if tot > 0 else 0.0)
    return float(np.mean(ratios)), covered


res = {}
for label, midi, wavname in (
        ("phase2", os.path.join(PROJ, "MIDI", "092-disco-schillinger.mid"),
         "092-disco-schillinger.wav"),
        ("phase1", os.path.join(PROJ, "MIDI",
                                "092-disco-schillinger-phase1.mid"),
         "092-disco-schillinger-phase1.wav")):
    wav, sr = read_wav(os.path.join(PROJ, "Audio", wavname))
    tl = note_timeline(midi)
    r, cov = note_energy_ratio(wav, sr, tl)
    res[label] = {"note_energy_ratio": round(r, 4), "windows": cov,
                  "notes_in_midi": len(tl)}
    print("%s: note-energy ratio %.3f over %d windows (%d MIDI notes)"
          % (label, r, cov, len(tl)))
    print("   verdict:", "PASS tonal" if r > 0.30 else "SUSPECT")

with open(os.path.join(PROJ, "Analysis", "tonal_check.json"), "w") as f:
    json.dump(res, f, indent=2)
