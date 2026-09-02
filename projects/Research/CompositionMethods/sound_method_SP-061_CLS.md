# Cepstral Liftering Synthesis (CLS) — Method SP-061

**ID:** SP-061 · **Acronym:** CLS · **Layer:** Synthesis Engines
**Target output:** Homomorphic Source/Resonator Deconvolution / Cross-Synthesis Timbres

## One-line description
Deconvolves a sound into excitation (source) and resonator (spectral envelope) via the complex cepstrum $\hat{x}=\mathcal{F}^{-1}\{\log X[k]\}$, then recombines one sound's excitation with another's resonator for exact, phase-preserving cross-synthesis.

## Source
Bogert, Healy & Tukey (1963) introduced the cepstrum (with its anagram vocabulary: *cepstrum/spectrum*, *quefrency/frequency*, *lifter/filter*, *saphe/phase*). Oppenheim (1965) formalized the complex cepstrum; Oppenheim & Schafer (1975/2009) developed it into homomorphic signal processing. In the Musicom catalog CLS is the exact-deconvolution counterpart to SP-028 LPC (parametric all-pole) and the phase-preserving foil to SP-031 (magnitude-only STFT cross-synthesis).

## Core theorem (homomorphic deconvolution)
For $x[n] = e[n] * h[n]$ (source convolved with resonator), the cepstrum converts convolution into **addition**:
$$\hat{x}[n] = \hat{e}[n] + \hat{h}[n], \qquad \hat{x}[n] = \mathcal{F}^{-1}\{\log X[k]\}$$

- $\hat{h}$ (envelope/formants/body) → **low quefrency** (near $q=0$)
- $\hat{e}$ (excitation/periodicity) → **high quefrency** (rahmonic peaks at $k q_0$, $q_0 = 1/f_0$)

A **lifter** $\ell[n]$ (quefrency window) separates them:
$$\hat{h}[n] \approx \hat{x}[n]\,\ell_{low}[n], \qquad \hat{e}[n] \approx \hat{x}[n]\,\ell_{high}[n], \qquad \ell_{low}+\ell_{high}=1$$

## The three cepstra
| Variant | Formula | Phase | Use |
|---|---|---|---|
| Power | $C_p[q] = |\mathcal{F}^{-1}\{\log|X|^2\}|^2$ | no | detection |
| Real | $C_r[q] = \mathcal{F}^{-1}\{\log|X|\}$ | no (min-phase only) | envelope/pitch measure |
| Complex | $\hat{x}[n] = \mathcal{F}^{-1}\{\log|X| + j\,\angle X\}$ | **yes** | **synthesis** |

## Cross-synthesis (source A × resonator B)
$$y[n] = \mathcal{F}^{-1}\{\exp(\mathcal{F}\{\hat{e}_A[n] + \hat{h}_B[n]\})\} = \mathcal{F}^{-1}\{\exp(\log E_A[k] + \log H_B[k])\}$$

Result: A's pitch/voicing + B's timbre/formant, with **phase preserved exactly** (no Griffin-Lim).

## Envelope interpolation (timbral morph)
$$\hat{h}_{A\to B}(\tau) = (1-\tau)\,\hat{h}_A + \tau\,\hat{h}_B, \qquad \tau\in[0,1]$$
A linear morph in quefrency space = a smooth, physically-plausible formant glide.

## Quefrency as a musical parameter
- Peak at $q_0$ ⇒ fundamental $f_0 = f_s/q_0$ (built-in pitch detector).
- Rahmonics at $k q_0$ ⇒ harmonics.
- Lifter cutoff $Q_c > 1/f_{0,min}$ keeps fundamentals in the source band; the cutoff decides what counts as timbre vs. pitch.
- A rahmonic at $q=\tau_{echo}$ = a delayed echo (add = insert reflection, notch = de-reverberate).

## Implementation (NumPy)

```python
import numpy as np

def complex_cepstrum(x, nfft=None):
    nfft = nfft or len(x)
    X = np.fft.fft(x, n=nfft)
    logX = np.log(np.abs(X) + 1e-12) + 1j * np.unwrap(np.angle(X))
    return np.fft.ifft(logX).real, X

def real_cepstrum(x, nfft=None):
    nfft = nfft or len(x)
    X = np.fft.fft(x, n=nfft)
    return np.fft.ifft(np.log(np.abs(X) + 1e-12)).real

def lifter_mask(n, q_cut, taper=0.1):
    m = np.zeros(n)
    q_cut = int(q_cut)
    edge = max(1, int(q_cut * taper))
    m[:q_cut] = 1.0
    for i in range(q_cut, q_cut + edge):
        if i < n:
            m[i] = 0.5 * (1 + np.cos(np.pi * (i - q_cut) / edge))
    m[-q_cut:] = m[1:q_cut + 1][::-1] if q_cut + 1 < n else m[1:][::-1]
    return m

def decompose(x, q_cut, nfft=None):
    nfft = nfft or len(x)
    xhat, X = complex_cepstrum(x, nfft)
    m = lifter_mask(nfft, q_cut)
    H = np.exp(np.fft.fft(xhat * m))
    E = np.exp(np.fft.fft(xhat * (1 - m)))
    return H, E

def cross_synthesize(exciter, resonator, q_cut, nfft=None):
    nfft = nfft or max(len(exciter), len(resonator))
    _, E = decompose(exciter, q_cut, nfft)     # source/excitation
    H, _ = decompose(resonator, q_cut, nfft)   # resonator/envelope
    return np.fft.ifft(np.exp(np.log(E) + np.log(H))).real

def cepstral_pitch(x, f_s, f_lo=50.0, f_hi=1000.0):
    c = real_cepstrum(x)
    q_lo, q_hi = int(f_s / f_hi), int(f_s / f_lo)
    return f_s / (q_lo + np.argmax(c[q_lo:q_hi]))
```

Real-time: 2048-sample FFT frames, 50% overlap, raised-cosine analysis window, overlap-add accumulation.

## References
- Bogert, Healy & Tukey (1963). "The Quefrency Alanysis of Time Series for Echoes…" *Proc. Symp. Time Series Analysis*, Wiley.
- Oppenheim (1965). "Superposition in a class of nonlinear systems." Ph.D. diss., MIT RLE.
- Oppenheim & Schafer (1975). *Digital Signal Processing*. Prentice-Hall.
- Childers, Skinner & Kemerait (1977). "The Cepstrum: A Guide to Processing." *Proc. IEEE* 65(10).
- Oppenheim & Schafer (2004). "From frequency to quefrency." *IEEE Signal Processing Magazine* 21(5).
- Randall (2017). "A history of cepstrum analysis…" *MSSP* 97.
- Oppenheim & Schafer (2009). *Discrete-Time Signal Processing*, 3rd ed.
