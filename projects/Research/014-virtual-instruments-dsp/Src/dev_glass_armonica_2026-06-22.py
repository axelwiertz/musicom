#!/usr/bin/env python3
"""
DEV: Resonant Glass Armonica — Physical Model
==============================================
A subtractive/physical simulation of wet-finger rubbed glass bowls.
Combines multi-modal resonant oscillators (fundamental + harmonic overtones
characteristic of glass/quartz) with a body comb-filter resonance,
friction-noise excitation, and ADSR envelope shaping.

DSP Architecture:
  Friction Noise Burst → Multi-Modal Sine Bank → Comb Filter Body → 
  Bandpass Resonant Shell → ADSR Envelope → Reverb Tail

Date: 2026-06-22
"""

import numpy as np
from scipy import signal
from scipy.io import wavfile
import soundfile as sf
import os, json, struct, subprocess
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────
SAMPLE_RATE = 48000
BIT_DEPTH = 24
BPM = 120
BEATS_PER_BAR = 4
NUM_BARS = 2
TOTAL_BEATS = NUM_BARS * BEATS_PER_BAR
BEAT_SECONDS = 60.0 / BPM
TOTAL_SECONDS = TOTAL_BEATS * BEAT_SECONDS
NUM_SAMPLES = int(SAMPLE_RATE * TOTAL_SECONDS)

OUTPUT_DIR = Path("/opt/data/projects/Genres/Research/virtual_instruments")
DATE_TAG = "2026-06-22"
INSTRUMENT_NAME = "glass_armonica"

# ── Note Frequencies (C4 major scale, 2 bars = 8 notes) ──────────────
# Melodic pattern: C4 E4 G4 B4 C5 B4 G4 E4 (ascending arpeggio, mirror)
NOTES_HZ = [261.63, 329.63, 392.00, 493.88, 523.25, 493.88, 392.00, 329.63]
NOTE_NAMES = ["C4", "E4", "G4", "B4", "C5", "B4", "G4", "E4"]
NOTE_DURATIONS = [BEAT_SECONDS * 1.0] * len(NOTES_HZ)  # quarter notes

# ── Glass Bowl Modal Parameters ───────────────────────────────────────
# Real glass bowls have inharmonic partials due to cylindrical geometry.
# We model the first 5 significant modes with measured Q factors.
def get_glass_mode_ratios():
    """
    Modal ratios for a glass bowl (approximate cylindrical shell modes).
    Ratios relative to fundamental:
      Mode 1: 1.00 (fundamental)
      Mode 2: 2.31 (first radial overtone)
      Mode 3: 3.85 (second radial overtone)
      Mode 4: 5.44 (third radial overtone — strong in glass)
      Mode 5: 7.23 (fourth radial overtone)
    Amplitude weights decrease with mode order.
    Q factors: glass has high Q (low damping), typically 200-500
    """
    return {
        "ratios":  [1.00, 2.31, 3.85, 5.44, 7.23],
        "weights": [1.00, 0.65, 0.35, 0.12, 0.04],
        "q_factors": [350, 280, 220, 180, 120]
    }

# ── Friction Excitation Model ─────────────────────────────────────────
def generate_friction_burst(duration_sec, sample_rate, intensity=0.7):
    """
    Models the sound of a wet finger dragging on a glass rim.
    Uses shaped pink noise + a filtered transient.
    """
    n_samples = int(sample_rate * duration_sec)
    # Pink noise via Voss-McCartney algorithm approximation
    white = np.random.randn(n_samples)
    # Integrate for pink (1/f) spectrum
    pink = np.cumsum(white) / np.sqrt(n_samples)
    pink = pink / np.max(np.abs(pink))
    
    # Transient attack: sharp onset with exponential decay
    t = np.linspace(0, duration_sec, n_samples)
    attack_env = np.exp(-t * 80.0)  # Fast decay ~12ms
    attack_env = attack_env / np.max(attack_env)
    
    # High-pass filter the pink noise (friction has more high content)
    sos_hp = signal.butter(4, 2000, 'hp', fs=sample_rate, output='sos')
    pink_hp = signal.sosfilt(sos_hp, pink)
    
    # Combine: transient + filtered noise
    friction = 0.3 * attack_env + 0.7 * pink_hp
    friction = friction * intensity
    friction = friction / np.max(np.abs(friction) + 1e-10)
    return friction

# ── Multi-Modal Oscillator Bank ───────────────────────────────────────
def generate_glass_tone(fundamental_hz, duration_sec, sample_rate, 
                         modal_params, friction_signal=None):
    """
    Generate a glass bowl tone by summing modal sine waves with 
    appropriate amplitude weights, Q-dependent decay, and friction excitation.
    """
    n_samples = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    
    ratios = modal_params["ratios"]
    weights = modal_params["weights"]
    q_factors = modal_params["q_factors"]
    
    output = np.zeros(n_samples)
    
    for i, (ratio, weight, q) in enumerate(zip(ratios, weights, q_factors)):
        freq = fundamental_hz * ratio
        # Damping envelope per mode: exponential decay based on Q factor
        # Q = f0 / bandwidth => decay time constant
        # Amplitude envelope: exp(-pi * f0 * t / Q)
        decay_rate = np.pi * freq / q
        damping_env = np.exp(-decay_rate * t)
        
        # Generate sine wave with mode-specific phase offset
        phase_offset = i * np.pi / 6  # Slight phase spread for richness
        sine_wave = np.sin(2 * np.pi * freq * t + phase_offset)
        
        # Apply damping envelope and weight
        mode_signal = weight * sine_wave * damping_env
        
        output += mode_signal
    
    # Normalize
    output = output / np.max(np.abs(output) + 1e-10)
    
    # If friction signal provided, convolve to add physical excitation realism
    if friction_signal is not None:
        # Short convolution for attack texture
        friction_trimmed = friction_signal[:min(len(friction_signal), 2048)]
        output = signal.fftconvolve(output, friction_trimmed, mode='same')
        output = output / np.max(np.abs(output) + 1e-10)
    
    return output

# ── Comb Filter Body Resonance ────────────────────────────────────────
def apply_comb_resonance(signal_array, sample_rate, delay_ms=3.2, feedback=0.6):
    """
    Comb filter models the glass body's cylindrical resonance.
    delay_ms: round-trip time through the glass wall.
    feedback: resonance feedback strength.
    """
    delay_samples = int(sample_rate * delay_ms / 1000.0)
    if delay_samples < 1:
        delay_samples = 1
    
    output = np.copy(signal_array)
    for i in range(delay_samples, len(output)):
        output[i] += feedback * output[i - delay_samples]
    
    # Normalize to prevent blowup
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak
    return output

# ── Bandpass Resonant Shell ───────────────────────────────────────────
def apply_shell_filter(signal_array, sample_rate, center_hz=1200, q=8.0):
    """
    High-Q bandpass filter simulating the glass shell's resonant body.
    Acts as the primary 'tonewood' filter.
    Uses a Bessel lowpass at the body resonance frequency.
    """
    norm_freq = center_hz / (sample_rate / 2.0)
    sos = signal.bessel(2, norm_freq, btype='low', output='sos')
    filtered = signal.sosfilt(sos, signal_array)
    
    # Also add a high shelf to simulate brightness
    sos_hs = signal.butter(2, 3000, btype='high', fs=sample_rate, output='sos')
    filtered = signal.sosfilt(sos_hs, filtered)
    
    return filtered / np.max(np.abs(filtered) + 1e-10)

# ── ADSR Envelope ─────────────────────────────────────────────────────
def adsr_envelope(n_samples, sample_rate, 
                  attack=0.008, decay=0.15, sustain_level=0.55, release=0.35):
    """
    ADSR envelope for friction-bowed glass.
    Attack: fast (finger contacts glass)
    Decay: moderate (settling into sustained friction)
    Sustain: held while finger moves
    Release: glass rings after finger leaves
    """
    attack_s = int(attack * sample_rate)
    decay_s = int(decay * sample_rate)
    release_s = int(release * sample_rate)
    sustain_end = n_samples - release_s
    
    env = np.zeros(n_samples)
    
    # Attack phase (linear rise)
    env[:attack_s] = np.linspace(0, 1.0, attack_s)
    
    # Decay phase (exponential fall to sustain level)
    if decay_s > 0:
        decay_curve = np.linspace(1.0, sustain_level, decay_s)
        env[attack_s:attack_s + decay_s] = decay_curve
    
    # Sustain phase
    if sustain_end > attack_s + decay_s:
        env[attack_s + decay_s:sustain_end] = sustain_level
    
    # Release phase (exponential decay to 0)
    if release_s > 0:
        release_curve = np.linspace(sustain_level, 0, release_s) ** 1.5
        env[sustain_end:] = release_curve
    
    return env

# ── Simple Room Reverb (Schroeder) ────────────────────────────────────
def apply_reverb(signal_array, sample_rate, decay=0.4, mix=0.2):
    """
    Simple Schroeder reverb with parallel comb filters.
    """
    # Parallel comb filters at different delays
    delays_ms = [21, 37, 45, 53]
    gains = [decay * 0.8, decay * 0.7, decay * 0.6, decay * 0.5]
    
    wet = np.zeros_like(signal_array)
    for delay_ms, gain in zip(delays_ms, gains):
        delay_samp = int(sample_rate * delay_ms / 1000.0)
        comb = np.copy(signal_array)
        for i in range(delay_samp, len(comb)):
            comb[i] += gain * comb[i - delay_samp]
        wet += comb
    wet = wet / len(delays_ms)
    
    # Allpass to smooth out coloration
    allpass_delay = int(sample_rate * 6 / 1000.0)
    allpass_gain = 0.5
    for i in range(allpass_delay, len(wet)):
        wet[i] = wet[i] + allpass_gain * wet[i - allpass_delay] - allpass_gain * wet[i]
    
    wet = wet / np.max(np.abs(wet) + 1e-10)
    output = (1 - mix) * signal_array + mix * wet
    return output / np.max(np.abs(output) + 1e-10)


# ═══════════════════════════════════════════════════════════════════════
#  COMPOSITION: 2-bar melodic pattern
# ═══════════════════════════════════════════════════════════════════════

def compose_melodic_pattern():
    """
    Build a 2-bar melodic study: C4 E4 G4 B4 C5 B4 G4 E4
    Each note gets its own glass tone generation with overlapping envelopes
    for legato effect.
    """
    print(f"Composing {len(NOTES_HZ)} notes over {NUM_BARS} bars ({TOTAL_SECONDS:.2f}s)")
    
    full_mix = np.zeros(NUM_SAMPLES)
    modal_params = get_glass_mode_ratios()
    
    current_sample = 0
    for i, (freq_hz, name, duration) in enumerate(zip(NOTES_HZ, NOTE_NAMES, NOTE_DURATIONS)):
        note_start = current_sample
        note_samples = int(SAMPLE_RATE * duration)
        
        print(f"  Note {i+1}/{len(NOTES_HZ)}: {name} ({freq_hz:.2f} Hz) — {duration:.3f}s")
        
        # Generate friction burst for this note
        friction = generate_friction_burst(0.05, SAMPLE_RATE, intensity=0.6 + 0.1*i)
        
        # Generate glass tone
        tone = generate_glass_tone(freq_hz, duration * 1.15, SAMPLE_RATE, 
                                    modal_params, friction_signal=friction)
        
        # Apply comb filter body resonance
        tone = apply_comb_resonance(tone, SAMPLE_RATE, 
                                     delay_ms=3.2 + 0.3 * (freq_hz / 261.63), 
                                     feedback=0.55 + 0.05 * (i % 3))
        
        # Apply shell bandpass filter
        tone = apply_shell_filter(tone, SAMPLE_RATE, 
                                   center_hz=min(1400, freq_hz * 3.2), 
                                   q=6.0)
        
        # ADSR envelope
        env = adsr_envelope(len(tone), SAMPLE_RATE, 
                            attack=0.015, decay=0.12, 
                            sustain_level=0.60, release=0.30)
        tone = tone * env
        
        # Add to mix with slight overlap for legato
        end_sample = min(note_start + len(tone), NUM_SAMPLES)
        full_mix[note_start:end_sample] += tone[:end_sample - note_start]
        
        current_sample += int(SAMPLE_RATE * duration * 0.92)  # 8% overlap
        
        # Crossfade between consecutive notes
        if i > 0:
            fade_len = int(SAMPLE_RATE * 0.012)
            start = note_start - fade_len
            if start >= 0:
                fade_in = np.linspace(0, 1, min(fade_len, note_samples))
                full_mix[note_start:note_start + len(fade_in)] *= fade_in
    
    # Normalize
    peak = np.max(np.abs(full_mix))
    if peak > 0:
        full_mix = full_mix / peak * 0.95  # Headroom
    
    print("  Applying master reverb...")
    full_mix = apply_reverb(full_mix, SAMPLE_RATE, decay=0.35, mix=0.15)
    
    print(f"  Final peak: {np.max(np.abs(full_mix)):.4f}")
    return full_mix


# ═══════════════════════════════════════════════════════════════════════
#  EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def export_wav(audio_data, filename):
    """Export 24-bit WAV file."""
    path = OUTPUT_DIR / filename
    # Scale to 24-bit range
    audio_int = np.clip(audio_data, -1.0, 1.0)
    audio_int = (audio_int * (2**23 - 1)).astype(np.int32)
    wavfile.write(str(path), SAMPLE_RATE, audio_int)
    print(f"  WAV:   {path} ({path.stat().st_size / 1024:.1f} KB)")
    return path

def export_ogg(audio_data, filename):
    """Export OGG/Opus via ffmpeg."""
    path = OUTPUT_DIR / filename
    # Write temporary WAV first
    temp_wav = OUTPUT_DIR / f"_temp_{DATE_TAG}.wav"
    sf.write(str(temp_wav), audio_data, SAMPLE_RATE, subtype='PCM_24')
    
    # Convert to OGG using ffmpeg with quality settings
    if filename.endswith('.opus'):
        # Opus — highest quality
        cmd = ['ffmpeg', '-y', '-i', str(temp_wav), 
               '-c:a', 'libopus', '-b:a', '256k', '-vbr', 'off',
               str(path)]
    else:
        # OGG Vorbis — high quality
        cmd = ['ffmpeg', '-y', '-i', str(temp_wav),
               '-c:a', 'libvorbis', '-q:a', '7',
               str(path)]
    
    subprocess.run(cmd, check=True, capture_output=True)
    temp_wav.unlink()  # Clean temp
    print(f"  OGG:   {path} ({path.stat().st_size / 1024:.1f} KB)")
    return path

def export_midi(filename):
    """Export MIDI file of the melodic pattern using mido."""
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage
    
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Tempo (MetaMessage, not regular Message)
    tempo_us = int(60_000_000 / BPM)
    track.append(MetaMessage('set_tempo', tempo=tempo_us, time=0))
    
    # Use MIDI note numbers
    # C4=60, E4=64, G4=67, B4=71, C5=72
    midi_notes = [60, 64, 67, 71, 72, 71, 67, 64]
    
    ticks_per_beat = mid.ticks_per_beat
    note_ticks = int(ticks_per_beat * 0.9)  # 90% of beat length
    
    for i, note in enumerate(midi_notes):
        # Note On
        track.append(Message('note_on', note=note, velocity=72, time=0 if i > 0 else note_ticks))
        # Note Off (after 90% of beat)
        track.append(Message('note_off', note=note, velocity=64, time=note_ticks))
    
    path = OUTPUT_DIR / filename
    mid.save(str(path))
    print(f"  MIDI:  {path} ({path.stat().st_size:.0f} bytes)")
    return path


# ═══════════════════════════════════════════════════════════════════════
#  METRICS / SYSTEM GRAPH
# ═══════════════════════════════════════════════════════════════════════

def compute_metrics(audio_data):
    """
    Compute resonant peak frequencies and Q factors.
    Uses Welch's method for PSD estimation + peak detection.
    """
    from scipy.signal import welch, find_peaks
    
    freqs, psd = welch(audio_data, fs=SAMPLE_RATE, nperseg=8192, noverlap=4096)
    
    # Find peaks in PSD (only above 50Hz, below 12kHz)
    mask = (freqs >= 50) & (freqs <= 12000)
    freqs_roi = freqs[mask]
    psd_roi = psd[mask]
    psd_db = 10 * np.log10(psd_roi + 1e-15)
    
    # Detect peaks
    peaks, properties = find_peaks(psd_db, prominence=3.0, distance=20)
    
    # Sort by prominence, take top 5
    prominences = properties['prominences']
    sorted_idx = np.argsort(prominences)[::-1]
    
    top_peaks = []
    for idx in sorted_idx[:5]:
        peak_idx = peaks[idx]
        f = freqs_roi[peak_idx]
        p = prominences[idx]
        
        # Estimate Q from -3dB bandwidth around peak
        half_max = psd_db[peak_idx] - 3
        # Find left and right -3dB crossings
        left = peak_idx
        while left > 0 and psd_db[left] > half_max:
            left -= 1
        right = peak_idx
        while right < len(psd_db) - 1 and psd_db[right] > half_max:
            right += 1
        
        bw = freqs_roi[right] - freqs_roi[left] if right > left else 1.0
        q = f / bw if bw > 0 else 0
        
        top_peaks.append({
            "freq_hz": round(f, 2),
            "peak_db": round(psd_db[peak_idx], 2),
            "prominence_db": round(p, 2),
            "q_factor": round(q, 1)
        })
    
    return top_peaks

def build_system_graph(metrics, modal_params):
    """
    Build a DSP system graph showing the signal chain with measurements.
    """
    lines = []
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║     RESONANT GLASS ARMONICA — DSP System Graph                    ║")
    lines.append("║     Physical Model: Multi-Modal Glass Bowl Simulation             ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")
    lines.append("┌────────────────── SIGNAL FLOW ───────────────────────────────────┐")
    lines.append("│                                                                  │")
    lines.append("│  Friction Noise ─▶ Modal Osc. Bank ─▶ Comb Filter ─▶ Shell BPF  │")
    lines.append("│   (pink+transient)    (5 sine modes)   (3.2ms delay)  (1.2kHz)  │")
    lines.append("│                                                                  │")
    lines.append("│  ADSR Envelope ─▶ Mix ─▶ Reverb ─▶ Output                        │")
    lines.append("│  (0.008/0.15/0.55/0.35)     (Schroeder, 0.15 mix)               │")
    lines.append("└──────────────────────────────────────────────────────────────────┘")
    lines.append("")
    lines.append("┌─────────────── GLASS MODAL PARAMETERS ───────────────────────────┐")
    lines.append("│  Mode │  Ratio │  Weight │  Q Factor │  Desc.                    │")
    lines.append("├───────┼────────┼─────────┼───────────┼───────────────────────────┤")
    
    for i, (r, w, q) in enumerate(zip(
            modal_params["ratios"], modal_params["weights"], modal_params["q_factors"])):
        descs = ["Fundamental", "1st Radial", "2nd Radial", "3rd Radial", "4th Radial"]
        lines.append(f"│  {i+1:>3}  │  {r:>5.2f}  │  {w:>5.2f}   │  {q:>5.0f}     │  {descs[i]:<24}│")
    
    lines.append("└───────┴────────┴─────────┴───────────┴───────────────────────────┘")
    lines.append("")
    lines.append("┌─────────────── MEASURED RESONANT PEAKS (from PSD) ──────────────┐")
    lines.append("│  Peak │  Freq (Hz) │  Level (dB) │  Prominence │  Q Factor     │")
    lines.append("├───────┼────────────┼─────────────┼─────────────┼───────────────┤")
    
    for i, p in enumerate(metrics[:5]):
        lines.append(f"│  {i+1:>3}  │  {p['freq_hz']:>8.2f}  │  {p['peak_db']:>9.2f}  │  {p['prominence_db']:>8.2f}  │  {p['q_factor']:>7.1f}      │")
    
    lines.append("└───────┴────────────┴─────────────┴─────────────┴───────────────┘")
    lines.append("")
    lines.append("┌─────────────── FILTER COEFFICIENTS ─────────────────────────────┐")
    lines.append("│  Comb Filter:  y[n] = x[n] + 0.55·y[n − 154]  (3.2ms @48kHz)    │")
    lines.append("│  Shell BPF:    Bessel 2nd-order, fc = Variable (3.2×fundamental)  │")
    lines.append("│  Friction HP:  Butterworth 4th-order, fc = 2kHz                   │")
    lines.append("│  Reverb:       4 parallel comb (21/37/45/53ms) + AP (6ms)        │")
    lines.append("└──────────────────────────────────────────────────────────────────┘")
    lines.append("")
    lines.append("┌─────────────── NOTE SEQUENCE ──────────────────────────────────┐")
    
    for i, (name, hz) in enumerate(zip(NOTE_NAMES, NOTES_HZ)):
        midi_note = 60 + i * 0  # will compute properly
        midi_note = max(60, round(12 * np.log2(hz / 440) + 69))
        lines.append(f"│  {i+1:>2}. {name:<4}  {hz:>7.2f} Hz  ◉ MIDI {midi_note:<3}  Quarter note{' ' if i % 2 == 0 else ''}              │")
    
    lines.append("└──────────────────────────────────────────────────────────────────┘")
    lines.append("")
    lines.append(f"  Sample Rate: {SAMPLE_RATE} Hz  |  Bit Depth: {BIT_DEPTH}-bit")
    lines.append(f"  Duration: {TOTAL_SECONDS:.2f}s  |  BPM: {BPM}")
    lines.append("  Export formats: WAV (24-bit), OGG (Vorbis q7), Opus (256k), MIDI")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 66)
    print("  DAILY DSP RESEARCH — Resonant Glass Armonica")
    print("  Physical Model: Multi-Modal Glass Bowl Simulation")
    print("=" * 66)
    print()
    
    modal_params = get_glass_mode_ratios()
    
    # Compose
    print("[1/5] Composing 2-bar melodic pattern...")
    audio = compose_melodic_pattern()
    print()
    
    # Compute metrics
    print("[2/5] Computing resonant peak metrics...")
    metrics = compute_metrics(audio)
    print(f"  Found {len(metrics)} resonant peaks")
    for p in metrics:
        print(f"    {p['freq_hz']:>8.2f} Hz  (Q={p['q_factor']:.1f}, prominence={p['prominence_db']:.1f} dB)")
    print()
    
    # Export WAV
    print("[3/5] Exporting audio...")
    wav_file = f"{INSTRUMENT_NAME}_{DATE_TAG}.wav"
    export_wav(audio, wav_file)
    
    # Export OGG
    ogg_file = f"{INSTRUMENT_NAME}_{DATE_TAG}.ogg"
    export_ogg(audio, ogg_file)
    
    # Export Opus (HQ)
    opus_file = f"{INSTRUMENT_NAME}_{DATE_TAG}.opus"
    export_ogg(audio, opus_file)
    print()
    
    # Export MIDI
    print("[4/5] Exporting MIDI...")
    midi_file = f"{INSTRUMENT_NAME}_{DATE_TAG}.mid"
    export_midi(midi_file)
    print()
    
    # Build system graph
    print("[5/5] Building DSP system graph...")
    graph = build_system_graph(metrics, modal_params)
    print()
    print(graph)
    print()
    
    # Save system graph as JSON report
    report = {
        "instrument": "Resonant Glass Armonica",
        "date": DATE_TAG,
        "sample_rate": SAMPLE_RATE,
        "bpm": BPM,
        "duration_sec": TOTAL_SECONDS,
        "notes": [{"name": n, "freq_hz": f} for n, f in zip(NOTE_NAMES, NOTES_HZ)],
        "modal_parameters": {
            "ratios": modal_params["ratios"],
            "weights": modal_params["weights"],
            "q_factors": modal_params["q_factors"]
        },
        "resonant_peaks": metrics,
        "files": {
            "wav": str(wav_file),
            "ogg": str(ogg_file),
            "opus": str(opus_file),
            "midi": str(midi_file)
        }
    }
    
    report_path = OUTPUT_DIR / f"{INSTRUMENT_NAME}_{DATE_TAG}_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  Report: {report_path}")
    print()
    print("=" * 66)
    print("  Experiment complete.")
    print("=" * 66)
    
    return audio, graph, metrics


if __name__ == "__main__":
    main()