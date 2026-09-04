# Method 077 — De Bruijn Universal Cycle Composition (DBUC)

**Paradigm**: Rules-Based (deterministic combinatorial construction)
**Layer**: Concrete
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity**: Weak (Mode-pinned)
**Metric Binding**: Grid-Locked
**Memory Depth**: Local (Length-$k$ window)
**Time Complexity**: $\mathcal{O}(n^k)$

## One-line description
Generate music from a de Bruijn sequence $B(k,n)$ — a cyclic word of length $n^k$ over an $n$-symbol alphabet whose every length-$k$ window appears exactly once — decoded into pitch (scale-degree alphabet), rhythm (binary hit alphabet), harmony (chord-symbol alphabet), structure (Hamiltonian/Eulerian cycle + Lyndon-word blocks), and texture (de Bruijn tori + offset voices). Maximal variety with zero verbatim repetition.

---

## Extended Mathematics

### Definition
A **de Bruijn sequence** $B(k, n)$ over an alphabet $\Sigma$ ($|\Sigma| = n$) is a cyclic word of length $n^k$ in which every word of length $k$ over $\Sigma$ occurs exactly once as a contiguous cyclic window. It exists for every $n, k \ge 1$. The number of distinct de Bruijn sequences is

$$\frac{(n!)^{n^{k-1}}}{n^k}.$$

**Binary example** ($n=2, k=3$): $B(3,2) = 00010111$. Sliding a length-3 window around it cyclically yields $000, 001, 010, 101, 011, 111, 110, 100$ — all 8 binary triples exactly once.

### de Bruijn graph
The de Bruijn graph $G(n, m)$ has $n^m$ vertices (all words of length $m$) and $n^{m+1}$ directed edges; an edge $(u, v)$ is labeled by the length-$(m{+}1)$ word $u[0]\, v[m{-}1]$. Then:

- A **Hamiltonian cycle** in $G(n, k{-}1)$ is a de Bruijn sequence $B(k, n)$.
- An **Eulerian circuit** in $G(n, k{-}2)$ is a de Bruijn sequence $B(k{-}1, n)$.

So $B(k,n)$ is simultaneously "visit every length-$(k{-}1)$ state exactly once" (macro-form path) and "traverse every length-$(k{-}1)$ transition exactly once" (event stream).

### Lyndon words and the FKM / Duval algorithm
A **Lyndon word** over an ordered alphabet is a nonempty word strictly smaller than all of its non-trivial rotations — the lexicographically minimal representative of an *aperiodic necklace*. The **lexicographically minimal** de Bruijn sequence $B(k, n)$ is the concatenation, in lexicographic order, of all Lyndon words over $\Sigma$ whose length divides $k$:

$$B(k,n) \;=\; \bigoplus_{\substack{w \text{ Lyndon over }\Sigma \\ |w| \,\mid\, k}} w \qquad(\text{lexicographic order}).$$

The **Duval (FKM) algorithm** enumerates these Lyndon words in $\mathcal{O}(n^k)$ total time with $\mathcal{O}(n)$ space (linear in output, constant extra). This is the basis of the implementation sketch.

### Higher-dimensional generalization: de Bruijn tori
A **de Bruijn torus** $B(k, n; d)$ is a $d$-dimensional cyclic array in which every $k$-cube sub-array over $\Sigma$ appears exactly once. The $d=2$ case is a time×voice texture where every $k{\times}k$ patch is unique. Slices of the torus supply per-voice streams; the $d{=}1$ case is the ordinary sequence.

### Exhaustiveness / anti-repetition trade-off
Where the Thue–Morse sequence (076) is *overlap-free* (avoids $XXX$), the de Bruijn sequence is *exhaustive*: it contains **every** length-$k$ factor exactly once, so it maximizes pattern diversity subject to a fixed window length while still guaranteeing **no verbatim length-$k$ repetition** (each window occurs once). The two are complementary extremal cases of "structured aperiodicity."

### Alphabet permutation invariance
Any permutation $\pi$ of $\Sigma$ applied to a de Bruijn sequence yields another (generally distinct) de Bruijn sequence. This is the mechanism for per-voice and per-section variation without losing the exhaustive property — a palette of distinct-but-related exhaustive streams over one pitch-class set.

---

## Python implementation sketch

```python
from __future__ import annotations

def lyndon_words(n: int, k: int):
    """Enumerate Lyndon words over {0..n-1} (Duval/FKM), words of length <= k."""
    w = [-1]
    while w:
        w[-1] += 1
        yield list(w)                       # w is a Lyndon word here
        m = len(w)
        while len(w) < k:                   # periodic extension (Duval)
            w.append(w[len(w) - m])
        while w and w[-1] == n - 1:         # backtrack
            w.pop()

def debruijn_sequence(n: int, k: int) -> list[int]:
    """Lexicographically minimal B(k, n): concat Lyndon words of length | k."""
    out = []
    for w in lyndon_words(n, k):
        if k % len(w) == 0:
            out.extend(w)
    return out

def debruijn_torus_rows(n: int, k: int, rows: int) -> list[list[int]]:
    """2D torus slice: offset copies of B(k,n) (approximate torus)."""
    seq = debruijn_sequence(n, k)
    return [seq[(i * k) % len(seq):] + seq[:(i * k) % len(seq)] for i in range(rows)]

def permuted_stream(seq: list[int], perm: list[int], offset: int = 0):
    """Apply a symbol permutation and phase offset to a de Bruijn stream."""
    L = len(seq)
    for i in range(L):
        yield perm[seq[(i + offset) % L]]
```

**Musicom integration** (engine authors the MIDI; sketch only — real imports per `AGENTS.md`):
```python
# from structures import UnitMatrix, MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=len(voice_specs), num_sections=len(section_specs))
# for v, (alphabet, order, offset, perm, clock) in enumerate(voice_specs):
#     composer.add_voice(f"V{v}", program=..., channel=v)
#     seq = debruijn_sequence(len(alphabet), order)
#     for s, (block_start, block_len) in enumerate(section_specs):
#         composer.add_section(f"S{s}", bars=...)       # once, outside voice loop
#         for j in range(block_len):
#             idx = (offset + block_start + j) % len(seq)
#             sym = perm[seq[idx]]                       # per-voice relabel
#             pitch = alphabet[sym]                      # degree/chord -> pitch
#             composer.fill_voice_section(v, s, create_note_unit(pitch, dur, tick))
# ok, msg = composer.validate()    # MUST be True before to_midi (per AGENTS.md)
```

---

## References
- Flye Sainte-Marie, C. (1894). "Question 48." *L'Intermédiaire des Mathématiciens* 1, 107–110.
- de Bruijn, N. G. (1946). "A combinatorial problem." *Proc. Koninklijke Nederlandse Akademie van Wetenschappen* 49, 758–764.
- van Aardenne-Ehrenfest, T., & de Bruijn, N. G. (1951). "Circuits and trees in oriented linear graphs." *Simon Stevin* 28, 203–217.
- Lyndon, R. C. (1954). "On Burnside's problem." *Transactions of the American Mathematical Society* 77, 202–215.
- Fredricksen, H., & Maiorana, J. (1978). "Necklaces of beads in k colors and k-ary de Bruijn sequences." *Discrete Mathematics* 23, 207–210.
- Duval, J.-P. (1983). "Factorizing words over an ordered alphabet." *Journal of Algorithms* 4(4), 363–381.
- Fredricksen, H., & Kessler, I. J. (1986). "An algorithm for generating necklaces of beads in two colors." *Discrete Mathematics* 61, 181–188.
- Knuth, D. E. (2011). *The Art of Computer Programming*, Vol. 4A, §7.2.1.1. Addison–Wesley.
- Nierhaus, G. (2009). *Algorithmic Composition: Paradigms of Automated Music Generation*. Springer.
