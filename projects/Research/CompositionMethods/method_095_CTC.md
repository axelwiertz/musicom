# Method 095 — Contour Theory Composition (CTC)

**Acronym**: CTC
**Paradigm**: Rules-Based
**Layer**: abstract
**Status**: Registered

---

## 1. Theoretical Foundation

Contour Theory (Friedmann 1985; Marvin & Laprade 1987; Morris 1993) provides a framework for analyzing and generating musical lines based on their **shape** — the pattern of rising, falling, and repeating between successive pitches — independent of exact interval sizes or pitch-class content. The key insight: listeners recognize melodies primarily by contour, not by exact intervals (Dowling 1978).

### Core Definitions

**Contour Point (CP)**: A pitch ordered in time, abstracted as its rank. For a sequence of $n$ pitches, the lowest is assigned rank 0, the next rank 1, ..., the highest rank $n-1$.

**Comparison Function** (Friedmann 1985):
$$
\text{CMP}(a,b) = 
\begin{cases}
+ & \text{if } b > a \\
0 & \text{if } b = a \\
- & \text{if } b < a
\end{cases}
$$

**Contour Adjacency Series (CAS)** (Marvin & Laprade 1987): A string of $n-1$ symbols from $\{+, -, 0\}$ encoding only the direction between adjacent contour points. Example: for pitches [C4, E4, D4, G4]:
- Ranks: [0, 2, 1, 3] (lowest=0)
- CAS: `< + - + >`

**Combinatorial Contour**: The full $n \times n$ self-comparison matrix of all pairwise CMP relations (upper triangle). Two contours with the same matrix belong to the same **contour class**.

**Contour Segment (CSeg)** (Morris 1993): A normalized sequence of contour ranks $[r_0, r_1, ..., r_{n-1}]$ where $r_i$ is the rank of the $i$-th point. Example: CSeg `<0 2 1 3>` means the sequence rises (0→2), falls (2→1), rises again (1→3).

**Contour Class**: Equivalence class closed under:
- **Transposition (T)**: Adding a constant to all ranks (renormalization)
- **Inversion (I)**: $r_i \rightarrow (n-1) - r_i$ (flips all directions)
- **Retrograde (R)**: $r_i \rightarrow r_{n-1-i}$ (reverses the sequence)
- **Retrograde-Inversion (RI)**: Both R then I

### Contour Reduction (Morris 1993)

An algorithm that extracts the structural skeleton: given a contour of length $n$, remove interior points that do not change the large-scale shape. Specifically:

1. Classify each point as **embellishing** or **structural** using the rule: a point $p_i$ is embellishing if removing it does not change the CAS of the reduced contour.
2. Apply recursively until only the essential turning points remain.
3. The resulting multi-level reduction is analogous to Schenkerian middleground but operating on pure shape.

### Contour Similarity Metrics

From the literature (Sampaio 2018):

| Algorithm | Acronym | Description | Complexity | Length Constraint |
|:---|:---|:---|:---|:---|
| Rigid Matrix | CSIM | Pairwise matrix comparison | $\mathcal{O}(n^2)$ | Same length only |
| Embedded Contour | EMB | Shared CSeg subsequences | $\mathcal{O}(C(n,m))$ | Any length |
| Correspondence | COR | CAS symbol matching | $\mathcal{O}(n)$ | Same length |
| Oscillation Spectrum | OSC | Fourier contour spectrum | $\mathcal{O}(n \log n)$ | $n \geq 6$ |
| Fuzzy | — | Membership in contour set | $\mathcal{O}(n^2)$ | Any length |

---

## 2. Method Workflow

### Phase A (Abstract Layer — this method)

```
Input:  Section plan (keys, bar counts per section)
        ContourVocabulary (library of CSeg prototypes)
        Transformation weights (p(I), p(R), p(RI))

Step 1: For each section s, select a CAS template
        — Rising:  + + + + +        (many +)
        — Falling: - - - - -        (many -)
        — Arch:    + + - - -        (rise→fall)
        — Valley:  - - + + +        (fall→rise)
        — Oscillating: + - + - +    (alternating)
        — Chaotic: random ± at given entropy

Step 2: For each voice v in section s, assign a CSeg length L_vs
        (typically 3-7 points, Miller's law ~7±2)

Step 3: Generate or select a CSeg of length L_vs
        — From the vocabulary by CAS matching
        — Via I/R/RI transformation of a seed CSeg
        — Via Morris reduction of a longer parent CSeg

Step 4: Apply transformation with probability p:
        — I: invert the CSeg
        — R: retrograde the CSeg  
        — RI: both
        — Identity: keep as-is

Step 5: Output = ContourProgression
        A sequence of (CSeg, section_id, voice_id, transform) tuples.

Step 6: Compute contour-tension curve per section:
        — T_1 = number of CAS direction changes (peak count)
        — T_2 = max CAS run length (sustained rise = building)
        — T_3 = CAS entropy H = -∑ p(±) log p(±)
        — T_total = w_1 T_1 + w_2 T_2 + w_3 T_3
```

### Phase B (Concrete Layer — separate downstream method)

```
Input:  ContourProgression from Phase A
        Scale/mode for each section

For each (CSeg, section_id, voice_id):
    1. Map CSeg ranks [0..n-1] onto scale degrees
       rank 0 → tonic (scale degree 1)
       rank 1 → scale degree 2
       ...
       rank n-1 → scale degree n
       (wrap around if n > 7 degrees)

    2. Generate MusicEvent sequence from resultant pitches
       Duration = derived from durational CAS (separate or coupled)
       Velocity = scaled by normalized rank position

    3. Fill UnitMatrix cell via create_note_unit or create_chord_unit
```

---

## 3. Mathematical Formulation

### CSeg Normalization

Given a raw pitch sequence $P = [p_0, p_1, ..., p_{n-1}]$, normalize:

$$
r_i = |\{j : p_j < p_i\}| + \frac{1}{2}|\{j : p_j = p_i\}|
$$

i.e., $r_i$ is the number of pitches strictly lower than $p_i$, plus half the number of equal pitches (for ties). This maps any pitch sequence to integers $[0, n-1]$.

### CAS from CSeg

$$
\text{CAS}_i = \text{CMP}(r_i, r_{i+1}) \quad \text{for } i = 0, ..., n-2
$$

### Contour Transformation Matrices

For a CSeg of length $n$:

**Inversion I**: matrix element $I_{ij} = (n-1) - A_{ij}$ where $A$ is the comparison matrix.

**Retrograde R**: $r'_i = r_{n-1-i}$.

**Retrograde-Inversion RI**: apply R then I.

These generate the dihedral group $D_n$ acting on the $n$ points.

### Contour Similarity (CSIM)

For two contours $A$ and $B$ of the same length $n$:

$$
\text{CSIM}(A,B) = \frac{2}{n(n-1)} \sum_{i=0}^{n-2} \sum_{j=i+1}^{n-1} \mathbb{1}[\text{CMP}(A_i,A_j) = \text{CMP}(B_i,B_j)]
$$

Then take the maximum over all 4 reflection forms:

$$
\text{CSIM}_{\max} = \max\{\text{CSIM}(A,B), \text{CSIM}(A, I(B)), \text{CSIM}(A, R(B)), \text{CSIM}(A, RI(B))\}
$$

### Contour Entropy

$$
H(\text{CAS}) = -p_+ \log_2 p_+ - p_- \log_2 p_- - p_0 \log_2 p_0
$$

where $p_+ = \frac{\#\{+\}}{n-1}$, etc. $H$ ranges from 0 (all same direction) to $\log_2 3$ (maximally varied).

---

## 4. Python Implementation Sketch

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

class CASymbol(Enum):
    UP = '+'
    DOWN = '-'
    SAME = '0'

@dataclass
class CSeg:
    """Contour Segment: normalized rank sequence."""
    ranks: List[int]  # e.g. [0, 2, 1, 3]
    
    def __post_init__(self):
        n = len(self.ranks)
        assert set(self.ranks) == set(range(n)), f"Invalid CSeg: {self.ranks}"
    
    @property
    def n(self) -> int:
        return len(self.ranks)
    
    def cas(self) -> List[CASymbol]:
        """Contour Adjacency Series."""
        result = []
        for i in range(self.n - 1):
            a, b = self.ranks[i], self.ranks[i+1]
            if b > a:
                result.append(CASymbol.UP)
            elif b < a:
                result.append(CASymbol.DOWN)
            else:
                result.append(CASymbol.SAME)
        return result
    
    def invert(self) -> 'CSeg':
        """Inversion: flip all directions."""
        return CSeg([(self.n - 1) - r for r in self.ranks])
    
    def retrograde(self) -> 'CSeg':
        """Retrograde: reverse order."""
        return CSeg(list(reversed(self.ranks)))
    
    def retrograde_invert(self) -> 'CSeg':
        """Retrograde-Inversion."""
        return self.retrograde().invert()
    
    def comparison_matrix(self) -> np.ndarray:
        """Full pairwise comparison matrix."""
        n = self.n
        mat = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(n):
                if self.ranks[j] > self.ranks[i]:
                    mat[i, j] = 1
                elif self.ranks[j] < self.ranks[i]:
                    mat[i, j] = -1
                # else 0 (equal)
        return mat
    
    def similarity(self, other: 'CSeg') -> float:
        """CSIM: pairwise matrix similarity, best over 4 forms."""
        def _csim(a: 'CSeg', b: 'CSeg') -> float:
            assert a.n == b.n
            n = a.n
            match = 0
            total = n * (n - 1) // 2
            for i in range(n):
                for j in range(i + 1, n):
                    ca = np.sign(a.ranks[j] - a.ranks[i])
                    cb = np.sign(b.ranks[j] - b.ranks[i])
                    if ca == cb:
                        match += 1
            return match / total
        
        forms = [
            other,
            other.invert(),
            other.retrograde(),
            other.retrograde_invert(),
        ]
        return max(_csim(self, f) for f in forms)
    
    def reduce(self, keep_indices: List[int]) -> 'CSeg':
        """Morris-style reduction: keep only specified indices, renormalize."""
        kept = [self.ranks[i] for i in keep_indices]
        sorted_vals = sorted(kept)
        rank_map = {v: i for i, v in enumerate(sorted_vals)}
        return CSeg([rank_map[v] for v in kept])


# ContourVocabulary: library of seed CSegs
CONTOUR_VOCABULARY = {
    'ascend3':   CSeg([0, 1, 2]),          # 3-note rising
    'descend3':  CSeg([2, 1, 0]),          # 3-note falling
    'arch4':     CSeg([0, 2, 3, 1]),       # 4-note arch (low-high-higher-mid)
    'valley4':   CSeg([2, 1, 0, 3]),       # 4-note valley
    'twist4':    CSeg([0, 3, 1, 2]),       # leap up, then down, then up
    'wave5':     CSeg([0, 3, 1, 4, 2]),    # 5-note undulating
    'leapfill5': CSeg([0, 4, 1, 3, 2]),    # leap up, fill down, adjust
    'zigzag5':   CSeg([1, 3, 0, 4, 2]),    # irregular 5-note contour
}


def csem_by_cas(cas: List[CASymbol], vocab: dict = None) -> List[CSeg]:
    """Return all CSegs whose CAS matches the given pattern."""
    if vocab is None:
        vocab = CONTOUR_VOCABULARY
    return [cseg for cseg in vocab.values() if cseg.cas() == cas]


def generate_cas_template(pattern_type: str, length: int) -> List[CASymbol]:
    """Generate a CAS template of given type and length."""
    if pattern_type == 'rising':
        return [CASymbol.UP] * (length - 1)
    elif pattern_type == 'falling':
        return [CASymbol.DOWN] * (length - 1)
    elif pattern_type == 'arch':
        half = (length - 1) // 2
        return [CASymbol.UP] * half + [CASymbol.DOWN] * ((length - 1) - half)
    elif pattern_type == 'valley':
        half = (length - 1) // 2
        return [CASymbol.DOWN] * half + [CASymbol.UP] * ((length - 1) - half)
    elif pattern_type == 'oscillate':
        return [CASymbol.UP if i % 2 == 0 else CASymbol.DOWN 
                for i in range(length - 1)]
    elif pattern_type == 'chaos':
        rng = np.random.default_rng()
        return [CASymbol(rng.choice(['+', '-'])) for _ in range(length - 1)]
    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")


def contour_tension(cseg: CSeg) -> dict:
    """Compute tension metrics from a CSeg."""
    cas = cseg.cas()
    n = len(cas)
    
    # T1: number of direction changes
    changes = sum(1 for i in range(1, n) if cas[i] != cas[i-1])
    
    # T2: max run length
    max_run = 0
    current_run = 1
    for i in range(1, n):
        if cas[i] == cas[i-1]:
            current_run += 1
        else:
            max_run = max(max_run, current_run)
            current_run = 1
    max_run = max(max_run, current_run)
    
    # T3: CAS entropy
    counts = {s: cas.count(s) for s in set(cas)}
    probs = [c / n for c in counts.values()]
    entropy = -sum(p * np.log2(p) for p in probs)
    
    return {
        'direction_changes': changes,
        'max_run_length': max_run,
        'entropy': round(entropy, 3),
        'tension_score': round(changes + max_run + entropy, 3),
    }


def compose_contour_progression(
    sections: List[str],
    voices: List[str],
    cadence_types: List[str],
    cseg_length: int = 4,
    seed: int = 42,
) -> dict:
    """
    Generate a ContourProgression: mapping of (section, voice) -> CSeg.
    
    Returns a dict: {(section, voice): (CSeg, transform_name)}
    """
    rng = np.random.default_rng(seed)
    progression = {}
    
    for section in sections:
        section_idx = sections.index(section)
        # Choose a CAS template per section (macro-form arc)
        # Sections alternate: rising, falling, arch, rising, ...
        template_type = cadence_types[section_idx % len(cadence_types)]
        template = generate_cas_template(template_type, cseg_length)
        
        # Match vocabulary CSegs to this template
        matches = csem_by_cas(template, CONTOUR_VOCABULARY)
        seed_cseg = rng.choice(matches) if matches else CSeg(list(range(cseg_length)))
        
        for voice in voices:
            voice_idx = voices.index(voice)
            # Apply voice-specific transformation
            transforms = ['I', 'R', 'RI', 'I']
            transform = transforms[(section_idx + voice_idx) % len(transforms)]
            
            if transform == 'I':
                cseg = seed_cseg.invert()
            elif transform == 'R':
                cseg = seed_cseg.retrograde()
            elif transform == 'RI':
                cseg = seed_cseg.retrograde_invert()
            else:
                cseg = seed_cseg
            
            progression[(section, voice)] = (cseg, transform)
    
    return progression


# === Example ===
if __name__ == '__main__':
    # 3 sections × 3 voices abstract contour plan
    prog = compose_contour_progression(
        sections=['Intro', 'Verse', 'Chorus'],
        voices=['Lead', 'Harmony', 'Bass'],
        cadence_types=['oscillate', 'arch', 'valley'],
        cseg_length=4,
    )
    
    for (sec, voice), (cseg, tf) in prog.items():
        print(f"[{sec}|{voice}] {tf:>3s} → CSeg {cseg.ranks}  "
              f"CAS: {[s.value for s in cseg.cas()]}  "
              f"Tension: {contour_tension(cseg)}")
```

---

## 5. Musical Elements Framework

| Element | Abstract Contribution | Concrete Mapping |
|:---|:---|:---|
| **PITCH** | Contour shape (CAS/CSeg) independent of PC content | Rank→scale-degree translation |
| **RHYTHM** | Durational contour (long→short pattern separate from pitch CAS) | Duration values from rank order |
| **HARMONY** | Vertical CSeg alignment across voices → density of turning points | Simultaneous rank mapping → chord voicing |
| **STRUCTURE** | CAS template sequence per section = macro-form | Section = (scale, bars) context for realization |
| **TEXTURE** | Direction-change density = textural complexity | High-change → angular/pointillistic; low-change → legato/lyrical |

---

## 6. UnitMatrix Integration

```
UnitMatrix (rows=voices, cols=sections)
┌─────────────────────────────────────────────┐
│             │ Section 0  │ Section 1       │
│ Lead        │ CSeg<0,2,1,3> │ CSeg<0,3,1,2>  │
│ Harmony     │ I(CSeg)    │ R(CSeg)        │
│ Bass        │ RI(CSeg)   │ CSeg<0,1,2,3>  │
└─────────────────────────────────────────────┘
```

Each cell = abstract CSeg. Concrete layer maps ranks to pitches via section's scale and fills with create_note_unit.

**Candidate code path**: `rules/contour_theory.py` (abstract layer), feeding into `rules/subset_network.py` or `generators/` for concrete realization.

---

## 7. References

1. Friedmann, M. L. (1985). "A Methodology for the Discussion of Contour: Its Application to Schoenberg's Music." *Journal of Music Theory*, 29(2), 223–248.
2. Marvin, E. W. & Laprade, P. A. (1987). "Relating Musical Contours: Extensions of a Theory for Contour." *Journal of Music Theory*, 31(2), 225–267.
3. Morris, R. D. (1993). "New Directions in the Theory and Analysis of Musical Contour." *Music Theory Spectrum*, 15(2), 205–228.
4. Quinn, I. (1997). "Fuzzy Extensions to the Theory of Contour." *Music Theory Spectrum*, 19(2), 232–263.
5. Quinn, I. (1999). "The Combinatorial Model of Pitch Contour." *Music Perception*, 16(4), 439–456.
6. Sampaio, M. S. (2018). "Contour Similarity Algorithms." *MusMat*, II(2), 49–75.
7. Carter-Ényì, A. (2016). "Contour Recursion and Auto-Segmentation." *Music Theory Online*, 22(1).
8. Dowling, W. J. (1978). "Scale and Contour: Two Components of a Theory of Memory for Melodies." *Psychological Review*, 85(4), 341–354.
9. Schmuckler, M. A. (1999). "Testing Models of Melodic Contour Similarity." *Music Perception*, 16(3), 295–326.