# Report: SP-115 — Auto-Wah / Envelope-Controlled Filter Synthesis (AWEFS)

## Metadata

| Field | Value |
|---|---|
| **Method ID** | SP-115 |
| **Method Name** | Auto-Wah / Envelope-Controlled Filter Synthesis (AWEFS) |
| **Layer** | absolute — Post-Processing / DSP |
| **One-line description** | Envelope follower modulates a resonant filter cutoff in response to input dynamics. Signal amplitude controls filter frequency via asymmetric attack/release level detection, creating a vowel-like automatic wah-wah effect without pedal control. |
| **Standalone file** | `sound_method_SP-115_AWEFS.md` |
| **Report file** | `report_SP-115.md` |
| **Candidate code path** | `sound/effects/envelope_filter.py` |
| **Acronym** | AWEFS |

## Summary-table row (inserted at line 299)

```
|| **SP-115** | Auto-Wah / Envelope-Controlled Filter Synthesis (AWEFS) | **Post-Processing / DSP** | Dynamic Filter Sweep / Envelope-Controlled Wah Effect | Envelope follower modulates a resonant filter cutoff in response to input dynamics. Signal amplitude controls filter frequency via asymmetric attack/release level detection, creating a vowel-like automatic wah-wah effect without pedal control. Lowpass/bandpass/peaking filter modes; per-voice or shared-bus configuration. $\mathcal{O}(1)$ per sample. Candidate: `sound/effects/envelope_filter.py`. |
```

## Line counts

| State | Lines |
|---|---|
| Before append | 25,515 |
| After append | 25,773 |
| Delta | +258 (+1 summary row + ~257 detailed section text) |

## Database verification

- **Summary row** found at line 299 (grep for `SP-115` in summary table area).
- **Detailed section** found at line 25,519 (grep for `### SP-115`).
- Both confirm successful insertion in the `methods_db.md` Sound Production Methods Framework section.

## Next free SP ID

SP-116 (current max = SP-115).

## SP ID resolution

- Summary table rows scanned from line 195–299 (SP-001 through SP-115).
- File cross-check against `sound_method_SP-*.md`: highest existing = SP-114 (SDCX). SP-115 is new.
- Report file cross-check: highest existing = SP-114. SP-115 is new.
- No duplication — SP-115 is genuinely new.

## Technical mechanics summary

AWEFS operates as a sample-by-sample or block-based DSP effect with 4 stages:

1. **Envelope Follower** — Dual-time-constant asymmetric level detector: fast attack (1–10 ms), slower release (50–500 ms). Rectified input → one-pole lowpass per time constant.
2. **Cutoff Map** — Normalized envelope (0–1) scaled by sensitivity and frequency range to produce instantaneous cutoff $f_c[n] = f_{\min} + s \cdot \hat{e}[n] \cdot (f_{\max} - f_{\min})$.
3. **Resonant Biquad** — Three modes (lowpass/bandpass/peaking) per RBJ cookbook. Coefficients recalculated every $N_{\text{block}}$ samples with linear interpolation to prevent zipper noise.
4. **Dry/Wet Mix** — Parallel blend of original dry and processed wet signals.

Key parameters: $f_{\min}$ (180–400 Hz), $f_{\max}$ (1500–3000 Hz), Q (0.5–20), sensitivity (0–1), $\tau_A$ (1–10 ms), $\tau_R$ (50–500 ms), filter mode (LP/BP/peaking), mix (0–1).

Complexity: $\mathcal{O}(1)$ per sample.

## Quirks and pitfalls hit

1. **Patch double-escape issue**: The initial patch double-escaped `$\mathcal{O}$` to `$\\mathcal{O}$` in the summary table row. Fixed with a second patch. The LaTeX backslash `\` in `\mathcal` must be written as a single `\` in the file, not `\\`.
2. **Missing newline before detailed section**: The `cat >>` append joined the detailed section directly to the last line of the PNC pitfalls without a blank line separator. Fixed with a patch that inserted `\n\n` between "atonality." and "### SP-115 —".
3. **Patch destroyed row**: The first attempt to fix the LaTeX double-escape accidentally removed the beginning of the SP-115 row. Fixed by restoring the full row from SP-113 through SP-115 in a single patch operation.
4. **Summary table format variance**: The SP summary table has inconsistent leading-pipe formatting (`||`, `|||`, `||||`). Used `|| **SP-115** |` which matches the majority of entries around it.

## Appendix: Complete section text appended

The full detailed section (### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration, ### Pitfalls) was appended to `methods_db.md` under the Sound Production Methods Framework section and is reproduced verbatim in the standalone file `sound_method_SP-115_AWEFS.md`.

## Related methods

- **SP-020 (ZDF State Variable Filter)**: provides the underlying filter technology but no envelope-follower modulation. AWEFS can use ZDF as its filter kernel.
- **SP-029 (Subtractive Synthesis)**: uses LFO or static filter on oscillator — AWEFS uses input-signal envelope for modulation.
- **SP-059 (FDLMS)**: modulated delay effects (chorus/flanger/vibrato), no envelope-controlled filter.
- **SP-106 (Phaser / APS)**: allpass-based notch-sweep via phase cancellation — AWEFS uses resonant-filter magnitude sweep.
- **SP-008 (DRC)**: broadband level-based dynamics — AWEFS is frequency-selective.
- **SP-006 (Humanization)**: micro-timing jitter — no frequency-selective processing.