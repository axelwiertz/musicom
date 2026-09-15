# -*- coding: utf-8 -*-
"""Audio stats: silence ratio + per-second RMS map + peak (stdlib only)."""
import json
import os
import struct
import wave

PROJ = "/opt/data/repos/musicom/projects/Styles/Trap/096-trap-skeleton-seoul"
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)
THRESH = 0.001


def stats_for(wav_path):
    with wave.open(wav_path, "rb") as wf:
        ch, sw, sr, n = (wf.getnchannels(), wf.getsampwidth(),
                         wf.getframerate(), wf.getnframes())
        data = wf.readframes(n)
    if sw == 2:
        samples = struct.unpack("<%dh" % (len(data) // 2), data)
        mono = [sum(samples[i * ch + c] for c in range(ch)) / (ch * 32768.0)
                for i in range(len(samples) // ch)]
    elif sw == 3:
        nframes = len(data) // (3 * ch)
        mono = []
        for i in range(nframes):
            s = 0.0
            for c in range(ch):
                off = (i * ch + c) * 3
                s += int.from_bytes(data[off:off + 3], "little",
                                    signed=True) / 8388608.0
            mono.append(s / ch)
    else:
        raise SystemExit("unsupported sample width %s" % sw)

    mono = [max(-1.0, min(1.0, x)) for x in mono]
    dur = len(mono) / sr
    silent = sum(1 for x in mono if abs(x) < THRESH) / len(mono)
    peak = max(abs(x) for x in mono)
    per_sec = []
    for sec in range(int(dur) + 1):
        seg = mono[sec * sr:(sec + 1) * sr]
        if seg:
            per_sec.append(round((sum(x * x for x in seg) / len(seg)) ** 0.5, 5))
    silent_secs = [i for i, r in enumerate(per_sec) if r < THRESH]
    return {"wav": os.path.basename(wav_path), "duration_s": round(dur, 2),
            "sr": sr, "channels": ch, "peak": round(peak, 4),
            "silence_ratio": round(silent, 4), "per_second_rms": per_sec,
            "silent_seconds": silent_secs,
            "verdict_silence": ("PASS" if silent < 0.3
                                else "SUSPECT (>30% silence)"),
            "wav_bytes": os.path.getsize(wav_path)}


out = {}
for label, fn in (("phase2", "096-trap-skeleton-seoul.wav"),
                  ("phase1", "096-trap-skeleton-seoul-phase1.wav")):
    p = os.path.join(PROJ, "Audio", fn)
    if os.path.exists(p):
        out[label] = stats_for(p)
        s = out[label]
        print(label, s["duration_s"], "s peak", s["peak"], "silence",
              s["silence_ratio"], "silent_secs", s["silent_seconds"],
              s["verdict_silence"])
        print("  per_second_rms:", s["per_second_rms"])

with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
    json.dump(out, f, indent=2)
