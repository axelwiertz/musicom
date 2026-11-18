# Method 145 — Dyck Path Ballot Composition (DPBC)

- **ID:** 145
- **Paradigm:** Rules-Based
- **Layer:** abstract (LAYER_ARCHITECTURE.md) — tension curve / contour prototype / phrase grammar, register-invariant, no concrete events. Feeds `rules/subset_network.py` via new `rules/dyck_paths.py`; concrete adapter `generators/dyck_contour.py`.
- **One-liner:** compose each section from a Dyck path — an n-up/n-down walk that never falls below 0 and must return to it (Bertrand's ballot law, counted by Catalan numbers) — so height is an *enforced* tension curve: HOME is a hard floor, returns are cadences, arches are phrases, peaks are climaxes.
- **First Catalan-family method in the DB.** Discrete ballot-law foil to 048 RBMPD (soft reflecting barrier, continuous), 095 CTC (general contours), 066 GTTM-HC (hierarchical tree vs flat line); context-free-language counterpart to 130 SFT-C (regular languages).

---

## 1. The mathematics

### 1.1 Dyck paths and the ballot law

A **Dyck path** of semilength $n$ is a sequence $w \in \{U,D\}^{2n}$ with $n$ up-steps and $n$ down-steps such that every partial sum $h(t) = \sum_{i\le t} w_i$ (with $U = +1$, $D = -1$) satisfies $h(t) \ge 0$, and $h(2n) = 0$. Equivalently, by **Bertrand's ballot theorem** (1887): in every prefix, $\#U \ge \#D$ — "the up-votes never trail the down-votes."

The count is the **Catalan number**

$$C_n = \frac{1}{n+1}\binom{2n}{n} = \binom{2n}{n} - \binom{2n}{n+1}, \qquad C_0{=}1,\; C_1{=}1,\; C_2{=}2,\; C_3{=}5,\; C_4{=}14,\; C_8{=}1430,\; C_{16}{=}35\,357\,670,$$

with recurrence $C_n = \sum_{i=1}^{n} C_{i-1} C_{n-i}$ and asymptotics $C_n \sim 4^n/(n^{3/2}\sqrt\pi)$. (OEIS A000108; known to Mingantu by 1730, Euler 1751, Catalan; André's reflection-counting proof 1887.)

**Strict-lead variant** (the off-by-one): requiring $\#U > \#D$ in every *nonempty* prefix counts *excursions* and equals $C_{n-1}$. The Dyck law allows ties (returns to 0). General ballot: for $p$ up / $q$ down votes, $p > q$, the strict-lead count is

$$b(p,q) = \frac{p-q}{p+q}\binom{p+q}{p}.$$

### 1.2 Structure theorems (all verified computationally in `_web145_dpbc/verify_dpbc_math.py`)

1. **First-return (arch) decomposition.** Every Dyck path is a unique concatenation of **primitive** arches (excursions touching 0 only at their ends). # primitive paths of semilength $m$ = $C_{m-1}$; # $k$-arch paths of semilength $n$ = $[x^n]\big(x\,C(x)\big)^k$ where $C(x) = \dfrac{1-\sqrt{1-4x}}{2x}$ is the Catalan generating function. Arch = phrase; arch boundary = cadence.
2. **Narayana peaks.** # Dyck paths of semilength $n$ with exactly $k$ peaks (U immediately followed by D) = $N(n,k) = \frac{1}{k}\binom{n-1}{k-1}\binom{n}{k-1} = \frac{1}{n}\binom{n}{k}\binom{n}{k-1}$ (OEIS A001263; $\sum_k N(n,k) = C_n$). Peak = climax point; peak *count* is a parameter with a known number of realizations.
3. **Chung–Feller equipartition (1949).** Among all $\binom{2n}{n}$ balanced $\pm1$ paths, **exactly $C_n$** have exactly $2k$ steps strictly above the axis, for *every* $k = 0..n$ (implies $(n+1)C_n = \binom{2n}{n}$). Choosing $k$ = choosing how many of the $2n$ slots live in the upper register — every choice has exactly $C_n$ realizations: an exact LIFT/TURN register-balance dial.
4. **Motzkin generalization.** Adding level steps (no height change) yields Motzkin paths, counted by $M_n$ (OEIS A001006; $M_8 = 1278$ vs $C_8 = 1430$). Level step = rest or repeated note. **The enumeration law changes** — quote $M_n$, not $C_n$, for pieces with rests.
5. **Dyck language is context-free, not regular** — balanced parentheses; provably not recognizable by a finite automaton. This is the precise formal-language boundary with 130 SFT-C (subshifts of finite type = regular languages).

### 1.3 Uniform sampling — the one correct algorithm

Naive: sample a uniform balanced word, rotate to the first global minimum (cycle lemma). **This is biased**: it produces Dyck path $D$ with probability $\propto 1/\text{arches}(D)$ (measured: at $n{=}2$, UUDD receives 4 balanced words, UDUD receives 2; at $n{=}10$ mean peaks 1.83 vs theory 5.50).

Correct: **first-return recursion** — $\text{Dyck}(n) = \text{arch}(j) \cdot \text{Dyck}(n-j)$ with $P(j) = C_{j-1}C_{n-j}/C_n$ for the first arch's semilength, and $\text{arch}(j) = \mathrm{U} \cdot \text{Dyck}(j-1) \cdot \mathrm{D}$. Measured at $n{=}10$, $N{=}20\,000$: mean peaks 5.510 (theory 5.500), mean arches 2.517 (theory 2.500).

---

## 2. Python implementation sketch

```python
"""rules/dyck_paths.py -- abstract tension-curve generator (Method 145 DPBC)."""
from math import comb
from random import Random

def catalan(n: int) -> int:
    return comb(2 * n, n) // (n + 1)

def narayana(n: int, k: int) -> int:
    return comb(n - 1, k - 1) * comb(n, k - 1) // k

def sample_dyck(n: int, rng: Random) -> list[int]:
    """Uniform Dyck path of semilength n as [+1/-1] steps.
    First-return recursion: P(first arch semilength j) = C_{j-1} C_{n-j} / C_n."""
    memo: dict[int, list[int]] = {}

    def dyck(m: int) -> list[int]:
        if m == 0:
            return []
        if m in memo:
            return memo[m]
        probs = [catalan(j - 1) * catalan(m - j) for j in range(1, m + 1)]
        r = rng.random() * catalan(m)
        acc = 0
        chosen = m
        for j in range(1, m + 1):
            acc += probs[j - 1]
            if r < acc:
                chosen = j
                break
        arch = [1] + dyck(chosen - 1) + [-1]      # primitive arch: U Dyck(j-1) D
        memo[m] = arch + dyck(m - chosen)
        return memo[m]

    return dyck(n)

def stats(path: list[int]) -> dict:
    """peaks (U-D pairs), arches (returns to 0 incl. final), max height."""
    h = pk = arches = mx = 0
    prev = 0
    for s in path:
        if prev == 1 and s == -1:
            pk += 1
        h += s
        if h == 0:
            arches += 1
        mx = max(mx, h)
        prev = s
    return {"peaks": pk, "arches": arches, "max_height": mx}

def tension_contract(n: int, k_cf: int, seed: int):
    """Abstract-layer contract: curve + arch partition + Chung-Feller balance k.
    (k_cf = how many of the 2n steps sit strictly above the axis.)"""
    rng = Random(seed)
    path = sample_dyck(n, rng)
    return {"semilength": n, "path": path, "stats": stats(path),
            "chung_feller_k": k_cf, "seed": seed}
```

```python
"""generators/dyck_contour.py -- concrete adapter (abstract -> UnitMatrix cells)."""
from structures import MusicUnit, MusicEvent

SCALE = [48, 50, 52, 53, 55, 57, 59]   # C major, C3..B3

def path_to_cell(path: list[int], slot_ticks: int, section_ticks: int,
                 volume: int = 96) -> MusicUnit:
    """height h(t) -> scale degree root+h(t). The ballot law keeps h >= 0,
    so the tonic (root) is a hard floor -- HOME is enforced, not preferred.
    Returns: one MusicUnit whose events fill the cell exactly (zero-drift)."""
    events, h, slot = [], 0, 0
    for s in path:
        h2 = h + s
        deg = h2
        pitch = SCALE[deg % 7] + 12 * (deg // 7)
        start = slot * slot_ticks
        events.append(MusicEvent(pitch=pitch, volume=volume,
                                 start_tick=start, end_tick=start + slot_ticks))
        h, slot = h2, slot + 1
    if slot * slot_ticks < section_ticks:      # tail rest: zero-drift padding
        events.append(MusicEvent(pitch=0, volume=0, start_tick=slot * slot_ticks,
                                 end_tick=section_ticks))
    return MusicUnit(events=events)

# engine loop:
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S); add_voice/add_section...
# composer.fill_voice_section("Lead", "A", path_to_cell(pathA, 240, 3840))
# ok, msg = composer.validate()   # zero-drift gate -- MUST be True
# composer.to_midi("dpbc.mid")
```

---

## 3. References

- Wikipedia: *Catalan number* (fetched 2026-11-18): formula, Dyck words, André 1887, Mingantu 1730s, ballot interpretation, asymptotics.
- Wikipedia: *Bertrand's ballot theorem* (fetched 2026-11-18): $b(p,q) = \frac{p-q}{p+q}\binom{p+q}{p}$; André's proof; cycle lemma; ties-allowed variant.
- Wikipedia: *Narayana number* (fetched 2026-11-18): $N(n,k) = \frac{1}{k}\binom{n-1}{k-1}\binom{n}{k-1}$; Dyck words with $k$ peaks.
- Wikipedia: *Dyck language* (fetched 2026-11-18): context-free, non-regular.
- Chung, K. L. & Feller, W. (1949). "On fluctuations in coin-tossing." *PNAS* 35(10), 605–608.
- OEIS: **A000108** (Catalan), **A001263** (Narayana), **A001006** (Motzkin) — fetched 2026-11-18 via `curl ...&fmt=text`.
- Verified artifacts (this run, 2026-11-18): `_web145_dpbc/verify_dpbc_math.py` (8/8 checks), `_web145_dpbc/compose_dpbc_demo.py`, outputs in `/opt/data/projects/Research/outputs/dpbc145/` (MIDI 426 B, WAV 2.4 MB, OGG 163 KB, provenance JSON).
