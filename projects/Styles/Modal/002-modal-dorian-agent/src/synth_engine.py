import numpy as np
import wave
import os
import sys

def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def generate_simple_wav(output_path, notes, sample_rate=44100):
    """
    notes: list of (midi_note, duration_sec, amplitude)
    """
    all_samples = []
    
    for midi_note, duration, amp in notes:
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        
        # Frequency
        freq = midi_to_freq(midi_note)
        
        # Sine wave
        samples = amp * np.sin(2 * np.pi * freq * t)
        
        # Simple ADSR Envelope (Attack/Release only)
        attack_len = int(0.05 * sample_rate)
        release_len = int(0.1 * sample_rate)
        
        if len(samples) > (attack_len + release_len):
            envelope = np.ones_like(samples)
            envelope[:attack_len] = np.linspace(0, 1, attack_len)
            envelope[-release_len:] = np.linspace(1, 0, release_len)
            samples *= envelope
            
        all_samples.append(samples)
        
    final_signal = np.concatenate(all_samples)
    final_signal = np.clip(final_signal, -1, 1)
    final_signal = (final_signal * 32767).astype(np.int16)
    
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(final_signal.tobytes())

if __name__ == "__main__":
    # Example: C Major Triad (C4, E4, G4)
    test_notes = [(60, 0.5, 0.5), (64, 0.5, 0.5), (67, 1.0, 0.5)]
    os.makedirs("/tmp/musicom_analysis", exist_ok=True)
    target = "/tmp/musicom_analysis/test_triad.wav"
    generate_simple_wav(target, test_notes)
    print(f"Generated: {target}")
