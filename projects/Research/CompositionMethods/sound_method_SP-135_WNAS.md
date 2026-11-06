# SP-135 — WaveNet Autoregressive Sample Synthesis (WNAS)

**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**ID:** SP-135
**Acronym:** WNAS
**One-line:** Learns the conditional distribution of each audio sample given all previous ones and renders raw audio by sequential autoregressive sampling, conditioned on mel/f0 features and global timbre codes.
**Candidate code path:** `sound/synthesis/wavenet_synthesis.py`
**Dispatched from:** `workflows/musicom_workflow.py::produce(method="SP-135", ...)`

---

## 1. Overview

WaveNet (van den Oord et al. 2016) is a fully probabilistic, autoregressive generative
model of raw audio. It factorizes the joint probability of a waveform as

$$p(\mathbf{x}) = \prod_{t=1}^{T} p(x_t \mid x_1, \dots, x_{t-1})$$

and models each conditional with a stack of **dilated causal convolutions** and
**gated activation units**, ending in a **256-way softmax** over μ-law-companded
sample values. Training maximizes exact log-likelihood (teacher forcing, fully
parallel over time). Generation is sequential: one sample predicted, fed back,
repeat. Conditioning (global: instrument/speaker/section codes; local: mel/f0
feature sequences) turns the raw model into an instrument that can switch timbre,
follow a score, and morph between instruments (NSynth).

Contrast with the DB neighbors:

| Method | Paradigm | Output | Objective |
|---|---|---|---|
| **SP-135 WNAS** | Autoregressive next-sample categorical | sample index (256 μ-law levels) | cross-entropy over samples |
| SP-045 DDSP | Feed-forward differentiable DSP modules | synthesis parameters (harmonic amps, noise filter, reverb) | spectral loss on rendered frames |
| SP-060 DDAS | Diffusion denoising (iterative) | whole waveform from noise | denoising score matching |

---

## 2. Technical Mechanics

### 2.1 μ-law companding front-end (ITU-T G.711, μ = 255)

Raw 16-bit audio (65,536 values) would need a 65,536-way softmax. Companding
compresses it to 256 levels:

$$f(x_t) = \operatorname{sign}(x_t)\,\frac{\ln\!\left(1 + \mu\,|x_t|\right)}{\ln(1+\mu)},\qquad -1 < x_t < 1,\quad \mu = 255$$

The law is ~linear for small signals and logarithmic for large ones, giving
roughly amplitude-independent *perceptual* quantization error. Inverse:

$$f^{-1}(y) = \operatorname{sign}(y)\,\frac{(1+\mu)^{|y|}-1}{\mu}$$

**Verified (this document, `_web135/sp135_verify.py`, NumPy, 16 kHz):**
round-trip SNR = **38.1 dB** at full scale, **33.8 dB** at −40 dBFS (naive
companded-domain rounding). This is the real noise floor of 256-level coding —
audible on quiet passages; plan the delivery chain accordingly (see Pitfalls).

### 2.2 Dilated causal convolutions

A causal convolution at layer $k$ with dilation $d_k$ computes

$$y[t] = \sum_{j=0}^{L-1} w[j]\,x[t - j\,d_k]$$

i.e. the filter is applied to inputs $d_k$ samples apart ("à trous"). Causality:
$y[t]$ depends only on $x[\le t]$. A stack of $K$ layers, filter length 2,
dilations $1,2,4,\dots,2^{K-1}$, has receptive field

$$R = 1 + \sum_{i=0}^{K-1} 2^i = 2^{K}$$

The paper's schedule is `1,2,4,...,512` per block (K=10, R=1024), repeated
3× (R ≈ 3072 samples ≈ 190 ms @16 kHz / 70 ms @44.1 kHz), and larger stacks for
music.

**Verified:** one-block receptive field measured exactly **1024**; 3-block last
tap **3069** (tap convention of the residual path); **zero future leakage**
(causality holds).

### 2.3 Gated activation unit (gated PixelCNN)

$$\mathbf{z} = \tanh\!\left(W_{f,k}\ast\mathbf{x}\right)\;\odot\;\sigma\!\left(W_{g,k}\ast\mathbf{x}\right)$$

- $W_{f,k}$: filter branch (content), $W_{g,k}$: gate branch (attention),
  $\ast$: convolution, $\odot$: elementwise product, $\sigma$: logistic sigmoid.
- The gate multiplicatively admits/blocked the tanh-filtered content; found
  significantly better than ReLU for audio (the paper's initial experiments).

### 2.4 Residual and parameterized skip connections

Each layer output $\mathbf{z}$ is projected twice:
- residual branch: $\mathbf{x}_{k+1} = \mathbf{x}_k + W_{r,k}\ast\mathbf{z}$ (deep-stack training, He et al. 2015)
- skip branch: $\mathbf{y} \mathrel{+}= W_{s,k}\ast\mathbf{z}$ (accumulated across all layers)

The accumulated skip sum goes through ReLU layers and the final 256-way softmax.

### 2.5 Conditioning

**Global** (one vector $\mathbf{h}$, broadcast over time — timbre/speaker/section):

$$\mathbf{z}=\tanh\!\left(W_{f,k}\ast\mathbf{x}+V_{f,k}^{T}\mathbf{h}\right)\;\odot\;\sigma\!\left(W_{g,k}\ast\mathbf{x}+V_{g,k}^{T}\mathbf{h}\right)$$

**Local** (time series $\mathbf{h}_t$, lower rate, upsampled by transposed
convolution $\mathbf{y}=f(\mathbf{h})$ to sample rate):

$$\mathbf{z}=\tanh\!\left(W_{f,k}\ast\mathbf{x}+V_{f,k}\ast\mathbf{y}\right)\;\odot\;\sigma\!\left(W_{g,k}\ast\mathbf{x}+V_{g,k}\ast\mathbf{y}\right)$$

with $V_{f,k}\ast\mathbf{y}$ a 1×1 convolution. The TTS experiments added an
external $\log F_0$ stream at 200 Hz — a low-rate conditioning channel that
carries long-range pitch contours the finite receptive field cannot.

### 2.6 Training vs inference

- **Training:** teacher forcing — predict all timesteps in parallel from
  ground-truth context (causal conv = shifted normal conv at train time);
  maximize log-likelihood = cross-entropy over 256 classes. Exact and tractable,
  so validation-set hyper-parameter tuning works.
- **Inference:** sequential — predict $x_t$, feed back, predict $x_{t+1}$.
  Naive cost $O(RF)$ MACs/sample/layer (measured 32.8 M MACs per 1 s @16 kHz for
  30 layers). Fixes: (a) **cached-state** inference — each layer keeps a queue of
  its own dilation-tap history, cost collapses to $O(\text{layers})$ per sample;
  (b) **Parallel WaveNet** (van den Oord et al. 2017) — distill the teacher into
  an inverse-autoregressive-flow (IAF) student that emits all samples in
  parallel, **>20× faster than real-time**.

---

## 3. NumPy implementation sketch (reference, inference)

```python
import numpy as np

MU = 255

def mulaw_quantize(x, mu=MU):
    """Float in (-1,1) -> level index in [0,255] (mu-law companded)."""
    y = np.sign(x) * np.log1p(mu * np.abs(x)) / np.log1p(mu)
    return np.clip(np.round(y * 127.5 + 127.5), 0, 255).astype(np.int64)

def inv_mulaw(level, mu=MU):
    """Level index -> float in (-1,1)."""
    y = level / 127.5 - 1.0
    return np.sign(y) * ((1 + mu) ** np.abs(y) - 1) / mu


class CachedDilatedCausalConv1D:
    """Causal dilated convolution with cached tap queues (O(1) per sample).
    Equivalent to out[t] = sum_j w[j] * x[t - j*d], causality by construction."""

    def __init__(self, w, dilation):
        self.w = np.asarray(w, dtype=np.float64)          # length-2 filter [w0, w1]
        self.d = int(dilation)
        self.q = np.zeros(self.d * (len(self.w) - 1) + 1)  # delay line for w1 taps

    def step(self, x):
        self.q = np.roll(self.q, 1)
        self.q[0] = x
        return self.w[0] * x + self.w[1] * self.q[self.d]


class GatedResidualBlock:
    """tanh(Wf*x) * sigmoid(Wg*x), then residual + skip projections."""

    def __init__(self, wf, wg, wr, ws, h_global=None, vf=None, vg=None):
        self.f = CachedDilatedCausalConv1D(wf, dilation=1)   # dilation set by caller
        self.g = CachedDilatedCausalConv1D(wg, dilation=1)
        self.wr, self.ws = wr, ws
        self.hg, self.vf, self.vg = h_global, vf, vg

    def step(self, x):
        f = np.tanh(self.f.step(x) + (self.vf @ self.hg if self.hg is not None else 0.0))
        g = 1.0 / (1.0 + np.exp(-(self.g.step(x) + (self.vg @ self.hg if self.hg is not None else 0.0))))
        z = f * g
        return x + self.wr * z, self.ws * z              # (residual, skip)


class WaveNetVocoder:
    """Reference autoregressive sampler: 3 blocks x dilations 1..512."""

    def __init__(self, n_blocks=3, n_hidden=64, rng_seed=0, temperature=0.9):
        self.rng = np.random.default_rng(rng_seed)
        self.temp = temperature
        dilations = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] * n_blocks
        self.blocks = []
        for d in dilations:
            self.blocks.append(GatedResidualBlock(
                np.random.randn(2) * 0.1, np.random.randn(2) * 0.1,
                np.random.randn() * 0.1, np.random.randn() * 0.1))
            # NOTE: dilations differ per layer; set self.blocks[-1].f.d = d etc.
            self.blocks[-1].f.d = d
            self.blocks[-1].g.d = d

    def sample(self, n_samples, cond_seq, global_code):
        out = np.zeros(n_samples)
        x = 0.0
        for t in range(n_samples):
            skip_sum = 0.0
            for b in self.blocks:
                x, s = b.step(x)
                skip_sum += s
            logits = 3.0 * skip_sum / self.temp       # crude head; real head = 2xReLU+softmax
            p = np.exp(logits - np.max(logits))       # placeholder 256-way distribution
            lvl = int(self.rng.integers(0, 256))      # sample level (real: categorical)
            x = inv_mulaw(lvl)
            out[t] = x
        return out
```

> The sketch above demonstrates the *mechanics* (μ-law codec, cached causal
> dilated conv with O(1) per-sample cost, gated unit, autoregressive loop). A
> *trained* model needs PyTorch + a corpus (NSynth, MagnaTagATune, or a project
> corpus) — see References. The verified math (μ-law SNR, receptive field,
> causality, softmax normalization) is in `_web135/sp135_verify.py`.

---

## 4. Musical Elements Framework

- **PITCH** — lives in the local conditioning (mel/f0), not an oscillator;
  continuous-time generation makes glides/microtones free; long-range pitch
  contours require an explicit low-rate f0 stream (~200 Hz).
- **RHYTHM** — absolute sample clock; onsets emerge from conditioning changes +
  learned attack statistics; sample-count exact → zero-drift safe by construction.
- **HARMONY** — one channel = one source; chords = rows (UnitMatrix voices);
  NSynth latent codes enable timbre morphing within a voicing.
- **STRUCTURE** — global codes per section = timbre switches; all long-range
  structure must be explicit in conditioning (the model's RF ≈ 190 ms cannot
  carry it).
- **TEXTURE** — the learned conditional distribution captures harmonics, noise,
  breath, room, even corpus recording quality; temperature = determinism knob.

---

## 5. UnitMatrix Integration

- **Rows = voices = conditioning streams** (`{model, global_code, sampler:{temperature, seed}, cached_state}`); each row owns its autoregressive state.
- **Columns = sections = conditioning segments** (`{global_code, feature_source, align:{hop, window}}`); state carried across seams (no click).
- **Cells = MusicUnit** → guide render (SP-001/SP-029/…) → feature extraction (mel/f0, fixed hop/window) → autoregressive resynthesis of exactly `n_samples = int(section_ticks/ticks_per_beat * 60/bpm * fs)`.
- **Produce:** `produce(midi_path, method="SP-135", params={...})`.
- **Stage order:** guide render → features → WNAS (replaces per-row source) → tone (SP-007) → spatialize (SP-021/053/132) → room (SP-009/032/075) → dynamics (SP-008/107) → loudness (SP-126) → dither (SP-122).

---

## 6. Pitfalls

1. Sequential generation is slow — use cached-state or IAF-distilled parallel inference.
2. 256-level μ-law noise floor ≈ 38 dB SNR (measured) — audibly lossy on quiet passages.
3. Exposure bias (teacher forcing vs self-feeding at generation) — errors accumulate.
4. RF ≈ 190 ms — no long-range coherence; conditioning must carry structure.
5. Build-time method: needs corpus + GPU training; `produce()` needs a checkpoint.
6. Stochastic sampling — seed + temperature for determinism; clip logits.
7. Naive NumPy causal conv is quadratic — implement tap queues.
8. The model reproduces the corpus's flaws (recording quality included).
9. Conditioning alignment: `n_samples` must be an exact multiple of the feature hop.
10. Distinct from SP-045 (DDSP) and SP-060 (DDAS) — do not chain interchangeably.
11. f0 must be in the conditioning for melodic rows.
12. Zero-drift: emit exactly the section sample count; warm-up inside the cell, never trim.

---

## 7. References

- van den Oord, A., et al. (2016). "WaveNet: A Generative Model for Raw Audio." arXiv:1609.03499.
- van den Oord, A., et al. (2017). "Parallel WaveNet: Fast High-Fidelity Speech Synthesis." arXiv:1711.10433 (ICML 2018).
- Engel, J., et al. (2017). "Neural Audio Synthesis of Musical Notes with WaveNet Autoencoders." arXiv:1704.01279 (ICML 2017).
- Engel, J., et al. (2020). "DDSP: Differentiable Digital Signal Processing." ICLR 2020.
- Ho, J., et al. (2020). "Denoising Diffusion Probabilistic Models." NeurIPS 2020.
- ITU-T (1988). Recommendation G.711 (μ-law companding).
- Yu, F., & Koltun, V. (2016). "Multi-Scale Context Aggregation by Dilated Convolutions." ICLR 2016.
- van den Oord, A., Kalchbrenner, N., & Kavukcuoglu, K. (2016). "Pixel Recurrent Neural Networks." ICML 2016.
- Verification prototype: `projects/Research/CompositionMethods/_web135/sp135_verify.py` + `_web135/verify_output.txt`.
