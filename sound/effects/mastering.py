"""Mastering-stage DSP: dynamic EQ, stereo imaging, limiting, LUFS metering.

Professional mastering tools for final polish and loudness standards compliance.
Based on ITU-R BS.1770-4 loudness measurement and common mastering practices.

Usage:
    # LUFS metering
    lufs = measure_lufs(audio, sample_rate=44100)
    
    # Dynamic EQ
    deq = DynamicEQ(sample_rate=44100)
    deq.add_band(400, q=2.0, threshold_db=-12, ratio=2.0)
    processed = deq.process(audio)
    
    # Stereo imaging (mono-safe)
    imager = StereoImager(sample_rate=44100)
    imager.set_width(0.0, below_hz=100)   # Mono sub-bass
    imager.set_width(1.5, above_hz=2000)  # Widen highs
    stereo = imager.process(mono_audio)
    
    # Limiter
    limiter = Limiter(threshold_db=-1.0, release_ms=100)
    limited = limiter.process(audio)
"""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass


# =============================================================================
# LUFS Metering (ITU-R BS.1770-4)
# =============================================================================

@dataclass
class LoudnessMetrics:
    """Loudness measurement results."""
    integrated_lufs: float      # Overall loudness (LUFS)
    loudness_range: float       # LRA (LU)
    true_peak_db: float         # True peak (dBTP)
    short_term_max: float       # Max 3s short-term loudness
    momentary_max: float        # Max 400ms momentary loudness


class LUFSMeter:
    """
    ITU-R BS.1770-4 loudness meter.
    
    Measures integrated loudness (LUFS), loudness range (LRA),
    true peak (dBTP), and short-term/momentary maxima.
    
    Streaming platform targets:
    - Spotify: -14 LUFS
    - Apple Music: -16 LUFS
    - YouTube: -14 LUFS
    - Tidal: -14 LUFS (normal), -1 LUFS (max)
    """
    
    # K-weighting filter coefficients (44100 Hz)
    # Stage 1: High-shelf boost (+4 dB above 1.5 kHz)
    # Stage 2: High-pass filter (-3 dB at 38 Hz)
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup K-weighting filters for the given sample rate."""
        # Simplified K-weighting using biquad coefficients
        # For accurate implementation, use scipy.signal
        try:
            from scipy.signal import lfilter, butter
            
            # Stage 1: High-shelf (approximation)
            # Boost +4 dB above 1.5 kHz
            self.hs_b, self.hs_a = self._high_shelf(1500, 4.0, self.sample_rate)
            
            # Stage 2: High-pass at 38 Hz
            self.hp_b, self.hp_a = butter(2, 38, btype='high', fs=self.sample_rate)
            
        except ImportError:
            # Fallback: no filtering (less accurate)
            self.hs_b = self.hs_a = np.array([1.0])
            self.hp_b = self.hp_a = np.array([1.0])
    
    def _high_shelf(self, freq: float, gain_db: float, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """Design high-shelf filter coefficients."""
        from scipy.signal import iirfilter
        
        # Approximate high-shelf using peaking EQ
        A = 10 ** (gain_db / 40.0)
        w0 = 2 * np.pi * freq / sr
        alpha = np.sin(w0) / 2 * np.sqrt(2)  # Q = 0.707
        
        b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
        b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
        a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        
        return np.array([b0/a0, b1/a0, b2/a0]), np.array([1.0, a1/a0, a2/a0])
    
    def _apply_k_weighting(self, audio: np.ndarray) -> np.ndarray:
        """Apply K-weighting filters to audio."""
        from scipy.signal import lfilter
        
        # Apply high-shelf then high-pass
        filtered = lfilter(self.hs_b, self.hs_a, audio)
        filtered = lfilter(self.hp_b, self.hp_a, filtered)
        return filtered
    
    def _measure_block(self, audio: np.ndarray) -> float:
        """Measure loudness of a single block in LUFS."""
        # Apply K-weighting
        filtered = self._apply_k_weighting(audio)
        
        # Mean square (RMS squared)
        if len(filtered.shape) > 1:
            # Stereo: sum of squares per channel, then mean
            mean_sq = np.mean(filtered ** 2, axis=0)
            mean_sq = np.mean(mean_sq)
        else:
            mean_sq = np.mean(filtered ** 2)
        
        # LUFS = -0.691 + 10 * log10(mean_sq)
        if mean_sq > 0:
            return -0.691 + 10 * np.log10(mean_sq)
        return -70.0  # Silence
    
    def measure(self, audio: np.ndarray) -> LoudnessMetrics:
        """
        Measure loudness metrics for audio.
        
        Args:
            audio: Input audio (mono or stereo), float32/64
            
        Returns:
            LoudnessMetrics with integrated LUFS, LRA, true peak, etc.
        """
        sr = self.sample_rate
        
        # Ensure float64 for precision
        audio = audio.astype(np.float64)
        
        # Integrated loudness (400ms blocks with 75% overlap)
        block_size = int(0.4 * sr)
        hop_size = int(0.1 * sr)  # 75% overlap
        
        n_blocks = max(1, (len(audio) - block_size) // hop_size + 1)
        block_loudness = []
        
        for i in range(n_blocks):
            start = i * hop_size
            end = start + block_size
            if end > len(audio):
                break
            block = audio[start:end]
            lufs = self._measure_block(block)
            if lufs > -70.0:  # Skip silence
                block_loudness.append(lufs)
        
        # Integrated loudness: average of blocks above -70 LUFS
        if block_loudness:
            # Apply gating (remove blocks 10 LU below threshold)
            threshold = np.mean(block_loudness) - 10.0
            gated = [l for l in block_loudness if l > threshold]
            integrated = np.mean(gated) if gated else -70.0
        else:
            integrated = -70.0
        
        # Loudness Range (LRA)
        # Use 3s blocks with 100ms hop
        lra_block_size = int(3.0 * sr)
        lra_hop = int(0.1 * sr)
        lra_blocks = []
        
        for i in range(max(1, (len(audio) - lra_block_size) // lra_hop + 1)):
            start = i * lra_hop
            end = start + lra_block_size
            if end > len(audio):
                break
            block = audio[start:end]
            lufs = self._measure_block(block)
            if lufs > -70.0:
                lra_blocks.append(lufs)
        
        if len(lra_blocks) >= 2:
            lra_blocks.sort()
            # 10th and 95th percentiles
            p10 = lra_blocks[int(0.1 * len(lra_blocks))]
            p95 = lra_blocks[int(0.95 * len(lra_blocks))]
            lra = p95 - p10
        else:
            lra = 0.0
        
        # True peak (sample peak approximation)
        true_peak = np.max(np.abs(audio))
        true_peak_db = 20 * np.log10(true_peak) if true_peak > 0 else -70.0
        
        # Short-term max (3s)
        short_blocks = []
        st_block_size = int(3.0 * sr)
        for i in range(max(1, len(audio) // st_block_size)):
            block = audio[i*st_block_size:(i+1)*st_block_size]
            if len(block) > 0:
                short_blocks.append(self._measure_block(block))
        short_max = max(short_blocks) if short_blocks else -70.0
        
        # Momentary max (400ms)
        mom_blocks = []
        mom_block_size = int(0.4 * sr)
        for i in range(max(1, len(audio) // mom_block_size)):
            block = audio[i*mom_block_size:(i+1)*mom_block_size]
            if len(block) > 0:
                mom_blocks.append(self._measure_block(block))
        mom_max = max(mom_blocks) if mom_blocks else -70.0
        
        return LoudnessMetrics(
            integrated_lufs=integrated,
            loudness_range=lra,
            true_peak_db=true_peak_db,
            short_term_max=short_max,
            momentary_max=mom_max
        )


def measure_lufs(audio: np.ndarray, sample_rate: int = 44100) -> float:
    """Convenience function: measure integrated loudness in LUFS."""
    meter = LUFSMeter(sample_rate)
    return meter.measure(audio).integrated_lufs


def normalize_to_lufs(audio: np.ndarray, target_lufs: float = -14.0,
                      sample_rate: int = 44100) -> np.ndarray:
    """
    Normalize audio to target LUFS level.
    
    Args:
        audio: Input audio
        target_lufs: Target loudness in LUFS (default -14 for Spotify)
        sample_rate: Sample rate
        
    Returns:
        Normalized audio
    """
    current_lufs = measure_lufs(audio, sample_rate)
    gain_db = target_lufs - current_lufs
    gain_linear = 10 ** (gain_db / 20.0)
    return audio * gain_linear


# =============================================================================
# Stereo Imaging
# =============================================================================

class StereoImager:
    """
    Mono-safe stereo width control.
    
    Allows different width settings for different frequency bands.
    Critical for mastering: keeps sub-bass mono (phase-safe) while
    allowing width in highs.
    
    Rules:
    - Below 100 Hz: Always mono (0.0 width)
    - 100-250 Hz: Small mono-compatible width OK
    - Above 2 kHz: Can widen significantly
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.width_settings: List[Tuple[float, float, float]] = []  # (below_hz, above_hz, width)
    
    def set_width(self, width: float, below_hz: Optional[float] = None,
                  above_hz: Optional[float] = None):
        """
        Set stereo width for a frequency band.

        Args:
            width: 0.0 = mono, 1.0 = normal stereo, >1.0 = widened
            below_hz: Apply to frequencies below this (None = no lower bound)
            above_hz: Apply to frequencies above this (None = no upper bound)

        Band semantics:
            set_width(w, below_hz=X)          → [0, X]
            set_width(w, above_hz=X)          → [X, nyquist]
            set_width(w, below_hz=X, above_hz=Y) → [X, Y]
        """
        nyq = self.sample_rate / 2
        if below_hz is None and above_hz is not None:
            lo, hi = float(above_hz), nyq   # "above X only"
        elif below_hz is not None and above_hz is None:
            lo, hi = 0.0, float(below_hz)   # "below X only"
        elif below_hz is None and above_hz is None:
            lo, hi = 0.0, nyq               # full band
        else:
            # both provided (below_hz and above_hz are non-None here)
            lo = below_hz if below_hz is not None else 0.0
            hi = above_hz if above_hz is not None else nyq
            lo, hi = float(lo), float(hi)   # explicit range (both given)
        self.width_settings.append((lo, hi, width))
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply stereo imaging to audio.
        
        Args:
            audio: Input audio (mono or stereo)
            
        Returns:
            Stereo audio (2D array, shape [samples, 2])
        """
        # Convert mono to stereo if needed
        if len(audio.shape) == 1:
            stereo = np.column_stack([audio, audio])
        else:
            stereo = audio.copy()
        
        if not self.width_settings:
            return stereo
        
        # Simple mid/side processing
        mid = (stereo[:, 0] + stereo[:, 1]) * 0.5
        side = (stereo[:, 0] - stereo[:, 1]) * 0.5
        
        # Per-band width via FFT split: each width_setting applies to its
        # frequency band independently (mono sub, widened highs, etc.).
        # (Previously: sequential side *= width across ALL settings — a bug
        # that collapsed any multi-band config to side=0.)
        n = len(side)
        side_fft = np.fft.rfft(side)
        freqs = np.fft.rfftfreq(n, 1 / self.sample_rate)
        nyq = self.sample_rate / 2
        
        # Build per-frequency width multiplier (start at 1.0 = unchanged)
        width_curve = np.ones(len(freqs), dtype=np.float64)
        for below_hz, above_hz, width in self.width_settings:
            lo = max(0.0, below_hz)
            hi = min(nyq, above_hz)
            mask = (freqs >= lo) & (freqs <= hi)
            width_curve[mask] = width
        
        side_fft = side_fft * width_curve
        side = np.fft.irfft(side_fft, n=n)
        
        # Reconstruct stereo from mid/side
        left = mid + side
        right = mid - side
        
        return np.column_stack([left, right])


# =============================================================================
# Limiter
# =============================================================================

class Limiter:
    """
    Transparent peak limiter with lookahead.
    
    Prevents clipping while preserving transients.
    Used as final stage in mastering chain.
    """
    
    def __init__(self, threshold_db: float = -1.0, release_ms: float = 100.0,
                 sample_rate: int = 44100):
        """
        Args:
            threshold_db: Ceiling in dB (typically -1.0 to -0.1)
            release_ms: Release time in milliseconds
            sample_rate: Sample rate
        """
        self.threshold_db = threshold_db
        self.release_ms = release_ms
        self.sample_rate = sample_rate
        self.threshold_linear = 10 ** (threshold_db / 20.0)
        self.release_coeff = np.exp(-1.0 / (release_ms * 0.001 * sample_rate))
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply limiting to audio.
        
        Args:
            audio: Input audio (mono or stereo)
            
        Returns:
            Limited audio (peaks at threshold_db)
        """
        output = audio.copy()
        
        # Compute envelope
        if len(audio.shape) > 1:
            envelope = np.max(np.abs(audio), axis=1)
        else:
            envelope = np.abs(audio)
        
        # Apply release smoothing
        smoothed = np.zeros_like(envelope)
        smoothed[0] = envelope[0]
        for i in range(1, len(envelope)):
            if envelope[i] > smoothed[i-1]:
                smoothed[i] = envelope[i]  # Fast attack
            else:
                smoothed[i] = smoothed[i-1] * self.release_coeff + envelope[i] * (1 - self.release_coeff)
        
        # Compute gain reduction
        gain = np.ones_like(smoothed)
        mask = smoothed > self.threshold_linear
        gain[mask] = self.threshold_linear / smoothed[mask]
        
        # Apply gain
        if len(output.shape) > 1:
            output *= gain[:, np.newaxis]
        else:
            output *= gain
        
        return output


# =============================================================================
# Dynamic EQ
# =============================================================================

class DynamicEQ:
    """
    Dynamic equalizer — frequency-band compression.
    
    Only reduces gain when signal exceeds threshold in that band.
    Unlike static EQ, doesn't permanently dull the track.
    
    Use cases:
    - Tame harsh resonances (2-5 kHz)
    - Reduce boxiness (300-500 Hz)
    - Control boomy bass notes
    """
    
    @dataclass
    class Band:
        """Dynamic EQ band configuration."""
        center_freq: float
        q: float
        threshold_db: float
        ratio: float
        attack_ms: float = 10.0
        release_ms: float = 100.0
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bands: List[DynamicEQ.Band] = []
    
    def add_band(self, center_freq: float, q: float = 2.0,
                 threshold_db: float = -12.0, ratio: float = 2.0,
                 attack_ms: float = 10.0, release_ms: float = 100.0):
        """
        Add a dynamic EQ band.
        
        Args:
            center_freq: Center frequency in Hz
            q: Q factor (bandwidth)
            threshold_db: Threshold in dB
            ratio: Compression ratio (e.g., 2.0 = 2:1)
            attack_ms: Attack time
            release_ms: Release time
        """
        self.bands.append(self.Band(
            center_freq, q, threshold_db, ratio, attack_ms, release_ms
        ))
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply dynamic EQ to audio.

        Args:
            audio: Input audio (mono 1D or stereo [n, 2])

        Returns:
            Processed audio
        """
        from scipy.signal import lfilter, butter

        is_stereo = len(audio.shape) > 1 and audio.shape[1] == 2
        if is_stereo:
            # Process per channel with the same band config (independent L/R).
            left = self.process(audio[:, 0])
            right = self.process(audio[:, 1])
            return np.column_stack([left, right])

        output = audio.copy()
        
        for band in self.bands:
            # Design bandpass filter for this band
            bw = band.center_freq / band.q
            low = max(20, band.center_freq - bw / 2)
            high = min(self.sample_rate / 2 - 1, band.center_freq + bw / 2)
            
            b, a = butter(2, [low, high], btype='band', fs=self.sample_rate)
            
            # Extract band
            band_signal = lfilter(b, a, output)
            
            # Compute envelope
            envelope = np.abs(band_signal)
            
            # Smooth envelope
            attack_samples = int(band.attack_ms * 0.001 * self.sample_rate)
            release_samples = int(band.release_ms * 0.001 * self.sample_rate)
            
            smoothed = np.zeros_like(envelope)
            smoothed[0] = envelope[0]
            for i in range(1, len(envelope)):
                if envelope[i] > smoothed[i-1]:
                    coeff = np.exp(-1.0 / attack_samples) if attack_samples > 0 else 0.0
                else:
                    coeff = np.exp(-1.0 / release_samples) if release_samples > 0 else 0.0
                smoothed[i] = smoothed[i-1] * coeff + envelope[i] * (1 - coeff)
            
            # Compute gain reduction
            threshold_linear = 10 ** (band.threshold_db / 20.0)
            gain = np.ones_like(smoothed)
            mask = smoothed > threshold_linear
            
            # Apply ratio
            over_db = 20 * np.log10(smoothed[mask] / threshold_linear)
            reduced_db = over_db / band.ratio
            gain[mask] = 10 ** (reduced_db / 20.0) * threshold_linear / smoothed[mask]
            
            # Apply gain to band
            if len(output.shape) > 1:
                output += band_signal * (gain[:, np.newaxis] - 1)
            else:
                output += band_signal * (gain - 1)
        
        return output


# =============================================================================
# Mastering Chain
# =============================================================================

class MasteringChain:
    """
    Orchestrate mastering processing in sequence.
    
    Typical chain:
    1. Dynamic EQ (remove resonances)
    2. Stereo imager (mono-safe width)
    3. Limiter (peak control)
    4. LUFS normalization (target loudness)
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.stages = []
    
    def add_dynamic_eq(self, **kwargs) -> 'MasteringChain':
        """Add dynamic EQ stage."""
        deq = DynamicEQ(self.sample_rate)
        self.stages.append(('dynamic_eq', deq, kwargs))
        return self
    
    def add_stereo_imager(self, **kwargs) -> 'MasteringChain':
        """Add stereo imager stage."""
        imager = StereoImager(self.sample_rate)
        self.stages.append(('stereo_imager', imager, kwargs))
        return self
    
    def add_limiter(self, threshold_db: float = -1.0, release_ms: float = 100.0) -> 'MasteringChain':
        """Add limiter stage."""
        limiter = Limiter(threshold_db, release_ms, self.sample_rate)
        self.stages.append(('limiter', limiter, {}))
        return self
    
    def process(self, audio: np.ndarray, target_lufs: Optional[float] = None) -> np.ndarray:
        """
        Process audio through mastering chain.
        
        Args:
            audio: Input audio
            target_lufs: Optional target loudness for final normalization
            
        Returns:
            Mastered audio
        """
        output = audio.copy()
        
        for stage_name, stage, kwargs in self.stages:
            if stage_name == 'dynamic_eq':
                output = stage.process(output)
            elif stage_name == 'stereo_imager':
                output = stage.process(output)
            elif stage_name == 'limiter':
                output = stage.process(output)
        
        # Final LUFS normalization
        if target_lufs is not None:
            output = normalize_to_lufs(output, target_lufs, self.sample_rate)
        
        return output


# =============================================================================
# Unified Master Stage (2026 streaming practice)
# =============================================================================

import math

LOUDNESS_TARGETS = {
    "streaming": -14.0,   # Spotify / YouTube / Tidal / Amazon
    "apple": -16.0,       # Apple Music
    "loud": -9.0,         # dense pop/hiphop (platform turns it down, sound stays dense)
    "dynamic": -18.0,     # folk / jazz / ambient / classical
}

# Genre → integrated LUFS target. Loud-first genres legitimately sit hotter
# (the platform normalizes them DOWN but the limiting that produced the
# loudness is baked in). Dynamic genres stay quiet on purpose.
GENRE_LUFS = {
    # dense / loud-first
    "pop": -9.0, "hiphop": -9.0, "trap": -8.0, "drill": -8.0, "phonk": -8.0,
    "edm": -9.0, "house": -10.0, "techno": -10.0, "disco": -11.0,
    "rock": -11.0, "amapiano": -11.0,
    # balanced
    "jazz": -14.0, "blues": -14.0, "soul": -13.0, "funk": -13.0,
    "chanson": -14.0, "country": -14.0, "reggae": -14.0, "latin": -13.0,
    # dynamic / quiet
    "ambient": -18.0, "classical": -18.0, "minimal": -18.0,
    "folk": -16.0, "solo": -16.0,
}


def target_for_style(style: Optional[str], fallback: float = -14.0) -> float:
    """Map a style name to its genre LUFS target (substring match)."""
    s = (style or "").lower().replace("_", " ").replace("-", " ")
    for key, val in GENRE_LUFS.items():
        if key in s:
            return float(val)
    return float(fallback)


def high_pass(audio: np.ndarray, cutoff_hz: float = 30.0,
              sample_rate: int = 44100) -> np.ndarray:
    """High-pass filter — remove inaudible sub-bass before the limiter.

    Sub energy below ~20-30 Hz wastes headroom and confuses lossy encoders
    (AAC/Ogg). Codec-safe mastering always trims it first.
    """
    from scipy.signal import butter, lfilter
    b, a = butter(2, cutoff_hz, btype="high", fs=sample_rate)
    if audio.ndim == 2:
        return np.column_stack([lfilter(b, a, audio[:, 0]),
                                lfilter(b, a, audio[:, 1])])
    return lfilter(b, a, audio)


def glue_compress(audio: np.ndarray, threshold_db: float = -18.0,
                  ratio: float = 2.0, attack_ms: float = 10.0,
                  release_ms: float = 150.0, sample_rate: int = 44100) -> np.ndarray:
    """Gentle soft-knee bus compressor — glue the mix (1-3 dB GR).

    Soft-knee gain computer on the peak envelope, then a one-pole smoothed
    gain-reduction signal. Fully vectorized; deterministic. Not a limiter.
    """
    from scipy.signal import lfilter
    mono = audio if audio.ndim == 1 else np.max(np.abs(audio), axis=1)
    env = np.abs(mono) + 1e-12
    env_db = 20.0 * np.log10(env)
    knee = 6.0
    over = env_db - threshold_db
    gr = np.zeros_like(env_db)
    hard = over > knee / 2.0
    soft = np.abs(over) <= knee / 2.0
    slope = 1.0 - 1.0 / ratio
    gr[hard] = (over[hard] - knee / 2.0) * slope
    gr[soft] = ((over[soft] + knee / 2.0) ** 2) / (2.0 * knee) * slope
    gr = np.maximum(gr, 0.0)
    # smooth gain reduction (one-pole, release-dominant)
    alpha = np.exp(-1.0 / (release_ms * 0.001 * sample_rate))
    gr_s = lfilter([1.0 - alpha], [1.0, -alpha], gr)
    gain = 10.0 ** (-gr_s / 20.0)
    if audio.ndim == 2:
        return audio * gain[:, None]
    return audio * gain


def true_peak_limit(audio: np.ndarray, ceiling_db: float = -1.0,
                    oversample: int = 4, release_ms: float = 50.0,
                    sample_rate: int = 44100) -> np.ndarray:
    """True-peak limiter — inter-sample peak aware (ceil -1 dBTP).

    Oversamples the peak envelope 4x to reconstruct inter-sample peaks
    (the hidden spikes lossy encoders create), then peak-holds over the
    release window and applies a ceiling gain. Vectorized (np.interp +
    scipy.ndimage). Keeps reconstructed peaks at or below ceiling_db.
    """
    from scipy.ndimage import maximum_filter1d
    ceiling = 10.0 ** (ceiling_db / 20.0)
    mono = audio if audio.ndim == 1 else np.max(np.abs(audio), axis=1)
    n = len(mono)
    t = np.arange(n) / sample_rate
    t_up = np.arange(n * oversample) / (sample_rate * oversample)
    env_up = np.interp(t_up, t, mono)
    env = env_up[: n * oversample].reshape(n, oversample).max(axis=1)
    win = max(1, int(release_ms * 0.001 * sample_rate))
    peak = maximum_filter1d(env, size=win, mode="nearest")
    gain = np.minimum(1.0, ceiling / np.maximum(peak, 1e-12))
    if audio.ndim == 2:
        return audio * gain[:, None]
    return audio * gain


def master(audio: np.ndarray, target_lufs: float = -14.0,
           ceiling_db: float = -1.0, hp_hz: float = 30.0,
           glue: bool = True, stereo: bool = True,
           sample_rate: int = 44100):
    """Unified modern mastering stage (2026 streaming practice).

    Codec-safe chain order:
      1. high-pass sub cleanup (hp_hz)
      2. gentle glue compression (bus)
      3. mono-safe stereo imaging (mono sub, widened highs)
      4. LUFS normalization to target
      5. true-peak limiting to ceiling (-1 dBTP)

    Returns (mastered_audio, report) where report carries measured
    integrated LUFS, true-peak dBTP, and per-stage LUFS deltas.
    """
    out = np.asarray(audio, dtype=np.float64).copy()
    meter = LUFSMeter(sample_rate)
    report = {"stages": [], "target_lufs": float(target_lufs)}

    def snap(name):
        report["stages"].append({
            "name": name,
            "lufs": round(float(meter.measure(out).integrated_lufs), 2),
        })

    snap("input")
    out = high_pass(out, hp_hz, sample_rate); snap("highpass")
    if glue:
        out = glue_compress(out, sample_rate=sample_rate); snap("glue")
    if stereo:
        imager = StereoImager(sample_rate)
        imager.set_width(0.0, below_hz=100.0)
        imager.set_width(1.3, above_hz=3000.0)
        out = imager.process(out); snap("stereo")
    out = normalize_to_lufs(out, target_lufs, sample_rate); snap("lufs_norm")
    out = true_peak_limit(out, ceiling_db=ceiling_db, sample_rate=sample_rate)
    out = np.clip(out, -1.0, 1.0)
    snap("true_peak_limit")

    report["integrated_lufs"] = round(float(meter.measure(out).integrated_lufs), 2)
    report["true_peak_db"] = round(20.0 * math.log10(max(float(np.max(np.abs(out))), 1e-12)), 2)
    return out, report


if __name__ == "__main__":
    # Smoke test
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Create test signal: pink noise + sine
    noise = np.random.randn(len(t)) * 0.1
    sine = np.sin(2 * np.pi * 440 * t) * 0.3
    test_signal = noise + sine
    
    # Test LUFS meter
    print("=== LUFS Meter ===")
    meter = LUFSMeter(sr)
    metrics = meter.measure(test_signal)
    print(f"Integrated LUFS: {metrics.integrated_lufs:.1f}")
    print(f"Loudness range: {metrics.loudness_range:.1f} LU")
    print(f"True peak: {metrics.true_peak_db:.1f} dBTP")
    
    # Test normalization
    normalized = normalize_to_lufs(test_signal, target_lufs=-14.0, sample_rate=sr)
    new_lufs = measure_lufs(normalized, sr)
    print(f"After normalization: {new_lufs:.1f} LUFS (target: -14.0)")
    
    # Test limiter
    print("\n=== Limiter ===")
    limiter = Limiter(threshold_db=-1.0, release_ms=100, sample_rate=sr)
    limited = limiter.process(test_signal)
    peak_before = np.max(np.abs(test_signal))
    peak_after = np.max(np.abs(limited))
    print(f"Peak before: {20*np.log10(peak_before):.1f} dB")
    print(f"Peak after: {20*np.log10(peak_after):.1f} dB")
    
    print("\n✓ Mastering tools smoke test passed")
