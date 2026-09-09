# -*- coding: utf-8 -*-
"""Audio stats: silence ratio + per-second RMS map + peak. Reads the RENDERED
WAV with stdlib only (wave + struct); no scipy required."""
import json
import os
import struct
import wave

PROJ = "/opt/data/repos/musicom/projects/Styles/Baroque/091-baroque-genetic-allemande"
WAV = os.path.join(PROJ, "Audio", "091-baroque-genetic-allemande.wav")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

with wave.open(WAV, "rb") as wf:
    ch = wf.getnchannels()
    sw = wf.getsampwidth()
    sr = wf.getframerate()
    n = wf.getnframes()
    data = wf.readframes(n)

# interleave -> mono float in [-1, 1]
if sw == 2:
    fmt = "<%dh" % (len(data) // 2)
    samples = struct.unpack(fmt, data)
    mono = [0.0] * (len(samples) // ch)
    for i in range(len(mono)):
        s = 0.0
        for c in range(ch):
            s += samples[i * ch + c]
        mono[i] = s / (ch * 32768.0)
elif sw == 3:
    nframes = len(data) // (3 * ch)
    mono = []
    for i in range(nframes):
        s = 0.0
        for c in range(ch):
            off = (i * ch + c) * 3
            b = data[off:off + 3]
            v = int.from_bytes(b, "little", signed=True)
            s += v / 8388608.0
        mono.append(s / ch)
else:
    raise SystemExit(f"unsupported sample width {sw}")

mono_f = [max(-1.0, min(1.0, x)) for x in mono]
dur = len(mono_f) / sr

THRESH = 0.001
silent = sum(1 for x in mono_f if abs(x) < THRESH) / len(mono_f)
peak = max(abs(x) for x in mono_f)

# per-second RMS
per_sec = []
for sec in range(int(dur) + 1):
    seg = mono_f[sec * sr:(sec + 1) * sr]
    if not seg:
        continue
    rms = (sum(x * x for x in seg) / len(seg)) ** 0.5
    per_sec.append(round(rms, 5))

silent_secs = [i for i, r in enumerate(per_sec) if r < THRESH]
stats = {
    "duration_s": round(dur, 2),
    "sr": sr,
    "channels": ch,
    "peak": round(peak, 4),
    "silence_ratio": round(silent, 4),
    "per_second_rms": per_sec,
    "silent_seconds": silent_secs,
    "verdict_silence": "PASS" if silent < 0.3 else "SUSPECT (>30% silence)",
    "wav_bytes": os.path.getsize(WAV),
}
with open(os.path.join(ANALYSIS_DIR, "render_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)

print("duration_s:", round(dur, 2))
print("peak:", round(peak, 4))
print("silence_ratio:", round(silent, 4))
print("silent_seconds:", silent_secs)
print("per_second_rms:", per_sec)
print("verdict:", stats["verdict_silence"])