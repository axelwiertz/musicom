# -*- coding: utf-8 -*-
"""
SP-013: Feedback Delay Line with High-Frequency Damping
Post-processing DSP effect applied to rendered WAV.

Simulates analog tape delay where higher frequencies are absorbed
more rapidly than lower frequencies. Creates warm, organic delay tails.
"""
import numpy as np
import wave
import os

# SP-013 Parameters
DELAY_MS = 375          # Delay time (3/8 note at 100 BPM = 0.375s)
FEEDBACK_GAIN = 0.45    # Feedback amount (0.0 to 1.0)
LP_COEFFICIENT = 0.3    # Low-pass filter cutoff (0.0 to 1.0, lower = darker)


def apply_feedback_delay_damped(audio, sr, delay_ms, feedback_gain, lp_coeff):
    """
    Apply feedback delay with high-frequency damping.
    
    audio: 1D or 2D numpy array (mono or stereo)
    sr: sample rate
    delay_ms: delay time in milliseconds
    feedback_gain: feedback amount (0.0 to 1.0)
    lp_coeff: low-pass filter coefficient (0.0 to 1.0, lower = darker)
    
    Returns: processed audio array
    """
    delay_samples = int(delay_ms * sr / 1000.0)
    
    if audio.ndim == 1:
        # Mono processing
        return _process_channel(audio, delay_samples, feedback_gain, lp_coeff)
    else:
        # Stereo: process each channel independently
        left = _process_channel(audio[:, 0], delay_samples, feedback_gain, lp_coeff)
        right = _process_channel(audio[:, 1], delay_samples, feedback_gain, lp_coeff)
        return np.column_stack([left, right])


def _process_channel(channel_data, delay_samples, feedback_gain, lp_coeff):
    """Process a single audio channel with damped feedback delay."""
    n = len(channel_data)
    output = np.zeros(n, dtype=np.float32)
    delay_buffer = np.zeros(delay_samples, dtype=np.float32)
    last_filter_out = 0.0
    
    for i in range(n):
        # Read from circular delay buffer
        delayed_sample = delay_buffer[i % delay_samples]
        
        # Apply low-pass filter to feedback (HF damping)
        filtered_delayed = lp_coeff * delayed_sample + (1.0 - lp_coeff) * last_filter_out
        last_filter_out = filtered_delayed
        
        # Output = dry + filtered delayed
        output[i] = channel_data[i] + feedback_gain * filtered_delayed
        
        # Write back to delay buffer
        delay_buffer[i % delay_samples] = channel_data[i] + feedback_gain * filtered_delayed
    
    return output


def normalize_peak(audio, target_db=-1.0):
    """Normalize audio to target peak level in dB."""
    target_linear = 10.0 ** (target_db / 20.0)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (target_linear / peak)
    return audio


def main():
    input_wav = "/opt/data/projects/Styles/Experimental/055-neural-spiking-delay/Audio/055-neural-spiking-delay.wav"
    output_wav = "/opt/data/projects/Styles/Experimental/055-neural-spiking-delay/Audio/055-neural-spiking-delay_normalized.wav"
    
    # Read WAV
    with wave.open(input_wav, 'rb') as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)
    
    # Convert to float32
    if sample_width == 2:
        audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(raw_data, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Reshape if stereo
    if n_channels == 2:
        audio = audio.reshape(-1, 2)
    
    print(f"Input: {n_channels}ch, {sr}Hz, {len(audio)} samples")
    
    # Apply SP-013: Feedback Delay with HF Damping
    audio_processed = apply_feedback_delay_damped(
        audio, sr, DELAY_MS, FEEDBACK_GAIN, LP_COEFFICIENT
    )
    
    # Normalize to -1dB
    audio_normalized = normalize_peak(audio_processed, target_db=-1.0)
    
    # Convert back to int16
    if n_channels == 2:
        audio_int16 = (audio_normalized * 32767).astype(np.int16).flatten()
    else:
        audio_int16 = (audio_normalized * 32767).astype(np.int16)
    
    # Write normalized WAV
    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    
    print(f"Output: {output_wav}")
    print(f"SP-013 applied: delay={DELAY_MS}ms, feedback={FEEDBACK_GAIN}, lp={LP_COEFFICIENT}")


if __name__ == "__main__":
    main()
