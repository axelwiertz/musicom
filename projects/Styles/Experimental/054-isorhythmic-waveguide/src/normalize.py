import numpy as np
import wave
import subprocess
import os

wav_in = "/tmp/054_render.wav"
wav_norm = "/tmp/054_normalized.wav"
ogg_out = "/opt/data/projects/Styles/Experimental/054-isorhythmic-waveguide/Audio/054-isorhythmic-waveguide.ogg"

# Read WAV
with wave.open(wav_in, 'rb') as wf:
    sr = wf.getframerate()
    ch = wf.getnchannels()
    sw = wf.getsampwidth()
    frames = wf.readframes(wf.getnframes())

# Convert to numpy
audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
peak = np.max(np.abs(audio))
print(f"Input peak: {peak:.0f}, samples: {len(audio)}, sr: {sr}, ch: {ch}")

# Normalize to -1dB (0.89 of max)
target_peak = 0.89 * 32767
if peak > 0:
    audio = audio * (target_peak / peak)
    new_peak = np.max(np.abs(audio))
    print(f"Normalized peak: {new_peak:.0f}")

# Write normalized WAV
audio_int16 = np.clip(audio, -32768, 32767).astype(np.int16)
with wave.open(wav_norm, 'w') as wf:
    wf.setnchannels(ch)
    wf.setsampwidth(sw)
    wf.setframerate(sr)
    wf.writeframes(audio_int16.tobytes())

print(f"Normalized WAV: {os.path.getsize(wav_norm)} bytes")

# Encode to Opus with higher bitrate
subprocess.run([
    "ffmpeg", "-i", wav_norm,
    "-codec:a", "libopus", "-b:a", "128k",
    "-y", ogg_out
], capture_output=True)

print(f"OGG: {os.path.getsize(ogg_out)} bytes")

# Cleanup
os.remove(wav_in)
os.remove(wav_norm)
