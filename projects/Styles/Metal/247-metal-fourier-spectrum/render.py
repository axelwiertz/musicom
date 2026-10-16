# -*- coding: utf-8 -*-
"""247 — render + master + verify (FluidSynth -> LUFS master -> Opus OGG)."""
import json
import os
import subprocess
import sys

import numpy as np

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
from compose import (  # noqa: E402
    CHORDS, POOL_BY_SECTION, section_of_bar, TOTAL_BARS, BAR, SIXTEENTH,
    PITCHED_VOICES, BASE, MIDI_PATH, PHASE1_PATH,
)
# Engine types — this script only READS the exported MIDI back for verification
# (mido is used strictly for readback analysis, never for authoring).
from structures import MusicEvent, MusicUnit  # noqa: E402,F401

AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

WAV_PATH = os.path.join(AUDIO_DIR, BASE + ".wav")
WAV1_PATH = os.path.join(AUDIO_DIR, BASE + "-phase1.wav")
OGG_PATH = os.path.join(AUDIO_DIR, BASE + ".ogg")
OGG1_PATH = os.path.join(AUDIO_DIR, BASE + "-phase1.ogg")


def render_wav(midi_path, wav_path):
    from utilities.env import fluidsynth_bin
    from sound.render.fluidsynth import discover_soundfont
    sf = discover_soundfont()
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", wav_path, sf, midi_path],
        capture_output=True, text=True)
    if r.returncode != 0 or os.path.getsize(wav_path) < 1000:
        raise RuntimeError(f"fluidsynth failed: {r.stderr[-500:]}")
    return sf


def master_wav(wav_path, style):
    from sound.effects.mastering import master, target_for_style
    from sound.utils.io import read_wav, write_wav
    audio, sr = read_wav(wav_path)
    fallback = target_for_style(style)          # 'metal' -> -14.0 fallback
    target = -11.0                               # rock (loud-first metal) target
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(wav_path, mastered, sr, normalize=False)
    return fallback, target, rep


def silence_stats(wav_path):
    from sound.utils.io import read_wav
    audio, sr = read_wav(wav_path)
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    n = len(mono)
    per_sec = []
    for t in range(0, n, sr):
        seg = mono[t:t + sr]
        if len(seg) == 0:
            continue
        per_sec.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
    return {"silence_ratio": round(silent, 4), "per_sec_rms": per_sec,
            "sr": sr, "duration_s": round(n / sr, 3)}


def to_ogg(wav_path, ogg_path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-codec:a", "libopus", "-b:a", "128k", ogg_path],
                   capture_output=True, text=True)
    assert os.path.getsize(ogg_path) > 40


def verify_midi(midi_path):
    # READING ONLY (analysis) — mido is used to read the exported MIDI back for
    # zero-drift / grid / harmony auditing; the MIDI itself was authored by the
    # musicom engine (UnitMatrixComposer.to_midi), never hand-rolled here.
    import mido
    mid = mido.MidiFile(midi_path)
    tracks = []
    for tr in mid.tracks:
        ch = None
        for m in tr:
            if m.type == "program_change":
                ch = m.channel
        t = 0
        onsets = []
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                onsets.append((t, m.note))
        if onsets:
            tracks.append({"channel": ch, "onsets": onsets,
                           "length": t})
    # zero-drift: all note tracks equal length
    lengths = [tr["length"] for tr in tracks]
    zero_drift = len(set(lengths)) == 1

    out_scale = 0
    out_chord = 0
    total_pitched = 0
    off_grid = 0
    for tr in tracks:
        if tr["channel"] == 9:
            continue
        for t, note in tr["onsets"]:
            total_pitched += 1
            pc = note % 12
            bar = min(TOTAL_BARS - 1, t // BAR)
            sec = section_of_bar(bar)
            pool = POOL_BY_SECTION[sec]
            cpc = set(CHORDS[bar][3])
            if pc not in pool:
                out_scale += 1
            if pc not in cpc:
                out_chord += 1
            if t % SIXTEENTH != 0:
                off_grid += 1
    return {"zero_drift": zero_drift, "track_lengths": lengths,
            "n_tracks": len(tracks), "out_scale": out_scale,
            "out_chord": out_chord, "total_pitched": total_pitched,
            "off_grid_onsets": off_grid}


def main():
    sf = render_wav(MIDI_PATH, WAV_PATH)
    render_wav(PHASE1_PATH, WAV1_PATH)

    fallback, target, rep = master_wav(WAV_PATH, "metal")
    fb1, tgt1, rep1 = master_wav(WAV1_PATH, "metal")

    to_ogg(WAV_PATH, OGG_PATH)
    to_ogg(WAV1_PATH, OGG1_PATH)

    sil2 = silence_stats(WAV_PATH)
    sil1 = silence_stats(WAV1_PATH)
    v2 = verify_midi(MIDI_PATH)
    v1 = verify_midi(PHASE1_PATH)

    stats = {
        "soundfont": sf,
        "target_for_style_metal": fallback, "chosen_target": target,
        "master_phase2": {"integrated_lufs": rep["integrated_lufs"],
                          "true_peak_db": rep["true_peak_db"]},
        "master_phase1": {"integrated_lufs": rep1["integrated_lufs"],
                          "true_peak_db": rep1["true_peak_db"]},
        "silence_phase2": sil2, "silence_phase1": sil1,
        "verify_phase2": v2, "verify_phase1": v1,
        "sizes": {
            "phase2_mid": os.path.getsize(MIDI_PATH),
            "phase1_mid": os.path.getsize(PHASE1_PATH),
            "phase2_wav": os.path.getsize(WAV_PATH),
            "phase1_wav": os.path.getsize(WAV1_PATH),
            "phase2_ogg": os.path.getsize(OGG_PATH),
            "phase1_ogg": os.path.getsize(OGG1_PATH),
        },
    }
    with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    print("SF:", sf)
    print("target_for_style('metal') =", fallback, "| chosen target =", target)
    print("PHASE2 master LUFS", rep["integrated_lufs"], "dBTP", rep["true_peak_db"])
    print("PHASE1 master LUFS", rep1["integrated_lufs"], "dBTP", rep1["true_peak_db"])
    print("PHASE2 silence_ratio", sil2["silence_ratio"], "dur", sil2["duration_s"], "s")
    print("PHASE1 silence_ratio", sil1["silence_ratio"], "dur", sil1["duration_s"], "s")
    print("VERIFY phase2:", json.dumps(v2))
    print("VERIFY phase1:", json.dumps(v1))
    for k, sz in stats["sizes"].items():
        print(f"  {k}: {sz} bytes")
    print("DONE")


if __name__ == "__main__":
    main()
