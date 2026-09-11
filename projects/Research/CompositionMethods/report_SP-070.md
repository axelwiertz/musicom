# Report — SP-070 Feedback Amplitude Modulation Synthesis (FBAM)

- **Method name:** Feedback Amplitude Modulation Synthesis (FBAM)
- **ID:** SP-070
- **Layer:** absolute
- **One-line description:** Nonlinear synthesis where a sinusoidal carrier is amplitude-modulated by its own fed-back output — $y(n)=\cos(\omega_0 n)[1+\beta\,y(n-1)]$ — a periodically linear time-varying one-pole filter whose coefficient is the input signal itself. A single scalar $\beta$ sweeps spectral brightness from a pure sinusoid to a full harmonic pulse train with no spectral holes; six variations add feedforward delay, allpass phase distortion, heterodyning (double-carrier formants), waveshaping (odd/even-harmonic control), non-unitary delay, and decoupled carrier/modulator (adaptive distortion effect). $\mathcal{O}(1)$ per sample (1 mul + 1 add + 1 lookup).
- **Next free SP ID:** SP-071

## Summary-table row (added)

`| **SP-070** | Feedback Amplitude Modulation Synthesis (FBAM) | **Synthesis Engines** | Harmonic-Rich / Formant / Distortion Timbres | Nonlinear synthesis where a sinusoidal carrier is amplitude-modulated by its own fed-back output: $y(n)=\cos(\omega_0 n)[1+\beta\,y(n-1)]$ — a periodically linear time-varying one-pole filter whose coefficient is the input itself. Single scalar $\beta$ sweeps brightness from a pure sinusoid to a full harmonic pulse train with no spectral holes; 6 variations add feedforward delay, allpass phase distortion, heterodyning (double-carrier formants), waveshaping (odd/even-harmonic control), non-unitary delay, and decoupled carrier/modulator (adaptive distortion effect). $\mathcal{O}(1)$ per sample (1 mul + 1 add + 1 lookup); the feedback-amplitude cousin of FM SP-010/017 and phase distortion SP-030. |`

## Line-count delta

- Before: 17093
- After (summary row + detail section): 17187
- Delta: +94

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-070_fbam.md`
- Report: `/opt/data/projects/Research/CompositionMethods/report_SP-070.md`
- DB: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row line 171, detail header line 17095)

## Candidate code path

`sound/synthesis/fbam.py` (sibling to `phase_mod.py`, `dx7_voice.py`, `west_coast.py`, `karplus_strong.py`); the adaptive-effect mode (Variation 6) also fits `sound/effects/` as a coefficient-modulated distortion.

## Technical mechanics summary

1. Basic equation $y(n)=\cos(\omega_0 n)[1+\beta y(n-1)]$ — feedback AM oscillator (one mul, one add, one table lookup per sample).
2. PLTV interpretation: $y(n)=x(n)+a(n)y(n-1)$ with $x(n)=a(n)=\cos(\omega_0 n)$; GTF $H(\omega,n)=\frac{1+\sum b_k(n)e^{-jk\omega}}{1-a_N e^{-jN\omega}}$.
3. Infinite expansion $y(n)=\sum_k\prod_m\cos[\omega_0(n-m)]$ → pure harmonic series, low-pass shape, ~$2^{-k}$ decay.
4. Stability: $|\beta a_N|<1$; aliasing is the practical $\beta$ limit; oversampling / cubed-cosine modulator widens it.
5. Scaling: per-$\beta$ polynomial gain, 2-D $(\beta,f_0)$ LUT, or RMS balancer.
6. Six variations: V1 feedforward delay, V2 allpass (phase distortion), V3 heterodyning (in/out-loop, double-carrier formants), V4 waveshaping (cos→feedback-FM partial, ABS→odd-only), V5 non-unitary delay (closed form at $D=f_s/f_0$), V6 decoupled filter (adaptive effect).
7. Applications: subtractive-without-filters, vocal formant stacks, abstract physical modeling, adaptive distortion.

## Quirks / pitfalls hit during this run

1. **`file` and `pdftotext` binaries absent** from the minimal cron image — the Springer PDF fetch returned a 3 KB HTML challenge page and the direct PDF couldn't be inspected with system tools. Resolved by installing `pypdf` into `$MUSICOM_PYTHON` (`pip install pypdf`) and extracting the full 18-page paper text from the open-access MURAL (Maynooth) repository copy at `https://mural.maynoothuniversity.ie/id/eprint/4193/1/VL_feedback.pdf`.
2. **Wikipedia has no FBAM article** ("Feedback amplitude modulation synthesis" is a red link). Switched to DuckDuckGo HTML search → found the canonical Aalto FBAM page (`research.spa.aalto.fi/publications/papers/jasp-fbam/`) and the primary paper; the Aalto page yielded the abstract, variations, sound examples, and cost table directly.
3. **LaTeX double-escape pitfall (known)** — verified post-patch: line 171 has `0` occurrences of `\\` (double-backslash) and column 1–3 reads `| *` (single pipe + space, no `||` prefix). Clean.
4. **ONE-TREE symlink** — `write_file`/`patch` resolved to `/opt/data/repos/musicom/projects/Research/CompositionMethods/...` (symlink target of `/opt/data/projects/Research/...`); identical resolution, no action needed.
5. **ID resolved dynamically, not assumed** — scanned summary table (`SP-069` max) + `sound_method_SP-*.md` / `report_SP-*.md` (both max at SP-069) + `grep -c "SP-070"` == 0. New ID = SP-070, matching the prior report's own "Next free SP ID: SP-070".

## Appendix — complete section text appended

See `methods_db.md` lines 17095–17186 (header `# Feedback Amplitude Modulation Synthesis (FBAM) (Method SP-070)` through References). Standalone expanded version (with NumPy sketch) in `sound_method_SP-070_fbam.md`.
