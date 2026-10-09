# Spectral Gating Adaptive Noise Reduction (SG-ANR)
## Sound Production Method SP-109

**Layer:** absolute
**Category:** Post-Processing / DSP
**Candidate Code Path:** `sound/effects/spectral_gate.py`
**Implementation Requirements:** NumPy, SciPy (STFT/ISTFT), Python 3.10+

---

## Extended Technical Description

Spectral Gating Adaptive Noise Reduction (SG-ANR) is a frequency-domain audio denoising technique that applies a time-varying, frequency-dependent gain mask to the Short-Time Fourier Transform (STFT) of a rendered audio buffer. The gain mask attenuates frequency bins where the estimated noise energy dominates, while preserving bins where the desired signal energy exceeds the noise floor.

The method operates in two modes:

1. **Stationary mode** — A single noise profile is estimated from a manually selected or automatically detected noise-only segment of the audio. The same noise threshold is applied across the entire signal.
2. **Non-stationary mode** — The noise floor is tracked continuously using per-bin exponential moving average (EMA), adapting to slowly varying noise conditions (e.g., changing room ambience, crowd noise, wind).

---

## Algorithm Walkthrough

### Step 1: STFT Analysis

The input signal $y[n]$ is framed into overlapping windows with a Hann window $w[n]$:

$$Y_m[k] = \sum_{n=0}^{N-1} y[mH + n] \, w[n] \, e^{-j2\pi kn/N}$$

Parameters:
- $N$ = FFT size (typically 1024–4096, must be power of 2)
- $H$ = hop size (typically $N/4$ for 75% overlap)
- $M$ = number of frames

### Step 2: Noise Profile Estimation

**Stationary mode:**
Given a noise-only segment of $M_{\text{noise}}$ frames (manually selected or VAD-detected):

$$|\hat{D}[k]| = \frac{1}{M_{\text{noise}}} \sum_{m=0}^{M_{\text{noise}}-1} |Y_m^{\text{(noise)}}[k]|$$

With per-bin standard deviation:

$$\sigma_D[k] = \sqrt{\frac{1}{M_{\text{noise}}} \sum_{m} \left(|Y_m^{\text{(noise)}}[k]| - |\hat{D}[k]|\right)^2}$$

**Non-stationary mode:**
Per-bin EMA noise floor tracker:

$$|\hat{D}_m[k]| = \alpha \, |\hat{D}_{m-1}[k]| + (1 - \alpha) \, |Y_m[k]|$$

where the forgetting factor $\alpha = \exp(-H / (\tau \cdot f_s))$ with time constant $\tau$ (typically 1–5 seconds for slowly varying noise).

### Step 3: Gain Mask Computation

**Sigmoid gate (preferred for smoothness):**

$$G_m[k] = \sigma\!\left(s \cdot \left( \frac{|Y_m[k]|}{|\hat{D}[k]|} - t \right) \right)$$

where $\sigma(z) = 1/(1+e^{-z})$, $s$ is the sigmoid slope (typically 10–50), and $t$ is the threshold ratio (typically 1.5–3.0).

**Power spectral subtraction gain (Boll 1979):**

$$G_m[k] = \sqrt{\max\left( \frac{|Y_m[k]|^2 - \beta |\hat{D}[k]|^2}{|Y_m[k]|^2},\; \gamma^2 \right)}$$

where $\beta$ is the over-subtraction factor ($\beta \ge 1$) and $\gamma$ is the spectral floor ($\gamma \approx 0.01$–$0.05$).

### Step 4: Smoothing

**Frequency-domain smoothing** (moving average across bins, width $W_f$ Hz):

$$\bar{G}_m[k] = \frac{1}{2B+1} \sum_{b=-B}^{B} G_m[k+b], \quad B = \left\lfloor \frac{W_f \cdot N}{2 \cdot f_s} \right\rfloor$$

**Time-domain smoothing** (one-pole IIR across frames):

$$\tilde{G}_m[k] = \eta \, \tilde{G}_{m-1}[k] + (1 - \eta) \, \bar{G}_m[k]$$

where $\eta$ corresponds to a smoothing time constant $\tau_{\text{smooth}}$ ms.

### Step 5: Apply Mask and Reconstruct

Apply the smoothed gain mask to the magnitude STFT, preserving original phase:

$$|\hat{X}_m[k]| = \tilde{G}_m[k] \cdot |Y_m[k]|$$
$$\hat{X}_m[k] = |\hat{X}_m[k]| \cdot e^{j\angle Y_m[k]}$$

Reconstruct via inverse STFT with overlap-add:

$$\hat{x}[n] = \sum_m \text{IFFT}\{\hat{X}_m[k]\} \cdot w_{\text{synth}}[n - mH]$$

---

## Python/NumPy Implementation Sketch

```python
import numpy as np
from scipy import signal

class SpectralGate:
    """Spectral Gating Adaptive Noise Reduction."""
    
    def __init__(self, n_fft=2048, hop_length=None, win_length=None,
                 mode='stationary', threshold_ratio=2.0, sigmoid_slope=20.0,
                 time_constant_s=2.0, freq_smooth_hz=500, time_smooth_ms=50,
                 floor_gamma=0.02, over_subtract_beta=1.5):
        self.n_fft = n_fft
        self.hop_length = hop_length or n_fft // 4
        self.win_length = win_length or n_fft
        self.mode = mode
        self.threshold_ratio = threshold_ratio
        self.sigmoid_slope = sigmoid_slope
        self.time_constant_s = time_constant_s
        self.freq_smooth_hz = freq_smooth_hz
        self.time_smooth_ms = time_smooth_ms
        self.floor_gamma = floor_gamma
        self.over_subtract_beta = over_subtract_beta
        self.window = signal.windows.hann(self.win_length, sym=False)
    
    def _compute_stft(self, y):
        """Compute STFT magnitude, phase."""
        _, _, stft = signal.stft(
            y, nperseg=self.win_length, noverlap=self.win_length - self.hop_length,
            nfft=self.n_fft, window=self.window, boundary=None, padded=True
        )
        return np.abs(stft), np.angle(stft)
    
    def _compute_istft(self, magnitude, phase):
        """Reconstruct audio from magnitude + phase STFT."""
        complex_stft = magnitude * np.exp(1j * phase)
        _, x_hat = signal.istft(
            complex_stft, nperseg=self.win_length,
            noverlap=self.win_length - self.hop_length,
            nfft=self.n_fft, window=self.window, boundary=False
        )
        return x_hat
    
    def _estimate_noise_stationary(self, noise_audio):
        """Estimate noise profile from noise-only segment."""
        mag_noise, _ = self._compute_stft(noise_audio)
        noise_profile = np.mean(mag_noise, axis=1)
        noise_std = np.std(mag_noise, axis=1)
        return noise_profile, noise_std
    
    def _sigmoid_gate(self, magnitude, noise_profile, sr):
        """Compute gain mask via sigmoid."""
        n_bins = magnitude.shape[0]
        # Per-bin SNR ratio
        ratio = magnitude / (noise_profile[:, np.newaxis] + 1e-10)
        # Sigmoid gate
        gain = 1.0 / (1.0 + np.exp(-self.sigmoid_slope * (ratio - self.threshold_ratio)))
        
        # Frequency-domain smoothing
        bin_width_hz = sr / self.n_fft
        smooth_bins = int(self.freq_smooth_hz / bin_width_hz)
        if smooth_bins > 1:
            from scipy.ndimage import uniform_filter1d
            gain = uniform_filter1d(gain, size=smooth_bins, axis=0, mode='nearest')
        
        # Time-domain smoothing
        smooth_frames = int(self.time_smooth_ms * sr / 1000 / self.hop_length)
        if smooth_frames > 1:
            from scipy.ndimage import uniform_filter1d
            gain = uniform_filter1d(gain, size=smooth_frames, axis=1, mode='nearest')
        
        return gain
    
    def reduce_noise(self, audio, sr, noise_audio=None):
        """Apply spectral gating noise reduction.
        
        Args:
            audio: 1D numpy array, noisy audio signal
            sr: sample rate in Hz
            noise_audio: 1D numpy array, noise-only segment (stationary mode)
        
        Returns:
            cleaned_audio: 1D numpy array
        """
        magnitude, phase = self._compute_stft(audio)
        
        if self.mode == 'stationary':
            if noise_audio is None:
                raise ValueError("stationary mode requires noise_audio")
            noise_profile, _ = self._estimate_noise_stationary(noise_audio)
        else:
            # Non-stationary: EMA noise tracker
            alpha = np.exp(-self.hop_length / (self.time_constant_s * sr))
            noise_profile = np.zeros(magnitude.shape[0])
            noise_tracked = np.zeros_like(magnitude)
            for m in range(magnitude.shape[1]):
                noise_profile = alpha * noise_profile + (1 - alpha) * magnitude[:, m]
                noise_tracked[:, m] = noise_profile
        
        if self.mode == 'stationary':
            gain = self._sigmoid_gate(magnitude, noise_profile, sr)
            cleaned_mag = gain * magnitude
        else:
            gain = self._sigmoid_gate(magnitude, noise_tracked, sr)
            cleaned_mag = gain * magnitude
        
        # Apply spectral floor to prevent complete nulling
        noise_floor = self.floor_gamma * (noise_profile[:, np.newaxis] if self.mode == 'stationary' else noise_tracked)
        cleaned_mag = np.maximum(cleaned_mag, noise_floor)
        
        return self._compute_istft(cleaned_mag, phase)
```

---

## References

- Boll, S. F. (1979). "Suppression of acoustic noise in speech using spectral subtraction." *IEEE Trans. Acoustics, Speech, and Signal Processing* 27(2), 113–120.
- Berouti, M., Schwartz, R., & Makhoul, J. (1979). "Enhancement of speech corrupted by acoustic noise." *Proc. IEEE ICASSP*, 208–211.
- Ephraim, Y. & Malah, D. (1984). "Speech enhancement using a minimum-mean square error short-time spectral amplitude estimator." *IEEE Trans. ASSP* 32(6), 1109–1121.
- Sainburg, T., Thielk, M., & Gentner, T. Q. (2020). "Finding, visualizing, and quantifying latent structure across diverse animal vocal repertoires." *PLoS Computational Biology* 16(10), e1008228. (noisereduce library)
- Audacity Team. "How Audacity Noise Reduction Works." Audacity Manual / Wiki.
- Martin, R. (2001). "Noise power spectral density estimation based on optimal smoothing and minimum statistics." *IEEE Trans. Speech and Audio Processing* 9(5), 504–512.
