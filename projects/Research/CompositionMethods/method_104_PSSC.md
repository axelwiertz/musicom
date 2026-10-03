# Method 104: Parsimonious Subset Sequence Composition (PSSC)

**ID:** 104  
**Acronym:** PSSC  
**Layer:** abstract  
**Paradigm:** Rules-Based  
**Primary Elements:** Pitch, Harmony, Structure, Texture

---

## Overview

Parsimonious Subset Sequence Composition (PSSC) generalises the classical Neo-Riemannian parsimonious voice-leading concept (P/L/R operations on triads) to **any n-subsets of any p-scale**, constructing chord progressions where successive chords differ by exactly one pitch class.

Developed by Hugues Bedouelle (2023–2025), the method provides a complete mathematical framework for designing **exhaustive, non-redundant, circular (nrep) sequences** of n-chord progressions from any parent scale. The 2024 extension adds **inversion bipartition**: when the parent scale is invariant under a musical inversion, the n-chords split into two complementary parsimonious strands.

PSSC operates at the **abstract layer**: it designs pitch-class subset sequences without specifying concrete register, duration, or dynamics. Its output feeds the concrete layer via `rules/subset_network.py` for voicing, rhythm, and register assignment.

---

## Mathematical Foundation

### Three Fundamental Relations

Let **C** be the set of all unordered pitch-class sets in 12-TET. For n-chords A, B (subsets of a parent p-scale S):

| Relation | Symbol | Definition |
|----------|--------|------------|
| **Parsimonious** | **Rp** | A Rp B iff ∃ (n−1)-chord C such that C ⊆ A and C ⊆ B. Equivalently, A and B share exactly n−1 pitch classes. |
| **Equivalence** | **Re** | A Re B iff ∃ transformation F ∈ {Tₙ, TₙI} such that A = F(B). (Forte's set-class relation.) |
| **Fuzzy** | **Rf** | A Rf B iff ∃ transformation F such that either F(A) Rp B or A Rp F(B). (Composition of parsimony and equivalence.) |

**Proposition 5.1** (Bedouelle 2023): All three relations Rp, Re, Rf are **compatible with any musical transformation** F ∈ {Tₙ, TₙI}. Applying F to every chord in a parsimonious/mild/fuzzy progression preserves the property. This creates a 48-form symmetry group: {direct, retrograde, inverted, retrograde-inverted} × 12 transpositions.

### Intervallic Guarantee

Two n-chords related by Rp share at least (n−2)/n of their interval content — e.g., tetrachords in Rp share ≥50% of their interval-class vectors.

---

## The 2D Table Representation

The n-chords of a p-scale are arranged in a table:

- **Rows** labelled by (n−1)-chord subsets: all chords in a row share the same (n−1)-subset and are pairwise in Rp.
- **Columns** labelled by set-class (Forte number): all chords in a column are pairwise in Re (equivalent under Tₙ/TₙI).

Two chords in different columns are in Rf iff they form an **orthogonal triangle** with a third chord at the row/column intersection.

**Mild progressions** follow edges within rows only (parsimony) or within columns only (equivalence), never crossing diagonals.

---

## Exhaustive Non-Redundant Parsimonious (nrep) Sequences

### Central Result (Bedouelle 2023, Proposition 10.1)

For p-scales of cardinal p = 2..9 and n-chords of cardinal n = 2..5, there exists at least one sequence of n-chords that is simultaneously:

| Property | Meaning |
|----------|---------|
| **Parsimonious** | Every adjacent pair is in Rp (differs by 1 pitch class) |
| **Exhaustive** | Every possible n-chord of the p-scale appears at least once |
| **Non-Redundant** | Each n-chord appears exactly once |
| **Circular** | First and last chords are also in Rp (loopable) |

### Construction Algorithm

Given a p-alphabet Uₚ (totally ordered set of p letters) and target n-word cardinality:

1. **Generate**: All C(n,p) n-words of Uₚ in lexicographic order.
2. **Partition**: Split by last letter into p−n+1 subsequences X_{n,i} (i = n..p).  
   Card(X_{n,i}) = C(n,i) − C(n,i−1).
3. **Walk**: For each X_{n,i}, construct a parsimonious walk Y_{n,i}:
   - Start from the first n-word; proceed stepwise while Aⱼ Rp Aⱼ₊₁ holds.
   - When broken, jump to the nearest reachable n-word within X_{n,i}.
   - The walk may proceed in either index direction.
4. **Concatenate**: Link Y_{n,i} and Y_{n,i+1} in alternating direct/retrograde order:
   - **Method Z'** (circular when i is odd):  
     Y_{n,n} → Y'_{n,n+1} → Y_{n,n+2} → Y'_{n,n+3} → ...
   - **Method Z"** (circular when i is even):  
     Y_{n,n} → Y_{n,n+1} → Y'_{n,n+2} → Y_{n,n+3} → ...
5. **Map**: Substitute letters with pitch classes via bijection from Uₚ to the normal-form ordered pc-set of the chosen p-scale.

### Example (Bedouelle 2023, Example 10.1)

For the minor hexachord [0,2,3,5,7,9] (Forte 6-33, p=6, n=4 tetrachords): the construction yields a circular nrep progression of all 15 tetrachords. Its 48-form family (direct, retrograde, inverted, retrograde-inverted × 12 Tₙ) generates 720 permutations for the hexatonic case.

---

## Inversion Bipartition (Bedouelle 2024 Extension)

When the p-scale S satisfies **I(S) = S** for some inversion I (true for whole-tone, octatonic, hexatonic, and many other symmetric scales), the set of n-chords **bipartitions** into two non-redundant parsimonious sequences:

- **Strand A**: One half of the n-chord set, forming a complete nrep sequence.
- **Strand B**: The image of Strand A under I — also nrep, and complementary.

Key properties:
- Strands are parsimoniously connected at the fixed points of I.
- Total progression length = 2 × C(n,p)/2 = C(n,p), same as before.
- Each strand can be assigned to a different voice for natural two-voice counterpoint.

---

## Musical Elements Framework

### PITCH
The core domain. n-chords are pitch-class subsets of a parent p-scale. The Rp relation ensures single-pc changes between successive chords, generating smooth stepwise voice-leading in the chromatic subset space. The 2D table rows capture maximum parsimony; columns capture set-class invariance. Chord quality and interval-class-vector identity are inherited from Forte set-class assignments (columns).

### RHYTHM
Not directly specified at the abstract layer. The nrep sequence imposes a natural ordering — each chord in the progression maps to one or more time slots in the UnitMatrix. The rhythm layer (concrete) assigns durations per chord: chords may be isochronous (one cell per chord), variable-length (weighted by interval vector or inversion state), or subdivided across beats.

### HARMONY
The primary output. The nrep progression **is** a harmonic plan: a sequence of pitch-class subsets that exhaustively explores the harmonic resources of the chosen p-scale. Since each step changes exactly one pc, the voice-leading between successive chords is maximally smooth. The fuzzy relation Rf bridges set-class boundaries, enabling local modulatory moves. The 48-form symmetry gives the composer enormous flexibility.

### STRUCTURE
Macro-form arises from how the circular nrep sequence is segmented across sections:
- Single circular pass = one large section
- Sequence partitioned across multiple columns (sections) of the UnitMatrix
- Alternating direct/retrograde strands across voices = canon-like relationships
- Inversion-bipartition yields paired strands for binary (A/B) form
- Transposition blocks create section boundaries

### TEXTURE
Chord cardinality n controls density: n=2 (dyadic), n=4 (tetrachordal), n=6 (hexachordal saturation). The alternating direct/retrograde concatenation pattern creates natural registral arcs (direct = expanding, retrograde = contracting) when mapped to register in the concrete layer.

---

## UnitMatrix Integration

### Voices (Rows)
Each voice carries a strand of the nrep sequence:
- Voice 1 = direct progression Z' or Z"
- Voice 2 = retrograde of Voice 1
- Voice 3 = inverted (TₙI) of Voice 1
- Voice 4 = retrograde-inverted of Voice 1

For the inversion-bipartition case: Voice 1 = Strand A, Voice 2 = Inversion of Strand A (Strand B).

### Sections (Columns)
The nrep sequence is divided across sections:
- Each section = k consecutive chords from the circular nrep progression
- Section transitions at natural breakpoints (joints between X_{n,i} subsequences)
- A circular sequence naturally maps to a repeat of the form

### Cells (MusicUnit)
Each cell receives one n-chord from the nrep sequence. The concrete layer (realization) then voices the chord (spread across registers), assigns duration/rhythm, sets dynamics/velocity, and applies ornamentation via `rules/realize.py`.

---

## Complexity

**Time:** O(C(n,p) · p) for constructing the nrep sequence (the lexicographic generation + walk).  
**Space:** O(C(n,p)) for storing the sequence.  
**Scale:** C(4,7) = 35 tetrachords for heptatonic scales; C(4,12) = 495 for dodecaphonic. The method is feasible for p ≤ 10; beyond that, use scale-degree subsets to reduce cardinality.

---

## Python Implementation Sketch

```python
from typing import List, Tuple, Set
from itertools import combinations

# --- Core relations ---

def parsimonious(A: Set[int], B: Set[int]) -> bool:
    """Rp relation: A and B share exactly card-1 elements."""
    if len(A) != len(B):
        return False
    return len(A & B) == len(A) - 1

def equivalent(A: Set[int], B: Set[int], p: int = 12) -> bool:
    """Re relation: A is Tn/TnI of B."""
    A_norm = tuple(sorted(A))
    for t in range(p):
        trans = {(x + t) % p for x in B}
        if tuple(sorted(trans)) == A_norm:
            return True
        inv = {(-x + t) % p for x in B}
        if tuple(sorted(inv)) == A_norm:
            return True
    return False

# --- Sequence construction ---

def nwords_of_alphabet(p_alphabet: int, n: int) -> List[Tuple[str, ...]]:
    """Generate all n-words of a p-alphabet (letters a,b,c,...) in lexicographic order."""
    letters = [chr(ord('a') + i) for i in range(p_alphabet)]
    return [tuple(c) for c in combinations(letters, n)]

def partition_by_last_letter(words: List[Tuple[str, ...]]) -> dict:
    """Partition words by their last letter."""
    groups = {}
    for w in words:
        key = w[-1]
        if key not in groups:
            groups[key] = []
        groups[key].append(w)
    return groups

def make_parsimonious_walk(subseq: List[Tuple[str, ...]]) -> List[Tuple[str, ...]]:
    """Construct a parsimonious walk through a subsequence (not guaranteed optimal)."""
    used = set()
    result = []
    current = 0
    direction = 1
    while len(used) < len(subseq):
        if current in used:
            # jump to next unused
            candidates = [i for i in range(len(subseq)) if i not in used]
            if not candidates:
                break
            current = candidates[0]
            direction = 1 if current < len(subseq) - 1 else -1
        used.add(current)
        result.append(subseq[current])
        # look ahead in current direction
        next_i = current + direction
        if 0 <= next_i < len(subseq) and next_i not in used and parsimonious(set(subseq[current]), set(subseq[next_i])):
            current = next_i
        else:
            # try opposite direction
            direction *= -1
            next_i = current + direction
            if 0 <= next_i < len(subseq) and next_i not in used and parsimonious(set(subseq[current]), set(subseq[next_i])):
                current = next_i
            else:
                # random-ish jump
                remaining = [i for i in range(len(subseq)) if i not in used and i != current]
                if remaining:
                    current = remaining[0]
                else:
                    break
    return result

def build_nrep_sequence(p: int, n: int) -> List[Tuple[str, ...]]:
    """Build a non-redundant exhaustive parsimonious sequence for p-alphabet, n-words."""
    words = nwords_of_alphabet(p, n)
    partition = partition_by_last_letter(words)
    # Build per-group walks
    keys = sorted(partition.keys())
    walks = []
    for i, k in enumerate(keys):
        walk = make_parsimonious_walk(partition[k])
        if i % 2 == 1:  # alternate retrograde
            walk = list(reversed(walk))
        walks.append(walk)
    # Concatenate
    result = []
    for w in walks:
        result.extend(w)
    return result
```

---

## References

- Bedouelle, H. (2023). "Exhaustive chord progressions and their use in music composition." *Journal of Mathematics and Music* 18(1), 42–60. DOI: [10.1080/17459737.2023.2166136](https://doi.org/10.1080/17459737.2023.2166136)
- Bedouelle, H. (2024). "Parsimonious sequences of pitch-class sets: bipartition through inversion and its applications to music composition." *Journal of Mathematics and Music* 19, 108–121. DOI: [10.1080/17459737.2024.2432901](https://doi.org/10.1080/17459737.2024.2432901)
- Bedouelle, H. (2025). "A post-tonal method of music composition." HAL hal-05425426.
- Forte, A. (1973). *The Structure of Atonal Music.* Yale University Press.
- Callender, C., Quinn, I. & Tymoczko, D. (2008). "Generalized voice-leading spaces." *Science* 320, 346–348.
- Cohn, R. (1997). "Neo-Riemannian operations, parsimonious trichords and their Tonnetz representations." *Journal of Music Theory* 41(1), 1–66.

---

## Candidate Code Path

The abstract-layer implementation lives in:
- `rules/subset_network.py` — PatternSequence, ParsimoniousSequence, nrep_construction, InversionBipartition
- `rules/set_theory.py` — core Forte prime/normal forms, ICV, which PSSC calls for set-class labelling

The concrete realization (voices, registers, durations) feeds through:
- `rules/realize.py` — `realize_progression(nrep_sequence, ...)` → `MusicEvent[]`
- `generators/pssc_generator.py` — generator module (optional, can delegate to existing generators)

---

## Pitfalls

1. **Combinatorial explosion**: C(n,p) grows quickly. For p > 10 or n near p/2, sequences are impractically long. Use scale-degree labels instead of raw pc-sets to cap cardinality.
2. **Rhythm not specified**: PSSC provides harmonic substrate only. Pair with 012 Euclidean, 069 CWCC, or another rhythm method.
3. **No register**: Chord voicings must be assigned by the concrete layer (default: close position within vocal range).
4. **Tonal gravity not inherent**: nrep sequences are tonally neutral. Filter to chords containing tonic/dominant for tonal music, or choose a scale with strong tonic bias.
5. **Inversion-invariant scales only for bipartition**: The 2024 bipartition requires I(S) = S. Asymmetric scales use the general 2023 construction.
6. **Table row order not unique**: Multiple nrep sequences exist for the same (p, n). The composer may need to evaluate candidates by musical criteria.