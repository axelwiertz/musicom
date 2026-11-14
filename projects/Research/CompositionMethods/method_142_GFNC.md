# Method 142 — Generative Flow Network Composition (GFNC)

**Layer:** concrete · **Paradigm:** AI-Driven · **Status:** verified toy prototype (`_web142/verify_142_GFNC.py`, 6/6 checks)
**Summary row added to `methods_db.md`:** yes (line 152) · **Method section appended:** lines 31349–31422 (74 lines)

---

## 1. One-line idea

Composition = **sampling a learned stochastic policy over the DAG of partial
UnitMatrix fillings**, trained by trajectory balance so that one forward pass
terminates at a complete piece drawn from the **reward-proportional
distribution** $P_T(x) \propto R(x)$ — a whole coherent *variation set* of a
form, not one optimized optimum, with no MCMC, no search tree, and no
denoising chain.

## 2. Why this is not already in the database

`grep -ic` on `methods_db.md` on 2026-11-14: `gflownet` = **0**, `flow network` = **0**,
`generative flow network` = **0**, `detailed balance` = **0**, `trajectory balance` = **0**,
`reward-proportional` = **0**, `mode-covering` = **0**. `generative flow` = 2 (both are
072 NFC *normalizing-flow* prose — an invertible exact-likelihood density);
`reward-guided` = 1 (062 RLPOC's tonal-gravity label). A literature query
(arXiv full-text `all:"GFlowNet" AND all:"music"` → 0; Crossref) found **no
published GFlowNet music method at all** — GFNC is the first music
instantiation documented in this survey.

| Method | Model | Why GFNC differs |
|---|---|---|
| 062 RLPOC | RL policy-gradient maximizing *expected* reward (mode-seeking) | GFNC matches the reward-*proportional* distribution — every high-reward mode is sampled, not just the best |
| 055 SAMC | one annealing trajectory to a single global optimum | GFNC amortizes the *entire* distribution over the DAG and samples it repeatedly; no temperature schedule |
| 064 MRFCC | Gibbs sampling from an energy model (MCMC mixing time) | GFNC is a *learned constructive sampler* — one forward pass per piece, no burn-in, no convergence diagnostics |
| 101 FMC | continuous flow-*matching* ODE transport (normalizing-flow family) | name collision only: no densities, no vector fields; GFN conserves a *flow on a DAG* (see Pitfall 1) |
| 047 DSMG | denoising chain over fixed-length token sequences | GFNC composes variable-length *compositional objects* token by token; no $T$-step reverse process |
| 063 MCTS-GC | per-step look-ahead tree search ($K\cdot L$ rollouts) | GFNC commits each token with one forward pass; no planning, no value network |
| 003 GA / 041 ACO / 117 PSO | iterative population search returning elites | GFNC returns draws from the full reward-proportional distribution; no population, no fitness iterations |
| 067 FOGI | corpus automaton walk (no reward) | GFNC is learned and reward-driven; corpus optional |
| 072 NFC | invertible exact-likelihood flow (normalizing flows) | GFNC is likelihood-free: the guarantee is *flow consistency*, not density |

No DB method learns a sampling policy whose termination distribution is
proportional to a reward; GFNC is the DB's first GFlowNet.

## 3. Model and math

### 3.1 The DAG and the flow

State space: all partial fillings of a $V \times S$ UnitMatrix (each cell
either empty, partially filled, or closed). Source $s_0$ = empty matrix;
terminal set $X$ = fully-filled matrices. Edges = legal token additions
`(voice, section, cell, pitch, duration, velocity)` plus close-cell /
close-piece actions. The DAG is finite and acyclic (depth = token count).

A **flow** $F$ is a non-negative function on states and edges. Normalize to
policies:

$$P_F(s'|s) = \frac{F(s \to s')}{F(s)}, \qquad
P_B(s|s') = \frac{F(s \to s')}{F(s')}.$$

**Detailed balance** (Bengio et al. 2023): for every edge,

$$F(s)\,P_F(s'|s) = F(s')\,P_B(s|s'), \qquad F(x) = R(x)\ \ (x \in X).$$

Consistency + the terminal boundary imply that rolling $P_F$ forward from
$s_0$ terminates at $x$ with probability $P_T(x) = R(x)/Z$, where
$Z = \sum_{x \in X} R(x) = F(s_0)$ is the total flow out of the source —
the partition function. *Proof sketch*: summing detailed balance over all
edges out of a state gives flow conservation
$F(s) = \sum_{s'} F(s \to s')$; by induction on DAG depth, the probability
mass that reaches $X$ through any trajectory $\tau = (s_0, \dots, s_n)$ is
$\prod_t P_F(s_t|s_{t-1}) = \prod_t \frac{F(s_t)}{F(s_{t-1})}\frac{F(s_{t-1}\to s_t)}{F(s_t)} = \frac{F(x)}{F(s_0)} = \frac{R(x)}{Z}$.
This is the GFlowNet analogue of the Markov-chain stationary-distribution
theorem — but reachable in *one pass* instead of after mixing.

### 3.2 Training: trajectory balance

The per-edge objective (flow matching, Bengio et al. 2021) needs edge-flow
estimates. **Trajectory balance** (Malkin et al. 2022) collapses the whole
trajectory into one residual:

$$\mathcal{L}_{\mathrm{TB}}(\tau) = \Big( \log Z + \sum_{t=1}^{n} \log P_F(s_t|s_{t-1})
- \sum_{t=1}^{n} \log P_B(s_{t-1}|s_t) - \log R(x) \Big)^2 .$$

$\log Z$ is a learned scalar; $P_F, P_B$ are softmax policies (here:
transformer/MLP over the partial-piece token sequence, masked by the legal
action set). At $\mathcal{L}_{\mathrm{TB}} = 0$ the guarantee is exact.
Standard variance-reduction extensions: subtrajectory balance (SubTB) and
local credit (LC) for long matrices.

### 3.3 The musical reward

$$R(x) = \sum_{v,s} w_{v,s}\,\varphi_{\text{cell}}(x_{v,s})
+ \sum_v \varphi_{\text{voice}}(x_{v,\cdot}) + \sum_s \varphi_{\text{section}}(x_{\cdot,s}),$$

with smooth surrogate potentials (all already computed elsewhere in the DB):

- $\varphi_{\text{cell}}$: tonal gravity (weighted pc-profile fit — 066's
  $T(y)$ math), density target, register target;
- $\varphi_{\text{voice}}$: melodic smoothness (interval cost — 081 Narmour
  potential), contour shape, register band, voice-independence penalty
  (shared-pc + parallel-motion — 056's prohibitions as soft rewards);
- $\varphi_{\text{section}}$: harmonic parsimony / voice-leading (050 OTVL
  Wasserstein cost, 104 PSSC common-tone counts), rhythmic evenness
  (012 Euclidean-likeness), form-template match (099 SSMC self-similarity).

Temperature: $R_\beta(x) = R(x)^\beta$ — any positive weight is a valid
terminal flow; $\beta = 1$ default, $\beta \to 0$ flattens toward uniform,
$\beta \to \infty$ sharpens toward the argmax (kills mode-covering).

### 3.4 Complexity

Inference $\mathcal{O}(T \cdot d^2)$ per piece ($T$ = note tokens, $d$ = model
width) — non-iterative: no denoising steps (047: $T \cdot N \cdot D$), no tree
search (063: $K \cdot L \cdot N$), no Gibbs sweeps (064: $I \cdot V \cdot S$).
Training $\mathcal{O}(E \cdot T \cdot d^2)$ over $E$ trajectories. Memory:
$\mathcal{O}(T \cdot d)$ context (the full partial matrix).

## 4. Python implementation sketch

```python
"""GFNC — Generative Flow Network Composition (gflownet_composition.py).
Sketch: DAG + trajectory-balance training + reward-proportional sampling.
The verified toy (pure numpy, tabular policies) is _web142/verify_142_GFNC.py.
"""
import numpy as np

# --- DAG over a VxS UnitMatrix; cell = list of (pc, dur, vel) tokens -----
class MusicDAG:
    def __init__(self, V, S, pcs, durs, section_len):
        self.V, self.S, self.pcs, self.durs = V, S, pcs, durs
        self.LEN = section_len          # 1920 ticks at tpb 480, 4/4
    def legal_actions(self, state):
        """(cell_v, cell_s, pc, dur, vel) fills + close-cell + close-piece."""
        acts = []
        for v in range(self.V):
            for s in range(self.S):
                cell = state.cells[v][s]
                if cell is None:
                    continue
                if sum(d for _, d, _ in cell.events) + self.LEN < self.LEN and not cell.closed:
                    for pc in self.pcs:
                        for d in self.durs:
                            acts.append(("note", v, s, pc, d))
                elif not cell.closed and self.can_close(cell):
                    acts.append(("close_cell", v, s))
        if all(c.closed for row in state.cells for c in row):
            acts.append(("close_piece",))
        return acts
    def can_close(self, cell):
        return sum(d for _, d, _ in cell.events) == self.LEN  # zero-drift gate

# --- policies: softmax over legal actions, context = token sequence -------
class GFNPolicy:
    def __init__(self, d):
        self.d = d  # transformer over the partial-piece token sequence (sketch)
    def forward_logprobs(self, state, acts):
        logits = self._net(state.token_seq())[: len(acts)]   # masked
        return logits - np.log(np.sum(np.exp(logits)))
    def backward_logprobs(self, state, acts):
        return self._bnet(state.token_seq())[: len(acts)]    # over predecessors

# --- training: trajectory balance ----------------------------------------
def train_tb(dag, policy, reward_fn, logZ, n_traj=8000, lr=0.1):
    for _ in range(n_traj):
        traj = [src]; s = src
        while not s.terminal:
            acts = dag.legal_actions(s)
            p = np.exp(policy.forward_logprobs(s, acts))
            a = np.random.choice(len(acts), p=p)
            s = s.apply(acts[a]); traj.append(s)
        lf = sum(np.log(policy.forward_logprobs(t, dag.legal_actions(t))[ai])
                 for t, ai in zip(traj[:-1], [chosen_actions]))
        lb = sum(np.log(policy.backward_logprobs(t, preds)[bi])
                 for t, bi in zip(traj[1:], [chosen_backward]))
        resid = logZ + lf - lb - np.log(reward_fn(traj[-1]))
        # SGD on (policy params, logZ) with gradient 2*resid * d(resid)/dparam
        logZ -= lr * 2.0 * resid

# --- sampling: one forward pass per piece --------------------------------
def sample_piece(dag, policy, seed=None):
    rng = np.random.default_rng(seed)
    s = src
    while not s.terminal:
        acts = dag.legal_actions(s)
        p = np.exp(policy.forward_logprobs(s, acts))
        s = s.apply(acts[rng.choice(len(acts), p=p)])
    return s  # fully-filled UnitMatrix -> validate() -> to_midi()
```

Engine integration follows the musicom workflow: closed cells carry the
terminal-landmark event `MusicEvent(0, 0, BAR, BAR)` (the
`_unit_from_events` zero-drift pattern), then `fill_voice_section` →
`validate()` → `to_midi()`.

## 5. Verification (6/6)

`_web142/verify_142_GFNC.py` trains a *tabular* GFlowNet by trajectory
balance on a toy 2-voice × 2-section UnitMatrix DAG (1 note per cell,
4 pitch classes: 625 states, 256 terminal pieces, 2000 edges; reward =
tonic gravity + horizontal smoothness + vertical consonance + bass anchor;
8000 TB updates, 50 000 samples):

| # | Check | Result |
|---|---|---|
| C1a | Pearson corr of empirical $P_T$ vs $R/Z$ | **0.9858** |
| C1b | max $\|P_T - R/Z\|$ over 256 pieces | **0.00107** |
| C1c | KL($R/Z$ ‖ $P_T^{\text{emp}}$) | **0.0049** |
| C2 | top-8 reward states sampled | **8/8**, min rel-freq ratio **0.932** |
| C3 | distinct pieces: omniscient greedy argmax vs GFN | **1** vs **8** modes |
| C5 | $\mathbb{E}[R]$ measured vs predicted $\sum_x R(x)^2/Z$ | **4.911** vs **4.951** |
| + | learned $\log Z$ vs true $\log \sum_x R(x)$ | **6.867** vs **6.894** |

Log: `_web142/verify_142_output.txt`.

## 6. Musical Elements Framework

- **PITCH**: pitch-class tokens per cell; tonality = the tonal-gravity
  reward term (weighted pc-profile fit), so pc frequencies follow the
  reward's preference — a tonal profile as a sampling distribution (097's
  MaxEnt reading, reached constructively, no corpus). Register bands per
  voice from per-voice reward terms.
- **RHYTHM**: tick-quantized duration tokens (480 tpb); groove term scores
  Euclidean-likeness (012) and density targets; the grid-locked skeleton is
  humanized downstream (concrete → absolute handoff), never inside the DAG.
- **HARMONY**: emergent from per-column parsimony/consonance potentials
  (050 OTVL / 104 PSSC); the policy learns "what progressions this reward
  likes" — coherent without an explicit grammar (contrast 086 HMM-C).
- **STRUCTURE**: macro-form = the per-section reward schedule
  (HOME/LIFT/TENSE/TURN weights); reprise = repeated schedule; a frozen
  schedule with masked cells = exact form skeleton with stochastic fill
  (001 Skeleton-First, learned).
- **TEXTURE**: density/register terms per cell; voice-independence penalty
  (shared-pc, parallel motion) = 056's prohibitions as soft rewards;
  mode-covering sampling = a variation set — every piece a different
  textural realization of the same form.

## 7. UnitMatrix Integration

**Voices = rows.** The policy's context is the full partial matrix; per-voice
reward terms (register band, contour, independence) make rows learn distinct
characters; separation is sampled (soft), not hard-forbidden.

**Sections = columns.** One reward-weight block $w_s$ per column; close-cell
is legal only when events sum to exactly `section_len` — the zero-drift
invariant is a *mask*, so seams cannot drift.

**Cells = MusicUnit.** Cell $(v,s)$ accumulates tokens until close; closing
appends the terminal landmark and yields the `MusicUnit` for
`fill_voice_section`; `validate()` then passes by construction.

**Candidate code path:** `generators/gflownet_composition.py` —
`MusicDAG`, `MusicReward`, `GFNPolicy` (transformer), `train_trajectory_balance`,
`GFNCGenerator`. Sibling of `generators/rl_policy.py` (062) in spirit
(sampling-, not maximizing-oriented); amortized-sampling complement to
`generators/mrf_constraint.py` (064).

## 8. References

- Bengio, E., Jain, M., Korablyov, M., Precup, D., & Bengio, Y. (2021). "Flow Network based Generative Models for Non-Iterative Diverse Candidate Generation." NeurIPS 2021. arXiv:2106.04399.
- Bengio, Y., Lahlou, S., Deleu, T., Hu, E. J., Tiwari, V., & Bengio, E. (2023). "GFlowNet Foundations." JMLR 24(210), 1–55. arXiv:2111.09266.
- Malkin, N., Lahlou, S., Deleu, T., Ji, K., Hu, E. J., Everett, K. E., Zhang, D., & Bengio, Y. (2022). "Trajectory Balance: Improved Credit Assignment in GFlowNets." NeurIPS 2022. arXiv:2201.13259.
- Jain, M., et al. (2022). "Biological Sequence Design with GFlowNets." ICML 2022. arXiv:2203.04115.
- Lahlou, S., et al. (2023). "A Theory of Continuous Generative Flow Networks." ICML 2023. arXiv:2301.12594.
- Jain, M., et al. (2023). "GFlowNets for AI-Driven Scientific Discovery." arXiv:2302.00615.
- Music-application gap query (2026-11-14): arXiv API full-text `all:"GFlowNet" AND all:"music"` → 0; `AND all:"lyrics"` → 0; Crossref bibliographic queries → molecular/EEG/peptide only. Wikipedia: no GFlowNet article.
- Verified toy: `_web142/verify_142_GFNC.py` (pure numpy, tabular policies), log `_web142/verify_142_output.txt`.
