# Report SP-113 — Psychoacoustic Bass Enhancement Synthesis (PBES)

## Summary

| Field | Value |
|---|---|
| **SP ID** | SP-113 |
| **Method Name** | Psychoacoustic Bass Enhancement Synthesis (PBES) |
| **Layer** | absolute — Post-Processing / DSP |
| **Acronym** | PBES |
| **One-line description** | Post-process that generates harmonics of bass content via controlled nonlinearity to create the missing-fundamental illusion of low bass on bandwidth-limited speakers. |
| **Summary table row** | `\| **SP-113** \| Psychoacoustic Bass Enhancement Synthesis (PBES) \| **Post-Processing / DSP** \| Virtual Bass Perception \| Post-process that generates harmonics of bass content via controlled nonlinearity to create the missing-fundamental illusion of low bass on bandwidth-limited speakers. Applies to rendered audio buffers or mix stems; per-voice or shared bus configuration. $\mathcal{O}(1)$ per sample. Candidate: \`sound/effects/bass_enhancer.py\`. \|` |
| **Line count (before)** | 25053 |
| **Line count (after)** | 25188 |
| **Delta** | +135 lines |
| **Standalone file** | `sound_method_SP-113_PBES.md` |
| **Report file** | `report_SP-113.md` (this file) |
| **Candidate code path** | `sound/effects/bass_enhancer.py` |

## Complete Section Text Appended

The full detailed section begins at line 25057 of methods_db.md and runs to line 25188. It includes:

- **### Source** (lines 25058-25072) — 8 references: Wikipedia missing fundamental, Larsen & Aarts 2002, Ben-Tzur & Colloms 1999, MaxxBass patent, Samsung TV paper, Philips patent, Klayman patent, Zoelzer's DAFX textbook.
- **### Layer** (line 25071) — absolute, Post-Processing / DSP, code path `sound/effects/bass_enhancer.py`
- **### Description** (lines 25073-25084) — Explains the missing fundamental/virtual pitch illusion, signal chain overview (LPF → nonlinear harmonic generation → BPF shaping → dynamic gain scaling → HPF dry path → delay compensation → sum), distinction from SP-097 SHOS (subharmonic divide-down).
- **### Technical Mechanics** (lines 25086-25133) — Full signal flow diagram, 6-step derivation with equations: Step 1 LPF bass extraction, Step 2 three harmonic generation methods (full-wave integrator A, asymmetric envelope follower B, half-wave clipping C), Step 3 BPF harmonic shaping, Step 4 envelope-follower dynamic gain, Step 5 HPF + delay compensation, Step 6 output sum. Cost analysis: ~15–25 MIPS with FIR, 12 MIPS with IIR on Motorola DSP.
- **### Musical Elements Framework** (lines 25135-25147) — PITCH (reinforces virtual fundamental, risk of intermodulation with polyphonic bass), RHYTHM (envelope follower preserves/d enhances rhythmic contour), HARMONY (generated 2nd/3rd harmonics enter lower-midrange — can reinforce or mask), STRUCTURE (per-section parameter arc controlling bass weight), TEXTURE (per-voice vs shared bus, stratified bass density).
- **### UnitMatrix Integration** (lines 25149-25156) — Voices = per-voice PBES instances with θ_v parameters; Sections = per-section θ_s with interpolation; Cell filling = post-process on rendered audio, zero-drift invariant untouched.
- **### Pitfalls** (lines 25158-25185) — 8 pitfalls with fixes: (1) intermodulation distortion, (2) phase distortion from IIR, (3) missing fundamental not universal, (4) over-enhancement buzzy timbre, (5) spectral overlap with midrange, (6) DC offset, (7) aliasing from nonlinear harmonics, (8) envelope follower attack hole.
- **Candidate code path** (line 25187) — `sound/effects/bass_enhancer.py` with PBEConfig, PBESingleVoice, PBEStereoBus, PBEZyler, pbe_preset.

## Technical Mechanics Summary

PBES is a post-processing DSP method based on the missing fundamental phenomenon:

1. **Bass extraction**: Linear-phase FIR LPF at $f_c$ (100–150 Hz) isolates bass region
2. **Harmonic generation via 3 alternative methods**:
   - A: Full-wave integrator (Larsen & Aarts) — $y_{int}[n] = y_{int}[n-1] + x_{lp}[n]$, reset at zero-crossings. Spectrum 1/k rolloff.
   - B: Asymmetric envelope follower (Waves MaxxBass) — fast rise $\alpha_{rise} \approx 1$, slow fall $\alpha_{fall} \in [0.03, 0.1]$. Spectral tilt $\gamma \in [0.5, 2.0]$ controlled by fall time.
   - C: Half-wave clipping (Samsung) — $y = \max(x, 0)$ + DC blocker. Simplest.
3. **Harmonic shaping**: BPF at $[f_c, 3f_c]$ removes fundamental + limits to 2–3 harmonics
4. **Dynamic gain scaling**: Envelope-follower tracks bass energy, scales harmonics proportionally
5. **Dry path**: HPF at $f_c$ + delay compensation to align with processed path
6. **Sum**: $y_{out} = g_{dry} \cdot x_{delayed} + g_{harm} \cdot x_{hs}$

Three methods produce the virtual pitch illusion without adding genuine subwoofer energy. The illusion works for ~70–80% of listeners (the remainder hear the overtones).

## Quirks / Pitfalls Hit

1. **Append newline issue**: The methods_db.md file did not have a trailing newline on its last line. When `cat temp_file >> methods_db.md` appended the new section, the first line of the section got concatenated onto the last line of the previous method's candidate code path. Fixed with patch: replaced the concatenated `...# Psychoacoustic Bass Enhancement...` with `.\n\n# Psychoacoustic Bass Enhancement...`.

2. **LaTeX backslash escaping**: During patch operations, LaTeX backslashes (`\mathcal{O}`) can get double-escaped to `\\mathcal{O}` if the tool treats them as escape characters. Verified both summary row and detailed section use single backslash.

3. **Summary table row format**: The existing summary table has inconsistent row formatting — some rows (SP-109, SP-110) start with `|||` or `||||` (triple/quadruple pipes) which are formatting errors. My new row (SP-113) uses a single leading `|` matching the majority of the table and the header format.

4. **Hardcoded vs. dynamic SP number**: Initially I checked the file for the highest SP. Summary table had SP-112 at the top but SP-112's detailed section was not at the end of the file (methods from other layers interleave). Both the summary table and the file-level scan (sound_method_SP-*.md, report_SP-*.md) confirmed SP-112 as the max.

5. **Symlink resolution**: The working directory `/opt/data/projects/Research/CompositionMethods/` is a symlink into `/opt/data/repos/musicom/projects/Research/CompositionMethods/`. All writes resolved through the symlink to the physical path.

## Verified Artifacts

- [x] Summary table updated with SP-113 row (line 295)
- [x] Detailed section appended (lines 25057–25188)
- [x] All required sub-headers present (Source, Layer, Description, Technical Mechanics, Musical Elements Framework, UnitMatrix Integration, Pitfalls)
- [x] Temp file cleaned up
- [x] Free SP number confirmed as SP-113 (max existing = SP-112)
- [x] Standalone file: `sound_method_SP-113_PBES.md` (278 lines)
- [x] Report file: `report_SP-113.md` (this file)
- [x] Line count verified (25053 → 25188, +135 lines)
- [x] Two SP-113 occurrences confirmed in DB (summary + detailed section)
- [x] No LaTeX double-escape or table-row | duplication issues in the final content