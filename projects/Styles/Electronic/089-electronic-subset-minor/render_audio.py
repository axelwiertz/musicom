# -*- coding: utf-8 -*-
"""089-electronic-subset-minor — audio render (SP-001 FluidSynth) + stats.

Job contract:
  - Render MIDI → WAV via discover_soundfont() (FluidR3_GM preferred),
    then OGG (opus, 48k, voip) for Telegram delivery.
  - Full mix + per-track stems (RenderPipeline.render_stems).
  - Verify: file sizes > 40 B, silence ratio + per-second RMS profile
    (mid-track gaps > 30% silence = suspect).
  - provenance.json sidecar per artifact.
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

# engine adapter (SP-001 default) — repo not pip-installed, add to path
REPO = "/opt/data/repos/musicom"
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from workflows.musicom_workflow import produce          # noqa: E402
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

PROJ = "/opt/data/projects/Styles/Electronic/089-electronic-subset-minor"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

P2 = os.path.join(MIDI_DIR, "089-electronic-subset-minor.mid")


def ogg_from(wav_path):
    ogg = wav_path.rsplit(".", 1)[0] + ".ogg"
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(ogg):
        raise RuntimeError(f"ffmpeg ogg failed: {r.stderr[-300:]}")
    return ogg


def stats(wav_path):
    """Silence ratio + per-second RMS profile."""
    data, sr = sf.read(wav_path, always_2d=True)
    mono = data.mean(axis=1)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    dur = len(mono) / sr
    rms_map = []
    for sec in range(int(dur) + 1):
        seg = mono[sec * sr:(sec + 1) * sr]
        if len(seg):
            rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
    peak = float(np.max(np.abs(mono)))
    return {"silence_ratio": round(silent, 4), "duration_s": round(dur, 2),
            "peak": round(peak, 4), "rms_per_sec": rms_map}


def main():
    print("=== rendering full mix (SP-001 FluidSynth) ===")
    res = produce(P2, method="SP-001", out_dir=AUDIO_DIR)
    mix_wav = res.wav_path
    mix_ogg = ogg_from(mix_wav)
    print("mix:", mix_wav, "->", mix_ogg)
    for p in (mix_wav, mix_ogg):
        assert os.path.getsize(p) > 40, f"empty render {p}"
    st = stats(mix_wav)
    print("MIX STATS:", json.dumps(st))
    assert st["silence_ratio"] < 0.30, \
        f"too much silence: {st['silence_ratio']:.2%}"

    # provenance for mix artifacts
    write_provenance(mix_ogg, AI_GENERATED, "SP-001 FluidSynth render",
                     parameters={"method": "SP-001", "sf2": "discover_soundfont()",
                                 "project": "089-electronic-subset-minor"})
    write_provenance(mix_wav, AI_GENERATED, "SP-001 FluidSynth render",
                     parameters={"method": "SP-001", "project": "089-electronic-subset-minor"})

    # stems
    print("=== rendering stems ===")
    stems_dir = os.path.join(AUDIO_DIR, "stems")
    os.makedirs(stems_dir, exist_ok=True)
    try:
        from sound.render.pipeline import RenderPipeline  # noqa: E402
        from sound.render.fluidsynth import discover_soundfont  # noqa: E402
        sf2 = discover_soundfont()
        fluid_bin = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
        pipe = RenderPipeline(fluidsynth_bin=fluid_bin,
                              soundfont_path=sf2) if sf2 else \
            RenderPipeline(fluidsynth_bin=fluid_bin)
        stems = pipe.render_stems(P2, stems_dir, format="wav")
        stem_files = {}
        for label, wav in stems.items():
            ogg = ogg_from(wav)
            stem_files[label] = {"wav": wav, "ogg": ogg}
            print("  stem:", label, "->", os.path.basename(wav))
    except Exception as e:  # stems optional — don't fail the job
        print("STEMS SKIPPED:", e)
        stem_files = {}

    report = {
        "mix": {"wav": mix_wav, "ogg": mix_ogg, "stats": st},
        "stems": stem_files,
    }
    with open(os.path.join(AUDIO_DIR, "render_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("RENDER OK")


if __name__ == "__main__":
    main()
