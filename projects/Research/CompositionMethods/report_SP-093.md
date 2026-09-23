# Research Report: Method SP-093 — Phase-Aligned Formant Synthesis (PAF)

**Date:** 2026-09-23  
**Method Name:** Phase-Aligned Formant Synthesis (PAF)  
**Method ID:** SP-093  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  
**Candidate Code Path:** `sound/synthesis/paf.py`, callable via `workflows.musicom_workflow.produce(method="SP-093")`  
**Standalone Spec:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-093_PAF.md`  
**Report File:** `/opt/data/projects/Research/CompositionMethods/report_SP-093.md`

---

## 1. Description
Phase-Aligned Formant (PAF) synthesis is an analytical distortion / waveshaping technique invented by Miller Puckette at IRCAM that produces specified formant centers and bandwidths by modulating a two-cosine carrier with a waveshaped pulse, maintaining coherent zero-phase across all partials for artifact-free multi-formant superposition.

---

## 2. Summary Table Row
```markdown
| **SP-093** | Phase-Aligned Formant Synthesis (PAF) | **Synthesis Engines** | Formant Vocal, Brass & Resonant Timbres | Generates precise, independent formant center frequencies and bandwidths via waveshaped pulse-train modulation of a two-cosine carrier: $x[n]=g(b|\sin(\omega_0 n/2)|)[(1-q)\cos(k\omega_0 n)+q\cos((k+1)\omega_0 n)]$. Formant center $(k+q)f_0$ and Gaussian/Cauchy bandwidth $b$ decouple pitch from timbre without filters; phase alignment allows coherent additive multi-formant superposition. $\mathcal{O}(1)$ per sample. Candidate: `sound/synthesis/paf.py`. |
```

---

## 3. Database Line Count Changes
- **Before append:** 19,790 lines
- **After append:** 19,936 lines
- **Delta:** +146 lines

---

## 4. Technical Mechanics Summary
- **Equation:**
  $$x[n] = g\Big(a \cdot \big|\sin(\omega_0 n / 2)\big|\Big) \cdot \Big[ (1 - q)\cos(k \omega_0 n) + q\cos\big((k + 1)\omega_0 n\big) \Big]$$
- **Parameters:**
  - $m = f_c / f_0$, $k = \lfloor m \rfloor$, $q = m - k$, $p = 1 - q$
  - Bandwidth index $a = \pi b_w / f_0$
  - Waveshaper $g_{\text{Cauchy}}(u) = 1 / (1 + u^2)$ or $g_{\text{Gauss}}(u) = \exp(-u^2)$
- **Phase Alignment:** All harmonics emerge in cosine phase at period boundaries ($n\omega_0 = 2\pi M$). Superposition of $N$ formants has zero destructive interference notches.
- **Normalization:** Amplitude scaled by $C(a) \approx 1 + a$.
- **Complexity:** $\mathcal{O}(1)$ per sample per formant, zero recursive filter states.

---

## 5. Quirks & Pitfalls Hit
- **Avoided Double Escapes:** Verified LaTeX formatting in markdown table row.
- **Table Integrity:** Single pipe syntax verified, no double `||` prefixes created.
- **Parameter Modulation:** Stepping $k$ mid-cycle can cause discontinuities; smooth interpolation or epoch-synchronized updates recommended.

---

## 6. Next Free SP ID
**SP-094** (SP-093 is now recorded in `methods_db.md` summary table and detailed section).
