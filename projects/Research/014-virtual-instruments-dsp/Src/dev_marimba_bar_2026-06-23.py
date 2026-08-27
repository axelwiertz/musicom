#!/usr/bin/env python3
"""
dev_marimba_bar_2026-06-23.py — Wooden Marimba Bar with Resonator Tube
==========================================================================
Daily DSP Research Experiment (2026-06-23)

Physical model of a rosewood marimba bar coupled to an acoustic resonator tube.
Key physics: inharmonic bar partials (f1 ~ 1, f2 ~ 4, f3 ~ 9.5, f4 ~ 17.5),
tuned resonator below each bar, mallet strike excitation with velocity scaling.

STRICT DIRECTION: No vocal formants, no speech synthesis, no human voice modeling.
This is a purely physical/subtractive instrument structure.

METRICS TRACKED:
  - Resonant peak frequencies (f1..f4) per note
  - Quality factor (Q) per partial
  - ADSR envelope parameters
  - Resonator tube tuning frequency
"""

import numpy as np
import soundfile as sf
import scipy.signal as signal
import struct
import wave
import json
import os
from datetime import date

# ─── Constants ───────────────────────────────────────────────────────────────
SAMPLE_RATE = 48000
DURATION = 4.0  # seconds (2 bars at 120 BPM ≈ 4 sec)
N_SAMPLES = int(SAMPLE_RATE * DURATION)
BPM = 120
BEATS_PER_BAR = 4
SECONDS_PER_BEAT = 60.0 / BPM

# ─── Instrument Definition: Marimba Bar ──────────────────────────────────────
class MarimbaBarPhysicalModel:
    """
    Physical model of a struck wooden bar with under-tuned resonator tube.
    
    Bar partials follow the relationship for a free-free rectangular bar:
      f_n = f_1 * ( (2n+1)² * π² / 4.73² )  (approximately)
    Simplified: f1, f2≈4*f1, f3≈9.5*f1, f4≈17.5*f1
    
    Each partial has:
      - Independent amplitude (higher partials quieter)
      - Independent decay time (higher partials decay faster; metallic)
      - Quality factor Q = π * f_n * τ (where τ = decay time constant)
    
    Resonator tube: quarter-wave tube tuned slightly below f1,
    modeled as a resonant bandpass filter with high Q.
    """
    
    def __init__(self, fundamental=440.0, bar_material='rosewood'):
        # ─── Bar partials ────────────────────────────────────────────────
        self.f1 = fundamental
        # Inharmonic ratios for a marimba bar (empirical)
        if bar_material == 'rosewood':
            ratio = [1.0, 4.0, 9.5, 17.5, 27.0]
            amp_ratio = [1.0, 0.45, 0.18, 0.07, 0.03]
            decay_ratio = [1.0, 0.6, 0.35, 0.2, 0.1]  # relative decay times
        else:  # synthetic default
            ratio = [1.0, 3.9, 9.3, 17.2, 26.5]
            amp_ratio = [1.0, 0.40, 0.15, 0.05, 0.02]
            decay_ratio = [1.0, 0.55, 0.30, 0.15, 0.08]
        
        self.partials = []
        for i in range(5):
            self.partials.append({
                'freq': self.f1 * ratio[i],
                'amp': amp_ratio[i],
                'decay_time': 1.0 * decay_ratio[i],  # seconds (T60)
            })
        
        # ─── Resonator tube ──────────────────────────────────────────────
        # Quarter-wave tube: tube_length = c / (4 * f_res)
        # Tuned ~5% below f1 for classic marimba warmth
        self.res_freq = self.f1 * 0.95
        self.res_Q = 25.0  # High Q for resonant tube
        
        # ─── ADSR envelope (mallet strike) ───────────────────────────────
        self.adsr = {
            'attack': 0.001,   # 1ms — very fast (mallet impact)
            'decay': 0.02,     # 20ms
            'sustain': 0.2,    # sustain level (relative)
            'release': 0.15,   # 150ms release
        }
        
        # ─── Mallet parameters ───────────────────────────────────────────
        self.mallet_hardness = 0.7  # 0=soft yarn, 1=hard poly
        
    def generate_note(self, duration_sec, velocity=0.8):
        """Generate a single marimba note with bar + resonator physics."""
        n_samples = int(SAMPLE_RATE * duration_sec)
        t = np.arange(n_samples) / SAMPLE_RATE
        
        # ─── Bar partials (additive synthesis with exponential decay) ────
        bar_signal = np.zeros(n_samples, dtype=np.float64)
        
        for p in self.partials:
            # Decay envelope: exponential with T60
            decay_env = np.exp(-3.0 * t / p['decay_time'])  # -60dB at decay_time
            # Partial oscillation
            partial_wave = np.sin(2 * np.pi * p['freq'] * t)
            # Add slight amplitude modulation from bar mode coupling
            amp_mod = 1.0 + 0.05 * np.sin(2 * np.pi * (p['freq'] * 0.01) * t)
            # Combine
            bar_signal += velocity * p['amp'] * decay_env * partial_wave * amp_mod
        
        # ─── Mallet strike transient ─────────────────────────────────────
        # Short noise burst at attack for mallet impact
        mallet_noise = np.random.randn(n_samples).astype(np.float64)
        mallet_env = np.exp(-t / 0.003) * np.exp(-t / 0.003)
        mallet_noise *= mallet_env * velocity * (0.3 + 0.5 * self.mallet_hardness)
        # Band-limit the mallet noise to 8kHz
        sos = signal.butter(4, 8000, btype='low', fs=SAMPLE_RATE, output='sos')
        mallet_noise = signal.sosfilt(sos, mallet_noise)
        
        # ─── ADSR envelope (shapes the overall note) ─────────────────────
        adsr_env = np.ones(n_samples, dtype=np.float64) * self.adsr['sustain']
        a_len = min(int(self.adsr['attack'] * SAMPLE_RATE), n_samples)
        d_len = min(int(self.adsr['decay'] * SAMPLE_RATE), n_samples - a_len)
        r_len = min(int(self.adsr['release'] * SAMPLE_RATE), n_samples - a_len - d_len)
        
        if a_len > 0:
            adsr_env[:a_len] = np.linspace(0, 1.0, a_len)
        if d_len > 0:
            adsr_env[a_len:a_len+d_len] = np.linspace(1.0, self.adsr['sustain'], d_len)
        if r_len > 0 and (a_len + d_len + r_len) <= n_samples:
            release_start = a_len + d_len
            release_end = release_start + r_len
            adsr_env[release_start:release_end] = np.linspace(self.adsr['sustain'], 0, r_len)
        
        # Apply ADSR
        bar_signal *= adsr_env
        mallet_noise *= adsr_env
        
        # ─── Resonator tube (bandpass filter) ────────────────────────────
        # Second-order bandpass at resonator frequency
        Q = self.res_Q
        f0 = self.res_freq
        w0 = 2 * np.pi * f0 / SAMPLE_RATE
        alpha = np.sin(w0) / (2 * Q)
        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        bar_resonated = signal.lfilter(b, a, bar_signal)
        noise_resonated = signal.lfilter(b, a, mallet_noise)
        
        # ─── Mix: bar (60%) + mallet noise (25%) + resonance (15%) ──────
        mix = (0.60 * bar_signal + 0.25 * mallet_noise + 0.15 * bar_resonated)
        
        # Add a touch of harmonic saturation (tube overdrive)
        mix = np.tanh(mix * 1.5) / 1.5
        
        # Normalize
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.95
        
        return mix
    
    def get_metrics(self):
        """Return tracked metrics for the instrument."""
        partials_data = []
        for i, p in enumerate(self.partials):
            Q = np.pi * p['freq'] * p['decay_time']
            partials_data.append({
                'partial': i + 1,
                'frequency_hz': round(p['freq'], 2),
                'amplitude_ratio': round(p['amp'], 4),
                'decay_time_sec': round(p['decay_time'], 4),
                'q_factor': round(Q, 1)
            })
        
        return {
            'instrument': 'Marimba Bar + Resonator Tube',
            'date': str(date.today()),
            'fundamental_hz': round(self.f1, 2),
            'resonator_tube_freq_hz': round(self.res_freq, 2),
            'resonator_tube_Q': self.res_Q,
            'partials': partials_data,
            'adsr': self.adsr,
            'mallet_hardness': self.mallet_hardness,
        }


# ─── Melodic Pattern (2 bars, 4/4 at 120 BPM) ───────────────────────────────
# C major pentatonic: C4 D4 E4 G4 A4 C5
# Pattern: ascending arpeggio with syncopated accent, repeated
NOTES = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63,
    'G4': 392.00, 'A4': 440.00, 'C5': 523.25,
    'B3': 246.94,  # for leading tone
}

# Two-bar pattern: note name, start beat, duration (beats), velocity
PATTERN = [
    # Bar 1: Ascending stroke pattern
    ('C4', 0.0, 0.5, 0.85),
    ('D4', 0.5, 0.5, 0.70),
    ('E4', 1.0, 0.5, 0.80),
    ('G4', 1.5, 0.5, 0.65),
    ('A4', 2.0, 0.75, 0.90),  # accented
    ('C5', 2.75, 0.25, 0.75), # ghost note
    ('E4', 3.0, 0.5, 0.60),
    ('G4', 3.5, 0.5, 0.70),
    
    # Bar 2: Descending with resonance
    ('A4', 4.0, 0.75, 0.88),  # accented
    ('G4', 4.75, 0.25, 0.65),
    ('E4', 5.0, 0.5, 0.75),
    ('D4', 5.5, 0.5, 0.60),
    ('C4', 6.0, 1.0, 0.85),  # held
    ('B3', 7.0, 0.5, 0.50),  # passing tone
    ('C4', 7.5, 0.5, 0.70),  # resolution
]


def generate_melody():
    """Generate the full 2-bar melodic study."""
    total_beats = 8.0  # 2 bars at 4/4
    total_sec = total_beats * SECONDS_PER_BEAT
    n_samples = int(SAMPLE_RATE * total_sec)
    mix = np.zeros(n_samples, dtype=np.float64)
    midi_events = []
    
    # Pre-build instruments for each unique note (cached)
    instr_cache = {}
    
    for note_name, start_beat, dur_beats, velocity in PATTERN:
        start_sec = start_beat * SECONDS_PER_BEAT
        dur_sec = dur_beats * SECONDS_PER_BEAT
        start_sample = int(start_sec * SAMPLE_RATE)
        
        if note_name not in instr_cache:
            freq = NOTES[note_name]
            instr_cache[note_name] = MarimbaBarPhysicalModel(
                fundamental=freq, bar_material='rosewood'
            )
        
        note_audio = instr_cache[note_name].generate_note(dur_sec, velocity)
        end_sample = start_sample + len(note_audio)
        
        if end_sample > n_samples:
            note_audio = note_audio[:n_samples - start_sample]
            end_sample = n_samples
        
        mix[start_sample:end_sample] += note_audio
        
        # MIDI note number
        midi_note = {
            'C4': 60, 'D4': 62, 'E4': 64, 'G4': 67,
            'A4': 69, 'C5': 72, 'B3': 59
        }[note_name]
        midi_events.append({
            'note': midi_note,
            'start_beat': round(start_beat, 2),
            'duration_beats': round(dur_beats, 2),
            'velocity': round(int(velocity * 127)),
        })
    
    # Normalize master mix
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.95
    
    return mix, midi_events, instr_cache


# ─── Export Functions ────────────────────────────────────────────────────────
def export_wav(filename, audio, sr=SAMPLE_RATE):
    """Export 24-bit WAV file."""
    # Normalize to 24-bit range
    audio_int = np.clip(audio * (2**23 - 1), -2**23, 2**23 - 1).astype(np.int32)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(3)  # 24-bit = 3 bytes
        wf.setframerate(sr)
        wf.writeframes(audio_int.tobytes())
    print(f"  WAV: {filename} ({len(audio)/sr:.2f}s, 24-bit)")


def export_ogg_opus(filename_wav, filename_ogg, filename_opus):
    """Convert WAV to OGG/Vorbis and Opus using ffmpeg."""
    import subprocess
    
    # OGG/Vorbis (high quality, q=7)
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', filename_wav, '-c:a', 'libvorbis', '-q:a', '7',
         filename_ogg],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        ogg_size = os.path.getsize(filename_ogg)
        print(f"  OGG: {filename_ogg} ({ogg_size//1024} KB)")
    else:
        print(f"  OGG error: {result.stderr[:200]}")
    
    # Opus (high quality, 192k)
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', filename_wav, '-c:a', 'libopus', '-b:a', '192k',
         filename_opus],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        opus_size = os.path.getsize(filename_opus)
        print(f"  Opus: {filename_opus} ({opus_size//1024} KB)")
    else:
        print(f"  Opus error: {result.stderr[:200]}")


def export_midi(filename, midi_events, bpm=BPM):
    """Export standard MIDI file with melodic events."""
    events = midi_events

    ticks_per_beat = 480
    tempo_us = int(60.0 / bpm * 1_000_000)
    
    with open(filename, 'wb') as f:
        # ─── MIDI header ──────────────────────────────────────────────
        f.write(b'MThd')
        f.write(struct.pack('>I', 6))       # chunk size
        f.write(struct.pack('>HHH', 1,      # format 1
                            1,              # 1 track
                            ticks_per_beat))
        
        # ─── Tempo track ──────────────────────────────────────────────
        f.write(b'MTrk')
        tempo_track_data = bytearray()
        # Tempo meta event
        tempo_track_data.extend(struct.pack('>I', 0))  # delta=0
        tempo_track_data.extend(b'\xFF\x51\x03')
        tempo_track_data.extend(struct.pack('>I', tempo_us)[1:])
        # End of track
        tempo_track_data.extend(struct.pack('>I', 0))
        tempo_track_data.extend(b'\xFF\x2F\x00')
        # Write track size + data
        f.write(struct.pack('>I', len(tempo_track_data)))
        f.write(tempo_track_data)
        
        # ─── Note track ───────────────────────────────────────────────
        f.write(b'MTrk')
        note_track_data = bytearray()
        
        # Program change: marimba (GM #12)
        note_track_data.extend(struct.pack('>I', 0))
        note_track_data.extend(b'\xC0\x0C')  # program 12 = marimba
        
        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e['start_beat'])
        
        current_tick = 0
        
        for ev in sorted_events:
            start_tick = int(ev['start_beat'] * ticks_per_beat)
            dur_ticks = int(ev['duration_beats'] * ticks_per_beat)
            velocity = ev['velocity']
            note = ev['note']
            
            # Delta time to note-on
            delta = start_tick - current_tick
            current_tick = start_tick
            # Write delta as variable-length
            if delta < 128:
                note_track_data.append(delta)
            elif delta < 16384:
                note_track_data.append(0x80 | (delta >> 7))
                note_track_data.append(delta & 0x7F)
            else:
                note_track_data.append(0x80 | (delta >> 14))
                note_track_data.append(0x80 | ((delta >> 7) & 0x7F))
                note_track_data.append(delta & 0x7F)
            
            # Note-on
            note_track_data.extend([0x90, note, velocity])
            
            # Delta to note-off
            delta = dur_ticks
            if delta < 128:
                note_track_data.append(delta)
            elif delta < 16384:
                note_track_data.append(0x80 | (delta >> 7))
                note_track_data.append(delta & 0x7F)
            else:
                note_track_data.append(0x80 | (delta >> 14))
                note_track_data.append(0x80 | ((delta >> 7) & 0x7F))
                note_track_data.append(delta & 0x7F)
            
            # Note-off
            note_track_data.extend([0x90, note, 0x00])
            
            current_tick += dur_ticks
        
        # End of track
        note_track_data.extend(struct.pack('>I', 0))
        note_track_data.extend(b'\xFF\x2F\x00')
        
        f.write(struct.pack('>I', len(note_track_data)))
        f.write(note_track_data)
    
    print(f"  MIDI: {filename} ({len(events)} notes)")


def analyze_spectrum(audio, sr=SAMPLE_RATE):
    """Compute spectral peaks for reporting."""
    n_fft = 4096
    freqs = np.fft.rfftfreq(n_fft, 1/sr)
    spectrum = np.abs(np.fft.rfft(audio[:n_fft]))
    
    peaks = []
    for i in range(1, len(spectrum) - 1):
        if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1]:
            peaks.append((freqs[i], spectrum[i]))
    
    peaks.sort(key=lambda x: -x[1])
    
    top_peaks = []
    for freq, amp in peaks[:8]:
        if freq > 20:  # ignore DC
            top_peaks.append(round(freq, 1))
    
    return top_peaks


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    base_dir = '/opt/data/projects/Genres/Research/virtual_instruments/'
    date_str = str(date.today())
    prefix = f'dev_marimba_bar_{date_str}'
    
    print(f"{'='*70}")
    print(f"  Daily DSP Research — Marimba Bar + Resonator Tube")
    print(f"  Date: {date_str}")
    print(f"{'='*70}")
    
    # ─── Generate melody ───────────────────────────────────────────────
    print("\n[1/5] Generating 2-bar melodic study...")
    audio, midi_events, instruments = generate_melody()
    print(f"  Audio: {len(audio)} samples @ {SAMPLE_RATE}Hz")
    print(f"  MIDI events: {len(midi_events)}")
    
    # ─── Get metrics from one instrument ───────────────────────────────
    print("\n[2/5] Computing instrument metrics...")
    # Use C4 instrument for reporting
    c4_instr = instruments['C4']
    metrics = c4_instr.get_metrics()
    
    print(f"  Fundamental: {metrics['fundamental_hz']} Hz")
    print(f"  Resonator tube: {metrics['resonator_tube_freq_hz']} Hz (Q={metrics['resonator_tube_Q']})")
    print(f"  Partials:")
    for p in metrics['partials']:
        print(f"    #{p['partial']}: {p['frequency_hz']} Hz (A={p['amplitude_ratio']}, τ={p['decay_time_sec']}s, Q={p['q_factor']})")
    print(f"  ADSR: {metrics['adsr']}")
    
    # ─── Spectrum analysis ─────────────────────────────────────────────
    print("\n[3/5] Spectral analysis...")
    peaks = analyze_spectrum(audio)
    print(f"  Dominant peaks (Hz): {peaks}")
    
    # ─── Export ─────────────────────────────────────────────────────────
    print("\n[4/5] Exporting files...")
    
    # WAV
    wav_path = f"{base_dir}{prefix}.wav"
    export_wav(wav_path, audio)
    
    # OGG + Opus
    ogg_path = f"{base_dir}{prefix}.ogg"
    opus_path = f"{base_dir}{prefix}.opus"
    export_ogg_opus(wav_path, ogg_path, opus_path)
    
    # MIDI
    midi_path = f"{base_dir}{prefix}.mid"
    export_midi(midi_path, midi_events)
    
    # ─── Save metrics JSON ──────────────────────────────────────────────
    print("\n[5/5] Saving metrics report...")
    metrics['spectral_peaks_hz'] = peaks
    metrics['pattern_notes'] = [{'note': e['note'], 'start_beat': e['start_beat'],
                                  'duration': e['duration_beats'], 'velocity': e['velocity']}
                                for e in midi_events]
    
    json_path = f"{base_dir}{prefix}_report.json"
    with open(json_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"  JSON: {json_path}")
    
    # ─── Summary ────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  ✓ Experiment complete: {prefix}")
    print(f"  ✓ Files: WAV + OGG + Opus + MIDI + JSON")
    print(f"{'='*70}")
    
    return metrics, peaks, audio


if __name__ == '__main__':
    main()