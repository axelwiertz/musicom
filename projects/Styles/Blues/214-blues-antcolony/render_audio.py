# -*- coding: utf-8 -*-
"""Render audio + verification for 214-blues-antcolony.

FluidSynth CLI (discover_soundfont) -> WAV -> Opus OGG, silence/RMS/tonal check,
then MANDATORY grid audit (onsets on 8th/16th) + harmony audit (pitched voices in
E blues scale AND their bar's blues chord set) on the phase-2 MIDI.
mido used for READING/analysis only.
"""
import os
import subprocess
import json
import wave
import numpy as np
import mido  # READING ONLY (analysis)

from sound.render.fluidsynth import discover_soundfont
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/Blues/214-blues-antcolony"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "214-blues-antcolony.mid")
P1_MID = os.path.join(MIDI_DIR, "214-blues-antcolony-phase1.mid")
P2_WAV = os.path.join(AUDIO_DIR, "214-blues-antcolony.wav")
P2_OGG = os.path.join(AUDIO_DIR, "214-blues-antcolony.ogg")
P1_WAV = os.path.join(AUDIO_DIR, "214-blues-antcolony-phase1.wav")
P1_OGG = os.path.join(AUDIO_DIR, "214-blues-antcolony-phase1.ogg")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

BLUES_PCS = {2, 4, 7, 9, 10, 11}
BAR12 = ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]
CHORD_PCS = {
    "I":  {4, 11, 2, 7},
    "IV": {9, 4, 2, 7},
    "V":  {11, 9, 2, 4},
}
BAR_TICKS = 1920
SECTION_TICKS = BAR_TICKS * 4

VOICE_NAMES = ["Piano", "Bass", "Harmonica", "Trumpet", "Drums"]


def render_midi(mid_path, wav_path, ogg_path, label):
    sf2 = discover_soundfont()
    cmd = [FLUIDSYNTH, "-ni", "-g", "1.2", "-F", wav_path, sf2, mid_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FluidSynth failed: {res.stderr}")
    assert os.path.getsize(wav_path) > 40, "WAV too small"
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libopus",
                    "-b:a", "128k", "-v", "error", ogg_path], check=True)
    assert os.path.getsize(ogg_path) > 40, "OGG too small"
    write_provenance(wav_path, classification=AI_ASSISTED,
                     generator="musicom.sound.render.fluidsynth",
                     parameters={"project": "214-blues-antcolony", "phase": label,
                                 "format": "wav",
                                 "soundfont": os.path.basename(sf2),
                                 "source_midi": os.path.basename(mid_path)})
    write_provenance(ogg_path, classification=AI_ASSISTED,
                     generator="ffmpeg libopus",
                     parameters={"project": "214-blues-antcolony", "phase": label,
                                 "format": "ogg", "codec": "libopus",
                                 "bitrate": "128k",
                                 "source_midi": os.path.basename(mid_path)})


def analyze_wav(wav_path):
    with wave.open(wav_path, "rb") as wf:
        n_ch = wf.getnchannels()
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_ch > 1:
        samples = samples.reshape(-1, n_ch).mean(axis=1)
    duration = len(samples) / sr
    silence_ratio = float(np.mean(np.abs(samples) < 0.001))
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    rms_per_sec = []
    for s in range(int(np.ceil(duration))):
        seg = samples[s * sr:(s + 1) * sr]
        rms_per_sec.append(round(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0, 4))
    chunk = int(0.5 * sr)
    n_chunks = max(1, len(samples) // chunk)
    tonal = 0
    for c in range(n_chunks):
        seg = samples[c * chunk:(c + 1) * chunk]
        if len(seg) < 32:
            continue
        fft = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
        band = (freqs >= 50) & (freqs <= 1000)
        if np.any(band) and np.max(fft[band]) > 0.01:
            tonal += 1
    return {
        "duration_sec": round(duration, 2),
        "silence_ratio": round(silence_ratio, 4),
        "peak": round(peak, 4),
        "tonal_ratio": round(tonal / n_chunks, 4),
        "rms_per_sec": rms_per_sec,
    }


def verify_midi(mid_path):
    mid = mido.MidiFile(mid_path)
    tracks = []
    for tr in mid.tracks:
        events = []
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                events.append({"pitch": m.note, "tick": t, "chan": m.channel})
        if events:
            tracks.append(events)

    grid_audit = {}
    harmony_audit = {}
    for ti, evs in enumerate(tracks):
        chans = {e["chan"] for e in evs}
        is_drums = 9 in chans
        onsets = [e["tick"] for e in evs]
        off16 = [o for o in onsets if o % 120 != 0]
        off8 = [o for o in onsets if o % 240 != 0]
        label = VOICE_NAMES[ti] if ti < len(VOICE_NAMES) else f"track{ti}"
        grid_audit[label] = {
            "drum_track": is_drums,
            "n_onsets": len(onsets),
            "off_16th": len(off16),
            "off_8th": len(off8),
        }
        if not is_drums:
            out_scale = 0
            out_chord = 0
            for e in evs:
                pc = e["pitch"] % 12
                tick = e["tick"]
                bar_idx = min(tick // BAR_TICKS, 23)
                func = BAR12[bar_idx % 12]
                chord = CHORD_PCS[func]
                if pc not in BLUES_PCS:
                    out_scale += 1
                if pc not in chord:
                    out_chord += 1
            harmony_audit[label] = {
                "n_notes": len(evs),
                "out_of_scale": out_scale,
                "out_of_chord": out_chord,
            }
    return grid_audit, harmony_audit


if __name__ == "__main__":
    print("--- Render Phase 2 ---")
    render_midi(P2_MID, P2_WAV, P2_OGG, "phase2")
    p2 = analyze_wav(P2_WAV)
    print("Phase 2 audio:", {k: v for k, v in p2.items() if k != "rms_per_sec"})

    print("\n--- Render Phase 1 ---")
    render_midi(P1_MID, P1_WAV, P1_OGG, "phase1")
    p1 = analyze_wav(P1_WAV)
    print("Phase 1 audio:", {k: v for k, v in p1.items() if k != "rms_per_sec"})

    print("\n--- Verify Phase 2 MIDI (grid + harmony) ---")
    grid_audit, harmony_audit = verify_midi(P2_MID)
    for k, v in grid_audit.items():
        print(f"GRID {k}: {v}")
    for k, v in harmony_audit.items():
        print(f"HARMONY {k}: {v}")

    result = {
        "audio": {"phase2": p2, "phase1": p1},
        "grid_audit": grid_audit,
        "harmony_audit": harmony_audit,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(result, f, indent=2)
    print("\nSummary -> Analysis/summary.json")