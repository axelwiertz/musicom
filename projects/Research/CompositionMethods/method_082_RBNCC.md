# Random Boolean Network Criticality Composition (RBNCC)

**Method ID**: 082
**Paradigm**: Nature-Led
**Layer**: concrete (emits note events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/boolean_network.py`
**Acronym**: RBNCC

## One-line description
Composes by running a synchronous random Boolean network (Kauffman's gene-regulatory model) at its critical point — the deterministic state trajectory falls into an attractor cycle that is decoded into a repeating groove/chord-progression loop, with connectivity $K$ and output bias $p$ as the edge-of-chaos creative dial and the pre-attractor transient as connective/tension material.

## Extended math

A random Boolean network is a triple $(N, K, \{f_i\})$: $N$ binary nodes
$x_i \in \{0,1\}$, each with $K$ incoming edges and a Boolean function
$f_i : \{0,1\}^K \to \{0,1\}$. Under **synchronous update** the state vector
$x(t) \in \{0,1\}^N$ evolves as

$$x_i(t+1) = f_i\big(x_{j_1(i)}(t), \dots, x_{j_K(i)}(t)\big).$$

Since the state space is finite ($2^N$), every trajectory is eventually
periodic: there is a **transient** of length $T$ followed by an **attractor
cycle** of length $L$ (a **point attractor** if $L=1$, else a **cycle
attractor**).

**Phase transition.** The Derrida–Pomeau annealed approximation gives a
critical mean connectivity

$$K_c = \frac{1}{2p(1-p)},$$

where $p = \Pr[f_i(\cdot)=0]$ is the output bias. For $p=0.5$, $K_c=2$. The
three regimes (Kauffman 1993):

| Regime | Condition | Attractor length | Character |
|---|---|---|---|
| Ordered (frozen) | $K < K_c$ | short, $L = O(1)$ | stable core, high overlap, strong memory |
| Critical (edge of chaos) | $K \approx K_c$ | $L \sim \sqrt{N}$ (power-law tail) | mixed frozen core + unstable periphery, maximal information |
| Chaotic | $K > K_c$ | $L \sim 2^N$ | no memory, sensitive to $x(0)$ |

The **frozen core** (nodes whose function is independent of most inputs)
provides the harmonic/scale scaffold; the **unstable periphery** provides the
figuration. In the critical regime the frozen fraction is intermediate, giving
an attractor cycle long enough to be a musical phrase and varied enough to be
interesting.

**Decoding.** Partition the state vector into per-tick musical features. For a
12-bit pitch-class sub-vector $x^{(pc)} \in \{0,1\}^{12}$, the sounding
pitch-class set at tick $t$ is $S_t = \{i : x^{(pc)}_i(t) = 1\}$. The attractor
cycle is a finite sequence of pc-sets $S_0 \to S_1 \to \dots \to S_{L-1} \to S_0$,
i.e. a **chord/scale progression**. Voice-leading between adjacent states is the
symmetric difference $S_{t+1} \triangle S_t$ (bits that flip), giving a natural
parsimony metric: minimize flips = smooth voice-leading.

**Density.** The expected number of active bits per tick is $Np$ (per bit); a
node with bias $p$ and mean connectivity $K$ has a fixed-point probability
determined self-consistently, so $p$ is the note-density dial and $K$ is the
complexity/stability dial.

**Cycle detection.** With $f$ the parallel update map, the classic
Floyd/Brent algorithm finds $(\mu, \lambda)$ (transient length, cycle length)
in $O(N \cdot \mu)$ evaluations and $O(1)$ memory, since $x(t)$ is
deterministic.

**Cost.** Each tick is $N$ Boolean lookups → $O(N)$ per tick; $O(N \cdot
(N_{\text{ticks}} + \mu))$ total, i.e. linear in the number of emitted events.
Deterministic per seed (no stochasticity after the truth tables are drawn).

## Python implementation sketch

```python
"""Random Boolean Network Criticality Composition (Method 082, RBNCC)."""
import random

def build_rbn(N, K, p=0.5, seed=0):
    """Return nodes as (incoming_edge_indices, truth_table)."""
    rng = random.Random(seed)
    nodes = []
    for _ in range(N):
        ins = rng.sample(range(N), K)             # K distinct incoming edges
        # truth table: one output bit per of 2^K input combinations, bias p
        table = [rng.random() < (1 - p) for _ in range(1 << K)]
        nodes.append((ins, table))
    return nodes

def step(nodes, x):
    """One synchronous update: x(t) -> x(t+1)."""
    out = []
    for ins, table in nodes:
        idx = 0
        for bitpos, src in enumerate(ins):
            idx |= (x[src] << bitpos)            # input pattern -> table index
        out.append(1 if table[idx] else 0)
    return out

def detect_cycle(nodes, x0):
    """Brent's algorithm: return (mu, lam) = (transient len, cycle len)."""
    power = lam = 1
    tortoise = x0
    hare = step(nodes, x0)
    while tortoise != hare:
        if power == lam:
            tortoise = hare
            power *= 2
            lam = 0
        hare = step(nodes, hare)
        lam += 1
    # find mu
    mu = 0
    tortoise = hare = x0
    for _ in range(lam):
        hare = step(nodes, hare)
    while tortoise != hare:
        tortoise = step(nodes, tortoise)
        hare = step(nodes, hare)
        mu += 1
    return mu, lam

def run(nodes, x0, n_steps):
    """Yield states x(0)..x(n_steps-1)."""
    x = x0
    for _ in range(n_steps):
        yield x
        x = step(nodes, x)

def decode_pcset(x, base=48):
    """Map a 12-bit sub-vector to sounding MIDI pitches (octave at base)."""
    return [base + i for i, b in enumerate(x[:12]) if b]

def compose_loop(N=24, K=2, p=0.5, n_steps=16, seed=0):
    """Build, run, and decode a critical-RBN groove as a pc-set sequence."""
    nodes = build_rbn(N, K, p, seed)
    x0 = [0] * N
    rng = random.Random(seed + 1)
    x0 = [rng.random() < (1 - p) for _ in range(N)]  # random initial state
    mu, lam = detect_cycle(nodes, x0)
    states = list(run(nodes, x0, mu + lam))[mu:]     # the attractor cycle only
    return [decode_pcset(s) for s in states], (mu, lam)
```

**Musicom integration** (engine authors the MIDI; real imports per AGENTS.md):
```python
# from structures import MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# for v in range(V): composer.add_voice(f"voice{v}", ...)
# for s in range(S):
#     K, p, n_steps = section_specs[s]              # per-section (K,p) dial
#     loop, (mu, lam) = compose_loop(N, K, p, n_steps, seed=hash((s, 0)))
#     for t, pcset in enumerate(loop):
#         composer.fill_voice_section("voice0", s, create_chord_unit(pcset, dur, tick=t))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References
- Kauffman, S. A. (1969). "Metabolic stability and epigenesis in randomly constructed genetic nets." *Journal of Theoretical Biology* 22(3), 437–467.
- Kauffman, S. A. (1993). *The Origins of Order: Self-Organization and Selection in Evolution*. Oxford University Press.
- Derrida, B., & Pomeau, Y. (1986). "Random networks of automata: a simple annealed approximation." *Europhysics Letters* 1(2), 45–49.
- Langton, C. G. (1990). "Computation at the edge of chaos: phase transitions and emergent computation." *Physica D* 42, 12–37.
- Gershenson, C. (2004). "Introduction to Random Boolean Networks." arXiv:cs/0406014.
- Aldana, M., Coppersmith, S., & Kadanoff, L. P. (2003). "Boolean dynamics with random couplings." In *Perspectives and Problems in Nonlinear Science*, Springer.
- Burraston, D., & Edmonds, E. (2005). "Cellular automata in generative electronic music and sonic art: a historical and technical review." *Digital Creativity* 16(3), 165–185.
