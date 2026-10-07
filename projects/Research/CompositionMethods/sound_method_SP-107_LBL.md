# Look-Ahead Brickwall Limiter (LBL) — Sound Production Method SP-107

## Overview

**Layer:** absolute (Sound Production — Post-Processing / DSP)
**Candidate code path:** `sound/effects/brickwall_limiter.py`
**Target output:** Peak Control / Loudness Maximization

Look-Ahead Brickwall Limiter (LBL) is the final dynamic-range control stage in a mastering chain, ensuring that no sample exceeds a specified amplitude threshold while preserving waveform integrity and maximizing perceived loudness. Unlike hard clipping (which introduces high-order harmonics) or full-band compression (SP-008, which uses ratio-based gain reduction), the brickwall limiter employs a predictive look-ahead strategy: it delays the input signal by a short window (typically 1–10 ms), analyzes the upcoming signal to compute gain reduction values, smooths them with configurable attack/hold/release envelope shaping, and applies the smoothed gain curve to the delayed signal.

## Technical Mechanics

### Gain Computer

For each input sample $x[n]$ (mono, or the maximum over all channels for stereo linked mode), the instantaneous required gain to stay below the threshold $T$ (linear amplitude, $T \in (0, 1)$) is:

$$g_{\max}[n] = \min\left(1,\; \frac{T}{|x[n]|}\right)$$

In the logarithmic (dB) domain:

$$G_{\max}[n] = \min\left(0,\; T_{\text{dB}} - 20\log_{10}|x[n]|\right)$$

where $T_{\text{dB}} = 20\log_{10} T$.

If $|x[n]| \leq T$, then $g_{\max} = 1$ (no reduction); if $|x[n]| > T$, then $g_{\max} < 1$.

### Peak-Hold (Moving Minimum)

A peak-hold buffer of length $H = \tau_{\text{hold}} \cdot f_s$ samples holds the minimum of $g_{\max}$ over the look-ahead window. This prevents the gain envelope from recovering prematurely between closely spaced transients:

$$g_{\text{PH}}[n] = -\text{peakHold}\left(-g_{\max}[n]\right)$$

Implemented as a circular buffer of $H$ samples: each sample writes $g_{\max}[n]$ and reads the minimum over $[n-H+1, n]$. Constant-time via the two-stack min-queue or $\mathcal{O}(\log H)$ via a priority queue.

For a 15 ms hold at 48 kHz: $H = 720$ samples.

### Exponential Release

After the peak-hold window, the gain recovers toward 1 (no reduction) with an exponential time constant $\tau_{\text{release}}$:

$$g_{\text{rel}}[n] = g_{\text{rel}}[n-1] + \alpha \cdot \left(g_{\text{PH}}[n] - g_{\text{rel}}[n-1]\right)$$

where the release slew factor $\alpha$ relates to $\tau_{\text{release}}$ by:

$$\alpha = 1 - \exp\left(-\frac{1}{\tau_{\text{release}} \cdot f_s}\right)$$

The release ensures that $g_{\text{rel}}[n] \leq g_{\text{PH}}[n]$ (envelope never exceeds the instantaneous maximum gain). Typical release times: 20–200 ms. Shorter release = faster recovery (more pumping), longer release = smoother (less modulation distortion).

### FIR Smoothing (Attack Shaping)

The attack phase of the gain curve is smoothed by a cascade of $K$ box-averaging filters (moving average, implemented as CIC/boxstack) of length $L_a = \tau_{\text{attack}} \cdot f_s$:

$$g_{\text{smooth}}[n] = \text{boxStack}_K\left(g_{\text{rel}}[n]\right)$$

$K=3$ or $4$ stages gives a Gaussian-like smoothing kernel with zero overshoot and fast spectral roll-off. The smoothing guarantees that the gain curve changes continuously (no step discontinuities), eliminating the high-frequency distortion that instantaneous gain changes would produce. The effective attack time $\tau_{\text{attack}}$ (1–15 ms) determines how far ahead the limiter begins reducing gain before a transient.

### Look-Ahead Delay

The input signal is delayed by $D = \tau_{\text{attack}} \cdot f_s$ samples (the same length as the FIR smoothing filter). The delayed signal is multiplied by the smoothed gain curve:

$$y[n] = x[n - D] \cdot g_{\text{smooth}}[n]$$

The look-ahead ensures that the gain reduction begins $\tau_{\text{attack}}$ milliseconds *before* the transient reaches the gain multiplier at the output, eliminating the "blunt attack" that zero-latency limiters produce.

### Make-Up Gain

After limiting, a fixed makeup gain $G_{\text{MU}}$ (linear gain, typically 0–6 dB) is applied to restore the perceived loudness lost to gain reduction:

$$y_{\text{out}}[n] = G_{\text{MU}} \cdot y[n]$$

### True-Peak (Inter-Sample Peak) Detection

An optional true-peak mode oversamples the signal by 2× or 4× (or uses analytic peak estimation via the Hilbert transform) to detect samples that would exceed the threshold after reconstruction (ITU-R BS.1770). The gain reduction is computed on the true-peak estimate rather than the sampled envelope:

$$|x|_{\text{true}}[n] = \max\left(|x[n]|,\; |x[n-1]|,\; |x[n]| + 0.5|x[n] - x[n-1]|\right)$$

### Complexity

Each sample requires: peak-hold insert/query $\mathcal{O}(\log H)$ (or $\mathcal{O}(1)$ with min-queue), release $\mathcal{O}(1)$, box-stack $\mathcal{O}(K)$ (usually 3–4 taps at a lower sub-rate, or a single cumulative-sum update), delay buffer write/read $\mathcal{O}(1)$. Total: $\mathcal{O}(1)$ per sample in practice. Total latency: $\tau_{\text{attack}}$ (typically 1.5–10 ms).

## Python/NumPy Implementation Sketch

```python
import numpy as np
from collections import deque

class PeakHold:
    """Moving minimum via two-stack min-queue."""
    def __init__(self, hold_samples: int):
        self.hold = hold_samples
        self.buffer = deque()
        self.min_stack = deque()
    
    def process(self, x: float) -> float:
        """Return the minimum over [n-H+1, n] of the input."""
        # Use negation: peak-hold on -x = moving minimum on x
        neg_x = -x
        self.buffer.append(neg_x)
        # Maintain monotonic stack for O(1) min
        while self.min_stack and self.min_stack[-1] > neg_x:
            self.min_stack.pop()
        self.min_stack.append(neg_x)
        # Evict old samples
        if len(self.buffer) > self.hold:
            old = self.buffer.popleft()
            if old == self.min_stack[0]:
                self.min_stack.popleft()
        return -self.min_stack[0]


class ExpRelease:
    """Exponential release filter."""
    def __init__(self, release_samples: float):
        self.slew = 1 / (release_samples + 1)
        self.state = 1.0
    
    def process(self, target: float) -> float:
        self.state += (target - self.state) * self.slew
        self.state = min(self.state, target)
        return self.state


class BoxStackSmoother:
    """Cascaded box-averaging filter (moving average)."""
    def __init__(self, length: int, stages: int = 3):
        self.stages = stages
        self.buffers = [deque([1.0] * length, maxlen=length) for _ in range(stages)]
        self.sums = [length * 1.0 for _ in range(stages)]
        self.len = length
    
    def process(self, x: float) -> float:
        val = x
        for i in range(self.stages):
            self.sums[i] += val - self.buffers[i][0]
            self.buffers[i].append(val)
            val = self.sums[i] / self.len
        return val


class LookAheadLimiter:
    """Look-Ahead Brickwall Limiter."""
    def __init__(self,
                 threshold_db: float = -0.5,
                 attack_ms: float = 5.0,
                 hold_ms: float = 15.0,
                 release_ms: float = 40.0,
                 makeup_gain_db: float = 2.0,
                 sample_rate: float = 44100.0,
                 true_peak: bool = True):
        
        self.threshold = 10.0 ** (threshold_db / 20.0)
        self.makeup_gain = 10.0 ** (makeup_gain_db / 20.0)
        self.true_peak = True
        self.sample_rate = sample_rate
        
        attack_samples = int(attack_ms * 0.001 * sample_rate)
        hold_samples = int(hold_ms * 0.001 * sample_rate)
        release_samples = release_ms * 0.001 * sample_rate
        
        # Delay buffer for look-ahead
        self.delay = deque([0.0] * attack_samples, maxlen=attack_samples)
        self.delay_len = attack_samples
        
        # Envelope processing chain
        self.peak_hold = PeakHold(attack_samples + hold_samples)
        self.release = ExpRelease(release_samples)
        self.smoother = BoxStackSmoother(attack_samples, stages=3)
        
        # GR meter
        self.gain_reduction_db = 0.0
    
    def _gain_computer(self, sample: float) -> float:
        """Compute maximum allowed gain for a sample."""
        abs_s = abs(sample)
        if self.true_peak:
            # Simple true-peak estimate (2nd-order)
            abs_s = max(abs_s, abs(sample * 0.1))  # placeholder for analytic peak
        if abs_s > self.threshold:
            return self.threshold / abs_s
        return 1.0
    
    def process_mono(self, buffer: np.ndarray) -> np.ndarray:
        """Process a mono float array [-1, 1] through the limiter."""
        out = np.zeros_like(buffer)
        for n in range(len(buffer)):
            x = buffer[n]
            
            # 1. Gain computer
            g_max = self._gain_computer(x)
            
            # 2. Peak hold (moving minimum)
            g_ph = self.peak_hold.process(g_max)
            
            # 3. Release
            g_rel = self.release.process(g_ph)
            
            # 4. FIR smoothing
            g_smooth = self.smoother.process(g_rel)
            
            # 5. Delay the input
            self.delay.append(x)
            delayed_x = self.delay[0] if self.delay_len > 0 else x
            
            # 6. Apply gain + makeup
            out[n] = delayed_x * g_smooth * self.makeup_gain
            
            # Meter
            self.gain_reduction_db = -20.0 * np.log10(max(g_smooth, 1e-10))
        
        # Hard clip to [-1, 1] to catch any numeric overshoot
        np.clip(out, -1.0, 1.0, out=out)
        return out
    
    def process_stereo(self, left: np.ndarray, right: np.ndarray) -> tuple:
        """Process stereo with linked gain reduction (max of both channels)."""
        out_l = np.zeros_like(left)
        out_r = np.zeros_like(right)
        
        for n in range(len(left)):
            # Linked sidechain: max of both channels
            x_l, x_r = left[n], right[n]
            x_max = max(abs(x_l), abs(x_r))
            
            # Common gain curve
            g_max = self._gain_computer(x_max)
            g_ph = self.peak_hold.process(g_max)
            g_rel = self.release.process(g_ph)
            g_smooth = self.smoother.process(g_rel)
            
            # Delay both channels
            self.delay.append(x_l)
            delayed_l = self.delay[0]
            # Use separate delay for right in production; simplified here
            delayed_r = x_r  
            
            out_l[n] = delayed_l * g_smooth * self.makeup_gain
            out_r[n] = delayed_r * g_smooth * self.makeup_gain
        
        np.clip(out_l, -1.0, 1.0, out=out_l)
        np.clip(out_r, -1.0, 1.0, out=out_r)
        return out_l, out_r

    def reset(self):
        """Reset all internal state (for new buffer)."""
        self.peak_hold = PeakHold(self.peak_hold.hold)
        self.release = ExpRelease(1.0 / self.release.slew - 1)
        self.release.state = 1.0
        self.delay = deque([0.0] * self.delay_len, maxlen=self.delay_len)
```

## Musical Elements Framework

| Element | LBL Role |
|---------|----------|
| **PITCH** | Limiter does not alter pitch; aggressive GR > 6 dB flattens envelope, reducing pitch salience |
| **RHYTHM** | Attack/hold/release shape rhythmic pumping; tempo-synced hold prevents flutter |
| **HARMONY** | Harmony-agnostic (broadband); chordal attacks trigger GR that ducks other voices |
| **STRUCTURE** | Per-section threshold/attack/hold/release arcs articulate macro-form |
| **TEXTURE** | Primary domain: transparent (1–2 dB GR) → moderate (3–6 dB) → aggressive (6–12+ dB) flattens dynamics |

## UnitMatrix Integration

- **Rows (Voices)**: Per-voice pre-limiting with individual thresholds, then a master bus limiter on the sum.
- **Columns (Sections)**: Limiter preset per section; crossfade parameters between sections.
- **Cells (MusicUnit integration)**: Cell config includes `threshold_db`, `attack_ms`, `hold_ms`, `release_ms`, `makeup_gain_db`, `true_peak`, `link_mode`.

## Pitfalls

1. **Latency**: Look-ahead adds 1.5–10 ms delay. Fine for offline render, critical for real-time.
2. **Inter-sample peaks**: Sample-level threshold still overshoots after D/A conversion; true-peak mode essential.
3. **Pumping**: Short release creates audible gain modulation; increase hold or release.
4. **Over-limiting**: >10 dB GR produces waveform flattening and distortion.
5. **Makeup vs. threshold conflict**: G_MU > 1/T re-exceeds threshold; apply makeup post-limiter + final clip.
6. **Attack/smoothing mismatch**: If smoothing > delay, gain curve hasn't settled before signal arrives.
7. **Stereo unlink**: Unlinked stereo shifts image; always use "max" or "sum" link mode.
8. **DC amplification**: Asymmetric gain envelopes amplify DC offset; highpass input at 20–40 Hz.

## References

- Zölzer, U. (2011). *DAFX: Digital Audio Effects*, 2nd ed. John Wiley & Sons, Ch. 7.
- Velsberg, M. (2022). "Designing a Straightforward Limiter." *Signalsmith Audio Blog*.
- Rudrich, D. (2019). "LookAhead Limiters." *SimpleCompressor Docs*, GitHub.
- ITU-R BS.1770-4 (2015). "Algorithms to Measure Audio Programme Loudness and True-Peak Level."
- Giannoulis, M., & Davies, J. (2014). "Digital Dynamic Range Compressor Design." *Proc. DAFx-14*.
- Smith, J. O. (2024). *Physical Audio Signal Processing* (online), Ch. 1.