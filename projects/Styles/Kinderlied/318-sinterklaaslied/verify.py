# -*- coding: utf-8 -*-
"""318-sinterklaaslied — verify-don't-trust audit (real numbers).

MIDI checks (always run):
  - zero-drift: every note track ends at the same absolute tick
  - off-grid audit: perfect MIDI onsets all 16th-aligned (0 off-grid);
    humanized has off-grid > 0 (the humanization is audible)
  - out-of-scale audit: pitched tracks (non-ch9) all in C major
  - melody register: recorder lead min/max (children-singable check)

Audio checks (run after render, if WAV present):
  - silence ratio + RMS (not digital silence)
  - harmonic energy % (tonal vs noise)
  - dominant spectral peak in 50-1000 Hz (should be a chord/bass fundamental)
"""

import json
import os
import sys

import mido
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
C_MAJOR = {0, 2, 4, 5, 7, 9, 11}
DRUM_CH = 9

# note name for readability
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(p):
    return f"{NAMES[p % 12]}{p // 12 - 1}"


def analyze_midi(tag):
    path = os.path.join(BASE, "MIDI", f"318-sinterklaaslied-{tag}.mid")
    mf = mido.MidiFile(path)
    tracks = {}   # track_index -> {"prog": int, "ch": int, "onsets": [], "max_end": int, "notes": []}
    for i, tr in enumerate(mf.tracks):
        t = 0
        prog, ch = None, None
        onsets, notes = [], []
        max_tick = 0
        max_audible_end = 0
        on = {}
        for m in tr:
            t += m.time
            max_tick = max(max_tick, t)
            if m.type == "program_change":
                prog, ch = m.program, m.channel
            elif m.type == "note_on" and m.velocity > 0:
                onsets.append(t)
                notes.append(m.note)
                on[m.note] = t
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                st = on.pop(m.note, None)
                if st is not None:
                    max_audible_end = max(max_audible_end, t)
        tracks[i] = {"prog": prog, "ch": ch, "onsets": onsets,
                     "notes": notes, "max_tick": max_tick,
                     "max_audible_end": max_audible_end}

    pitched = [tr for tr in tracks.values() if tr["ch"] != DRUM_CH and tr["notes"]]
    drum = [tr for tr in tracks.values() if tr["ch"] == DRUM_CH]

    note_tracks = {i: tr for i, tr in tracks.items() if tr["notes"]}
    padded_lengths = {i: tr["max_tick"] for i, tr in note_tracks.items()}
    zero_drift = len(set(padded_lengths.values())) == 1

    off_grid = [o for tr in pitched for o in tr["onsets"] if o % 120 != 0]
    out_of_scale = sorted({n for tr in pitched for n in tr["notes"]
                           if n % 12 not in C_MAJOR})

    # melody = the recorder track (prog 74)
    lead = next((tr for tr in pitched if tr["prog"] == 74), None)
    lead_range = (min(lead["notes"]), max(lead["notes"])) if lead else None

    return {
        "tag": tag,
        "zero_drift": zero_drift,
        "padded_track_length_ticks": padded_lengths,
        "last_audible_note_end_ticks": {i: tr["max_audible_end"]
                                         for i, tr in note_tracks.items()},
        "total_notes": sum(len(tr["notes"]) for tr in tracks.values()),
        "off_grid_onsets": len(off_grid),
        "out_of_scale_notes": out_of_scale,
        "lead_range_midi": lead_range,
        "lead_range_names": (note_name(lead_range[0]), note_name(lead_range[1]))
                            if lead_range else None,
    }


def analyze_audio(tag):
    path = os.path.join(BASE, "Audio", f"318-sinterklaaslied-{tag}.wav")
    if not os.path.exists(path):
        return None
    from sound.utils.io import read_wav
    audio, sr = read_wav(path)
    mono = audio.mean(axis=1)
    rms = float(np.sqrt(np.mean(mono ** 2)))
    silent = float(np.mean(np.abs(mono) < 0.001))

    # FFT on a 0.5 s window near the middle (dense full-texture moment)
    N = int(0.5 * sr)
    win = mono[len(mono) // 2: len(mono) // 2 + N]
    win = win * np.hanning(N)
    spec = np.abs(np.fft.rfft(win))
    freqs = np.fft.rfftfreq(N, 1 / sr)
    band = (freqs >= 50) & (freqs <= 1000)
    peak_hz = float(freqs[band][np.argmax(spec[band])])

    # harmonic energy: fraction of energy in the first 8 harmonics of the
    # strongest low fundamental (tonal vs noise)
    f0 = float(freqs[np.argmax(spec)])
    harm = 0.0
    for k in range(1, 9):
        idx = np.argmin(np.abs(freqs - f0 * k))
        harm += spec[idx] ** 2
    total = float(np.sum(spec ** 2))
    harmonic_energy = float(harm / total) if total > 0 else 0.0

    return {
        "rms": round(rms, 4),
        "silence_ratio": round(silent, 4),
        "dominant_peak_hz_50_1000": round(peak_hz, 1),
        "strongest_fundamental_hz": round(f0, 1),
        "harmonic_energy_pct": round(100 * harmonic_energy, 1),
    }


def main():
    out = {}
    for tag in ("perfect", "humanized"):
        out[tag] = {"midi": analyze_midi(tag), "audio": analyze_audio(tag)}

    os.makedirs(os.path.join(BASE, "Analysis"), exist_ok=True)
    with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
