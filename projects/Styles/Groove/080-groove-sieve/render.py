# -*- coding: utf-8 -*-
"""080-groove-sieve: FluidSynth render + silence/RMS profile + phase-1 render."""
import os
import subprocess
import json

import numpy as np
import wave

PROJ = "/opt/data/projects/Styles/Groove/080-groove-sieve"
AUDIO_DIR = os.path.join(PROJ, "Audio")
SF2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/usr/bin/ffmpeg"

MIDIS = {
    "080-groove-sieve": os.path.join(PROJ, "MIDI/080-groove-sieve.mid"),
    "080-groove-sieve-phase1": os.path.join(PROJ, "MIDI/080-groove-sieve-phase1.mid"),
}

os.makedirs(AUDIO_DIR, exist_ok=True)


def wav_stats(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n = wf.getnframes()
        sr = wf.getframerate()
        data = np.frombuffer(wf.readframes(n), dtype=np.int16)
    mono = data.astype(np.float32) / 32768.0
    if wf.getnchannels() == 2:
        mono = (mono[0::2] + mono[1::2]) * 0.5
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    dur = len(mono) / sr
    rms_per_s = []
    for i in range(0, len(mono), sr):
        seg = mono[i:i + sr]
        if len(seg):
            rms_per_s.append(float(np.sqrt(np.mean(seg ** 2))))
    peak = float(np.max(np.abs(mono)))
    return {
        "duration_s": round(dur, 2),
        "silence_ratio": round(silent, 4),
        "peak": round(peak, 4),
        "rms_per_second": [round(r, 4) for r in rms_per_s],
    }


results = {}
for name, midi_path in MIDIS.items():
    wav = os.path.join(AUDIO_DIR, name + ".wav")
    ogg = os.path.join(AUDIO_DIR, name + ".ogg")
    if os.path.exists(wav):
        os.remove(wav)
    cmd = [FLUID, "-ni", "-g", "1.2", "-F", wav, SF2, midi_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(wav):
        print("FLUIDSYNTH FAIL", name, r.stderr[-500:])
        continue
    size_wav = os.path.getsize(wav)
    # safety: FluidSynth massive-WAV guard
    assert size_wav < 100 * 1024 * 1024, "WAV too big: %s" % size_wav
    # ogg via ffmpeg opus
    r2 = subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", wav,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg],
        capture_output=True, text=True, timeout=120)
    if r2.returncode != 0:
        print("FFMPEG FAIL", name, r2.stderr[-500:])
        continue
    stats = wav_stats(wav)
    stats["wav_bytes"] = size_wav
    stats["ogg_bytes"] = os.path.getsize(ogg)
    results[name] = stats
    print(name, "wav=%d ogg=%d" % (size_wav, os.path.getsize(ogg)),
          "silence=%.4f peak=%.4f dur=%.2fs" %
          (stats["silence_ratio"], stats["peak"], stats["duration_s"]))
    print("  rms/s:", stats["rms_per_second"])

with open(os.path.join(PROJ, "Analysis/render_stats.json"), "w") as f:
    json.dump(results, f, indent=2)
print("render_stats written")
