"""Audio I/O utilities - WAV reading/writing and format handling.

Consolidates WAV I/O logic from across the codebase.
"""

import os
import wave
import struct
import numpy as np
from typing import Tuple, Optional


def read_wav(filepath: str) -> Tuple[np.ndarray, int]:
    """Read WAV file and return audio data as numpy array.
    
    Args:
        filepath: Path to WAV file
        
    Returns:
        Tuple of (audio_data, sample_rate)
        audio_data is float32 normalized to [-1, 1]; mono → 1D,
        stereo → [n, 2] (channels preserved)
    """
    try:
        import scipy.io.wavfile as wavfile
        sr, data = wavfile.read(filepath)
        
        # Convert to float32 normalized
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0
        elif data.dtype == np.float32:
            pass  # Already normalized
        else:
            # Unknown format, try to normalize
            max_val = np.max(np.abs(data))
            if max_val > 0:
                data = data.astype(np.float32) / max_val
        
        # Keep channel layout: 1D mono, [n,2] stereo (no silent mono-fold)
        return data, sr
        
    except ImportError:
        # Fallback to stdlib wave
        with wave.open(filepath, 'rb') as wf:
            sr = wf.getframerate()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            n_frames = wf.getnframes()
            
            raw_data = wf.readframes(n_frames)
            
            if sampwidth == 2:
                dtype = np.int16
                max_val = 32768.0
            elif sampwidth == 4:
                dtype = np.int32
                max_val = 2147483648.0
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")
            
            data = np.frombuffer(raw_data, dtype=dtype)
            data = data.astype(np.float32) / max_val
            
            if n_channels > 1:
                data = data.reshape(-1, n_channels)  # keep stereo [n,2]
                
        return data, sr


def write_wav(filepath: str, audio_data: np.ndarray, sample_rate: int, 
              normalize: bool = True) -> str:
    """Write audio data to WAV file.
    
    Args:
        filepath: Output path
        audio_data: Audio data (float32 or int16)
        sample_rate: Sample rate in Hz
        normalize: If True, normalize to [-1, 1] before writing
        
    Returns:
        Path to written file
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    # Convert to float32 if needed
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    
    # Normalize if requested
    if normalize:
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.95  # Leave headroom

    # Clip to [-1, 1]
    audio_data = np.clip(audio_data, -1.0, 1.0)

    # Convert to int16 (preserve channel count: 1D=mono, [n,2]=stereo)
    audio_i16 = (audio_data * 32767).astype(np.int16)

    try:
        import scipy.io.wavfile as wavfile
        wavfile.write(filepath, sample_rate, audio_i16)
    except ImportError:
        # Fallback to stdlib wave
        n_channels = 2 if audio_i16.ndim == 2 else 1
        if n_channels == 2:
            # Interleave L/R for stdlib wave: audio_i16.T = [2,n] → ravel = L0,R0,L1,R1...
            raw = audio_i16.T.ravel().tobytes()
        else:
            raw = audio_i16.tobytes()
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(raw)
    
    return filepath


def normalize_audio(audio_data: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    """Normalize audio to target peak amplitude.
    
    Args:
        audio_data: Audio data (float32)
        target_peak: Target peak amplitude (default 0.95 for headroom)
        
    Returns:
        Normalized audio data
    """
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        return audio_data / max_val * target_peak
    return audio_data


__all__ = [
    "read_wav",
    "write_wav",
    "normalize_audio",
]
