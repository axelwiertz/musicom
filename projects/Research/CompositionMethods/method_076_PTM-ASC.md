# Method 076 — Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC)

**Paradigm**: Rules-Based (deterministic substitution)
**Layer**: Concrete
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity**: Weak (Scale-mapped)
**Metric Binding**: Grid-Locked
**Memory Depth**: None (Self-similar recurrence)
**Time Complexity**: $\mathcal{O}(N)$

## One-line description
Generate music from the Thue–Morse automatic sequence $t(n)=s_2(n)\bmod 2$ (substitution $0{\to}01$, $1{\to}10$): bits map to pitch intervals/onset patterns, Prouhet's equal-power partition gives balanced multi-voice harmony, and self-similarity plus overlap-freeness yields non-repeating, recursively nested macro-form.

---

## Extended Mathematics

### Definition
The Thue–Morse sequence $t = (t(n))_{n\ge 0}$ over $\{0,1\}$ is defined by

$$t(n) = s_2(n) \bmod 2,$$

where $s_2(n)$ is the number of 1-bits in the binary expansion of $n$ (the base-2 digit sum). Equivalently,

$$t(n) = \frac{1}{2}\Big(1 - (-1)^{s_2(n)}\Big).$$

The first 16 terms: $t = 0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0$.

### Substitution (morphism) fixed point
$t$ is the unique fixed point (starting from 0) of the uniform length-2 morphism

$$\sigma:\; 0 \mapsto 01,\quad 1 \mapsto 10.$$

Level $k$ is $\sigma^k(0)$, of length $2^k$, and satisfies the complement-concatenation recursion

$$\sigma^k(0) \;=\; \sigma^{k-1}(0)\; \overline{\sigma^{k-1}(0)},$$

where $\overline{\cdot}$ is bitwise complement. Levels:
- $t_0 = 0$
- $t_1 = 01$
- $t_2 = 0110$
- $t_3 = 01101001$
- $t_4 = 0110100110010110$

### Recurrence (no lookback)
$$t(2n) = t(n), \qquad t(2n+1) = 1 - t(n).$$
The whole sequence is a pure function of the index — "memory depth = none" in the true sense; there is no context window, only the self-similar recurrence.

### Overlap-freeness / cube-freeness (Thue 1906, 1912)
$t$ contains no factor of the form $aXaXa$ (where $a$ is a symbol and $X$ any word, possibly empty) — i.e. no *overlap*, hence no cube $XXX$ (three consecutive equal blocks). This is the strongest possible non-repetition property for an infinite binary word: it is "apart from nothing" reproducible while never literally repeating a block three times.

### Balance / equidistribution
Every factor of even length $2m$ contains exactly $m$ ones and $m$ zeros:

$$\big|\{i : t(i)=1,\; i \in [a, a{+}2m)\}\big| = m \quad \forall a, m.$$

In particular $t$ has uniform symbol frequency $1/2$ — it is a *perfectly balanced* aperiodic word (the aperiodic limit of the Euclidean-rhythm family).

### Prouhet–Tarry–Escott partition (Prouhet 1851)
For $k \ge 1$ define
$$S_k = \{\,n < 2^k : t(n) = 0\,\}, \qquad T_k = \{\,n < 2^k : t(n) = 1\,\}.$$
Then $|S_k| = |T_k| = 2^{k-1}$, and for every $0 \le j < k$,

$$\sum_{n \in S_k} n^{j} \;=\; \sum_{n \in T_k} n^{j}.$$

That is, the two index sets are indistinguishable by any power-sum of degree $< k$. Musically this yields a *balanced multi-voice split*: assign the $n$-th note (in any sorted pitch list) to voice A iff $t(n)=0$, else voice B — the two voices then agree on mean, variance, skewness, kurtosis, …, up to order $k-1$.

### Generalized ($p$-ary) Thue–Morse
For a base $p \ge 2$ and target modulus $p$,

$$t_p(n) \;=\; \sum_{i} d_i \pmod p \quad\text{where } n = \sum_i d_i p^i.$$

$t_p$ is a balanced $p$-ary word (each of the $p$ symbols appears with frequency $1/p$ on even blocks), giving $p$-voice equal-power partitions. $t_2 = t$. The $t_p$ family supplies the texture palette (base = number of concurrent independent voices).

### Automaticity
$t$ is **2-automatic**: there is a 2-state finite automaton reading the base-2 digits of $n$ (least significant first) that outputs $t(n)$. Consequently each bit is computable in $\mathcal{O}(1)$ — total $\mathcal{O}(N)$ for $N$ events.

### Turtle-geometry bridge (fractal form)
Driving a turtle with "turn left on 0, turn right on 1" traces the **Koch snowflake** (Jun, von Haeseler, Peitgen & Skordev 1987); the same self-similarity that tiles the snowflake is what nests the piece's form, and the fractal dimension of the curve is a single-number summary of structural/textural density.

---

## Python implementation sketch

```python
from __future__ import annotations

def thue_morse(n: int) -> int:
    """t(n) = parity of popcount(n). O(1) via bin().count."""
    return bin(n).count("1") & 1

def thue_morse_prefix(k: int) -> list[int]:
    """First 2**k symbols: substitution fixed point = w + complement(w)."""
    w = [0]
    for _ in range(k):
        w += [1 - b for b in w]
    return w

def generalized_thue_morse(n: int, base: int) -> int:
    """t_p(n) = base-p digit sum mod p."""
    s = 0
    while n:
        n, d = divmod(n, base)
        s += d
    return s % base

def prouhet_partition(notes: list[int]) -> tuple[list[int], list[int]]:
    """Split 2**k sorted notes into two equal-power voices by t(n)."""
    a = [p for n, p in enumerate(notes) if thue_morse(n) == 0]
    b = [p for n, p in enumerate(notes) if thue_morse(n) == 1]
    return a, b

def scale_walk(bit: int, scale_size: int = 7) -> int:
    """Bit -> +/- one scale degree (asymmetric map avoids mirror halves)."""
    return 1 if bit == 0 else 0   # +1 on 0, +0 on 1  -> drift bias, no strict mirror

class ThueMorseGenerator:
    """Deterministic generator: one stream per voice, one morphic level per section."""
    def __init__(self, base=2, offset=0):
        self.base, self.offset = base, offset

    def bits(self, k: int):
        """Yield 2**k bits for this stream (section of morphic level k)."""
        for i in range(1 << k):
            n = i + self.offset
            yield (thue_morse(n) if self.base == 2 else generalized_thue_morse(n, self.base))
```

**Musicom integration** (engine authors the MIDI; sketch only):
```python
# from structures import UnitMatrix, MusicUnit   # real imports per AGENTS.md
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=len(voice_specs), num_sections=len(section_specs))
# for v, (base, offset, mapping) in enumerate(voice_specs):
#     composer.add_voice(f"V{v}", program=..., channel=v)
#     gen = ThueMorseGenerator(base, offset)
#     for s, (k, _) in enumerate(section_specs):
#         composer.add_section(f"S{s}", bars=...)  # once, outside voice loop
#         for i, bit in enumerate(gen.bits(k)):
#             pitch = mapping[bit](scale_walk(bit))   # decode
#             composer.fill_voice_section(v, s, create_note_unit(pitch, 1920))
# ok, msg = composer.validate()   # MUST be True before to_midi
```

---

## References
- Prouhet, E. (1851). "Mémoire sur quelques relations entre les puissances des nombres." *Comptes Rendus de l'Académie des Sciences de Paris* 33, 225.
- Thue, A. (1906). "Über unendliche Zeichenreihen." *Norske Vid. Selsk. Skr. I. Mat. Nat. Kl. Christiana* 7, 1–22.
- Thue, A. (1912). "Über die gegenseitige Lage gleicher Teile gewisser Zeichenreihen." *Norske Vid. Selsk. Skr. I. Mat. Nat. Kl. Christiana* 1, 1–67.
- Morse, M. (1921). "Recurrent geodesics on a surface of negative curvature." *Transactions of the American Mathematical Society* 22(1), 84–100.
- Morse, M., & Hedlund, G. A. (1944). "Unending chess, symbolic dynamics and a problem in semigroups." *Duke Mathematical Journal* 11(1), 1–7.
- Allouche, J.-P., & Shallit, J. (2003). *Automatic Sequences: Theory, Applications, Generalizations*. Cambridge University Press.
- Jun, K.-S., von Haeseler, F., Peitgen, H.-O., & Skordev, G. (1987). "On self-similarity and the Koch curve." (Thue–Morse turtle/paperfolding connection.)
- Nierhaus, G. (2009). *Algorithmic Composition: Paradigms of Automated Music Generation*. Springer.
- Toussaint, G. T. (2013). *The Geometry of Musical Rhythm*. CRC Press.
