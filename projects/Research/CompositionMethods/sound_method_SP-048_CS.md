# Commuted Synthesis (CS) — Method SP-048

Sound Production Method — Musicom Composition Methods Database
Category: **Synthesis Engines** (Physical Modeling family)
Target Output: Physical Plucked/Struck String Timbre

---

## 1. One-Line Summary

Commuted synthesis pre-convolves a measured (or modeled) instrument **body impulse response** with the **excitation** (pick/hammer) into a single aggregate **excitation table**, then drives a Karplus-Strong delay-line loop with that table. The expensive body resonator filter is eliminated from the per-sample loop — replaced by a one-time lookup-table read — giving realistic guitar/piano/marimba timbres at near-Karplus-Strong cost.

---

## 2. Source & History

Commuted synthesis was introduced by **Julius O. Smith III** at CCRMA, Stanford University, in the late 1980s and published in *Physical Audio Signal Processing* (W3K Publishing, 2010, ISBN 978-0-9745607-2-4; "Commuted Synthesis" and "Body-Model Factoring" sections). It was the enabling technology behind the first commercial physical-modeling synthesizers — the **Yamaha VL1/VL7 (1994)** and the **Korg Prophecy (1995)/Z1 (1997)** — which could not have run full waveguide-plus-body simulations on 1990s DSP chips.

The core insight is an application of the **commutativity of linear time-invariant (LTI) systems**. In a plucked/struck stringed instrument the excitation, the string, and the radiating body are chained in series, so their transfer functions multiply. Because convolution commutes, the body resonator can be moved from the end of the chain (after the string waveguide) to the front, where it is convolved once with the excitation to form a single aggregate excitation table.

In the Musicom catalog, commuted synthesis is the **efficiency counterpart** to SP-011 (Karplus-Strong), SP-023 (digital waveguide woodwind), SP-024 (bowed string), and SP-003/SP-042 (modal plate/bar modeling): those methods keep the resonator explicit and pay for it per sample; commuted synthesis pre-computes the resonator into the excitation and keeps only a cheap KS/waveguide loop at runtime.

---

## 3. Full Technical Mechanics

### 3.1 LTI Factorization

The radiated sound of a stringed instrument is modeled as a chain of LTI systems:

$$Y(z) = E(z) \cdot S(z) \cdot H_b(z)$$

- $E(z)$ = excitation (pick/hammer force)
- $S(z)$ = string (delay-line waveguide)
- $H_b(z)$ = body/soundboard/enclosure resonator

Since LTI systems commute, the body can be moved ahead of the string:

$$Y(z) = \underbrace{\left[ E(z) \cdot H_b(z) \right]}_{A(z)} \cdot S(z)$$

### 3.2 Aggregate Excitation Table

The bracketed term is precomputed once as a finite table:

$$a(n) = e(n) * h_b(n) = \sum_{m} e(m)\, h_b(n - m)$$

- **Pluck**: $e(n) = \delta(n)$ (single impulse) → $a(n) = h_b(n)$; the table *is* the body impulse response.
- **Hammer strike**: $e(n)$ is a short exponentially-decaying noise burst; $a(n)$ is the body response to that strike.
- **Pick-position comb filtering**: restored by injecting a second, negated impulse delayed by the round-trip travel time to the bridge (Smith's "pick-position illusion").

### 3.3 Karplus-Strong String Loop

At runtime the table is read once into a delay line of length $L = f_s / f_0$ samples, with a damping filter in the feedback path:

$$y(n) = a(n) + g \cdot \text{LPF}\!\left( y(n - L) \right)$$

- $g \approx 0.99$ = loop gain
- LPF = one-pole low-pass $H(z) = \dfrac{1-\alpha}{1-\alpha z^{-1}}$, $\alpha \in [0,1]$, or a moving-average filter

The loop produces the harmonic series at $f_0$ with high-frequency decay set by the filter; the table injects the body's formant envelope and attack transient on the first pass. Successive passes of the table through the loop are negligible because the loop gain is below unity and the table is much shorter than the loop delay.

### 3.4 Body-Model Factoring

The least-damped resonances of $h_b(n)$ are factored out and implemented as parallel biquads, leaving only the most-damped modal components in the table:

$$H_b(z) = \underbrace{\prod_{k} \frac{b_{0k} + b_{1k} z^{-1} + b_{2k} z^{-2}}{1 + a_{1k} z^{-1} + a_{2k} z^{-2}}}_{\text{parametric resonances}} \cdot H_{b,\text{residual}}(z)$$

Benefits: shorter table (less memory), better signal-to-quantization-noise ratio, and the dominant formants become real-time-controllable parameters (body size, material, mic position).

### 3.5 Table Shortening

If the measured $h_b(n)$ is too long, it is first converted to **minimum phase** (maximum shortening with identical magnitude spectrum), then windowed with the right wing of an exponential window $w(n) = r^n$, which has the interpretation of uniformly increasing resonator damping (all poles/zeros contracted radially in the $z$-plane by factor $r$).

### 3.6 Complexity

Per voice per sample: one table read (on note start), one delay-line read, one multiply, one filter — $O(1)$ per sample after the initial $O(L_{\text{table}})$ injection. The full body filter ($O(N_b)$ per sample) is eliminated entirely.

---

## 4. Musical Elements Framework

- **PITCH**: Set by the loop delay $L = f_s / f_0$ (MIDI→Hz), exactly as in Karplus-Strong (SP-011). The aggregate excitation table does not alter pitch — it only colors the spectrum — so pitch and timbre are fully decoupled. Fractional-delay interpolation (allpass) is required for accurate intonation at non-integer $L$.
- **RHYTHM**: Comes from the UnitMatrix onset grid and the attack transient baked into the table. Pluck tables (impulse excitation) give fast, bright attacks; hammer tables (noise-burst excitation) give softer, thumpier attacks with a longer noise component — the same pitch grid can be re-articulated with different tables to change the rhythmic feel without changing the notes.
- **HARMONY**: The string loop is a harmonic comb (integer multiples of $f_0$), so the output is strongly pitched and harmonically consonant with itself. The body's formant envelope (baked into the table) emphasizes fixed frequency regions independent of the played pitch — this is exactly how real instruments keep their identity across registers. Body-model factoring lets the composer tune the dominant formants per section, shifting the perceived brightness/register of a chord without changing its notes.
- **STRUCTURE**: Macro-form is expressed through table selection and factored-resonance settings per section. Section A = small body (short, bright table); section B = large body (long, dark table with low formants); a continuous crossfade between two tables (interpolated per note) gives a smooth timbral morph across section joins — the physical-modeling analogue of SP-041's wavetable morphing.
- **TEXTURE**: Texture density is controlled by the number of voices, each with its own table and loop. Dense plucked textures (many short-decay loops) give a guitar/mandolin strum; long-decay loops with dark tables give a piano/soundboard wash. The noise component of hammer tables adds inharmonic attack texture that the pure KS loop lacks.

---

## 5. UnitMatrix Integration (Voices and Sections)

- **Rows (Voices)**: Each voice $v$ is an independent commuted-synthesis instrument: its own aggregate excitation table $a_v(n)$, loop gain $g_v$, damping coefficient $\alpha_v$, and (optionally) factored body biquads. Voice 1 (lead) = bright pluck table + short decay; Voice 2 (bass) = dark hammer table + low $f_0$; Voice 3 (pad) = long-decay loop + heavily damped table; Voice 4 (percussion) = noise-burst table + very short loop (near-impulse). Each row renders to a mono buffer, then summed or spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)**: Each section $s$ supplies (a) a table selection or crossfade target, (b) loop gain/damping settings, and (c) factored body-resonance parameters. Section boundaries = table swaps or crossfades; a continuous table morph across joins gives seamless timbral transitions, a hard swap gives discrete contrast.
- **Cells** $U_{v,s}$:
  - `{PITCH}`: MIDI pitch → loop delay $L = f_s / f_0$ (with fractional-delay allpass for intonation).
  - `{RHYTHM}`: Onset/offset grid from the UnitMatrix; each onset triggers a fresh table read into the loop.
  - `{TEXTURE}`: The aggregate excitation table (or its crossfade position), loop gain $g$, damping $\alpha$, and factored biquad settings — the cell's timbre and decay character.
- **Mapping Flow**:
  1. Measure or model the body impulse response $h_b(n)$; convolve with the chosen excitation $e(n)$ to build each aggregate table.
  2. Optionally factor the least-damped resonances into biquads and shorten the table (minimum-phase + exponential window).
  3. For each voice, run the KS loop at the cell's pitch; on each note onset, read the table into the loop.
  4. Sum voices; post-process (SP-007 EQ, SP-008 DRC, SP-009/SP-032 reverb); export audio or spatialize.
  5. Validate zero-drift upstream via the musicom engine (commuted synthesis is downstream of the symbolic UnitMatrix).

---

## 6. Implementation Sketch (Python / NumPy)

```python
import numpy as np
from scipy.signal import lfilter

def midi_to_hz(p):
    return 440.0 * 2 ** ((p - 69) / 12)

def make_pluck_excitation(n=8):
    """Impulse excitation (ideal pluck)."""
    e = np.zeros(n); e[0] = 1.0
    return e

def make_hammer_excitation(n=64, tau=0.03, fs=44100):
    """Short exponentially-decaying noise burst (hammer strike)."""
    t = np.arange(n) / fs
    return np.random.randn(n) * np.exp(-t / tau)

def make_body_ir(fs=44100, dur=0.15, n_res=5):
    """Synthetic body impulse response: sum of damped sinusoids (formants)."""
    n = int(dur * fs)
    t = np.arange(n) / fs
    h = np.zeros(n)
    rng = np.random.default_rng(0)
    for k in range(n_res):
        f = 300 + 400 * k + 150 * rng.random()      # formant freqs
        d = np.exp(-t / (0.01 + 0.02 * k))          # decreasing damping
        h += d * np.sin(2 * np.pi * f * t)
    h /= np.max(np.abs(h)) + 1e-9
    return h

def commuted_synth(midi_notes, excitation, body_ir, fs=44100,
                   loop_gain=0.995, damping=0.5, body_gain=1.0):
    """Render a mono commuted-synthesis voice.

    midi_notes: list of (pitch, dur_sec, velocity).
    excitation: e(n); body_ir: h_b(n). Aggregate table a = e * h_b.
    """
    a = np.convolve(excitation, body_ir) * body_gain   # aggregate excitation table
    total = int(sum(dur for _, dur, _ in midi_notes) * fs) + fs
    out = np.zeros(total)
    t_idx = 0
    for pitch, dur, vel in midi_notes:
        nsamp = int(dur * fs)
        L = fs / midi_to_hz(pitch)                    # loop delay (samples)
        # fractional-delay split: integer delay + first-order allpass
        Li = int(np.floor(L)); frac = L - Li
        buf = np.zeros(Li + 2)
        prev = 0.0
        for i in range(nsamp):
            # inject aggregate table on note start
            if i < len(a):
                buf[0] += a[i] * vel
            # read delay line
            dly = buf[0]
            # allpass fractional delay
            ap = frac * dly + prev
            prev = dly - frac * ap
            # one-pole damping in feedback
            fb = ap * (1 - damping) + damping * buf[-1]
            buf[-1] = fb
            out[t_idx] = ap
            # shift delay line
            buf = np.roll(buf, -1)
            buf[-2] = loop_gain * fb
            t_idx += 1
    return out
```

**Production notes**:
- The per-sample Python loop above is for clarity — use a compiled loop (Cython/Numba/C) or a real-time environment in production; the DSP itself is trivial ($O(1)$ per sample).
- The musicom engine handles UnitMatrix fill and zero-drift MIDI export upstream; commuted synthesis consumes the symbolic pitch/onset data as `midi_notes`.
- **Table design**: keep the aggregate table shorter than the shortest loop delay ($L_{\min} = f_s / f_{0,\max}$) so the injection finishes before the first loop readback; otherwise the tail of the table collides with the first feedback pass. Shorten via minimum-phase conversion + exponential window when needed.

---

## 7. Pitfalls

1. **Table longer than the loop delay**: If $a(n)$ is longer than $L = f_s / f_0$, the table's tail overlaps the first feedback pass and smears the attack. Fix: shorten the table (minimum-phase + exponential window) or cap the table at $L_{\min}$ samples.
2. **Loop instability / runaway**: Loop gain $g \ge 1$ with a lossless filter causes the delay line to ring forever or blow up. Fix: keep $g \le 0.995$ and always include a damping filter in the feedback path; clamp the buffer per sample.
3. **Pitch inaccuracy from integer delay**: Using `int(fs/f0)` quantizes pitch audibly at high registers. Fix: fractional-delay allpass interpolation (first-order allpass suffices for plucked timbres).
4. **DC / low-frequency buildup**: A body IR with DC offset or a very low formant injects rumble that the loop sustains. Fix: high-pass the table (or the final voice) at ~20–40 Hz; remove DC from $h_b(n)$ before convolution.
5. **Loss of pick-position character**: A single impulse excitation loses the comb-filtered pick-position timbre. Fix: inject a second, negated impulse delayed by the round-trip travel time to the bridge (Smith's pick-position illusion), or use a measured pluck excitation.
6. **Nonlinearity of real strings**: Commuting assumes the string is LTI; real strings stiffen (slight pitch rise with amplitude) and couple polarizations. Fix: acceptable for most timbres — the error is inaudible for plucked/struck sounds; for bowed strings keep the explicit nonlinear model (SP-024) instead.
7. **Table quantization noise**: A long, heavily damped table wastes bits on inaudible tail samples and raises quantization noise. Fix: body-model factoring — pull the least-damped resonances into biquads, keep only the most-damped components in the table.
8. **Static timbre across the piece**: Reusing one table for every note makes the instrument sound sampled and lifeless. Fix: crossfade between multiple tables (pluck position, body size, mic distance) per section, and modulate the factored biquad formants for real-time timbral evolution.

---

## 8. Comparison With Related Methods

| Method | Resonator | Runtime Cost | Timbre Source | Control |
|---|---|---|---|---|
| Karplus-Strong (SP-011) | None (loop damping only) | $O(1)$ | Loop + filter | Pitch, decay |
| Commuted Synthesis (SP-048) | Baked into excitation table (+ optional biquads) | $O(1)$ | Measured body IR | Pitch, table, factored formants |
| Digital Waveguide Woodwind (SP-023) | Explicit reflection filter | $O(1)$ | Reed + pipe model | Pitch, pressure, filter |
| Bowed String (SP-024) | Explicit (nonlinear friction) | $O(1)$ w/ Newton solve | Bow-string friction | Pitch, bow force/velocity |
| Modal Bank (SP-042) | Explicit parallel biquads | $O(N_{\text{modes}})$ | Eigenmode decomposition | Per-mode gain/damping |

---

## 9. References

- Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing. "Commuted Synthesis" and "Body-Model Factoring" sections. https://ccrma.stanford.edu/~jos/pasp/Commuted_Synthesis.html
- Smith, J. O. (1993). "Efficient Synthesis of Stringed Musical Instruments." *Proceedings of the International Computer Music Conference (ICMC)*, Tokyo.
- Karjalainen, M., Välimäki, V., and Jánosy, Z. (1993). "Towards High-Quality Sound Synthesis of the Guitar and String Instruments." *ICMC*, Tokyo. (Commuted-synthesis guitar models.)
- Karplus, K. and Strong, A. (1983). "Digital Synthesis of Plucked-String and Drum Timbres." *Computer Music Journal* 7(2). (The KS loop reused by commuted synthesis.)
- Yamaha VL1/VL7 (1994) — first commercial physical-modeling synths using commuted-synthesis-style excitation tables. (Owner's manual, "Physical Modeling" section.)
- Korg Prophecy (1995) / Z1 (1997) — MOSS physical-modeling engines with plucked-string models. (Owner's manuals.)
