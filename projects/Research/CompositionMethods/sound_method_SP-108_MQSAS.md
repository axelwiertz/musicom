# McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) — Sound Production Method SP-108

## Overview

**Layer:** absolute (Sound Production — Post-Processing / DSP)
**Candidate code path:** `sound/effects/sinusoidal_modeling.py`
**Target output:** Sinusoidal Resynthesis / Spectral Editing / Partial-Level Transformation

McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) is the foundational sinusoidal modeling technique for audio analysis, spectral editing, and high-quality resynthesis. Unlike the channel vocoder (SP-046), which uses a fixed filter bank, or the phase vocoder (SP-026), which operates on fixed STFT bins, MQSAS tracks the exact frequency, amplitude, and phase of each spectral peak over time, producing a collection of continuous partial trajectories. Unlike SMS (SP-027), which adds a separate stochastic residual model, MQSAS models the entire signal as a sum of sinusoids alone — every sample is reconstructed from partials, with no residual component, making it a pure sinusoidal representation.

MQSAS is the analysis-resynthesis engine behind SPEAR, SNDAN, Lemur, and Loris spectral editing platforms, and is the standard method for high-quality partial editing, time-stretching/pitch-shifting with formant preservation, spectral morphing, and cross-synthesis. It is the analysis counterpart to SP-039 (IFFT Fast Additive Synthesis): SP-039 builds spectra from scratch, while MQSAS extracts them from existing audio.

## Technical Mechanics

The MQSAS pipeline has three stages: **peak detection**, **partial tracking**, and **oscillator bank synthesis**.

### Peak Detection (Analysis)

The input signal $x[n]$ is windowed into overlapping frames of length $M$ with hop size $R$ (typically $M = 4f_s/f_a$, $R = M/4$, where $f_a$ is the minimum analysis frequency). The STFT frame $m$ is:

$$X_m[k] = \sum_{n=0}^{M-1} w[n]\, x[n+mR]\, e^{-j2\pi kn / N}$$

where $w[n]$ is a Hanning/Hamming window and $N$ is the FFT size (zero-padded from $M$ to $N = 2^{\lceil\log_2 M\rceil+1}$ for 2× oversampling).

For each frame, local magnitude maxima are identified. For each candidate peak at bin $k^*$, the three bins $k^*-1, k^*, k^*+1$ with magnitudes $\alpha=|X[k^*-1]|, \beta=|X[k^*]|, \gamma=|X[k^*+1]|$ are fitted to a parabola. The interpolated peak location $p$ (in bins) and refined frequency are:

$$p = \frac{1}{2}\,\frac{\alpha - \gamma}{\alpha - 2\beta + \gamma} \in [-1/2, 1/2]$$

$$f_k = (k^* + p)\,\frac{f_s}{N}$$

The phase at the peak is obtained by evaluating the parabola on the real and imaginary spectra separately, producing a complex interpolated spectral value.

### Partial Tracking

Peaks across frames are matched into continuous partial trajectories via a nearest-neighbor assignment. For each active track $T_i$, predicted frequency $\hat{f}_i^{(m)}$ and amplitude $\hat{A}_i^{(m)}$ are extrapolated. The matching cost:

$$E_{ij} = \sqrt{\left[12\log_2\!\left(\frac{f_j}{\hat{f}_i}\right)\right]^2 + \left[\frac{1}{12}\,20\log_{10}\!\left(\frac{A_j}{\hat{A}_i}\right)\right]^2}$$

tracks are extended, born (new peak > $T_b$ threshold), or die (no match within $\Delta f_{\max}$). The birth threshold is frequency-dependent to compensate for spectral rolloff:

$$T_b(f) = A_{\max} + A_L + A_R\,b^{f/20000}$$

where $A_L = -24$ dB, $A_R = 32$ dB, $b = 0.0075$ (Klingbeil 2005 defaults).

### Cubic Phase Interpolation Synthesis

The signal is resynthesized as the sum of $K$ partials:

$$y[n] = \sum_{i=1}^{K} A_i[n] \cos\big(\theta_i[n]\big)$$

The critical MQ innovation is cubic phase interpolation between analysis frames. At hop interval $t \in [0, R]$, a cubic polynomial:

$$\theta_i(t) = a + bt + ct^2 + dt^3$$

is solved to match both phase and instantaneous frequency at frame boundaries:

$$\theta_i(0) = \phi_i^{(m)},\quad \theta_i'(0) = \omega_i^{(m)}$$
$$\theta_i(R) = \phi_i^{(m+1)},\quad \theta_i'(R) = \omega_i^{(m+1)}$$

The solution:

$$a = \phi_i^{(m)},\quad b = \omega_i^{(m)}$$
$$c = \frac{3}{R^2}(\phi_i^{(m+1)} - \phi_i^{(m)}) - \frac{1}{R}(\omega_i^{(m+1)} + 2\omega_i^{(m)})$$
$$d = \frac{2}{R^3}(\phi_i^{(m)} - \phi_i^{(m+1)}) + \frac{1}{R^2}(\omega_i^{(m+1)} + \omega_i^{(m)})$$

This guarantees $C^1$ continuity (continuous phase and frequency) at every frame boundary, eliminating the clicks and frequency discontinuities of linear-phase interpolation.

**Complexity:** Analysis $\mathcal{O}(N\log N)$ per frame. Synthesis $\mathcal{O}(K)$ per sample.

## Musical Elements Framework

- **PITCH**: Exact pitch preserved from analyzed source. Pitch modification by multiplying all partial frequencies by a constant factor $f_i' = f_i \cdot 2^{\Delta/1200}$. Formant-preserving pitch shift: leave the amplitude envelope $A(f)$ stationary while sliding partials beneath it. No harmonicity assumption -- inharmonic partials retain their ratios.

- **RHYTHM**: Time-stretching implemented by reading partial breakpoint functions at rate $f_s/\beta$. Time-stretch preserves transients and attacks better than the phase vocoder (SP-026) because partial tracking maintains temporal alignment. Per-voice stretch factor $\beta$ controls section-level temporal compression/expansion.

- **HARMONY**: Partial editing enables harmonic restructuring: individual partials can be silenced, amplified, or transposed. Cross-synthesis (source A amplitudes × source B frequencies) produces hybrid spectra. A `harmonic_filter_mask` per section selectively retains/spatializes partial bands.

- **STRUCTURE**: Macro-form is the sequence of per-section processing parameters (pitch shift, stretch factor, partial density, filter mask). Section transitions interpolate parameter sets over a crossfade window. Structural contrast from dramatic filter mask changes.

- **TEXTURE**: Controlled by the number of tracked partials $K$ per frame. Dense textures use 200+ partials; sparse textures use 5-20. The death threshold $T_d$ and birth threshold $T_b$ control textural density: higher thresholds produce sparser, cleaner textures.

## UnitMatrix Integration

**Voices** = independent partial trajectory databases per stem. Each voice $v$ has its own $(\Delta_v, \beta_v, K_{\max}^{(v)}, M_v)$ parameter set from the cell config. Synthesis sums voices independently.

**Sections** = parameter vector $P^{(s)} = \{\Delta^{(s)}, \beta^{(s)}, K_{\max}^{(s)}, T_d^{(s)}, M^{(s)}\}$. Parameters are constant or envelope-driven within a section; interpolated across transitions.

**Cell properties:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| `pitch_shift_cents` | float | cents | $\Delta$, factor on all partial frequencies |
| `time_stretch_factor` | float | ratio | $\beta$, temporal scaling |
| `partial_density` | int | count | $K_{\max}$, max partials per frame |
| `death_threshold_db` | float | dB | $T_d$, amplitude floor for partial retention |
| `harmonic_filter_mask` | array | bool | per-partial silencing |
| `spectral_morph_target` | str | path | second analysis for cross-morph |

**Rendering:** load per-voice partial DB → apply $P_v^{(s)}$ → oscillator bank with cubic phase → sum voices → master mix.

## Pitfalls

1. **Tonalization of noise**: With too few partials, noise sounds like a "swarm of sinusoids." Mitigation: adaptive partial count or combine with SMS residual (SP-027).
2. **Cubic overshoot on frequency jumps**: Abrupt frequency changes can cause chirp artifacts. Mitigation: monotonic frequency constraint on cubic coefficients.
3. **Threshold sensitivity**: Birth/death thresholds are signal-dependent; incorrect tuning causes thinning or noise retention.
4. **Attack smear**: Fixed frame rate may miss rapid transients. Mitigation: smaller hop size or transient-detection pre-layer.
5. **Computational cost**: $\mathcal{O}(K)$ per sample at $K=200$ requires ~9M cosine evaluations/sec. Use IFFT synthesis (SP-039) for preview, oscillator bank for final.
6. **Phase seams at section boundaries**: Abrupt parameter changes cause phase discontinuities. Mitigation: carry oscillator states across boundary or 5-10 ms crossfade.
7. **vs. SP-027 SMS**: MQSAS has no noise residual; prefer SMS for sounds with significant noise (breath, cymbal, ambient). MQSAS for melodic/harmonic voices.

## References

- McAulay, R. J. & Quatieri, T. F. (1986). "Speech Analysis/Synthesis Based on a Sinusoidal Representation." *IEEE Trans. ASSP*, 34(4), 744-754.
- Smith, J. O. & Serra, X. (1987). "PARSHL: An Analysis/Synthesis Program for Non-Harmonic Sounds." *Proc. ICMC*.
- Quatieri, T. F. & McAulay, R. J. (1992). "Shape-Invariant Time-Scale and Pitch Modification of Speech." *IEEE Trans. SP*, 40(3), 497-510.
- Lagrange, M. et al. (2003). "Enhanced Partial Tracking Using Linear Prediction." *Proc. DAFx-03*.
- Klingbeil, M. (2005). "SPEAR: Sinusoidal Partial Editing Analysis and Resynthesis." *Proc. ICMC*.
- Glover, J., Lazzarini, V. & Timoney, J. (2010). "Simpl: A Python Library for Sinusoidal Modelling." *Proc. DAFx-10*.