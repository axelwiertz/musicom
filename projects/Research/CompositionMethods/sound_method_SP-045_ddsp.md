# Differentiable Digital Signal Processing (DDSP) — Sound Method SP-045

**ID**: SP-045
**Name**: Differentiable Digital Signal Processing (DDSP)
**Layer**: Synthesis Engines
**Paradigm**: AI-Driven (Deep Generative) — neural decoder driving classic DSP modules
**Target Output**: Neural-controlled harmonic + filtered-noise timbres (instrument synthesis, timbre transfer, pitch/timbre-decoupled rendering)

---

## One-Line Description
Embeds classic DSP building blocks (harmonic additive oscillator bank, time-varying filtered noise, reverberation) as differentiable modules inside a neural network, so a small decoder network learns to control genuine DSP synthesis end-to-end — giving interpretable knobs (f0, harmonic amplitudes, noise filter), strong inductive bias, and pitch/timbre decoupling.

---

## Source & History
Engel, J., Hantrakul, L., Gu, C., & Roberts, A. (2020), "DDSP: Differentiable Digital Signal Processing," *ICLR 2020*, Google Magenta. Motivated by the failure of raw-waveform autoregressive models (WaveNet, SampleRNN) to generalize from small corpora: instead of regressing samples directly, DDSP regresses the *parameters of a known DSP synthesizer*, and because every DSP op is differentiable, gradients flow from an audio-domain loss back into the network. Predecessor: Engel et al. (2017) "Neural Audio Synthesis of Musical Notes with WaveNet Autoencoders" (ICML 2017). Pitch tracker: Kim et al. (2018) "CREPE" (ICASSP 2018). Extensions: Hayes et al. (2021) "Neural Waveshaping Synthesis" (ISMIR), Shan et al. (2022) "Differentiable Wavetable Synthesis" (ICASSP).

---

## Technical Mechanics

### 1. Harmonic (additive) oscillator bank
$K$ sinusoids at integer multiples of the fundamental, with time-varying per-harmonic amplitudes $A_k(n)$:

$$y_h(n) = \sum_{k=1}^{K} A_k(n)\, \sin\!\big(\phi_k(n)\big), \qquad \phi_k(n) = 2\pi \sum_{m=0}^{n} \frac{k\, f_0(m)}{f_s}$$

Phase accumulated recursively so $f_0$ can glide (vibrato/glissando) without discontinuity:

$$\phi_k(n) = \phi_k(n-1) + \frac{2\pi k\, f_0(n)}{f_s}$$

Typical $K = 60$ harmonics (≈8 kHz bandwidth at 130 Hz f0).

### 2. Filtered noise (stochastic) component
A time-varying FIR filter driven by white noise — captures breath, bow noise, transients:

$$y_n(n) = \sum_{m=0}^{M} h_m(n)\, \epsilon(n-m), \qquad \epsilon(n) \sim \mathcal{N}(0,1)$$

$M$ typically 65 taps; the decoder outputs the taps $h_m(n)$ directly (differentiable convolution).

### 3. Reverb
Summed harmonic + noise convolved with an impulse response (learned, or synthetic FDN — see SP-032):

$$y_{out}(n) = \big(y_h(n) + y_n(n)\big) \ast r(n)$$

### 4. Encoder
- $f_0$: CREPE — 6-layer CNN, 1024-bin log-frequency output, argmax → Hz.
- Loudness: A-weighted RMS in log space:

$$l(n) = \log_{10}\!\left(\sqrt{\sum_{f} w_f\, |X(n,f)|^2}\right)$$

### 5. Decoder
MLP or GRU maps $[f_0(n), l(n), z]$ → harmonic amplitudes $A_k(n)$ (sigmoid) and noise FIR taps $h_m(n)$. $z$ = per-instrument latent embedding (timbre identity).

### 6. Multi-scale spectral loss
L1 distance in linear + log STFT magnitude across multiple FFT sizes:

$$\mathcal{L} = \sum_{i} \Big[ \|S_i(y) - S_i(\hat{y})\|_1 + \|\log S_i(y) - \log S_i(\hat{y})\|_1 \Big], \quad i \in \{2048, 1024, 512, 256, 128, 64\}$$

Log term emphasizes quiet partials/noise; multi-scale captures transients + sustained detail.

### Complexity
- Synthesis: $\mathcal{O}(K \cdot T)$ harmonic + $\mathcal{O}(M \cdot T)$ noise — real-time on CPU.
- Encoder: $\mathcal{O}(T)$ convolutional. Decoder: small MLP/GRU.
- Training dominated by STFT losses.

---

## Musical Elements Framework
- **PITCH**: $f_0(n)$ *is* the pitch control. Decoupled from timbre — same decoder renders any $f_0$ trajectory. MIDI → Hz via $f_0 = 440 \cdot 2^{(p-69)/12}$. Exact, continuous, no quantization artifacts.
- **RHYTHM**: Loudness envelope $l(n)$ + harmonic-amplitude envelope $A_k(n)$ shape attack/decay; filtered-noise supplies onset transients. Continuous (not grid-locked) — follows the UnitMatrix onset schedule.
- **HARMONY**: Lives in symbolic domain (UnitMatrix chord/pitch data). DDSP renders each voice's pitch independently; vertical harmony preserved because each voice's $f_0$ comes from chord tones already in the matrix. $A_k$ shapes *timbre*, not harmonic function.
- **STRUCTURE**: Macro-form via latent code $z$ per section (timbre switches) + per-section control trajectories. Recurrent decoder state (GRU) carries section context.
- **TEXTURE**: Harmonic/noise balance = primary texture knob. High $A_k$ + low noise = pure tone; low $A_k$ + high noise = breathy/percussive. Reverb amount + active harmonic count set density. Multiple DDSP voices summed = polyphonic texture.

---

## UnitMatrix Integration (Voices = rows, Sections = columns, Cells = MusicUnit)
- **Rows (Voices)**: Each voice $v$ = independent DDSP decoder instance, driven by its own $f_0$ + loudness from the matrix. Lead = flute-like $z_1$; Bass = bowed/saw $z_2$; Pad = high-harmonic low-noise $z_3$; Percussion = noise-dominant $z_4$. Each row renders mono buffer, summed or spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)**: Each section $s$ supplies latent timbre code $z_s$ + control trajectory over its window. Section boundaries = timbre switches/crossfades. $f_0$ + loudness continuous across joins (no reset).
- **Cells** $U_{v,s}$:
  - `{PITCH}`: MIDI pitch → $f_0$ trajectory (Hz). Glissando → smooth ramp; vibrato → sinusoidal $f_0$ modulation.
  - `{RHYTHM}`: onset times + velocities → loudness envelope $l(n)$ + amplitude attack/decay.
  - `{TEXTURE}`: latent $z$, harmonic count $K$, noise-filter order $M$, harmonic/noise mix, reverb amount.
- **Mapping Flow**:
  1. Extract per-voice $f_0$ + loudness from UnitMatrix cells.
  2. Run DDSP decoder conditioned on $[f_0, l, z_s]$ → harmonic amplitudes + noise taps.
  3. Synthesize $y_h + y_n$, sum.
  4. Reverb (SP-032 FDN or learned IR).
  5. Sum voices; post-process (SP-007 EQ, SP-008 DRC); export or spatialize.

---

## Implementation Sketch (Python / NumPy)

```python
import numpy as np

class DDSPDecoder:
    """Minimal DDSP-style decoder: MLP maps [f0, loudness, z] -> harmonic
    amplitudes + noise FIR taps, then renders harmonic + filtered-noise audio."""
    def __init__(self, n_harmonics=60, n_noise_taps=65, n_z=16, hidden=256, fs=16000, seed=0):
        rng = np.random.default_rng(seed)
        self.K = n_harmonics
        self.M = n_noise_taps
        self.fs = fs
        # small MLP weights (trained end-to-end in practice; random here for demo)
        self.W1 = rng.normal(0, 0.1, (hidden, 3 + n_z))
        self.b1 = np.zeros(hidden)
        self.W_amp = rng.normal(0, 0.1, (n_harmonics, hidden))
        self.W_fir = rng.normal(0, 0.1, (n_noise_taps, hidden))

    def _mlp(self, c):
        h = np.tanh(self.W1 @ c + self.b1)
        A = 1 / (1 + np.exp(-(self.W_amp @ h)))   # (K,) in [0,1]
        h_fir = self.W_fir @ h                     # (M,) FIR taps
        return A, h_fir

    def render(self, f0, loudness, z, T):
        """f0: (T,) Hz, loudness: (T,), z: (n_z,) latent -> (T,) audio."""
        out = np.zeros(T)
        phase = np.zeros(self.K)
        noise_state = np.zeros(self.M)
        rng = np.random.default_rng(1)
        for n in range(T):
            c = np.concatenate([[f0[n]], [loudness[n]], z])
            A, h_fir = self._mlp(c)
            # harmonic bank
            phase = (phase + 2 * np.pi * np.arange(1, self.K + 1) * f0[n] / self.fs) % (2 * np.pi)
            y_h = np.sum(A * np.sin(phase))
            # filtered noise (time-varying FIR)
            eps = rng.normal()
            noise_state = np.roll(noise_state, 1)
            noise_state[0] = eps
            y_n = np.dot(h_fir, noise_state)
            out[n] = y_h + y_n
        return out

def midi_to_hz(p):
    return 440.0 * 2 ** ((p - 69) / 12)
```

- **Training**: Full DDSP trains encoder (CREPE) + decoder jointly against multi-scale spectral loss using autograd (PyTorch/TensorFlow). NumPy-only feasible for *inference* once weights exported.
- **Tooling**: PyTorch/TensorFlow for training; NumPy for offline inference; musicom engine for UnitMatrix fill + zero-drift MIDI export upstream.

---

## Pitfalls
1. **Pitch-tracker octave errors** — CREPE can report $f_0$ an octave off. Fix: median-filter, octave-correction, or drive $f_0$ directly from MIDI (UnitMatrix always has exact pitch).
2. **Aliasing from high harmonics** — if $K \cdot f_0 > f_s/2$, upper partials alias. Fix: cap $K$ so $K \cdot f_{0,\max} < f_s/2$, or apply per-harmonic rolloff.
3. **Harmonic/noise imbalance** — too much noise = hissy; too little = sterile organ tone. Fix: expose mix as cell parameter; log-term in loss calibrates noise energy.
4. **Phase discontinuity on f0 jumps** — abrupt note transitions can click. Fix: keep phase accumulator running (never reset), or crossfade amplitudes.
5. **Reverb smearing transients** — long IR blurs attacks. Fix: short early-reflection IR or FDN with damping (SP-032); route noise transients around reverb.
6. **Latent posterior collapse** — decoder ignores $z$, timbres collapse. Fix: KL annealing, or fixed per-instrument embedding table.
7. **Training-data timbre bias** — only reproduces corpus timbres. Fix: augment corpus, larger latent space.
8. **Loudness normalization mismatch** — naive velocity→loudness over/under-drives decoder. Fix: calibrate velocity to training loudness range.

---

## References
- Engel, J., Hantrakul, L., Gu, C., & Roberts, A. (2020). "DDSP: Differentiable Digital Signal Processing." *ICLR 2020*.
- Engel, J., et al. (2017). "Neural Audio Synthesis of Musical Notes with WaveNet Autoencoders." *ICML 2017*.
- Kim, J. W., Salamon, J., Li, P., & Bello, J. P. (2018). "CREPE: A Convolutional Representation for Pitch Estimation." *ICASSP 2018*.
- Hayes, B., Saitis, C., & Fazekas, G. (2021). "Neural Waveshaping Synthesis." *ISMIR 2021*.
- Shan, S., Hantrakul, L., et al. (2022). "Differentiable Wavetable Synthesis." *ICASSP 2022*.
- Magenta DDSP repository (2020–present). Reference implementation (PyTorch/TensorFlow).
