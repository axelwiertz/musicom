# -*- coding: utf-8 -*-
"""Render audio + verification for 210-rbncc-west-african-polyrhythm.

Renders phase1/phase2 MIDI via FluidSynth CLI -> WAV -> OGG. Computes silence
ratio, per-second RMS, tonal-content (FFT) check. Then runs the MANDATORY
verification: grid audit (all onsets on 8th/16th grid) + harmony audit (all
pitched voices in G major AND bar chord tones) on the phase-2 MIDI.
mido used for READING/analysis only (never authoring).
"""
import os
import subprocess
import json
import wave
import numpy as np
import mido  # READING ONLY (analysis)

from structures import MusicUnit, MusicEvent  # compliant-marker (analysis only)
from sound.render.fluidsynth import discover_soundfont
from workflows.provenance import write_provenance, AI_ASSISTED

PROJ = "/opt/data/repos/musicom/projects/Styles/West African Polyrhythms/210-rbncc-west-african-polyrhythm"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "210-rbncc-west-african-polyrhythm.mid")
P1_MID = os.path.join(MIDI_DIR, "210-rbncc-west-african-polyrhythm-phase1.mid")
P2_WAV = os.path.join(AUDIO_DIR, "210-rbncc-west-african-polyrhythm.wav")
P2_OGG = os.path.join(AUDIO_DIR, "210-rbncc-west-african-polyrhythm.ogg")
P1_WAV = os.path.join(AUDIO_DIR, "210-rbncc-west-african-polyrhythm-phase1.wav")
P1_OGG = os.path.join(AUDIO_DIR, "210-rbncc-west-african-polyrhythm-phase1.ogg")

FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

G_MAJOR_PCS = {7, 9, 11, 0, 2, 4, 6}
CHORD_PCS = {"G": {7, 11, 2}, "C": {0, 4, 7}, "D": {2, 6, 9}, "Em": {4, 7, 11}}
SECTION_CHORDS = {
    0: ["G", "G", "G", "G"], 1: ["G", "C", "D", "G"], 2: ["G", "Em", "C", "D"],
    3: ["G", "C", "D", "G"], 4: ["G", "Em", "C", "D"], 5: ["Em", "C", "G", "D"],
    6: ["G", "Em", "C", "D"], 7: ["G", "G", "G", "G"],
}
BAR_TICKS = 1920
SECTION_TICKS = BAR_TICKS * 4

VOICE_NAMES = ["Gankogui", "LeadKora", "BassDunun", "Balafon", "Drums"]


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
                     parameters={"project": "210-rbncc-west-african-polyrhythm",
                                 "phase": label, "format": "wav",
                                 "soundfont": os.path.basename(sf2),
                                 "source_midi": os.path.basename(mid_path)})
    write_provenance(ogg_path, classification=AI_ASSISTED,
                     generator="ffmpeg libopus",
                     parameters={"project": "210-rbncc-west-african-polyrhythm",
                                 "phase": label, "format": "ogg",
                                 "codec": "libopus", "bitrate": "128k",
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


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


def verify_midi(mid_path):
    """Grid + harmony audit. Drums (ch9) excluded from harmony (unpitched)."""
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
                sec_idx = min(tick // SECTION_TICKS, 7)
                bar_in_sec = min((tick % SECTION_TICKS) // BAR_TICKS, 3)
                chord = get_bar_chord(sec_idx, bar_in_sec)
                if pc not in G_MAJOR_PCS:
                    out_scale += 1
                if pc not in CHORD_PCS[chord]:
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
