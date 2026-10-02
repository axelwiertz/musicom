# Report SP-102 — Amplitude Modulation Synthesis (AMS)

## Method Identity
- **Method ID:** SP-102
- **Method Name:** Amplitude Modulation Synthesis (AMS)
- **Layer:** absolute (sound production — Synthesis Engine)
- **One-line Description:** Modulates carrier oscillator amplitude with a modulator oscillator; sub-audio $f_m$ = tremolo, audio-rate $f_m$ = DSB+Carrier sidebands at $f_c \pm f_m$.
- **Candidate Code Path:** `sound/synthesis/am_synthesis.py`
- **Acronym:** AMS

## Summary Table Row

```
|| **SP-102** | Amplitude Modulation Synthesis (AMS) | **Synthesis Engines** | AM Sideband / Tremolo Timbres | Modulates carrier oscillator amplitude with a modulator oscillator $m(t) = [1 + m \cos(2\pi f_m t)]$. Sub-audio $f_m$ = tremolo; audio-rate $f_m$ = DSB+Carrier sidebands at $f_c \pm f_m$. $m$ controls sideband strength; $m>1$ overmodulation. $\mathcal{O}(1)$ per sample per voice. Candidate: `sound/synthesis/am_synthesis.py`. |
```

## Line Count
- **Before:** 22625 lines
- **After:** 22726 lines
- **Delta:** +101 lines

## Standalone File
- **Path:** `sound_method_SP-102_AMS.md`
- **Full path:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-102_AMS.md`

## Report File
- **Path:** `report_SP-102.md`
- **Full path:** `/opt/data/projects/Research/CompositionMethods/report_SP-102.md`

## Next Free SP ID
- **SP-103**

---

## Complete Section Text (Appended to methods_db.md)

```
---
# Amplitude Modulation Synthesis (AMS) (Method SP-102)

### Source
Strange, Allen (1983). *Electronic Music: Systems, Techniques, and Controls*. — d'Escrivan, Julio (2012). *Amplitude Modulation Synthesis*, in *The Oxford Handbook of Computer Music*. — Roads, Curtis (2015). *Composing Electronic Music: A New Aesthetic*. Oxford University Press, pp. 144–148. — Creasey, David (2004). *Audio Processes*, pp. 560–575.

### Layer
**absolute** — sound production method. Renders symbolic note events into raw audio by applying amplitude modulation between a carrier oscillator and a modulator oscillator at synthesis-engine level. Candidate code path: `sound/synthesis/am_synthesis.py`.

### Description
**Amplitude Modulation Synthesis (AMS)** is a time-domain synthesis technique where the instantaneous amplitude of a carrier oscillator (typically a sine wave or complex waveform) is varied proportionally to the instantaneous amplitude of a modulator oscillator. At sub-audio modulator frequencies ($f_m < 20$ Hz) the effect is perceived as tremolo — a periodic volume fluctuation. At audio-rate modulator frequencies ($f_m \ge 20$ Hz) the amplitude fluctuations are too fast to perceive as volume changes; instead, the ear hears new spectral components (sidebands) at the sum and difference frequencies of the carrier and modulator partials.

AMS is the simplest and most intuitive of the modulation synthesis family. It is the direct ancestor of Ring Modulation (SP-063, which suppresses the carrier) and a companion to FM (SP-010/SP-017, which modulates frequency rather than amplitude). Its distinguishing feature from RM is the **presence of the carrier** in the output and the use of a **unipolar modulating signal** (always $\ge 0$, achieved by adding a DC offset to the bipolar modulator).

### Technical Mechanics

**Basic AM (Double-Sideband with Carrier — DSB+Carrier):**

$$y(t) = A_c \left[1 + m \cdot \cos(2\pi f_m t)\right] \cos(2\pi f_c t)$$

where:
- $A_c$ = carrier amplitude
- $f_c$ = carrier frequency (Hz)
- $f_m$ = modulator frequency (Hz)
- $m$ = modulation index, $0 \le m \le 1$

Expanding the product reveals the three spectral components:

$$y(t) = A_c \cos(2\pi f_c t) + \frac{m A_c}{2} \cos\left[2\pi (f_c + f_m) t\right] + \frac{m A_c}{2} \cos\left[2\pi (f_c - f_m) t\right]$$

1. **Carrier** at $f_c$ with amplitude $A_c$
2. **Upper sideband (USB)** at $f_c + f_m$ with amplitude $mA_c/2$
3. **Lower sideband (LSB)** at $f_c - f_m$ with amplitude $mA_c/2$

When $f_m$ exceeds $f_c$, the lower sideband $f_c - f_m$ becomes negative — in AM synthesis it crosses through 0 Hz and is reflected back (folded) as a positive frequency (similar to FM aliasing but originating from the DC fold).

**Modulation Index $m$:**

$$m = \frac{\text{peak deviation}}{\text{carrier amplitude}} = \frac{A_{\max} - A_c}{A_c} = \frac{A_c - A_{\min}}{A_c}$$

- $m = 0$: no modulation — pure carrier sine.
- $m = 1$: 100% modulation — carrier envelope just touches zero.
- $m > 1$: **overmodulation** — envelope distortion generates additional sidebands beyond the fundamental three; the carrier envelope inverts at the trough, producing a waveform discontinuity that enriches the spectrum unpredictably (Creasey 2004).

**Unipolar Modulator Requirement:** To produce classic AM (DSB+Carrier), the modulator must be unipolar (positive only). This is achieved by adding a DC offset equal to the modulator's amplitude:

$$m(t) = 1 + m \cdot \cos(2\pi f_m t) \quad \text{where } m \le 1 \implies m(t) \ge 0$$

Ring modulation (SP-063) omits the DC offset (bipolar modulator), yielding DSB-SC.

**Generalization to Complex Waves:** For a carrier with $P$ partials at frequencies $f_{c,p}$ with amplitudes $A_{c,p}$ and a modulator with $Q$ partials at $f_{m,q}$ with amplitudes $A_{m,q}$:

$$y(t) = \sum_{p=1}^{P} \sum_{q=1}^{Q} A_{c,p} A_{m,q} \cos(2\pi f_{c,p} t) \left[1 + m \cdot \cos(2\pi f_{m,q} t)\right]$$

Each carrier partial produces a USB at $f_{c,p} + f_{m,q}$ and an LSB at $f_{c,p} - f_{m,q}$, so $P \times Q$ sideband pairs appear. For non-harmonic ratios of $f_c/f_m$, the result is inharmonic (bell-like, metallic). For integer ratios, the sidebands land on harmonic multiples of the fundamental.

**Discrete-Time Implementation:**

$$y[n] = A_c \left[1 + m \cdot \cos(2\pi f_m n / f_s)\right] \cos(2\pi f_c n / f_s)$$

Phase-accumulator-based oscillators for carrier and modulator, multiplied sample-by-sample:

```python
import numpy as np
def am_synthesis(f_c, f_m, sr, duration, m=0.5, A_c=0.5):
    n = np.arange(int(sr * duration))
    carrier = np.cos(2 * np.pi * f_c * n / sr)
    modulator = 1 + m * np.cos(2 * np.pi * f_m * n / sr)
    return A_c * carrier * modulator
```

**Complexity:** $\mathcal{O}(1)$ per sample per voice — two phase accumulators, one multiplier, one addition. Suitable for real-time polyphonic rendering.

### Musical Elements Framework

**PITCH:** The perceived pitch of an AM tone is ambiguous. When $m$ is low ($<0.5$), the carrier frequency $f_c$ dominates and the ear hears the carrier pitch with a sideband coloration. When $m \to 1$, the sidebands approach the carrier in amplitude, and the ear may hear the sideband interval (a major/minor chord if $f_c/f_m$ is a consonant ratio) or a pitch at the GCD of $(f_c, f_m, f_c\pm f_m)$. For sub-audio tremolo ($f_m < 20$ Hz), pitch is purely $f_c$.

**RHYTHM:** At sub-audio rates, the tremolo period $1/f_m$ provides a rhythmic pulsation that can lock to the bar grid. Section-based $f_m$ envelopes map to accelerando/ritardando of the tremolo rate. AM sideband spectrum changes at note onsets create rhythmic definition in the spectral domain.

**HARMONY:** Audio-rate AM ($f_m > 20$ Hz) generates a three-tone chord from a single note: $f_c$, $f_c+f_m$, $|f_c-f_m|$. By controlling the $f_c/f_m$ ratio, the composer selects the harmonic quality: $f_c/f_m = 1 \to$ octave, $2 \to$ twelfth (perfect 5th + octave), $3 \to$ double octave + major 3rd, $4 \to$ double octave + major 3rd + minor 3rd, etc. Irrational ratios yield inharmonic bell/gong spectra. Carrier/modulator waveform choice (saw/square/triangle) adds $P \times Q$ denser sideband clusters.

**STRUCTURE:** Section-level macro-form controls: per-section $m$ (dry→wet), $f_c$ (register), $f_m$ (harmonic density), and carrier/modulator waveform pair. AM-on/off creates a referenced structural contrast (pure tone → modulated). Overmodulation (m>1) acts as a structural intensifier (distortion climax).

**TEXTURE:** Multiple AM voices with different $(f_c, f_m, m)$ produce a polyphonic AM ensemble. Voice counts and spectral overlap (sideband collision) control density. AM of noise yields sideband-filtered noise textures. When $f_m$ approaches zero (DC), the effect disappears; when $f_m$ sweeps, the texture morphs continuously from tremolo to sideband-laden chord to inharmonic clangor.

### UnitMatrix Integration (Voices & Sections)

**Voices:** Each UnitMatrix voice is an AM-synthesis voice with independent $(f_{c,v}, f_{m,v}, m_v, \text{waveform}_v, A_{c,v})$ parameters. Percussion AM voices use noise carriers modulated by envelope-shaped modulator bursts. The per-voice AM parameter vector is stored in the voice metadata.

**Sections:** Each section $s$ defines an AM macro-envelope: $f_c(s)$, $f_m(s)$, $m(s)$, and a waveform pair selector. Section transitions interpolate these parameters linearly over a crossfade buffer, preventing clicks. A section with $m=0$ (pure sine) contrasts with $m=1$ (full AM chord), creating a structural A/B alternation.

**Cell filling:** Each cell $U_{v,s}$ specifies note events (MIDI pitch $\to$ $f_c$, gate $\to$ ADSR amplitude, velocity $\to$ $m$). The AM oscillator runs during the note's gate, and the rendered buffer is placed into the cell's time slot per the zero-drift invariant. The AM sideband timbre is intrinsic to the oscillator — no post-processing needed.

### Pitfalls

1. **DC offset from unipolar modulator:** The $1 + m\cdot\cos(\cdot)$ term produces a DC offset if the mean deviates from zero. AC-coupling (DC-blocking filter) after the render removes DC but may introduce a transient. Alternative: use DSB-SC (Ring Mod) and re-inject the carrier separately.
2. **Overmodulation distortion:** $m > 1$ causes carrier envelope inversion, generating unpredictable sidebands and potential aliasing. Bandlimiting the modulator or using oversampling helps. Use ADAA (SP-062) on the AM product for cleaner overmodulation.
3. **Sideband foldover:** When $f_m > f_c$, the LSB $f_c - f_m$ goes negative. The fold-back reflection creates spectral components that may clash with intended harmonic structure. Anti-aliased frequency shifting or careful $f_c/f_m$ planning is needed.
4. **Pitch ambiguity:** At high $m$, the ear may not track $f_c$ reliably. If the voice must carry a clear pitch (e.g., melody line), a secondary pure-tone oscillator mixed in at low level anchors the pitch.
5. **Sideband gap:** AM produces only one sideband pair per partial pair, whereas FM (SP-010) produces theoretically infinite sidebands. AM spectra are sparser — useful for clean chords but may sound thin for dense textures. Parallel AM voice stacking fills spectral gaps.
6. **Modulator choice:** Using a saw/square modulator instead of sine introduces $P \times Q$ partials quickly. A 10-partial carrier $\times$ 10-partial modulator = 200 sidebands + 10 carrier partials — controlled complexity versus potential muddiness.
```

---

## Technical Mechanics Summary

AMS is the foundational modulation synthesis method. Its core equation $y(t)=A_c[1+m\cos(2\pi f_m t)]\cos(2\pi f_c t)$ produces exactly three spectral components (carrier + sum/difference sidebands) for pure sine inputs, scaling to $P(2Q+1)$ components for complex waves. The method bridges tremolo (sub-audio modulation, rhythmic) and timbre synthesis (audio-rate modulation, harmonic/inharmonic). Key parameters: $f_c$ (pitch/register), $f_m$ (sideband spacing / harmonic density), $m$ (sideband strength / brightness), and waveform choice (spectral richness). Complexity $\mathcal{O}(1)$/sample.

## Quirks and Pitfalls Hit During Implementation

1. **Double-escaped LaTeX:** The `patch` tool double-escapes backslashes in LaTeX math expressions. The summary table row required a post-patch fix to convert `\\cos` back to `\cos`, `\\pm` to `\pm`, and `\\mathcal` to `\mathcal`. This was done with a targeted Python `replace()` on the file.
2. **Table row prefix normalization:** Existing rows use `|| ` (double pipe) prefix consistently for SP-097-SP-101. My added row matched this format. However, some earlier rows from the SP section had `|` single-pipe prefixes but these are artifacts from different table structures (the composition methods table above it uses single pipes).
3. **Patch string uniqueness:** The `|---|` separator appears many times in the file. Using the full SP-101 row as context ensured the correct target was matched.
4. **Symlink resolution:** The file paths `/opt/data/projects/Research/CompositionMethods/` is a symlink to `/opt/data/repos/musicom/projects/Research/CompositionMethods/`. Both resolve to the same physical file.

## Verification
- `grep -n 'SP-102' methods_db.md` shows line 274 (summary table) and line 22628 (detailed heading).
- Delta is +101 lines (22625 → 22726).
- Standalone file: `sound_method_SP-102_AMS.md` — 10232 bytes.
- Report file: `report_SP-102.md` (this file).
- No duplicate SP-102 found — summary table confirms unique ID.