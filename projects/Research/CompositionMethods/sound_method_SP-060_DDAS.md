# Denoising Diffusion Audio Synthesis (DDAS) — SP-060

**Method ID**: SP-060
**Layer**: Synthesis Engines
**Paradigm**: Stochastic / AI-Driven (learned reverse diffusion over raw audio / spectrogram / latent)
**Target Output**: Neural diffusion — corpus-learned organic timbre, breath, correlated multi-voice texture from conditioning

---

## One-line description

Audio synthesis by learning to *reverse* a fixed forward process that gradually noisifies real audio into Gaussian noise, then sampling the reverse process from pure noise under a conditioning signal $c$ (mel-spectrogram / STFT image / f0-loudness-label feature). DDIM sampling with $\eta=0$ makes it deterministic per seed; the conditioning acts as the control surface (pitch, rhythm, harmony, timbre). The audio-domain counterpart to 047 DSMG (symbolic diffusion) and the stochastic foil to 045 DDSP (deterministic DSP prior).

---

## Full technical mechanics

### 1. Forward (noising) process

A fixed Markov chain adds Gaussian noise to data $x_0$ over $T$ steps:

$$q(x_t \mid x_{t-1}) = \mathcal{N}\!\big(x_t;\ \sqrt{1-\beta_t}\,x_{t-1},\ \beta_t \mathbf{I}\big)$$

where $\beta_1,\dots,\beta_T \in (0,1)$ is a variance schedule (linear from $10^{-4}$ to $0.02$, or cosine). Let $\alpha_t = 1-\beta_t$ and $\bar\alpha_t = \prod_{s=1}^{t}\alpha_s$. By Gaussian reparameterization and additivity, the full trajectory is closed-form from $x_0$:

$$q(x_t \mid x_0) = \mathcal{N}\!\big(x_t;\ \sqrt{\bar\alpha_t}\,x_0,\ (1-\bar\alpha_t)\mathbf{I}\big)$$

$$x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon,\qquad \epsilon \sim \mathcal{N}(0,\mathbf{I})$$

At $t=T$, $\bar\alpha_T \approx 0$ so $x_T \approx \mathcal{N}(0,\mathbf{I})$ — pure noise.

### 2. Reverse process + noise prediction ($\epsilon$-parameterization)

The reverse process is learned as

$$p_\theta(x_{t-1} \mid x_t) = \mathcal{N}\!\big(x_{t-1};\ \mu_\theta(x_t, t, c),\ \sigma_t^2 \mathbf{I}\big)$$

and instead of predicting $\mu_\theta$ directly, the network predicts the noise (the reparameterization that stabilizes training):

$$\mu_\theta(x_t,t,c) = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1-\bar\alpha_t}}\,\epsilon_\theta(x_t, t, c)\right)$$

Training objective — the simplified variational bound (single MSE, no discriminator, no ELBO balancing):

$$\mathcal{L} = \mathbb{E}_{t,\,x_0,\,\epsilon}\Big[\big\|\epsilon - \epsilon_\theta(\sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon,\ t,\ c)\big\|^2\Big]$$

### 3. Score-based SDE view

The forward process is the discretization of a variance-preserving (VP) SDE:

$$dx = -\tfrac{1}{2}\beta(t)\,x\,dt + \sqrt{\beta(t)}\,dw$$

whose reverse-time SDE is

$$dx = \big[-\tfrac{1}{2}\beta(t)\,x - \beta(t)\nabla_x \log p_t(x)\big]\,dt + \sqrt{\beta(t)}\,d\bar{w}$$

with the score identified as $\nabla_x \log p_t(x) \approx -\epsilon_\theta(x_t,t,c)/\sqrt{1-\bar\alpha_t}$. This connects DDAS to the continuous-time family of 058 NODE-CTC (both integrate a dynamical system), but with the dynamics *learned* rather than prescribed.

### 4. Sampling

**DDPM ancestral sampling** (stochastic):

$$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\Big(x_t - \frac{1-\alpha_t}{\sqrt{1-\bar\alpha_t}}\,\epsilon_\theta(x_t,t,c)\Big) + \sigma_t\,z,\qquad z \sim \mathcal{N}(0,\mathbf{I}),\ \ \sigma_t = \sqrt{\beta_t}$$

**DDIM sampling** (deterministic, accelerated — the workhorse for real-time audio):

$$\hat{x}_0 = \frac{x_t - \sqrt{1-\bar\alpha_t}\,\epsilon_\theta(x_t,t,c)}{\sqrt{\bar\alpha_t}}$$

$$x_{t-1} = \sqrt{\bar\alpha_{t-1}}\,\hat{x}_0 + \sqrt{1-\bar\alpha_{t-1}}\,\epsilon_\theta(x_t,t,c)$$

which skips steps (10–50 instead of 1000). Setting $\eta=0$ makes the process *fully deterministic given the seed* — the property that lets DDAS satisfy the musicom zero-drift determinism gate. With a variance term $\eta>0$ the DDIM update becomes stochastic DDPM (interpolates between the two).

### 5. Conditioning and classifier-free guidance

$c$ is the control surface. Waveform-domain (DiffWave) conditions on a mel-spectrogram frame sequence (plus a global timbre/style label) concatenated to U-Net features; spectrogram-domain (Riffusion) conditions by inpainting a spectrogram image. Classifier-free guidance sharpens conditioning adherence:

$$\hat\epsilon_\theta(x_t,t,c) = \epsilon_\theta(x_t,t,\varnothing) + w\,\big[\epsilon_\theta(x_t,t,c) - \epsilon_\theta(x_t,t,\varnothing)\big]$$

where $\varnothing$ is a dropped-conditioning token (10–15% dropout during training) and $w \ge 1$ is the guidance scale.

### 6. Inpainting / continuation

To continue or repair audio, keep the known region fixed: at each sampling step overwrite the known coordinates with the forward-diffused ground truth $q(x_0, \bar\alpha_t)$, so only the masked region is denoised. This chains UnitMatrix sections seamlessly.

### 7. Latent diffusion

For long audio, diffuse in a low-rate latent space: encode $z = \mathcal{E}(x)$ (VAE / neural codec), denoise the latent, decode $\hat{x} = \mathcal{D}(\hat{z})$. Riffusion uses 512×512 STFT-magnitude images (5 s) inverted by Griffin-Lim or a neural vocoder; Dance Diffusion uses a pretrained VAE latent. Latent diffusion cuts cost ~10–50×.

### 8. Complexity

Sampling $\mathcal{O}(T \cdot C)$ for $T$ steps and $C$ = cost of one U-Net forward ($\mathcal{O}(LD)$ for length-$L$ audio at width $D$). DDIM reduces $T$ to 10–50. Training GPU-bound (hours–days); inference near-real-time on GPU for short clips.

---

## Python / NumPy implementation sketch

```python
import numpy as np

# --- Pure-NumPy DDIM sampler for audio (SP-060 DDAS) ---
# Assumes a pre-trained denoiser eps_theta(x_t, t, c) is available
# (waveform: 1D conv U-Net; spectrogram: 2D U-Net over STFT images).
# Training requires a deep-learning framework (torch/jax); the schedule,
# forward noising, and sampling loops below are framework-free.

def linear_schedule(T, beta_start=1e-4, beta_end=0.02):
    betas = np.linspace(beta_start, beta_end, T)
    alphas = 1.0 - betas
    alpha_bar = np.cumprod(alphas)
    return betas, alphas, alpha_bar

def q_sample(x0, alpha_bar_t, eps=None):
    """Forward noising: x_t = sqrt(abar) x0 + sqrt(1-abar) eps."""
    eps = np.random.randn(*x0.shape) if eps is None else eps
    return np.sqrt(alpha_bar_t) * x0 + np.sqrt(1.0 - alpha_bar_t) * eps

def classifier_free(eps_theta, x_t, t, c, w=3.0):
    """Classifier-free guidance: blend conditional and unconditional."""
    uncond = eps_theta(x_t, t, None)
    if c is None:
        return uncond
    cond = eps_theta(x_t, t, c)
    return uncond + w * (cond - uncond)

def ddim_sample(eps_theta, c, shape, T=1000, steps=50, eta=0.0, seed=None):
    """DDIM (or DDPM if steps==T and eta=1) reverse sampling.
    eta=0 -> deterministic given seed; eta=1 -> stochastic DDPM.
    Returns x_0 (denoised audio, shape).
    """
    rng = np.random.default_rng(seed)
    betas, alphas, alpha_bar = linear_schedule(T)
    times = np.linspace(T - 1, 0, steps).round().astype(int)  # DDIM subsample
    x_t = rng.standard_normal(shape)  # x_T ~ N(0, I)
    for i, t in enumerate(times):
        eps = classifier_free(eps_theta, x_t, t, c, w=3.0)
        ab_t = alpha_bar[t]
        x0_hat = (x_t - np.sqrt(1.0 - ab_t) * eps) / np.sqrt(max(ab_t, 1e-8))
        t_prev = times[i + 1] if i + 1 < steps else 0
        ab_prev = alpha_bar[t_prev]
        x_t = np.sqrt(ab_prev) * x0_hat + np.sqrt(1.0 - ab_prev) * eps
        if eta > 0:
            sigma = eta * np.sqrt((1.0 - ab_prev) / (1.0 - ab_t) * (1.0 - ab_t / ab_prev))
            x_t = x_t + sigma * rng.standard_normal(shape)
    return x_t

# --- Inpainting / continuation: mask unknown region, hold known fixed ---
def inpaint(eps_theta, c, known_mask, known_audio, shape, T=1000, steps=50, seed=None):
    rng = np.random.default_rng(seed)
    betas, alphas, alpha_bar = linear_schedule(T)
    times = np.linspace(T - 1, 0, steps).round().astype(int)
    x_t = rng.standard_normal(shape)
    for t in times:
        # keep known region at its forward-diffused truth
        x_t = q_sample(known_audio, alpha_bar[t]) * known_mask + x_t * (1 - known_mask)
        eps = eps_theta(x_t, t, c)
        ab_t = alpha_bar[t]
        x0_hat = (x_t - np.sqrt(1.0 - ab_t) * eps) / np.sqrt(max(ab_t, 1e-8))
        ab_prev = alpha_bar[0] if t == times[-1] else alpha_bar[t - 1]
        x_t = np.sqrt(ab_prev) * x0_hat + np.sqrt(1.0 - ab_prev) * eps
    return x_t

# --- Musicom integration sketch (conceptual — engine does MIDI authoring) ---
# 1. Compose + fill the UnitMatrix; validate zero-drift; export symbolic MIDI.
# 2. Render each voice's conditioning c_v: either (a) a mel-spectrogram of the
#    voice rendered by any SP-xxx engine (SP-029 subtractive, SP-039 additive),
#    or (b) a direct feature trajectory (f0 + loudness + per-section label),
#    exactly as SP-045 DDSP consumes f0/loudness.
# 3. Denoise per voice: audio_v = ddim_sample(eps_theta, c_v, shape_v, seed=seed).
#    Same seed across voices + different c_v -> correlated-but-distinct timbres;
#    different seeds -> independent realizations.
# 4. Sum voices, post-process (SP-007 EQ, SP-008 DRC), spatialize (SP-021/034/043).
```

**Tooling**: schedule / forward noising / DDIM loops are framework-free NumPy and run for small U-Nets; production training/inference uses PyTorch/JAX (DiffWave/Riffusion checkpoints ~100 M params, a few seconds per 5 s clip on GPU).

---

## Musical Elements Framework

- **PITCH**: carried by the conditioning $c$, not an explicit oscillator. Mel-spectrogram / STFT conditioning encodes the pitch contour; the denoiser reproduces the fundamental + harmonic series with corpus-learned timbre. Guidance scale $w$ trades adherence (exact pitch) vs naturalness (diversity). Unlike SP-045 DDSP (pitch = hard f0 control), DDAS pitch is *emergent* — it can glide, bend, and micro-detune in ways a rigid oscillator cannot.
- **RHYTHM**: (a) the conditioning's temporal structure (onset positions) is reproduced as the attack envelope; (b) DDIM step count is a transient-sharpness knob (fewer steps = softer attacks). Cross-attention aligns conditioning frames to output frames, preserving beat positions.
- **HARMONY**: joint spectral structure of the conditioning — a chord becomes simultaneous partials; diffusion naturally models correlated multi-pitch spectra. Inpainting re-harmonizes: mask a region, re-condition on a new chord label.
- **STRUCTURE**: the conditioning schedule $[c_1 \dots c_S]$ across sections (like 047 DSMG section-token sequence, 058 NODE-CTC conditioning sequence). Inpainting chains sections seamlessly. The noise level $t$ is a global structure clock — all voices denoise in lockstep, cohering the multi-voice render.
- **TEXTURE**: the primary dimension DDAS adds — the stochastic reverse process injects corpus-learned noise/breath/air ("living" detail) that deterministic engines (SP-029/SP-039) must bolt on. Guidance scale and DDIM $\eta$ control texture density.

---

## UnitMatrix Integration (Voices and Sections)

- **Rows (Voices)**: each voice $v$ = a separate denoising run conditioned on $c_v$. **(a) shared-seed ensemble** — one noise $x_T$ per section, denoised under $V$ conditionings → correlated but timbrally distinct (diffusion analog of SP-045 per-voice banks sharing one f0 tracker); **(b) independent seeds** — each voice own noise → max voice independence (analog of entangled-vs-separable in 052 QWC).
- **Columns (Sections)**: each section prescribes a conditioning tensor $c_s$ (mel frame block / STFT region / feature vector). Columns become a conditioning arc: A = sparse flute, B = dense pad, C = re-harmonized inpainting of A. Section joins use inpainting (known = previous tail, masked = next section) → seamless.
- **Cells** $U_{v,s}$: `{PITCH}` → $c_{v,s}$ frequency content; `{RHYTHM}` → $c_{v,s}$ temporal envelope (DDIM steps set transient sharpness); `{HARMONY}` → simultaneous partials (guidance on chord label); `{TEXTURE}` → per-cell guidance $w$ and DDIM $\eta$.
- **Mapping Flow**: (1) compose + validate + export MIDI; (2) render per-voice conditioning; (3) denoise per voice (`ddim_sample`), inpainting across sections; (4) sum, post-process, spatialize.

---

## Pitfalls

1. **Phase incoherence (spectrogram domain)** → STFT-magnitude has no phase; naive Griffin-Lim is muffled/phasey. Fix: neural vocoder (HiFi-GAN/MelGAN), or diffuse in waveform/latent domain.
2. **Checkerboard/striping artifacts** → strided conv U-Net aliasing. Fix: BlurPool anti-aliased resampling, weight norm, DDPM init scaling.
3. **Too few DDIM steps → blurry** → keep steps ≥ 50 for music, raise $w$, use cosine schedule.
4. **Conditioning ignored** → drop conditioning only 10–15% in training, use classifier-free guidance at inference, monitor pitch error.
5. **Chunk-boundary clicks** → overlap-add crossfade, or carry context + inpainting so each chunk is conditioned on the previous denoised tail.
6. **Training instability** → cosine/linear schedule with $\beta_T \le 0.02$, EMA weights, gradient clipping, large batch; no GAN-style discriminator loss.
7. **Compute for long audio** → diffuse in low-rate latent (10–50× cheaper) or coarse-hop spectrogram, then vocode.
8. **Non-determinism breaks zero-drift gate** → DDIM $\eta=0$ + fixed seed for reproducible renders; reserve stochastic sampling for explicit interactive runs.

---

## Comparison With Related Methods

| Method | Generative principle | Conditioning | Output domain | Deterministic? |
|---|---|---|---|---|
| DDSP (SP-045) | deterministic DSP modules (harmonic+filtered-noise) trained end-to-end | f0 + loudness + latent timbre code | waveform | yes (given controls) |
| DSMG (047) | diffusion over discrete symbolic tokens | token context + section prompts | MIDI events | no (sampling) |
| MT-GAC (057) | adversarial (generator vs. critic) | latent vector | multi-track piano-roll | no |
| NODE-CTC (058) | prescribed neural ODE dynamics | per-section conditioning vector | continuous-time hidden state | yes (given init) |
| **DDAS (SP-060)** | **learned reverse diffusion (denoising)** | **mel/STFT/feature + label** | **waveform / spectrogram / latent** | **yes with DDIM η=0** |

---

## References

- Sohl-Dickstein, J., Weiss, E. A., Maheswaranathan, N., & Ganguli, S. (2015). "Deep Unsupervised Learning using Nonequilibrium Thermodynamics." *Proceedings of the 32nd International Conference on Machine Learning (ICML)*.
- Ho, J., Jain, A., & Abbeel, P. (2020). "Denoising Diffusion Probabilistic Models." *Advances in Neural Information Processing Systems 33 (NeurIPS)*.
- Song, Y., Sohl-Dickstein, J., Kingma, D. P., Kumar, A., Ermon, S., & Poole, B. (2021). "Score-Based Generative Modeling through Stochastic Differential Equations." *International Conference on Learning Representations (ICLR)*.
- Song, J., Meng, C., & Ermon, S. (2021). "Denoising Diffusion Implicit Models." *ICLR*. (DDIM accelerated sampling.)
- Kong, Z., Ping, W., Huang, J., Zhao, K., & Catanzaro, B. (2021). "DiffWave: A Versatile Diffusion Model for Audio Synthesis." *ICLR*.
- Forsgren, S., & Martiros, H. (2022). "Riffusion: Stable diffusion for real-time music generation." (Spectrogram-domain latent diffusion.)
- HarmonAI (2023). *Dance Diffusion* — open-source diffusion-based audio generation toolkit.
