"""FDN (feedback delay network) reverb — Rev Ocean 'Tidal' style.

Multi-stage diffusion via parallel delay lines with a feedback matrix,
modulated delay times, freeze (infinite sustain) and input ducking.

Usage:
    fdn = FDN(sample_rate=44100)
    wet = fdn.process(audio)
"""

import numpy as np
from typing import Optional

__all__ = ["FDN"]

# Prime-ish delay lengths (samples @ 44.1k) — spread for diffusion
_PRIME_DELAYS = [1471, 1693, 1871, 2053, 2237, 2399, 2593, 2797]


def _hadamard(n: int) -> np.ndarray:
    """Sylvester-Hadamard matrix (n must be power of 2), normalized."""
    h = np.array([[1.0]])
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    return h / np.sqrt(n)


class FDN:
    """Feedback delay network reverb."""

    def __init__(self, sample_rate: int = 44100, n_delays: int = 8):
        if n_delays & (n_delays - 1):
            raise ValueError("n_delays must be a power of 2 for Hadamard")
        self.sample_rate = sample_rate
        self.n_delays = n_delays

        scale = sample_rate / 44100.0
        self._base_delays = [max(1, int(d * scale))
                             for d in _PRIME_DELAYS[:n_delays]]
        # buffers hold delay + 1 for interpolation
        self._buffers = [np.zeros(d + 2) for d in self._base_delays]
        self._indices = [0] * n_delays

        # Normalized Hadamard feedback matrix
        self._matrix = _hadamard(n_delays)

        # One-pole LPF state per line (brightness)
        self._lp_state = np.zeros(n_delays)

        # Parameters
        self.size = 0.7          # 0-1, feedback gain
        self.decay = 0.5         # 0-1, tail length
        self.brightness = 0.8    # 0-1, high-frequency damping (1.0 = bright)
        self.modulation = 0.0    # 0-1, LFO depth on delay times
        self.freeze = False      # infinite sustain
        self.width = 0.8         # 0-1 stereo spread
        self.duck_amount = 0.0   # 0-1, input ducking
        self.wet_dry = 0.3

    def set(self, size: Optional[float] = None, decay: Optional[float] = None,
            brightness: Optional[float] = None, modulation: Optional[float] = None,
            freeze: Optional[bool] = None, width: Optional[float] = None,
            duck_amount: Optional[float] = None, wet_dry: Optional[float] = None):
        """Set any subset of reverb parameters."""
        if size is not None:
            self.size = size
        if decay is not None:
            self.decay = decay
        if brightness is not None:
            self.brightness = brightness
        if modulation is not None:
            self.modulation = modulation
        if freeze is not None:
            self.freeze = freeze
        if width is not None:
            self.width = width
        if duck_amount is not None:
            self.duck_amount = duck_amount
        if wet_dry is not None:
            self.wet_dry = wet_dry

    def reset(self):
        """Clear delay line state."""
        for i in range(self.n_delays):
            self._buffers[i].fill(0.0)
            self._indices[i] = 0
        self._lp_state.fill(0.0)

    def _feedback_gain(self) -> float:
        """Map size/decay to feedback gain per line."""
        if self.freeze:
            return 0.995
        base = 0.70 + 0.28 * self.size
        return base * (0.5 + 0.5 * self.decay)

    def _process_mono(self, audio: np.ndarray) -> np.ndarray:
        n = len(audio)
        out = np.zeros(n, dtype=np.float64)
        fb = self._feedback_gain()
        g = 1.0 - self.brightness
        mod_amp = self.modulation * 8.0  # max ±8 samples sweep
        sr = self.sample_rate

        # Ducking envelope
        duck_env = None
        if self.duck_amount > 0:
            env = np.abs(audio)
            k = np.exp(-1.0 / (0.05 * sr))  # 50ms follower
            duck_env = np.zeros(n)
            prev = 0.0
            for i in range(n):
                prev = env[i] + k * (prev - env[i])
                duck_env[i] = prev

        delays = np.array(self._base_delays, dtype=float)
        idx = np.array(self._indices, dtype=int)
        bufs = self._buffers
        lp = self._lp_state.copy()

        # LFO phase for modulation
        lfo_phase = 0.0
        lfo_inc = 2.0 * np.pi * 0.15 / sr  # 0.15 Hz slow movement

        for i in range(n):
            inp = float(audio[i])

            # Read taps with modulated delay
            if mod_amp > 0:
                mod = mod_amp * np.sin(lfo_phase)
                lfo_phase += lfo_inc
                read_d = np.clip(delays + mod, 1, None)
            else:
                read_d = delays

            taps = np.zeros(self.n_delays)
            for j in range(self.n_delays):
                rd = int(read_d[j])
                b = bufs[j]
                pos = idx[j] - rd
                taps[j] = b[pos % (len(b) - 2)]

            # Feedback matrix
            fb_in = self._matrix @ taps

            # Lowpass (brightness) + feedback
            lp = g * lp + (1.0 - g) * fb_in
            delayed = lp * fb

            # Write into delay lines
            for j in range(self.n_delays):
                b = bufs[j]
                b[idx[j] % (len(b) - 2)] = inp * 0.5 + delayed[j]
                idx[j] = (idx[j] + 1) % (len(b) - 2)

            wet = float(np.sum(taps)) / self.n_delays

            # Ducking: attenuate wet when input present
            if duck_env is not None:
                duck = 1.0 - self.duck_amount * np.clip(duck_env[i] * 4.0, 0.0, 1.0)
                wet *= duck

            out[i] = inp * (1.0 - self.wet_dry) + wet * self.wet_dry

        self._indices = list(idx)
        self._lp_state = lp
        return out

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply FDN reverb (mono or stereo input)."""
        is_stereo = audio.ndim > 1 and audio.shape[1] >= 2
        if is_stereo:
            left = self._process_mono(audio[:, 0].astype(np.float64))
            # Independent right pass with slight delay offset for width
            base = self.wet_dry
            saved = self.wet_dry
            self.wet_dry = base
            right = self._process_mono(audio[:, 1].astype(np.float64))
            self.wet_dry = saved
            # Width via mid/side on the wet portion
            mid = (left + right) * 0.5
            side = (left - right) * 0.5
            out_l = mid + side * self.width
            out_r = mid - side * self.width
            return np.column_stack([out_l, out_r]).astype(audio.dtype)
        return self._process_mono(audio.astype(np.float64)).astype(audio.dtype)
