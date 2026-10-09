# -*- coding: utf-8 -*-
"""232 render.py — SP-001 FluidSynth render -> WAV + OGG for phase1 & phase2.

Uses the sanctioned workflow adapter (produce) which resolves the soundfont
via discover_soundfont() and runs fluidsynth -ni -g 1.2 then ffmpeg to opus.
Then measures silence ratio + per-second RMS on the rendered WAV.
"""
import os
import json
import wave

import numpy as np

from workflows.musicom_workflow import produce
from workflows.provenance import write_provenance, AI_ASSISTED

import compose as C

AUDIO_DIR = os.path.join(C.PROJECT_DIR, "Audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def analyze_wav(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n_ch = wf.getnchannels()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_ch > 1:
        audio = audio.reshape(-1, n_ch).mean(axis=1)
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    silent = float(np.sum(np.abs(audio) < 0.001) / len(audio)) if len(audio) else 0.0
    # per-second RMS
    secs = len(audio) // sr
    rms_map = []
    for s in range(secs):
        seg = audio[s * sr:(s + 1) * sr]
        rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 5) if len(seg) else 0.0)
    rms_mean = float(np.sqrt(np.mean(audio ** 2))) if len(audio) else 0.0
    return {"sr": sr, "channels": n_ch, "seconds": round(len(audio) / sr, 2),
            "peak": round(peak, 4), "silence_ratio": round(silent, 4),
            "rms_mean": round(rms_mean, 5), "rms_per_second": rms_map}


def main():
    stats = {}
    for label, midi in [("phase2", C.MIDI_PATH), ("phase1", C.PHASE1_PATH)]:
        r = produce(midi, method="SP-001", out_dir=AUDIO_DIR)
        stats[label] = {
            "wav": r.wav_path, "ogg": r.ogg_path,
            "wav_bytes": os.path.getsize(r.wav_path),
            "ogg_bytes": os.path.getsize(r.ogg_path),
            "analysis": analyze_wav(r.wav_path),
        }
        assert os.path.getsize(r.wav_path) > 40
        assert os.path.getsize(r.ogg_path) > 40
        write_provenance(
            r.wav_path, classification=AI_ASSISTED,
            generator="SP-001 FluidSynth SoundFont render",
            parameters={"project": C.BASE, "method": 32, "phase": label,
                        "key": C.KEY_NAME, "bpm": C.BPM},
            notes="FluidSynth (discover_soundfont) render of phase MIDI.")
        print(f"[{label}] wav={stats[label]['wav_bytes']}B "
              f"ogg={stats[label]['ogg_bytes']}B "
              f"peak={stats[label]['analysis']['peak']} "
              f"silence={stats[label]['analysis']['silence_ratio']} "
              f"rms={stats[label]['analysis']['rms_mean']}")

    with open(os.path.join(C.ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("[OK] render_stats.json written")


if __name__ == "__main__":
    main()
