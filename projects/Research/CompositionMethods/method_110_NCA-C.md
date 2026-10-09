# Neural Cellular Automata Composition (NCA-C) — Method 110

**Paradigm:** AI-Driven
**Layer:** concrete

## Overview

NCA-C uses a 2D grid of continuous-state cells (rows = voices, columns = time slots), where every cell shares a small neural network (CNN) as its local update rule. The network is trained end-to-end via backpropagation through time (BPTT) to generate coherent musical structure from a seed. Unlike classical CA (hand-crafted rules) or chaotic CML (coupled logistic maps), NCA-C learns its local interactions from data — discovering *how* musical patterns should propagate across voices and time.

## Core Algorithm

### Grid Definition

Let the grid have dimensions $V \times T$:
- $V$ = number of UnitMatrix voices (rows)
- $T$ = number of time slots (columns)

Each cell $s_{i,j}^{(t)} \in \mathbb{R}^C$ is a continuous state vector with $C$ channels (typically $C=12$–$16$). The grid is initialized from a seed: one or a few cells at $(0,0)$ set to a learned seed vector $s_{\text{seed}}$, all others zero.

### Update Rule

At each discrete timestep $t$, every cell computes:

$$s_{i,j}^{(t+1)} = s_{i,j}^{(t)} + m_{i,j}^{(t)} \cdot f_\theta(\mathcal{P}(s_{i,j}^{(t)}))$$

where:
- $\mathcal{P}(s_{i,j})$ is the **perception vector**: the 3×3 neighborhood of $s_{i,j}$, flattened and concatenated with two gradient channels ($\partial s/\partial x$, $\partial s/\partial y$) computed via Sobel-like fixed filters. Dimension = $9C + 2C = 11C$.
- $f_\theta$ is a small neural network: $11C \to 128 \to \text{ReLU} \to 128 \to \text{ReLU} \to C$ (or a 3×3 CNN with 1–2 hidden layers).
- $m_{i,j}^{(t)} \in \{0,1\}$ is a stochastic mask (Bernoulli($p=0.5$)) implementing asynchronous cell updates.

The perception function can be written explicitly:

$$\mathcal{P}(s_{i,j}) = \left[ s_{i-1,j-1}, s_{i-1,j}, s_{i-1,j+1}, s_{i,j-1}, s_{i,j}, s_{i,j+1}, s_{i+1,j-1}, s_{i+1,j}, s_{i+1,j+1}, \nabla_x s_{i,j}, \nabla_y s_{i,j} \right]$$

where $\nabla_x s_{i,j} = s_{i,j+1} - s_{i,j-1}$ and $\nabla_y s_{i,j} = s_{i+1,j} - s_{i-1,j}$ (or Sobel kernel variants).

### Decoding

After $K$ timesteps (typically 128–512), the final state $s^{(K)}$ is decoded per cell via a learned readout function $D_\phi$:

$$D_\phi(s_{i,j}^{(K)}) = (\text{pitch}_{i,j}, \text{duration}_{i,j}, \text{velocity}_{i,j}, \text{active}_{i,j})$$

- **pitch**: softmax over $12$ pitch classes + octave offset (linear)
- **duration**: sigmoid-scaled to tick range
- **velocity**: sigmoid → $[0, 127]$
- **active**: sigmoid → onset probability (threshold at 0.5 gates the note)

### Training Objective

$$\mathcal{L} = \underbrace{\mathbb{E}_{(x,y)\sim\mathcal{D}} \big[ \text{CE}(D(s^{(K)}), y) \big]}_{\text{supervised reconstruction}} + \lambda_1 \|s^{(K)}\|_2^2 + \lambda_2 \|\theta\|_2^2$$

where $\mathcal{D}$ is a dataset of paired (seed, target-music) examples, and CE is cross-entropy for pitch + MSE for duration/velocity. The gradients flow backward through all $K$ timesteps and through $f_\theta$, enabling discovery of local update rules that produce globally coherent output.

### Python Implementation Sketch

```python
import torch
import torch.nn as nn

class NCAUpdateRule(nn.Module):
    """Shared local CNN update rule for all cells."""
    def __init__(self, n_channels: int = 16, hidden: int = 128):
        super().__init__()
        # Perception: 3x3 neighborhood * n_channels + 2*C gradients = 11*C
        self.net = nn.Sequential(
            nn.Linear(11 * n_channels, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_channels),
        )
        # Zero-initialize final layer so initial updates are near-zero
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, perception: torch.Tensor) -> torch.Tensor:
        return self.net(perception)  # shape: (V, T, C)

class NCAStateDecoder(nn.Module):
    """Per-cell readout from state vector to musical parameters."""
    def __init__(self, n_channels: int, n_pitch_classes: int = 12):
        super().__init__()
        self.pitch_head = nn.Linear(n_channels, n_pitch_classes)   # softmax over PC
        self.octave_head = nn.Linear(n_channels, 1)                # octave offset
        self.dur_head = nn.Linear(n_channels, 1)                   # duration (ticks)
        self.vel_head = nn.Linear(n_channels, 1)                   # velocity
        self.active_head = nn.Linear(n_channels, 1)                # onset gate

    def forward(self, state: torch.Tensor):
        # state shape: (V, T, C)
        pitch_logits = self.pitch_head(state)       # (V, T, 12)
        octave = self.octave_head(state).sigmoid() * 8  # 0-8 octaves
        duration = self.dur_head(state).sigmoid() * 1920  # up to 1 bar
        velocity = self.vel_head(state).sigmoid() * 127
        active = self.active_head(state).sigmoid()
        return pitch_logits, octave, duration, velocity, active

class NCAComposer(nn.Module):
    """Full NCA composition model."""
    def __init__(self, n_voices: int, n_time: int, n_channels: int = 16):
        super().__init__()
        self.n_voices = n_voices
        self.n_time = n_time
        self.n_channels = n_channels
        self.seed = nn.Parameter(torch.randn(1, 1, n_channels) * 0.01)  # seed state
        self.update_rule = NCAUpdateRule(n_channels)
        self.decoder = NCAStateDecoder(n_channels)

    def sobel_gradients(self, state: torch.Tensor) -> torch.Tensor:
        """Compute spatial gradients (Sobel-like)."""
        dx = torch.zeros_like(state)
        dy = torch.zeros_like(state)
        dx[:, :, 1:-1, :] = state[:, :, 2:, :] - state[:, :, :-2, :]
        dy[:, 1:-1, :, :] = state[:, 2:, :, :] - state[:, :-2, :, :]
        return dx, dy

    def perceive(self, state: torch.Tensor) -> torch.Tensor:
        """Gather 3x3 neighborhood + gradients for each cell."""
        # state shape: (1, V, T, C)
        # Pad for boundary handling
        padded = torch.nn.functional.pad(state, (0, 0, 1, 1, 1, 1), mode='replicate')
        # (1, V+2, T+2, C)
        dx, dy = self.sobel_gradients(state)  # (1, V, T, C)
        patches = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                patches.append(padded[:, 1+di:self.n_voices+1+di, 1+dj:self.n_time+1+dj, :])
        # stack: (1, V, T, 9C)
        perception = torch.cat(patches + [dx, dy], dim=-1)
        return perception  # (1, V, T, 9C + 2C = 11C)

    def forward(self, n_steps: int = 128, p_update: float = 0.5):
        """Run NCA for n_steps, return decoded music."""
        # Initialize grid
        state = torch.zeros(1, self.n_voices, self.n_time, self.n_channels)
        state[:, 0, 0, :] = self.seed  # seed at (0, 0)

        for _ in range(n_steps):
            mask = (torch.rand(1, self.n_voices, self.n_time, 1) < p_update).float()
            perception = self.perceive(state)  # (1, V, T, 11C)
            delta = self.update_rule(perception)  # (1, V, T, C)
            state = state + mask * delta

        pitch_logits, octave, duration, velocity, active = self.decoder(state)
        return pitch_logits, octave, duration, velocity, active

    def compose(self, seed_override=None, n_steps=128, active_threshold=0.5):
        """Generate a UnitMatrix-compatible composition."""
        pitch_logits, octave, duration, velocity, active = self.forward(n_steps)
        pitch_class = pitch_logits.argmax(dim=-1)           # (V, T)
        octave_val = octave.squeeze(-1).round().int()       # (V, T)
        midi_pitch = pitch_class + octave_val * 12 + 24     # (V, T)
        note_active = (active.squeeze(-1) > active_threshold).cpu().numpy()
        duration_ticks = (duration.squeeze(-1) * 1920).cpu().numpy()
        velocity_vals = velocity.squeeze(-1).cpu().numpy()
        return midi_pitch, note_active, duration_ticks, velocity_vals
```

## Musical Elements Framework

- **PITCH**: Encoded via softmax over 12 pitch classes per cell. The 3×3 perception field means pitch at (voice $i$, time $j$) is influenced by neighbors at ($i\pm1$, $j$) — harmonic context — and ($i$, $j\pm1$) — melodic context. Stepwise motion and interval preferences emerge from training data.
- **RHYTHM**: Active-channel threshold gates note onsets. The stochastic update mask forces the NCA to maintain patterns regardless of update schedule → robust rhythm. Rhythmic density controlled by per-section threshold modulation.
- **HARMONY**: Vertical coupling in the 3×3 perception field (adjacent voice rows at same column) teaches chord voicings. The NCA learns statistically consonant interval distributions from training data.
- **STRUCTURE**: Section conditioning via extra state channels (section-ID one-hot) or separate seed per section. Form propagates through the grid via the shared update rule as a morphogen gradient.
- **TEXTURE**: Degree of cross-voice coupling controls homophony vs. polyphony. Train on independent voices → weak coupling; train on chorales → strong coupling.

## UnitMatrix Integration

- **Voices** = grid rows $0 \ldots V-1$. Each row is decoded to a voice's MusicUnit sequence.
- **Sections** = column ranges. Section condition via input channels or per-section seed.
- **Cells** = individual grid positions $(i,j)$, decoded to MusicEvent (pitch, duration, velocity) after $K$ timesteps.

## Pitfalls

1. **BPTT instability** — gradients vanish/explode through $K\ge128$ steps. Use gradient clipping and truncated BPTT.
2. **Propagation speed** — information travels at 1 col/timestep via 3×3 perception. For $T=512$, need $K\ge512$.
3. **Fixed voice count** — cannot add voices after training without retraining.
4. **Grid quantization** — uniform time columns lose micro-timing expression.
5. **Determinism** — fixed seed + mask = identical output. Inject noise for diversity.
6. **Computational cost** — memory scales as $\mathcal{O}(K \cdot V \cdot T \cdot C)$. Use gradient checkpointing.

## References

- Mordvintsev, A., Randazzo, E., Niklasson, E. & Levin, M. (2020). "Growing Neural Cellular Automata." *Distill*. doi:10.23915/distill.00023
- Delarosa, O. (2021). "Growing MIDI Music Files Using Convolutional Cellular Automata." *ICMLC 2021 Workshop*.
- Spitznagel, M. & Keuper, J. (2026). "Review and Reference Implementation of Neural Cellular Automata." *TMLR*.
- Mordvintsev, A. & Niklasson, E. (2021). "Differentiable Logic Cellular Automata." *Google Research*.
- Variengien, A. & Glanois, C. (2024). "Illuminating Diverse Neural Cellular Automata for Level Generation." *GECCO 2022*.