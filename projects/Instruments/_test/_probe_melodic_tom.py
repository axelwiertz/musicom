# -*- coding: utf-8 -*-
"""Probe FluidR3 GM117 Melodic Tom: audibility sweep, pitch tracking, decay.

Renders one MIDI with sequential notes (24..108), segments the WAV, and
measures per-note RMS + spectral peak. Also probes velocity response and
decay time for a single mid note.
"""
import os
import subprocess
import sys

sys.path.insert(0, "/opt/data/repos/musicom")
sys.path.insert(0, "/opt/data/projects/Instruments")

import mido  # noqa: E402
import numpy as np  # noqa: E402
import wave  # noqa: E402

from sound.render.fluidsynth import discover_soundfont  # noqa: E402

OUT = "/opt/data/projects/Instruments/_test/_probe_melodic_tom"
os.makedirs(OUT, exist_ok=True)
SF2 = discover_soundfont()
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
print("SF2:", SF2)

TPB = 480
NOTE_GAP = 480  # ticks between note starts
NOTE_LEN = 360  # ticks
BPM = 120
SPT = 60.0 / BPM / TPB  # seconds per tick


def make_sweep_midi(notes, path, vel=100):
    m = mido.MidiFile(ticks_per_beat=TPB)
    trk = mido.MidiTrack()
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.Message("program_change", program=117, channel=0, time=0))
    m.tracks.append(trk)
    t = 0
    for n in notes:
        trk.append(mido.Message("note_on", note=n, velocity=vel, channel=0, time=t))
        trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=NOTE_LEN))
        t = NOTE_GAP - NOTE_LEN
    m.save(path)


def render(midi, wav):
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, midi],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-500:])
    return os.path.getsize(wav)


def read_wav(path):
    w = wave.open(path, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    w.close()
    return data, sr


def rms(x):
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0


def spectral_peak(x, sr):
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    # limit to 50..8000 (avoid DC + ultrasonic)
    m = (freqs >= 50) & (freqs <= 8000)
    idx = int(np.argmax(spec[m]))
    return float(freqs[m][idx]), float(spec[m][idx])


# ---------------------------------------------------------------- sweep
notes = list(range(24, 109, 3))
midi_path = os.path.join(OUT, "sweep.mid")
wav_path = os.path.join(OUT, "sweep.wav")
make_sweep_midi(notes, midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
print(f"sweep rendered: {os.path.getsize(wav_path)} bytes, sr={sr}")

step_s = NOTE_GAP * SPT
win = int(0.20 * sr)  # 200 ms analysis window after onset
print(f"\n{'note':>4} {'expect Hz':>9} {'rms':>8} {'peak Hz':>8} {'ratio':>6}")
audible = []
for i, n in enumerate(notes):
    start = int(i * step_s * sr)
    seg = data[start:start + win]
    if len(seg) < sr // 20:
        break
    r = rms(seg)
    f0exp = 440.0 * 2.0 ** ((n - 69) / 12.0)
    pk, _ = spectral_peak(seg, sr)
    ratio = pk / f0exp if f0exp else 0
    flag = "" if r > 6e-5 else "  <-- silent"
    if r > 6e-5:
        audible.append(n)
    print(f"{n:>4} {f0exp:>9.1f} {r:>8.5f} {pk:>8.1f} {ratio:>6.2f}{flag}")
print(f"\naudible notes: {audible[0]}..{audible[-1]} ({len(audible)}/{len(notes)})"
      if audible else "\naudible notes: NONE")

# ---------------------------------------------------------------- pitch tracking
# detailed tracking on the audible span, every note
span = [n for n in range(audible[0], audible[-1] + 1)]
midi_path = os.path.join(OUT, "track.mid")
wav_path = os.path.join(OUT, "track.wav")
make_sweep_midi(span, midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
print(f"\npitch tracking ({len(span)} notes):")
print(f"{'note':>4} {'expect Hz':>9} {'peak Hz':>8} {'cents':>7}")
for i, n in enumerate(span):
    start = int(i * step_s * sr)
    seg = data[start:start + win]
    if len(seg) < sr // 20:
        break
    f0exp = 440.0 * 2.0 ** ((n - 69) / 12.0)
    pk, _ = spectral_peak(seg, sr)
    cents = 1200 * np.log2(pk / f0exp) if pk > 0 else 0
    print(f"{n:>4} {f0exp:>9.1f} {pk:>8.1f} {cents:>7.0f}")

# ---------------------------------------------------------------- decay (note 57, A3)
midi_path = os.path.join(OUT, "decay.mid")
wav_path = os.path.join(OUT, "decay.wav")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
trk.append(mido.Message("note_on", note=57, velocity=100, channel=0, time=0))
trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=TPB * 4))
m.save(midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
print("\ndecay (A3=57, 4 s tail):")
for lo, hi in [(0, 0.05), (0.05, 0.2), (0.2, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 3.5)]:
    seg = data[int(lo * sr):int(hi * sr)]
    print(f"  {lo:>4}-{hi:>4} s: rms={rms(seg):.6f} peak={float(np.max(np.abs(seg))):.5f}")

# ---------------------------------------------------------------- velocity response
midi_path = os.path.join(OUT, "vel.mid")
wav_path = os.path.join(OUT, "vel.wav")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
t = 0
for vel in [20, 40, 60, 80, 100, 120]:
    trk.append(mido.Message("note_on", note=57, velocity=vel, channel=0, time=t))
    trk.append(mido.Message("note_off", note=57, velocity=0, channel=0, time=NOTE_LEN))
    t = NOTE_GAP - NOTE_LEN
m.save(midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
print("\nvelocity response (A3):")
for i, vel in enumerate([20, 40, 60, 80, 100, 120]):
    start = int(i * step_s * sr)
    seg = data[start:start + win]
    pk = float(np.max(np.abs(seg)))
    print(f"  vel {vel:>3}: peak={pk:.4f} rms={rms(seg):.5f}")

# ---------------------------------------------------------------- buzz check on a melodic fill
midi_path = os.path.join(OUT, "fill.mid")
wav_path = os.path.join(OUT, "fill.wav")
m = mido.MidiFile(ticks_per_beat=TPB)
trk = mido.MidiTrack()
trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(104), time=0))
trk.append(mido.Message("program_change", program=117, channel=0, time=0))
m.tracks.append(trk)
fill = [57, 60, 62, 64, 62, 60, 57, 55, 57, 60, 62, 64, 65, 64, 62, 60]
t = 0
for n in fill:
    trk.append(mido.Message("note_on", note=n, velocity=96, channel=0, time=t))
    trk.append(mido.Message("note_off", note=n, velocity=0, channel=0, time=160))
    t = 240 - 160
m.save(midi_path)
render(midi_path, wav_path)
data, sr = read_wav(wav_path)
spec = np.abs(np.fft.rfft(data[: int(0.5 * sr)]))
freqs = np.fft.rfftfreq(len(data[: int(0.5 * sr)]), 1 / sr)
buzz = spec[(freqs >= 4000) & (freqs < 8000)].sum()
tot = spec[(freqs >= 50) & (freqs < 16000)].sum()
print(f"\nfill 4-8kHz buzz = {buzz / max(tot, 1e-9) * 100:.1f}%")
