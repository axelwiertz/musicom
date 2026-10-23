# Method 123 — Game-Theoretic Best-Response Composition (GTBRC)

**Paradigm:** Rules-Based (strategic) · **Layer:** concrete · **ID:** 123 · **Date:** 2026-10-23

> Treat the UnitMatrix as a non-cooperative game. Rows are players, columns are
> rounds, cells are outcomes. Each voice owns a private utility (tessitura, density,
> distance from the chord) and pays a congestion cost for sharing a
> (register band × metric slot) resource. The cost structure makes the game an
> **exact potential game**, so best-response dynamics is a descent on a scalar
> potential: it always terminates at a pure Nash equilibrium, and the potential
> recorded along the way *is* the tension curve.

---

## 1. The object

A composition is a tuple $\mathcal{G} = \langle V, \{S_i\}, \{c_i\} \rangle$ with

- players $i = 1..V$ — the **voices** (UnitMatrix rows);
- resources $r = (b,t) \in B \times T$ — a register band crossed with a metric slot;
  $R = \lvert B \rvert \lvert T \rvert$ of them;
- pure strategies $s_i \in S_i$, each a finite subset of resources plus a pitch class
  per resource: $s_i = \{(r_1, \pi_1), \dots, (r_m, \pi_m)\}$;
- loads $n_r(s) = \lvert\{ j : r \in s_j \}\rvert$;
- costs

$$c_i(s) \;=\; \mathrm{priv}_i(s_i) \;+\; \sum_{r \in s_i} c_r\bigl(n_r(s)\bigr),
\qquad c_r(k) = w_1 k + w_2 k^2 .$$

The private term is the voice's own taste:

$$\mathrm{priv}_i(s_i) \;=\; \alpha\,\lvert b(s_i) - h_i \rvert \;+\; \beta\,\lvert m - \mu_i \rvert \;+\; \gamma\,\#\{\text{non-chord tones in } s_i\},$$

with $h_i$ the home band, $\mu_i$ the preferred density and $\gamma$ the strength of
tonal gravity. **Tonality is an incentive, not a constraint** — voice $i$ seeks the
chord because seeking it pays.

This is exactly Rosenthal's (1973) congestion game: costs are separable per resource
and depend on the resource only through its load.

## 2. The potential theorem

Define

$$\Phi(s) \;=\; \sum_i \mathrm{priv}_i(s_i) \;+\; \sum_{r} \sum_{k=1}^{n_r(s)} c_r(k).$$

**Claim (exactness).** For all $i$, all $s_{-i}$ and all $s_i, s_i'$:

$$c_i(s_i, s_{-i}) - c_i(s_i', s_{-i}) \;=\; \Phi(s_i, s_{-i}) - \Phi(s_i', s_{-i}).$$

*Proof sketch.* Only player $i$'s own set changes, so the private sums cancel. For a
resource $r \in s_i' \setminus s_i$ the load rises from $n$ to $n+1$ and $\Phi$ gains
$c_r(n+1)$, which is exactly the term $c_i$ gains; for $r \in s_i \setminus s_i'$ the
load falls from $n$ to $n-1$, $\Phi$ loses $c_r(n)$ and so does $c_i$. Resources
outside $s_i \cup s_i'$ are untouched. Both sides telescope. $\square$

**Corollary 1 (finite improvement property).** Any sequence of strict unilateral
improvements strictly decreases $\Phi$; $\Phi$ is bounded below on the finite strategy
space, so no improving sequence can cycle, and every maximal sequence ends at a pure
Nash equilibrium (Monderer & Shapley 1996, Thm 3.1 in the reverse direction).

**Corollary 2 (termination bound).** With rational payoffs of denominator $L$, every
strict improvement lowers $\Phi$ by at least $1/L$, so the number of improving moves is
at most $L\,(\Phi(s^0) - \Phi_{\min})$, hence polynomial in the input size. Measured:
≤5 moves, ≤5 sweeps, in every one of 380 runs.

**Corollary 3 (tension curve).** The sequence $\Phi(s^{(0)}) > \Phi(s^{(1)}) > \dots >
\Phi(s^{\mathrm{NE}})$ is generated for free by the composition process and is a
Lyapunov function of it — a tension curve with a dynamical meaning rather than a
stylistic one.

## 3. Solution concepts (the method's parameter space)

| concept | rule | guarantee | musical use |
|---|---|---|---|
| **pure best response** | $s_i \leftarrow \arg\min c_i(\cdot, s_{-i})$ in seeded random order | terminates at pure NE (FIP) | default; crisp, deterministic texture |
| **fictitious play** (Brown 1951) | best-respond to the empirical frequency of others' past play | converges in zero-sum (Robinson 1951); converges to the NE set in potential games | development across repeats of a section |
| **logit / quantal response** (McKelvey–Palfrey 1995) | $P(s_i) \propto \exp(-\lambda\, c_i(s_i,s_{-i}))$ | statistical equilibrium; $\lambda\to\infty$ ⇒ best response | risk / rubato dial; measured entropy 9.940 → 3.807 nats for $\lambda = 0 \to 20$ |
| **correlated equilibrium** (Aumann 1974; Hart–Mas-Colell 2000) | public signal ("conductor") + regret matching | no player wants to deviate given the signal | force a specific verticality; removes coordination failure |
| **zero-sum minimax** (von Neumann 1928) | LP over mixed strategies | value exists; no pure NE in general | Xenakis *Duel*: two voices in opposition |

The correlated-equilibrium LP, for reference, maximises the players' weighted payoff
over distributions $p$ on profiles subject to obedience:

$$\max_{p \ge 0,\ \sum_s p(s) = 1} \sum_s p(s) \sum_i u_i(s)
\quad\text{s.t.}\quad
\sum_{s_{-i}} p(s_i, s_{-i})\bigl[u_i(s_i', s_{-i}) - u_i(s_i, s_{-i})\bigr] \le 0
\;\;\forall i, s_i, s_i' .$$

## 4. Price of anarchy

$$\mathrm{PoA} \;=\; \frac{\max\{\Phi(s) : s \text{ is a pure NE}\}}{\min_{s} \Phi(s)} .$$

Measured on 12-strategy catalogues by exhaustive enumeration of all $12^V$ profiles:

| config | resources | pure NE found | $\Phi(\mathrm{OPT})$ | PoA worst | PoA mean |
|---|---|---|---|---|---|
| 4 voices, 4 bands × 16 slots | 64 | 45 | 18.00 | 1.000 | 1.000 |
| 2 voices, 3 bands × 8 slots | 24 | 15 | 9.00 | 1.000 | 1.000 |
| 3 voices, 3 bands × 8 slots | 24 | 30 | 13.50 | 1.000 | 1.000 |
| 4 voices, 3 bands × 8 slots | 24 | 69 | 18.00 | **1.083** | 1.027 |
| 3 voices, 2 bands × 8 slots, $w_2{=}3$ | 16 | 20 | 25.50 | 1.000 | 1.000 |
| 4 voices, 2 bands × 8 slots, $w_2{=}3$ | 16 | 40 | 34.00 | 1.000 | 1.000 |

Decentralisation costs at most 8.3 % on the crowded configuration and nothing at all
when registers are plentiful or congestion is steep enough to make the optimum unique.
That is the honest reading: PoA ≈ 1 means **the game is too cooperative to generate
friction**; if audible tension is wanted, raise $w_2$ or switch to the zero-sum variant.

## 5. Musical mapping

| game object | musical object |
|---|---|
| player $i$ | voice $i$ (row) |
| round $t$ | section $t$ (column) |
| resource $(b,t)$ | register band × metric slot — "where an onset may go" |
| strategy $s_i$ | one gesture (rhythm + register + pitch classes) |
| load $n_r$ | doubling / masking at that band-slot |
| private term | tessitura, density taste, tonal attraction |
| convex congestion $w_2 k^2$ | pressure toward hocket / register separation |
| potential $\Phi$ | harmonic-tension energy of the whole texture |
| equilibrium | the stable sonority the section resolves to |
| payoff change at a seam | modulation / new formal unit |
| price of anarchy | "individualism" of the texture |

## 6. Python implementation sketch

```python
import random

def build(bands, slots, voices, chord, seed):
    rng, res, out = random.Random(seed), [], []
    idx = {(b, t): b * slots + t for b in range(bands) for t in range(slots)}
    for v in range(voices):
        home, pool = v, []
        for _ in range(12):
            band = max(0, min(bands - 1, home + rng.choice([-1, 0, 0, 1])))
            n = rng.choice([2, 3, 4, 4, 5])
            sl = sorted(rng.sample(range(slots), n))
            pcs = [rng.choice(chord) if rng.random() > .15
                   else (rng.choice(chord) + rng.choice([1, 2])) % 12 for _ in sl]
            priv = 2.0 * abs(band - home) + abs(n - 4) + 2.0 * sum(p not in chord for p in pcs)
            pool.append((frozenset(idx[(band, t)] for t in sl), tuple(pcs), band, sl, priv))
        out.append(pool)
    return out

def loads(prof, nres):
    L = [0] * nres
    for st in prof:
        for r in st[0]:
            L[r] += 1
    return L

def cost(i, prof, st, nres, w1=1.0, w2=1.5):
    L = loads([p for j, p in enumerate(prof) if j != i], nres)   # exclude mover
    return st[4] + sum(w1 * (L[r] + 1) + w2 * (L[r] + 1) ** 2 for r in st[0])

def potential(prof, nres, w1=1.0, w2=1.5):
    phi = sum(st[4] for st in prof)
    for k in loads(prof, nres):
        for j in range(1, k + 1):
            phi += w1 * j + w2 * j * j
    return phi

def best_response(S, rng, nres, max_sweeps=500):
    prof, curve = [rng.choice(S[i]) for i in range(len(S))], []
    curve.append(potential(prof, nres))
    for _ in range(max_sweeps):
        moved = False
        order = list(range(len(S))); rng.shuffle(order)
        for i in order:
            cur, bc, best = prof[i], cost(i, prof, prof[i], nres), prof[i]
            for s in S[i]:
                if s is cur:
                    continue
                c = cost(i, prof, s, nres)
                if c < bc - 1e-12:
                    best, bc = s, c
            if best is not cur:
                prof[i] = best; moved = True
                curve.append(potential(prof, nres))   # ← the tension curve
        if not moved:
            break
    return prof, curve
```

Realisation into the engine (`_unit_from_events` pads the terminal landmark so the
zero-drift gate passes even when a voice rests at the end of a section):

```python
for k, t in enumerate(slots):
    start = t * EIGHTH
    nxt = slots[k + 1] * EIGHTH if k + 1 < len(slots) else SECTION_LEN
    ev.append(MusicEvent(pitch=BASE[band] + pcs[k], volume=80,
                         start_tick=start, end_tick=start + min(nxt - start, 4 * EIGHTH)))
composer.fill_voice_section(name, section, _unit_from_events(ev, SECTION_LEN))
```

## 7. Verification (real runs)

`projects/Research/outputs/gtbrc_validate/gtbrc_verify.py`:

```
runs=200  potential-decrease violations=0        (all 380 runs: 0 violations)
terminated at pure Nash equilibrium: 200/200     (30/30 in each of 6 configs)
sweeps to convergence: mean 2.05  max 3
improving moves: mean 3.1  max 5
profiles enumerated=20736  pure NE count=45  PoA worst 1.000
max per-resource load: equilibrium 1.00  random 1.43 / 1.87 / 2.13 (V=3/4/5)
logit entropy: lambda 0 -> 9.940 nats, lambda 20 -> 3.807 nats
```

`projects/Research/outputs/gtbrc_validate/gtbrc_demo.py` (through the musicom engine):

```
section A: sweeps=2  Phi 46.0 -> 36.5   (2 improving moves)
section B: sweeps=2  Phi 53.5 -> 29.5   (4)
section C: sweeps=2  Phi 48.5 -> 29.5   (4)
section D: sweeps=4  Phi 53.5 -> 29.5   (4)
validate: True OK
midi gtbrc_demo.mid bytes=494 notes=38 duration=20.0s
preflight_check.py: COMPLIANT
```

## 8. Pitfalls

1. Exactness is fragile: a single pairwise (interval-consonance) term destroys it and
   best response can cycle. The verifier's own first version had an off-by-one in the
   load and produced 0/200 equilibria and 500 576 potential violations — the test
   (`assert ΔΦ == Δc_i` on every move) is the only reliable guard.
2. Equilibrium is only as musical as the payoff.
3. Multiple equilibria (45–69 in the demos) break literal repetition unless the start
   profile and seed are pinned.
4. $w_2 = 0$ collapses to unison (max load jumps to the random baseline).
5. Use correlated equilibrium when the section must land on one verticality.
6. Zero-sum has no potential: solve by LP or fictitious play, never naive best response.
7. Grid-locked by construction — humanise afterwards, never inside the payoff.
8. Tie-breaking must be seeded and epsilon-guarded.
9. Enumerating equilibria is $\mathcal{O}(\lvert S \rvert^V)$ — exhaustive only for $V \le 4$.

## 9. References

von Neumann & Morgenstern (1944) *Theory of Games and Economic Behavior*; Nash (1950,
1951); Brown (1951); Robinson (1951); Rosenthal (1973) *IJGT* 2:65–67; Aumann (1974)
*JME* 1:67–96; McKelvey & Palfrey (1995) *GEB* 10:6–38; Monderer & Shapley (1996)
*GEB* 14:124–143; Koutsoupias & Papadimitriou (1999) *STACS*; Hart & Mas-Colell (2000)
*Econometrica* 68:1127–1150; Fudenberg & Levine (1998); Roughgarden (2005); Young
(2004); Shoham & Leyton-Brown (2009). Musical: Xenakis (1971) *Formalized Music*
(*Duel* 1959, *Strategie* 1959–62); Huron (2006) *Sweet Anticipation*; Lerdahl (2001)
*Tonal Pitch Space*.
