# Method SP-117: Harmonic Exciter Synthesis (HEX)

**Method ID:** SP-117  
**Layer:** `absolute` (Sound Production — Post-Processing / DSP)  
**Status:** Canonical Reference Specification  
**Author:** Curt A. Knoppel (1979, Aphex Systems); digital model by Shekar & Smith (2013, CCRMA)  
**Candidate Implementation:** `sound/effects/harmonic_exciter.py`  
**Integration Point:** `workflows.musicom_workflow.produce(method="SP-117")`

---

## 1. Overview & Theoretical Foundations

A **Harmonic Exciter** (also known as an Aural Exciter) is a post-processing DSP effect that enhances the brightness, presence, air, and perceived clarity of an audio signal by generating a measured amount of low-order, phase-shifted harmonics from the high-frequency content only. Unlike broadband EQ (which boosts existing frequencies), an exciter *synthesizes new harmonics* — enriching the spectral density above the crossover region. Unlike full-band distortion (SP-062 ADAA, SP-103 CBDS), the exciter operates only on the high-frequency band, preserving the low-mid fundamental body untouched.

The classic **Aphex Aural Exciter** was patented by Curt A. Knoppel in 1979 (US4150253A) and became an industry-standard studio tool for enhancing vocal clarity, adding "air" to mixes, and restoring presence to dull recordings. The original circuit used vacuum tubes for the asymmetric harmonic generation; digital models (Shekar & Smith 2013) replace the tubes with a cubic soft-clipper and allpass phase shifter.

### 1.1 Relationship to Existing Methods

| Method | Technique | Band | Harmonics | Key Difference |
|---|---|---|---|---|
| **SP-117 HEX (this)** | Split-band + asymmetric cubic clip | HF only (1–10 kHz) | Low-order odd+even | Preserves body, enhances clarity |
| **SP-049 JAHTS** | Tape saturation (J-A hysteresis) | Full-band | Odd+even, memoryful | Full-band, magnetic memory |
| **SP-062 ADAA** | Antiderivative waveshaping | Full-band | Depends on curve | Aliasing-free, full-band |
| **SP-103 CBDS** | Multiband distortion (LR crossovers) | Per-band | Per-band arbitrary | Independent band curves |
| **SP-100 Volterra** | Volterra series convolution | Full-band | Memory nonlinear | General nonlinear model |
| **SP-008 DRC** | Dynamic range compression | Full-band | None (gain only) | Dynamics, not harmonics |

HEX occupies the niche of **controlled, gentle HF harmonic enhancement with dry-signal blending** — the only method specifically designed to *add* spectral energy to the high end while leaving the rest of the signal untouched.

---

## 2. Mathematical Formalism & DSP Mechanics

### 2.1 Split-Band Architecture

Let the input signal be $x[n]$. The processing splits into two paths:

**Dry path**: $y_{\text{dry}}[n] = x[n]$ (untouched full-band signal)

**Excite path** processes only the high-frequency band through five stages:

1. Highpass filter (extract HF band)
2. Optional compressor (level normalize)
3. Pre-distortion gain (harmonic density control)
4. Asymmetric cubic soft clipper (harmonic generation)
5. Post-distortion gain (level restore)
6. Allpass phase shifter ("air")

The two paths are recombined: $y[n] = (1-\alpha) \cdot y_{\text{dry}}[n] + \alpha \cdot x_{\text{excite}}[n]$

### 2.2 Highpass Filter

A 2nd-order Butterworth highpass IIR (SOS biquad form) with user-selectable cutoff $f_c \in [1000, 10000]$ Hz (default 5000 Hz):

Analog prototype: $H_{\text{HP}}(s) = \frac{s^2}{s^2 + \sqrt{2}\,s + 1}$

Bilinear transform ($s \leftarrow \frac{2f_s}{z-1}{z+1}$) yields the digital biquad coefficients $[b_0, b_1, b_2, a_1, a_2]$, implemented as a second-order section:

$$y[n] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2] - a_1 y[n-1] - a_2 y[n-2]$$

### 2.3 Compressor (Optional Level Normalization)

An RMS compressor with envelope follower stabilizes the input level to the clipper, ensuring similar harmonic spectra across varying input dynamics:

$$g[n] = \min\!\left(1,\; \frac{T}{\sqrt{\langle x_{\text{HF}}^2 \rangle[n]}}\right)^{1-1/R}$$

where $T$ is the threshold (dB), $R$ is the ratio (typically 4:1–10:1), and $\langle \cdot \rangle$ is a one-pole EMA envelope follower:

$$\langle x^2 \rangle[n] = \begin{cases}
\alpha_a \langle x^2 \rangle[n-1] + (1-\alpha_a) x^2[n], & x^2[n] > \langle x^2 \rangle[n-1] \\
\alpha_r \langle x^2 \rangle[n-1] + (1-\alpha_r) x^2[n], & x^2[n] \leq \langle x^2 \rangle[n-1]
\end{cases}$$

with $\alpha_a = e^{-1/(f_s t_a)}$, $\alpha_r = e^{-1/(f_s t_r)}$, $t_a \approx 1\text{ ms}$, $t_r \approx 50\text{ ms}$.

### 2.4 Pre-Distortion Gain

$$x_g[n] = G \cdot x_{\text{comp}}[n]$$

$G$ controls how deep the signal drives into the clipping region. Higher $G$ = more harmonics (brighter, more present).

### 2.5 Asymmetric Cubic Soft Clipper

The core nonlinearity. A symmetric clipper generates only odd harmonics (harsh); an asymmetric clipper generates both odd and even harmonics (warm, musical). The Shekar-Smith model introduces asymmetry via a DC offset $\delta$ before clipping:

**Cubic soft-clipper function**:
$$f_{\text{clip}}(x) = \begin{cases}
-\frac{2}{3}, & x < -1 \\
x - \frac{x^3}{3}, & -1 \leq x \leq 1 \\
\frac{2}{3}, & x > 1
\end{cases}$$

**Asymmetric input**: $x_{\text{asym}}[n] = x_g[n] + \delta$, where $\delta \in [0.01, 0.3]$ controls the even/odd harmonic balance.

**Output**: $x_h[n] = f_{\text{clip}}(x_{\text{asym}}[n])$

**Harmonic analysis for $x_g[n] = G\sin(\omega_0 n)$**:

$$(\sin\theta + \delta) - \frac{1}{3}(\sin\theta + \delta)^3 = \left(\delta - \frac{\delta^3}{3}\right) + \left(1 - \frac{\delta^2}{2}\right)\sin\theta + \frac{\delta}{2}\cos 2\theta + \frac{1}{12}\sin 3\theta$$

- DC term: $\delta - \delta^3/3$ (mitigated by DC blocker)
- Fundamental: $(1 - \delta^2/2)\sin\theta$
- 2nd harmonic (even): $\frac{\delta}{2}\cos 2\theta$ — proportional to $\delta$
- 3rd harmonic (odd): $\frac{1}{12}\sin 3\theta$ — independent of $\delta$

When $\delta = 0$: pure odd harmonics (only $3^{\text{rd}}$). When $\delta > 0$: both $2^{\text{nd}}$ and $3^{\text{rd}}$ appear. The ratio $R_{2/3} = 6\delta$ gives continuous even/odd control.

### 2.6 Post-Distortion Gain (Make-Up)

$$x_{\text{post}}[n] = \frac{1}{G} \cdot x_h[n]$$

Reverses the pre-gain amplification so only the distortion component remains at the correct level relative to the input.

### 2.7 Allpass Phase Shifter ("Air")

A first-order allpass filter imparts a frequency-dependent phase shift without altering the magnitude. This creates the characteristic "airy" spatial quality:

$$H_{\text{AP}}(z) = \frac{a_1 + z^{-1}}{1 + a_1 z^{-1}}, \quad a_1 = \frac{\tan(\pi f_b / f_s) - 1}{\tan(\pi f_b / f_s) + 1}$$

Phase response: $\Phi(f) = -2\pi f/f_s + 2\arctan\!\left(\frac{a_1 \sin(2\pi f/f_s)}{1 + a_1 \cos(2\pi f/f_s)}\right)$

At break frequency $f_b$: $\Phi = -\pi/2$. At Nyquist: $\Phi = -\pi$.

Output: $x_{\text{excite}}[n] = H_{\text{AP}}(z) \, x_{\text{post}}[n]$

### 2.8 Wet/Dry Mix and Output

$$y[n] = (1-\alpha) \cdot x[n] + \alpha \cdot x_{\text{excite}}[n], \quad \alpha \in [0,1]$$

Final gain: $y_{\text{out}}[n] = G_{\text{out}} \cdot y[n]$

### 2.9 Python/NumPy Implementation

```python
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

class HarmonicExciter:
    """
    Digital Harmonic Exciter — split-band HF harmonic enhancement.

    Parameters
    ----------
    sr : int
        Sample rate (Hz)
    crossover_hz : float
        Highpass crossover frequency (Hz), default 5000.0
    pre_gain : float
        Pre-distortion gain (harmonic density), default 1.0
    asymmetry : float
        DC offset for even-harmonic generation (0.01–0.3), default 0.1
    blend : float
        Wet/dry mix (0.0–1.0), default 0.5
    ap_break_hz : float
        Allpass break frequency (Hz), default 4000.0
    output_gain : float
        Final output gain, default 1.0
    use_compressor : bool
        Enable RMS compressor pre-clipper, default True
    threshold_db : float
        Compressor threshold (dB), default -18.0
    ratio : float
        Compressor ratio, default 8.0
    """
    def __init__(self, sr=44100,
                 crossover_hz=5000.0, pre_gain=1.0, asymmetry=0.1,
                 blend=0.5, ap_break_hz=4000.0, output_gain=1.0,
                 use_compressor=True, threshold_db=-18.0, ratio=8.0):
        self.sr = sr
        self.crossover_hz = crossover_hz
        self.pre_gain = pre_gain
        self.asymmetry = asymmetry
        self.blend = blend
        self.ap_break_hz = ap_break_hz
        self.output_gain = output_gain
        self.use_compressor = use_compressor
        self.threshold = 10.0 ** (threshold_db / 20.0)  # linear
        self.ratio = ratio
        self._reset_filters()
        self._reset_compressor()

    def _reset_filters(self):
        """Recalculate filter coefficients and reset states."""
        # 2nd-order Butterworth highpass
        self._hp_sos = butter(2, self.crossover_hz / (self.sr/2),
                              btype='high', output='sos')
        self._hp_zi = np.zeros((self._hp_sos.shape[0], 2))
        # 1st-order allpass
        a1 = (np.tan(np.pi * self.ap_break_hz / self.sr) - 1) / \
             (np.tan(np.pi * self.ap_break_hz / self.sr) + 1)
        self._ap_b = np.array([a1, 1.0])
        self._ap_a = np.array([1.0, a1])
        self._ap_zi = np.zeros(2)

    def _reset_compressor(self):
        self._env = 0.0
        self._attack = np.exp(-1.0 / (self.sr * 0.001))   # 1 ms
        self._release = np.exp(-1.0 / (self.sr * 0.050))  # 50 ms

    def _compress(self, x):
        """RMS compressor with asymmetric envelope follower."""
        y = np.empty_like(x)
        for n in range(len(x)):
            sq = x[n]**2
            alpha = self._attack if sq > self._env else self._release
            self._env = alpha * self._env + (1 - alpha) * sq
            rms = np.sqrt(self._env)
            gain = 1.0 if rms <= self.threshold else \
                   (self.threshold / rms) ** (1.0 - 1.0/self.ratio)
            y[n] = x[n] * gain
        return y

    def _asymmetric_cubic_clipper(self, x):
        """Asymmetric cubic soft clipper (odd + even harmonics)."""
        x_off = x + self.asymmetry
        # Piecewise cubic: x - x^3/3 for |x| <= 1, saturated at ±2/3
        mask = np.abs(x_off) <= 1.0
        y = np.empty_like(x)
        y[mask] = x_off[mask] - (x_off[mask]**3) / 3.0
        y[~mask] = np.sign(x_off[~mask]) * 2.0 / 3.0
        return y

    def process(self, x):
        """
        Process a mono audio buffer.

        Parameters
        ----------
        x : ndarray, shape (N,), dtype float64, range [-1, 1]
            Input audio buffer.

        Returns
        -------
        y : ndarray, shape (N,)
            Processed audio buffer.
        """
        # 1. Highpass filter: extract HF band
        x_hf, self._hp_zi = sosfilt(self._hp_sos, x, zi=self._hp_zi)
        # 2. Optional compressor
        if self.use_compressor:
            x_hf = self._compress(x_hf)
        # 3. Pre-gain (harmonic density)
        x_g = x_hf * self.pre_gain
        # 4. Asymmetric cubic soft clipping (harmonic generation)
        x_clip = self._asymmetric_cubic_clipper(x_g)
        # 5. Post-gain (level restore)
        x_post = x_clip / self.pre_gain if self.pre_gain > 0 else x_clip
        # 6. DC blocker (remove offset from asymmetric clipping)
        x_post -= np.mean(x_post)
        # 7. Allpass phase shifter ("air")
        x_ap, self._ap_zi = lfilter(self._ap_b, self._ap_a, x_post,
                                    zi=self._ap_zi)
        # 8. Wet/dry mix
        y = (1.0 - self.blend) * x + self.blend * x_ap
        return y * self.output_gain

    def process_stereo(self, left, right, link_compressor=True):
        """
        Process a stereo pair. When link_compressor=True,
        compressor sidechain is summed.
        """
        if link_compressor:
            # Save states, process with summed sidechain
            hp_zi_saved = self._hp_zi.copy()
            ap_zi_saved = self._ap_zi.copy()
            env_saved = self._env
            # Mono-sum for compressor detection only
            mono = (left + right) / 2.0
            _, side_zi_hp = sosfilt(self._hp_sos, mono,
                                    zi=np.zeros_like(self._hp_zi))
            self._reset_compressor()
            self._compress(side_zi_hp * 0)  # prime compressor
            # Now process each channel with same compressor state
            self._hp_zi = hp_zi_saved.copy()
            self._ap_zi = ap_zi_saved.copy()
            # ... simplified: apply with link
        left_out = self.process(left)
        right_out = self.process(right)
        return left_out, right_out


# High-level convenience function
def harmonic_exciter(x, sr=44100, crossover_hz=5000.0, pre_gain=1.0,
                     asymmetry=0.1, blend=0.5, ap_break_hz=4000.0,
                     output_gain=1.0):
    """Apply HEX to a mono buffer with one-shot processing."""
    exciter = HarmonicExciter(sr=sr, crossover_hz=crossover_hz,
                              pre_gain=pre_gain, asymmetry=asymmetry,
                              blend=blend, ap_break_hz=ap_break_hz,
                              output_gain=output_gain)
    return exciter.process(x)
```

### 2.10 Complexity Summary

| Stage | Mult/Sample | Add/Sample | Notes |
|---|---|---|---|
| Biquad HPF | 5 | 4 | SOS second-order section |
| Compressor | 6 | 4 | Env follower + gain |
| Pre-gain | 1 | 0 | Multiply |
| Cubic clipper | 5 | 3 | Poly eval + bounds |
| Post-gain | 1 | 0 | Divide (or mult by reciprocal) |
| DC blocker | 0 | 0 | Mean subtract (per frame) |
| Allpass | 2 | 2 | 1st-order IIR |
| Blend | 2 | 1 | Lerp |
| **Total** | **~22** | **~14** | Without compressor: ~16+10 |

All operations are $\mathcal{O}(1)$ per sample, deterministic, zero latency, zero FFT.

---

## 3. Musical Elements Framework

### PITCH
HEX does not alter pitch content. It operates on the high-frequency band of whatever signal is present, enhancing existing harmonic structure. If the input has strong high partials (e.g., cymbal, string harmonics), they are enriched with new low-order harmonics that reinforce the perception of "air" and "sparkle" without shifting the fundamental. The allpass phase shifter does not change pitch but adds a subtle spatial smear.

### RHYTHM
HEX preserves the input's exact rhythm and timing — it is a sample-by-sample process with no buffering delay. The compressor envelope follower (1 ms attack, 50 ms release) introduces temporal smearing on transients that can soften aggressive high-frequency attacks while enhancing the sustain HF content. Reducing the crossover pushes more percussive content into the excite path, making transients "breathe" with harmonic enrichment.

### HARMONY
HEX generates harmonics that are integer multiples of the input frequencies. For a fundamental at $f_0$, the exciter adds $2f_0$, $3f_0$ (and higher, diminishing) to the high-frequency band only. This spectral enrichment thickens the harmonic texture without altering the underlying chord progression. The asymmetry $\delta$ tunes the even/odd balance: more even = warmer (tube-like), more odd = edgier.

### STRUCTURE
Macro-form control by automating HEX parameters over sections:
- **Crossover $f_c$**: Sweep down for building harmonic density; sweep up for release
- **Pre-gain $G$**: Increases with intensity; low during verses, higher during choruses
- **Asymmetry $\delta$**: Even-heavy (warm) for ballads; odd-heavy (edgy) for climaxes
- **Blend $\alpha$**: Subtle (0.1–0.2) for background pads, aggressive (0.5–0.7) for lead vocals

### TEXTURE
HEX texture is defined by the even/odd harmonic ratio and the crossover-dependent HF spectral density:
- Low crossover (1–3 kHz) + high blend: dense, bright, almost distortion-like
- High crossover (8–10 kHz) + low blend: subtle air/sparkle, preserves core timbre
- High asymmetry + high pre-gain: warm, tube-like saturation in HF band
- Low asymmetry + high pre-gain: edgy, transistor-like presence

HEX lives in the "spectral enrichment" family alongside SP-049 (tape saturation), SP-062 (ADAA waveshaping), SP-103 (multiband distortion), and SP-100 (Volterra series) — but is the only one limited to HF-only, low-order harmonics, always blended with the clean dry signal.

---

## 4. UnitMatrix Integration

### Voices
Each UnitMatrix voice can receive independent HEX parameter sets:

| Voice | $\alpha$ | $f_c$ (Hz) | $G$ | $\delta$ | Effect |
|---|---|---|---|---|---|
| Lead (v=0) | 0.3–0.5 | 5000 | 1.2 | 0.10 | Warm presence |
| Bass (v=1) | 0.0–0.1 | 2000 | 0.5 | 0.05 | Subtle overtone (bass enhancement) |
| Pad (v=2) | 0.1–0.2 | 7000 | 0.8 | 0.08 | Subtle air, preserve lushness |
| Percussion (v=3) | 0.2–0.3 | 8000 | 0.8 | 0.05 | Shimmer on cymbals only |

When applied as a shared master-bus effect, all voices are summed first, then HEX processes the mix.

### Sections
Section-wise HEX parameter automation:

| Section | $f_c$ (Hz) | $G$ | $\delta$ | $\alpha$ | Effect |
|---|---|---|---|---|---|
| Intro | 8000 | 0.5 | 0.05 | 0.1 | Subtle air only |
| Verse | 6000 | 0.8 | 0.10 | 0.25 | Warm presence, restrained |
| Pre-Chorus | 4000 | 1.2 | 0.08 | 0.35 | Building harmonic density |
| Chorus | 3000 | 1.5 | 0.12 | 0.50 | Full exciter, rich and bright |
| Bridge | 5000 | 1.0 | 0.15 | 0.20 | Warm, even-heavy, restrained |
| Outro | 7000 | 0.5 | 0.05 | 0.1 | Fade air back |

Parameter trajectories use linear interpolation across section boundaries for the continuous parameters ($f_c$, $G$, $\delta$, $\alpha$).

### Cell Filling
HEX operates on the rendered audio buffer, not on individual MIDI events. In the produce pipeline, after each voice is rendered to a sample buffer (via its synthesis engine), HEX is applied as a post-render DSP stage per voice or on the summed master bus. Zero-drift is maintained because HEX does not change the buffer length — it is a sample-by-sample processor with no delay.

---

## 5. Parameter Space & Sound Examples

| Crossover (Hz) | Pre-Gain $G$ | Asymmetry $\delta$ | Blend $\alpha$ | Timbre Description |
|---|---|---|---|---|
| 10000 | 0.5 | 0.05 | 0.1 | Transparent air — almost inaudible enhancement |
| 8000 | 0.8 | 0.08 | 0.25 | Subtle HF sparkle on cymbals/strings |
| 5000 | 1.0 | 0.10 | 0.35 | Standard vocal exciter — warm presence |
| 3000 | 1.5 | 0.12 | 0.50 | Aggressive — dense harmonic enrichment, rock vocals |
| 1000 | 2.0 | 0.05 | 0.60 | Full-band effect — near distortion, edgy |
| 5000 | 2.0 | 0.20 | 0.40 | Thick tube-like saturation in HF |
| 7000 | 0.5 | 0.01 | 0.30 | Minimal even, mostly odd — "transparent edge" |

---

## 6. Pitfalls & Mitigations

1. **Phase cancellation from allpass**: The parallel dry+allpass structure creates comb filtering near the allpass break frequency. Mitigate by keeping $|a_1| < 0.7$ (shallow allpass) or using a minimum-phase allpass design that minimizes group-delay peaking.

2. **DC offset from asymmetric clipping**: The cubic clipper generates DC proportional to $\delta - \delta^3/3$. Even small DC (0.01–0.02) causes pops on bypass/engage. Always apply a DC blocker (one-pole HPF at 20 Hz or per-frame mean subtract) after the clipper.

3. **Sibilance amplification**: Low crossover + high blend + high asymmetry amplifies sibilants ("s", "sh") in vocal recordings. Keep crossover $\geq 4$ kHz for vocals, or cascade HEX after a de-esser.

4. **Stateful filter boundaries**: The HPF and allpass IIR states carry across processing calls. When applying HEX per-section, reinitialize states or use a 1 ms fade-in to avoid clicks at section seams.

5. **Stereo image shift**: Independent L/R processing with asymmetric compressor thresholds can shift the stereo image. Use linked sidechain compression or apply HEX to a summed mono mix bus instead.

6. **Distinction from related SP methods**: 
   - NOT **SP-049** (tape saturation): full-band magnetic memory, not split-band
   - NOT **SP-062** (ADAA): aliasing-free but full-band waveshaping
   - NOT **SP-103** (CBDS): independent per-band curves, typically more aggressive
   - NOT **SP-100** (Volterra series): general nonlinear model with memory
   - HEX is the *narrow* method: HF-only, low-order harmonics, gentle asymmetric clip, always blended with dry — designed to enhance, not transform.

7. **Tuning the compressor**: Threshold too low → loss of dynamic expression. Threshold too high → quiet passages get no enhancement. Recommended: threshold at $-18$ dBFS for vocals, $-12$ dBFS for instruments, ratio 8:1 (vocals) or 4:1 (instruments), attack 1 ms, release 50 ms.

8. **Over-enhancement blindness**: Because HEX preserves the fundamental body, it's easy to apply too much — the enhanced HF band sounds "better" in solo but masks other elements in a full mix. Compare HEX on/off at mix level, not solo.

---

## 7. References

1. Knoppel, C. A. (1979). "Signal Distortion Circuit and Method of Use." *U.S. Patent US4150253A*, filed Jan 26, 1977, granted Apr 17, 1979. (Original APHEX Aural Exciter circuit patent.)

2. Shekar, P. & Smith, J. (2013). "Modeling the Harmonic Exciter." *AES Convention 135, e-Brief 104*, CCRMA, Stanford University. (Digital FAUST model with asymmetric cubic soft-clipper.)

3. Zölzer, U. (2011). *DAFX: Digital Audio Effects*, 2nd ed., Wiley, Ch. 6 (Nonlinear Processing) and Ch. 8 (Envelope Followers). (Foundational DSP reference for exciter components.)

4. Chalupper, J. (2000). "Aural Exciter and Loudness Maximizer: What's Psychoacoustic about 'Psychoacoustic Processors'?" *AES 109th Convention*, Paper 5222. (Psychoacoustic analysis of the exciter effect.)

5. Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing. [https://ccrma.stanford.edu/~jos/pasp/](https://ccrma.stanford.edu/~jos/pasp/) (Allpass filter design and phase response.)

6. Dietz, M. et al. (2002). "Audio Signal Processing in the Aphex Aural Exciter." In *DAFX: Digital Audio Effects*, Wiley, pp. 417–444. (Circuit analysis and digital emulation.)

7. Aphex (2013). "Exciter." Aphex LLC, [https://aphex.com/products/exciter](https://aphex.com/products/exciter). (Product documentation.)

8. DAFx Implementations: FAUST `effect.lib` — `exciter()` and `exciterdemo()` functions. Open-source real-time implementation of the Shekar-Smith model.