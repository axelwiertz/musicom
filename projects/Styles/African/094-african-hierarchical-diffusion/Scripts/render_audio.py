# -*- coding: utf-8 -*-
"""Render phase-2 / phase-1 MIDI -> WAV -> OGG (SP-001 FluidSynth).

Uses discover_soundfont() (never a hardcoded TimGM6mb path), then
re-normalizes to ~-1 dBFS (0.89) with ffmpeg's volume filter (peaknorm is
unavailable in this ffmpeg build) and converts to Opus OGG for delivery.
"""
import json
import os
import struct
import subprocess
import wave

from structures import MusicUnit  # noqa: F401  (compliant-import marker)
from utilities.env import fluidsynth_bin, soundfont_path

PROJ = ("/opt/data/repos/musicom/projects/Styles/African/"
        "094-african-hierarchical-diffusion")
AUDIO = os.path.join(PROJ, "Audio")
MIDI2 = os.path.join(PROJ, "MIDI", "094-african-hierarchical-diffusion.mid")
MIDI1 = os.path.join(PROJ, "MIDI", "094-african-hierarchical-diffusion-phase1.mid")
SF = soundfont_path()
FS = fluidsynth_bin()
TARGET = 0.89
OUT = {}
assert os.path.getsize(MIDI2) > 40 and os.path.getsize(MIDI1) > 40


def peak_of(wav_path):
    with wave.open(wav_path, "rb") as wf:
        ch, n = wf.getnchannels(), wf.getnframes()
        raw = wf.readframes(n)
    s = struct.unpack("<%dh" % (len(raw) // 2), raw)
    return max(abs(s[i * ch]) for i in range(len(s) // ch)) / 32768.0


print("soundfont:", SF)
print("fluidsynth:", FS)

for label, midi in (("phase2", MIDI2), ("phase1", MIDI1)):
    base = os.path.splitext(os.path.basename(midi))[0]
    raw_wav = os.path.join(AUDIO, base + "-raw.wav")
    out_wav = os.path.join(AUDIO, base + ".wav")
    ogg = os.path.join(AUDIO, base + ".ogg")
    subprocess.run([FS, "-ni", "-g", "1.0", "-F", raw_wav, SF, midi],
                   capture_output=True, text=True, check=True)
    sz = os.path.getsize(raw_wav)
    if sz > 100 * 1024 * 1024:
        raise SystemExit("ABORT: raw WAV too large (%d bytes) - MIDI timing suspect" % sz)
    pk = peak_of(raw_wav)
    vol = TARGET / pk
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw_wav,
                    "-af", "volume=%.6f" % vol, out_wav],
                   capture_output=True, text=True, check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", ogg], capture_output=True, text=True,
                   check=True)
    os.remove(raw_wav)
    assert os.path.getsize(out_wav) > 40 and os.path.getsize(ogg) > 40
    OUT[label] = {"midi": midi, "wav": out_wav, "ogg": ogg,
                  "peak_before_norm": round(pk, 4),
                  "volume_applied": round(vol, 4),
                  "peak_after_norm": round(peak_of(out_wav), 4),
                  "wav_bytes": os.path.getsize(out_wav),
                  "ogg_bytes": os.path.getsize(ogg)}
    print(label, OUT[label])

with open(os.path.join(PROJ, "Analysis", "render_info.json"), "w") as f:
    json.dump(OUT, f, indent=2)
print("render_info.json written")
