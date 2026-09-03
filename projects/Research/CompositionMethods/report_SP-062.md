# Report — SP-062 Antiderivative Antialiasing for Nonlinear Waveshaping (ADAA)

## Summary
- **Method name:** Antiderivative Antialiasing for Nonlinear Waveshaping (ADAA)
- **ID:** SP-062
- **Layer:** absolute (sound production) · Post-Processing / DSP
- **One-line description:** Anti-aliases an arbitrary memoryless (or stateful) waveshaper $y=f(x)$ without oversampling — the pointwise evaluation is replaced by the average of $f$ over each sample interval, computed as a divided difference of the antiderivative $F(x)=\int f(x)\,dx$ (1st-order linear-segment or 2nd-order quadratic-segment), removing inharmonic "digital grunge" of clippers/saturators at $\mathcal{O}(1)$ per sample.

## Line counts
- **Before:** 15513 lines
- **After:** 15647 lines
- **Delta:** +134 lines (133 section + 1 summary row)

## Summary-table row (appended at line 155, after SP-061 row, before the `---` separator)
| **SP-062** | Antiderivative Antialiasing for Nonlinear Waveshaping (ADAA) | **Post-Processing / DSP** | Aliasing-Free Distortion / Saturation / Wavefolding | Anti-aliases an arbitrary memoryless (or stateful) waveshaper $y=f(x)$ without oversampling: replaces the pointwise evaluation with the average of $f$ over each sample interval, computed as a divided difference of the antiderivative $F(x)=\int f(x)\,dx$ — 1st-order (linear segment) or 2nd-order (quadratic segment, flatter passband). Removes the inharmonic "digital grunge" of clippers/saturators at base sample rate for $\mathcal{O}(1)$ cost; the no-oversampling counterpart to SP-049 (16× oversampled) and the waveshaper complement to SP-019/SP-029/SP-051. |

## Standalone file
`/opt/data/projects/Research/CompositionMethods/sound_method_SP-062_ADAA.md`

## Candidate code path
`sound/effects/adaa_waveshaper.py` (new module alongside `shimmer_reverb.py`, `bbd_chorus.py`, `tilt_eq.py`, `spectral_gate.py`). Consumes a rendered mono voice buffer (SP-001 FluidSynth / SP-029 subtractive / SP-039 additive), returns the anti-aliased distorted buffer. Vectorized NumPy; no oversampling, no decimation filter.

## Append workflow
1. Resolved next ID dynamically: scanned summary table (`SP-001`…`SP-061`) AND standalone files (`sound_method_SP-*.md` up to SP-061, `report_SP-*.md` up to SP-061). Highest = SP-061 → new ID = **SP-062**. Confirmed `grep -c SP-062` = 0 before starting (no duplication).
2. Layer classification: `absolute` (sound production), Post-Processing / DSP. Stated in section + report header.
3. Researched method via web (DAFx-16, IEEE SPL 2017, DAFx-19, DAFx-20, Chowdhury ADAA repo).
4. `write_file` full section → `_temp_sp062.md` (17940 bytes).
5. `printf '\n' >> methods_db.md && cat _temp_sp062.md >> methods_db.md && rm _temp_sp062.md`.
6. `patch` (replace mode) inserted the SP-062 summary row after the SP-061 row, before the `---` separator.
7. Wrote standalone `sound_method_SP-062_ADAA.md`.
8. Re-read patched lines to verify no `||` prefix and no `\\` double-escaping.

## Verification
- `wc -l methods_db.md` → **15647** lines (was 15513).
- `grep SP-062` → summary row (line 155), detailed-section header (line 15516), plus comparison-table row and code references inside the section.
- Patch pitfall check: new row has single leading `|`, single `\` backslashes, `\int`, `\mathcal{O}` render correctly (no `||`, no `\\\\`).

## Technical mechanics summary
1. **Problem** — memoryless waveshaper $f$ generates harmonics above Nyquist; direct $y[n]=f(x[n])$ aliases them.
2. **Continuous-time convolution** — anti-aliased output = box-kernel average $y[n]=\frac1T\int_{t_{n-1}}^{t_n}f(x(t))dt$.
3. **First-order ADAA** — linear segment → divided difference of $F$: $y[n]=\frac{F(x[n])-F(x[n-1])}{x[n]-x[n-1]}$, $f(x[n])$ when denominator ≈ 0.
4. **Second-order ADAA** — quadratic segment, flatter passband (corrects the sinc roll-off), uses $F$ differences at three samples.
5. **Closed-form antiderivatives** — hard clip $F=\tfrac12x^2$ (|x|≤1) / $x\operatorname{sgn}(x)-\tfrac12$; tanh $F=\ln\cosh x$; polynomials by inspection.
6. **Stateful ADAA** (Holters 2019) — averages the nonlinear state term inside the implicit (trapezoidal) update; slots into SP-051 WDF circuits.
7. **Cost** — $\mathcal{O}(1)$ per sample (2–3 eval of $F$ + 1 division), deterministic per seed → zero-drift gate compatible; cheaper than SP-049's 16× oversampling.

## Musical Elements Framework
- **PITCH** = preserved exactly; added harmonics stay integer multiples (no inharmonic aliases), so distortion stays in tune at high pitch.
- **RHYTHM** = zero group delay, no filter smearing; distortion compresses attack → sharpens onset accents.
- **HARMONY** = nonlinearity shape selects harmonic spectrum (odd-only symmetric vs. even-rich asymmetric); band-limited so full chords drive cleanly.
- **STRUCTURE** = drive/shape schedule per section (clean → saturated → clipped → folded); continuous drive ramp = smooth saturation arc.
- **TEXTURE** = drive amount is the texture knob; ADAA removes "digital grunge" so high drive stays warm/musical.

## UnitMatrix Integration
- **Rows (Voices)** = bus mode (one ADAA on summed mix) or per-voice mode (independent drive $D_v$ + shape $f_v$ per row).
- **Columns (Sections)** = drive arc $D_s$ + optional shape morph; joins ramp drive continuously.
- **Cells** `{PITCH}` unchanged; `{RHYTHM}` zero-latency accent; `{HARMONY}` harmonic-shaped by $f$; `{TEXTURE}` drive+shape per cell.
- Flow: compose → render clean mono buffers → `adaa1/adaa2` per cell/voice → sum → SP-007/008/009 post.

## Pitfalls documented
1. Zero-denominator NaN (flat segments) → branch to $f(x[n])$.
2. Antiderivative must be continuous/closed-form → tabulate numerically if needed.
3. First-order top-end roll-off (sinc) → use 2nd-order or treble tilt.
4. tanh $F_2$ ($\operatorname{Li}_2$) precision near $x=0$ → Taylor series.
5. Stateful shapes need Holters extension (naive wrapping aliases the state).
6. Sparse input stays sparse → hybridization rule (continuous fill layer).
7. Drive gain must apply before $F$, makeup gain after.

## Quirks hit during execution
- **ID discovery:** highest existing = SP-061 (CLS); file scan (sound_method_SP-061, report_SP-061) confirmed. New ID = **SP-062**.
- **Append point:** detailed sections live at end of file (was line 15513), summary table at lines 91–154. Appended section at end with leading blank line; summary row inserted before the `---` at line 155.
- **Patch pitfall check:** re-read lines 154–156 and confirmed single leading `|` and single backslashes (`\int`, `\mathcal{O}`, `\hat`), no `||` prefix, no `\\` double-escaping.
- **Line-count delta:** 15513 → 15647 = +134 (section 133 lines + summary row 1 line).

## Next free SP ID
**SP-063**
