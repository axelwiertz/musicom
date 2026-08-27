# Method 060 — Structured State Space Sequence Composition (S4SC)

**Paradigm:** AI-Driven (Deep Generative)
**Acronym:** S4SC
**Primary Elements:** Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity:** Variable (Selective-gate)
**Metric Binding:** Grid-Locked / Continuous
**Memory Depth:** Macro / State-Space
**Time Complexity:** $\mathcal{O}(N \cdot d \cdot d_{state})$

---

## Source

Structured State Space Sequence Composition (S4SC) is built on the Structured State Space Model (S4) and its selective successor Mamba — the linear-time sequence-modeling paradigm that emerged to replace the quadratic attention bottleneck of transformers.

Foundational line of work:
- **Gu, A., Goel, K., & Ré, C. (2022).** "Efficiently Modeling Long Sequences with Structured State Spaces." *ICLR 2022* (S4) — unified continuous-time state-space models, recurrence, and convolution under the HiPPO framework.
- **Gu, A., & Dao, T. (2023).** "Mamba: Linear-Time Sequence Modeling with Selective State Spaces." *arXiv:2312.00752* — made the state-space parameters *input-dependent* (the S6 selective mechanism) and added a hardware-aware parallel scan, matching transformer quality at linear cost.

The core object is a continuous-time linear dynamical system:

$$h'(t) = A\, h(t) + B\, x(t), \qquad y(t) = C\, h(t) + D\, x(t)$$

discretized (zero-order hold) into a recurrence $h_k = \bar{A} h_{k-1} + \bar{B} x_k$ that is both a fast linear-time recurrence and (for time-invariant parameters) a global convolution.

In the Musicom catalog, S4SC is the linear-time, long-context counterpart to **054 ATS** (autoregressive transformer): it generates symbolic music token-by-token like 054, but its state-space recurrence gives $\mathcal{O}(N)$ cost and a built-in long-range memory (HiPPO) that a transformer only approximates with quadratic attention. It is the *trained* counterpart to **059 ESN-RC** (which also uses a recurrent state, but untrained and fixed). It complements 047 diffusion / 046 VAE / 057 GAN by modeling the discrete symbolic surface directly with linear-time long-context memory.

---

## Description

S4SC generates music by treating the UnitMatrix as a discrete token sequence and processing it through a stack of structured state-space layers. Each layer maintains a latent state $h(t) \in \mathbb{R}^{N \times d_{state}}$ that evolves according to a continuous-time linear system, discretized per timestep.

Key property: **linear-time sequence modeling with long-range memory**. Unlike a transformer (attention is $\mathcal{O}(N^2)$), an SSM layer is $\mathcal{O}(N)$ because the recurrence is a first-order scan, yet the HiPPO-initialized state matrix $A$ optimally compresses unbounded input history — so a single layer carries phrase-to-form-scale context without a quadratic attention matrix.

In the **selective (Mamba/S6)** variant, the transition matrix $\bar{A}$, input projection $\bar{B}$, and output projection $C$ become *functions of the current token* $x_k$, so the model can *selectively* remember or forget. This selectivity is the musical lever — it gates which chord function, motif, or section label persists in the state across the piece.

---

## Extended Mathematics

### Continuous-time state-space layer

$$h'(t) = A\, h(t) + B\, x(t), \qquad y(t) = C\, h(t) + D\, x(t)$$

### Zero-order-hold discretization (step size $\Delta$)

$$\bar{A} = e^{\Delta A}, \qquad \bar{B} = (\Delta A)^{-1}\left(e^{\Delta A} - I\right) \Delta B$$

$$h_k = \bar{A}\, h_{k-1} + \bar{B}\, x_k, \qquad y_k = C\, h_k + D\, x_k$$

### Selective (S6) input-dependent parameters

$$\Delta_k = \text{softplus}(W_\Delta x_k + b_\Delta), \qquad B_k = W_B x_k, \qquad C_k = W_C x_k$$

### HiPPO memory

The state matrix $A$ is initialized with the HiPPO-LegS basis so the state $h_k$ is the optimal polynomial projection of the full input history $x_{0:k}$ — i.e., $h_k$ compresses unbounded context with minimal loss. Memory capacity grows with $d_{state}$ and with $\rho(\bar{A}) \to 1$.

### Parallel associative scan

Because $\bar{A}$ is diagonal (or diagonal-plus-low-rank), the recurrence $h_k = \bar{A}_k h_{k-1} + \bar{B}_k x_k$ is a first-order linear recurrence computable in $\mathcal{O}(N \log N)$ (or $\mathcal{O}(N)$ on GPU) via a parallel prefix scan — no sequential bottleneck, constant memory.

### Complexity

- Per layer: $\mathcal{O}(N \cdot d \cdot d_{state})$ — linear in sequence length $N$.
- Contrast: transformer attention $\mathcal{O}(N^2 d)$.
- Memory: constant (no growing KV cache).

---

## Musical Elements Framework

- **PITCH**: Discrete pitch tokens (REMI note-on with pitch). Output head = softmax over pitch vocabulary; sampled pitch quantized to active scale. HiPPO memory conditions predicted pitch on full melodic context → long-range motivic recall without an explicit attention window.
- **RHYTHM**: Time-shift tokens interleaved with note-on/off tokens (as in 054 ATS). The selective $\Delta$ gate forgets exact micro-timing while retaining metric phase → metric regularity with organic variation. Linear-time scan makes long rhythmic patterns (ostinati, talea) cheap.
- **HARMONY**: Chord function (HOME/LIFT/TENSE/TURN) injected as conditioning token. Selective parameters $B_k, C_k, \Delta_k$ computed from current token → a chord token *reconfigures* the recurrence to emphasize active harmonic context. HiPPO memory preserves the harmonic trajectory (progression) → pitch stays consonant with local chord, smooth voice-leading.
- **STRUCTURE**: Macro-form is the strongest asset. SSM layers process the *entire* piece in linear time with long-range memory → a late-section cadence can be conditioned on the opening theme without quadratic attention. Section-label tokens (A/B/A'/C) = hard structural switches; selective gate decides prior-section state persistence (clean contrast vs. through-composed continuity). Trained analogue of 059 ESN-RC's fading memory.
- **TEXTURE**: Multi-voice via separate token streams per voice or interleaved stream with voice-id tokens. Selective mechanism decouples voices (voice-id reconfigures $B_k, C_k$); shared state provides vertical coupling. Texture density = note-on token rate per voice per section.

---

## UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: Each voice $v$ = dedicated output head (or SSM channel) over shared state. Voice 1 (lead) = high-register head; Voice 2 (bass) = low-register; Voice 3 (pad) = chord-tone; Voice 4 (percussion) = velocity/onset head. Voice-id tokens route events to rows. Shared state = vertical coherence; per-voice heads = independent contours.
- **Columns (Sections)**: Each section $s$ delimited by section-label token $[S_s]$. Selective gate at boundaries decides prior-section state persistence. Section label conditions pitch/rhythm heads → distinct harmonic function + density profile per column.
- **Cells** $U_{v,s}$:
  - `{PITCH}`: Scale-quantized pitch tokens from voice $v$'s head within section $s$.
  - `{RHYTHM}`: Time-shift tokens within section $s$.
  - `{TEXTURE}`: Event density (note-on count per beat), learned from section label.
- **Mapping Flow**:
  1. Serialize structure → token sequence `[S_A][chord:HOME] note-on(pitch) time-shift ... [S_B][chord:LIFT] ...`.
  2. Feed through stack of SSM layers (linear-time scan maintaining $h_k$).
  3. Decode per voice (output head over pitch/velocity/time-shift); sample/argmax.
  4. Reconstruct (voice, pitch, onset, velocity) tuples.
  5. Assign to UnitMatrix cells by section boundaries; fill MusicUnits.
  6. Validate zero-drift; export via musicom engine.

---

## Python Implementation Sketch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SelectiveSSMBlock(nn.Module):
    """Minimal selective (S6/Mamba-style) state-space block."""
    def __init__(self, d_model=256, d_state=16, d_inner=512, dt_rank=16, seed=0):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.d_state = d_state
        self.d_inner = d_inner
        self.in_proj = nn.Linear(d_model, d_inner * 2, bias=False)   # x, z
        self.x_proj = nn.Linear(d_inner, dt_rank + d_state * 2, bias=False)  # dt, B, C
        self.dt_proj = nn.Linear(dt_rank, d_inner)
        A = torch.arange(1, d_state + 1, dtype=torch.float32).unsqueeze(0).repeat(d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))   # HiPPO-style diagonal A
        self.D = nn.Parameter(torch.ones(d_inner))
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)

    def _scan(self, Abar, Bbar, C, x):
        B, L, D, N = x.shape[0], x.shape[1], self.d_inner, self.d_state
        h = torch.zeros(B, D, N, device=x.device)
        ys = []
        for k in range(L):
            h = Abar[:, k] * h + Bbar[:, k] * x[:, k].unsqueeze(-1)
            ys.append((C[:, k] * h).sum(-1))
        return torch.stack(ys, dim=1)

    def forward(self, u):
        xz = self.in_proj(u)
        x, z = xz.chunk(2, dim=-1)
        x = F.silu(x)
        dtBC = self.x_proj(x)
        dt, B, C = dtBC.split([self.dt_proj.in_features, self.d_state, self.d_state], dim=-1)
        dt = F.softplus(self.dt_proj(dt))
        A = -torch.exp(self.A_log)
        Abar = torch.exp(dt.unsqueeze(-1) * A.unsqueeze(0))
        Bbar = dt.unsqueeze(-1) * B.unsqueeze(-2)
        y = self._scan(Abar, Bbar, C, x) + x * self.D
        y = y * F.silu(z)
        return self.out_proj(y)

class S4SCComposer(nn.Module):
    def __init__(self, vocab, d_model=256, n_layers=8, d_state=16):
        super().__init__()
        self.embed = nn.Embedding(vocab, d_model)
        self.layers = nn.ModuleList([SelectiveSSMBlock(d_model, d_state) for _ in range(n_layers)])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab)

    def forward(self, ids):
        x = self.embed(ids)
        for layer in self.layers:
            x = x + layer(self.norm(x))
        return self.head(self.norm(x))
```

- **Training**: Autoregressive next-token cross-entropy over a REMI-tokenized MIDI corpus. Linear-time forward/backward; associative scan parallelized on GPU (hardware-aware, as in Mamba).
- **Inference**: Token-by-token sampling (temperature/top-k) with running hidden state persisting across the whole piece.
- **Tooling**: PyTorch (or `mamba-ssm` / `causal-conv1d` CUDA kernels); `miditok`/REMI for tokenization; musicom engine for UnitMatrix fill + zero-drift MIDI export.

---

## Pitfalls

1. **Discretization blow-up**: Large $\Delta_k$ → $\bar{A} = e^{\Delta A}$ overflows / unstable state. Fix: clamp $\Delta$, keep $A$ negative, monitor state norm.
2. **HiPPO init loss**: Random (non-HiPPO) $A$ destroys long-range memory. Fix: initialize $A$ with HiPPO matrix, keep learnable but regularized.
3. **Causal-order violation**: Selective scan assumes strict left-to-right causal order. Fix: serialize UnitMatrix in temporal order, never shuffle tokens.
4. **Selective gate collapse**: Saturated gates ($\Delta \to 0$) freeze state → stuck note / repeated loop. Fix: moderate $\Delta$ init, floor on $\Delta$, dropout on gating projections.
5. **Voice bleed**: Single interleaved stream leaks one voice's state into another. Fix: explicit voice-id tokens + per-voice heads, or separate SSM channels; verify per-voice pitch independence (cf. FHNS 037 pitfall).
6. **Time-shift drift**: Autoregressive time-shift rounding accumulates → timeline drift. Fix: quantize time-shifts to tick grid, re-snap onsets to section boundaries, run `composer.validate()`.
7. **Section-boundary leakage**: Gate not closing at section label → unwanted through-composition. Fix: explicit section-reset token or learned gate driving $\Delta \to 0$ at boundaries.

---

## References

- Gu, A., Goel, K., & Ré, C. (2022). "Efficiently Modeling Long Sequences with Structured State Spaces." *ICLR 2022*.
- Gu, A., & Dao, T. (2023). "Mamba: Linear-Time Sequence Modeling with Selective State Spaces." *arXiv:2312.00752*.
- Gu, A., Johnson, I., Goel, K., Saab, K., Dao, T., Rudra, A., & Ré, C. (2021). "Combining Recurrent, Convolutional, and Continuous-time Models with Linear State Space Layers." *NeurIPS 2021*.
- Gu, A., Dao, T., Ermon, S., Rudra, A., & Ré, C. (2020). "HiPPO: Recurrent Memory with Optimal Polynomial Projections." *NeurIPS 2020*.
- Dao, T., & Gu, A. (2024). "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality." *ICML 2024*.
- Huang, C.-Z. A., et al. (2019). "Music Transformer." *ICLR 2019*. (REMI-style event-token representation.)
- Hsiao, W.-Y., Liu, J.-Y., Yeh, Y.-C., & Yang, Y.-H. (2021). "Compound Word Transformer." *AAAI 2021*.
