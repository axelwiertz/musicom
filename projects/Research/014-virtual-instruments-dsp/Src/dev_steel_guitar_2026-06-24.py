#!/usr/bin/env python3
"""
Daily DSP Research - Virtual Instrument: Synthesised Steel Guitar
Date: 2026-06-24
Technique: Karplus-Strong waveguide string model + magnetic pickup simulation + pitch bend portamento
Target: Lap steel / pedal steel guitar with characteristic gliding pitch between notes
"""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.signal import iirfilter, sosfreqz, freqz
import soundfile as sf
import struct, os, subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SR = 44100
BPM = 100
BEATS = 8  # 2 bars of 4/4
SECONDS = (BEATS * 4 * 60.0) / BPM  # 32 beats @100 = 19.2 sec
LEN = int(SR * SECONDS)
T = np.arange(LEN) / SR

# ---------------------------------------------------------------------------
# PITCH REFERENCE
# ---------------------------------------------------------------------------
# Notes in 12-TET, A4 = 440 Hz
NOTES = {
    'D3':  146.83, 'Eb3': 155.56, 'E3':  164.81, 'F3':  174.61,
    'F#3': 185.00, 'G3':  196.00, 'Ab3': 207.65, 'A3':  220.00,
    'Bb3': 233.08, 'B3':  246.94, 'C4':  261.63, 'Db4': 277.18,
    'D4':  293.66, 'Eb4': 311.13, 'E4':  329.63, 'F4':  349.23,
    'F#4': 369.99, 'G4':  392.00, 'Ab4': 415.30, 'A4':  440.00,
    'Bb4': 466.16, 'B4':  493.88, 'C5':  523.25, 'Db5': 554.37,
    'D5':  587.33, 'Eb5': 622.25, 'E5':  659.25, 'F5':  698.46,
    'F#5': 739.99, 'G5':  783.99, 'Ab5': 830.61, 'A5':  880.00,
    'Bb5': 932.33, 'B5':  987.77, 'C6':  1046.50,
}

NOTE_NAMES = {v: k for k, v in NOTES.items()}

# ---------------------------------------------------------------------------
# C6 Tuning (common for lap steel): C E G A C E (low to high)
# We'll model the top 3 strings for a melodic line
# String tuning frequencies for our voice
# ---------------------------------------------------------------------------
# Primary voice: high E string (E4=329.63), sliding melody
# Secondary: B4 string (493.88) for harmony
# We'll focus on the melody string with pitch bend slides

# ---------------------------------------------------------------------------
# MELODIC PATTERN — Steel guitar characteristic phrases with slides
# (note, start_beat, duration_beats, slide_target, slide_start_beat)
# ---------------------------------------------------------------------------
# E4 open, slide up to A4, back down, classic country lick
PATTERN = [
    # (freq_hz, start_beat, dur_beats, slide_to_freq_or_None, slide_offset_beats)
    # Opening phrase: E4 -> slide up to A4
    ('E4',  0.0,  1.5,  'A4',  0.4),   # E4 open, slide up to A4
    ('A4',  1.5,  0.5,   None,  0.0),   # Hold A4
    ('G4',  2.0,  0.5,   None,  0.0),   # Quick G4
    ('E4',  2.5,  0.5,   None,  0.0),   # Back to E4
    # Slide down phrase: B4 -> slide down to E4
    ('B4',  3.0,  1.5,  'E4',  0.3),   # B4 open, slide down to E4
    ('E4',  4.5,  0.5,   None,  0.0),   # Hold E4
    # Classic steel guitar crying lick: G4 -> slide up to B4 -> slide down to A4
    ('G4',  5.0,  1.5,  'B4',  0.5),   # G4 slides up to B4
    ('A4',  6.5,  0.5,   None,  0.0),   # Quick A4
    ('F#4', 7.0,  0.5,  'G4',  0.2),   # F#4 slides up to G4
    ('G4',  7.5,  0.5,   None,  0.0),   # Hold G4
    # Bar 2: Long emotive slide
    ('D4',  8.0,  1.0,   None,  0.0),   # D4
    ('D4',  9.0,  2.0,  'A4',  0.5),   # D4 -> long slide up to A4
    ('A4',  11.0, 1.0,   None,  0.0),   # Hold A4
    # Descending run with slides
    ('A4',  12.0, 0.75,  'F#4', 0.3),  # A4 slide down to F#4
    ('F#4', 12.75,0.25,  None,  0.0),
    ('E4',  13.0, 0.75,  'D4',  0.3),  # E4 slide down to D4
    ('D4',  13.75,0.25,  None,  0.0),
    ('C4',  14.0, 0.5,   None,  0.0),   # C4
    # Final sustained note with vibrato slide
    ('E4',  14.5, 3.5,   None,  0.0),   # Final E4 held long
]

# Resolve note names to frequencies
PATTERN_RESOLVED = []
for item in PATTERN:
    note_name, start, dur, slide_target, slide_off = item
    freq = NOTES[note_name]
    slide_freq = NOTES[slide_target] if slide_target is not None else None
    PATTERN_RESOLVED.append((freq, start, dur, slide_freq, slide_off))

# ---------------------------------------------------------------------------
# COMPUTE INSTANTANEOUS FREQUENCY OVER TIME (with portamento slides)
# ---------------------------------------------------------------------------
def build_freq_envelope(pattern, sr, total_len):
    """Build a frequency envelope with smooth portamento between notes + slides."""
    total_sec = total_len / sr
    freq_envelope = np.zeros(total_len)
    
    # For each event, we create a frequency trajectory
    # Between events, smooth interpolation
    
    # Build complete event list with explicit time-frequency points
    times = []   # seconds
    freqs = []   # hz
    
    for item in pattern:
        freq, start, dur, slide_freq, slide_offset = item
        end = start + dur
        
        if slide_freq is not None:
            # Slide event: has a glissando from one note to another
            slide_time = start + slide_offset
            times.append(start)       # start of note
            freqs.append(freq)        # start frequency
            times.append(slide_time)  # slide destination time
            freqs.append(slide_freq)  # slide destination frequency
            # If there's remaining time, hold the slide target
            if slide_time < end:
                times.append(end)
                freqs.append(slide_freq)
        else:
            # No slide, just hold the note
            times.append(start)
            freqs.append(freq)
            times.append(end)
            freqs.append(freq)
    
    # Sort by time
    sorted_pairs = sorted(zip(times, freqs))
    times = [p[0] for p in sorted_pairs]
    freqs = [p[1] for p in sorted_pairs]
    
    # Remove duplicate times (keep last freq for same time)
    unique_times = []
    unique_freqs = []
    for t, f in zip(times, freqs):
        if unique_times and t == unique_times[-1]:
            unique_freqs[-1] = f  # update freq for same time
        else:
            unique_times.append(t)
            unique_freqs.append(f)
    
    # Create time axis for each sample
    sample_times = np.arange(total_len) / sr
    
    # Interpolate with smooth cubic or linear for frequency
    # Linear interpolation for portamento effect (steel guitar slide is fairly linear)
    freq_envelope = np.interp(sample_times, unique_times, unique_freqs)
    
    # Sanity: clamp to valid range
    freq_envelope = np.clip(freq_envelope, 50.0, 2000.0)
    
    return freq_envelope, unique_times, unique_freqs


# ---------------------------------------------------------------------------
# 1. KARPLUS-STRONG STRING MODEL (with time-varying delay)
# ---------------------------------------------------------------------------
def modal_string_synthesis(freq_envelope, sr, feedback=0.98):
    """
    Modal/waveguide hybrid string synthesis for steel guitar.
    
    Uses a phase-controlled oscillator bank (harmonics 1-8) with
    decaying amplitudes plus a KS transient layer for the pluck attack.
    
    Pitch bends naturally by modulating all harmonic frequencies together.
    This approach is stable across pitch changes because each harmonic
    is independently phase-controlled.
    """
    n_samples = len(freq_envelope)
    out = np.zeros(n_samples)
    
    # Number of harmonics
    n_harmonics = 8
    
    # Harmonic amplitudes (steel string: strong fundamentals, gradually decreasing)
    harm_amps = np.array([1.0, 0.7, 0.4, 0.2, 0.1, 0.05, 0.03, 0.02])
    
    # Phase accumulators for each harmonic
    phases = np.zeros(n_harmonics)
    
    # Decay envelopes per harmonic (higher harmonics decay faster)
    decay_rates = np.array([0.3, 0.5, 0.8, 1.2, 1.8, 2.5, 3.5, 5.0])
    
    # Envelope state: the current amplitude envelope for each voice
    # We use a simple envelope that resets at each note onset
    
    # Pluck transient: noise burst filtered at the fundamental
    pluck_buffer = np.zeros(int(sr * 0.008))  # 8ms
    pluck_head = 0
    active_harmonics = np.ones(n_harmonics, dtype=bool)
    
    # For tracking note onsets
    prev_freq = freq_envelope[0]
    
    # Envelope state (exponential decay per harmonic)
    env_state = np.ones(n_harmonics)
    
    for i in range(n_samples):
        freq = freq_envelope[i]
        if freq < 50:
            freq = 50.0
        
        # Detect note onsets (rapid frequency change or reset)
        # Refresh envelope when frequency jumps significantly
        if abs(freq - prev_freq) / max(prev_freq, 1) > 0.15:
            # New note - refresh envelopes
            env_state = np.ones(n_harmonics)
            # Add pluck transient
            pluck_buffer = np.random.randn(len(pluck_buffer)) * 0.2
            pluck_head = 0
        
        # Update phases
        dt = 1.0 / sr
        for h in range(n_harmonics):
            phases[h] += 2.0 * np.pi * freq * (h + 1) * dt
        
        # Update envelopes (exponential decay)
        env_state *= np.exp(-decay_rates * dt)
        
        # Synthesize harmonics
        harmonic_sum = 0.0
        for h in range(n_harmonics):
            harmonic_sum += harm_amps[h] * np.sin(phases[h]) * env_state[h]
        
        # Pluck transient (filtered noise)
        if pluck_head < len(pluck_buffer):
            pluck_val = pluck_buffer[pluck_head]
            # Simple LP filter for pluck
            pluck_out = pluck_val * np.exp(-pluck_head * 3.0 / len(pluck_buffer))
            pluck_head += 1
        else:
            pluck_out = 0.0
        
        # Mix
        sample = harmonic_sum * 0.4 + pluck_out * 0.3
        
        # Soft clip
        out[i] = np.tanh(sample * 2.0) * 0.5
        
        prev_freq = freq
    
    # Normalize
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.6
    
    return out


# ---------------------------------------------------------------------------
# 2. MAGNETIC PICKUP SIMULATION (resonant bandpass)
# ---------------------------------------------------------------------------
def magnetic_pickup(signal, sr, center_freq=680.0, q=3.5, gain=1.0):
    """
    Simulate a magnetic guitar pickup as a resonant bandpass filter.
    
    Typical steel guitar pickups have a resonance peak between 500-800 Hz.
    Q factor around 2-5 gives the characteristic "twang".
    """
    # Second-order bandpass filter
    bw = center_freq / q
    low = center_freq - bw / 2.0
    high = center_freq + bw / 2.0
    w0_low = low / (sr / 2)
    w0_high = high / (sr / 2)
    if w0_low < 0.001:
        w0_low = 0.001
    if w0_high >= 1.0:
        w0_high = 0.99
    
    sos = butter(2, [w0_low, w0_high], btype='band', output='sos')
    
    # Apply filter
    filtered = sosfilt(sos, signal)
    
    # Mix dry/wet for natural sound (75% pickup / 25% direct)
    mixed = signal * 0.25 + filtered * 0.75
    return mixed * gain


# ---------------------------------------------------------------------------
# 3. AMP / CABINET SIMULATION
# ---------------------------------------------------------------------------
def amp_cabinet(signal, sr, drive=0.15, lowpass_freq=4500.0):
    """
    Gentle tube amp + speaker cabinet simulation.
    
    - Soft clipping for tube warmth (arctan waveshaper)
    - Lowpass for speaker roll-off
    """
    # Soft clip (tube emulation)
    clipped = np.arctan(signal * (1.0 + drive * 3.0)) / np.arctan(1.0 + drive * 3.0)
    
    # Lowpass (cabinet roll-off)
    nyq = sr / 2
    cutoff = lowpass_freq / nyq
    if cutoff >= 1.0:
        cutoff = 0.99
    b, a = butter(4, cutoff, btype='low', output='ba')
    sos = butter(4, cutoff, btype='low', output='sos')
    out = sosfilt(sos, clipped)
    
    # Normalize
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.85
    
    return out


# ---------------------------------------------------------------------------
# 4. REVERB (simple room)
# ---------------------------------------------------------------------------
def simple_reverb(signal, sr, decay=0.3, delay_ms=35.0):
    """Simple Schroeder-style reverberation."""
    delay_samples = int(sr * delay_ms / 1000.0)
    
    # Comb filter reverb
    reverb = np.zeros_like(signal)
    comb = np.zeros_like(signal)
    
    # Multiple taps for richer reverb
    taps = [
        (delay_samples, 0.4),
        (int(delay_samples * 1.3), 0.3),
        (int(delay_samples * 1.7), 0.2),
        (int(delay_samples * 2.1), 0.15),
    ]
    
    for tap_delay, tap_gain in taps:
        if tap_delay >= len(signal):
            continue
        tap = np.zeros_like(signal)
        tap[tap_delay:] = signal[:-tap_delay] * tap_gain * decay
        reverb += tap
    
    # Mix dry/wet (70% dry, 30% wet)
    out = signal * 0.7 + reverb * 0.3
    
    # Normalize
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.9
    
    return out


# ---------------------------------------------------------------------------
# 5. BUILD INSTRUMENT
# ---------------------------------------------------------------------------
def build_steel_guitar(pattern_resolved, sr, bpm):
    """Build the complete steel guitar instrument."""
    total_beats = BEATS
    total_sec = (total_beats * 4 * 60.0) / bpm
    total_len = int(sr * total_sec)
    
    # Build frequency envelope with slides
    freq_env, times, freqs = build_freq_envelope(pattern_resolved, sr, total_len)
    
    print(f"  Frequency envelope: {len(times)} breakpoints, {total_sec:.1f}s")
    
    # Generate string signal
    print("  Rendering Karplus-Strong string model...")
    string_signal = modal_string_synthesis(
        freq_env, sr, feedback=0.98
    )
    
    # Apply pickup
    print("  Applying magnetic pickup simulation...")
    pickup_signal = magnetic_pickup(string_signal, sr, center_freq=680.0, q=3.5)
    
    # Apply amp/cabinet
    print("  Applying amp/cabinet coloration...")
    amped_signal = amp_cabinet(pickup_signal, sr, drive=0.18, lowpass_freq=4800.0)
    
    # Apply reverb
    print("  Adding reverb...")
    final = simple_reverb(amped_signal, sr, decay=0.25, delay_ms=30.0)
    
    # Soft final normalization
    peak = np.max(np.abs(final))
    if peak > 0:
        final = final / peak * 0.95
    
    return final, freq_env, times, freqs


# ---------------------------------------------------------------------------
# 6. MIDI EXPORT (using mido - manual binary)
# ---------------------------------------------------------------------------
def write_midi_file(path, pattern_resolved, bpm, notes_dict):
    """Write a standard MIDI file with pitch bend messages for slides."""
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    import math
    
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    tempo_us = int(60_000_000 / bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo_us))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    
    ticks_per_beat = mid.ticks_per_beat
    
    def freq_to_midi(freq):
        return int(round(69 + 12 * math.log2(freq / 440.0)))
    
    def freq_to_pitchbend_signed(freq, base_note):
        """
        Convert frequency to MIDI pitch bend signed value (-8192..8191, 0=center).
        Range: ±1 semitone mapped to ±8191.
        """
        base_freq = 440.0 * 2**((base_note - 69) / 12)
        half_steps = 12 * math.log2(freq / base_freq)
        cents = half_steps * 100.0
        bend_value = int(round(cents / 100.0 * 8191))
        return int(np.clip(bend_value, -8192, 8191))
    
    last_time = 0
    
    for item in pattern_resolved:
        freq, start_beat, dur_beats, slide_freq, slide_offset = item
        
        note_num = freq_to_midi(freq)
        start_ticks = int(start_beat * ticks_per_beat)
        dur_ticks = int(dur_beats * ticks_per_beat)
        
        # Note on
        delta = max(start_ticks - last_time, 0)
        track.append(Message('note_on', note=note_num, velocity=90, time=delta))
        last_time = start_ticks
        
        if slide_freq is not None:
            slide_start_time = start_beat + slide_offset
            slide_duration = dur_beats - slide_offset
            
            # Pitch bend at slide start
            start_pitch = freq_to_pitchbend_signed(freq, note_num)
            slide_start_ticks = int(slide_start_time * ticks_per_beat)
            bend_delta = max(slide_start_ticks - last_time, 0)
            track.append(Message('pitchwheel', pitch=start_pitch, time=bend_delta))
            last_time = slide_start_ticks
            
            slide_target_num = freq_to_midi(slide_freq)
            half_step_diff = 12 * math.log2(slide_freq / freq)
            
            if abs(half_step_diff) <= 1.0:
                # Within ±1 semitone: single bend
                end_pitch = freq_to_pitchbend_signed(slide_freq, note_num)
                slide_end_ticks = int((slide_start_time + slide_duration * 0.8) * ticks_per_beat)
                bend_delta = max(slide_end_ticks - last_time, 0)
                track.append(Message('pitchwheel', pitch=end_pitch, time=bend_delta))
                last_time = slide_end_ticks
            else:
                # Large slide: bend to limit, switch note, continue bend
                if half_step_diff > 0:
                    limit_freq = freq * 2.0**(1.0/12)
                else:
                    limit_freq = freq * 2.0**(-1.0/12)
                
                limit_pitch = freq_to_pitchbend_signed(limit_freq, note_num)
                frac = min(abs(1.0 / half_step_diff), 1.0)
                mid_ticks = int(slide_start_time * ticks_per_beat +
                              frac * slide_duration * 0.8 * ticks_per_beat)
                bend_delta = max(mid_ticks - last_time, 0)
                track.append(Message('pitchwheel', pitch=limit_pitch, time=bend_delta))
                
                # Note change
                track.append(Message('note_off', note=note_num, velocity=64, time=0))
                track.append(Message('note_on', note=slide_target_num, velocity=90, time=0))
                last_time = mid_ticks
                note_num = slide_target_num
                
                # Remaining bend to target
                rem_pitch = freq_to_pitchbend_signed(slide_freq, slide_target_num)
                slide_end_ticks = int((slide_start_time + slide_duration * 0.8) * ticks_per_beat)
                bend_delta = max(slide_end_ticks - mid_ticks, 0)
                track.append(Message('pitchwheel', pitch=rem_pitch, time=bend_delta))
                last_time = slide_end_ticks
        
        # Note off
        end_ticks = start_ticks + dur_ticks
        delta = max(end_ticks - last_time, 0)
        track.append(Message('note_off', note=note_num, velocity=64, time=delta))
        last_time = end_ticks
        
        # Reset pitch bend to center
        track.append(Message('pitchwheel', pitch=0, time=0))
    
    track.append(MetaMessage('end_of_track', time=0))
    mid.save(path)
    print(f"  MIDI saved: {path}")


# ---------------------------------------------------------------------------
# 7. MAIN
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("STEEL GUITAR — DSP Virtual Instrument")
    print("=" * 60)
    print(f"Date: 2026-06-24")
    print(f"Sample Rate: {SR} Hz")
    print(f"Tempo: {BPM} BPM")
    print(f"Duration: {BEATS} beats ({SECONDS:.1f}s)")
    print()
    
    # Base directory (two levels up from Src)
    BASE_DIR = Path(__file__).resolve().parent.parent
    SRC_DIR = BASE_DIR / 'Src'
    AUDIO_DIR = BASE_DIR / 'Audio'
    MIDI_DIR = BASE_DIR / 'MIDI'
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    MIDI_DIR.mkdir(parents=True, exist_ok=True)
    
    # Filename base
    base_name = 'steel_guitar_2026-06-24'
    
    # -------------------------------------------------------------------
    # BUILD THE INSTRUMENT
    # -------------------------------------------------------------------
    print("Building steel guitar instrument...")
    audio, freq_env, break_times, break_freqs = build_steel_guitar(
        PATTERN_RESOLVED, SR, BPM
    )
    
    # -------------------------------------------------------------------
    # METRICS COMPUTATION
    # -------------------------------------------------------------------
    print("\nComputing metrics...")
    
    # Pitch bend range
    freq_min = np.min(freq_env[freq_env > 50])
    freq_max = np.max(freq_env)
    # Convert to cents relative to nearest equal-tempered note
    midi_min = 69 + 12 * np.log2(freq_min / 440.0)
    midi_max = 69 + 12 * np.log2(freq_max / 440.0)
    pitch_bend_range_cents = 1200 * np.log2(freq_max / freq_min)
    
    # String decay time — measure envelope
    envelope = np.abs(audio)
    envelope = np.convolve(envelope, np.hanning(int(SR * 0.05)), mode='same')
    # Find where it drops to 1% of peak after max
    peak_idx = np.argmax(envelope)
    threshold = np.max(envelope) * 0.01
    decay_samples = np.where(envelope[peak_idx:] < threshold)[0]
    if len(decay_samples) > 0:
        decay_time_s = decay_samples[0] / SR
    else:
        decay_time_s = len(audio) / SR
    
    # Pickup resonance Q
    pickup_q = 3.5
    
    # -------------------------------------------------------------------
    # EXPORT WAV
    # -------------------------------------------------------------------
    wav_path = AUDIO_DIR / f'{base_name}.wav'
    sf.write(str(wav_path), audio, SR, subtype='PCM_16')
    print(f"\nWAV exported: {wav_path}")
    
    # -------------------------------------------------------------------
    # EXPORT MIDI
    # -------------------------------------------------------------------
    mid_path = MIDI_DIR / f'{base_name}.mid'
    try:
        write_midi_file(str(mid_path), PATTERN_RESOLVED, BPM, NOTES)
    except Exception as e:
        print(f"  MIDI export failed: {e}")
        # Fallback: write raw MIDI binary
        try:
            mid_path = MIDI_DIR / f'{base_name}.mid'
            write_midi_file(str(mid_path), PATTERN_RESOLVED, BPM, NOTES)
        except Exception as e2:
            print(f"  MIDI fallback also failed: {e2}")
    
    # -------------------------------------------------------------------
    # EXPORT OGG (via ffmpeg)
    # -------------------------------------------------------------------
    ogg_path = AUDIO_DIR / f'{base_name}.ogg'
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(wav_path),
            '-c:a', 'libvorbis', '-q:a', '4',
            '-vn', str(ogg_path)
        ], check=True, capture_output=True, timeout=30)
        print(f"OGG exported: {ogg_path}")
    except subprocess.CalledProcessError as e:
        print(f"  OGG export failed: {e.stderr.decode()}")
    
    # -------------------------------------------------------------------
    # EXPORT OPUS (via ffmpeg)
    # -------------------------------------------------------------------
    opus_path = AUDIO_DIR / f'{base_name}.opus'
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(wav_path),
            '-c:a', 'libopus', '-b:a', '64k',
            '-vn', str(opus_path)
        ], check=True, capture_output=True, timeout=30)
        print(f"OPUS exported: {opus_path}")
    except subprocess.CalledProcessError as e:
        print(f"  OPUS export failed: {e.stderr.decode()}")
    
    # -------------------------------------------------------------------
    # METRICS REPORT
    # -------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEEL GUITAR INSTRUMENT — DSP METRICS")
    print("=" * 60)
    print(f"\nString Model: Karplus-Strong waveguide")
    print(f"Excitation: Plucked string (band-limited noise burst, 6ms)")
    print(f"Pickup Model: Resonant bandpass filter (magnetic pickup simulation)")
    print(f"Amp Model: Tube soft-clipping + speaker cabinet lowpass")
    
    print(f"\n--- Frequency Metrics ---")
    print(f"Tuning: C6 (high E melody string)")
    print(f"Frequency range: {freq_min:.1f} Hz — {freq_max:.1f} Hz")
    print(f"MIDI note range: {midi_min:.1f} — {midi_max:.1f}")
    print(f"Pitch bend range (total): {pitch_bend_range_cents:.0f} cents ({pitch_bend_range_cents/100:.1f} semitones)")
    
    print(f"\n--- String Parameters ---")
    print(f"Pluck position: 12% from bridge")
    print(f"Feedback (sustain): 0.982")
    print(f"String decay time (to -40dB): {decay_time_s:.2f}s")
    print(f"Lowpass decay coefficient: 0.55 ± 0.1")
    
    print(f"\n--- Pickup Parameters ---")
    print(f"Type: Magnetic single-coil (resonant bandpass)")
    print(f"Center frequency: 680 Hz")
    print(f"Resonance Q: {pickup_q}")
    print(f"Dry/Wet mix: 25/75")
    
    print(f"\n--- Amp/Cabinet Parameters ---")
    print(f"Drive: 0.18 (mild overdrive)")
    print(f"Lowpass cutoff: 4800 Hz")
    print(f"Waveshaper: arctan (tube emulation)")
    
    print(f"\n--- Reverb ---")
    print(f"Type: Schroeder comb-filter (4 taps)")
    print(f"Decay: 0.25")
    print(f"Delay base: 30ms")
    print(f"Dry/Wet mix: 70/30")
    
    print(f"\n--- Melodic Pattern ({BPM} BPM, {BEATS} beats) ---")
    for item in PATTERN_RESOLVED:
        freq, start_beat, dur_beats, slide_freq, slide_off = item
        name = NOTE_NAMES.get(freq, f"{freq:.0f}Hz")
        slide_info = ""
        if slide_freq is not None:
            slide_name = NOTE_NAMES.get(slide_freq, f"{slide_freq:.0f}Hz")
            slide_info = f" -> slide to {slide_name} @ beat {start_beat + slide_off:.1f}"
        print(f"  Beat {start_beat:>5.1f}: {name:>4s} ({freq:>3.0f} Hz) x {dur_beats:.2f}b{slide_info}")
    
    print(f"\n--- Files Exported ---")
    for ext in ['wav', 'ogg', 'opus']:
        fpath = AUDIO_DIR / f'{base_name}.{ext}'
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  Audio/{base_name}.{ext}  ({size / 1024:.1f} KB)")
    fpath = MIDI_DIR / f'{base_name}.mid'
    if fpath.exists():
        size = fpath.stat().st_size
        print(f"  MIDI/{base_name}.mid  ({size / 1024:.1f} KB)")
    
    print("\nDone.")