# Method 130 — Subshift of Finite Type Composition (SFT-C)

- **Paradigm**: Rules-Based
- **Layer**: concrete (emits `MusicEvent`s that fill UnitMatrix cells)
- **Module**: `generators/subshift_sft.py`, class `SFTComposer`
- **DB section**: `methods_db.md` → `# Subshift of Finite Type Composition (SFT-C) (Method 130)`

Composes each voice as a walk through a constrained word language: a finite list of
**forbidden words** defines the grammar, generation = walking the grammar's de Bruijn
graph, and the language's **topological entropy** is the variety/tension meter.

---

## 1. The mathematical object

Let $A$ be a finite alphabet (pitch classes, scale degrees, interval classes, or
$\{0,1\}$ for onset/rest). A **shift space** is a closed, shift-invariant set of
bi-infinite sequences $x\in A^{\mathbb{Z}}$ (the shift $\sigma$ deletes the first
symbol). A **subshift of finite type (SFT)** is

$$X_F=\bigl\{x\in A^{\mathbb{Z}}:\ \text{no word of }F\text{ occurs in }x\bigr\},
\qquad F\subset\bigcup_{n\ge1} A^n \text{ finite}.$$

Every SFT is an **edge shift**: with states = allowed $k$-blocks and edges = allowed
$(k{+}1)$-blocks (the **de Bruijn graph of order $k{+}1$**), a bi-infinite path in the
0/1 adjacency matrix $A$ is a bi-infinite word in $X_F$, and vice versa. A $k$-step SFT
is one whose membership test needs only windows of length $k{+}1$.

Verified structure (2026-10-31, `verify_130_SFTC.py`):

| object | value | check |
|---|---|---|
| golden-mean shift (forbid `11`) | $p(n)=F(n+2)$ for $n=1..11$ ($p(8)=55$) | direct enumeration == Fibonacci |
| Perron eigenvalue of $\begin{smallmatrix}0&1\\1&1\end{smallmatrix}$ | $\varphi=1.61803399$ | power iteration, $<10^{-6}$ error |
| entropy of golden-mean shift | $\log\varphi=0.4812$ nats/sym ($0.694$ bits/sym) | from $\lambda$ and from $p(8)/p(7)$ |
| RLL$(1,\infty)$ capacity | $\lambda=\varphi$ | run-length adjacency |
| RLL$(2,\infty)$ capacity | $\lambda=1.465571$ = supergolden ratio (root of $x^3-x^2-1=0$) | power iteration + direct counts $p(8)=28,\ p(9)=41$, ratio $1.4643$ |
| Fibonacci word complexity | $p(n)=n+1$ for $n=2..19$ | Morse–Hedlund bound $p(n)\ge n+1$ respected exactly |
| Parry measure, golden-mean | $P=\begin{smallmatrix}0&1\\ 1/\varphi^2&1/\varphi\end{smallmatrix}=\begin{smallmatrix}0&1\\0.382&0.618\end{smallmatrix}$ | row sums $=1$ |
| product shift, forbid $L>U$ | $6/9$ columns survive on a $3\times3$ pair alphabet | column filter |
| de Bruijn order-2 edge walks | length-6 words $=21=F(8)$ | edge-walk count == direct count |

## 2. Musical mapping

**Alphabet** = pitch vocabulary per voice; **forbidden words** = the style sheet.
**Entropy** $h=\log\lambda(A)$ = variety rate per symbol; **constraint pressure**
$\Delta h=\log k-h$ = tension; **period-$n$ orbits** = ostinati; **Parry measure** =
least-biased emission; **RLL$(d,k)$** = rhythm run-length grammars; **product shift +
column constraints** = harmony/counterpoint; **sliding-block codes** = motivic
re-encoding; **Morse–Hedlund** = the no-degeneracy law; **Krieger embedding** = any
style is a subshift of a finite-type super-shift.

- **Pitch** follows the symbol value: symbol $s$ → degree $s$ of the ladder, then a
  per-voice register offset. The tonic fixed point (the repeating tonic-degree word) is
  the HOME orbit; TENSE = high-$\Delta h$ grammar region; the cadence is the collapse of
  the continuation set to a single orbit — a forced resolution, which is exactly what a
  perfect authentic cadence is.
- **Rhythm** = a $\{0,1\}$ alphabet with RLL$(d,k)$: at least $d$ rests between onsets,
  at most $k$ consecutive rests. Capacity $\log_2\lambda$ = the groove's variety rate
  (measured: $(1,\infty)\to0.694$ bits/sym, $(2,\infty)\to0.551$ bits/sym).
- **Harmony** = column constraints on the product shift: chord membership forbids
  non-chord columns; voice-leading forbids 2-column words that leap in both voices;
  parallels forbid (fifth,fifth) and (unison,unison). The progression is *emergent*.
- **Structure** = section-wise grammar schedule $(F_j,A_j)$; $h_j$ = section character;
  reprise = exact grammar + orbit reuse; zeta function enumerates available ostinati.
- **Texture** = the entropy gap $h(X_1)+h(X_2)-h(X_1\times X_2)$ = harmonic binding;
  zero gap = independent voices, large gap = chorale.

## 3. Complexity

| operation | cost |
|---|---|
| build de Bruijn graph of order $k{+}1$ | $\mathcal{O}(|A|^{k+1})$ (state count) |
| entropy via power iteration | $\mathcal{O}(I\cdot|E|)$ on the edge graph |
| Parry matrix | one more Perron-vector pass, $\mathcal{O}(I\cdot|E|)$ |
| emit one symbol (walk one edge) | $\mathcal{O}(1)$ amortized; $\mathcal{O}(N)$ per voice |
| periodic orbits / trace$(A^n)$ | $\mathcal{O}(n\cdot|E|)$ per $n$ |
| product shift column filter | $\mathcal{O}(|A_1|\cdots|A_V|)$ per column rule |

Practical note: $k\le2$ grammars cover most riff/counterpoint rules (a 7-degree
alphabet at $k{=}3$ is 2401 states — still fine; $k{=}5$ is 7⁶ — not fine; push
longer memory to the sofic/DFA layer).

## 4. Python implementation sketch

```python
import numpy as np
from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

class SFTComposer:
    def __init__(self, alphabet, forbidden, k=1):
        # alphabet: list of symbols; forbidden: set of strings over alphabet
        self.alpha = list(alphabet)
        self.idx = {s: i for i, s in enumerate(alphabet)}
        self.k = k
        self.states, self.edges = self._build_debruijn(forbidden)

    def _build_debruijn(self, forbidden):
        # states = allowed k-blocks; edges = (state, next_symbol, next_state)
        from itertools import product
        blocks = set(product(self.alpha, repeat=self.k))
        for f in forbidden:
            for i in range(len(f) - self.k + 1):
                w = tuple(f[i:i+self.k])
                blocks.discard(w)
        states = sorted(blocks)
        edges = []
        for s in states:
            for a in self.alpha:
                t = s[1:] + (a,)
                if t in blocks and tuple(s[1:]) + (a,) not in forbidden:
                    edges.append((s, a, t))
        return states, edges

    def adjacency(self):
        m = len(self.states); si = {s: i for i, s in enumerate(self.states)}
        A = np.zeros((m, m))
        for s, a, t in self.edges:
            A[si[s], si[t]] = 1
        return A

    def entropy(self):
        A = self.adjacency()
        x = np.ones(A.shape[0]); lam = 1.0
        for _ in range(500):
            x = A @ x; lam = x.max(); x = x / lam
        return float(np.log(lam))          # nats / symbol

    def parry_matrix(self):
        A = self.adjacency(); lam = np.exp(self.entropy())
        v = np.ones(A.shape[0])
        for _ in range(500):
            v = A @ v; v = v / v.max()
        P = np.zeros_like(A, dtype=float)
        for i in range(A.shape[0]):
            P[i] = A[i] * v / (lam * v[i]) # row sums == 1 (verify!)
        return P

    def walk(self, seed, length, mode="parry"):
        # mode: 'parry' (max-entropy), 'uniform', 'orbit' (repeat a period loop)
        rng = np.random.default_rng(seed)
        P = self.parry_matrix() if mode == "parry" else None
        si = {s: i for i, s in enumerate(self.states)}
        syms = [self.states[0][-1]]  # seed the walk with one symbol
        cur = self.states[0]
        for _ in range(length - 1):
            i = si[cur]
            if mode == "uniform":
                nxts = [t for s, a, t in self.edges if s == cur]
                nxt = nxts[rng.integers(len(nxts))]
            else:
                # sample from row i of Parry P over successor states
                row = P[i]; succ = [j for j in range(len(row)) if row[j] > 0]
                p = np.array([row[j] for j in succ]); p = p / p.sum()
                j = succ[rng.choice(len(succ), p=p)]
                nxt = self.states[j]
            syms.append(nxt[-1]); cur = nxt
        return syms

def rll_adjacency(d, k):
    """(d,k) run-length-limited: >= d zeros between ones, <= k consecutive zeros."""
    m = k + 1  # states = zero-run length 0..k (0 = last symbol was 1)
    B = np.zeros((m, m))
    for j in range(0, k + 1):
        if j < k:
            B[j][j + 1] = 1            # emit 0
        if j >= d:
            B[j][0] = 1                # emit 1 only after >= d zeros
    return B
# capacity = log2(spectral_radius(B));  rll_adjacency(1, inf) ~ golden mean

def emit(symbols, ladder, slot_ticks, velocities):
    """Decode a symbol list into per-row MusicEvents (row given by ladder)."""
    out = []
    for t, s in enumerate(symbols):
        pitch = ladder[s]              # symbol -> ladder degree
        start = t * slot_ticks
        out.append(MusicEvent(pitch=pitch, volume=velocities[t % len(velocities)],
                              start_tick=start, end_tick=start + slot_ticks))
    return out

# composer.create_matrix / add_voice / add_section, then per cell:
#   syms = sft.walk(seed, N_cell, mode='parry')
#   composer.fill_voice_section(voice, section, _unit_from_events(emit(...), SEC_LEN))
# ok, msg = composer.validate()  -> must be True ; to_midi(path)
```

Verified numeric core: `verify_130_SFTC.py` (Fibonacci counts, $\varphi$ power
iteration, RLL capacities, Morse–Hedlund budget, Parry row-stochasticity, crossing
column filter, de Bruijn edge-walk counts). A full 4-voice reference render through
`UnitMatrixComposer` is the natural next step (mirror `abgc_129_compose.py`), with a
bass row on an RLL$(1,\infty)$ grammar and three degree rows bound by a no-crossing
column constraint.

## 5. Selection heuristics

| want | do |
|---|---|
| sparse minimalist pulse | RLL$(1,\infty)$ or golden-mean grammar on $\{0,1\}$ |
| groove with density cap | RLL$(d,k)$ with $d$ = max subdivision, $k$ = max rest run |
| varied diatonic melody | 7-degree alphabet, forbid leap-leap and tritone, $k\le2$ |
| tension rise | raise $\Delta h$ (tighten $F$) per section |
| cadence | collapsing grammar: forbid every continuation but the tonic orbit |
| ostinato / riff | ride one period-$n$ orbit (zeta-function listing) |
| chorale binding | product shift + no-crossing + no-parallel column rules |
| reprise / recap | reuse exact $(F,A)$ and orbit of the A section |
| max-entropy style sample | Parry walk; flatter variety: uniform walk |

## 6. References

- Lind, D. & Marcus, B. (1995). *An Introduction to Symbolic Dynamics and Coding*, Cambridge University Press. — SFTs, edge shifts, entropy $h=\log\lambda$, zeta function, Parry measure, Krieger embedding.
- Morse, M. & Hedlund, G. A. (1944). "Symbolic dynamics II: Sturmian trajectories." *American Journal of Mathematics* 66(1): 1–42. — Morse–Hedlund theorem ($p(n)\le n$ ⟹ periodic).
- Parry, W. (1964). "Intrinsic Markov chains." *Transactions of the American Mathematical Society* 112: 55–66. — measure of maximal entropy.
- Kautz, W. H. (1965). "Fibonacci codes for synchronization control." *IEEE Transactions on Information Theory* IT-11: 284–292; Immink, K. A. S. (1990). "Runlength-limited sequences." *Proceedings of the IEEE* 78(11): 1745–1759. — $(d,k)$ RLL capacity.
- Weiss, B. (1973). "Subshifts of finite type and sofic systems." *Monatshefte für Mathematik* 77: 462–474. — sofic = regular-language generalization.
- Shannon, C. E. (1948). "A mathematical theory of communication." *Bell System Technical Journal* 27. — constrained-channel capacity = entropy rate of the language.
- Gómez Aíza, R. (2020). "Symbolic dynamical scales: modes, orbitals, and transversals." arXiv:2009.02669. — scales from vertex shifts (first-symbol rule), n-TET; pitch-alphabet source.
- "Symbolic Dynamics of Music from Europe and Japan." arXiv:1810.06119. — block-entropy *analysis* of musical texts (adjacent, non-method).
- Counterpoint: Fux, J. J. (1725). *Gradus ad Parnassum* — the original forbidden-word grammar (cf. method 056 SCCC).

## 7. Pitfalls (short form)

1. Full shift with no forbidden words = DBUC (077), not SFT-C; soft weights only = Markov (002). Keep hard 0/1 constraints.
2. Unbounded-memory rules ("always start on tonic") are sofic/DFA, not SFT — layer a DFA on top.
3. Glue walk segments with state continuity ($k{-}1$ overlapping symbols) or the seam creates a forbidden word.
4. De Bruijn graph is $\mathcal{O}(|A|^{k+1})$; keep $k\le2$ for pitch grammars.
5. Golden-mean $h=\log\varphi$ is very thin — use for percussion/sparse, not melody.
6. Orbits are available ostinati, not good ones; pair with phrase contour.
7. Morse–Hedlund: $p(n)\le n$ ⟹ your "varied" section is secretly a loop.
8. Parry needs the right Perron vector and row sums $=1$; record $\lambda$, $v$, mode in provenance.
9. Zero-drift: $N_j\times$ slot_ticks must tile the section; pad short walks to the seam.
10. "No parallels" is a 2-block rule with hidden-parallel loopholes; record the exact forbidden-word list verbatim in provenance — the grammar IS the method.
