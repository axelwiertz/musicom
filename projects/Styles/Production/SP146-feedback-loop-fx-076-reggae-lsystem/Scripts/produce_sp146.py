# -*- coding: utf-8 -*-
"""SP-146 Feedback-Loop Echo + Codec Loss — production for 076-reggae-lsystem.

Absolute-layer effect: render the (reworked, per-bar chord-quantized) source
MIDI with FluidSynth (dry carrier), apply FeedbackLoopFX (echo whose wobble /
drive / tone / codec-loss stages live INSIDE the feedback path — RC-20 V2
Echo+Loss style), master to the reggae LUFS target, encode Opus OGG, and verify
pitch / harmonic energy / silence / RMS.
"""
import json
import os
import subprocess

import numpy as np

from sound.effects.feedback_loop_fx import FeedbackLoopFX
from sound.effects.mastering import master, target_for_style
from sound.render.fluidsynth import discover_soundfont
from sound.utils.io import read_wav, write_wav
from utilities.env import fluidsynth_bin

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(OUT, "Audio")
MIDI_DIR = os.path.join(OUT, "MIDI")
ANALYSIS = os.path.join(OUT, "Analysis")
for d in (AUDIO, MIDI_DIR, ANALYSIS):
    os.makedirs(d, exist_ok=True)

SRC_MIDI = os.path.join(MIDI_DIR, "076-reggae-lsystem-reworked.mid")
STYLE = "Reggae"
BPM = 96.0
SR = 44100

# A aeolian pitch classes for verification
SCALE_PCS = {9, 11, 0, 2, 4, 5, 7}

# --- SP-146 parameters (eighth-note dub echo locked to 96 BPM) ------------
BEAT_S = 60.0 / BPM
DELAY_MS = BEAT_S * 0.5 * 1000.0          # 312.5 ms = eighth note
FX_PARAMS = {
    "delay_ms": DELAY_MS,
    "feedback": 0.55,
    "mix": 0.35,
    "wobble_cents": 6.0,
    "wobble_rate": 0.5,
    "flutter_rate": 6.3,
    "drive": 0.12,
    "tone_hz": 6000.0,
    "smear": 0.15,
    "codec": True,
    "codec_bitrate": 96.0,
    "reverse": False,
}

DRY_WAV = os.path.join(AUDIO, "076-reggae-lsystem-reworked-dry.wav")
FINAL_WAV = os.path.join(AUDIO, "SP146-feedback-loop-fx-076-reggae-lsystem.wav")
FINAL_OGG = os.path.join(AUDIO, "SP146-feedback-loop-fx-076-reggae-lsystem.ogg")


def render_dry():
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("No SoundFont found")
    fs = fluidsynth_bin()
    r = subprocess.run(
        [fs, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", DRY_WAV, sf, SRC_MIDI],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(DRY_WAV) or os.path.getsize(DRY_WAV) < 1000:
        raise RuntimeError("fluidsynth failed: %s" % r.stderr[-500:])
    print("dry render OK: %s (%d bytes, soundfont=%s)"
          % (DRY_WAV, os.path.getsize(DRY_WAV), os.path.basename(sf)))
    return sf


def verify(audio, sr, label):
    mono = audio.mean(axis=1) if audio.ndim == 2 else audio
    mono = np.asarray(mono, dtype=float)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    # per-second RMS profile
    per_sec = []
    for s in range(0, len(mono) - sr, sr):
        per_sec.append(float(np.sqrt(np.mean(mono[s:s + sr] ** 2))))
    win = int(0.5 * sr)
    hit = 0
    valid = 0
    harms = []
    for start in range(0, len(mono) - win, win):
        seg = mono[start:start + win]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        if rms < 0.005:
            continue
        valid += 1
        spec = np.abs(np.fft.rfft(seg * np.hanning(win)))
        freqs = np.fft.rfftfreq(win, 1.0 / sr)
        band = (freqs >= 50.0) & (freqs <= 1000.0)
        bspec = spec[band]
        bfreq = freqs[band]
        f0 = float(bfreq[np.argmax(bspec)])
        midi = round(12.0 * np.log2(f0 / 440.0) + 69.0)
        if (midi % 12) in SCALE_PCS:
            hit += 1
        h8 = 0.0
        for k in range(1, 9):
            m = (freqs >= k * f0 - 15.0) & (freqs <= k * f0 + 15.0)
            h8 += float(np.sum(spec[m]))
        harms.append(h8 / (float(np.sum(bspec)) + 1e-12))
    hit_rate = hit / valid if valid else 0.0
    mean_harm = float(np.mean(harms)) if harms else 0.0
    mid_silence = float(np.sum(np.asarray(per_sec) < 0.002)) if per_sec else 0.0
    print("[%s] silence=%.2f%%  fft-hit=%.3f (n=%d)  mean-harmonic=%.4f  "
          "mid-silent-secs=%d/%d"
          % (label, silent * 100, hit_rate, valid, mean_harm,
             mid_silence, len(per_sec)))
    return {"silence_ratio": round(silent, 4),
            "fft_dominant_pc_hit_rate": round(hit_rate, 4),
            "valid_windows": valid,
            "mean_harmonic_energy": round(mean_harm, 4),
            "per_second_rms": [round(x, 4) for x in per_sec],
            "mid_track_silent_seconds": int(mid_silence)}


def main():
    sf = render_dry()
    dry, sr = read_wav(DRY_WAV)
    print("dry shape=%s sr=%d peak=%.3f" % (dry.shape, sr, float(np.abs(dry).max())))

    # --- apply SP-146 (absolute layer, whole piece) -----------------------
    fx = FeedbackLoopFX(sr, **FX_PARAMS)
    effected = fx.process(dry)
    print("effected shape=%s peak=%.3f" % (effected.shape, float(np.abs(effected).max())))

    # --- master to reggae target ------------------------------------------
    target = target_for_style(STYLE)   # reggae -> -14.0
    mastered, rep = master(effected, target_lufs=target, ceiling_db=-1.0,
                           sample_rate=sr)
    write_wav(FINAL_WAV, mastered, sr, normalize=False)
    print("mastered: target=%.1f  lufs=%s  tp=%s dB"
          % (target, rep["integrated_lufs"], rep["true_peak_db"]))

    # --- Opus OGG ----------------------------------------------------------
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", FINAL_WAV,
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", FINAL_OGG],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(FINAL_OGG):
        raise RuntimeError("ffmpeg failed: %s" % r.stderr[-300:])

    # --- verification ------------------------------------------------------
    dry_stats = verify(dry, sr, "dry")
    fin_stats = verify(mastered, sr, "final")

    stats = {
        "method": "SP-146",
        "module": "sound.effects.feedback_loop_fx",
        "style": STYLE,
        "target_lufs": target,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "peak": round(float(np.abs(mastered).max()), 4),
        "rms": round(float(np.sqrt(np.mean(mastered ** 2))), 4),
        "sample_rate": sr,
        "fx_params": FX_PARAMS,
        "soundfont": os.path.basename(sf),
        "dry": dry_stats,
        "final": fin_stats,
        "files": {
            "dry_wav": os.path.basename(DRY_WAV),
            "dry_wav_bytes": os.path.getsize(DRY_WAV),
            "final_wav": os.path.basename(FINAL_WAV),
            "final_wav_bytes": os.path.getsize(FINAL_WAV),
            "final_ogg": os.path.basename(FINAL_OGG),
            "final_ogg_bytes": os.path.getsize(FINAL_OGG),
            "src_midi": os.path.basename(SRC_MIDI),
            "src_midi_bytes": os.path.getsize(SRC_MIDI),
        },
        "master_stages": rep.get("stages"),
    }
    with open(os.path.join(ANALYSIS, "render_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    prov = {
        "project": "076-reggae-lsystem",
        "production": "SP-146 Feedback-Loop Echo + Codec Loss (RC-20 V2-style)",
        "carrier": "FluidSynth dry render of reworked (per-bar chord-quantized) MIDI",
        "layer": "absolute",
        "style": STYLE,
        "bpm": BPM,
        "fx_params": FX_PARAMS,
        "target_lufs": target,
        "integrated_lufs": rep["integrated_lufs"],
        "true_peak_db": rep["true_peak_db"],
        "verification": {"dry": dry_stats, "final": fin_stats},
    }
    with open(os.path.join(OUT, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print("DONE")
    print("FINAL_WAV=%s (%d bytes)" % (FINAL_WAV, os.path.getsize(FINAL_WAV)))
    print("FINAL_OGG=%s (%d bytes)" % (FINAL_OGG, os.path.getsize(FINAL_OGG)))
    print("STATS=%s" % os.path.join(ANALYSIS, "render_stats.json"))


if __name__ == "__main__":
    main()
