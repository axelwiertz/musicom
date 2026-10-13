# Psychoacoustic Bass Enhancement Synthesis (PBES) — SP-113

## Overview

**ID**: SP-113
**Layer**: absolute — Post-Processing / DSP
**Name**: Psychoacoustic Bass Enhancement Synthesis (PBES)
**Code path**: `sound/effects/bass_enhancer.py`
**Complexity**: $\mathcal{O}(M_{LPF}+M_{BPF})$ per sample per voice for filter banks; $\mathcal{O}(1)$ for the harmonic generator core
**Aliases**: MaxxBass, virtual bass, missing-fundamental synthesis, psychoacoustic bass, harmonic bass enhancement

**One-line description**: Generates the perceptual illusion of low bass on bandwidth-limited speakers by synthesizing harmonics of bass content via controlled nonlinearity, exploiting the missing-fundamental/virtual-pitch phenomenon.

---

## Source

[1] Wikipedia contributors. "Missing fundamental." *Wikipedia, The Free Encyclopedia.*
[2] Larsen, E. & Aarts, R. M. (2002). "Reproducing Low-Pitched Signals through Small Loudspeakers." *Journal of the Audio Engineering Society* 50(3), 517–528.
[3] Ben-Tzur, D. & Colloms, M. (1999). "The Effect of MaxxBass Psychoacoustic Bass Enhancement System on Loudspeaker Design." 106th AES Convention.
[4] U.S. Patent No. 5,930,373, Shashoua, M. (1999). — Waves MaxxBass algorithm.
[5] Arora, M., Oh, Y., Kim, S., Lee, H. & Jang, S. (2008). "Low Complexity Virtual Bass Enhancement Algorithm for TV Speakers." *Samsung Electronics DM Research Lab.*
[6] U.S. Patent No. 6,111,960, Aarts et al. (Philips). — Low-Pitched Signal Reproduction.
[7] U.S. Patent No. 6,287,767, Klayman. — Augmented Spectral Synthesis.
[8] Zoelzer, U. (2002). *DAFX Digital Audio Effects.* John Wiley & Sons.
[9] Benade, A. (1976). *Fundamentals of Musical Acoustics.* Oxford University Press. — On the missing fundamental and residue pitch.

## Layer

**absolute** — Post-Processing / DSP
Code path: `sound/effects/bass_enhancer.py`

## Description

Psychoacoustic Bass Enhancement Synthesis (PBES) generates the perceptual *illusion* of low-frequency bass content that is physically absent or inaudible from the audio signal. It exploits the **missing fundamental** (virtual pitch) phenomenon: when a complex tone contains a set of integer-related partials at frequencies $2f_0, 3f_0, 4f_0 \dots$, the auditory system infers a pitch at $f_0$ even when $f_0$ itself is below the speaker's cutoff or entirely absent from the spectrum.

The method is a **post-processing DSP layer** applied to rendered audio buffers (or mix stems). Its signal chain: (1) extract the bass region below a crossover frequency $f_c$ via linear-phase lowpass filter; (2) generate a harmonic series from the extracted bass signal using a controlled nonlinearity; (3) shape the generated harmonics with a bandpass filter $[f_c, 3f_c]$ that removes both the fundamental (already inaudible) and harmonics above $3f_c$; (4) scale the harmonic path by a dynamic gain $g_{harm}(t)$ derived from the bass envelope follower; (5) highpass-filter the original signal to remove the inaudible bass region; and (6) sum the shaped, gain-scaled harmonics back with the delayed highpassed original, compensating for filter group delay.

PBES sits in the **Post-Processing / DSP** layer: it transforms previously rendered audio (from SP-001 FluidSynth, SP-029 subtractive, SP-111 Duffing, or any other engine), not a synthesis engine itself.

**Distinction from SP-097 (Sub-Harmonic Oscillator Synthesis)**: SHOS generates frequency-divided subharmonics (*downward*: $f_0/d$) from a master oscillator — a synthesis-time technique producing actual low frequencies. PBES generates *upward* harmonics ($2f_0, 3f_0, \dots$) from existing audio to create the *perception* of the absent fundamental — a post-process that adds no genuine low-frequency energy. Complementary: SHOS for bass-synth voices, PBES for bass-bus enhancement.

## Technical Mechanics

### Signal Flow (mono)

```
x[n] ──→ [LPF at f_c] ──→ x_lp[n] ──→ [Harmonic Generator H{·}] ──→ x_harm[n] ──→ [BPF: f_c … 3f_c] ──→ x_hs[n] ──→ ×g_harm[n] ──→ +
         └─→ [HPF at f_c] ──→ x_hp[n] ──→ [delay Δ] ──→ ─────────────────────────────────────────────────────────→ +
                                                                                                              ↓
                                                                                                        y_out[n]
```

### Step 1 — Bass Extraction

A linear-phase lowpass filter isolates the bass region:

$$x_{lp}[n] = \sum_{k=0}^{N-1} h_{LP}[k] \cdot x[n-k]$$

where $h_{LP}$ has $-3\text{ dB}$ corner at $f_c$ (typically 100–150 Hz). Linear-phase FIR preferred (constant group delay $\Delta = (N-1)/2$); Bessel IIR acceptable for low-MIPS implementations.

### Step 2 — Harmonic Generation (three methods)

**Method A — Full-wave integrator (Larsen & Aarts 2002)**

$$y_{int}[n] = y_{int}[n-1] + x_{lp}[n]$$

with periodic zero-crossing reset. Spectrum: $|Y_{int}[k]| \approx 1/k$, giving natural 1/k harmonic rolloff with both odd and even harmonics.

**Method B — Asymmetric envelope follower (Shashoua/Waves MaxxBass patent)**

$$y_{ef}[n] = \begin{cases}
\alpha_{rise} x_{lp}[n] + (1-\alpha_{rise}) y_{ef}[n-1], & x_{lp}[n] > y_{ef}[n-1] \\
\alpha_{fall} x_{lp}[n] + (1-\alpha_{fall}) y_{ef}[n-1], & \text{else}
\end{cases}$$

with $\alpha_{rise} \approx 1.0$ (1 ms) and $\alpha_{fall} \approx 0.03$–0.1 (3–10 ms). Spectral tilt $|Y_{ef}[k]| \propto 1/k^{\gamma(T_{fall})}$ with $\gamma \in [0.5, 2.0]$, controlled by the fall-time parameter.

**Method C — Half-wave clipping with shaping filter (Samsung method 2)**

$$y_{hw}[n] = \max(x_{lp}[n], 0)$$

followed by DC-blocking highpass: $y_{ac}[n] = y_{hw}[n] - \overline{y}_{hw}$. Simple, fast, but requires DC removal.

### Step 3 — Harmonic Shaping Filter

$$x_{hs}[n] = \sum_{k=0}^{M-1} h_{BP}[k] \cdot y_{harm}[n-k]$$

where $h_{BP}$ has passband $[f_c, 3f_c]$. The HPF at $f_c$ removes the fundamental from the harmonic path (preventing real bass energy from the harmonic branch); the LPF at $3f_c$ limits to 2-3 harmonics, sufficient for the missing fundamental effect.

### Step 4 — Envelope-Follower Gain Scaling

$$g_{harm}[n] = G_{target} \cdot \sqrt{\frac{E_{lp}[n]}{E_{ref}}}, \quad
E_{lp}[n] = \beta x_{lp}^2[n] + (1-\beta) E_{lp}[n-1]$$

$\beta$ corresponds to a 20–50 ms RMS window. Quiet passages get proportionally less enhancement, preserving the dynamic contour.

### Step 5 — Dry Path (HPF + Delay)

$$x_{hp}[n] = \sum_{k=0}^{N-1} h_{HP}[k] \cdot x[n-k], \quad
x_{delayed}[n] = x_{hp}[n - \Delta], \quad
\Delta = \lfloor (N_{LP} + N_{BP})/2 \rfloor$$

The delay aligns the processed harmonic path with the dry path, compensating for FIR filter group delays.

### Step 6 — Output Sum

$$y_{out}[n] = g_{dry} \cdot x_{delayed}[n] + g_{harm}[n] \cdot x_{hs}[n]$$

Typical mixing: $g_{dry}=1.0$, $g_{harm} \in [0.05, 0.4]$ (corresponding to ~3–12 dB harmonic enhancement of bass RMS).

### Python/NumPy Implementation Sketch

```python
import numpy as np
from scipy import signal

class PBES:
    """
    Psychoacoustic Bass Enhancement Synthesis (SP-113)
    
    Generates the missing-fundamental illusion by synthesizing
    harmonics of the bass region via controlled nonlinearity.
    """
    
    def __init__(self, fs=48000, fc=120):
        # Crossover filters (linear-phase FIR, 512 taps)
        self.fs = fs
        self.fc = fc
        self._design_filters(fc, fs, ntaps=512)
        
        # State for harmonic generators
        self.y_int = 0.0          # integrator state (Method A)
        self.y_ef_prev = 0.0      # envelope follower state (Method B)
        self.e_lp = 0.0           # RMS envelope follower
        self.dc_bias = 0.0        # DC blocker state (Method C)
        
        # Harmonic generator method selector
        self.method = "B"         # A | B | C
        self.alpha_rise = 0.99    # fast rise (≈1ms)
        self.alpha_fall = 0.05    # slow fall (≈5ms)
        self.g_target = 0.15      # harmonic gain target
        self.g_dry = 1.0          # dry signal gain
        
    def _design_filters(self, fc, fs, ntaps=512):
        # Lowpass — bass extraction
        self.lpf_b = signal.firwin(ntaps, fc, pass_zero='lowpass', fs=fs)
        self.lpf_a = 1.0
        # Highpass — dry path
        self.hpf_b = signal.firwin(ntaps, fc, pass_zero='highpass', fs=fs)
        self.hpf_a = 1.0
        # Bandpass — harmonic shaping
        self.bpf_b = signal.firwin(ntaps, [fc, 3*fc], pass_zero='bandpass', fs=fs)
        self.bpf_a = 1.0
        # Delay compensation (FIR group delay = (ntaps-1)/2)
        self.delay = (ntaps - 1) // 2
        
    def _full_wave_integrate(self, x):
        """Method A: Full-wave integration"""
        y = np.zeros_like(x)
        for n in range(len(x)):
            self.y_int += x[n]
            if x[n] >= 0 and (n == 0 or x[n-1] < 0):
                self.y_int = 0.0  # zero-crossing reset
            y[n] = self.y_int
        return y
    
    def _asymmetric_envelope(self, x):
        """Method B: Asymmetric envelope follower"""
        y = np.zeros_like(x)
        for n in range(len(x)):
            if x[n] > self.y_ef_prev:
                y[n] = self.alpha_rise * x[n] + (1-self.alpha_rise) * self.y_ef_prev
            else:
                y[n] = self.alpha_fall * x[n] + (1-self.alpha_fall) * self.y_ef_prev
            self.y_ef_prev = y[n]
        return y
    
    def _half_wave_clip(self, x):
        """Method C: Half-wave clipping + DC blocker"""
        y = np.maximum(x, 0)
        # First-order DC blocker
        dc = np.zeros_like(y)
        for n in range(len(y)):
            dc[n] = y[n] - self.dc_bias + 0.995 * (dc[n-1] if n > 0 else 0)
            self.dc_bias = y[n]
        return dc
    
    def process(self, x):
        """
        Process one audio buffer.
        
        Parameters
        ----------
        x : np.ndarray shape (N,) — input audio buffer
        
        Returns
        -------
        y : np.ndarray shape (N,) — bass-enhanced output
        """
        # Step 1: Bass extraction
        x_lp = signal.convolve(x, self.lpf_b, mode='same')
        
        # Step 2: Harmonic generation
        if self.method == "A":
            x_harm = self._full_wave_integrate(x_lp)
        elif self.method == "B":
            x_harm = self._asymmetric_envelope(x_lp)
        else:
            x_harm = self._half_wave_clip(x_lp)
        
        # Step 3: Harmonic shaping BPF
        x_hs = signal.convolve(x_harm, self.bpf_b, mode='same')
        
        # Step 4: Dynamic gain scaling
        beta = np.exp(-1.0 / (0.030 * self.fs))  # 30ms RMS
        for n in range(len(x_lp)):
            self.e_lp = beta * x_lp[n]**2 + (1-beta) * self.e_lp
        g_harm = self.g_target * np.sqrt(self.e_lp / (np.max(x_lp**2) if np.max(x_lp**2) > 0 else 1.0))
        
        # Step 5: Dry path HPF + delay compensation
        x_hp = signal.convolve(x, self.hpf_b, mode='same')
        x_delayed = np.concatenate([
            np.zeros(self.delay), 
            x_hp[:-self.delay]
        ]) if self.delay > 0 else x_hp
        
        # Step 6: Output sum
        y = self.g_dry * x_delayed + g_harm * x_hs
        
        return y
```

### Cost

With FIR lengths $N=512$ and $f_s=48$ kHz: ~15–25 MIPS per voice in Python/NumPy; optimized C/DSP (Motorola 56371) achieves 12 MIPS for the full stereo chain with Bessel IIR filters. The harmonic generator itself is $\mathcal{O}(1)$ per sample.

## Musical Elements Framework

### PITCH
PBES does not modify pitch — it generates harmonics of the *existing* bass pitch. The perceptual effect reinforces the bass pitch's virtual fundamental: the listener hears the bass note at the same $f_0$ but perceptually "deeper." Polyphonic bass (two simultaneous pitches) generates intermodulation products; best results are monophonic or octave-related bass sources.

### RHYTHM
The envelope follower $g_{harm}[n]$ ducks harmonic gain during silences, preserving the original rhythmic contour. The asymmetric follower (Method B) has fast rise catching each attack and slow fall sustaining through the decay — enhances rhythmic definition by adding harmonic "crack" to attacks. Delay compensation keeps the harmonic path time-aligned.

### HARMONY
The harmonic path's BPF at $[f_c, 3f_c]$ places the 2nd and 3rd harmonics of the bass in the lower-midrange. These can harmonically reinforce chord tones ($f_0=65\,\text{Hz}$ (C2) → $2f=130\,\text{Hz}$ (C3)) or mask midrange voices if excessive. The effect is indirect but significant: bass gains psychoacoustic weight without occupying the subwoofer spectrum.

### STRUCTURE
Macro-form = per-section parameter schedule over $(f_c, g_{harm}, \text{method}, \alpha_{fall})$:
- Intro: dry only (PBES off)
- Verse: subtle $g_{harm}=0.10$, $f_c=120$ Hz, Method B
- Pre-Chorus: $g_{harm}=0.15$, $f_c=150$ Hz, $\alpha_{fall}=0.03$ (brighter)
- Chorus: $g_{harm}=0.25$, fast $\alpha_{fall}=0.02$, Method C
- Bridge: $g_{harm}=0.05$, $f_c=100$ Hz
- Outro: fade harmonic gain to 0
Section transitions ramp smoothly.

### TEXTURE
Per-voice PBES (separate on kick, bass synth, pad) creates stratified bass texture: kick PBES with fast envelope enhances punch, bass-synth PBES with slow envelope sustains, sub-pad PBES more subtle. Shared bus PBES folds all bass into one harmonic stream. Pairs with SP-008 compression and SP-007 spectral masking EQ.

## UnitMatrix Integration

**Voices** = rows. Each UnitMatrix voice carries its own PBES instance with parameter cluster $\theta_v = (f_c, g_{harm}, \text{method}, \alpha_{rise}, \alpha_{fall})$, or routes to a shared bass bus PBES.

**Sections** = columns. Each section defines $\theta_s$ — dry (off), subtle, full, bridge (warm), fade — and transitions interpolate $\theta$ over a crossfade window (32–256 samples). The RMS envelope follower state $E_{lp}[n]$ carries across section boundaries to avoid gain-reset thumps.

**Cell filling**: PBES is a post-process on the rendered audio buffer. The cell's `MusicUnit` events are rendered to audio by any synthesis engine; PBES is applied to the summed voice buffer for the section *after* the synthesis render and *before* spatialization/effects sends. The zero-drift invariant (equal-length tracks) is untouched — PBES does not change buffer length. Audio provenance records PBES parameters per section $\theta_s$ for reproducibility.

## Pitfalls

1. **Intermodulation distortion with polyphonic bass** — two simultaneous bass pitches through the same nonlinearity produce $|f_1 \pm f_2|$ products. Fix: per-voice PBES instances, or use Method B (asymmetric follower, lower intermodulation).
2. **Phase distortion from IIR filter group delay** — frequency-dependent delay misaligns harmonic and dry paths. Fix: linear-phase FIR with delay compensation; Bessel IIR if MIPS-constrained.
3. **Missing fundamental not universally perceived** — ~20–30% of listeners don't hear the virtual pitch. Fix: `fundamental_blend` knob to mix a small amount of real subwoofer content (SP-097).
4. **Over-enhancement → synthetic "buzzy" timbre** — $g_{harm} > 0.4$ or harmonics beyond 4th sound artificial. Fix: limit to $g_{harm} \le 0.35$, BPF at $[f_c, 3f_c]$.
5. **Spectral overlap with midrange voices** — 2nd harmonic of 80 Hz bass = 160 Hz (vocal range). Fix: dynamic sidechain EQ ducking the harmonic path.
6. **DC offset from asymmetric processing** — Methods B and C introduce DC bias. Fix: 20 Hz DC-blocking highpass after harmonic generator.
7. **Aliasing from nonlinear harmonics** — harmonics above Nyquist fold back. Fix: oversample 2× when $f_c > f_s/6$; otherwise ensure $3f_c < f_s/2$.
8. **Envelope follower attack "hole"** — harmonic gain may decay between bass attacks. Fix: $\alpha_{fall} \ge 3\tau_{attack}$; separate fast PBES for kick drum.