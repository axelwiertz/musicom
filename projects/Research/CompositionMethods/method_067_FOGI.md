# Method 067 — Factor Oracle Guided Improvisation (FOGI)

**Paradigm**: Stochastic
**Classification**: Pitch, Rhythm, Harmony, Structure, Texture | Tonal Gravity: Weak (Corpus-implicit) | Metric Binding: Grid-Locked / Continuous | Memory Depth: Meso / Longest-Repeated-Suffix | Time Complexity: $\mathcal{O}(n)$ build, $\mathcal{O}(1)$ per improv symbol

---

## 1. What it is

Factor Oracle Guided Improvisation (FOGI) is a **non-parametric, data-driven** composition engine. It models a reference corpus (one seed motif, a style excerpt, or an entire composition) as a *Factor Oracle* automaton, then re-generates material by walking that automaton while occasionally "jumping" along its suffix-link structure into a repeated past context. The result is an arbitrarily long, corpus-styled sequence that is locally grammatical (every emitted continuation actually occurred in the source) but globally novel (the spliced phrase boundaries never occurred contiguously).

It is the **unbounded-context generalization of Method 002 (Markov transitions)**. A $k$-th-order Markov chain uses a *fixed* hand-tuned prefix length as context. A Factor Oracle uses the **longest repeated suffix of the entire history** as context — a context length that grows automatically to exactly the span the source demonstrably repeats. There is no order parameter to tune, and no training loop: the automaton *is* the model.

## 2. Historical line

The Factor Oracle was introduced for string matching by **Allauzen, Crochemore & Raffinot (1999)**. Its musical turn came from **Assayag & Dubnov (2004)** and the IRCAM **OMax** system (2006), which turned the oracle's suffix links into a live improvisation machine. **Dubnov, Assayag & El-Yaniv (1998)** had already connected the underlying Lempel-Ziv incremental-parsing scheme to music information theory (the "Information Rate" of a sequence), giving the recombination mechanism a formal meaning: suffix-link jumps traverse genuinely *informative* branch points.

## 3. Data structure

A Factor Oracle over a symbol string $x_1 \dots x_n$ is:

- **States** $0 \dots n$ (one per position, plus the empty root 0).
- **Forward transitions** $\delta(q, a) \to q'$: a directed acyclic graph edge labeled by a symbol.
- **Suffix links** $sfx[i]$: a reverse arc pointing from state $i$ to the state reached by the **longest proper suffix of $x_1\dots x_i$ that also appears elsewhere as a prefix path**.

Two invariants matter musically:

1. Every **factor** (contiguous substring) of the source is spelled by *some* forward path from the root. The oracle therefore recognizes at least the whole factor language of the source (and, thanks to the construction, a superset of it — which is what lets it generate *new* strings).
2. A **divergence point** is a state with $\geq 2$ outgoing forward transitions — a place where the source's material genuinely split. These are the improvisation hinges: repeated motifs live on suffix-link cycles that keep returning to divergence points (the "Trojan islands" of Passeron), and every suffix-link *landing* state is exactly such a context of ambiguity.

## 4. Formal build (online, left-to-right)

Initialize: state 0, $sfx[0] = -1$, no transitions.

For each incoming symbol $x_i$ (arriving at state $i{-}1$):

1. Create state $i$; add forward transition $i{-}1 \xrightarrow{x_i} i$.
2. Walk back along suffix links: $k = sfx[i{-}1]$, then loop while $k \neq -1$ and $x_i \notin \delta(k)$.
   - During the walk, add **stationary** forward transitions $\delta(k)[x_i] = i$ (this is what lets the oracle accept more than the source's factors).
3. When the walk stops at some $k$ with $x_i \in \delta(k)$, set $sfx[i] = \delta(k)[x_i]$; if the walk bottoms out at $-1$, set $sfx[i] = 0$.

After processing $n$ symbols, $sfx[i]$ equals the state reached by the **longest repeated suffix** of the prefix ending at $i$.

**Complexity**: $\mathcal{O}(n)$ time and $\mathcal{O}(n)$ space in the worst case — at most $n$ states, $\le 2(n-1)$ forward arcs plus $n$ suffix links (stationary transitions add at most a linear factor). This is dramatically cheaper than any trained generative model, and cheaper than an equivalent-order Markov chain.

## 5. Generation (the improvisation loop)

Maintain a current state $q$, starting from the root. Iterate:

- **Continuation mode** (probability $1 - p_{recomb}$): follow a forward transition $\delta(q, a)$ whose label is drawn proportionally to its **oracle weight** (count of outgoing continuations per label, optionally recency-weighted); advance $q \gets \delta(q,a)$; emit $a$.
- **Recombination mode** (probability $p_{recomb}$): jump back along the suffix link — one hop, or a *chain* of hops (multi-hop) — to some earlier state $q' \gets sfx(\dots sfx(q))$ that shares a long suffix with $q$ but is a divergence point; then resume continuation from $q'$.

Because the two modes alternate, the output is a **patchwork of source phrases joined at shared repeated suffixes**. Every local transition is source-legal, so the ear never hears a "wrong" note or rhythm relative to the corpus; the *junctions* are where novelty enters.

## 6. Musical Elements Framework

| Element | Mechanism |
|---|---|
| **PITCH** | Emitted symbols = quantized pitch (or pitch+duration) events from the corpus. Forward transitions replay exact source pitch; recombination splices contexts whose longest repeated suffix matches, so every interval is one the source actually used after that context. Off-key material is impossible (the oracle cannot leave the corpus pitch set). |
| **RHYTHM** | Either encoded jointly into each symbol (onset/IOI tuples, preserving source groove/swing), or driven by a *parallel* FOGI over an IOI/velocity alphabet. Recombination perturbs the rhythmic surface exactly where it perturbs pitch. |
| **HARMONY** | Implicit in the corpus. A **shared oracle** (one automaton over the interleaved multi-voice symbol stream) encodes vertical co-occurrence directly in the symbol, so chordal cohesion is guaranteed without a chord grammar layer. |
| **STRUCTURE** | Emergent from suffix-link topology. Self-referencing suffix-link cycles = "theme" regions the walk re-enters (refrain/rondo); long recombination jumps = development pivots. **Section-token conditioning** (section-id symbols in the alphabet, with transitions restricted to the current section) restores explicit A→B→A macro-form. |
| **TEXTURE** | Branching factor at $q$ = texture density. Dense divergence points improvise into varied/ornamented texture; sparse single-continuation states replay verbatim and thin out. The Dubnov **Information Rate** down the suffix chain is a continuous texture/scalar signal. |

## 7. UnitMatrix integration (Musicom)

- **Rows (Voices)** $v$: each voice is (a) an independent FOGI walk over its own corpus slice (polyphonic), or (b) a shared-oracle slot reader (homophonic — vertical consonance from co-encoded symbols).
- **Columns (Sections)** $s$: a continuation-leg of the walk. Section-token conditioning confines each column to its section's reference region.
- **Cells** $U_{v,s}$ carry `PITCH` (emitted symbol), `RHYTHM` (onset/IOI from the same/parallel alphabet), `HARMONY` (shared-oracle chord slot or chord-label symbol), `TEXTURE` (branching factor at the emitting state).

## 8. Reference implementation

```python
from __future__ import annotations
from collections import defaultdict
import numpy as np


class FactorOracle:
    """Linear-time Factor Oracle over a symbol string (Allauzen-Crochemore-Raffinot 1999)."""

    def __init__(self, symbols):
        self.n = len(symbols) + 1
        self.sfx = [-1] * self.n                # suffix links (reverse arcs)
        self.fwd = [defaultdict(list) for _ in range(self.n)]  # forward transitions
        self._build(symbols)

    def _build(self, s):
        for i, sym in enumerate(s, start=1):
            # 1. direct forward transition from previous state
            self.fwd[i - 1][sym].append(i)
            # 2. walk suffix links, adding stationary transitions until a match
            k = self.sfx[i - 1]
            while k != -1 and sym not in self.fwd[k]:
                self.fwd[k][sym].append(i)
                k = self.sfx[k]
            self.sfx[i] = (k + 1) if k != -1 else 0

    def improvise(self, n_steps, p_recomb=0.33, seed=None):
        rng = np.random.default_rng(seed)
        q, out = 0, []
        for _ in range(n_steps):
            if rng.random() < p_recomb:
                # recombination: hop back through repeated context (1-2 suffix hops)
                hops = int(rng.integers(1, 3))
                for _ in range(hops):
                    if self.sfx[q] <= 0:
                        break
                    q = self.sfx[q]
            syms = list(self.fwd[q].keys())
            if not syms:                        # dead state -> reset to root
                q = 0
                syms = list(self.fwd[q].keys())
            if not syms:
                break
            counts = np.array([len(self.fwd[q][s]) for s in syms], dtype=float)
            sym = syms[int(rng.choice(len(syms), p=counts / counts.sum()))]
            q = rng.choice(self.fwd[q][sym])    # oracle-weighted target selection
            out.append(sym)
        return out


# --- demo: improvise a new melody from a tiny reference ----------------------
if __name__ == "__main__":
    # reference: (midi pitch, duration in ticks) — a 2-bar cantus
    corpus = [(60, 480), (62, 480), (64, 960), (62, 480), (60, 1920),
              (67, 480), (64, 480), (62, 480), (60, 960), (62, 1920)]
    fo = FactorOracle(corpus)
    gen = fo.improvise(n_steps=48, p_recomb=0.30, seed=7)
    print("reference :", corpus)
    print("improvized:", gen)
```

## 9. Pitfalls

1. **Verbatim replay**: $p_{recomb} = 0$ just echoes the source — keep $p_{recomb} \in [0.2, 0.45]$ and allow multi-hop jumps so *distant* repeated contexts (not only adjacent ones) get spliced.
2. **Dead ends**: reset to the root (or climb the suffix chain) when $\delta(q) = \emptyset$; never emit a run of silence.
3. **Sparse/staccato output**: a sparse reference improvises gap-filled textures (the 011/032 failure mode) — add a continuous fill layer (026 DPSM arpeggios, sustained pad, walking bass).
4. **Narrow/atonal corpus**: the oracle cannot leave the corpus pitch set, so off-key notes never happen — but a narrow corpus stays narrow. Pre-quantize or post-run through 022 MCWS when tonal gravity is required.
5. **Symbol blowup**: interleaving many voices multiplies the alphabet geometrically and thins statistics. Cap the shared oracle at ~4 voices, or use per-voice oracles + a chord-label oracle.
6. **Section bleed-through**: without section tokens the walk drifts across section boundaries mid-section. Use section-conditioned oracles or a section-id token.

## 10. References

- Allauzen, C., Crochemore, M., and Raffinot, M. (1999). "Factor oracle: a new structure for pattern matching." *SOFSEM'99*, LNCS 1725, pp. 295–310.
- Assayag, G., and Dubnov, S. (2004). "Using Factor Oracles for Machine Improvisation." *Soft Computing* 8(9), pp. 604–610.
- Assayag, G., Bloch, G., Chemillier, M., Cont, A., and Dubnov, S. (2006). "OMax brothers: a dynamic topology of agents for improvisation learning." *Proc. ACM Workshop on Audio and Music Computing Multimedia*, Santa Barbara.
- Dubnov, S., Assayag, G., and El-Yaniv, R. (1998). "Universal classification applied to musical sequences." *Proc. ICMC*, Ann Arbor.
- Lefebvre, G., and Lecroq, T. (2002). "A Heuristic for Computing Repeats with a Factor Oracle: Application to Biological Sequences." *RAIRO Theoretical Informatics and Applications* 36(2).
- Cont, A., Assayag, G., and Dubnov, S. (2007). "Guided improvisation as dynamic calls to an offline model." *Sound and Music Computing (SMC)*.