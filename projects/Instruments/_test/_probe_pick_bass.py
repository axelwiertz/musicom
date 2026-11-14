# -*- coding: utf-8 -*-
"""Probe GM34 Electric Bass (pick) in FluidR3: preset name, pitch sweep,
attack/decay, brightness vs GM33 (finger)."""
import os
import struct
import subprocess
import tempfile
import wave

import numpy as np
import mido
from sound.render.fluidsynth import discover_soundfont

SF2 = discover_soundfont()
FS = os.environ.get("MUSICOM_FLUIDSYNTH", "/opt/data/micromamba/envs/musicom/bin/fluidsynth")
print("SF2:", SF2)

# ---- preset names -------------------------------------------------------
data = open(SF2, "rb").read()
phdr = data.find(b"phdr")
phdr_size = struct.unpack("<I", data[phdr + 4:phdr + 8])[0]
presets = {}
for i in range(phdr_size // 38):
    off = phdr + 8 + i * 38
    name = data[off:off + 20].split(b"\x00")[0].decode("latin1")
    pn, bk = struct.unpack("<HH", data[off + 20:off + 24])
    presets[(bk, pn)] = name
for p in (32, 33, 34, 35, 36, 37):
    print(f"preset {p}: {presets.get((0, p), 'MISSING')!r}")


def midi_one(pitch, program, vel=90, dur=960, path=None):
    m = mido.MidiFile()
    m.ticks_per_beat = 480
    t0 = mido.MidiTrack(); m.tracks.append(t0)
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    t0.append(mido.MetaMessage("end_of_track", time=2 * dur))
    t1 = mido.MidiTrack(); m.tracks.append(t1)
    t1.append(mido.Message("program_change", program=program, channel=0, time=0))
    t1.append(mido.Message("note_on", note=pitch, velocity=vel, channel=0, time=0))
    t1.append(mido.Message("note_off", note=pitch, velocity=0, channel=0, time=dur))
    t1.append(mido.MetaMessage("end_of_track", time=dur))
    m.save(path)


def render(pitch, program, vel=90, dur=960):
    fd, mid = tempfile.mkstemp(suffix=".mid"); os.close(fd)
    wav = mid.replace(".mid", ".wav")
    midi_one(pitch, program, vel, dur, mid)
    r = subprocess.run([FS, "-ni", "-g", "1.2", "-F", wav, SF2, mid],
                       capture_output=True)
    assert r.returncode == 0, r.stderr[-400:]
    w = wave.open(wav, "rb"); sr = w.getframerate()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    w.close(); os.unlink(mid); os.unlink(wav)
    return sr, d.astype(np.float32) / 32768.0


def rms(x):
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0


def centroid(x, sr):
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / sr)
    return float((s * f).sum() / max(s.sum(), 1e-9))


print("\n=== pitch sweep preset 34 (vel 90) ===")
for p in range(21, 109, 3):
    sr, a = render(p, 34, 90, dur=480)
    seg = a[: int(0.4 * sr)]
    print(f"{p:3d} rms={rms(seg)*1000:8.1f} peak={np.max(np.abs(a)):.3f}")

print("\n=== finger(33) vs pick(34) tone @ E2=40, A2=45, D3=50 ===")
for p in (40, 45, 50):
    sr, a33 = render(p, 33, 90, dur=960)
    sr, a34 = render(p, 34, 90, dur=960)
    n = int(0.5 * sr)
    c33, c34 = centroid(a33[:n], sr), centroid(a34[:n], sr)
    en33 = rms(a33[: int(0.05 * sr)]); en34 = rms(a34[: int(0.05 * sr)])
    tail33 = rms(a33[int(0.6 * sr):int(1.2 * sr)]) / max(np.max(np.abs(a33)), 1e-9)
    tail34 = rms(a34[int(0.6 * sr):int(1.2 * sr)]) / max(np.max(np.abs(a34)), 1e-9)
    print(f"note {p}: centroid finger={c33:6.0f} Hz pick={c34:6.0f} Hz "
          f"(+{100*(c34-c33)/c33:4.0f}%) attack rms f={en33:.4f} p={en34:.4f} "
          f"tail f={tail33:.4f} p={tail34:.4f}")

print("\n=== attack window (pick, note 40) 0-5 ms vs 0-50 ms ===")
sr, a = render(40, 34, 90, dur=960)
for ms in (5, 10, 20, 50):
    print(f"  0-{ms}ms rms={rms(a[: int(ms/1000*sr)]):.4f}")

print("\n=== velocity response note 40 (vel 30..120) ===")
for v in (30, 50, 70, 90, 110, 120):
    sr, a = render(40, 34, v, dur=480)
    print(f"  vel {v}: rms={rms(a[:int(0.3*sr)])*1000:8.2f} peak={np.max(np.abs(a)):.3f}")
