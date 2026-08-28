# Report — SP-056 Walsh Function Synthesis (Fast Walsh–Hadamard Transform)

## Summary

| Field | Value |
|---|---|
| Method ID | **SP-056** |
| Name | Walsh Function Synthesis (Fast Walsh–Hadamard Transform) |
| Acronym | FWHT |
| Layer | Synthesis Engines |
| One-line description | Additive synthesis in the sequency domain: decompose a periodic waveform into a sum of Walsh functions (binary ±1 square waves) via the Fast Walsh–Hadamard Transform — an O(N log N) butterfly with zero multiplications. Beauchamp's brightness B = Σ n|a_n| / Σ |a_n| is a one-knob timbre morph; resynthesis = phase accumulator + table read. Casio VL-Tone VL-1 lineage. |

## Summary-table row (appended to methods_db.md)

```
| **SP-056** | Walsh Function Synthesis (Fast Walsh–Hadamard Transform) | **Synthesis Engines** | Reedy / Hollow / Chiptune Square-Wave Timbres | Additive synthesis in the sequency domain: decomposes a periodic waveform into a sum of Walsh functions (binary $\pm1$ square waves) via the Fast Walsh–Hadamard Transform — an $\mathcal{O}(N \log N)$ butterfly with zero multiplications (add/subtract only). Sequency replaces frequency; Beauchamp's brightness $B=\sum n|a_n|/\sum|a_n|$ (the sequency centroid) is a one-knob timbre morph. Multiplier-free resynthesis = phase accumulator + table read. Casio VL-Tone VL-1 lineage. |
```

## Line counts

| Metric | Value |
|---|---|
| methods_db.md before append | 13518 |
| methods_db.md after append (detailed section) | 13834 |
| methods_db.md after summary row | 13835 |
| Net delta | +317 lines |

## Files

| File | Path | Status |
|---|---|---|
| Standalone write-up | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-056_FWHT.md` | written (13 KB) |
| Report | `/opt/data/projects/Research/CompositionMethods/report_SP-056.md` | this file |
| Temp append file | `/opt/data/projects/Research/CompositionMethods/_temp_sp056.md` | created then removed (cat >> + rm) |

## Verify (grep)

```
143:| **SP-056** | Walsh Function Synthesis ... (summary row)
13653:# Walsh Function Synthesis (Fast Walsh–Hadamard Transform) (Method SP-056)   (detailed section header)
13656:Walsh functions form a complete orthogonal set ... (source)
13824:| **Walsh (SP-056)** | **Square wave ... (comparison table row)
```

## Technical mechanics summary

1. **Walsh functions** — complete orthogonal set of binary ±1 square waves; the n-th function has n (or ⌈n/2⌉) zero-crossings per period = its *sequency*. Built from the Rademacher system r_k(t) = sign(sin(2^(k+1)πt)).
2. **Sylvester–Hadamard matrix** — H_1=[1], H_{2N}=[[H_N,H_N],[H_N,−H_N]]; rows are Walsh functions, H_N H_N^T = N I.
3. **FWHT** — Walsh coefficients a = (1/N) H_N x, computed by an FFT-shaped butterfly whose twiddles are ±1 → O(N log N) additions, **zero multiplications**.
4. **Resynthesis** — x[n] = (H_N a)_n; time-varying synthesis = phase accumulator φ[n] = φ[n−1] + N f0/fs (mod N) + table read w[⌊φ⌋], where w[j] = Σ_k a_k H_N[k,j] is precomputed once.
5. **Brightness** — B = Σ n|a_n| / Σ |a_n| (sequency centroid); Beauchamp (1982) matches |a_n| and tilts to hit target B → one-knob timbre morph.
6. **Anti-aliasing** — sequency truncation (keep K<N lowest terms) and/or integer-sub-multiple N; optionally PolyBLEP per edge.

## Musical Elements Framework mapping

- **PITCH**: accumulator rate Δφ = N f0/fs only; fully decoupled from the timbre vector a.
- **RHYTHM**: per-note ADSR gates the sum; brightness envelope B(t) per onset.
- **HARMONY**: sequency spectrum {|a_n|} + B = the "harmonic" content in the square-wave basis.
- **STRUCTURE**: brightness trajectory B(s) per section + coefficient-set switching = timbral macro-form.
- **TEXTURE**: retained-term count K + sequency distribution = squareness/density; per-voice B/K stratification.

## UnitMatrix Integration

- Voices = rows: each owns a coefficient vector a_v + brightness B_v + its own phase accumulator.
- Sections = columns: each prescribes B_s + coefficient-set index; continuous B crossfade at joins.
- Cells U_{v,s}: {PITCH}=f0, {HARMONY}=B/K, {RHYTHM}=envelope, {TEXTURE}=coefficient selection/morph.
- Flow: fill matrix → validate zero-drift → export MIDI (musicom) → per-voice Walsh render → sum → post-process → spatialize.

## Quirks / pitfalls hit during execution

1. **Prompt had stale SP numbering.** The task said "highest existing is SP-044, new method is SP-045", but the DB had already grown to SP-055 (FSHT). I re-derived the true next ID = **SP-056** from the summary table + section headers, and confirmed no SP-056 existed anywhere.
2. **LaTeX backslash double-escape check** — the two known patch pitfalls were verified: the new summary row has a single `|` prefix (no `||`), and the `\\` sequences in the file (12 lines) are legitimate LaTeX matrix/cases row separators (e.g. `\\begin{bmatrix} H_N & H_N \\\\ H_N & -H_N`) consistent with pre-existing rows — no double-escape bug introduced.
3. **Sibling subagent warning** — the patch tool reported the file was modified by another agent at 09:11:52 (after my first read). Re-read confirmed my SP-056 summary row is present exactly once at line 143 with correct single-pipe format; no conflict.
4. **Wikipedia API search** for "Beauchamp brightness" returned false hits (biomedical ethics author T.L. Beauchamp); resolved via DuckDuckGo which surfaced the correct James W. Beauchamp (UIUC, musical acoustics) and his 1982 JAES paper + 1984 Academic Press book "Applications of Walsh and Related Functions".
5. **Sequency-ordering subtlety** — documented the Paley-vs-Hadamard (sequency) ordering issue and provided the Gray-code row permutation so analysis and synthesis use one ordering end-to-end.

## References (primary)

- Walsh (1923), *American Journal of Mathematics* 45(1).
- Rademacher (1922), *Mathematische Annalen* 87.
- Beauchamp (1982), *JAES* 30(6), 396–406.
- Beauchamp (1984), *Applications of Walsh and Related Functions*, Academic Press.
- Hadamard (1893), *Bulletin des Sciences Mathématiques* 17.
- Casio (1981), VL-Tone VL-1 Service Manual.
- Harmuth (1970), *Transmission of Information by Orthogonal Functions*, Springer.
