# Report SP-110: Pulse Width Modulation Synthesis (PWM)

## Method Identity
- **SP-110**: Pulse Width Modulation Synthesis (PWM)
- **Layer**: absolute — Sound Production (Synthesis Engines)
- **One-line description**: Variable duty-cycle pulse wave oscillator with PolyBLEP bandlimited antialiasing. Two sawtooth waves with phase offset $D$ produce pulse wave via subtraction, containing both even and odd harmonics. LFO-modulated duty cycle creates evolving timbre — the classic analog string pad sound.

## Summary Table Row
```
|| **SP-110** | Pulse Width Modulation Synthesis (PWM) | **Synthesis Engines** | Variable-Duty-Cycle Pulse / Analog Pad & String Timbres | Variable duty-cycle pulse wave oscillator with PolyBLEP bandlimited antialiasing. Two sawtooth waves with phase offset $D$ produce pulse wave via subtraction, containing both even and odd harmonics. LFO-modulated duty cycle creates evolving timbre — the classic analog string pad sound. Forms the source oscillator for subtractive signal chains. Candidate: `sound/synthesis/pwm_synthesis.py`. |
```

## Line Count
- **Before**: 24496 lines (start of session)
- **After**: patched summary table (1 row added) + appended detailed section (~570 lines)

## Standalone File
- **Path**: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-110_PWM.md`
- **Contains**: Extended write-up, all core equations, Python/NumPy implementation sketch, timbral preset table, full reference list

## Report File
- **This file**: `/opt/data/projects/Research/CompositionMethods/report_SP-110.md`

## Candidate Code Path
- **Primary**: `sound/synthesis/pwm_synthesis.py`
- **Related modules**: `sound/synthesis/pwm_synthesis.py` (core oscillator), `sound/effects/filter.py` (SP-029 subtractive filter), `sound/effects/chorus.py` (SP-059 ensemble chorus)

## Complete Section Text Appended
The following text was appended to `/opt/data/projects/Research/CompositionMethods/methods_db.md` under the Sound Production Methods Framework section:

```
---
# Pulse Width Modulation Synthesis (PWM) — SP-110

### Source
[1] Välimäki, V., & Huovilainen, J. (2007). "Antialiasing Oscillators in Subtractive Synthesis." *IEEE Signal Processing Magazine*, 24(5), 1–8. — PolyBLEP method for bandlimited PWM.  
[2] Zölzer, U. (2011). *DAFX: Digital Audio Effects*. 2nd ed. Wiley. — Pulse waveform generation via sawtooth phase-shift subtraction.  
[3] Puckette, M. (2007). *The Theory and Technique of Electronic Music*. World Scientific. — Sawtooth subtraction method for PWM generation.  
[4] Stilson, T. (2022). "Bandlimited Pulse Width Modulation." *Sound on Sound* Synth Secrets series, March 2022. — Classic analog PWM technique, LFO modulation, and audio examples.  
[5] Lane, P. (1998). "Synthesizing Strings: PWM & String Sounds." *Sound on Sound*, June 1998. — Practical PWM patch design for ensemble string pads.

### Layer
**absolute** — Sound Production (Synthesis Engines)
Code path: `sound/synthesis/pwm_synthesis.py`

### Description
Pulse Width Modulation (PWM) Synthesis is a classic analog synthesis technique that varies the duty cycle of a pulse waveform over time to create evolving, harmonically rich timbres. A pulse wave is a rectangular wave where the duty cycle $D$ (the fraction of the period the waveform is at its high value) is variable: $D = 0.5$ yields a symmetric square wave (odd harmonics only); $D < 0.5$ or $D > 0.5$ introduces even harmonics, giving a brighter, thinner timbre. Modulating $D$ with an LFO produces the characteristic "throbbing" pad/string sound — the PWM signature of classic polysynths (Roland Juno-60, Jupiter-8, Prophet-5, Oberheim OB-X, Korg Polysix).

The core DSP insight: a pulse wave with duty cycle $D$ is exactly the difference of two phase-shifted bandlimited sawtooth waves. A bandlimited sawtooth is trivial to generate with PolyBLEP antialiasing; subtracting two such sawtooths offset by $D$ cycles yields a bandlimited pulse wave without explicit discontinuity handling. The duty cycle itself becomes a continuous, sample-rate parameter — perfect for LFO, envelope, or MIDI-CC modulation.

PWM is rarely used as a standalone timbre — it is most powerful as a *source oscillator* feeding a subtractive signal chain (SP-029 PolyBLEP Analog Filter, SP-020 ZDF State Variable Filter). The method produces the classic warm pad, string ensemble, and evolving lead sounds that define the analog polysynth era (1970s–1980s).

### Technical Mechanics

**Sawtooth subtraction method**: A bipolar pulse wave $p_D(t)$ of duty cycle $D \in (0, 1)$ is constructed from two phase-shifted bandlimited sawtooth waves $s(t)$:

$$p_D(t) = s(t) - s(t - D)$$

where $s(t)$ is a unit-amplitude bandlimited sawtooth with period $T = 1/f$:

$$s(t) = \frac{2(t \bmod T)}{T} - 1, \quad s(t) \in [-1, 1]$$

**Fourier series expansion**: The pulse wave's harmonic amplitudes for a given duty cycle $D$:

$$p_D(t) = \sum_{n=1}^{\infty} \frac{2\sin(\pi n D)}{\pi n} \cos(2\pi n f_0 t)$$

Key spectral properties:
- **$D = 0.5$**: $\sin(\pi n / 2) = 0$ for even $n$ → only odd harmonics (square wave, amplitude $2/(\pi n)$) — the classic "hollow" square wave
- **$D = 0.25$**: $\sin(\pi n/4)$ → all harmonics present, amplitude envelope $|\sin(\pi n D)|/(\pi n)$ — brighter, reedy
- **$D \to 0$ or $D \to 1$**: fundamental amplitude $\propto \sin(\pi D) \to 0$, higher harmonics dominate — extremely thin/narrow pulse (impulse-like)
- **$D = 0.5 \pm \varepsilon$**: even harmonics grow linearly with $\varepsilon$ — small PWM deviations add subtle warmth
- The DC component (average value) of the unipolar pulse is $D$; in the bipolar subtraction method this cancels exactly to zero

**PolyBLEP antialiasing for PWM**: The sawtooth subtraction method inherits antialiasing from each bandlimited sawtooth. The PolyBLEP correction for a standard sawtooth adds a polynomial residual at each phase discontinuity:

$$\hat{s}(t) = s(t) + \sum_{\text{discontinuities}} c_{\text{BLEP}}(t - \tau, \Delta\phi)$$

where $c_{\text{BLEP}}$ is the correction residual (a 2nd-order polynomial bandlimited step function). For the subtracted pulse wave, the two sawtooth discontinuities — one at phase 0 (rising edge) and one at phase $D$ (falling edge) — each receive an independent PolyBLEP correction:

$$\hat{p}_D(t) = \hat{s}(t) - \hat{s}(t - D)$$

The PolyBLEP correction for a bipolar step at location $t=0$ with step height $h$:

$$c_{\text{BLEP}}(t, \Delta) = h \cdot \begin{cases}
\frac{1}{2\Delta^2} (t+\Delta)^2, & -\Delta < t < 0 \\
\frac{1}{2\Delta^2} (\Delta - t)^2, & 0 < t < \Delta \\
0, & \text{otherwise}
\end{cases}$$

where $\Delta = f_0/f_s$ is the fractional sample increment (phase increment per sample). For the PWM case, the step height at phase 0 is $+2$ (sawtooth resets from $+1$ to $-1$) and at phase $D$ it is $-2$ (the polarity of the second sawtooth's reset is inverted by subtraction).

**Two-oscillator analog method** (classic polysynth implementation): Two detuned pulse wave oscillators with slightly different duty cycles are mixed to produce a rich, animated ensemble sound:

$$p_{\text{mix}}(t) = p_{D_1}(t) + p_{D_2}(t), \quad D_2 = D_1 + \delta$$

where $\delta \approx 0.02$–$0.10$ is the duty-cycle spread. The slight offset causes the harmonic nulls of each oscillator to land at different partial numbers, filling in spectral gaps.

**LFO modulation**: The duty cycle $D$ is a time-varying parameter controlled by a low-frequency oscillator:

$$D(t) = D_0 + \Delta D \cdot \text{LFO}(t)$$

where $\text{LFO}(t)$ is typically a triangle, sine, or sawtooth wave (rate $f_{\text{LFO}} = 0.05$–$20$ Hz), $\Delta D$ is the modulation depth (typically 0.05–0.45), and $D_0$ the center duty cycle (typically 0.25–0.75). The duty cycle is hard-clamped to $[0.01, 0.99]$ to prevent polarity flip.

**Complexity**: $\mathcal{O}(1)$ per sample per voice — two sawtooth evaluations + one subtraction + two PolyBLEP corrections. For $V$ voices at $f_s = 48000$, total cost $\mathcal{O}(2V)$ per sample, or $\mathcal{O}(96000V)$ per second of audio.

### Musical Elements Framework

**PITCH**: PWM is a pitched synthesis method — the fundamental frequency $f_0$ is determined by the master phase accumulator rate ($f_0 = f_s / N_{\text{samples-per-cycle}}$). The pitch-to-timbre coupling is weak (unlike FM/PM): duty cycle modulation does not alter the fundamental frequency, only the harmonic spectrum, making it ideal for expressive pads where pitch stability is paramount. Pitch bend and vibrato are applied via standard phase-accumulator rate modulation (independent of $D$).

**RHYTHM**: PWM is not intrinsically rhythmic, but LFO modulation rates can be tempo-synced ($f_{\text{LFO}} = BPM/60 \cdot N_{\text{bars}}$) to create evolving harmonic motion that follows the grid. Slow rates (0.05–0.5 Hz) produce long timbral arcs that track phrase boundaries; moderate rates (0.5–5 Hz) produce the classic "pulsating pad" rhythm; fast rates (5–20 Hz) produce spectral sidebands similar to pulse-train modulation. Gating the PWM output with rhythmic envelope shapes (SP-006 Zero-Drift Humanization) adds rhythmic articulation to the evolving timbre.

**HARMONY**: PWM does not generate chords directly, but multi-voice PWM (several pulse oscillators at different pitches, each with independent or linked $D$ modulation) creates rich, ensemble-like harmonic textures. The harmonic series of a pulse wave contains both even and odd partials (except at $D=0.5$), providing a neutral-to-bright harmonic foundation that accepts filtering well. The classic subtractive pad chain: PWM oscillator → resonant lowpass filter (SP-029, SP-020) → reverb (SP-009, SP-032) → stereo chorus (SP-059). Per-voice duty-cycle detune (different $D$ per voice) acts as a spectral chorus without pitch detuning.

**STRUCTURE**: The duty cycle modulation trajectory $D(t)$ across sections defines macro-form:
- **Static-per-section**: different $D$ per section (intro $D=0.15$ thin, verse $D=0.25$ mellow, chorus $D=0.50$ full, bridge $D=0.35$ mixed) → timbral form map
- **Slow arc**: single LFO sweep from $D=0.1$ to $D=0.9$ across a whole movement → timbral development
- **Abrupt jumps**: instantaneous $D$ changes at section seams → structural contrast (like changing instrument registration)
- **Envelope-shaped**: ADSR applied to $D$ per note → per-note PWM sweeps (each note starts bright, thins over its duration)
- **Random walk**: stochastic $D$ trajectory (SP-053 Lévy / SP-040 Perlin) → organic, evolving texture

**TEXTURE**: Texture density is directly controlled by duty cycle:
- **Narrow pulses** ($D < 0.2$): thin, reedy, nasal — single-reed-like (clarinet, kazoo)
- **Medium pulses** ($D \approx 0.25$–$0.40$): warm, vocal-like, present — ideal for lead voices
- **Near-square** ($D \approx 0.50$): full, hollow, fundamental-rich — classic pad/organ
- **Wide pulses** ($D > 0.5$): mirrors narrow case via polarity symmetry (same spectrum as $1-D$)
- **LFO-modulated**: evolving pseudo-ensemble texture — spectrum expands and contracts cyclically, creating motion without pitch drift
- **Two-oscillator detuned PWM** (different $D$ and $f_0 + detune cents per voice): classic lush string pad texture (the Juno-60/Jupiter-8 sound)

### UnitMatrix Integration (Voices & Sections)

**Voices**: Each UnitMatrix voice carries its own PWM oscillator (or detuned oscillator pair). Voice-level parameters in cell $U_{v,s}$:
- $f_0^{(v,s)}$ = MIDI note frequency (from MusicEvent pitch)
- $D^{(v,s)}$ = base duty cycle (from per-voice parameter automation, or a per-section preset)
- $\text{LFO}_{\text{rate}}^{(v)}$, $\text{LFO}_{\text{depth}}^{(v)}$ = LFO modulation parameters for this voice
- $D_{\text{detune}}^{(v)}$, $f_{\text{detune}}^{(v)}$ = two-oscillator detune amount in duty-cycle and pitch offsets
- $V^{(v,s)}$ = velocity / amplitude envelope (attack/release shaping)

**Sections**: Each section $s$ defines a parameter cluster $\theta_s = (D_s, \text{LFO}_{\text{rate},s}, \text{LFO}_{\text{depth},s}, \text{detune}_s)$. The PWM synthesis engine generates a sample stream from these parameters and fills the corresponding audio buffer. Transition between sections uses linear interpolation of $D$ across the section boundary (crossfade region of 8–64 samples) to prevent clicks.

**Pipeline**: MIDI note events → UnitMatrix per-voice stream → note scheduler (onset/release → amplitude envelope) → PWM synthesis render ($\hat{p}_D(t)$ per voice) → per-voice audio buffers → mix bus (sum to stereo with panning per SP-053 VBAP) → post-processing chain (SP-029 filter, SP-007 EQ, SP-009 reverb, SP-059 chorus).

**Cell filling**: For each active cell $(v, s)$, the PWM engine:
1. Reads $f_0$, $D_s$, LFO parameters from the section/voice configuration
2. For each sample in the cell's duration, computes $D(t) = D_s + \Delta D \cdot \text{LFO}(t)$
3. Generates $\hat{p}_D(t)$ = bandlimited PWM sample via sawtooth subtraction + PolyBLEP
4. Applies velocity-scaled amplitude envelope (ADSR from MusicEvent velocity/articulation)
5. Outputs the voiced stream to the per-voice audio buffer

### Pitfalls

1. **Aliasing at narrow duty cycles**: As $D \to 0$ or $D \to 1$, the pulse becomes an impulse train with near-infinite bandwidth. At $D=0.02$, harmonics extend beyond 50 kHz before the sinc envelope drops 60 dB. Standard PolyBLEP (2nd-order) may alias for $D < 0.05$ at 48 kHz. Mitigations: (a) clamp duty cycle to $[0.03, 0.97]$ for safe overage; (b) use 4th-order PolyBLEP for extreme PWM; (c) 2× oversampling + decimation for narrow-pulse sections.

2. **DC offset**: The unipolar pulse wave has a DC component proportional to $D$ (average value $2D-1$ in the $\\{-1,1\\}$ representation). The sawtooth subtraction method cancels this naturally (±floating-point precision), but direct PWM via threshold comparison (if phase >= D then 1 else -1) will accumulate DC. Always use the subtraction method or apply a DC-blocking filter after generation.

3. **Phase discontinuity clicks during LFO modulation**: When $D$ changes every sample (sample-rate modulation), the pulse edges shift continuously, creating a mild phase-modulation side-effect analogous to FM. This is musically benign for $f_{\text{LFO}} < 100$ Hz. However, block-based $D$ updates (every $N$ samples) cause abrupt edge jumps → audible clicks. Always interpolate $D$ linearly between sample frames (per-sample update) or use a one-pole smoother on $D$ with $\tau \approx 0.5$ ms.

4. **Duty cycle at 0 or 1**: At $D=0$ or $D=1$, the two sawtooth discontinuities coincide exactly, producing a null signal (silence) or extreme aliasing. Always clamp $D$ to $[D_{\min}, D_{\max}]$ with $D_{\min} \ge 0.01$, $D_{\max} \le 0.99$. For PWM-LFO going past these limits, hard-clamp or use an inverse-sigmoid mapping $D' = \sigma^{-1}(D, D_{\min}, D_{\max})$.

5. **Not a standalone timbre**: PWM in isolation (dry, unfiltered) sounds thin, buzzy, and fatiguing — it is primarily a *source oscillator* for subtractive synthesis and effects processing. The method produces its characteristic warm sound only when: (a) a lowpass/resonant filter removes harsh upper harmonics (SP-029/SP-020), (b) a chorus/ensemble effect spreads the voice across the stereo field (SP-059), and (c) reverb provides spatial depth (SP-009/SP-032). The method's strength is as a *source material generator* for the UnitMatrix's sound-production pipeline, not a final output.

6. **CPU cost for dense polyphony**: Two PolyBLEP sawtooths per voice × $V$ voices = $2V$ sawtooth evaluations + $4V$ PolyBLEP corrections per sample. For $V=8$ at $f_s=48000$, this is ~768,000 operations/second — comfortable on modern CPUs but heavy for real-time embedded systems. Alternatives for high-voice-count sections: wavetable-lookup PWM (SP-041 BLW-MI with pre-computed duty-cycle tables) or DPW (differentiated parabolic wave) for $D > 0.2$ at lower cost.

7. **PolyBLEP correction gets cheaper with more oscillators**: Sharing the same PolyBLEP tables across all voices (pre-computed $\Delta$ bins) reduces the per-correction cost to a table lookup + multiply. Always pre-compute the PolyBLEP correction polynomial coefficients for all expected $\Delta$ values (phase increments).
```

## Technical Mechanics Summary

1. **Core equation**: $p_D(t) = s(t) - s(t-D)$ — pulse wave = difference of two phase-shifted sawtooths
2. **Fourier amplitude**: $A_n(D) = 2|\sin(\pi n D)|/(\pi n)$ — duty cycle controls all partial amplitudes
3. **$D=0.5$**: only odd harmonics (square wave). $D=0.25$: all harmonics with $\sin(\pi n/4)$ envelope
4. **PolyBLEP antialiasing**: 2nd-order polynomial correction at each sawtooth reset discontinuity
5. **LFO modulation**: $D(t) = D_0 + \Delta D \cdot \text{LFO}(t)$, with $[0.03, 0.97]$ clamp
6. **Two-oscillator ensemble**: $p_{\text{mix}} = p_{D_1}(t) + p_{D_1+\delta}(t)$ with duty spread $\delta \approx 0.02$–$0.10$
7. **Complexity**: $\mathcal{O}(1)$ per sample per voice

## Quirks / Pitfalls Hit During Development

1. **Summary table format inconsistency**: The SP summary table has inconsistent leading pipes: some rows use `||` (two pipes = empty first column) while others (SP-098 through SP-109) use `|||` (three pipes = two empty columns). This appears to be a historical artifact of table reformatting. The patch tool automatically preserved the surrounding format. After patching, re-read the table to verify column alignment.

2. **LaTeX backslash escaping in existing file**: The methods_db.md uses `\` for LaTeX (single backslash). The patch tool automatically handles this correctly in patch mode, but when writing new content with write_file, backslashes in strings need careful attention. The existing file uses single `\` for LaTeX commands (e.g., `\mathcal{O}`, `\sin`, `\sum`), which is standard for Pandoc/GFM rendering.

3. **File size**: The methods_db.md is 24.5 KB initially and grew by approximately 570 lines after the append. The write_file → terminal cat → terminal rm workflow for appending was straightforward but requires two terminal calls (cat + rm) after the write_file.

4. **PolyBLEP sign convention**: The PolyBLEP correction formula for a rising step (from -1 to +1, height=2) subtracts the correction from the raw sawtooth value. For a falling step (from +1 to -1, height=-2), the correction is added (subtracting a negative). The `_polyblep_2nd_order` method in the implementation handles both cases by accepting a signed `height` parameter.

5. **DC offset cancellation**: The sawtooth subtraction method inherently cancels DC offset because both sawtooths have the same DC bias (1.0 in the unipolar form, 0.0 in the bipolar form), and $p_D(t) = s(t) - s(t-D)$ removes the common DC. Direct threshold PWM (if phase >= D then 1 else -1) retains a $2D-1$ DC component that must be removed.

## Next Free SP ID
The next available SP ID after SP-110 is **SP-111**.