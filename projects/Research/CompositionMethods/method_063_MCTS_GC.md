# Monte Carlo Tree Search Guided Composition (MCTS-GC)

**Method 063** · **Paradigm: AI-Driven** · **Musicom Method Master Map**

## One-Liner
Treats composition as a sequential decision process and *plans ahead* with PUCT (Predictor Upper Confidence for Trees) tree search before committing each event: an autoregressive policy prior proposes actions, a musical value function scores rolled-out futures, and the visit-count distribution over the root's children selects the next note/time-shift/section-id. Look-ahead planning satisfies long-horizon constraints (cadence resolution, voice-leading) that greedy decoders violate.

## Classification
| Attribute | Value |
|---|---|
| Paradigm | AI-Driven |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Strong (Value-guided) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Macro / Search Horizon |
| Time Complexity | $\mathcal{O}(K \cdot L \cdot N)$ per step ($K$ iterations, $L$ rollout depth, $N$ model size) |

## Extended Math

### The PUCT selection formula
Each tree node stores four statistics: visit count $N(s,a)$, total value $Q(s,a)$, prior probability $P(s,a)$ from a policy, and a value estimate $V(s)$. Selection descends the tree by:

$$a^* = \arg\max_a \left[ \frac{Q(s,a)}{N(s,a)} + c_{puct} \, P(s,a) \, \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s,a)} \right]$$

### Backup
On reaching a leaf, the value $v$ of the rolled-out continuation is propagated back up the path:

$$N(s,a) \leftarrow N(s,a) + 1, \qquad Q(s,a) \leftarrow Q(s,a) + v$$

### The musical value function
The leaf value is a weighted sum of musical objectives, one per compositional dimension:

$$V(\tau) = \sum_k w_k \, \phi_k(\tau)$$

- $\phi_1$ = **tonal gravity** — chord-tone alignment at harmonic stress points (HOME/LIFT/TENSE/TURN),
- $\phi_2$ = **groove** — onset-grid alignment weighted by metric strength,
- $\phi_3$ = **counterpoint** — voice independence (penalizes unison/parallel collapse),
- $\phi_4$ = **texture** — note density per cell vs. target,
- $\phi_5$ = **structure** — cadence placement at section boundaries.

Per-section weights $w_k^{(s)}$ give each UnitMatrix column its own objective profile — the *reward schedule across sections is the macro-form arc*.

### Visit-count sampling
After $K$ iterations, the next action is sampled from the root's visit-count distribution with temperature $\tau$:

$$\pi(a \mid s_t) = \frac{N(s_t, a)^{1/\tau}}{\sum_b N(s_t, b)^{1/\tau}}$$

$\tau \to 0$ = greedy (argmax), $\tau = 1$ = proportional, $\tau \to \infty$ = uniform. Dirichlet noise $\mathrm{Dir}(\alpha)$ is added to the root prior (AlphaZero recipe) to force exploration.

## Python Implementation Sketch

```python
import math
import random
from collections import defaultdict

class MCTSNode:
    def __init__(self, state, prior=0.0):
        self.state = state
        self.prior = prior
        self.N = 0.0          # visit count
        self.W = 0.0          # total value
        self.children = {}    # action -> MCTSNode

    def value(self):
        return self.W / self.N if self.N > 0 else 0.0

    def puct(self, c_puct, sum_N):
        return self.value() + c_puct * self.prior * math.sqrt(sum_N) / (1 + self.N)

def search(root, policy, value_fn, n_iters=200, c_puct=1.0, max_depth=32):
    """Grow a PUCT tree from root; return visit-count distribution over root actions."""
    for _ in range(n_iters):
        node, path = root, []
        # SELECT
        while node.children and not node.state.is_terminal():
            sum_N = sum(c.N for c in node.children.values())
            a, node = max(node.children.items(),
                          key=lambda kv: kv[1].puct(c_puct, sum_N))
            path.append(node)
        # EXPAND + EVALUATE
        if not node.state.is_terminal():
            for a, p in policy(node.state):            # policy returns (action, prior) pairs
                node.children[a] = MCTSNode(node.state.apply(a), prior=p)
        v = value_fn(node.state.rollout(max_depth))    # weighted musical objectives
        # BACKUP
        for n in path:
            n.N += 1
            n.W += v
    return {a: c.N for a, c in root.children.items()}

def compose(policy, value_fn, state0, temperature=0.8, n_iters=200):
    """Compose the whole piece: search, sample, advance, repeat."""
    state = state0
    events = []
    while not state.is_terminal():
        root = MCTSNode(state)
        visits = search(root, policy, value_fn, n_iters=n_iters)
        # temperature visit-count sampling
        total = sum(v ** (1 / temperature) for v in visits.values())
        r = random.random() * total
        for a, v in visits.items():
            r -= v ** (1 / temperature)
            if r <= 0:
                state = state.apply(a)
                events.append(a)
                break
    return events
```

### Musical objective examples (NumPy)

```python
def tonal_gravity(pitches, chord_tones, stress_mask, scale_tones):
    r = 0.0
    for p, ch, stress, sc in zip(pitches, chord_tones, stress_mask, scale_tones):
        if stress:
            r += 1.0 if p in ch else -1.0
        else:
            r += 0.5 if p in sc else -0.5
    return r / len(pitches)

def counterpoint(voice_pitches):
    V = len(voice_pitches)
    r = 0.0
    for i in range(V):
        for j in range(i + 1, V):
            unisons = sum(1 for a, b in zip(voice_pitches[i], voice_pitches[j]) if a == b)
            r -= unisons / max(len(voice_pitches[i]), 1)
    return r / max(V * (V - 1) / 2, 1)
```

## UnitMatrix Integration
- **Rows (Voices)**: each voice $v$ is a separate action head over the shared search state (or an independent tree with a cross-voice coupling term in the value function). Counterpoint term enforces horizontal independence.
- **Columns (Sections)**: each section $s$ injects a section-id action and switches value-function weights $w_k^{(s)}$. State is *not reset* at boundaries — the tree carries prior material forward and scores the join.
- **Cells** $U_{v,s}$: `{PITCH}` (PUCT-chosen, scale-quantized), `{RHYTHM}` (time-shift actions snapped to tick grid), `{TEXTURE}` (density steered by $\phi_4$).

## Pitfalls
1. **Search cost**: full PUCT per event is expensive. Fix: amortize (search every $k$-th event), cap $K$/$L$, use hand-coded (not neural) value functions.
2. **Value-function miscalibration**: one over-weighted objective produces grid-perfect gibberish. Fix: normalize each $\phi_k$ to $[0,1]$, per-section weights.
3. **Policy-prior domination**: $c_{puct}$ too low → tree replays the prior's argmax. Fix: tune $c_{puct}$ (~1.0), Dirichlet root noise, verify search changes argmax vs. greedy.
4. **Rollout horizon truncation**: short rollouts can't see the next cadence. Fix: $L$ spans ≥ one phrase, or learned leaf value.
5. **Off-grid drift**: time-shift rounding error → validation failure. Fix: snap to tick grid, run `composer.validate()`.
6. **Voice collapse**: weak counterpoint term → identical lines. Fix: per-voice heads + strong $\phi_3$, verify per-voice pitch entropy.
7. **Temperature miscalibration**: $\tau \to 0$ frozen, $\tau \to \infty$ noisy. Fix: $\tau \approx 0.5\text{–}1.0$, log the seed.

## References
- Kocsis, L. and Szepesvári, C. (2006). "Bandit based Monte-Carlo Planning." *ECML 2006*. (UCT.)
- Ferreira, L. N., Mou, L., Whitehead, J., and Lelis, L. H. S. (2022). "Controlling Perceived Emotion in Symbolic Music Generation with Monte Carlo Tree Search." *AAAI AIIDE-22*. arXiv:2208.05162. (The canonical MCTS-for-music reference.)
- Silver, D., et al. (2016). "Mastering the game of Go with deep neural networks and tree search." *Nature* 529. (AlphaGo.)
- Silver, D., et al. (2017). "Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm." arXiv:1712.01815. (AlphaZero.)
- Coulom, R. (2006). "Efficient Selectivity and Backup Operators in Monte-Carlo Tree Search." *CG 2006*.
