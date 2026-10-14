# Spectral Dynamics Compression/Expansion (SDCX) — SP-114

## Overview

**ID**: SP-114
**Layer**: absolute — Post-Processing / DSP
**Name**: Spectral Dynamics Compression/Expansion (SDCX)
**Code path**: `sound/effects/spectral_dynamics.py`
**Complexity**: $\mathcal{O}(W \log W + B)$ per hop (dominated by two FFTs, $B \ll W$)
**Aliases**: Spectral compression, FFT-domain dynamics, per-band compression, spectral dynamics processing

**One-line description**: STFT-domain dynamics processor that applies independent compression, expansion, limiting, and gating to each of $N$ perceptually-scaled frequency bands (ERB grouping), with per-band threshold, ratio, attack, release, and knee parameters.

---

## Source

[1] Zölzer, U. (2011). *DAFX: Digital Audio Effects* (2nd ed.). John Wiley & Sons. — Chapter 8: Spectral Processing.
[2] Smith, J. O. (2011). *Spectral Audio Signal Processing*. CCRMA, Stanford University. https://ccrma.stanford.edu/~jos/sasp/
[3] Moore, B. C. J. & Glasberg, B. R. (1983). "Suggested formulae for calculating auditory-filter bandwidths and excitation patterns." *J. Acoust. Soc. Am.* 74(3), 750–753. — ERB scale for perceptual band grouping.
[4] Dahl, M. (2010). "Spectral Dynamics Processing — A New Approach to Dynamics in the Frequency Domain." *Proc. 128th AES Convention*, London.
[5] Moffat, D., Sandler, M. & Smith, J. O. (2012). "Spectral Dynamics: An Exploration of Frequency-Domain Dynamic Range Compression." *Proc. 15th Int. Conf. on Digital Audio Effects (DAFx-12)*.
[6] Jia, S. et al. (2023). "High-Fidelity Noise Reduction with Differentiable Signal Processing." arXiv:2310.11364.
[7] Průša, Z. & Holighaus, N. (2015). "Phase vocoder with spectral smoothing." *Proc. 18th Int. Conf. on Digital Audio Effects (DAFx-15)*.
[8] KERN Audio. "Spectral compression explained." https://kernaudio.io/guides/compression/spectral-compression-explained

## Layer

**absolute** — Post-Processing / DSP
Code path: `sound/effects/spectral_dynamics.py`

## Description

Spectral Dynamics Compression/Expansion (SDCX) is an STFT-domain dynamics processing framework that applies independent dynamic-range control (compression, expansion, limiting, gating) to each of $N$ perceptually scaled frequency bands — ranging from a few dozen ERB-scale bands up to the full FFT bin resolution. Unlike broadband compression (one gain for the entire spectrum) or multiband compression (3-6 bands via crossover filters with phase artifacts at seam points), SDCX operates directly on the STFT magnitude spectrum: the analysis frames are transformed to the frequency domain, grouped into bands, each band's envelope is detected, a per-band time-varying gain is computed from independent threshold/ratio/attack/release/knee parameters, and the gain-modified magnitude spectrum is recombined with the original phase and resynthesized via ISTFT overlap-add.

SDCX is a **post-processing DSP** method: it always acts on a previously rendered audio buffer. It consumes a stereo or mono audio buffer and outputs a buffer of the same dimensions. When used per-voice in a UnitMatrix context, each voice can carry its own spectral dynamics profile (band-specific thresholds, compression style), enabling frequency-selective voice arrangement.

**Distinction from related methods:**
- **SP-008 (Dynamic Range Compression)**: broadband single-stage DRC — one threshold, one ratio, one attack/release for the entire spectrum. SDCX has $N$ independent DRC stages.
- **SP-103 (Crossover Band Distortion)**: splits into N bands via Linkwitz-Riley filters, applies *distortion* per band, recombines via L-R filters. SDCX splits via STFT, applies *dynamics* per band, recombines via ISTFT with no crossover-phase artifacts.
- **SP-109 (Spectral Gating / Noise Reduction)**: applies binary/sigmoid noise-suppression gain *relative to a noise floor estimate*. SDCX applies compression/expansion gain *relative to each band's own threshold* — a classic dynamics curve, not a noise floor.
- **SP-072 (HPSS)**: splits into harmonic/percussive stems via time/frequency median filtering. SDCX shapes dynamics across frequency, not separates.
- **SP-026 (Phase Vocoder)**: modifies time/pitch via STFT. SDCX modifies dynamics only, preserves time/pitch.
- **SP-031 (Spectral Cross-Synthesis)**: transfers spectral envelope between signals via STFT. SDCX uses the signal's *own* envelope to drive compression.

SDCX sits alongside SP-026, SP-031, SP-050 (Spectral Delay) as an STFT-domain processing method, but where those modify the spectrum for timbre/pitch/time transformations, SDCX modifies it for *dynamics control* — the STFT-domain analog of a compressor/expander/gate.

## Technical Mechanics

### Signal Flow (mono)

```
x[n] → [STFT: window, FFT] → |X[k,l]| → [Group Bins into Bands b=1..B] → [Level Envelope Detector] → [Gain Computer: T,R,Knee,Attack,Release] → G[b,l]
                                                                                                                              ↓
↑ ← [ISTFT: IFFT, OLA window, OLA] ← x_out[n] ← [Recombine: G[b,l]·|X[k,l]|·exp(j∠X[k,l])] ← [Apply Gain Mask] ← ———— ———— ———— ┘
```

**Step 1 — STFT Analysis.** Input $x[n]$ (length $L$ at $f_s$) is segmented into frames of length $W$ (typically 2048–8192) with 75% overlap (hop size $H = W/4$), windowed by a Hann window:

$$X[k,l] = \sum_{n=0}^{W-1} x[lH + n] \, w[n] \, e^{-2\pi j kn / W}$$

where $k = 0..W-1$, $l = 0..\lfloor L/H\rfloor$. Magnitude $|X[k,l]|$ and phase $\angle X[k,l]$ are preserved for resynthesis.

**Step 2 — Band Grouping.** FFT bins are grouped into $B$ bands per the ERB scale:

$$M[b,l] = \sqrt{\frac{1}{|\text{band}[b]|}\sum_{k \in \text{band}[b]} |X[k,l]|^2} \quad \text{(RMS per band)}$$

Two modes: full-bin ($B = W/2+1$, one compressor per bin) or perceptual ($B \approx 20–40$ ERB bands). ERB bandwidth: $\text{ERB}(f) = 24.7 \times (4.37f/1000 + 1)$.

**Step 3 — Per-Band Envelope Detection.**

$$E[b,l] = \begin{cases}
\alpha_{\text{attack}}[b]\, M[b,l] + (1-\alpha_{\text{attack}}[b])\, E[b,l-1], & M[b,l] > E[b,l-1] \\
\alpha_{\text{release}}[b]\, M[b,l] + (1-\alpha_{\text{release}}[b])\, E[b,l-1], & \text{else}
\end{cases}$$

where $\alpha = 1 - \exp(-H / (\tau \cdot f_s))$ for hop $H$.

**Step 4 — Gain Computer.** Classic static DRC curve per band:

$$G_{\text{dB}}[b,l] = \begin{cases}
0, & E_{\text{dB}} \le T - W_{\text{knee}}/2 \\
\frac{E_{\text{dB}} - T + W_{\text{knee}}/2}{W_{\text{knee}}} \cdot \frac{W_{\text{knee}}}{2}\left(\frac{1}{R} - 1\right), & T - W_{\text{knee}}/2 < E_{\text{dB}} < T + W_{\text{knee}}/2 \\
(E_{\text{dB}} - T)\left(\frac{1}{R} - 1\right), & E_{\text{dB}} \ge T + W_{\text{knee}}/2
\end{cases}$$

Modes: Downward ($R>1$), Upward ($R<1$), Gate ($R>1$ below $T$), Limiter ($R\to\infty$).

**Step 5 — Temporal Gain Smoothing.** One-pole across frames:

$$G_{\text{smooth}}[b,l] = \alpha_{\text{smooth}}[b]\, G_{\text{smooth}}[b,l-1] + (1-\alpha_{\text{smooth}}[b])\, G_{\text{dB}}[b,l]$$

**Step 6 — Gain-to-Bin Interpolation & Magnitude Masking.** Interpolate $B$ gains back to $W/2+1$ bins; apply with phase preserved:

$$Y[k,l] = 10^{G_{\text{bin}}[k,l] / 20} \cdot X[k,l]$$

**Step 7 — ISTFT Resynthesis.** Inverse FFT per frame, overlap-add with COLA:

$$x_{\text{out}}[n] = \sum_l \left( \frac{1}{W} \sum_{k=0}^{W-1} Y[k,l] \, e^{2\pi j kn / W} \right) w_{\text{synth}}[n - lH]$$

### Complexity

$\mathcal{O}(W \log W + B)$ per hop, dominated by 2× FFT. At $W=4096$, $B=40$, $f_s=44100$ → ~5 ms latency with 75% overlap, real-time on a single core.

## Python/NumPy Implementation Sketch

```python
import numpy as np
from scipy.signal import stft, istft, get_window

class SpectralDynamics:
    """STFT-domain per-band compressor/expander."""

    def __init__(self, fs=44100, n_fft=4096, hop_length=None,
                 n_bands=40, threshold_db=None, ratio=None,
                 attack_ms=5.0, release_ms=50.0, knee_db=6.0,
                 mode='downward'):
        self.fs = fs
        self.n_fft = n_fft
        self.hop = hop_length or n_fft // 4
        self.window = get_window('hann', n_fft)
        # ERB band edges
        self.band_edges = self._erb_bands(n_fft, fs, n_bands)
        # Band grouping matrix (n_bands × n_bins)
        self.bin_to_band = self._build_grouping(n_fft, n_bands)
        # Parameters (broadcast to bands)
        self.threshold = np.full(n_bands, threshold_db or -20.0)
        self.ratio = np.full(n_bands, ratio or 2.0)
        self.knee = np.full(n_bands, knee_db or 6.0)
        # Time constants
        self.alpha_attack = 1 - np.exp(-self.hop / (attack_ms * 1e-3 * fs))
        self.alpha_release = 1 - np.exp(-self.hop / (release_ms * 1e-3 * fs))
        self.alpha_smooth = 0.3  # 1-10 ms smoothing
        self.mode = mode
        # State
        self._envelope = np.zeros(n_bands)
        self._smooth_gain = np.zeros(n_bands)

    def process(self, x):
        """Process mono audio array x, return processed array."""
        # STFT analysis
        f, t, Zxx = stft(x, fs=self.fs, window=self.window,
                         nperseg=self.n_fft, noverlap=self.n_fft - self.hop)
        mag = np.abs(Zxx)
        phase = np.angle(Zxx)
        n_frames = mag.shape[1]

        out_mag = np.zeros_like(mag)
        for l in range(n_frames):
            # Per-band RMS
            band_mag = np.sqrt(self.bin_to_band @ (mag[:, l]**2))
            # Envelope detection
            mask = band_mag > self._envelope
            alpha = np.where(mask, self.alpha_attack, self.alpha_release)
            self._envelope = alpha * band_mag + (1 - alpha) * self._envelope
            # Gain compute (dB domain)
            env_db = 20 * np.log10(np.maximum(self._envelope, 1e-6))
            T, R, W = self.threshold, self.ratio, self.knee
            diff = env_db - T
            gain_db = np.zeros_like(env_db)
            # Below knee
            below = diff <= -W/2
            # In knee
            knee_zone = np.abs(diff) < W/2
            gain_db[knee_zone] = ((diff[knee_zone] + W[knee_zone]/2) / W[knee_zone]
                                  * (W[knee_zone]/2) * (1/R[knee_zone] - 1))
            # Above knee
            above = diff >= W/2
            gain_db[above] = diff[above] * (1/R[above] - 1)
            # Smooth
            self._smooth_gain = (self.alpha_smooth * self._smooth_gain
                                 + (1 - self.alpha_smooth) * gain_db)
            # Gain mask -> bins
            gain_linear = 10**(self._smooth_gain / 20)
            bin_gain = self.bin_to_band.T @ gain_linear
            out_mag[:, l] = mag[:, l] * bin_gain

        # ISTFT
        _, x_out = istft(out_mag * np.exp(1j * phase), fs=self.fs,
                         window=self.window, nperseg=self.n_fft,
                         noverlap=self.n_fft - self.hop)
        return x_out

    def _erb_bands(self, n_fft, fs, n_bands):
        """Compute ERB band edges for given FFT size."""
        # ERB(f) = 24.7 * (4.37*f/1000 + 1)
        # Map n_bands equally along ERB scale from 20 Hz to Nyquist
        nyquist = fs / 2
        erb_low = 24.7 * (4.37 * 20 / 1000 + 1) * np.log(1 + 20/(24.7*4.37/1000))
        erb_high = 24.7 * (4.37 * nyquist / 1000 + 1) * np.log(1 + nyquist/(24.7*4.37/1000))
        erb_centers = np.linspace(erb_low, erb_high, n_bands + 1)
        # Convert back to Hz
        freq_edges = 24.7 * (4.37 / 1000) * (np.exp(erb_centers / (24.7 * (4.37/1000) + 1)) - 1)
        freq_edges[0] = 20
        freq_edges[-1] = nyquist
        return freq_edges

    def _build_grouping(self, n_fft, n_bands):
        """Build (n_bands x n_bins) grouping matrix."""
        bin_freqs = np.fft.rfftfreq(n_fft, 1/self.fs)
        edges = self._erb_bands(n_fft, self.fs, n_bands)
        n_bins = len(bin_freqs)
        mat = np.zeros((n_bands, n_bins))
        for b in range(n_bands):
            mask = (bin_freqs >= edges[b]) & (bin_freqs < edges[b+1])
            mat[b, mask] = 1.0 / np.sqrt(np.sum(mask))  # RMS normalization
        return mat
```

## Musical Elements Framework

**PITCH** — SDCX does not generate pitch, but shapes the dynamics of existing pitch bands. Each ERB/perceptual band tracks a specific frequency region, so per-band compression sculpts the spectral balance of individual pitch ranges.

**RHYTHM** — Attack and release times per band create frequency-dependent rhythmic response. Short attack on transient bands tightens percussive attacks; long release on low bands sustains kick/sub-bass tail.

**HARMONY** — Per-band thresholds mapped to chord-tone frequency regions. Low threshold on root bands attenuates them relative to overtones; the per-band threshold vector can follow chord changes as a spectral dynamics harmony follower.

**STRUCTURE** — The full spectral dynamics profile (thresholds, ratios, attack/release arrays) varies per section as a parameter vector. This spectral "snapshot" per section defines the section's overall dynamic character.

**TEXTURE** — Upward spectral compression brings out room noise and air; downward tames harshness; short-release low-band compression creates pulsing sub-bass (spectral pump); gate-mode creates frequency-stuttering. Texture is the sum of per-band DRC envelopes.

## UnitMatrix Integration (Voices & Sections)

**Voices** = rows, each with `SDCXParams[v]`:

```python
SDCXParams = {
    'b_groups': 40,
    'threshold': np.linspace(-10, -30, 40),      # dB per band
    'ratio': np.linspace(2.5, 1.2, 40),
    'knee': 6.0,
    'attack_ms': np.linspace(3, 0.5, 40),
    'release_ms': np.linspace(80, 20, 40),
    'mode': 'downward',
}
```

- Voice 1 (Lead): moderate all-band compression, tight attack in 2–8 kHz band.
- Voice 2 (Harmony): gentle compression, open highs.
- Voice 3 (Bass): heavy compression on sub-200 Hz band.
- Voice 4 (Drums): hard attack on high-mid bands, fast release on lows.

**Sections** = columns, each with `section_params[s]`. Voice and section params blend:
```python
params = SDCXParams[v] * (1 - α) + section_params[s] * α
```

**Cell filling** for cell $(v, s)$:
1. Voice's audio buffer for section $s$ already rendered by a synthesis SP method.
2. Load voice and section `SDCXParams`, blend.
3. Run full STFT → band grouping → envelope → gain → mask → ISTFT pipeline.
4. Return processed buffer.

SDCX can be applied as the last production stage before mixdown/spatialization, or as a per-voice insert.

## Pitfalls

1. **Metallic ("Musical") Noise.** Full-bin mode with aggressive gain creates correlated spectral scalloping — metallic artifact. **Fix**: use ERB band grouping ($B \geq 20$).

2. **Pre-echo / Windowing Ring.** Rapid per-band gain change causes windowing ringing. **Fix**: inter-frame gain smoothing of at least 2–5 ms.

3. **Time-Smearing of Transients.** The ~93 ms STFT window smears rapid transients. **Fix**: shorter window (2048) or reduce SDCX depth on transient bands.

4. **Per-Band Attack Mismatch Artifacts.** Adjacent bands with very different attack/release times create spectral "holes." **Fix**: spatial smoothing of attack/release arrays across bands (Gaussian blur of 3–5 bands).

5. **Expansion Noise Floor Breathing.** Upward expansion boosts noise, creating breathing. **Fix**: noise-floor floor per band.

6. **CPU Cost.** 2× FFT per frame per voice. **Fix**: batch offline for multi-voice renders; limit to master bus for online.

7. **Pipeline Confusion.** SDCX modifies dynamics only — distinct from SP-026 (time/pitch), SP-031 (timbre morph), SP-050 (spectral delay).

8. **Gain Bandwidth Interaction.** Discontinuous band-edge thresholds sound like narrow filters. **Fix**: cross-band smoothing of threshold/ratio arrays.

---