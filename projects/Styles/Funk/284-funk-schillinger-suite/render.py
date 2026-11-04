# -*- coding: utf-8 -*-
"""Render + master 284-funk-schillinger-suite (perfect + humanized) to OGG.

FluidSynth -> master() LUFS pass -> Opus OGG. Both dual-version MIDIs.
"""
import os
import json
import subprocess

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.utils.io import read_wav, write_wav
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/projects/Styles/Funk/284-funk-schillinger-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
STYLE = "funk"
TARGET = target_for_style(STYLE)

assert SF and os.path.exists(SF), "no soundfont: %r" % SF
print("soundfont:", SF, "target_lufs:", TARGET)

report = {}
for tag in ("perfect", "humanized"):
    midi = os.path.join(MIDI_DIR, f"284-funk-schillinger-suite-{tag}.mid")
    wav = os.path.join(AUDIO_DIR, f"284-funk-schillinger-suite-{tag}.wav")
    ogg = os.path.join(AUDIO_DIR, f"284-funk-schillinger-suite-{tag}.ogg")

    # 1. FluidSynth render (raw)
    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, midi],
                   check=True, capture_output=True)
    assert os.path.getsize(wav) > 40, "empty wav"

    # 2. master to genre loudness
    audio, sr = read_wav(wav)
    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    # silence ratio
    mono = mastered.mean(axis=1) if mastered.ndim > 1 else mastered
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))

    # 3. Opus OGG
    subprocess.run(["ffmpeg", "-y", "-i", wav,
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", ogg, "-loglevel", "error"], check=True)

    for p in (wav, ogg):
        assert os.path.getsize(p) > 40, "empty audio: %s" % p

    report[tag] = {
        "wav": wav, "ogg": ogg,
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
        "target_lufs": TARGET,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "silence_ratio": round(silent, 4),
        "sample_rate": sr,
    }
    write_provenance(
        ogg, AI_ASSISTED,
        "FluidSynth (FluidR3_GM) -> master() LUFS -> Opus OGG",
        parameters={"style": STYLE, "target_lufs": TARGET, "tag": tag,
                    "source_midi": os.path.basename(midi),
                    "integrated_lufs": rep["integrated_lufs"],
                    "true_peak_db": rep["true_peak_db"],
                    "silence_ratio": round(silent, 4)},
        notes=f"{tag} render: master() to {TARGET} LUFS, -1 dBTP ceiling")

    print(f"[{tag}] LUFS={rep['integrated_lufs']:.2f} "
          f"TP={rep['true_peak_db']:.2f} silence={silent:.3f} "
          f"wav={os.path.getsize(wav)} ogg={os.path.getsize(ogg)}")

with open(os.path.join(PROJ, "Analysis", "render_stats.json"), "w") as f:
    json.dump(report, f, indent=2)

print("RENDER DONE")
