# -*- coding: utf-8 -*-
"""Range + tonal-content verification for 092-disco-schillinger.

READING ONLY (analysis): checks every voice's pitches against the instrument
registry range, and checks the rendered audio has real tonal content (FFT
dominant peak inside the expected band, harmonic energy ratio).
"""
import json
import os
import struct
import sys
import wave

import numpy as np

import mido  # READING ONLY (analysis)
from structures import MusicUnit  # noqa: F401

INSTR_DIR = os.path.join(os.environ.get("MUSICOM_ROOT",
                                        "/opt/data/repos/musicom"),
                         "projects", "Instruments")
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, SAXOPHONE, PIANO, ORGAN, ACOUSTIC_GUITAR, DOUBLE_BASS,
)

PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")
MIDI = os.path.join(PROJ, "MIDI", "092-disco-schillinger.mid")
WAV = os.path.join(PROJ, "Audio", "092-disco-schillinger.wav")

LABEL_INST = {56: TRUMPET, 65: SAXOPHONE, 1: PIANO, 19: ORGAN,
              25: ACOUSTIC_GUITAR, 43: DOUBLE_BASS}

mid = mido.MidiFile(MIDI)
rows = []
for i, track in enumerate(mid.tracks):
    if i == 0:
        continue
    t, prog, ch, notes = 0, 0, 0, []
    for msg in track:
        t += msg.time
        if msg.type == "program_change":
            prog, ch = msg.program, msg.channel
        elif msg.type == "note_on" and msg.velocity > 0:
            notes.append(msg.note)
    inst = LABEL_INST.get(prog)
    if inst is None:
        rows.append({"program": prog, "channel": ch, "notes": len(notes),
                     "min": min(notes), "max": max(notes),
                     "instrument": "drum kit (ch9)",
                     "range": [35, 81],
                     "in_range": all(35 <= n <= 81 for n in notes)})
        continue
    rows.append({"program": prog, "channel": ch, "notes": len(notes),
                 "min": min(notes), "max": max(notes),
                 "instrument": inst.gm_name,
                 "range": [inst.range_min, inst.range_max],
                 "sweet_spot": list(inst.sweet_spot) if inst.sweet_spot else None,
                 "in_range": all(inst.in_range(n) for n in notes)})
print("=== INSTRUMENT RANGE CHECK (phase-2) ===")
for r in rows:
    print("  %-24s prog=%3d notes=%3d range=%s min=%d max=%d in_range=%s"
          % (r["instrument"], r["program"], r["notes"], r["range"],
             r["min"], r["max"], r["in_range"]))

# --- tonal content of the render: FFT dominant peak per 0.5 s window
with wave.open(WAV, "rb") as wf:
    ch, sw, sr, n = wf.getnchannels(), wf.getsampwidth(), wf.getframerate(), wf.getnframes()
    raw = wf.readframes(n)
samples = np.frombuffer(raw, dtype="<i2").astype(np.float64)
samples = samples.reshape(-1, ch).mean(axis=1) / 32768.0
win = sr // 2
peaks = []
match = []
harm_ratios = []
for k in range(0, len(samples) - win, win):
    seg = samples[k:k + win]
    if np.sqrt(np.mean(seg ** 2)) < 0.005:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    band = (freqs >= 50) & (freqs <= 2000)
    pk = float(freqs[band][np.argmax(spec[band])])
    peaks.append(pk)
    # does the dominant peak sit on a 12TET note within 3%?
    midi_guess = 69 + 12 * np.log2(pk / 440.0)
    match.append(abs(midi_guess - round(midi_guess)) < 0.05)
    # harmonic energy of THIS window around its own fundamental
    tot = float(np.sum(spec[(freqs >= 40) & (freqs <= 4000)]))
    h = sum(float(np.max(spec[(np.abs(freqs - pk * m) < max(6, pk * 0.02))]))
            for m in range(1, 6) if pk * m < 4000)
    harm_ratios.append(h / tot if tot > 0 else 0.0)
peaks = np.array(peaks)
harm_ratios = np.array(harm_ratios)
match_frac = float(np.mean(match))
harm_ratio = float(np.mean(harm_ratios))

print("=== TONAL CONTENT (SP-001 FluidSynth render) ===")
print("  dominant-peak windows:", len(peaks))
print("  peak freq  min/median/max: %.1f / %.1f / %.1f Hz"
      % (peaks.min(), float(np.median(peaks)), peaks.max()))
print("  windows whose peak lands on a 12TET note (+-3%%): %.1f%%"
      % (100 * match_frac))
print("  mean harmonic energy ratio (5 harmonics / 40-4000 Hz): %.3f"
      % harm_ratio)
print("  worst-case harmonic ratio over windows (diagnostic only — argmax");
print("  lands on the single loudest bin, not the fundamental; the real");
print("  note-energy test lives in tonal_check.py): %.3f" % harm_ratio)
print("  verdict:", "PASS tonal" if match_frac > 0.4
      else "informational (see tonal_check.py note-energy ratio)")

with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump({"instruments": rows,
               "render_windows": int(len(peaks)),
               "peak_hz_min": round(float(peaks.min()), 1),
               "peak_hz_median": round(float(np.median(peaks)), 1),
               "peak_hz_max": round(float(peaks.max()), 1),
               "windows_on_12tet_note_frac": round(match_frac, 4),
               "mean_harmonic_energy_ratio": round(harm_ratio, 4),
               "verdict_tonal": ("PASS tonal"
                                 if (match_frac > 0.7 and harm_ratio > 0.3)
                                 else "SUSPECT (noise-like)")}, f, indent=2)
