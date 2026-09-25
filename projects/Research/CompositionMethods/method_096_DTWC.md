# Method 096 — Dynamic Time Warping Composition (DTWC)

**Acronym**: DTWC
**Paradigm**: Rules-Based
**Layer**: concrete
**Next free ID**: 097

## Extended Write-up

### Mathematical Foundation

Dynamic Time Warping (DTW) finds the optimal alignment between two sequences $A = a_1,\dots,a_N$ and $B = b_1,\dots,b_M$ by solving:

$$D(i,j) = d(a_i, b_j) + \min\{D(i-1,j), D(i,j-1), D(i-1,j-1)\}$$

where $d(\cdot,\cdot)$ is the local distance (typically L1 or L2 norm over the multi-dimensional feature vector), subject to boundary conditions $D(1,1)=d(a_1,b_1)$, $D(N,M)$ final cost, and optionally a Sakoe–Chiba window $|i-j|\le w$.

The optimal warp path is $P = \{(p_1,q_1),\dots,(p_K,q_K)\}$ obtained by backtracking from $(N,M)$ to $(1,1)$ following the argmin steps. Each step belongs to $\{(1,0),(0,1),(1,1)\}$ — vertical (source stretched), horizontal (target compressed), or diagonal (matched).

### Morphing — Generating New Material

Given the warp path $P$, the output sequence $O = o_1,\dots,o_K$ is:

$$o_k = (1-\alpha) \cdot a_{p_k} + \alpha \cdot b_{q_k}, \quad \alpha \in [0,1],\; k = 1\dots K$$

where $\alpha$ is the morph parameter. The raw output is post-processed:
- **Pitch**: nearest quantization to scale (if grid-locked mode), or continuous pitch-bend (fluid mode)
- **Onset**: cumulative sum of per-step time increments $\Delta t_k = \tau_A \cdot \Delta p_k + \tau_B \cdot \Delta q_k$ where $\tau_A, \tau_B$ are the average inter-onset intervals of source/target
- **Duration**: interpolated between $a_{p_k}$ and $b_{q_k}$ durations
- **Velocity**: interpolated between source and target velocities

### Multi-Voice Extension

For $V$ voices, each voice $v$ has its own source-target pair $(A_v, B_v)$ and morph parameter $\alpha_v$. The total morph output for voice $v$ is $O_v$. The cross-voice coupling cost:

$$C_{\text{couple}} = \sum_{t} \|O_1[t] - O_2[t]\|^2$$

can be minimized by adjusting $\alpha_v$ (shared harmonic skeleton mode) or left free (independent texture mode).

### Macro-Form via $\alpha$ Schedule

For a $S$-section piece, $\alpha(s)$ defines the morph trajectory:

- **Linear**: $\alpha(s) = s/S$
- **Ease-in-out**: $\alpha(s) = \frac{1}{2}[1 - \cos(\pi s/S)]$
- **Stepwise**: $\alpha(s) \in \{0, 0.25, 0.5, 0.75, 1\}$

Section 1 is source-like; section $S$ is target-like; middle sections are hybrids. The warp cost $D_{\text{tot}}(A,B)$ per section measures how much material has changed and serves as a tension/novelty gauge.

## Python Implementation Sketch

```python
import numpy as np
from typing import List, Tuple, Optional

def dtw_cost_matrix(A: np.ndarray, B: np.ndarray,
                    window: Optional[int] = None) -> np.ndarray:
    """
    Compute the DTW accumulated cost matrix.
    
    A: (N, D) source sequence
    B: (M, D) target sequence
    window: Sakoe-Chiba band radius (None = no constraint)
    """
    N, M = len(A), len(B)
    D = np.full((N+1, M+1), np.inf)
    D[0, 0] = 0.0
    if window is None:
        window = max(N, M)
    for i in range(1, N+1):
        lo = max(1, i - window)
        hi = min(M, i + window)
        for j in range(lo, hi+1):
            cost = np.linalg.norm(A[i-1] - B[j-1])  # L2 distance
            D[i, j] = cost + min(D[i-1, j], D[i, j-1], D[i-1, j-1])
    return D[1:, 1:]  # (N, M) accumulated cost


def backtrack(D: np.ndarray) -> List[Tuple[int, int]]:
    """Backtrack through accumulated cost matrix to get warp path."""
    N, M = D.shape
    i, j = N-1, M-1
    path = [(i, j)]
    while i > 0 or j > 0:
        candidates = []
        if i > 0 and j > 0:
            candidates.append((D[i-1, j-1], i-1, j-1))
        if i > 0:
            candidates.append((D[i-1, j], i-1, j))
        if j > 0:
            candidates.append((D[i, j-1], i, j-1))
        _, i, j = min(candidates, key=lambda x: x[0])
        path.append((i, j))
    return list(reversed(path))


def morph_warp(A: np.ndarray, B: np.ndarray,
               alpha: float = 0.5,
               path: Optional[List[Tuple[int, int]]] = None,
               scale_degrees: Optional[np.ndarray] = None
               ) -> np.ndarray:
    """
    Morph between source A and target B along the DTW warp path.
    
    Returns (K, D) array where K = len(path).
    """
    if path is None:
        D = dtw_cost_matrix(A, B)
        path = backtrack(D)
    # Interpolate
    K = len(path)
    morph = np.zeros((K, A.shape[1]))
    for k, (i, j) in enumerate(path):
        morph[k] = (1 - alpha) * A[i] + alpha * B[j]
    # Optional scale quantization
    if scale_degrees is not None:
        pitch_col = 0  # assume pitch is first column
        sd = np.round(morph[:, pitch_col]).astype(int)
        morph[:, pitch_col] = sd  # snap to integer
    return morph


def dtwc_compose(source_seqs: List[np.ndarray],
                 target_seqs: List[np.ndarray],
                 alphas: List[float],
                 ticks_per_beat: int = 480,
                 grid_quantize: bool = True) -> List[List[Tuple]]:
    """
    Multi-voice DTW composition.
    
    source_seqs[v]: (N_v, D) — voice v source
    target_seqs[v]: (M_v, D) — voice v target
    alphas[v]: morph param for voice v
    
    Returns list of voice lists: voice v = [(pitch, onset_ticks, dur_ticks, vel), ...]
    """
    voices = []
    for v in range(len(source_seqs)):
        A, B = source_seqs[v], target_seqs[v]
        a = alphas[v]
        cost_mat = dtw_cost_matrix(A, B)
        path = backtrack(cost_mat)
        morph_seq = morph_warp(A, B, a, path)
        # Convert morph sequence to events
        events = []
        tick = 0
        for k in range(len(morph_seq)):
            pitch = int(round(morph_seq[k, 0]))
            dur = int(round(morph_seq[k, 2])) if morph_seq.shape[1] > 2 else ticks_per_beat
            vel = int(round(morph_seq[k, 3])) if morph_seq.shape[1] > 3 else 80
            if grid_quantize:
                tick = ((tick // ticks_per_beat) + 1) * ticks_per_beat
            events.append((pitch, tick, dur, vel))
            tick += dur
        voices.append(events)
    return voices


# Example usage
if __name__ == "__main__":
    # Source: C major scale ascending
    src = np.array([[60, 480, 80],
                    [62, 480, 80],
                    [64, 480, 80],
                    [65, 480, 80],
                    [67, 480, 80],
                    [69, 480, 80],
                    [71, 480, 80],
                    [72, 480, 80]], dtype=float)
    # Target: C major arpeggio
    tgt = np.array([[60, 960, 90],
                    [64, 480, 80],
                    [67, 960, 95],
                    [72, 960, 100]], dtype=float)
    
    events = dtwc_compose([src], [tgt], [0.5])
    print(f"Morphed {len(src)} events + {len(tgt)} → {len(events[0])} events")
    for e in events[0][:12]:
        print(f"  pitch={e[0]}, onset={e[1]}, dur={e[2]}, vel={e[3]}")
```

## References

- Vintsyuk, T. K. (1968). "Speech discrimination by dynamic programming." *Kibernetika*, 4:81–88.
- Sakoe, H. and Chiba, S. (1978). "Dynamic programming algorithm optimization for spoken word recognition." *IEEE Trans. Acoustics, Speech, and Signal Processing*, 26(1):43–49.
- Müller, M. (2007). "Dynamic Time Warping." In *Information Retrieval for Music and Motion*, ch. 4, pp. 69–84. Springer.
- Müller, M., Kurth, F., and Clausen, M. (2009). "Audio Matching via Chroma-Based Statistical Features." *ISMIR 2005*.
- Ewert, S., Müller, M., and Grosche, P. (2009). "High Resolution Audio Synchronization using Chroma Onset Features." *ICASSP 2009*.
- Aloupis, G., et al. (2006). "Geometric and Algorithmic Aspects of the Dynamic Time Warping Distance." *CCCG 2006*.

## Candidate Code Path

`generators/dtwc_morph.py` — A morphing generator that takes source/target sequence arrays and an alpha schedule, produces MusicEvents for each UnitMatrix cell. The generator reads source/target from pre-existing material (or from seed generators 001/002/040), computes DTW, and fills cells with morphed events.