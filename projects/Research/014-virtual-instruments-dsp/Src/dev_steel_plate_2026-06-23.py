#!/usr/bin/env python3
"""
Daily DSP Research - Virtual Instrument: Resonant Steel Pan/Plate
Date: 2026-06-23
Technique: Physical modeling via comb filter + resonant bandpass bank
Target: Inharmonic metallic plate partials struck by mallet excitation
"""

import numpy as np
from scipy.signal import butter, sosfilt, lfilter
from scipy.io.wavfile import write as wav_write
import soundfile as sf
import struct, os, subprocess

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SR = 44100
BPM = 120
BEATS = 8  # 2 bars of 4/4
SECONDS = (BEATS * 4 * 60.0) / BPM  # 16 beats @120 = 8 seconds
LEN = int(SR * SECONDS)
T = np.arange(LEN) / SR

# ---------------------------------------------------------------------------
# 1. PLATE MODEL - Inharmonic partials (rectangular steel plate)
# ---------------------------------------------------------------------------
F0 = 220.0  # fundamental (A3)

# Inharmonic ratios for a free rectangular plate (modal series)
PARTIAL_RATIOS = np.array([
    1.0,       # (1,1) fundamental
    2.76,      # (1,2)
    3.0,       # (2,1)
    5.4,       # (2,2)
    5.8,       # (1,3)
    6.7,       # (3,1)
    8.9,       # (2,3)
    9.2,       # (3,2)
    12.2,      # (1,4)
    13.3,      # (3,3)
    16.2,      # (2,4)
])

PARTIAL_FREQS = F0 * PARTIAL_RATIOS
# Q factors — higher Q for lower partials (more resonance), lower Q higher up
PARTIAL_QS = np.array([120, 100, 95, 85, 70, 65, 55, 50, 40, 35, 30])
# Amplitude weights — fundamental strongest, decreasing irregularly (like real plate)
PARTIAL_GAINS = np.array([0.9, 0.6, 0.5, 0.35, 0.25, 0.2, 0.15, 0.12, 0.08, 0.06, 0.04])

N_PARTIALS = len(PARTIAL_FREQS)

# ---------------------------------------------------------------------------
# 2. EXCITATION - Mallet strike (band-limited noise burst)
# ---------------------------------------------------------------------------
def mallet_hit(duration=0.008):
    """Short noise burst with rapid decay — models a hard mallet."""
    n = int(SR * duration)
    noise = np.random.randn(n) * 0.5
    env = np.linspace(1.0, 0.01, n)**2
    return noise * env

# ---------------------------------------------------------------------------
# 3. RESONANT BANDPASS FILTER BANK
# ---------------------------------------------------------------------------
def design_resonant_bp(freq, q, sr=SR):
    """2nd-order resonant bandpass (biquad) at given freq/Q."""
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / (2 * q)
    b0 = alpha
    b1 = 0.0
    b2 = -alpha
    a0 = 1.0 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1.0 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([1.0, a1, a2]) / a0

def apply_biquad(signal, b, a):
    """Apply a biquad filter via direct form I."""
    return lfilter(b, a, signal)

# ---------------------------------------------------------------------------
# 4. COMB FILTER (wave reflections in the plate body)
# ---------------------------------------------------------------------------
def comb_filter(signal, delay_s, feedback=0.75):
    """Feedback comb filter emulating wave reflection in plate."""
    delay_n = int(round(delay_s * SR))
    out = np.zeros_like(signal)
    for n in range(len(signal)):
        out[n] = signal[n] + feedback * (out[n - delay_n] if n >= delay_n else 0.0)
    return out

# ---------------------------------------------------------------------------
# 5. ADSR ENVELOPE
# ---------------------------------------------------------------------------
def adsr_envelope(length, atk=0.002, dec=0.15, sus_level=0.15, rel=1.2):
    """Generate ADSR envelope."""
    env = np.zeros(length)
    a_len = int(atk * SR)
    d_len = int(dec * SR)
    r_len = int(rel * SR)
    
    # Attack
    env[:a_len] = np.linspace(0, 1.0, a_len)
    # Decay to sustain
    d_end = min(a_len + d_len, length)
    env[a_len:d_end] = np.linspace(1.0, sus_level, d_end - a_len)
    # Sustain
    r_start = max(0, length - r_len)
    env[d_end:r_start] = sus_level
    # Release
    if r_start > d_end:
        env[r_start:] = np.linspace(sus_level, 0.0, r_len)
    return env

# ---------------------------------------------------------------------------
# 6. NOTE PATTERN (2-bar melody at 120 BPM)
# ---------------------------------------------------------------------------
# Notes in Hz: A3=220, B3=247, C#4=277, D4=294, E4=330, F#4=370, G#4=415, A4=440
NOTES = [220, 247, 277, 294, 330, 370, 415, 440]
NOTE_NAMES = ['A3', 'B3', 'C#4', 'D4', 'E4', 'F#4', 'G#4', 'A4']

# 2-bar melodic pattern: (note_index, start_beat, duration_beats)
PATTERN = [
    (0, 0, 1.0),   # A3
    (2, 1, 0.5),   # C#4
    (4, 1.5, 0.5), # E4
    (5, 2, 1.0),   # F#4
    (4, 3, 0.5),   # E4
    (2, 3.5, 0.5), # C#4
    (0, 4, 0.75),  # A3
    (6, 4.75, 0.25),# G#4 (grace)
    (7, 5, 1.0),   # A4
    (5, 6, 0.5),   # F#4
    (4, 6.5, 0.5), # E4
    (2, 7, 1.0),   # C#4
]

BEAT_SEC = 60.0 / BPM  # 0.5s per beat

# ---------------------------------------------------------------------------
# 7. RENDER ENGINE
# ---------------------------------------------------------------------------
def render_note(freq_hz, duration_s):
    """Render a single note of the steel plate at given frequency."""
    n_samples = int(duration_s * SR)
    if n_samples <= 0:
        return np.array([])
    
    # Scale partials to the note frequency
    freqs = freq_hz * PARTIAL_RATIOS
    gains = PARTIAL_GAINS.copy()
    
    # Excitation
    exc = mallet_hit(0.006)
    exc_padded = np.zeros(n_samples)
    exc_len = min(len(exc), n_samples)
    exc_padded[:exc_len] = exc[:exc_len]
    
    # Sum of resonant bandpass outputs
    out = np.zeros(n_samples)
    for i in range(N_PARTIALS):
        b, a = design_resonant_bp(freqs[i], PARTIAL_QS[i])
        filtered = apply_biquad(exc_padded, b, a)
        out += filtered * gains[i] * 0.15
    
    # Comb filter for body resonance (delay = 1/freq)
    out = comb_filter(out, 1.0 / freq_hz, feedback=0.65)
    
    # ADSR envelope
    env = adsr_envelope(n_samples, atk=0.001, dec=0.3, sus_level=0.08, rel=max(duration_s - 0.3, 0.3))
    out = out * env
    
    return out

def render_pattern(pattern, note_freqs):
    """Mix all notes in pattern into single buffer."""
    total_n = LEN
    mix = np.zeros(total_n)
    
    for note_idx, start_beat, dur_beats in pattern:
        freq = note_freqs[note_idx]
        start_s = start_beat * BEAT_SEC
        dur_s = dur_beats * BEAT_SEC
        start_n = int(start_s * SR)
        
        note = render_note(freq, dur_s)
        note_len = min(len(note), total_n - start_n)
        if note_len > 0:
            mix[start_n:start_n + note_len] += note[:note_len]
    
    # Normalize
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.95
    return mix

# ---------------------------------------------------------------------------
# 8. EXPORT
# ---------------------------------------------------------------------------
out_dir = "/opt/data/projects/Genres/Research/virtual_instruments"
os.makedirs(out_dir, exist_ok=True)
date_str = "2026-06-23"
base = f"{out_dir}/dev_steel_plate_{date_str}"

print("Rendering steel plate instrument...")
audio = render_pattern(PATTERN, NOTES)

# WAV (16-bit)
wav_path = base + ".wav"
audio_int16 = np.int16(audio * 32767)
wav_write(wav_path, SR, audio_int16)
print(f"  WAV: {wav_path}")

# OGG (via soundfile)
ogg_path = base + ".ogg"
sf.write(ogg_path, audio, SR, format='OGG', subtype='VORBIS')
print(f"  OGG: {ogg_path}")

# Opus via ffmpeg
opus_path = base + ".opus"
subprocess.run([
    "ffmpeg", "-y", "-i", wav_path,
    "-c:a", "libopus", "-b:a", "128k",
    opus_path
], capture_output=True)
print(f"  Opus: {opus_path}")

# MIDI file
midi_path = base + ".mid"

def write_midi(path, pattern, note_freqs, bpm):
    """Write a simple MIDI file from the pattern data."""
    # Reference: A4=440 => MIDI 69
    def freq_to_midi(f):
        return int(round(69 + 12 * np.log2(f / 440.0)))
    
    # MIDI file constants
    ticks_per_beat = 480
    tempo_us = int(60_000_000 / bpm)
    
    # Track events
    events = []
    tick = 0
    
    for note_idx, start_beat, dur_beats in pattern:
        midi_note = freq_to_midi(note_freqs[note_idx])
        start_tick = int(start_beat * ticks_per_beat)
        dur_ticks = int(dur_beats * ticks_per_beat)
        events.append((start_tick, 'on', midi_note, 100))
        events.append((start_tick + dur_ticks, 'off', midi_note, 0))
    
    events.sort()
    
    # Build MIDI binary
    track_data = bytearray()
    track_data.extend(b'\x00\xff\x51\x03')
    track_data.extend(tempo_us.to_bytes(3, 'big'))
    
    last_tick = 0
    for evt_tick, evt_type, note, vel in events:
        delta = evt_tick - last_tick
        # Variable length delta
        if delta < 128:
            track_data.append(delta)
        elif delta < 16384:
            track_data.append((delta >> 7) | 0x80)
            track_data.append(delta & 0x7F)
        else:
            track_data.append((delta >> 14) | 0x80)
            track_data.append(((delta >> 7) & 0x7F) | 0x80)
            track_data.append(delta & 0x7F)
        
        if evt_type == 'on':
            track_data.extend([0x90, note, vel])
        else:
            track_data.extend([0x80, note, vel])
        last_tick = evt_tick
    
    # End of track
    track_data.extend([0x00, 0xff, 0x2f, 0x00])
    
    # MIDI header + track chunk
    track_len = len(track_data)
    midi_bytes = bytearray()
    midi_bytes.extend(b'MThd')
    midi_bytes.extend((6).to_bytes(4, 'big'))  # header length
    midi_bytes.extend((1).to_bytes(2, 'big'))   # format 1
    midi_bytes.extend((1).to_bytes(2, 'big'))   # 1 track
    midi_bytes.extend(ticks_per_beat.to_bytes(2, 'big'))
    midi_bytes.extend(b'MTrk')
    midi_bytes.extend(track_len.to_bytes(4, 'big'))
    midi_bytes.extend(track_data)
    
    with open(path, 'wb') as f:
        f.write(midi_bytes)

write_midi(midi_path, PATTERN, NOTES, BPM)
print(f"  MIDI: {midi_path}")

# ---------------------------------------------------------------------------
# 9. METRICS REPORT
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("STEEL PLATE INSTRUMENT — DSP METRICS")
print("="*60)
print(f"\nExcitation: Mallet strike (band-limited noise burst, 6ms)")
print(f"Body model: Feedback comb filter + resonant BP filter bank")
print(f"\nFundamental: {F0} Hz (A3)")
print(f"\nResonant Partial Bank:")
print(f"{'#':>3} {'Freq (Hz)':>10} {'Ratio':>7} {'Q Factor':>8} {'Gain':>5}")
print("-"*38)
for i in range(N_PARTIALS):
    print(f"{i+1:>3} {PARTIAL_FREQS[i]:>10.1f} {PARTIAL_RATIOS[i]:>7.2f} {PARTIAL_QS[i]:>8.1f} {PARTIAL_GAINS[i]:>5.2f}")

print(f"\nComb Filter:")
print(f"  Delay: 1/F0 = {1/F0:.4f}s ({int(round(SR/F0))} samples)")
print(f"  Feedback: 0.65 (metallic sustain)")

print(f"\nADSR Envelope:")
print(f"  Attack:  0.001s")
print(f"  Decay:   0.30s")
print(f"  Sustain: 0.08")
print(f"  Release: note-dependent (>=0.3s)")

print(f"\nMelodic Pattern ({BPM} BPM, {BEATS} beats):")
for note_idx, start_beat, dur_beats in PATTERN:
    name = NOTE_NAMES[note_idx]
    freq = NOTES[note_idx]
    print(f"  Beat {start_beat:>4.1f}: {name:>4s} ({freq:>3.0f} Hz) x {dur_beats:.2f} beats")

print(f"\nFiles Exported:")
for ext in ['wav', 'ogg', 'opus', 'mid']:
    print(f"  {base}.{ext}")

# Verify file sizes
for ext in ['wav', 'ogg', 'opus', 'mid']:
    fpath = f"{base}.{ext}"
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        print(f"  Size: {size / 1024:.1f} KB")