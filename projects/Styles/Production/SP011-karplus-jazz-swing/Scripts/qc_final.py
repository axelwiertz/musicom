# -*- coding: utf-8 -*-
"""Final render QC: per-second RMS, longest silent gap, classic harmonic energy."""
import json
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")
from sound.synthesis.karplus_strong import midi_to_freq

WAV = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Audio/SP011-jazz-swing-karplus-strong.wav")
SRC = Path("/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid")

with wave.open(str(WAV), "rb") as wf:
    sr = wf.getframerate()
    nch = wf.getnchannels()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
mono = raw.reshape(-1, nch).mean(axis=1)
dur = len(mono) / sr

# per-second RMS (final render, trimmed to 16.2s)
sec_rms = []
for s in range(int(dur)):
    seg = mono[s * sr:(s + 1) * sr]
    sec_rms.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
print(f"dur={dur:.2f}s")
print("per_sec_rms=" + json.dumps(sec_rms))
print("min_rms=", min(sec_rms), "at sec", sec_rms.index(min(sec_rms)))

# longest silent gap within music region (first 16s)
mask = np.abs(mono[: int(16.0 * sr)]) >= 0.001
gaps = []
run = 0
for v in mask:
    if not v:
        run += 1
    else:
        if run:
            gaps.append(run)
        run = 0
if run:
    gaps.append(run)
gaps.sort(reverse=True)
print("longest_silent_gaps_s=" + json.dumps([round(g / sr, 3) for g in gaps[:8]]))

# classic harmonic energy: sum of FFT mag in +-3% bins of h*f0min (h=1..8)
# vs full-spectrum sum, on music region
import mido
mid = mido.MidiFile(str(SRC))
tempo = 500000
for m in mid.tracks[0]:
    if m.type == "set_tempo":
        tempo = m.tempo
notes = []
for track in mid.tracks[1:]:
    abstick = 0
    active = {}
    for m in track:
        abstick += m.time
        if m.type == "note_on" and m.velocity > 0 and m.channel != 9:
            active[m.note] = abstick
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if m.note in active:
                notes.append(m.note)
f0min = midi_to_freq(min(notes))
seg = mono[: int(16.0 * sr)]
seg = seg * np.hanning(len(seg))
spec = np.abs(np.fft.rfft(seg))
ff = np.fft.rfftfreq(len(seg), 1 / sr)
full = float(np.sum(spec))
h_energy = 0.0
for h in range(1, 9):
    m = (ff >= f0min * h * 0.97) & (ff <= f0min * h * 1.03)
    if m.any():
        h_energy += float(np.sum(spec[m]))
print(f"f0min={f0min:.1f} Hz")
print(f"classic_harmonic_energy_pct={100*h_energy/full:.1f}% (h1-8 of {f0min:.0f}Hz vs full spectrum)")

res = {
    "dur_s": round(dur, 2),
    "per_sec_rms": sec_rms,
    "min_rms": min(sec_rms),
    "longest_silent_gaps_s": [round(g / sr, 3) for g in gaps[:8]],
    "classic_harmonic_energy_pct": round(100 * h_energy / full, 1),
}
Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing/Analysis/qc_final.json").write_text(json.dumps(res, indent=2))
print("QC DONE")
