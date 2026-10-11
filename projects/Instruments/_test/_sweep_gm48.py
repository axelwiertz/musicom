# -*- coding: utf-8 -*-
"""Empirical FluidR3 pitch sweep for GM48 String Ensemble 1.

Renders single held notes across 24-108 with FluidR3_GM.sf2 and measures
RMS. Reports audibility + gaps so the KB range is grounded, not guessed.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
FS = os.environ.get("MUSICOM_FLUIDSYNTH", "/opt/data/micromamba/envs/musicom/bin/fluidsynth")

NOTES = list(range(24, 109, 6))  # C1..C8 every 6 semitones


def render_note(note, dur_s=1.2):
    """One held note -> wav in temp, return RMS."""
    import mido
    mid = mido.MidiFile()
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(90)))
    tr.append(mido.Message("program_change", program=48, channel=0, time=0))
    tr.append(mido.Message("note_on", note=note, velocity=92, channel=0, time=0))
    ticks = int(dur_s * 480 * 2)  # 90bpm, 480tpb -> 0.5s/beat
    tr.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=ticks))
    fd, mid_path = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    mid.save(mid_path)
    wav_path = mid_path.replace(".mid", ".wav")
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav_path, SF2, mid_path],
                       capture_output=True)
    os.unlink(mid_path)
    if r.returncode != 0 or not os.path.exists(wav_path):
        return None
    w = wave.open(wav_path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    os.unlink(wav_path)
    seg = data[int(0.2 * sr):int(0.5 * sr)]  # steady state, skip attack
    return float(np.sqrt(np.mean(seg ** 2)))


print(f"SF2: {SF2}")
print("note  rms")
results = {}
for n in NOTES:
    rms = render_note(n)
    results[n] = rms
    bar = "#" * int((rms or 0) / 0.0005) if rms else "SILENT"
    print(f"{n:4d}  {rms if rms is None else f'{rms:.5f}':>10}  {bar}")

audible = [n for n, r in results.items() if r and r > 0.0005]
silent = [n for n, r in results.items() if not r or r <= 0.0005]
print(f"\naudible: {audible}")
print(f"silent/low: {silent}")