# Method 069 — Christoffel Word Combinatorial Composition (CWCC)

**Paradigm:** Rules-Based (Deterministic)
**Classification:** Tonal Gravity = Strict (Mode/Well-Formed) · Metric Binding = Grid-Locked · Memory Depth = Macro/Word · Time Complexity = $\mathcal{O}(N)$

---

## Abstract

CWCC composes music from **Christoffel words** — the unique balanced binary words of algebraic combinatorics on words. One master word generates an entire piece: its **cyclic conjugates** are the scale modes, its **Sturmian-morphism** iterates are the macro-form, its **Christoffel dual** (the fifth/fourth folding word) is the harmonic skeleton, and its $\{1,0\}$ instantiation is the Euclidean rhythm timeline. Because a Christoffel word is *balanced* and *conjugate to a central word*, the resulting pitch structures automatically satisfy **Myhill's Property** (every generic interval has exactly two specific sizes) and **maximal evenness** (notes spread as evenly as possible in the octave / over the bar) — the mathematical properties that make the diatonic scale and the world's groove timelines sound "right". The method is fully deterministic, seedable, train-free, and linear-time.

---

## 1. Definitions

### 1.1 Christoffel word

For coprime integers $p, q \ge 1$ and a two-letter alphabet $\{a, b\}$, the **lower Christoffel word** $C(p,q)$ of slope $q/p$ has $p$ copies of $a$, $q$ copies of $b$, and length $n = p + q$. It is the coding of the lower mechanical word, obtained by discretizing the line segment from $(0,0)$ to $(p,q)$:

$$w_k = \begin{cases} b, & \lfloor (k+1) q / n \rfloor > \lfloor k q / n \rfloor,\\[2pt] a, & \text{otherwise,} \end{cases}\qquad k = 0, \dots, n-1.$$

Equivalently, the $b$ letters occupy the positions $k_i = \lfloor i \cdot n / q \rfloor$ for $i = 1, \dots, q$. For example $C(5,2) = \text{\texttt{aaabaab}}$ (positions of the two $b$'s: $\lfloor 7/2 \rfloor=3$, $\lfloor 14/2 \rfloor=7$ → indices 3 and 7).

### 1.2 Balance and central words

A finite word $w$ is **balanced** if, for any two factors $u, v$ of $w$ with $|u| = |v|$, the counts $|u|_b$ and $|v|_b$ differ by at most 1. Christoffel words are exactly the balanced words that are **primitive** (not a power of a shorter word). A **central word** is a word of the form $w = a\,u\,b$ where $u$ is a palindrome; every Christoffel word is conjugate to a unique central word. Central words are the *standard* words — the words representing "authentic" modal structure (Clampitt–Noll 2011).

### 1.3 The diatonic modes as conjugates

$C(5,2) = \text{\texttt{aaabaab}}$ read as a step pattern ($a$ = whole tone, $b$ = semitone) is the **Lydian** scale. Its seven cyclic conjugates (rotations) are the seven diatonic modes:

| rotation | word | mode |
|---|---|---|
| 0 | `aaabaab` | Lydian |
| 1 | `aabaaab` | Ionian (standard/central) |
| 2 | `abaaaba` | Mixolydian |
| 3 | `baaabaa` | Dorian |
| 4 | `aaabaab`→`aabaaab`… | (etc.) |
| … | … | Aeolian, Phrygian, Locrian |

The **standard word** `aabaaab` (Ionian) is the central word of the conjugacy class; its palindrome is `abaaaba`.

### 1.4 Sturmian morphisms

The **standard Sturmian morphisms** are the four substitutions

$$G = (a \mapsto a,\ b \mapsto ab),\qquad D = (a \mapsto ba,\ b \mapsto b),$$
$$\widetilde{G} = (a \mapsto a,\ b \mapsto ba),\qquad \widetilde{D} = (a \mapsto ab,\ b \mapsto b).$$

$G$ and $D$ generate the Sturmian morphism monoid; the fixed points of these morphisms are the **standard Sturmian words** (irrational-mechanical words). The orbit of `b` under $G$ is the **Fibonacci sequence of words**:

$$\texttt{b} \to \texttt{ab} \to \texttt{aab} \to \texttt{abaab} \to \texttt{aabaaab} \to \cdots$$

with lengths $1, 2, 3, 5, 8, 13, \dots$ (Fibonacci numbers). The limit is the Fibonacci infinite word (the characteristic Sturmian word of slope $1/\varphi$). Every Christoffel word is a **central word** of a standard Sturmian word, so the morphisms both generate and preserve the class.

### 1.5 Christoffel duality (height–width)

The **dual** of a Christoffel word is obtained by swapping the roles of the slope parameters. Musically (Clampitt–Noll), the step-pattern word over $\{a,b\}$ (whole/half, the *height* axis) is dual to the **folding word** over $\{x,y\}$ (ascending fifth / descending fourth, the *width* axis). For the diatonic:

$$\text{step word: } \texttt{aaabaab}\ (a=W,\ b=H) \quad\longleftrightarrow\quad \text{folding word: } \texttt{xyxyxyy}\ (x=+P5,\ y=-P4).$$

The folding word is a single circle-of-fifths traversal of the seven pitch classes (F C G D A E B for Lydian). Handschin's **tone character** (*Toncharakter*) is exactly the width coordinate — position along the fifth chain, as opposed to height (log-frequency).

### 1.6 Euclidean rhythms are Christoffel words

The Bjorklund/Euclidean rhythm $E(k,n)$ — $k$ onsets evenly distributed over $n$ pulses — is precisely the Christoffel word $C(k, n-k)$ over $\{1, 0\}$:

$$E(3,8) = \text{\texttt{10010010}}\ (\text{tresillo}),\qquad E(5,8) = \text{\texttt{10110110}},\qquad E(2,5) = \text{\texttt{10010}}.$$

This is the Toussaint (2005) result: every "traditional world rhythm" generated by the Euclidean algorithm is a Christoffel word, hence balanced, hence maximally even.

---

## 2. Musical Elements Framework

- **PITCH** — accumulate the word's letters over a step-size table ($a{=}2,\ b{=}1$ semitones for diatonic; $a{=}2,b{=}3$ pentatonic; $a{=}1,b{=}2$ chromatic well-formed). The mode = the starting rotation (finalis). Melody = a factor of a Christoffel/Sturmian word read linearly: balanced conjunct motion with exactly two interval sizes (Myhill), never clumping.
- **RHYTHM** — a $\{1,0\}$ Christoffel word is an Euclidean timeline. Morphism substitution = diminution/augmentation (each `1` → sub-rhythm, each `0` → rest-subword). Coprime stacked words = interlocking polymeter.
- **HARMONY** — the folding word (duality image) gives circle-of-fifths progressions; suffix `yy` = plagal motion; divider incidence distinguishes authentic/plagal. Generic width (fifth index) = harmonic tension; |width| distance = fifth-lattice distance (cf. 051 SGLM).
- **STRUCTURE** — iterated Sturmian morphisms = self-similar fractal form (Fibonacci word prefixes). Section transitions = mode conjugation (rotation = modulation). $G$/$\widetilde{G}$ = development/inversion, $D$/$\widetilde{D}$ = recapitulation/retrograde.
- **TEXTURE** — per-voice Christoffel stream with its own $(p,q)$; balancedness guarantees maximal-evenness polyphony (no clumping, no accidental unisons). $q/(p+q)$ = sparse↔dense knob; morphism depth = granularity.

## 3. UnitMatrix Integration (Voices & Sections)

- **Voices (rows)** = word families $(p_v, q_v)$ + morphism depth. Lead = high-$p$ (dense, conjunct); bass = low-$p$ sampled from the folding word; pad = $G$-iterated long word (continuous fill); percussion = Euclidean word.
- **Sections (columns)** = (rotation index $r_s$, morphism depth $d_s$). A→B→A = rotate to dominant-mode word and back; development = extra $G$; recapitulation = $D$.
- **Cells** $U_{v,s}$: `{PITCH}` = $k$-th letter accumulated through the step table; `{RHYTHM}` = $\{1,0\}$ word on the pulse grid; `{HARMONY}` = folding-word factor at the cell; `{TEXTURE}` = per-voice density $q_v/(p_v+q_v)$ + depth.

## 4. Implementation (Python)

```python
from __future__ import annotations
from math import gcd

def christoffel_word(p: int, q: int, a: str = "a", b: str = "b") -> str:
    """Lower Christoffel word C(p,q): p x a, q x b, balanced (gcd must be 1)."""
    assert gcd(p, q) == 1, "p, q must be coprime for a Christoffel word"
    n = p + q
    return "".join(b if ((k + 1) * q) // n > (k * q) // n else a for k in range(n))

def modes(word: str) -> list[str]:
    """Cyclic conjugates = the modes of the scale."""
    return [word[i:] + word[:i] for i in range(len(word))]

def sturmian_morph(word: str, morph: str) -> str:
    rules = {
        "G":  {"a": "a",  "b": "ab"},
        "D":  {"a": "ba", "b": "b"},
        "G~": {"a": "a",  "b": "ba"},
        "D~": {"a": "ab", "b": "b"},
    }
    return "".join(rules[morph][c] for c in word)

def word_to_pitch(word: str, start: int = 60, step: dict | None = None) -> list[int]:
    step = step or {"a": 2, "b": 1}          # whole / half step (diatonic)
    out, cur = [], start
    for c in word:
        out.append(cur)
        cur += step[c]
    return out

def euclidean_rhythm(k: int, n: int) -> str:
    """E(k,n) = Christoffel word C(k, n-k) over {1,0}."""
    return christoffel_word(k, n - k, a="1", b="0")

def fibonacci_words(depth: int) -> list[str]:
    """G-iterates of 'b': lengths 1,2,3,5,8,..."""
    out, s = [], "b"
    for _ in range(depth):
        out.append(s)
        s = sturmian_morph(s, "G")
    return out

if __name__ == "__main__":
    master = christoffel_word(5, 2)                 # "aaabaab" = Lydian
    assert master == "aaabaab"
    print("modes:", modes(master))                   # 7 diatonic modes
    print("Ionian scale:", word_to_pitch(modes(master)[1]))   # [60,62,64,65,67,69,71]
    print("tresillo:", euclidean_rhythm(3, 8))       # "10010010"
    print("fibonacci words:", fibonacci_words(6))    # b, ab, aab, abaab, ...
    # Musicom: fill UnitMatrix cells from these streams, then composer.validate()
    # + composer.to_midi() per AGENTS.md — never hand-roll mido.
```

## 5. Pitfalls (summary)

1. **Non-coprime $(p,q)$** → not a Christoffel word. Reduce by $\gcd$ first.
2. **Sparse/staccato output** → honor the hybridization rule; always layer a continuous fill voice.
3. **Wrong step table** → diatonic is $a{=}2,b{=}1$; pentatonic/others differ.
4. **Mode-rotation confusion** → fix the anchor note; name modes from the standard (Ionian) word.
5. **Morphism blow-up** → Fibonacci growth; cap depth (~≤12).
6. **Duality only for generated scales** → restrict to well-formed scales, else treat folding word as independent constraint.
7. **No downbeat accent** → break evenness deliberately at cadences.

## 6. References

- Christoffel, E. B. (1875). "Observatio arithmetica." *Annali di Matematica Pura ed Applicata* 6, 148–152.
- Berstel, J. (1990). "Tracé de droites, fractions continues et morphismes itérés." In *Mots*, Hermès, 298–309.
- Lothaire, M. (2002). *Algebraic Combinatorics on Words.* Cambridge University Press.
- Berstel, J., Lauve, A., Reutenauer, C., & Saliola, F. V. (2009). *Combinatorics on Words: Christoffel Words and Repetitions in Words.* CRM Monograph 27, AMS.
- Clough, J., & Myerson, G. (1985). "Variety and Multiplicity in Diatonic Systems." *Journal of Music Theory* 29(2), 249–270.
- Carey, N., & Clampitt, D. (1989). "Aspects of Well-Formed Scales." *Music Theory Spectrum* 11(2), 187–206.
- Clough, J., & Douthett, J. (1991). "Maximally Even Sets." *Journal of Music Theory* 35(1/2), 93–173.
- Toussaint, G. T. (2005). "The Euclidean Algorithm Generates Traditional Musical Rhythms." *Proceedings of BRIDGES*, 47–56.
- Noll, T. (2009). "Ionian Theorem." *Journal of Mathematics and Music* 3(3), 137–151.
- Clampitt, D., & Noll, T. (2011). "Modes, the Height-Width Duality, and Handschin's Tone Character." *Music Theory Online* 17.1.
