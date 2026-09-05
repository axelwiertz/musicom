#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Render phase-1 MIDI to WAV + OGG (contrast artifact) + write provenance
sidecars for all audio artifacts."""
import os
import json
import numpy as np
import wave

from workflows.musicom_workflow import produce
from workflows.provenance import write_provenance, AI_GENERATED, AI_ASSISTED
from sound.render.fluidsynth import discover_soundfont

PROJ = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira"
MIDI1 = os.path.join(PROJ, "MIDI", "086-son-markov-guajira-phase1.mid")
AUDIO = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO, exist_ok=True)

sf = discover_soundfont()
assert sf and os.path.exists(sf)
print("soundfont:", sf)

res = produce(MIDI1, method="SP-001", out_dir=AUDIO)
print("phase1 produced:", os.path.basename(res.wav_path), os.path.basename(res.ogg_path))

# provenance for phase-2 + phase-1 audio artifacts
write_provenance(
    os.path.join(AUDIO, "086-son-markov-guajira.wav"), "ai-assisted",
    generator="SP-001 FluidSynth render of phase-2 MIDI (Method 002 + rules)",
    sources=[os.path.join(PROJ, "MIDI", "086-son-markov-guajira.mid")],
    parameters={"method": "SP-001", "soundfont": sf})
write_provenance(
    os.path.join(AUDIO, "086-son-markov-guajira.ogg"), "ai-assisted",
    generator="ffmpeg libopus voip 48k from phase-2 WAV",
    sources=[os.path.join(AUDIO, "086-son-markov-guajira.wav")],
    parameters={"codec": "libopus", "application": "voip", "bitrate": "48k"})
write_provenance(
    os.path.join(AUDIO, "086-son-markov-guajira-phase1.wav"), "ai-generated",
    generator="SP-001 FluidSynth render of phase-1 MIDI (raw Markov draft)",
    sources=[MIDI1],
    parameters={"method": "SP-001", "soundfont": sf})
write_provenance(
    os.path.join(AUDIO, "086-son-markov-guajira-phase1.ogg"), "ai-generated",
    generator="ffmpeg libopus voip 48k from phase-1 WAV",
    sources=[os.path.join(AUDIO, "086-son-markov-guajira-phase1.wav")],
    parameters={"codec": "libopus", "application": "voip", "bitrate": "48k"})

# silence/RMS stats for the phase-1 render too
wav1 = os.path.join(AUDIO, "086-son-markov-guajira-phase1.wav")
with wave.open(wav1, "rb") as wf:
    sr = wf.getframerate()
    n = wf.getnframes()
    ch = wf.getnchannels()
    raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
mono = data.reshape(-1, ch).mean(axis=1) if ch > 1 else data
silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
stats = {
    "phase1_wav_bytes": os.path.getsize(wav1),
    "phase1_ogg_bytes": os.path.getsize(os.path.join(AUDIO, "086-son-markov-guajira-phase1.ogg")),
    "phase1_duration_s": round(len(mono) / sr, 2),
    "phase1_silence_ratio": round(silent, 4),
}
with open(os.path.join(PROJ, "Analysis", "render_stats_phase1.json"), "w") as f:
    json.dump(stats, f, indent=2)
print(json.dumps(stats, indent=2))
