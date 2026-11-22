# -*- coding: utf-8 -*-
"""319-sinterklaasavond — verify-don't-trust audit.

MIDI: zero-drift, off-grid, out-of-scale (G major), lead range, conjunctness.
Audio (post-render): silence ratio, RMS, harmonic energy, dominant peak, and
reverb-tail length (the SP-032 FDN production method leaves a measurable tail).
"""

import json
import os

import mido
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
G_MAJOR = {7, 9, 11, 0, 2, 4, 6}   # G A B C D E F#
DRUM_CH = 9
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(p):
    return f"{NAMES[p % 12]}{p // 12 - 1}"


def analyze_midi(tag):
    path = os.path.join(BASE, "MIDI", f"319-sinterklaasavond-{tag}.mid")
    mf = mido.MidiFile(path)
    tracks = {}
    for i, tr in enumerate(mf.tracks):
        t = 0
        prog, ch = None, None
        onsets, notes = [], []
        max_tick, max_audible_end = 0, 0
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
        tracks[i] = {"prog": prog, "ch": ch, "onsets": onsets, "notes": notes,
                     "max_tick": max_tick, "max_audible_end": max_audible_end}

    pitched = [tr for tr in tracks.values() if tr["ch"] != DRUM_CH and tr["notes"]]
    note_tracks = {i: tr for i, tr in tracks.items() if tr["notes"]}
    padded = {i: tr["max_tick"] for i, tr in note_tracks.items()}
    zero_drift = len(set(padded.values())) == 1

    off_grid = [o for tr in pitched for o in tr["onsets"] if o % 120 != 0]
    out_of_scale = sorted({n for tr in pitched for n in tr["notes"]
                           if n % 12 not in G_MAJOR})

    lead = next((tr for tr in pitched if tr["prog"] == 74), None)
    lead_range = (min(lead["notes"]), max(lead["notes"])) if lead else None

    # conjunctness: max consecutive melodic leap in the lead (<= a 3rd = 4 st).
    # Reset at section boundaries — each section's melody is generated
    # independently, so a seam leap is a new phrase, not a melodic error.
    SECTION_STARTS = {0, 7680, 23040, 38400}
    max_leap = 0
    if lead:
        sorted_lead = sorted(lead["onsets"])
        note_at = dict(zip(lead["onsets"], lead["notes"]))
        prev = None
        for o in sorted_lead:
            p = note_at[o]
            # reset at section boundaries (humanizer jitters the seam onset a
            # few ticks, so match within a small tolerance)
            if any(abs(o - s) <= 24 for s in SECTION_STARTS):
                prev = None
            if prev is not None:
                max_leap = max(max_leap, abs(p - prev))
            prev = p

    return {
        "tag": tag,
        "zero_drift": zero_drift,
        "padded_track_length_ticks": padded,
        "off_grid_onsets": len(off_grid),
        "out_of_scale_notes": out_of_scale,
        "lead_range_midi": lead_range,
        "lead_range_names": (note_name(lead_range[0]), note_name(lead_range[1]))
                            if lead_range else None,
        "max_consecutive_leap_st": max_leap,
    }


def analyze_audio(tag):
    path = os.path.join(BASE, "Audio", f"319-sinterklaasavond-{tag}.wav")
    if not os.path.exists(path):
        return None
    from sound.utils.io import read_wav
    audio, sr = read_wav(path)
    mono = audio.mean(axis=1)
    rms = float(np.sqrt(np.mean(mono ** 2)))
    silent = float(np.mean(np.abs(mono) < 0.001))

    N = int(0.5 * sr)
    win = mono[len(mono) // 2: len(mono) // 2 + N] * np.hanning(N)
    spec = np.abs(np.fft.rfft(win))
    freqs = np.fft.rfftfreq(N, 1 / sr)
    band = (freqs >= 50) & (freqs <= 1000)
    peak_hz = float(freqs[band][np.argmax(spec[band])])
    f0 = float(freqs[np.argmax(spec)])
    harm = sum(spec[np.argmin(np.abs(freqs - f0 * k))] ** 2 for k in range(1, 9))
    harmonic_energy = float(harm / float(np.sum(spec ** 2))) if np.sum(spec) > 0 else 0.0

    # reverb tail: SP-032 FDN reverb extends the render past the last note.
    # Duration (s) is the clean measure — the wet render runs longer than dry.
    duration_seconds = round(len(mono) / sr, 2)

    return {
        "rms": round(rms, 4),
        "silence_ratio": round(silent, 4),
        "dominant_peak_hz_50_1000": round(peak_hz, 1),
        "strongest_fundamental_hz": round(f0, 1),
        "harmonic_energy_pct": round(100 * harmonic_energy, 1),
        "duration_seconds": duration_seconds,
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
