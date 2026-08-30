# Method 072 — Normalizing Flow Composition (NFC)

**Paradigm**: AI-Driven (Deep Generative)
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Classification**: Tonal Gravity = Strong (Condition/Invertible-prior) · Metric Binding = Grid-Locked / Continuous · Memory Depth = Macro / Latent Trajectory · Time Complexity = $\mathcal{O}(K \cdot d)$ per pass, $\mathcal{O}(E \cdot B \cdot K \cdot d)$ training

---

## One-line description

Trains an **invertible, exact-likelihood normalizing flow** $x = f_\theta(z)$ that maps a Gaussian latent space onto the density of symbolic music, then composes by pushing sampled points — or *walking a curated path through the invertible latent space* — through the forward map.

## Why this is novel (not a duplicate)

046 VAE is *variational* (ELBO bound, not exact likelihood, not invertible); 047 DSMG is a *stochastic* denoising process (the reverse of a diffusion is a flow only in the noiseless limit); 054 ATS is *autoregressive* (no latent, no invertibility). NFC is the only method in the DB that gives **exact likelihood**, a **trainable, invertible, two-way map**, and an **inspectable latent topology** where *every piece (real or generated) has a unique latent coordinate*. That invertibility is what turns composition into *path-walking on a learned musical manifold* — a mechanism none of 001–071 offers.

---

## Extended mathematics

### 1. Change of variables (the core identity)

A flow is a chain of $K$ bijective, differentiable layers

$$z_0 \sim p_0(z_0), \qquad z_k = f_k(z_{k-1}), \qquad x = f_K \circ \cdots \circ f_1(z_0) = f_\theta(z_0).$$

Because $f_\theta$ is a diffeomorphism, the density of $x$ is given exactly by the change-of-variables formula:

$$p_X(x) = p_0\big(f_\theta^{-1}(x)\big)\left|\det \frac{\partial f_\theta^{-1}}{\partial x}\right| = p_0(z_0)\prod_{k=1}^{K}\left|\det \frac{\partial f_k}{\partial z_{k-1}}\right|^{-1}.$$

Training maximizes $\log p_X(x)$ directly (no ELBO, no adversarial objective, no score matching). This is the *only* generative family in the DB with exact likelihood.

### 2. Affine coupling layer (tractable Jacobian)

The dense Jacobian of a general bijective layer costs $\mathcal{O}(d^3)$ to determinant. Real-NVP avoids this with a **triangular** structure. Split $z = (z_a, z_b)$; keep $z_a$ fixed, transform $z_b$ affinely with parameters produced by an *arbitrary* (uninverted) network of the fixed half:

$$y_a = z_a, \qquad y_b = z_b \odot \exp\big(s(z_a; c)\big) + t(z_a; c), \qquad \log\left|\det \frac{\partial y}{\partial z}\right| = \sum_i s_i(z_a; c).$$

The inverse is explicit (subtract then divide), so **one layer serves as both generator and encoder**. Glow adds invertible $1\times1$ convolutions

$$\det W = \det\!\big(PLU\big) = \sum_i \log|s_{ii}|$$

and activation normalization to mix dimensions and stabilize scale.

### 3. Latent geometry and the pullback metric

Because $f_\theta^{-1}$ is exact, every piece has a unique latent coordinate. Interpolation is meaningful **only** in latent space — data-space interpolation of piano rolls is a meaningless mixture, but the flow guarantees the entire latent path lies on the learned musical manifold. The manifold's geometry is the **pullback metric**

$$G(z) = J_f(z)^\top J_f(z), \qquad J_f = \frac{\partial f_\theta}{\partial z},$$

whose geodesics are the natural (manifold-respecting) interpolation paths — preferable to linear interpolation, which can cross low-density off-manifold regions.

### 4. Latent trajectory = macro-form

Let $\{z_1, \dots, z_S\}$ be section waypoints (function centroids) and $\{c_1, \dots, c_S\}$ the conditioning (chord-function) sequence. The piece is the curve

$$z(t) = \operatorname{path}\big(t;\, z_1, \dots, z_S\big), \qquad t \in [0, 1],$$

decoded at bar resolution $x_{\text{bar}} = f_\theta\big(z(t_{\text{bar}}); c_{s(t)}\big)$:

- linear path $\Rightarrow$ section blend (046 VAE-LSI behavior),
- spline through function centroids $\Rightarrow$ functional form (HOME→LIFT→TENSE→TURN),
- closed loop $z(t{+}T)=z(t)$ $\Rightarrow$ rondo/recapitulation.

### 5. Exact likelihood as tension

$\log p_X(x)$ is computable exactly for any generated bar, so it doubles as a **tension/fitness score**: idiomatic material sits at high density, surprising/unusual material at low density. A tension arc is drawn by scheduling the trajectory through low-density (TENSE) then high-density (HOME) regions.

### 6. Conditioning and a structured prior

Chord labels $c$ are concatenated to each coupling layer's conditioning network, giving the conditional density $p(x \mid c)$. A **Gaussian-mixture prior** with one component per harmonic function,

$$p_0(z) = \sum_{m \in \{\text{HOME},\text{LIFT},\text{TENSE},\text{TURN}\}} \pi_m \,\mathcal{N}(z; \mu_m, \Sigma_m),$$

places each harmonic function as a distinct latent basin — section function becomes a property of *where in latent space the waypoint sits*.

---

## Python implementation sketch

```python
from __future__ import annotations
import torch, torch.nn as nn

class AffineCoupling(nn.Module):
    """Real-NVP affine coupling layer with conditioning vector c."""
    def __init__(self, d: int, hid: int, cond_dim: int = 0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d // 2 + cond_dim, hid), nn.ReLU(),
            nn.Linear(hid, hid), nn.ReLU(),
            nn.Linear(hid, d),
        )
    def forward(self, x, c=None, reverse=False):
        xa, xb = x.chunk(2, dim=-1)
        h = torch.cat([xa, c], dim=-1) if c is not None else xa
        out = self.net(h)
        log_s, t = out.chunk(2, dim=-1)
        log_s = torch.tanh(log_s)          # clamp for stability
        if not reverse:
            yb = xb * log_s.exp() + t
            return torch.cat([xa, yb], -1), log_s.sum(-1)
        xb_ = (xb - t) * (-log_s).exp()
        return torch.cat([xa, xb_], -1), (-log_s).sum(-1)

class Flow(nn.Module):
    def __init__(self, d, K=8, hid=256, cond_dim=0):
        super().__init__()
        self.layers = nn.ModuleList([AffineCoupling(d, hid, cond_dim) for _ in range(K)])
    def _run(self, x, c, reverse):
        logdet = torch.zeros(x.shape[0], device=x.device)
        for layer in self.layers:
            x, ld = layer(x, c, reverse=reverse)
            logdet += ld
        return x, logdet
    def log_prob(self, x, c=None):
        z, logdet = self._run(x, c, reverse=True)
        prior = -0.5 * (z * z).sum(-1) - 0.5 * z.shape[-1] * torch.log(torch.tensor(2 * torch.pi))
        return prior + logdet
    def sample_latent(self, z, c=None):
        x, _ = self._run(z, c, reverse=False)
        return x

# musicom integration (conceptual — engine authors the MIDI):
#   model = Flow(d=V*(n_pitch+n_onset+n_vel), K=8, cond_dim=n_chord)
#   for each section: walk latent path z(t) at bar resolution, decode, quantize,
#   then composer.fill_voice_section(...) per voice, validate zero-drift, to_midi.
```

---

## UnitMatrix integration (summary)

| Dimension | Mechanism |
|---|---|
| Rows (Voices) | Per-voice output blocks decoded from a shared latent; multi-head coupling = lead/bass/pad separation; block-diagonal Jacobian = independent lines |
| Columns (Sections) | Latent waypoint $z_s$ + condition $c_s$ per section; interpolated path = smooth section join |
| Cells $U_{v,s}$ | `{PITCH}` decoded pitch block → scale/MIDI; `{RHYTHM}` onset/offset block → ticks; `{HARMONY}` condition $c_s$ + prior component; `{TEXTURE}` active-unit count + local Jacobian density |

---

## References

- Tabak, E. G., & Vanden-Eijnden, E. (2010). "Density estimation by dual ascent of the log-likelihood." *Comm. Math. Sci.* 8(1), 217–233.
- Tabak, E. G., & Turner, C. V. (2013). "A family of nonparametric density estimation algorithms." *Comm. Pure Appl. Math.* 66(2), 145–164.
- Rezende, D. J., & Mohamed, S. (2015). "Variational inference with normalizing flows." *ICML* 37, 1530–1538.
- Dinh, L., Krueger, D., & Bengio, Y. (2015). "NICE: Non-linear Independent Components Estimation." *ICLR Workshop*.
- Dinh, L., Sohl-Dickstein, J., & Bengio, S. (2017). "Density estimation using Real NVP." *ICLR*.
- Kingma, D. P., & Dhariwal, P. (2018). "Glow: Generative flow with invertible 1×1 convolutions." *NeurIPS* 31.
- Papamakarios, G., Nalisnick, E., Rezende, D. J., Mohamed, S., & Lakshminarayanan, B. (2021). "Normalizing flows for probabilistic modeling and inference." *JMLR* 22(57), 1–64.
- Todd, P. M. (1989). "A Connectionist Approach to Algorithmic Composition." *Computer Music Journal* 13(4), 27–43.
