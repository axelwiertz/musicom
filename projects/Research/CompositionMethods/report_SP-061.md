# Report — SP-061 Cepstral Liftering Synthesis (CLS)

## Summary
- **Method name:** Cepstral Liftering Synthesis (CLS)
- **ID:** SP-061
- **Layer:** Synthesis Engines
- **One-line description:** Deconvolves a sound into excitation (source) and resonator (spectral envelope) via the complex cepstrum $\hat{x}=\mathcal{F}^{-1}\{\log X[k]\}$, which turns convolution into addition; a lifter separates the two components exactly (phase preserved), and cross-synthesis recombines one sound's excitation with another's resonator. The exact-deconvolution counterpart to SP-028 LPC and the phase-preserving foil to SP-031 magnitude cross-synthesis.

## Line counts
- **Before:** 15112 lines
- **After:** 15281 lines
- **Delta:** +169 lines

## Summary-table row (appended at line 152)
| **SP-061** | Cepstral Liftering Synthesis (CLS) | **Synthesis Engines** | Homomorphic Source/Resonator Deconvolution / Cross-Synthesis Timbres | Deconvolves a sound into excitation (source) and resonator (spectral envelope) via the complex cepstrum $\hat{x}=\mathcal{F}^{-1}\{\log X[k]\}$, which turns convolution into addition and lands the two components in disjoint quefrency regions. Liftering (quefrency-domain windowing) separates them exactly with phase preserved; cross-synthesis recombines one sound's excitation with another's resonator. The exact-deconvolution counterpart to SP-028 LPC and the phase-preserving foil to SP-031 magnitude cross-synthesis. |

## Standalone file
`/opt/data/projects/Research/CompositionMethods/sound_method_SP-061_CLS.md`

## Append workflow
1. `write_file` full section → `_temp_sp061.md` (21885 bytes).
2. `printf '\n' >> methods_db.md && cat _temp_sp061.md >> methods_db.md` then `rm _temp_sp061.md`.
3. `patch` (replace mode) inserted the SP-061 summary row immediately after the SP-060 row, before the `---` separator.

## Verification
- `wc -l methods_db.md` → **15281** lines (was 15112).
- `grep SP-061` → 4 hits: summary row (line 152), detailed-section header (line 15115), Python docstring (line 15200), comparison-table row (line 15271).

## Technical mechanics summary
1. **Three cepstra** — power $C_p[q]=|\mathcal{F}^{-1}\{\log|X|^2\}|^2$; real $C_r[q]=\mathcal{F}^{-1}\{\log|X|\}$; complex $\hat{x}[n]=\mathcal{F}^{-1}\{\log|X|+j\angle X\}$ (phase-preserving, the synthesis workhorse).
2. **Homomorphic theorem** — $x=e*h \Rightarrow \hat{x}=\hat{e}+\hat{h}$; $\hat{h}$ (envelope) at low quefrency, $\hat{e}$ (excitation) at high quefrency (rahmonics at $k q_0$).
3. **Liftering** — quefrency-domain window $\ell_{low}+\ell_{high}=1$ separates source and resonator; cutoff $Q_c$ decides the timbre/pitch boundary.
4. **Cross-synthesis** — $y=\mathcal{F}^{-1}\{\exp(\mathcal{F}\{\hat{e}_A+\hat{h}_B\})\}$ = A's pitch/voicing + B's timbre, phase preserved (no Griffin-Lim).
5. **Envelope morph** — $\hat{h}(\tau)=(1-\tau)\hat{h}_A+\tau\hat{h}_B$, linear cepstral interpolation = formant glide.
6. **Quefrency control** — peak at $q_0 \Rightarrow f_0=f_s/q_0$ (pitch detection); rahmonic at $q=\tau_{echo}$ = echo insert/remove.
7. **Complexity** — $\mathcal{O}(N\log N)$ per frame; fully deterministic → zero-drift gate compatible.

## Musical Elements Framework
- **PITCH** = excitation rahmonic spacing $q_0=1/f_0$ (cross-synthesis transplants A's pitch into B's resonator); cepstral pitch detection enables formant-preserving re-synthesis.
- **RHYTHM** = excitation schedule (cell onset grid); source type sets attack (pulse=sustained, impulse=pluck, noise=breathy).
- **HARMONY** = resonator formant structure (chord = multi-formant envelope or per-note resonator bank); harmonic resonator = tonal gravity, inharmonic = metallic.
- **STRUCTURE** = resonator schedule $\hat{h}_s$ per section + lifter-cutoff arc $Q_{c,s}$; cepstral envelope interpolation at section joins.
- **TEXTURE** = lifter cutoff (short=smooth/mellow, long=bright/granular) + excitation noise mix + rahmonic echo add/remove.

## UnitMatrix Integration
- **Rows** = independent CLS voices (each: excitation schedule × its own resonator $\hat{h}_v$).
- **Columns** = timbral arc $\hat{h}_s$; joins morph the cepstrum linearly.
- **Cells** `{PITCH}`=excitation f0, `{RHYTHM}`=onset grid/source type, `{HARMONY}`=resonator formants, `{TEXTURE}`=lifter cutoff + noise mix.

## Pitfalls documented
1. Phase-unwrap failure → warbly output (always `np.unwrap`).
2. $\log(0)$ blow-up at spectral nulls → add floor (eps / −120 dB).
3. Lifter edge ringing → comb artifacts (raised-cosine taper).
4. Cepstral aliasing/rahmonic foldover → choose nfft > longest quefrency.
5. Pure sine = no rahmonic → pitch split fails (fall back to ACF/ZC).
6. Real cepstrum only inverts minimum-phase → use complex cepstrum for synthesis.
7. Sparse excitation → staccato (hybridization rule: add continuous fill + silent padding event).
8. Stochastic excitation breaks determinism → seed noise per cell (mirror DDIM $\eta=0$ convention).

## Quirks hit during execution
- **ID discovery:** the task brief assumed SP-044 was the highest and the new method SP-045, but the DB had already advanced to SP-060 (DDAS, appended 2026-09-01). Re-derived the correct next ID = **SP-061** from the actual table + detailed-section headers.
- **Append point:** the detailed sections live at the *end* of the file (line 15112), not adjacent to the summary table (line 151). Appended after the last reference line of SP-060/RBM-C with a leading blank line; the summary row went at line 152 before the `---`.
- **Patch pitfall check:** confirmed the new row has a single leading `|` and single `\` backslashes (no `||` prefix, no `\\` double-escaping).

## References
- Bogert, Healy & Tukey (1963), "The Quefrency Alanysis of Time Series for Echoes…", *Proc. Symp. Time Series Analysis*, Wiley.
- Oppenheim (1965), "Superposition in a class of nonlinear systems", Ph.D. diss., MIT RLE.
- Oppenheim & Schafer (1975), *Digital Signal Processing*, Prentice-Hall.
- Childers, Skinner & Kemerait (1977), "The Cepstrum: A Guide to Processing", *Proc. IEEE* 65(10), 1428–1443.
- Oppenheim & Schafer (2004), "From frequency to quefrency", *IEEE Signal Processing Magazine* 21(5).
- Randall (2017), "A history of cepstrum analysis…", *MSSP* 97.
- Oppenheim & Schafer (2009), *Discrete-Time Signal Processing*, 3rd ed.
