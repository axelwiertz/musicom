"""Aperiodic Granular Synthesis Engine (SP-013).

Splits audio into micro-sonic grains (10-100ms) and schedules them using stochastic,
non-periodic (aperiodic) time intervals and jitter. Creates dense, evolving ambient
textures and clouds.
"""

import numpy as np
import random
import os

from ..utils.io import read_wav, write_wav


class AperiodicGranulator:
    """
    Aperiodic Granular Synthesis Engine for Sound (WAV) Production.
    Takes a source audio buffer and scatters it stochastically to generate
    dense, evolving ambient textures and clouds.
    """
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_cloud(self, 
                       source_path: str, 
                       output_path: str, 
                       duration_sec: float = 10.0,
                       grain_size_ms: float = 50.0,
                       density_grains_per_sec: int = 100,
                       pitch_shift_semi: float = 0.0,
                       position_jitter_ms: float = 50.0,
                       grain_jitter_ms: float = 10.0) -> str:
        """
        Synthesizes an aperiodic granular cloud from a source WAV file.
        
        Args:
            source_path: Path to source WAV file
            output_path: Output WAV path
            duration_sec: Output duration in seconds
            grain_size_ms: Base grain size in milliseconds
            density_grains_per_sec: Number of grains per second
            pitch_shift_semi: Pitch shift in semitones
            position_jitter_ms: Position jitter in milliseconds
            grain_jitter_ms: Grain size jitter in milliseconds
            
        Returns:
            Path to output WAV file
        """
        # Load source WAV
        data, sr = read_wav(source_path)
        if data.ndim == 2:
            data = data.mean(axis=1)  # fold stereo source to mono for granular
        
        # Resample if needed
        if sr != self.sample_rate:
            # Simple linear resampling
            ratio = self.sample_rate / sr
            new_len = int(len(data) * ratio)
            x_old = np.linspace(0, 1, len(data))
            x_new = np.linspace(0, 1, new_len)
            data = np.interp(x_new, x_old, data)
            sr = self.sample_rate

        total_samples = int(duration_sec * self.sample_rate)
        output_buffer = np.zeros(total_samples, dtype=np.float32)
        grain_len_base = int((grain_size_ms / 1000.0) * self.sample_rate)
        
        total_grains = int(duration_sec * density_grains_per_sec)
        
        # Stochastic aperiodic scheduling
        start_times_sec = np.sort(np.random.uniform(0.0, duration_sec - (grain_size_ms/1000.0), total_grains))
        
        for start_sec in start_times_sec:
            # Current playhead relative to total source file
            playhead_ratio = start_sec / duration_sec
            source_center_sample = int(playhead_ratio * len(data))
            
            # Apply position jitter
            pos_jitter_samples = int((random.uniform(-position_jitter_ms, position_jitter_ms) / 1000.0) * self.sample_rate)
            source_idx = self._clip_idx(source_center_sample + pos_jitter_samples, 0, len(data) - 1)
            
            # Apply grain size jitter
            g_jitter_samples = int((random.uniform(-grain_jitter_ms, grain_jitter_ms) / 1000.0) * self.sample_rate)
            grain_len = max(100, grain_len_base + g_jitter_samples)
            
            # Extraction boundary
            if source_idx + grain_len > len(data):
                source_idx = len(data) - grain_len
                
            grain = data[source_idx:source_idx+grain_len]
            
            # Apply Hanning window to prevent transient clicks
            window = np.hanning(grain_len)
            grain_windowed = grain * window
            
            # Pitch shifting / resampling simulation (microtonal scaling)
            if pitch_shift_semi != 0.0:
                scale_factor = 2 ** (pitch_shift_semi / 12.0)
                xp = np.arange(len(grain_windowed))
                new_len = int(len(grain_windowed) / scale_factor)
                if new_len > 10:
                    x = np.linspace(0, len(grain_windowed) - 1, new_len)
                    grain_windowed = np.interp(x, xp, grain_windowed)
                    grain_len = len(grain_windowed)
            
            # Target output projection
            target_start = int(start_sec * self.sample_rate)
            if target_start + grain_len > total_samples:
                grain_len = total_samples - target_start
                grain_windowed = grain_windowed[:grain_len]
                
            if grain_len > 0:
                output_buffer[target_start:target_start+grain_len] += grain_windowed
                
        # Normalize to avoid clipping
        max_val = np.max(np.abs(output_buffer))
        if max_val > 0:
            output_buffer = output_buffer / max_val * 0.9
            
        # Write output WAV
        write_wav(output_path, output_buffer, self.sample_rate, normalize=False)
        
        return output_path
    
    @staticmethod
    def _clip_idx(val: int, low: int, high: int) -> int:
        return min(max(val, low), high)


if __name__ == "__main__":
    # Example usage
    granulator = AperiodicGranulator()
    # granulator.generate_cloud("source.wav", "cloud.wav", duration_sec=10.0)
    print("AperiodicGranulator ready. Call generate_cloud(source, output, ...) to use.")
