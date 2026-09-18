# Method 090 — Golomb Ruler Distinct-Difference Composition (GRDC)

- **Paradigm:** Rules-Based
- **Layer:** concrete (SCALE L3 onset-lattice / L2 pitch-pool; feeds `generators/`)
- **Elements:** Pitch, Rhythm, Harmony, Structure, Texture
- **Tonal Gravity:** Weak (ICV-invariant pool)
- **Metric Binding:** Grid-Locked
- **Memory Depth:** Macro / Ruler Span
- **Complexity:** $\mathcal{O}(S \cdot m^2)$ search, $\mathcal{O}(m^2)$ verify

## Extended Math

**Golomb ruler.** $G=\{g_0<\dots<g_{m-1}\}\subset\mathbb{Z}_{\ge0}$ with
$g_j-g_i=g_l-g_k \Rightarrow (i,l)=(j,k)$. Length $L=g_{m-1}$; optimal $L^*(m)$ known to $m\approx28$ ($L^*(5)=11,\ L^*(6)=17,\ L^*(7)=25,\ L^*(8)=34$). Counting bound (Shearer):
$$L \;\ge\; \tfrac{1}{2}m^2 - O(m),$$
because the $\binom{m}{2}$ distinct differences must fit into $[1,L]$.

**Finite Sidon set.** $S\subset\mathbb{Z}_n$, $|S|=m$, all *modular* differences distinct ⇒ $m(m-1)\le n-1$; Bose–Chowla constructs $|S|=\lfloor\sqrt{n}\rfloor$ for prime powers $n$; Ruzsa gives density $\approx\sqrt{N}$ in $[1,N]$. In $\mathbb{Z}_{12}$ this is exactly a pitch-class set with interval vector entries $\le 1$ (checked with the IC kernel, not raw linear differences — interval *class* folds $d$ with $12-d$).

**All-interval example.** $m{=}4$: $\{0,1,4,6\}$, ICV $=[1,1,1,1,1,1]$ = Forte 4-Z15 (Z-partner 4-Z29) — every interval class exactly once.

**Onset-grid compression.** Ruler marks $g_i$ on span $L$ compressed into a window of $B$ pulses: $\theta_i=\lfloor g_i B/L\rfloor$; compression can *collide* marks (pigeonhole when $B < \binom{m}{2}\cdot 2$ margin) — assert $\theta$ injective, else widen $B$ (Shearer's bound tells you how much: $B\gtrsim m^2$).

**Composite ruler (harmony).** Voices carry rulers $G_1,\dots,G_V$; the verticality union $U=\bigcup_v (G_v + t_v)$ has duplicate-difference count
$$\kappa = \binom{|U|}{2} - \bigl|\{\,g_j-g_i : g_i,g_j\in U,\ i<j\,\}\bigr| \ge 0,$$
with $\kappa=0$ (Sidon union) = maximum-interval-variety sonority, $\kappa>0$ = duplicated intervals = tension scalar.

## Python implementation sketch

```python
from itertools import combinations

def is_golomb(marks):
    d = sorted(b - a for a, b in combinations(marks, 2))
    return all(d[k] != d[k + 1] for k in range(len(d) - 1))

def golomb_backtrack(order, length, seed_marks=(0,)):
    """Exact search with symmetry breaking (g0=0, ceil L via caller)."""
    marks = list(seed_marks)
    def diffs():
        return {b - a for a, b in combinations(marks, 2)}
    def rec(limit):
        if len(marks) == order:
            return list(marks)
        for cand in range(marks[-1] + 1, limit + 1):
            new_d = {cand - g for g in marks}
            if not (new_d & diffs()):          # distinct-difference prune
                marks.append(cand)
                r = rec(limit)
                if r: return r
                marks.pop()
        return None
    for L in range(sum(range(order)), length + 1):   # lower bound ~ m^2/2
        r = rec(L)
        if r: return r
    return None

def sidon_icv_pool(size, modulus=12, trials=20000, seed=0):
    import random
    rng = random.Random(seed); best = []
    for _ in range(trials):
        cand = sorted(rng.sample(range(modulus), size))
        icv = [0] * 6
        for a, b in combinations(cand, 2):
            icv[min((b - a) % modulus, (a - b) % modulus) - 1] += 1
        if max(icv) <= 1 and len(cand) > len(best):
            best = cand
    return best

def golomb_onsets(marks, window_pulses):
    L = marks[-1]
    theta = [g * window_pulses // L for g in marks]
    assert len(set(theta)) == len(theta), "compression collision — widen window"
    return theta

# UnitMatrix wiring (sanctioned workflow only):
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=3, num_sections=4)
# composer.add_voice("Lead", program=..., channel=0)
# composer.add_section("A", bars=2)
# pool = sidon_icv_pool(5)                       # e.g. [0,1,4,9,11]-type
# for on, g in zip(golomb_onsets([0,1,4,10,12,17], 16), range(6)):
#     tick = on * 480; pitch = 60 + pool[g % len(pool)]
#     composer.fill_voice_section("Lead", "A", create_note_unit(pitch, 480))  # etc.
# ok, msg = composer.validate()                   # zero-drift gate
# composer.to_midi("out.mid")
```

## References

- Golomb, S. W. (1972). "How to number a graph." In *Graph Theory and Computing*, pp. 23–37. Academic Press.
- Babcock, W. C. (1953). "Intermodulation interference in radio systems." *Bell Syst. Tech. J.* 32(1): 63–73.
- Bloom, G. S., & Golomb, S. W. (1977). *Comm. ACM* 20(2): 92–94.
- Shearer, J. B. (1998). "Some new optimum Golomb rulers." *IEEE Trans. Inf. Theory* 44(2): 778–782.
- Dimitromanolakis, A. (2002). *Analysis of the Golomb Ruler and the Sidon Sequence Problems*. DTU dissertation.
- Sidon, S. (1932). *Math. Annalen* 106; Erdős & Turán (1941). *J. London Math. Soc.* 16: 212–215.
- Bose, R. C., & Chowla, S. (1962). *Comment. Math. Helv.* 37: 141–147.
- Ruzsa, I. Z. (1993). *Acta Arithmetica* 65.
