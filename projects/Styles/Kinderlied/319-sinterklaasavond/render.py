# -*- coding: utf-8 -*-
"""319-sinterklaasavond — render + production (SP-032 FDN Reverb) + master.

Chain: FluidSynth (FluidR3_GM) -> SP-032 FDN Reverb (warm hall) -> master
(-16 LUFS) -> Opus OGG. The FDN reverb is the production method on the
humanized render; the perfect render is kept dry (FluidSynth + master) so the
production method's effect is A/B-able.

Writes Analysis/render_report.json (LUFS, true peak, FDN params, sizes).
"""

import json
import os
import subprocess

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style
from sound.effects.fdn_reverb import FDN
from sound.utils.io import read_wav, write_wav

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, "Audio")
ANALYSIS = os.path.join(BASE, "Analysis")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(ANALYSIS, exist_ok=True)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF = discover_soundfont()
TARGET = target_for_style("sinterklaas")   # -16.0
FDN_PARAMS = {"size": 0.72, "decay": 0.62, "brightness": 0.45,
              "wet_dry": 0.32, "width": 1.0}

report = {}
for tag in ("perfect", "humanized"):
    midi = os.path.join(BASE, "MIDI", f"319-sinterklaasavond-{tag}.mid")
    wav = os.path.join(AUDIO, f"319-sinterklaasavond-{tag}.wav")
    ogg = os.path.join(AUDIO, f"319-sinterklaasavond-{tag}.ogg")

    subprocess.run([FLUID, "-ni", "-g", "1.2", "-F", wav, SF, midi],
                   check=True, capture_output=True)
    audio, sr = read_wav(wav)

    # production method: SP-032 FDN reverb (warm hall) on the humanized render;
    # the perfect render stays dry so the production pass is A/B-able.
    if tag == "humanized":
        fdn = FDN(sample_rate=sr)
        fdn.set(**FDN_PARAMS)
        audio = fdn.process(audio)

    mastered, rep = master(audio, target_lufs=TARGET, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav, mastered, sr, normalize=False)

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", wav, "-codec:a", "libopus", "-b:a", "96k", ogg],
                   check=True, capture_output=True)

    report[tag] = {
        "soundfont": os.path.basename(SF),
        "target_lufs": TARGET,
        "integrated_lufs": round(rep["integrated_lufs"], 2),
        "true_peak_db": round(rep["true_peak_db"], 3),
        "production": "SP-032 FDN Reverb" if tag == "humanized" else "dry (SP-001)",
        "fdn_params": FDN_PARAMS if tag == "humanized" else None,
        "wav_bytes": os.path.getsize(wav),
        "ogg_bytes": os.path.getsize(ogg),
    }
    assert os.path.getsize(wav) > 40, f"empty WAV: {wav}"
    assert os.path.getsize(ogg) > 40, f"empty OGG: {ogg}"
    print(tag, "->", report[tag], flush=True)

with open(os.path.join(ANALYSIS, "render_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("done")
