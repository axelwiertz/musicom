# Phaser / Allpass Modulation Synthesis (APS) — Sound Production Method SP-106

## Overview

**Layer:** absolute (Sound Production — Post-Processing / DSP)
**Candidate code path:** `sound/effects/phaser.py`
**Target output:** Phase-Swept Modulation / Spectral Notch Filtering

Phaser / Allpass Modulation Synthesis (APS) is a classic modulation effect that cascades N first-order allpass filters with LFO-modulated break frequencies to create moving spectral notches through phase cancellation when mixed with the dry signal. Each allpass stage has unity gain at all frequencies but introduces a frequency-dependent phase shift; when the phase-shifted wet signal sums with the dry, frequencies where the accumulated phase shift equals (2k+1)π cancel destructively. $N/2$ notches are produced for $N$ allpass stages.

## Technical Mechanics

### First-Order IIR Allpass Filter

The fundamental building block is the first-order allpass filter:

$$H_{\mathrm{AP}}(z) = \frac{a + z^{-1}}{1 + a z^{-1}}$$

where $a \in (-1, 1)$ is the allpass coefficient. The difference equation:

$$y[n] = a\,x[n] + x[n-1] - a\,y[n-1]$$

Magnitude response: $|H_{\mathrm{AP}}(e^{j\omega})| = 1$ (unity gain at all frequencies).

The break frequency $f_b$ (where phase shift = $-\pi/2$) relates to coefficient $a$:

$$a = \frac{\tan(\pi f_b / f_s) - 1}{\tan(\pi f_b / f_s) + 1}$$

### Allpass Chain

The phaser uses $N$ first-order allpass filters in cascade. Total phase shift:

$$\Theta_{\mathrm{total}}(\omega) = \sum_{i=1}^{N} \Theta_i(\omega)$$

When summed with dry signal at mix ratio $g$:

$$H_{\mathrm{phaser}}(z) = 1 + g \prod_{i=1}^{N} H_{\mathrm{AP},i}(z)$$

Amplitude response:

$$|H_{\mathrm{phaser}}(e^{j\omega})| = \sqrt{1 + g^2 + 2g\cos[\Theta_{\mathrm{total}}(\omega)]}$$

Notches occur at $\Theta_{\mathrm{total}}(\omega) = (2k+1)\pi$. For $N$ stages → $N/2$ notches.

### LFO Modulation

Each stage's break frequency is modulated by an LFO:

$$f_{b,i}[n] = f_{\min} + \frac{1}{2}\bigl(1 + \sin(\omega_{\mathrm{lfo}} n + \phi_i)\bigr) (f_{\max} - f_{\min})$$

$$a_i[n] = \frac{\tan\bigl(\pi f_{b,i}[n] / f_s\bigr) - 1}{\tan\bigl(\pi f_{b,i}[n] / f_s\bigr) + 1}$$

where $\phi_i = i \pi / N$ spreads the notches evenly.

### Feedback

A portion of the output is fed back: $x'[n] = x[n] + \beta \cdot y_{\mathrm{wet}}[n-1]$, $\beta \in [0, 0.95)$.

### Stereo Phaser

Two parallel instances with opposite LFO phases: $\phi_L = 0$, $\phi_R = \pi$.

## Python/NumPy Implementation Sketch

```python
import numpy as np

class AllpassFilter:
    """First-order IIR allpass filter."""
    def __init__(self):
        self.delay = 0.0  # x[n-1] - a*y[n-1]
    
    def process(self, x, a):
        """Process one sample with coefficient a."""
        y = a * x + self.delay
        self.delay = x - a * y
        return y

class Phaser:
    """N-stage LFO-modulated phaser effect."""
    def __init__(self, num_stages=4, lfo_rate=0.5, depth=0.7,
                 feedback=0.3, f_min=100.0, f_max=4000.0,
                 wet_mix=0.5, sample_rate=44100.0):
        self.num_stages = num_stages
        self.lfo_rate = lfo_rate
        self.depth = depth
        self.feedback = feedback
        self.f_min = f_min
        self.f_max = f_max
        self.wet_mix = wet_mix
        self.sample_rate = sample_rate
        
        self.filters = [AllpassFilter() for _ in range(num_stages)]
        self.lfo_phase = 0.0
        self.fb_sample = 0.0
        
        # Coefficient update block size and interpolation
        self.block_size = 128
        self.block_phase = 0
        self.old_a = [0.0] * num_stages
        self.new_a = [0.0] * num_stages
        self._recalc_coeffs(0.0)  # initial coefficients
    
    def _recalc_coeffs(self, lfo_val):
        """Compute allpass coefficients from LFO value."""
        norm = (lfo_val * self.depth + 1.0) * 0.5  # [0, 1]
        norm = np.clip(norm, 0.0, 1.0)
        fc = self.f_min + norm * (self.f_max - self.f_min)
        for i in range(self.num_stages):
            # Phase offset per stage
            phase_offset = i * np.pi / self.num_stages
            offset_norm = (np.sin(np.arcsin(lfo_val) + phase_offset) * self.depth + 1.0) * 0.5
            offset_fc = self.f_min + np.clip(offset_norm, 0.0, 1.0) * (self.f_max - self.f_min)
            tan_val = np.tan(np.pi * offset_fc / self.sample_rate)
            # Clamp to avoid instability
            tan_val = np.clip(tan_val, 1e-6, 1e6)
            self.new_a[i] = (tan_val - 1.0) / (tan_val + 1.0)
    
    def process(self, x):
        """Process one sample, return output."""
        # LFO phase update
        self.lfo_phase += 2.0 * np.pi * self.lfo_rate / self.sample_rate
        lfo = np.sin(self.lfo_phase)
        
        # Block-wise coefficient update
        if self.block_phase == 0:
            self.old_a = list(self.new_a)
            self._recalc_coeffs(lfo)
        interp = self.block_phase / self.block_size if self.block_size > 0 else 1.0
        
        # Feedback
        chain_in = x + self.fb_sample * self.feedback
        
        # Run allpass chain
        y = chain_in
        for i in range(self.num_stages):
            a = self.old_a[i] + interp * (self.new_a[i] - self.old_a[i])
            y = self.filters[i].process(y, a)
        
        self.fb_sample = y
        
        # Dry/wet mix
        output = (1.0 - self.wet_mix) * x + self.wet_mix * y
        
        self.block_phase = (self.block_phase + 1) % self.block_size
        return output
    
    def process_buffer(self, buffer):
        """Process a full audio buffer."""
        out = np.zeros_like(buffer)
        for n in range(len(buffer)):
            out[n] = self.process(buffer[n])
        # Normalize
        peak = np.max(np.abs(out))
        if peak > 1.0:
            out = out / peak * 0.99
        return out
    
    def reset(self):
        """Reset all filter states."""
        for f in self.filters:
            f.delay = 0.0
        self.lfo_phase = 0.0
        self.fb_sample = 0.0
        self.block_phase = 0

# Example: 4-stage phaser on a 440Hz sine
if __name__ == "__main__":
    sr = 44100
    dur = 4.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sine = np.sin(2 * np.pi * 440 * t)
    
    phaser = Phaser(4, lfo_rate=0.5, depth=0.8, feedback=0.4, wet_mix=0.6, sample_rate=sr)
    processed = phaser.process_buffer(sine)
    
    # Normalize
    processed /= np.max(np.abs(processed)) * 1.01
    
    print(f"Input shape: {sine.shape}")
    print(f"Output shape: {processed.shape}")
    print(f"Output peak: {np.max(np.abs(processed)):.3f}")
```

## References

- Zölzer, U. (2011). *DAFX: Digital Audio Effects*, 2nd ed. John Wiley & Sons, Ch. 8.
- Smith, J. O. (2010). *Physical Audio Signal Processing*, online edition, Ch. 8 "Phasing with First-Order Allpass Filters."
- Kiiski, R., Esqueda, F., & Välimäki, V. (2016). "Time-Variant Gray-Box Modeling of a Phaser Pedal." *DAFx-16*, Brno.
- Dattorro, J. (1997). "Effect Design Part 1: Phaser and Flanger." *JAES*, Preprint 4776.
- "Allpass Filter: All You Need To Know" — WolfSound (thewolfsound.com/allpass-filter/).
- Audio-DSP-Phaser — GitHub: JDSherbert/Audio-DSP-Phaser.