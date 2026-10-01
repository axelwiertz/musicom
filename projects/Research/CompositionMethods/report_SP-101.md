# Report: SP-101 — Digital Waveguide Synthesis (DWS)

## Identification

| Field | Value |
|---|---|
| **Method ID** | SP-101 |
| **Method Name** | Digital Waveguide Synthesis (DWS) |
| **Layer** | absolute — sound production (synthesis engine) |
| **Category** | Synthesis Engines |
| **Target Output** | Physical-Modeling String / Wind / Percussion Timbre |
| **Candidate Code Path** | `sound/synthesis/digital_waveguide.py` |
| **Workflow Integration** | `workflows.musicom_workflow.produce(method="SP-101")` |

## Summary Table Row

Added to the SP summary table in `methods_db.md` (line 272):

```
||| **SP-101** | Digital Waveguide Synthesis (DWS) | **Synthesis Engines** | Physical-Modeling String/Wind/Percussion Timbre | Models acoustic wave propagation as bidirectional traveling waves in digital delay lines. A vibrating string, acoustic bore, or struck bar is realized as a pair of delay lines looped via termination filters, fractional-delay interpolators, scattering junctions, and nonlinear excitations (pluck, bow, blow, strike). Loop filter $H_L(z)$ governs decay spectrum; stiffness allpass chain produces inharmonic partials for piano/bell timbres. Generalizes Karplus-Strong (SP-011) to arbitrary terminations and multi-waveguide networks. $\mathcal{O}(1)$ per sample per waveguide. Candidate: `sound/synthesis/digital_waveguide.py`. |
```

## Detailed Section Location

The section "Sound Production Method SP-101 — Digital Waveguide Synthesis (DWS)" was appended to the end of `methods_db.md` (the file now has 22,546 lines, up from 22,327 — an increase of 219 lines). It contains:

- ### Source (with references)
- ### Layer (absolute)
- ### Description (core DWS definition and d'Alembert solution)
- ### Technical Mechanics (7 subsections: Ideal String, Lossy String, Fractional Delay, Stiffness Dispersion, Scattering Junctions, Excitation Types, Computational Complexity)
- ### Musical Elements Framework (PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE)
- ### UnitMatrix Integration (Voices & Sections)
- ### Pitfalls (8 numbered items)

## File Manifest

| File | Status | Size |
|---|---|---|
| `methods_db.md` | Updated | 22,546 lines (pre: 22,327, delta: +219) |
| `sound_method_SP-101_DWS.md` | Created | 13,389 bytes |
| `report_SP-101.md` | Created | (this file) |

## Technical Mechanics Summary

Digital Waveguide Synthesis is the most general physical-modeling technique for 1D wave-propagating media:

1. **Ideal string**: bidirectional delay line of length $K = \lfloor f_s / (2f_0) \rfloor$ with inverting terminations. Output = $y^+[n-p] + y^-[n+p]$ at pickup position $p$.

2. **Loss**: lumped single-pole loop filter $H_L(z) = g(1-a)/(1-az^{-1})$ with gain $g$ and lowpass $a$.

3. **Pitch tuning**: Thiran first-order allpass $F(z) = (a_\delta + z^{-1})/(1 + a_\delta z^{-1})$ provides continuous fractional-delay interpolation $\delta \in [0,1)$.

4. **Stiffness dispersion**: chain of $R$ allpass sections approximates quadratic group-delay $\tau_g(\omega) \approx \tau_0 + \alpha \omega^2$, producing inharmonic partials $f_n = n f_0 \sqrt{1 + B n^2}$.

5. **Scattering junctions**: at area discontinuity $A_1 \to A_2$, reflection coefficient $k = (A_1 - A_2)/(A_1 + A_2)$. Lossless, energy-conserving.

6. **Excitations**: pluck (triangle initial condition), bow (tanh friction + noise), blow (Bernoulli flow), air-jet (jet-drive), strike (Hertz contact), commuted (pre-convolved excitation).

7. **Complexity**: $\mathcal{O}(1)$ per sample for basic string; $\mathcal{O}(R + J)$ per sample with stiffness + scattering.

## Quirks and Pitfalls Hit

1. **Table prefix normalization**: The SP summary table had inconsistent pipe prefixes: `||` for older rows (SP-060–SP-097) and `|||` for recent rows (SP-098–SP-100). The patch adding SP-101 matched the adjacent style. After the first patch, SP-100 gained an extra pipe (`||||`), fixed in a second normalization patch.

2. **SP-101 did not exist**: Cross-check confirmed SP-101 and SP-102 are composition method IDs (no "SP-" prefix) in the main table, not sound production methods. The SP summary table only goes to SP-100, confirming SP-101 is truly free.

3. **Detailed section appended to file end**: The 218-line detailed section was written to a temp file, appended via `cat >>`, and the temp file removed per the workflow.

4. **No manual escaping needed**: The standalone method file uses LaTeX math delimiters `$$...$$` with single backslashes — correct for Markdown rendering. The methods_db.md detailed section uses the same.

## Next Free SP ID

**SP-102**.

## Summary

SP-101 (DWS) adds a major missing synthesis paradigm to the musicom sound production repertoire: physical modeling via digital waveguides. This completes the physical-modeling family alongside SP-011 (Karplus-Strong), SP-023 (reed), SP-024 (bowed string), SP-065 (brass lip-reed), SP-066 (air-jet flute), SP-074 (piano hammer-string), SP-087 (TR-808 snare), SP-098 (TR-808 kick), and SP-099 (comb filter resonance). DWS is the most general formulation, subsuming KR as a special case and extending to wind bores, stiff bars, and waveguide mesh networks.