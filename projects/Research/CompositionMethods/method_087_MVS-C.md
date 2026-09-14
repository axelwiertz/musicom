# Multiple Viewpoint Systems Composition (MVS-C)

**Method ID**: 087
**Paradigm**: Stochastic
**Layer**: concrete (emits note/onset/duration events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/multiple_viewpoint.py`
**Acronym**: MVS-C

## One-line description

Composes by combining many specialized statistical predictors (viewpoints: pitch, pitch-interval, contour, scale-degree, onset-interval, duration, metric-position, chord — plus linked product viewpoints) into one product-of-experts distribution over the next event, then sampling or argmax-decoding it. Backoff with PPM* escape adapts context order automatically; a long-term corpus model (style) and a short-term within-piece model (structure/repetition) are blended in log space (IDyOM). Entropy-based viewpoint selection drops redundant features.

## Extended math

### The viewpoint ensemble

Let a musical surface be a sequence of events `e_1 … e_N`, each an attribute tuple. A **viewpoint** `τ` is a partial function `τ : E* → [τ]` from event histories to a feature value in a finite type `[τ]`. Each viewpoint carries an independent conditional estimator `P(τ(e_i) | h)`, where `h = e_1…e_{i−1}` is the history.

The ensemble prediction over the next event `x` is a normalized **product-of-experts**:

```
P(x | h) = (1/Z) · Π_{τ∈Φ} P(τ(x) | h)^{w_τ},      (1)
Z(h)     = Σ_{x} Π_{τ∈Φ} P(τ(x) | h)^{w_τ}
```

with `w_τ` the viewpoint weight and `Φ` the active viewpoint set. Composition draws `x ~ P(·|h)` (stochastic) or takes `x = argmax_x P(x|h)` (deterministic per seed).

### Backoff with escape (PPM*)

For a viewpoint with maximal context order `k` and actual matched context `h`:

```
P(τ|h) = c(τ,h)/T(h)                       if c(τ,h) > 0,
P(τ|h) = e(h) · P(τ|h′)                     otherwise,       (2)
```

where `h′` is the length-`|h|−1` suffix of `h`, `e(h)` the escape mass, `c(τ,h)` the count, `T(h) = Σ_τ c(τ,h)`. Standard PPM escape choices: **method A** `e(h) = 1/(T(h)+1)` (seen symbols `+1` each), **method C** `e(h) = u(h)/(T(h)+u(h))` with `u(h)` the number of distinct continuations, **method D (PPM*)** `e(h) = (u(h)/2)/T(h)`.

### LTM/STM blend (IDyOM)

Two model families, combined by a second product-of-experts:

```
log P(x|h) = α · log P_LTM(x|h) + (1−α) · log P_STM(x|h) − log Z,      (3)
```

`α ∈ [0,1]` the blend. LTM is corpus-trained and frozen during composition; STM is trained incrementally on the piece so far. Early (`t` small) the STM is near-uniform → LTM (style) dominates; later the STM's inflated counts on recurring motifs dominate → structure and recapitulation emerge without an explicit form model.

### Entropy-based viewpoint selection (Conklin 1995)

Viewpoints are ranked by held-out cross-entropy `H(τ) = −(1/M) Σ log P(τ(e_i)|h_i)` over a held-out set; only the `k` lowest-entropy (most informative) viewpoints survive. Correlated viewpoints (pitch vs scale-degree vs interval) are pruned to a single representative so the product in (1) does not double-count evidence.

### Complexity

- Amortized (hash/trie indexed fixed-order counts): `O(N · k)` for `N` events and `k` active viewpoints.
- Naive per-step scan over the type alphabet: `O(N · k · V)` with `V = max_τ |[τ]|` (linked viewpoints are the big `V`).
- LTM training: `O(C · k)` over corpus size `C`.
- Log-space throughout; normalizer `Z` via log-sum-exp (guards underflow, shared with 086 HMM-C).

## Python implementation sketch

```python
"""Multiple Viewpoint Systems Composition (Method 087, MVS-C).

Each viewpoint is a fixed-order counter with PPM* escape; the ensemble is a
log-space product-of-experts. LTM = corpus-trained, STM = piece-incremental.
The musicom engine (UnitMatrixComposer) authors the MIDI — this module only
produces (pitch, onset, duration) event tuples. Deterministic per seed.
"""
import math
from collections import defaultdict


class ViewpointModel:
    """Fixed-order count model with PPM* (method-D) escape."""
    def __init__(self, max_order, escape="D"):
        self.max_order = max_order
        self.escape = escape
        # context (tuple, order o) -> counter of continuation -> count
        self.counts = defaultdict(lambda: defaultdict(int))
        self.total = defaultdict(int)

    def observe(self, ctx, sym):
        for o in range(min(len(ctx), self.max_order), -1, -1):
            h = tuple(ctx[-o:]) if o else ()
            self.counts[h][sym] += 1
            self.total[h] += 1

    def prob(self, ctx, sym):
        for o in range(min(len(ctx), self.max_order), -1, -1):
            h = tuple(ctx[-o:]) if o else ()
            T = self.total[h]
            if T == 0:
                continue
            c = self.counts[h].get(sym, 0)
            if c > 0:
                u = len(self.counts[h])
                e = (u / 2.0) / T if self.escape == "D" else 1.0 / (T + 1)
                return (1 - e) * c / T
            # escape: carry (1-e) mass down to shorter context
        return 1e-9  # fully unseen -> tiny floor


def _viewpoint_feature(kind, ctx, x):
    """Decode a candidate event x into this viewpoint's feature."""
    if kind == "pitch":
        return x[0]
    if kind == "interval":
        return x[0] - ctx[-1][0] if ctx else 0
    if kind == "contour":
        d = x[0] - ctx[-1][0] if ctx else 0
        return 1 if d > 0 else (-1 if d < 0 else 0)
    if kind == "scale_degree":
        return x[0] % 12
    if kind == "ioi":
        return x[1]  # onset tick delta
    if kind == "duration":
        return x[2]
    if kind == "metric":
        return x[3]  # beat position in bar
    raise KeyError(kind)


class MultipleViewpointComposer:
    def __init__(self, viewpoints, alpha=0.5, seed=0):
        import random
        self.viewpoints = viewpoints        # list of (kind, weight)
        self.alpha = alpha                  # LTM blend
        self.ltm = {k: ViewpointModel(3) for k, _ in viewpoints}
        self.stm = {k: ViewpointModel(3) for k, _ in viewpoints}
        self.history = []                   # list of (pitch, onset, dur, metric)
        self.rng = random.Random(seed)

    def train_ltm(self, event_seq):
        ctx = []
        for e in event_seq:
            for k, _ in self.viewpoints:
                self.ltm[k].observe(ctx, _viewpoint_feature(k, ctx, e))
            ctx.append(e)

    def _log_prob(self, x):
        ctx = self.history
        lp = 0.0
        for k, w in self.viewpoints:
            f = _viewpoint_feature(k, ctx, x)
            lp_ltm = math.log(self.ltm[k].prob(ctx, f))
            lp_stm = math.log(self.stm[k].prob(ctx, f))
            lp += w * (self.alpha * lp_ltm + (1 - self.alpha) * lp_stm)
        return lp

    def predict(self, candidates):
        """Return normalized distribution over candidate events."""
        lps = [self._log_prob(x) for x in candidates]
        m = max(lps)
        z = math.log(sum(math.exp(lp - m) for lp in lps)) + m
        return [math.exp(lp - z) for lp in lps]

    def compose_next(self, candidates, mode="sample"):
        probs = self.predict(candidates)
        if mode == "argmax":
            x = candidates[max(range(len(candidates)), key=lambda i: probs[i])]
        else:
            r = self.rng.random()
            acc = 0.0
            x = candidates[-1]
            for c, p in zip(candidates, probs):
                acc += p
                if r <= acc:
                    x = c
                    break
        for k, _ in self.viewpoints:
            f = _viewpoint_feature(k, self.history, x)
            self.stm[k].observe(self.history, f)
        self.history.append(x)
        return x


# --- Musicom integration (engine authors the MIDI) ---
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# mvs = MultipleViewpointComposer(viewpoints=[("pitch",1.0),("interval",0.7),
#                                             ("scale_degree",0.9),("metric",0.8)],
#                                 alpha=0.5, seed=7)
# mvs.train_ltm(corpus_events)
# for cell in cells:
#     x = mvs.compose_next(candidates, mode="sample")
#     composer.fill_voice_section(voice, section, create_note_unit(x[0], x[2]))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References

- Conklin, D., & Witten, I. H. (1995). "Multiple Viewpoint Systems for Music Prediction." *Journal of New Music Research* 24(1), 51–73.
- Cleary, J. G., & Witten, I. H. (1984). "Data Compression Using Adaptive Coding and Partial String Matching." *IEEE Transactions on Communications* 32(4), 396–402.
- Conklin, D. (2003). "Music Generation from Statistical Models." *Proc. AISB Symposium on AI and Creativity in the Arts and Sciences*, Aberystwyth.
- Pearce, M. T. (2005). "The Construction and Evaluation of Statistical Models of Melodic Structure in Music Perception and Composition." PhD thesis, Department of Computing, City University London.
- Pearce, M. T., & Wiggins, G. A. (2006). "Expectation in Melody: The Influence of Context and Learning." *Music Perception* 23(5), 377–405.
- Pearce, M. T., Ruiz, M. H., Kapasi, S., Wiggins, G. A., & Bhattacharya, J. (2010). "Unsupervised Statistical Learning Underpins Computational, Behavioural, and Neural Manifestations of Musical Expectation." *NeuroImage* 50(1), 302–313.
