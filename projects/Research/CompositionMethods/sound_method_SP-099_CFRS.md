# Comb Filter Resonance Synthesis (CFRS) — Sound Method SP-099

## Overview

**Comb Filter Resonance Synthesis (CFRS)** generates pitched sound by exciting a feedback comb filter with short-duration excitation signals — impulses, noise bursts, filtered noise, or oscillator pings — and letting the feedback delay line ring at its resonant frequencies. It is the simplest pitched sound synthesizer: a comb filter + impulse = pitched tone.

## Layer

**absolute** — sound production (synthesis engine). Candidate code path: `sound/synthesis/comb_resonance.py`.

## Technical Mechanics

### 1. Feedback Comb Filter (Core Resonator)

Difference equation:
$$y[n] = x[n] + g \cdot y[n - K]$$

$z$-domain transfer function:
$$H(z) = \frac{Y(z)}{X(z)} = \frac{1}{1 - g z^{-K}}$$

Frequency response magnitude:
$$|H(e^{j\omega})| = \frac{1}{\sqrt{1 + g^2 - 2g \cos(\omega K)}}$$

Resonant peaks at:
$$f_k = \frac{k}{K} \cdot f_s, \quad k = 1,2,\dots,\lfloor K/2\rfloor$$

where $f_0 = f_s / K$ is the fundamental pitch.

$T_{60}$ decay time:
$$T_{60} = \frac{-3K \cdot \log 10}{f_s \cdot \log g} \approx \frac{-6.908 \cdot K}{f_s \cdot \log g}$$

### 2. Fractional Delay

For exact equal-temperament tuning (when $K = f_s/f_0$ is fractional):

Linear interpolation (simple, ~2¢ error):
$$y[n] = x[n] + g \cdot ((1-\alpha) \cdot y[n-\lfloor K\rfloor] + \alpha \cdot y[n-\lceil K\rceil])$$

First-order allpass (flat magnitude, better):
$$H_{ap}(z) = \frac{c + z^{-1}}{1 + c z^{-1}}, \quad c = \frac{1-\alpha}{1+\alpha}$$

4-point Lagrange (highest quality):
$$y[n] = g \cdot \sum_{i=0}^{3} \ell_i(\alpha) \, y[n - \lfloor K \rfloor - i]$$

### 3. Excitation Models

| Mode | Excitation Signal | Typical Timbre |
|---|---|---|
| **Impulse (IEC)** | $x[n] = A \delta[n]$ | Plucked string, struck bar, marimba |
| **Noise Burst (NEC)** | $x[n] = A \cdot e^{-n/\tau} \cdot w[n]$ | Pitched metallic noise, snare-like |
| **Filtered Noise** | $x[n] = (\text{BPF} * w)[n]$ | Dark drone, body resonance |
| **Oscillator Ping (OEC)** | $x[n] = A \sin(2\pi f_{\text{exc}} n/f_s) e^{-n/\tau}$ | Resonant cavity tone, tuning fork |
| **Parallel Comb Bank (PCB)** | $y = \sum_c y_c$, $y_c[n] = x[n] + g_c y_c[n-K_c]$ | Bell cluster, gamelan, inharmonic wash |

### 4. Dispersion (Allpass Chain)

Chain of $M$ allpass filters inside the feedback loop for metallic inharmonicity:

$$y[n] = x[n] + g \cdot H_{ap,1} \circ \cdots \circ H_{ap,M}\{y[n-K]\}$$

Each allpass: $H_{ap,i}(z) = (c_i + z^{-1})/(1 + c_i z^{-1})$.

## Python / NumPy Implementation

```python
import numpy as np

class CombFilterResonance:
    """
    Comb Filter Resonance Synthesis (CFRS) — SP-099.
    """
    def __init__(self, sr=44100):
        self.sr = sr
        self.delay_buffer = None
        self.write_ptr = 0

    def render_note(self, pitch_midi: int, velocity: float, duration_beats: float,
                    bpm: float = 120, feedback: float = 0.98,
                    excitation: str = 'impulse', frac_delay: str = 'linear',
                    noise_burst_ms: float = 5.0, noise_filter_cutoff: float = None,
                    dispersion_coeffs: list = None) -> np.ndarray:
        duration_sec = (duration_beats * 60.0) / bpm
        n_samples = int(self.sr * duration_sec)
        freq = 440.0 * 2 ** ((pitch_midi - 69) / 12.0)
        delay_samples = self.sr / freq

        # Build excitation
        if excitation == 'impulse':
            exc = np.zeros(n_samples)
            exc[0] = velocity
        elif excitation == 'noise_burst':
            burst_len = int(self.sr * noise_burst_ms / 1000.0)
            exc = np.random.uniform(-0.5, 0.5, n_samples)
            env = np.exp(-np.arange(n_samples) / burst_len)
            exc = exc * env * velocity
            if noise_filter_cutoff is not None:
                from scipy.signal import butter, sosfilt
                sos = butter(4, noise_filter_cutoff/(self.sr/2), btype='low', output='sos')
                exc = sosfilt(sos, exc)
        elif excitation == 'osc_ping':
            ping_len = int(self.sr * noise_burst_ms / 1000.0)
            t = np.arange(ping_len)
            ping = np.sin(2*np.pi*freq*t/self.sr) * velocity
            exc = np.zeros(n_samples)
            exc[:ping_len] = ping * np.exp(-t/(ping_len/3))
        else:
            exc = np.zeros(n_samples)

        int_delay = int(np.floor(delay_samples))
        frac = delay_samples - int_delay
        buf_size = int_delay + 4
        self.delay_buffer = np.zeros(buf_size)
        self.write_ptr = 0

        out = np.zeros(n_samples)
        ap_states = [0.0 for _ in (dispersion_coeffs or [])]

        for n in range(n_samples):
            read_pos = (self.write_ptr - int_delay) % buf_size
            # Fractional delay
            if frac_delay == 'linear':
                r2 = (read_pos - 1) % buf_size
                delayed = (1-frac)*self.delay_buffer[read_pos] + frac*self.delay_buffer[r2]
            elif frac_delay == 'allpass':
                delayed = self.delay_buffer[read_pos]
                ap_state = self.delay_buffer[(read_pos-1)%buf_size] if int_delay>0 else 0.0
                delayed += frac * (delayed - ap_state)
                self.delay_buffer[(read_pos-1)%buf_size] = delayed
            else:  # lagrange4
                idx = [(read_pos-i)%buf_size for i in range(4)]
                l0 = (frac-1)*(frac-2)*(frac-3)/(-6)
                l1 = frac*(frac-2)*(frac-3)/2
                l2 = frac*(frac-1)*(frac-3)/(-2)
                l3 = frac*(frac-1)*(frac-2)/6
                delayed = l0*self.delay_buffer[idx[0]] + l1*self.delay_buffer[idx[1]] \
                        + l2*self.delay_buffer[idx[2]] + l3*self.delay_buffer[idx[3]]

            # Allpass dispersion
            if dispersion_coeffs:
                for i, c in enumerate(dispersion_coeffs):
                    ap_out = -c*delayed + ap_states[i]
                    ap_states[i] = delayed + c*ap_out
                    delayed = ap_out

            fb = feedback * delayed
            out[n] = exc[n] + fb
            self.delay_buffer[self.write_ptr] = out[n]
            self.write_ptr = (self.write_ptr + 1) % buf_size

        peak = np.max(np.abs(out))
        return out * (0.99/peak) if peak > 0 else out

    def render_parallel_bank(self, pitch_midis, amplitudes, feedbacks,
                              duration_beats, bpm=120, **kwargs):
        total = None
        for midi, amp, fb in zip(pitch_midis, amplitudes, feedbacks):
            buf = self.render_note(midi, amp, duration_beats, bpm, feedback=fb, **kwargs)
            if total is None:
                total = buf
            else:
                sz = min(len(total), len(buf))
                total = total[:sz] + buf[:sz]
        peak = np.max(np.abs(total))
        return total * (0.99/peak) if peak > 0 else total
```

## Musical Elements Framework

| Element | CFRS Mapping |
|---|---|
| **PITCH** | Delay length $K = f_s/f_0$; fractional interpolation for ET; allpass chain for inharmonicity |
| **RHYTHM** | Gate-driven onset; comb decay $T_{60}$ for sustain/overlap; burst length for micro-rhythm |
| **HARMONY** | Single comb = harmonic; PCB with coprime delays = inharmonic clusters; octave-stacked combs = chords |
| **STRUCTURE** | Section-level CFRS parameters (excitation, feedback, dispersion); decay provides crossfade |
| **TEXTURE** | 4 excitation modes × PCB density × dispersion; uniform vs inharmonic spectral decay |

## UnitMatrix Integration

**Voices = rows**: Each voice is one CFRS instance or PCB group with per-note parameters (pitch, velocity, feedback, excitation, dispersion).

**Sections = columns**: Section-level CFRS defaults overrideable per note.

**Cells = MusicUnit**: Iterates notes in section, renders each via CFRS, sums into audio buffer.

**Production dispatch**: `produce(midi_path, method="SP-099", params={...})`

## DSP Requirements

- Python 3.x, NumPy, SciPy (optional for scipy.signal filters)
- Sampling rate: 44100 Hz (standard), 48000 Hz (pro)
- Memory: ~4 bytes × ($K$ + 4) per comb ($K = f_s/f_0$, ~21–1010 for MIDI 12–108)
- CPU: $\mathcal{O}(1)$ per sample per comb; PCB with $C$ combs = $\mathcal{O}(C)$
- Latency: block-based rendering (no real-time constraint in offline music notation pipeline)

## Key Differences from Related Methods

| vs. SP-011 (Karplus-Strong) | No loop lowpass filter → uniform harmonic decay, brighter/metallic; impulse or noise burst vs KS's initial noise burst only; pre-filter optional not required |
|---|---|
| vs. SP-032 (FDN Reverb) | Single feedback comb vs N-comb matrix; designed for pitched tone generation not spatialization; impulse train excitation vs diffuse noise |
| vs. SP-033 (Digital Waveguide) | Single delay line without scattering junctions; no bidirectional wave splitting; no terminations/boundary conditions |
| vs. SP-042 (Modal Synthesis) | Delay-line resonator bank vs biquad filter bank; combs carry whole harmonic series vs per-mode biquads; cheaper ($\mathcal{O}(C)$ vs $\mathcal{O}(N)$) but coarser |
| vs. SP-003 (Modal Plate/Bar) | Generic comb + optional dispersion vs physically derived eigenmodes; no FEM/geometry input required |

## References

1. Smith III, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing. Ch. 2–3.
2. Karplus, K. & Strong, A. (1983). "Digital Synthesis of Plucked-String and Drum Timbres." *CMJ* 7(2), 43–55.
3. Jaffe, D. A. & Smith, J. O. (1983). "Extensions of the Karplus-Strong Plucked-String Algorithm." *CMJ* 7(2), 56–69.
4. Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters." *JAES* 45(9), 660–684.
5. Puckette, M. (2007). *The Theory and Technique of Electronic Music*. World Scientific. Ch. 4.
6. Dodge, C. & Jerse, T. A. (1997). *Computer Music: Synthesis, Composition, and Performance* (2nd ed.). Schirmer. pp. 129–137.
7. Roads, C. (1996). *The Computer Music Tutorial*. MIT Press. Ch. 6.
8. Välimäki, V. et al. (2012). "Fifty Years of Artificial Reverberation." *IEEE Trans. Audio, Speech & Lang. Process.* 20(5), 1421–1448.