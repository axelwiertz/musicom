# Shepard–Risset Glissando Synthesis — Method SP-064

**ID:** SP-064 · **Acronym:** SRG · **Layer:** Synthesis Engines (absolute — sound production)
**Target output:** Endless Ascension / Pitch-Circular Drone & Pad Timbres

## One-line description
Sums $N$ octave-spaced partials $f_i=f_0 2^i$ under a fixed log-frequency spectral envelope $A(\log_2 f)$ of period one octave, then glides all partials upward together by a common octave offset $r(t)=ct$ while holding the envelope stationary. After one full octave every partial lands in its neighbor's slot, so the spectrum is identical to $t{=}0$ — the pitch rises forever with zero net frequency change (the Risset endless glissando). Discrete variant steps 12 semitones on a pitch-class circle (Shepard scale); tempo analog is the Risset rhythm (endless accelerando). $\mathcal{O}(N)$ per sample.

## Source
- Shepard, R. N. (1964). "Circularity in Judgments of Relative Pitch." *J. Acoust. Soc. Am.* 36(12), 2346–2353.
- Risset, J.-C. (1969). "Pitch control and pitch paradoxes demonstrated with computer-synthesized sound." *J. Acoust. Soc. Am.* 46(1B), 88.
- Risset, J.-C. (1971). *An Introductory Catalogue of Computer Synthesized Sounds*. Bell Laboratories.
- Risset, J.-C. (1986). "Pitch and rhythm paradoxes." *J. Acoust. Soc. Am.* 80(3), 961–962.
- Deutsch, D. (1986). "A musical paradox." *Music Perception* 3(3), 275–280.
- Roads, C. (1996). *The Computer Music Tutorial*, §7 (Pitch circularity / Shepard tones). MIT Press.

## Core equations

**Octave-stacked partials under a fixed envelope:**
$$y(t) = \sum_{i=0}^{N-1} A\big(\log_2(f_0)+i\big)\,\sin\!\big(2\pi f_i t + \phi_i\big),\qquad f_i = f_0 \cdot 2^i$$

**Period-one-octave spectral envelope** (stationary; does NOT glide):
$$A(\log_2 f) = \cos^2\!\Big(\tfrac{\pi}{2}(\log_2 f - \log_2 f_c)\Big)
\qquad\text{or}\qquad
A(\log_2 f) = \exp\!\Big(-\tfrac{(\log_2 f - \log_2 f_c)^2}{2\sigma^2}\Big),\ \sigma \approx 1 \text{ octave}$$

**Continuous Risset glissando** ($r(t)=ct$, offset in octaves):
$$f_i(t) = f_0 \cdot 2^{i + ct},\qquad
\phi_i(t) = 2\pi f_0\, 2^{i}\cdot \frac{2^{ct}-1}{c\ln 2}$$

**The invariance (the whole illusion):** at $t=T$ with $cT=1$ (one full octave), $f_i(T)=f_0 2^{i+1}=f_{i+1}(0)$ — every partial sits in its neighbor's former slot, and the stationary envelope assigns the identical amplitude. The spectrum is *exactly* the same as $t{=}0$, yet each partial tracked continuously rose one octave → endless ascension with zero net frequency change.

**Discrete Shepard scale:** offset steps $k/12$ octaves, $k=0,\dots,11$; after 12 steps the set returns to itself → a circular chromatic scale with no octave boundary.

**Risset rhythm (tempo analog):** inter-onset intervals halve each cycle under a log-tempo-periodic loudness envelope → endless accelerando.

## Implementation (NumPy)

```python
import numpy as np

def shepard_risset_glissando(f0, n_partials, octaves_per_sec, duration, sr,
                             envelope="cos", f_center=1000.0, sigma=1.0,
                             direction=+1.0):
    """Render a continuous Shepard-Risset glissando (endless ascension).

    f0:              reference frequency of the lowest audible partial (Hz)
    n_partials:      octave-spaced partial count (>= 8)
    octaves_per_sec: glissando rate in octaves/second (+ rising, - falling)
    duration:        seconds (choose so octaves_per_sec * duration is an INTEGER)
    Returns a mono float32 buffer normalized to [-1, 1].
    """
    t = np.arange(int(duration * sr)) / sr
    c = direction * octaves_per_sec
    y = np.zeros_like(t)
    log2_fc = np.log2(f_center)
    for i in range(n_partials):
        phase = 2*np.pi * f0 * (2.0**i) * (np.exp2(c*t) - 1.0) / (c*np.log(2.0))
        logf = np.log2(f0) + i            # FIXED envelope coordinate
        if envelope == "cos":
            a = np.cos(np.pi*(logf - log2_fc)/2.0)**2
        else:
            a = np.exp(-((logf - log2_fc)**2) / (2.0*sigma**2))
        a = np.clip(a, 0.0, 1.0)
        y += a * np.sin(phase)
    return y / (np.max(np.abs(y)) + 1e-9)

def shepard_scale(f0, n_partials, steps=12, step_dur=0.5, sr=44100, envelope="cos"):
    """Discrete Shepard scale: 12 steps = one circular octave, endless ascent."""
    out = []
    for k in range(steps):
        out.append(shepard_risset_glissando(f0 * 2.0**(k/12.0), n_partials,
                                            0.0, step_dur, sr, envelope=envelope))
    return np.concatenate(out)
```

Candidate code path: `sound/synthesis/shepard_risset.py` (new module alongside `additive.py`, `phase_mod.py`, `spectral_wavetable.py`).

## References
- Shepard, R. N. (1964). "Circularity in Judgments of Relative Pitch." *J. Acoust. Soc. Am.* 36(12), 2346–2353.
- Risset, J.-C. (1969). "Pitch control and pitch paradoxes demonstrated with computer-synthesized sound." *J. Acoust. Soc. Am.* 46(1B), 88.
- Risset, J.-C. (1971). *An Introductory Catalogue of Computer Synthesized Sounds*. Bell Laboratories.
- Risset, J.-C. (1986). "Pitch and rhythm paradoxes." *J. Acoust. Soc. Am.* 80(3), 961–962.
- Deutsch, D. (1986). "A musical paradox." *Music Perception* 3(3), 275–280.
- Roads, C. (1996). *The Computer Music Tutorial*, §7. MIT Press.
- Risset, J.-C. (1969). *Computer Suite from Little Boy* and *Mutations*.
