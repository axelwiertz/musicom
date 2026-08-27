# Method 062 — Reinforcement Learning Policy Optimization Composition (RLPOC)

**Paradigm:** AI-Driven (Deep Generative)
**Classification:** Tonal Gravity: Strong (Reward-guided) · Metric Binding: Grid-Locked / Continuous · Memory Depth: Macro / Rollout Horizon · Time Complexity: $\mathcal{O}(E \cdot T \cdot N)$ training, $\mathcal{O}(T \cdot N)$ inference

## One-line summary
Treats composition as a sequential decision process: an autoregressive policy (RNN/transformer) pre-trained by maximum likelihood is fine-tuned with policy-gradient RL (PPO + KL-control) to maximize an explicit, tunable musical reward vector (tonal gravity, groove, counterpoint, texture density, structure), with a KL penalty to the prior preventing reward hacking.

## Extended math

### The RL formulation of composition
State $s_t$ = partial UnitMatrix (all tokens emitted so far). Action $a_t$ = next musical token (note-on/note-off, pitch, velocity, time-shift, section-id). Policy $\pi_\theta(a_t \mid s_t)$ = autoregressive model. Trajectory $\tau = (s_0, a_0, a_1, \dots, a_T)$ = full piece.

### Fine-tuning objective (KL-control / RLHF)
$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\big[R(\tau)\big] - \beta \sum_t \mathrm{KL}\big(\pi_\theta(\cdot \mid s_t) \,\|\, \pi_{prior}(\cdot \mid s_t)\big)
$$

- $R(\tau)$: sequence-level reward.
- $\pi_{prior}$: the MLE pre-trained policy (frozen).
- $\beta$: KL coefficient — trades objective satisfaction against staying idiomatic (musicality).

### Reward decomposition (the compositional steering wheel)
$$
R(\tau) = \sum_k w_k \, \phi_k(\tau)
$$

| $k$ | $\phi_k$ | Musical dimension | Typical form |
|---|---|---|---|
| 1 | Tonal gravity | PITCH / HARMONY | +1 chord tone at stress point, −1 non-scale tone; passing tones free between stress points |
| 2 | Groove | RHYTHM | +metric weight on-grid, −0.5·distance off-grid |
| 3 | Counterpoint | TEXTURE | −unison/parallel collapse between voices |
| 4 | Texture density | TEXTURE | ± deviation from target note count per cell |
| 5 | Structure | STRUCTURE | +cadence at section boundary, −abrupt section jump |

Per-section weights $w_k^{(s)}$ give each UnitMatrix column its own objective profile — the reward schedule across sections *is* the macro-form arc.

### PPO with clipped surrogate (Schulman et al. 2017)
$$
L^{CLIP}(\theta) = \mathbb{E}_t\Big[\min\big(r_t(\theta)\,\hat{A}_t,\ \mathrm{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\,\hat{A}_t\big)\Big]
$$
$$
r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{old}}(a_t \mid s_t)}
$$

- $\hat{A}_t$: Generalized Advantage Estimate (GAE) of reward-to-go.
- $\epsilon$: clip range (typically 0.2).
- $\beta$: adaptively scaled to a target KL $\delta \approx 0.01$ nats/token (Ziegler et al. 2019; RL Tuner 2025).

### Complexity
- Rollout: $\mathcal{O}(T \cdot N)$ per episode ($T$ tokens, $N$ model size).
- PPO epoch: $\mathcal{O}(E \cdot T \cdot N)$ over $E$ episodes.
- Inference (composition): single autoregressive forward pass — same cost as 054 ATS.

## Python implementation sketch

```python
import numpy as np

def tonal_gravity_reward(pitches, chord_tones, stress_mask, scale_tones):
    """phi_1: reward chord tones at stress points, scale tones elsewhere."""
    r = 0.0
    for p, chord, stress, scale in zip(pitches, chord_tones, stress_mask, scale_tones):
        if stress:
            r += 1.0 if p in chord else -1.0
        else:
            r += 0.5 if p in scale else -0.5
    return r / len(pitches)

def groove_reward(onsets, grid, metric_weights):
    """phi_2: reward onsets on strong beats, penalize off-grid."""
    r = 0.0
    for t in onsets:
        d = min(abs(t - g) for g in grid)
        if d == 0:
            r += metric_weights.get(t % grid[-1], 1.0)
        else:
            r -= 0.5 * d
    return r / max(len(onsets), 1)

def counterpoint_reward(voice_pitches):
    """phi_3: penalize unison/parallel collapse between voices."""
    V = len(voice_pitches)
    r = 0.0
    for i in range(V):
        for j in range(i + 1, V):
            unisons = sum(1 for a, b in zip(voice_pitches[i], voice_pitches[j]) if a == b)
            r -= unisons / max(len(voice_pitches[i]), 1)
    return r / max(V * (V - 1) / 2, 1)

def ppo_update(policy, prior, episodes, advantages, beta=0.01, eps=0.2):
    """One PPO epoch with KL-control toward the frozen prior (pseudocode)."""
    loss = 0.0
    for ep, adv in zip(episodes, advantages):
        logp_new = policy.log_prob(ep.actions, ep.states)
        logp_old = ep.logp_old.detach()
        ratio = (logp_new - logp_old).exp()
        clipped = ratio.clamp(1 - eps, 1 + eps)
        kl = (logp_new - prior.log_prob(ep.actions, ep.states)).mean()
        loss += -min(ratio * adv, clipped * adv).mean() + beta * kl
    loss.backward()
    return loss.item()
```

### Full pipeline
1. Pre-train $\pi_{prior}$ by MLE (teacher forcing) on a REMI-token corpus; freeze.
2. Define reward vector $\phi_k$ and per-section weights $w_k^{(s)}$.
3. Roll out episodes $\tau \sim \pi_\theta$; compute $R(\tau)$ and GAE advantages.
4. PPO update + adaptive KL penalty $\beta$; iterate until rewards plateau.
5. Sample the fine-tuned policy → decode tokens → UnitMatrix cells $U_{v,s}$.
6. Fill UnitMatrix, `composer.validate()`, export via the musicom engine.

## UnitMatrix integration
- **Rows (Voices):** per-voice output head $h_v$ over a shared policy state; counterpoint reward $\phi_3$ enforces independence. Add a head, not a model.
- **Columns (Sections):** section-id token switches reward weights $w_k^{(s)}$; policy state is *not* reset at boundaries; structure reward $\phi_5$ scores the join.
- **Cells:** `{PITCH}` = pitch tokens from head $h_v$; `{RHYTHM}` = time-shift tokens snapped to grid; `{TEXTURE}` = density steered by $\phi_4$.

## Pitfalls
1. **Reward hacking / mode collapse** — fix: keep KL penalty active, normalize rewards, early-stop on held-out musicality metric, human spot-check.
2. **Sparse-reward credit assignment** — fix: GAE + dense per-step reward terms.
3. **KL miscalibration** — fix: adaptive KL scaling (target $\delta$).
4. **Off-grid drift** — fix: snap decoded onsets to tick grid, run `composer.validate()`.
5. **Voice collapse** — fix: per-voice heads + strong $\phi_3$; verify per-voice pitch entropy.
6. **Reward-weight miscalibration** — fix: normalize each $\phi_k$ to $[0,1]$, per-section weights.
7. **Reward-model overfitting (RLHF variant)** — fix: ensemble reward models, keep KL to prior, mix hand-coded + learned rewards (MusicRL-RU).

## References
- Jaques, N., Gu, S., Bahdanau, D., Hernández-Lobato, J. M., Turner, R. E., & Eck, D. (2017). "Sequence Tutor: Conservative Fine-Tuning of Sequence Generation Models with KL-control." *ICML 2017*. arXiv:1611.02796.
- Cideron, G., et al. (2024). "MusicRL: Aligning Music Generation to Human Preferences." arXiv:2402.04229.
- Agostinelli, A., et al. (2023). "MusicLM: Generating Music From Text." arXiv:2301.11325.
- Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). "Proximal Policy Optimization Algorithms." arXiv:1707.06347.
- Williams, R. J. (1992). "Simple statistical gradient-following algorithms for connectionist reinforcement learning." *Machine Learning* 8(3–4).
- Ziegler, D. M., et al. (2019). "Fine-Tuning Language Models from Human Preferences." arXiv:1909.08593.
- OpenAI (2025). "RL Tuner: The Surprisingly Simple Recipe for RLHF."
