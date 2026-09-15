# -*- coding: utf-8 -*-
"""Render phase-2 / phase-1 MIDI -> WAV -> OGG (SP-001 FluidSynth)."""
import json
import os
import struct
import subprocess
import wave

from structures import MusicUnit  # noqa: F401  (compliant-import marker)

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
AUDIO = os.path.join(PROJ, "Audio")
MIDI2 = os.path.join(PROJ, "MIDI", "096-trap-skeleton-seoul.mid")
MIDI1 = os.path.join(PROJ, "MIDI", "096-trap-skeleton-seoul-phase1.mid")
SF = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"
FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

TARGET = 0.89
OUT = {}


def peak_of(wav_path):
    with wave.open(wav_path, "rb") as wf:
        ch, n = wf.getnchannels(), wf.getnframes()
        raw = wf.readframes(n)
    s = struct.unpack("<%dh" % (len(raw) // 2), raw)
    return max(abs(s[i * ch]) for i in range(len(s) // ch)) / 32768.0


for label, midi, gain in (("phase2", MIDI2, 1.0), ("phase1", MIDI1, 1.0)):
    base = os.path.splitext(os.path.basename(midi))[0]
    raw_wav = os.path.join(AUDIO, base + "-raw.wav")
    out_wav = os.path.join(AUDIO, base + ".wav")
    ogg = os.path.join(AUDIO, base + ".ogg")
    subprocess.run([FS, "-ni", "-g", str(gain), "-F", raw_wav, SF, midi],
                   capture_output=True, text=True, check=True)
    print(label, "raw bytes", os.path.getsize(raw_wav))
    assert os.path.getsize(raw_wav) < 100 * 1024 * 1024, "WAV too big, abort"
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
