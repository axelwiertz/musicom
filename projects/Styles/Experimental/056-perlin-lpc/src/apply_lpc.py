# -*- coding: utf-8 -*-
"""
SP-028: Linear Predictive Coding (LPC) Synthesis post-processing
Analyzes FluidSynth WAV output via autocorrelation/Levinson-Durbin
Resynthesizes through all-pole IIR filter for formant-like coloration
"""
import os
import numpy as np
import wave

PROJECT_DIR = "/opt/data/projects/Styles/Experimental/056-perlin-lpc"
INPUT_WAV = os.path.join(PROJECT_DIR, "Audio", "056-perlin-lpc_raw.wav")
OUTPUT_WAV = os.path.join(PROJECT_DIR, "Audio", "056-perlin-lpc_lpc.wav")

# LPC parameters
LPC_ORDER = 12  # typical for speech/music formant modeling
FRAME_SIZE = 1024  # samples per analysis frame
HOP_SIZE = 512  # hop between frames


def read_wav(path):
    """Read WAV file as float32 array."""
    with wave.open(path, 'rb') as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)  # mono mix

    return audio, sr


def write_wav(path, audio, sr):
    """Write float32 array as 16-bit WAV."""
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())


def autocorrelation(signal, max_lag):
    """Compute autocorrelation up to max_lag."""
    n = len(signal)
    result = np.zeros(max_lag + 1)
    for lag in range(max_lag + 1):
        if lag >= n:
            break
        result[lag] = np.sum(signal[:n - lag] * signal[lag:])
    return result


def levinson_durbin(r, order):
    """Solve Yule-Walker equations via Levinson-Durbin recursion."""
    a = np.zeros(order + 1)
    a[0] = 1.0
    e = r[0]

    for i in range(1, order + 1):
        # Compute reflection coefficient
        acc = 0.0
        for j in range(1, i):
            acc += a[j] * r[i - j]
        k = -(r[i] + acc) / e if abs(e) > 1e-10 else 0.0

        # Update coefficients
        a_new = a.copy()
        for j in range(1, i):
            a_new[j] = a[j] + k * a[i - j]
        a_new[i] = k
        a = a_new

        # Update error
        e = (1 - k * k) * e
        if abs(e) < 1e-10:
            break

    return a, e


def lpc_analysis_synthesis(audio, sr, lpc_order=12, frame_size=1024, hop_size=512):
    """
    Analyze audio frame-by-frame, extract LPC coefficients,
    then resynthesize through all-pole filter.
    """
    n_samples = len(audio)
    output = np.zeros(n_samples)

    # Window function (Hamming)
    window = np.hamming(frame_size)

    # Process frame by frame
    n_frames = (n_samples - frame_size) // hop_size + 1

    for frame_idx in range(n_frames):
        start = frame_idx * hop_size
        end = start + frame_size

        if end > n_samples:
            break

        # Extract and window frame
        frame = audio[start:end] * window

        # Autocorrelation
        r = autocorrelation(frame, lpc_order)

        # Levinson-Durbin to get LPC coefficients
        a, error = levinson_durbin(r, lpc_order)

        # Resynthesize through all-pole filter: H(z) = 1 / A(z)
        # Use scipy-like filter implementation (direct form II)
        # y[n] = -a[1]*y[n-1] - a[2]*y[n-2] - ... + x[n]
        filtered = np.zeros(frame_size)
        for n in range(frame_size):
            acc = frame[n]
            for i in range(1, lpc_order + 1):
                if n - i >= 0:
                    acc -= a[i] * filtered[n - i]
            filtered[n] = acc

        # Overlap-add synthesis
        output[start:end] += filtered * window

    # Normalize
    max_val = np.max(np.abs(output))
    if max_val > 0:
        output = output / max_val * 0.95

    return output


def main():
    if not os.path.exists(INPUT_WAV):
        raise SystemExit(f"Input WAV not found: {INPUT_WAV}")

    print(f"Reading {INPUT_WAV}...")
    audio, sr = read_wav(INPUT_WAV)
    print(f"  Sample rate: {sr} Hz, Duration: {len(audio)/sr:.2f}s")

    print(f"Applying LPC analysis/synthesis (order={LPC_ORDER})...")
    output = lpc_analysis_synthesis(audio, sr, LPC_ORDER, FRAME_SIZE, HOP_SIZE)

    print(f"Writing {OUTPUT_WAV}...")
    os.makedirs(os.path.dirname(OUTPUT_WAV), exist_ok=True)
    write_wav(OUTPUT_WAV, output, sr)

    size = os.path.getsize(OUTPUT_WAV)
    print(f"OK: {OUTPUT_WAV} ({size} bytes)")


if __name__ == "__main__":
    main()
