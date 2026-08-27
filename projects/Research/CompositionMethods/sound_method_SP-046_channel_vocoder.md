# Channel Vocoder (Filter-Bank Vocoder) — Sound Production Method SP-046

**ID**: SP-046
**Layer**: Synthesis Engines
**Target Output**: Spectral-Envelope Transfer / Cross-Synthesis Timbres
**Paradigm**: Rules-Based (deterministic DSP) — no training, no corpus.

## One-line description
Classic filter-bank vocoder (Dudley 1939): decompose a *modulator* into N log-spaced band envelopes, then gain-modulate an identical filter bank driven by a *carrier* to impose the modulator's spectral shape onto the carrier — the "robot voice"/talkbox effect and a general cross-synthesis tool.

## Summary-table row
| **SP-046** | Channel Vocoder (Filter-Bank Vocoder) | **Synthesis Engines** | Spectral-Envelope Transfer / Cross-Synthesis Timbres | Splits the signal into an analysis bank (N log-spaced bandpass filters → rectified, smoothed envelopes) and a synthesis bank (identical filters gain-modulated by those envelopes) to impose a modulator's spectral shape onto a carrier. Classic Dudley (1939) "robot voice"/talkbox effect and general cross-synthesis tool; voiced/unvoiced detector picks pitched vs noise carrier. |

## Source
Homer Dudley, Bell Labs (1939), US Patent 2,151,091; the Voder demonstrated at the 1939 New York World's Fair. Core of SIGSALY (1943), the first secure voice-encryption system. Complements LPC (SP-028), formant synthesis (SP-004/SP-015/SP-025/SP-038), phase vocoder (SP-026), and SMS (SP-027). The sound-production counterpart to spectral-analysis composition methods (039 SMA, 031 spectral cross-synthesis).

## Technical Mechanics (full math)

**1. Analysis filter bank.** $N$ bandpass filters $H_k(f)$, $k = 1 \dots N$, log-spaced centers $f_k = f_{low} \cdot (f_{high}/f_{low})^{k/N}$ (80 Hz → 8 kHz, $N = 8$–$32$). Each is a 2nd-order bandpass (constant-Q biquad):

$$H_k(z) = \frac{b_{0,k}(1 - z^{-2})}{1 + a_{1,k} z^{-1} + a_{2,k} z^{-2}}$$

Modulator $x(n)$ filtered per band: $x_k(n) = x(n) \ast h_k(n)$.

**2. Envelope extraction.** Full-wave rectify + lowpass (cutoff ~20–30 Hz):

$$e_k(n) = \text{LPF}\big(\,|x_k(n)|\,\big)$$

The envelope carries the slow spectral-energy trajectory; phase/pitch structure is discarded.

**3. Synthesis filter bank.** Carrier $c(n)$ through the *identical* bank, gain-modulated per band:

$$y_k(n) = e_k(n) \cdot \big(c(n) \ast h_k(n)\big)$$

**4. Output.** Sum all bands:

$$y(n) = \sum_{k=1}^{N} e_k(n)\, \big(c(n) \ast h_k(n)\big)$$

**5. Carrier selection.** Voiced/unvoiced detector (zero-crossing rate + low-band energy) picks sawtooth/square at modulator $f_0$ (voiced) vs white noise (unvoiced). For cross-synthesis the carrier is another instrument, retaining its own harmonic content under a reshaped spectral envelope.

**Complexity**: $\mathcal{O}(N \cdot T)$ per stage ($N$ biquads × samples, twice). Real-time on CPU for $N \le 64$; no FFT required.

## Python / NumPy implementation sketch

```python
import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

def log_spaced_centers(n_bands, f_low=80.0, f_high=8000.0):
    return f_low * (f_high / f_low) ** (np.arange(n_bands) / n_bands)

def design_bandpass_bank(centers, fs, q=2.0):
    sos_list = []
    for fc in centers:
        bw = fc / q
        low = max(fc - bw/2, 1.0)
        high = min(fc + bw/2, fs/2 - 1.0)
        sos_list.append(butter(2, [low, high], btype='bandpass', fs=fs, output='sos'))
    return sos_list

def envelope_extract(band_signal, fs, cutoff=30.0):
    rect = np.abs(band_signal)
    sos = butter(2, cutoff, btype='lowpass', fs=fs, output='sos')
    return sosfiltfilt(sos, rect)   # zero-phase for offline; use sosfilt for real-time

def channel_vocoder(modulator, carrier, fs, n_bands=16, q=2.0, env_cutoff=30.0):
    centers = log_spaced_centers(n_bands)
    bank = design_bandpass_bank(centers, fs, q)
    out = np.zeros_like(carrier)
    for k, sos in enumerate(bank):
        xk = sosfilt(sos, modulator)
        ek = envelope_extract(xk, fs, env_cutoff)
        ck = sosfilt(sos, carrier)
        out += ek * ck
    return out / (np.max(np.abs(out)) + 1e-9)

def midi_to_hz(p): return 440.0 * 2 ** ((p - 69) / 12)
```

FFT optimization: replace per-band time-domain filters with STFT magnitude extraction (analysis) + magnitude shaping + inverse STFT (synthesis), mirroring SP-026/SP-031.

## UnitMatrix integration
- **Voices (rows)**: each voice = one vocoder instance. Modulator = another voice (cross-synthesis), external audio, or synthesized (noise / formant source SP-015/SP-038). Carrier = the voice's own pitch/harmony content (SP-029/SP-039/SP-001).
- **Sections (columns)**: each section supplies a carrier source + band config ($N$, spacing, smoothing $\tau$). Section boundary = carrier switch/crossfade; modulator envelope continuous across joins.
- **Cells** $U_{v,s}$: `{PITCH}` = carrier pitch (MIDI→Hz); `{RHYTHM}` = modulator onset/velocity envelope → $e_k$ attack/decay; `{TEXTURE}` = $N$, carrier type, voiced/unvoiced threshold, $\tau$.
- **Flow**: pick modulator/carrier → analysis bank → $N$ envelopes → synthesis bank → sum → post-process (SP-007/SP-008) → spatialize (SP-021/SP-034/SP-043).

## Pitfalls
1. Envelope smoothing too slow/fast (smears transients vs leaks carrier ripple) — set cutoff ~20–30 Hz, expose $\tau$.
2. Band overlap/leakage — use 1/3-octave or critical-band spacing, ~−3 dB crossover.
3. Carrier/envelope level mismatch — normalize output, scale envelopes by $1/N$.
4. Voiced/unvoiced misclassification — robust detector or always-pitched carrier for pitched modulators.
5. Phase cancellation across bands — use identical filter bank (same SOS, same forward filtering) both stages.
6. Zero-phase filtering latency (`sosfiltfilt`) desyncs voices — use causal `sosfilt` for real-time.
7. Robot-voice at $N < 8$ — use $N \ge 16$ (natural), $N \ge 32$ (high fidelity).
8. Pure-sine carrier has no harmonics to shape — always use harmonically rich carrier.

## References
- Dudley, H. (1939). "Remaking Speech." *JASA* 11(2).
- Dudley, H. (1939). US Patent 2,151,091, "Signal Transmission."
- Gold, B., & Rader, C. M. (1967). "The Channel Vocoder." *IEEE Trans. Audio Electroacoustics* 15(4).
- Flanagan, J. L. (1972). *Speech Analysis, Synthesis and Perception*. Springer.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley.
- Smith, J. O. (2010). *Physical Audio Signal Processing*.
