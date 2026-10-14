# Report: SP-114 — Spectral Dynamics Compression/Expansion (SDCX)

## Metadata

| Field | Value |
|---|---|
| **Method ID** | SP-114 |
| **Method Name** | Spectral Dynamics Compression/Expansion (SDCX) |
| **Layer** | absolute — Post-Processing / DSP |
| **One-line description** | STFT-domain dynamics processor that applies independent compression, expansion, limiting, and gating to each of $N$ perceptually-scaled frequency bands (ERB grouping), with per-band threshold, ratio, attack, release, and knee parameters. |
| **Standalone file** | `sound_method_SP-114_SDCX.md` |
| **Report file** | `report_SP-114.md` |
| **Candidate code path** | `sound/effects/spectral_dynamics.py` |
| **Acronym** | SDCX |

## Summary-table row (inserted at line 297)

```
|| **SP-114** | Spectral Dynamics Compression/Expansion (SDCX) | **Post-Processing / DSP** | Spectral Dynamics / Per-Band Compression, Expansion & Gating | STFT-domain dynamics processor that applies independent compression, expansion, limiting, and gating to each of $N$ perceptually-scaled frequency bands (ERB grouping). Per-band threshold, ratio, attack, release, and knee parameters. Frame-by-frame STFT analysis → band grouping → level detection → gain computer → magnitude masking → ISTFT overlap-add. Preserves phase. $O(W \log W + B)$ per hop. Candidate: `sound/effects/spectral_dynamics.py`. |
```

## Line counts

| State | Lines |
|---|---|
| Before append | 25,274 |
| After append | 25,452 |
| Delta | +178 (+1 summary row + ~155 detailed section text + padding) |

## Database verification

- **Summary row** found at line 297 (grep for `SP-114` in summary table area).
- **Detailed section** found at line 25,277 (grep for `### SP-114`).
- Both confirm successful insertion in the `methods_db.md` Sound Production Methods Framework section.

## Next free SP ID

SP-115 (current max = SP-114).

## SP ID resolution

- Summary table rows scanned from line 190–297 (SP-001 through SP-114).
- File cross-check against `sound_method_SP-*.md`: highest existing = SP-113 (PBES) and SP-114 (SDCX, just created).
- Report file cross-check: highest existing = SP-113. SP-114 is new.
- No duplication — SP-114 is genuinely new.

## Technical mechanics summary

SDCX operates as an STFT-domain dynamics processor with 7 stages:

1. **STFT Analysis** — Hann-windowed frames, 2048–8192 pt FFT, 75% overlap
2. **Band Grouping** — FFT bins grouped into $B \approx 20–40$ ERB perceptual bands (or full-bin mode $B = W/2+1$)
3. **Envelope Detection** — Classic analog-style per-band peak/RMS follower with independent attack/release
4. **Gain Computer** — Per-band DRC curve with threshold, ratio, knee, supporting downward/upward/limit/gate modes
5. **Temporal Smoothing** — One-pole IIR per band to suppress zipper noise
6. **Magnitude Masking** — Gains interpolated to bin resolution, applied to magnitude while preserving phase
7. **ISTFT Resynthesis** — Inverse FFT + overlap-add

Complexity: $\mathcal{O}(W \log W + B)$, dominated by two FFTs per frame.

## Quirks and pitfalls hit

1. **Patch double-escape issue**: In the original DB, some lines had `\\` (double-escaped LaTeX) and some had single-escaped `\`. The patch normalized these. Verified the SP-114 row uses single `\` for LaTeX.
2. **Summary table format**: Some previous rows had `| **SP-NNN** |` (missing the leading `|` — just one pipe). The patch fixed SP-111, SP-112, SP-113 to `|| **SP-NNN** |` format. Verified SP-114 has the correct `|| **SP-NNN** |` format.
3. **Off-by-one in SP resolution**: The sound_method files go up to SP-113, but the summary table showed some missing SP rows (e.g., SP-076 was a composition method, not SP). File scan (not just table scan) was the authoritative source — confirmed SP-113 was highest.

## Appendix: Complete section text appended

The full detailed section (### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration, ### Pitfalls) was appended to `methods_db.md` under the Sound Production Methods Framework section and is reproduced verbatim in the standalone file `sound_method_SP-114_SDCX.md`.

## Related methods

- SP-008 (DRC): broadband single-stage — SDCX is granular by frequency.
- SP-026 (Phase Vocoder): same STFT pipeline, different modification (time/pitch shift).
- SP-031 (Spectral Cross-Synthesis): same STFT pipeline, different modification (envelope transfer between signals).
- SP-050 (Spectral Delay): same STFT pipeline, different modification (delay per bin).
- SP-072 (HPSS): source separation, not dynamics.
- SP-103 (Crossover Band Distortion): multiband crossover + distortion — SDCX uses STFT for zero-crossover-phase.
- SP-109 (Spectral Gating / Noise Reduction): noise floor suppression — SDCX uses classic DRC curve, not noise floor.