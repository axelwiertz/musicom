#!/usr/bin/env python3
"""
Daily DSP Research — Virtual Instrument: Resonant Metal Plate (Physical Model)
Date: 2026-06-21
Target: Simulate struck metal plate with sympathetic body resonance coupling.
Architecture: Multi-mode resonant bandpass filters + comb filter body coupling
             + impact excitation model + ADSR envelope shaping.
No vocal formants, no speech synthesis. Pure subtractive/physical model.
"""

import numpy as np
import soundfile as sf
from scipy import signal, fft
import struct
import json
import os
import sys

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
SAMPLE_RATE = 48000
BPM = 120
SECONDS_PER_BEAT = 60.0 / BPM
BARS = 2
BEATS_PER_BAR = 4
TOTAL_BEATS = BARS * BEATS_PER_BAR
TOTAL_SECONDS = TOTAL_BEATS * SECONDS_PER_BEAT
N_SAMPLES = int(TOTAL_SECONDS * SAMPLE_RATE)
T = np.linspace(0, TOTAL_SECONDS, N_SAMPLES, endpoint=False)

# Output base name
OUT_BASE = "/opt/data/projects/Genres/Research/virtual_instruments/resonant_plate_2026-06-21"

# ──────────────────────────────────────────────
# METAL PLATE PHYSICAL PARAMETERS
# ──────────────────────────────────────────────
# A clamped metal plate has inharmonic overtones.
# Ratio approximation for a square plate (Chladni patterns):
# f_ratio ≈ [1.0, 1.59, 2.14, 2.30, 2.65, 3.16, 3.60, 4.08]
PLATE_FUNDAMENTAL = 131.0  # C3 — plate resonant base

plate_ratios = np.array([1.0, 1.59, 2.14, 2.30, 2.65, 3.16, 3.60, 4.08, 4.68, 5.25])
plate_freqs = PLATE_FUNDAMENTAL * plate_ratios

# Q factors — metal plates have moderate to high Q on low modes, lower on high
plate_Q = np.array([80.0, 65.0, 50.0, 42.0, 35.0, 28.0, 22.0, 18.0, 15.0, 12.0])

# Mode amplitudes (relative strike excitation strength)
plate_amps = np.array([1.0, 0.85, 0.55, 0.40, 0.25, 0.18, 0.10, 0.07, 0.04, 0.02])

# ──────────────────────────────────────────────
# BUILD RESONANT BANDPASS FILTER BANK
# ──────────────────────────────────────────────
def design_resonant_bpf(freq, Q, sr, order=2):
    """Design a resonant 2nd-order bandpass filter (peaking EQ topology)."""
    w0 = 2.0 * np.pi * freq / sr
    alpha = np.sin(w0) / (2.0 * Q)
    b = np.array([alpha, 0.0, -alpha])
    a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])
    # Normalize for unity gain at center
    gain_correction = 1.0 / (alpha / (1.0 + alpha))
    return b, a, gain_correction

# Build filter bank
filter_bank = []
for i in range(len(plate_freqs)):
    b, a, gain = design_resonant_bpf(plate_freqs[i], plate_Q[i], SAMPLE_RATE)
    filter_bank.append((b.copy(), a.copy(), gain))

# ──────────────────────────────────────────────
# COMB FILTER — BODY COUPLING
# ──────────────────────────────────────────────
# Feedback comb simulates wave reflections in the plate body.
# Delay in samples = sample_rate / frequency_of_body_resonance
BODY_RESONANCE_FREQ = 43.0  # Low body hum ~43 Hz (approx F1)
COMB_DELAY = int(SAMPLE_RATE / BODY_RESONANCE_FREQ)
COMB_FEEDBACK = 0.82  # Feedback gain — determines resonance decay
COMB_DAMPING = 0.15   # High-frequency damping per tap

# ──────────────────────────────────────────────
# IMPACT EXCITATION (STRIKE MODEL)
# ──────────────────────────────────────────────
def generate_strike_envelope(duration_sec, sr, hardness=5.0):
    """Physical strike: fast attack, exponential decay.
       hardness > 1 = harder mallet (more high freq content)."""
    n = int(duration_sec * sr)
    env = np.exp(-hardness * np.linspace(0, 10, n))
    env /= np.max(env)  # normalize to 1.0
    return env

def generate_strike_noise(n_samples, sr, density=0.3):
    """Impact noise burst — models mallet contact."""
    noise = np.random.randn(n_samples)
    # Shape with rapid decay
    env = np.exp(-density * np.linspace(0, 15, n_samples))
    return noise * env

# ──────────────────────────────────────────────
# ADSR ENVELOPE
# ──────────────────────────────────────────────
def adsr_envelope(n_samples, sr, attack_s, decay_s, sustain_level, release_s, gate_fraction=1.0):
    """Generate ADSR envelope."""
    n_attack = int(attack_s * sr)
    n_decay = int(decay_s * sr)
    n_gate = int(n_samples * gate_fraction)
    n_release = int(release_s * sr)
    n_sustain = n_gate - n_attack - n_decay
    n_release_actual = min(n_release, n_samples - n_gate)

    env = np.zeros(n_samples)

    # Attack
    if n_attack > 0:
        env[:n_attack] = np.linspace(0.0, 1.0, n_attack)

    # Decay
    if n_decay > 0:
        env[n_attack:n_attack+n_decay] = np.linspace(1.0, sustain_level, n_decay)

    # Sustain
    if n_sustain > 0:
        env[n_attack+n_decay:n_gate] = sustain_level

    # Release
    if n_release_actual > 0 and n_gate < n_samples:
        env[n_gate:n_gate+n_release_actual] = np.linspace(
            sustain_level, 0.0, n_release_actual
        )

    return env

# ──────────────────────────────────────────────
# MELODY PATTERN — 2 bars, 8 beats
# ──────────────────────────────────────────────
# Notes: C3, Eb3, G3, Bb3, C4, Ab3, F3, D3 (vs. baseline plate fundamental)
# Each note is played as a struck plate with pitch shift via resampling
melody_pitches_hz = np.array([131.0, 155.6, 196.0, 233.1, 261.6, 207.7, 174.6, 146.8])
melody_durations = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])  # in beats
n_notes = len(melody_pitches_hz)

# ──────────────────────────────────────────────
# SYNTHESIS ENGINE
# ──────────────────────────────────────────────
def synthesize_note(pitch_hz, duration_beats, sr, bpm):
    """Synthesize a single struck plate note at given pitch."""
    dur_sec = duration_beats * (60.0 / bpm)
    n = int(dur_sec * sr)
    if n <= 0:
        return np.zeros(0)

    # Pitch ratio relative to plate fundamental
    pitch_ratio = pitch_hz / PLATE_FUNDAMENTAL

    # 1. Generate impact excitation
    strike_dur = min(0.015, dur_sec * 0.3)  # 15ms strike
    strike_env = generate_strike_envelope(strike_dur, sr, hardness=8.0)
    strike_noise = generate_strike_noise(int(strike_dur * sr), sr, density=0.4)

    # 2. Excite a short noise burst into the filter bank
    excitation = np.zeros(n)
    exc_len = min(len(strike_noise), n)
    excitation[:exc_len] = strike_noise[:exc_len] * strike_env[:exc_len]

    # 3. Run through resonant filter bank (each mode)
    output = np.zeros(n)
    for i, (b, a, gain) in enumerate(filter_bank):
        # Scale pitch ratio into the filter frequencies
        # We shift the filter excitation by resampling
        ratio = pitch_ratio * plate_ratios[i]
        if ratio > 0.25 and ratio < 4.0:  # reasonable range
            # Apply amplitude weighting
            amp = plate_amps[i]
            # Filter the excitation through this resonant mode
            mode_signal = signal.lfilter(b * gain, a, excitation) * amp
            output += mode_signal

    # 4. Apply comb filter body coupling
    comb_buffer = np.zeros(COMB_DELAY)
    comb_output = np.zeros(n)
    for i in range(n):
        tap = comb_buffer[i % COMB_DELAY]
        comb_output[i] = output[i] + tap * COMB_FEEDBACK
        comb_buffer[i % COMB_DELAY] = output[i] + tap * COMB_DAMPING
    output = comb_output

    # 5. Apply ADSR envelope
    env = adsr_envelope(
        n, sr,
        attack_s=0.002,    # 2ms — percussive
        decay_s=0.08,      # 80ms
        sustain_level=0.15,
        release_s=0.5,     # 500ms
        gate_fraction=0.95
    )
    output *= env

    # 6. Normalize per note
    peak = np.max(np.abs(output))
    if peak > 0:
        output *= 0.5 / peak

    return output

# ──────────────────────────────────────────────
# RENDER FULL PATTERN
# ──────────────────────────────────────────────
print("=== Resonant Metal Plate Physical Model ===")
print(f"Sample Rate: {SAMPLE_RATE} Hz")
print(f"Pattern: {BARS} bars, {TOTAL_BEATS} beats @ {BPM} BPM")
print(f"Plate Fundamental: {PLATE_FUNDAMENTAL:.1f} Hz")
print(f"Body Resonance: {BODY_RESONANCE_FREQ:.1f} Hz")
print("")

full_audio = np.zeros(N_SAMPLES)
current_sample = 0

for idx in range(n_notes):
    pitch = melody_pitches_hz[idx]
    dur_beats = melody_durations[idx]
    note_samples = int(dur_beats * SECONDS_PER_BEAT * SAMPLE_RATE)

    if current_sample + note_samples > N_SAMPLES:
        note_samples = N_SAMPLES - current_sample
    if note_samples <= 0:
        break

    print(f"  Note {idx + 1}/{n_notes}: pitch={pitch:.1f} Hz, "
          f"duration={dur_beats:.2f} beats ({dur_beats * SECONDS_PER_BEAT:.2f}s)")
    note_audio = synthesize_note(pitch, dur_beats, SAMPLE_RATE, BPM)
    actual_len = min(len(note_audio), note_samples)
    full_audio[current_sample:current_sample + actual_len] += note_audio[:actual_len]
    current_sample += note_samples

# Normalize master
peak = np.max(np.abs(full_audio))
if peak > 0:
    full_audio *= 0.95 / peak
print(f"\nMaster peak: {peak:.4f} → normalized to 0.95")

# ──────────────────────────────────────────────
# ANALYSIS: RESONANT PEAK DETECTION
# ──────────────────────────────────────────────
print("\n--- Spectral Analysis ---")

# Compute FFT of the full mix
window = np.hanning(N_SAMPLES)
fft_data = fft.rfft(full_audio * window)
fft_mag = np.abs(fft_data)
fft_freqs = fft.rfftfreq(N_SAMPLES, 1.0 / SAMPLE_RATE)

# Find peaks in spectrum
from scipy.signal import find_peaks
peak_indices, peak_properties = find_peaks(
    fft_mag,
    height=np.max(fft_mag) * 0.02,
    distance=int(SAMPLE_RATE / 500),  # min 5 Hz apart
    prominence=np.max(fft_mag) * 0.01
)

# Top peaks by magnitude
top_peaks = sorted(zip(fft_freqs[peak_indices], fft_mag[peak_indices]),
                   key=lambda x: x[1], reverse=True)[:10]

print("\nResonant Peaks (top 10):")
peak_metrics = []
for freq, mag in top_peaks:
    # Estimate Q from -3dB bandwidth around peak
    peak_idx = np.argmin(np.abs(fft_freqs - freq))
    half_power = mag / np.sqrt(2)
    # Search left and right for -3dB points
    left_idx = peak_idx
    while left_idx > 0 and fft_mag[left_idx] > half_power:
        left_idx -= 1
    right_idx = peak_idx
    while right_idx < len(fft_mag) - 1 and fft_mag[right_idx] > half_power:
        right_idx += 1
    bw = fft_freqs[right_idx] - fft_freqs[left_idx]
    q_est = freq / bw if bw > 0 else 0
    peak_metrics.append((freq, q_est, mag))
    print(f"  f={freq:7.2f} Hz   Q≈{q_est:6.1f}   mag={mag:.2e}")

# ──────────────────────────────────────────────
# EXPORT: WAV & OPUS
# ──────────────────────────────────────────────
print("\n--- Export ---")

# WAV (48kHz 24-bit)
wav_path = f"{OUT_BASE}.wav"
sf.write(wav_path, full_audio, SAMPLE_RATE, subtype='PCM_24')
print(f"WAV: {wav_path}")

# OGG / Opus via ffmpeg
ogg_path = f"{OUT_BASE}.ogg"
opus_path = f"{OUT_BASE}.opus"

# Write temp WAV for conversion
os.system(f"ffmpeg -y -i {wav_path} -c:a libvorbis -q:a 6 {ogg_path} 2>/dev/null")
print(f"OGG: {ogg_path}")

os.system(f"ffmpeg -y -i {wav_path} -c:a libopus -b:a 128k {opus_path} 2>/dev/null")
print(f"Opus: {opus_path}")

# ──────────────────────────────────────────────
# MIDI EXPORT
# ──────────────────────────────────────────────
def write_midi_file(melody_hz, durations_beats, bpm, filename):
    """Write a MIDI file from pitch and duration data."""
    try:
        from mido import Message, MidiFile, MidiTrack, MetaMessage
        has_mido = True
    except ImportError:
        has_mido = False

    # Note numbers from Hz
    note_numbers = []
    for hz in melody_hz:
        nn = int(69 + 12 * np.log2(hz / 440.0))
        nn = max(12, min(108, nn))
        note_numbers.append(nn)

    if has_mido:
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        ticks_per_beat = 480
        track.append(MetaMessage('set_tempo', tempo=int(60_000_000 / bpm)))
        track.append(MetaMessage('time_signature', numerator=4, denominator=4))

        velocity = 100
        for i, (nn, dur_beats) in enumerate(zip(note_numbers, durations_beats)):
            delta_ticks = int(dur_beats * ticks_per_beat)
            track.append(Message('note_on', note=nn, velocity=velocity, time=0))
            track.append(Message('note_off', note=nn, velocity=0, time=delta_ticks))

        mid.save(filename)
        return True
    else:
        # Fallback: write raw MIDI binary
        ticks_per_beat = 480
        tempo_us = int(60_000_000 / bpm)
        with open(filename, 'wb') as f:
            # Header
            f.write(b'MThd')
            f.write(struct.pack('>I', 6))
            f.write(struct.pack('>HHH', 1, 1, ticks_per_beat))
            # Track
            track_data = bytearray()
            # Tempo
            track_data.extend(struct.pack('>B', 0))  # delta
            track_data.extend(b'\xFF\x51\x03')
            track_data.extend(struct.pack('>I', tempo_us)[1:])  # 3 bytes
            # Time signature
            track_data.extend(struct.pack('>B', 0))
            track_data.extend(b'\xFF\x58\x04\x04\x02\x18\x08')
            # Notes
            for i, (nn, dur_beats) in enumerate(zip(note_numbers, durations_beats)):
                delta = 0 if i == 0 else int(melody_durations[i-1] * ticks_per_beat)
                delta = min(delta, 0x7F)  # simple single-byte, small enough
                track_data.extend(struct.pack('>BBB', delta, 0x90, nn, 100))
                dur_ticks = int(dur_beats * ticks_per_beat)
                dur_ticks = min(dur_ticks, 0x7F)
                track_data.extend(struct.pack('>BBB', dur_ticks, 0x80, nn, 0))
            # End of track
            track_data.extend(b'\x00\xFF\x2F\x00')
            track_len = len(track_data)
            f.write(b'MTrk')
            f.write(struct.pack('>I', track_len))
            f.write(track_data)
        return True

midi_path = f"{OUT_BASE}.mid"
write_midi_file(melody_pitches_hz, melody_durations, BPM, midi_path)
print(f"MIDI: {midi_path}")

# ──────────────────────────────────────────────
# SYSTEM GRAPH REPORT
# ──────────────────────────────────────────────
print("\n\n=== SYSTEM GRAPH: RESONANT METAL PLATE ===")
print("=" * 60)
print("\nSIGNAL FLOW:")
print("  Mallet Strike (noise burst + impact env)")
print("    ↓")
print("  Resonant BPF Bank (10 modes)")
print("    ├─ Mode 1:  {:.1f} Hz  Q={:.0f}  amp={:.2f}".format(
    plate_freqs[0], plate_Q[0], plate_amps[0]))
for i in range(1, min(6, len(plate_freqs))):
    print("    ├─ Mode {}: {:.1f} Hz  Q={:.0f}  amp={:.2f}".format(
        i+1, plate_freqs[i], plate_Q[i], plate_amps[i]))
print("    ├─ ... ({} more modes)".format(len(plate_freqs) - 6))
print("    ↓")
print("  Comb Filter Body Coupling")
print("    ├─ Delay: {} samples ({:.1f} Hz)".format(COMB_DELAY, BODY_RESONANCE_FREQ))
print("    ├─ Feedback: {:.2f}".format(COMB_FEEDBACK))
print("    └─ Damping: {:.2f}".format(COMB_DAMPING))
print("    ↓")
print("  ADSR Envelope")
print("    ├─ Attack:  2 ms")
print("    ├─ Decay:  80 ms")
print("    ├─ Sustain: 0.15")
print("    └─ Release: 500 ms")
print("    ↓")
print("  OUTPUT (normalized to 0.95 peak)")

print("\nFILTER COEFFICIENTS (selected modes):")
for i in [0, 1, 2, 5]:
    b, a, gain = filter_bank[i]
    print("  Mode {} ({:.1f} Hz, Q={:.0f}):".format(i+1, plate_freqs[i], plate_Q[i]))
    print("    b = [{:.6f}, {:.6f}, {:.6f}]".format(b[0], b[1], b[2]))
    print("    a = [{:.6f}, {:.6f}, {:.6f}]".format(a[0], a[1], a[2]))
    print("    gain correction = {:.4f}".format(gain))

print("\nMELODY PATTERN (2 bars):")
for i in range(n_notes):
    print("  Beat {:2d}: note={:.1f} Hz  (MIDI nn={:d})  dur={:.1f} beats".format(
        i, melody_pitches_hz[i],
        int(69 + 12 * np.log2(melody_pitches_hz[i] / 440.0)),
        melody_durations[i]))

print("\nDETECTED RESONANT PEAKS:")
print("  {:>8s}  {:>8s}  {:>10s}".format("Freq(Hz)", "Q-factor", "Magnitude"))
for freq, q_val, mag in peak_metrics[:8]:
    print("  {:8.2f}  {:8.1f}  {:10.2e}".format(freq, q_val, mag))

print("\nEXPORTED FILES:")
for ext in ['wav', 'ogg', 'opus', 'mid']:
    path = f"{OUT_BASE}.{ext}"
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  {ext.upper():4s}: {path}  ({size:,} bytes)")

print("=" * 60)
print("END REPORT")