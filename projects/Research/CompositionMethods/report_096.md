# Registration Report — Method 096: Dynamic Time Warping Composition (DTWC)

**Date**: 2026-09-25
**Agent**: Hermes (music research cron job)
**Method ID**: 096
**Method Name**: Dynamic Time Warping Composition
**Acronym**: DTWC
**Paradigm**: Rules-Based
**Layer**: concrete

## One-line Description

Computes the optimal non-linear alignment (warp path) between two musical sequences via the DTW algorithm, then generates new material by walking the path and interpolating between matched points — a morphing/variation method for transforming and blending musical ideas.

## Summary Table Row

```
| **096** | concrete | Dynamic Time Warping Composition (DTWC) | **Rules-Based** | Pitch, Rhythm, Structure, Texture | Moderate (Source/Target-anchored) | Grid-Locked / Continuous | Meso / Warp Path | $\mathcal{O}(N \cdot M)$ | Computes the optimal non-linear alignment (warp path) between two musical sequences via DTW, then generates new material by walking the path and interpolating between matched points. Morph parameter $\alpha$ blends source→target; warp path density controls rhythmic stretch/compression. Multi-voice morphs per UnitMatrix row. |
```

## Files

| File | Path |
|------|------|
| **methods_db.md** | `/opt/data/repos/musicom/projects/Research/CompositionMethods/methods_db.md` |
| **Standalone method** | `/opt/data/repos/musicom/projects/Research/CompositionMethods/method_096_DTWC.md` |
| **This report** | `/opt/data/repos/musicom/projects/Research/CompositionMethods/report_096.md` |

## Line Count

- **Before**: 20256 lines
- **After**: 20309 lines
- **Delta**: +53 lines (+1 summary row, +52 detailed method section appended at end of file)

## Classification Details

| Attribute | Value |
|-----------|-------|
| **Paradigm** | Rules-Based |
| **Layer** | concrete (generates concrete MusicEvents from input sequences) |
| **Primary Elements** | Pitch, Rhythm, Structure, Texture |
| **Tonal Gravity** | Moderate (Source/Target-anchored — the source and target define the tonal center implicitly; optional scale quantization post-filter) |
| **Metric Binding** | Grid-Locked / Continuous (quantized tempo grid or continuous-time fluid mode) |
| **Memory Depth** | Meso / Warp Path (whole sequence context; the warp path encodes the full-source-to-target alignment) |
| **Time Complexity** | $\mathcal{O}(N \cdot M)$ (standard DP with optional Sakoe-Chiba window reduces to $\mathcal{O}(N \cdot w)$) |
| **Deterministic** | Yes (same inputs + seed = identical output) |

## Complete Method Section Text (appended)

```
## 096 — Dynamic Time Warping Composition (DTWC)

### Source
Dynamic time warping (DTW) was introduced by Vintsyuk (1968) for speech recognition, formalized by Sakoe & Chiba (1978) with locality constraints, and extended to music synchronization and alignment by Müller (2007). The generative application — morphing between musical sequences by walking the DTW warp path and interpolating matched points — has been used in computer-aided composition, automatic variation generation, and style-interpolation systems (Aloupis et al. 2006; Müller et al. 2009; Ewert et al. 2009).

### Layer
concrete

### Description
[See methods_db.md for full text — 4 algorithmic steps: cost matrix, accumulated cost & warp path, interpolation along path, rhythmic decoding]

### Musical Elements Framework
| Element | DTWC Mapping |
|---------|-------------|
| PITCH | Multi-dimensional pitch vectors warped and interpolated along path |
| RHYTHM | Warp path shape — dense vertical runs = stretched, horizontal = compressed |
| HARMONY | Chord vectors blended; projection to nearest chord post-filters |
| STRUCTURE | Macro-form = section-level alpha(s) schedule |
| TEXTURE | Per-voice alpha_v decorrelation |

### UnitMatrix Integration
Voices (Rows): Each UnitMatrix voice is a separate DTW channel.
Sections (Columns): Each section has its own alpha(s) value and optional source-target pair.

### Pitfalls
1. Path degeneracy — mitigate with Sakoe-Chiba window
2. Error propagation — use robust distance (L1)
3. Rhythmic ambiguity — post-hoc beat-tracking
4. Harmonic blur — use slerp or chord projection
5. Texture severing — enforce shared harmonic skeleton
6. Not from-scratch — requires seed generators
```

(Note: The above is a condensed summary. The full section as stored in methods_db.md is the complete write-up with all details.)

## Candidate Code Path

The generator would live at:
```
generators/dtwc_morph.py
```

This module would:
- Accept source and target sequences as numpy arrays of shape (N, D) and (M, D)
- Compute DTW cost matrix and backtrack warp path
- Apply alpha morph interpolation
- Output List[List[MusicEvent]] for per-voice per-section filling

Relationship to existing generators:
- Requires seed material from other generators (001 Skeleton-First, 002 Markov, 040 Perlin) or external sources — it is a *morphing/transformation* method, not a from-scratch generator
- Complements 055 SAMC (SAMC finds global optimum by annealing; DTWC morphs between two fixed endpoints via dynamic programming)
- Cousin of 050 OTVL (both align two structures; OT moves mas between distributions, DTW warps time-indexed sequences)

## Quirks and Pitfalls Hit During Registration

1. **Triple-pipe artifact**: The methods_db.md summary table has a pre-existing `|||` (triple pipe) prefix on lines 094 and 095, likely a previous patch artifact. My inserted 096 row initially got triple pipes too; required a targeted patch to normalize to `||`.
2. **LaTeX escaping**: The original file stores `\mathcal{O}` with a single backslash in the MD content. The read_file display shows this correctly. Did not encounter double-escape issues.
3. **Summary table format**: The DTWC summary row omits "Harmony" from Primary Elements because the method does not model harmony intrinsically — harmony is a post-filter projection. The description explicitly states it computes alignment, not harmony.

## Next Free ID

**097** (since 095 was the previous max, 096 is now taken)