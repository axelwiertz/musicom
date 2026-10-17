# Discrete Denoising Diffusion Probabilistic Model Composition (D3PM-C) — Method 118

**Paradigm:** AI-Driven  
**Layer:** concrete  
**Acronym:** D3PM-C  
**Next free ID:** 119

---

## Overview

Discrete Denoising Diffusion Probabilistic Model Composition (D3PM-C) applies structured discrete-state diffusion (Austin et al. 2021, D3PM, NeurIPS) to the generation of symbolic music directly in the discrete token domain. Unlike continuous diffusion models (047 DSMG) which add Gaussian noise to continuous values, D3PM-C corrupts and denoises tokens (pitch classes, duration labels, velocity bins, instrument codes) via a Markov transition matrix over a categorical vocabulary. The forward process gradually replaces tokens with noise according to a schedule; the reverse process learns to reconstruct the original sequence step by step.

Plasser, Peter & Widmer (2023, IJCAI-23) implemented this as **SCHmUBERT** (Symbolic Creative Hierarchic music Unmasking Bidirectional Encoder Representation Transformer), a bidirectional transformer encoder that predicts clean tokens from corrupted ones. The model achieves state-of-the-art results on symbolic music generation metrics and supports flexible note-level infilling and post-hoc classifier guidance.

---

## Mathematical Foundation

### Forward Process (Corruption)

Define a discrete sequence $x_0 = (x_0^{(1)}, \ldots, x_0^{(D)})$ where each $x_0^{(i)} \in \{1, 2, \ldots, K\}$ is a token from a vocabulary of $K$ categories. The forward Markov process applies a transition matrix $Q_t \in \mathbb{R}^{K \times K}$ at each timestep $t = 1, \ldots, T$:

$$q(x_t \mid x_{t-1}) = \mathrm{Cat}(x_t; \mathbf{p} = x_{t-1} Q_t)$$

where $x_{t-1}$ is treated as a one-hot row vector. The cumulative transition matrix after $t$ steps is:

$$\overline{Q}_t = Q_1 Q_2 \cdots Q_t$$

giving the closed-form marginal:

$$q(x_t \mid x_0) = \mathrm{Cat}(x_t; \mathbf{p} = x_0 \overline{Q}_t)$$

Three transition-matrix designs are available:

**1. Uniform diffusion** — transitions with equal probability to any state:

$$[Q_t]_{ij} = (1-\beta_t)\mathbf{1}_{i=j} + \beta_t/K$$

The stationary distribution is uniform over all $K$ categories.

**2. Absorbing-state diffusion** — each token transitions to a special [MASK] state $\mathbf{m}$ with probability $\beta_t$:

$$[Q_t]_{ij} = (1-\beta_t)\mathbf{1}_{i=j \neq m} + \beta_t\mathbf{1}_{j=m} + \mathbf{1}_{i=j=m}$$

Tokens at the [MASK] state remain there forever. This establishes a formal connection to BERT-style masked language models: at high noise levels the sequence is fully masked, and generation proceeds by progressive unmasking.

**3. Discretized Gaussian** — transition probabilities decay with ordinal distance $|i-j|$:

$$[Q_t]_{ij} \propto \exp\left(-\frac{(i-j)^2}{2\sigma_t^2}\right) \quad \text{normalized over } j$$

Mimics continuous Gaussian diffusion on discrete ordinal data (e.g., MIDI pitch numbers, velocity bins).

### Reverse Process (Denoising)

The reverse process learns $p_\theta(x_{t-1} \mid x_t)$ by predicting a "clean" estimate $\tilde{x}_0$:

$$p_\theta(x_{t-1} \mid x_t) \propto \sum_{\tilde{x}_0} q(x_{t-1} \mid x_t, \tilde{x}_0) \cdot \tilde{p}_\theta(\tilde{x}_0 \mid x_t)$$

The posterior $q(x_{t-1} \mid x_t, \tilde{x}_0)$ is computed analytically from the forward process:

$$q(x_{t-1} \mid x_t, \tilde{x}_0) = \frac{q(x_t \mid x_{t-1}, \tilde{x}_0)\, q(x_{t-1} \mid \tilde{x}_0)}{q(x_t \mid \tilde{x}_0)}$$

### Training Objective

Loss combines the variational lower bound (VLB) with an auxiliary cross-entropy loss:

$$\mathcal{L} = \mathcal{L}_{\mathrm{VLB}} + \lambda \mathcal{L}_{\mathrm{CE}}$$

where $\mathcal{L}_{\mathrm{VLB}}$ is the negative ELBO:

$$\mathcal{L}_{\mathrm{VLB}} = \mathbb{E}_{q(x_0)} \left[ D_{\mathrm{KL}}(q(x_T \mid x_0) \parallel p(x_T)) + \sum_{t=2}^T \mathbb{E}_{q(x_t \mid x_0)} \left[ D_{\mathrm{KL}}(q(x_{t-1} \mid x_t, x_0) \parallel p_\theta(x_{t-1} \mid x_t)) \right] - \mathbb{E}_{q(x_1 \mid x_0)} \left[ \log p_\theta(x_0 \mid x_1) \right] \right]$$

and $\mathcal{L}_{\mathrm{CE}}$ is a reweighted cross-entropy on the $x_0$ prediction, focusing on early timesteps to stabilise training.

### Classifier Guidance

A separately trained classifier $p_\phi(c \mid x_t)$ guides the reverse process post-hoc without retraining:

$$\tilde{p}_\theta(x_{t-1} \mid x_t, c) \propto p_\theta(x_{t-1} \mid x_t) \cdot p_\phi(c \mid x_{t-1})^\gamma$$

where $\gamma \geq 0$ is the guidance strength. This enables control over note density, genre, or register at generation time.

---

## Token Representation (SCHmUBERT)

Plasser et al. (2023) encode notes as 4-tuples $\langle \mathrm{pitch}, \mathrm{duration}, \mathrm{velocity}, \mathrm{instrument} \rangle$ arranged in a rectangular grid over time:

| Token field | Categories |
|-------------|------------|
| Pitch | 0–127 (MIDI) + rest + [MASK] |
| Duration | whole, half, quarter, eighth, sixteenth, dotted/triplet variants + [MASK] |
| Velocity | 1–127 (folded into 16 bins) + [MASK] |
| Instrument | 0–127 (GM program) + [MASK] |

The 16-bar context window with 16th-note resolution yields up to 1024 time positions. The bidirectional transformer encoder (12 layers, 8 heads, d_model=512) processes the full grid. The absorbing state is used as the [MASK] token.

---

## Algorithm

### Training

```
Input: corpus of symbolic music token sequences x_0^(1:D)
for each batch:
  sample t ~ Uniform(1, T)
  sample x_t ~ q(x_t | x_0) via cumulative transition matrix
  compute loss: L = L_VLB + λ * L_CE
  update θ via gradient descent
```

### Unconditional Generation

```
Input: trained model p_θ, step count T, token count D
Initialize: x_T ~ Uniform(K)        # uniform diffusion
        or: x_T = [MASK]^D          # absorbing diffusion
for t = T down to 1:
  predict p_θ(x_{t-1} | x_t)
  sample x_{t-1} from predicted distribution
Output: x_0 (generated token sequence)
```

### Conditional Generation / Infilling

```
Input: partially observed sequence x_obs at known positions M
Initialize: x_T = x_obs at M, else [MASK] or uniform
for t = T down to 1:
  predict p_θ(x_{t-1} | x_t)
  sample x_{t-1}
  clamp: x_{t-1}[M] = x_obs[M]   # keep observed tokens fixed
Output: x_0 (infilled sequence)
```

---

## Python Implementation Sketch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class D3PMComposer:
    """
    Discrete Denoising Diffusion Probabilistic Model for symbolic music.
    Implements absorbing-state D3PM (Austin et al. 2021; Plasser et al. 2023).
    """
    
    def __init__(self, vocab_size, mask_token_id, T=256, beta_schedule='cosine'):
        self.vocab_size = vocab_size
        self.mask_id = mask_token_id
        self.T = T
        self.betas = self._cosine_beta_schedule(T) if beta_schedule == 'cosine' \
                     else self._linear_beta_schedule(T)
        
        # Precompute transition matrices Q_t and cumulative Q̄_t
        self.Q_bar = self._compute_cumulative_transitions()
    
    def _cosine_beta_schedule(self, T, s=0.008):
        steps = torch.arange(T + 1, dtype=torch.float32)
        f_t = torch.cos((steps / T + s) / (1 + s) * torch.pi / 2) ** 2
        alpha_bar_t = f_t / f_t[0]
        beta_t = 1 - alpha_bar_t[1:] / alpha_bar_t[:-1]
        return torch.clamp(beta_t, 0.0, 0.999)
    
    def _compute_cumulative_transitions(self):
        """Q̄_t for absorbing-state diffusion."""
        # Absorbing: at each step, a token stays with prob (1-β_t),
        # or transitions to [MASK] with prob β_t. [MASK] stays.
        Q_bar = []
        log_alpha_cum = torch.zeros(self.T + 1)
        for t in range(self.T):
            log_alpha_cum[t+1] = log_alpha_cum[t] + torch.log(1 - self.betas[t])
        for t in range(self.T + 1):
            Q_bar_t = torch.zeros(self.vocab_size, self.vocab_size)
            # Diagonal: probability of surviving (not masked)
            survival = torch.exp(log_alpha_cum[t])
            Q_bar_t.fill_((1 - survival) / (self.vocab_size - 1))
            Q_bar_t[range(self.vocab_size), range(self.vocab_size)] = survival
            # Mask row: mask stays mask
            Q_bar_t[self.mask_id] = 0
            Q_bar_t[self.mask_id, self.mask_id] = 1.0
            Q_bar.append(Q_bar_t)
        return torch.stack(Q_bar)
    
    def forward_corrupt(self, x_0, t):
        """Corrupt clean tokens to timestep t: sample x_t ~ q(x_t | x_0)."""
        assert t.ndim == 1  # per-batch timestep
        x_0_onehot = F.one_hot(x_0, num_classes=self.vocab_size).float()
        logits = x_0_onehot @ self.Q_bar[t].T  # [B, D, K]
        x_t = torch.distributions.Categorical(logits=logits).sample()
        return x_t
    
    def denoise_step(self, model, x_t, t):
        """
        Single reverse step: predict p_θ(x_{t-1} | x_t).
        model(x_t, t) -> predicted clean logits for each position.
        """
        clean_logits = model(x_t, t)  # [B, D, K]
        if t > 1:
            # Compute q(x_{t-1} | x_t, x̂_0) posterior
            t_tensor = torch.full((x_t.shape[0],), t, dtype=torch.long)
            x_t_onehot = F.one_hot(x_t, num_classes=self.vocab_size).float()
            
            # Posterior logits = log Q_{t-1} + log Q̄_t^{-1} + clean_logits
            # Simplified: use the D3PM posterior formula
            log_posterior = self._posterior_logits(clean_logits, x_t_onehot, t_tensor)
            x_t_minus_1 = torch.distributions.Categorical(logits=log_posterior).sample()
        else:
            # t=1: directly predict x_0 from x_1
            x_t_minus_1 = torch.argmax(clean_logits, dim=-1)
        return x_t_minus_1
    
    def generate(self, model, D, device='cpu'):
        """Unconditional generation."""
        x = torch.full((1, D), self.mask_id, dtype=torch.long, device=device)
        for t in range(self.T, 0, -1):
            t_tensor = torch.full((1,), t, dtype=torch.long, device=device)
            x = self.denoise_step(model, x, t)
        return x.squeeze(0)
    
    def infill(self, model, x_obs, mask_positions, device='cpu'):
        """
        Conditional infilling: generate tokens at masked positions,
        keep observed tokens fixed.
        """
        D = x_obs.shape[0]
        x = torch.full((1, D), self.mask_id, dtype=torch.long, device=device)
        x[0, ~mask_positions] = x_obs[~mask_positions]  # clamp observed
        for t in range(self.T, 0, -1):
            t_tensor = torch.full((1,), t, dtype=torch.long, device=device)
            x_pred = self.denoise_step(model, x, t)
            # Clamp: only update masked positions
            x = torch.where(mask_positions.unsqueeze(0), x_pred, x)
            # Re-clamp observed
            x[0, ~mask_positions] = x_obs[~mask_positions]
        return x.squeeze(0)
```

---

## Relationship to Existing Methods

| Method | Domain | Mechanism | Generation | This differs by |
|--------|--------|-----------|------------|-----------------|
| 047 DSMG | Continuous | Gaussian score-based | Denoising piano-roll latents | **Discrete token space** rather than continuous parameters |
| 101 FMC | Embedding | ODE vector-field flow | Deterministic ODE integration | **Markov transition matrix corruption** rather than flow ODE |
| 106 NAPC | Discrete token | Confidence-based unmasking | Iterative mask-predict | **Scheduled probabilistic corruption** rather than deterministic confidence ranking |
| 054 ATS | Discrete token | Autoregressive causal attention | Token-by-token left-to-right | **Parallel non-autoregressive generation** with bidirectional context |
| 060 S4SC | Embedding/token | Continuous state-space recurrence | Sequential linear-time | **Discrete categorical diffusion** rather than continuous state spaces |

D3PM-C fills the discrete-diffusion niche: a principled probabilistic generative framework for discrete symbolic music tokens with a proper information-theoretic objective (ELBO), scheduled corruption analogous to physical annealing, and post-hoc classifier guidance — all in the discrete domain without continuous approximations.

---

## References

- Austin, J., Johnson, D. D., Ho, J., Tarlow, D. & van den Berg, R. (2021). "Structured Denoising Diffusion Models in Discrete State-Spaces." *Advances in Neural Information Processing Systems* 34 (NeurIPS 2021). arXiv:2107.03006.

- Plasser, M., Peter, S. & Widmer, G. (2023). "Discrete Diffusion Probabilistic Models for Symbolic Music Generation." *Proceedings of the 32nd International Joint Conference on Artificial Intelligence (IJCAI-23)*, Macau, China. arXiv:2305.09489.

- Mittal, G., Engel, J., Hawthorne, C. & Simon, I. (2021). "Symbolic music generation with diffusion models." *International Society for Music Information Retrieval (ISMIR 2021)*. — The reference continuous-diffusion model for symbolic music (applied to continuous VAE latents, not discrete tokens).

- Hoogeboom, E., Gritsenko, D., Salimans, T. & Cohen, T. (2021). "Argmax Flows and Multinomial Diffusion." *NeurIPS 2021*.

- Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N. & Ganguli, S. (2015). "Deep Unsupervised Learning using Nonequilibrium Thermodynamics." *ICML 2015*.