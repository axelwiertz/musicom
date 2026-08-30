# Dispersive Waveguide Spring Reverb (DWSR) — SP-058

**Method ID**: SP-058
**Layer**: Synthesis Engines
**Paradigm**: Nature-Led (physical modeling of a metal spring tank)
**Target Output**: Physical spring-reverb ambience / metallic, inharmonic, "boing"-chirping tail

---

## One-line description

Audio reverberation by physically modeling a helical spring tank as a **dispersive digital waveguide**: a feedback delay line (the spring's round-trip) into which is inserted a cascade of **negative-coefficient first-order allpass filters** — whose frequency-dependent group delay reproduces the spring's stiff-string dispersion $c_p \propto \sqrt{\omega}$ (high frequencies propagate faster) — plus a one-pole damping filter. Two to three coprime-length springs give the dense, non-flanging, metallic wash and the characteristic downward "boing"/"drip" attack chirp of a real Accutronics tank. The physical-modeling reverb that fills the gap between SP-009 (convolutive room IR) and SP-032 (abstract FDN).

---

## Full technical mechanics

### The dispersive stiff-string wave equation

A helical spring carries transverse bending waves obeying the dispersive stiff-string PDE (shared with piano-string modeling, hence the kinship to SP-042 modal banks and SP-048 commuted synthesis):

$$\rho A\,\frac{\partial^2 u}{\partial t^2} = \kappa\,\frac{\partial^2 u}{\partial x^2} - EI\,\frac{\partial^4 u}{\partial x^4},$$

where $u(x,t)$ is transverse displacement, $\rho A$ mass per unit length, $\kappa$ the effective stiffness ("tension" analogue for a coil), $EI$ the bending rigidity. The fourth-order term makes the medium dispersive.

### Dispersion relation

For a plane wave $u \propto e^{j(\omega t - kx)}$:

$$\omega^2 = c^2 k^2 + b^2 k^4, \qquad c = \sqrt{\kappa/\rho A},\quad b = \sqrt{EI/\rho A},$$

with phase velocity

$$c_p^2(\omega) = \tfrac{1}{2}\Big(c^2 + \sqrt{c^4 + 4b^2\omega^2}\Big).$$

Limits: low $\omega$ gives $c_p \approx c$ (non-dispersive); high $\omega$ gives $c_p \approx \sqrt{b\omega}$ (velocity grows with frequency). **High frequencies traverse the spring faster and return earlier** — this is the entire mechanism behind the downward "boing" chirp.

### Dispersive allpass approximation

A plain delay line propagates all frequencies at one speed. Dispersion is injected as a cascade of $M$ first-order allpass filters with **negative** coefficient $a \in (-1,0)$:

$$A(z) = \frac{a + z^{-1}}{1 + a z^{-1}}, \qquad \tau_g(\omega) = \frac{1 - a^2}{1 + a^2 + 2a\cos\omega}.$$

For $a < 0$ the group delay is *large at low frequency, small at high frequency* — matching the spring's physical dispersion. Writing $a = -a_0$ ($a_0>0$), the DC-to-Nyquist delay swing per section is

$$\tau_g(0) - \tau_g(\pi) = \frac{4a_0}{1 - a_0^2}.$$

$M$ (dispersion order) and $a_0$ (dispersion strength) are the two timbre knobs.

### Spring tank topology

Per spring $s$: drive gain $g_s$ → dispersive waveguide (delay $z^{-L_s}$ + allpass cascade $A^M(z)$ in the loop) → one-pole damping filter $D(z)=g_d(1-\alpha)/(1-\alpha z^{-1})$ → output taps at a few positions (drive/mid/pickup), summed. Loop gain $g_d<1$ sets $T_{60}$; $\alpha$ gives frequency-dependent decay (HF dies faster). Optional $\tanh(\cdot)$ at the drive tap models magnetic-transducer saturation ("drip").

Impulse response = an infinite train of increasingly low-pass-filtered, increasingly dispersively-spread echoes: "boing" chirp on early returns, melting into smooth metallic wash on late returns. $S=2$–$3$ coprime-length springs raise echo density enough to read as reverb rather than discrete delays.

### Complexity

$\mathcal{O}(SM)$ per sample ($S$ springs $\times M$ allpass sections + 1 damping filter each); memory $\mathcal{O}(L)$ per spring. Real-time for several voices on a single core.

---

## Python / NumPy implementation sketch

```python
import numpy as np

def spring_reverb(x, sr=44100, springs=((2203, 0.62, 12), (1789, 0.58, 14), (1511, 0.54, 16)),
                  drive=0.5, alpha=0.15, wet=1.0, dry=0.5):
    """Dispersive waveguide spring reverb (SP-058).
    springs: (delay_len_samples, loop_gain, allpass_order) per spring.
    a0 < 0 is the dispersive allpass coefficient (negative => low freq delayed more)."""
    a0 = 0.55                                # dispersion strength in (0,1)
    out = np.zeros_like(x)
    for L, g_loop, M in springs:
        buf = np.zeros(L)                     # circulating delay line
        ap_x = np.zeros(M)                    # allpass state (x-memory)
        ap_y = np.zeros(M)                    # allpass state (y-memory)
        dl = 0.0                              # damping one-pole state
        ptr = 0
        for n in range(len(x)):
            v = g_loop * dl                    # read damped circulating sample
            dl += alpha * (buf[ptr] - dl)      # one-pole LP damping update
            s = drive * x[n] + v               # inject dry + feedback
            # dispersive allpass cascade (negative coeff)
            for m in range(M):
                u = s - a0 * ap_x[m]           # forward
                ap_y[m] = u
                s = ap_x[m] + a0 * u           # output = state + a0*u
                ap_x[m] = u - a0 * ap_y[m]     # update state
            buf[ptr] = s
            # output taps (integer offsets, wrapped)
            out[n] += wet * (0.3 * buf[(ptr - 0) % L]
                            + 0.5 * buf[(ptr - L // 3) % L]
                            + 0.7 * buf[(ptr - 2 * L // 3) % L])
            ptr = (ptr + 1) % L
    return dry * x + out

# --- Musicom integration (conceptual) ---
# Render each voice's dry buffer via its synthesis engine (any SP-xxx),
# run spring_reverb() per voice with its tank recipe, sum voices,
# post-process (SP-007 EQ / SP-008 DRC), optionally spatialize (SP-021/034/043).
# Fill UnitMatrix cells, validate zero-drift, export via the musicom engine
# (composer.validate() + composer.to_midi()) per AGENTS.md — never hand-roll mido.
```

**Tooling**: pure NumPy (JIT-compile the per-sample loop with Numba for real-time); no FFT, no convolution, no recorded IR. DWSR consumes *rendered audio buffers* from any SP-xxx voice engine and returns a reverberant buffer.

---

## Musical Elements Framework

- **PITCH**: Pitch-transparent — preserves the dry fundamental exactly; only adds a dispersive tail. The "boing" is broadband/transient (inharmonic chirp), not a pitched note. High dispersion smears fast lines into a shimmering wash.
- **RHYTHM**: Spring delay lengths are rhythmic *periods* in the tail; short tank = fast dense decay, long tank = slow spacious decay. Tuned delay length ($L = f_s \cdot 60/\text{BPM}$) turns the spring into a syncopated "drip" echo. The chirp softens grid-locked onsets (012/032) into flow.
- **HARMONY**: Inharmonic by construction (dispersive modes are not integer multiples), so the tail is harmonically "neutral" — adds shimmer without beating, ideal for dense chromatic/dissonant material; poor choice when a warm tonal bloom is wanted (use SP-009). $a_0$ tunes how much the tail detunes the spectrum.
- **STRUCTURE**: Tank recipe per section. Section A = short/bright (snappy), B = long/dark (washy), coda = layered second spring. The stateful tail carries across section joins — naturally continuous form-glue (FDN SP-032 shares this; convolutive SP-009 cannot).
- **TEXTURE**: The tail *is* texture — fills gaps between sparse onsets with a continuous metallic wash (directly serves the 011/032 hybridization rule). "Boing" = per-note chirp accent; per-spring uncorrelated density = smooth non-flanging wash.

---

## UnitMatrix Integration

- **Rows (Voices)**: Each voice $v$ gets its own tank (own springs, lengths, dispersion, decay). Lead = short/bright; bass = dry or very short (avoid low-end mud); pad = long/dark; percussion = medium + high dispersion (max "drip").
- **Columns (Sections)**: Per-section tank recipe (spring count, lengths, dispersion, decay) forms a timbre arc; dispersion ramp morphs the tail near-harmonic → metallic without touching the dry signal.
- **Cells** $U_{v,s}$: `{PITCH}` unchanged (post-render); `{RHYTHM}` = tank delay length per section; `{HARMONY}` = dispersion $a_{0,v,s}$ (how inharmonically the tail smears the chord); `{TEXTURE}` = wet/dry + decay $\alpha_{v,s}$ (sparse cells long/wet, dense cells short/dry).
- **Mapping Flow**: compose → validate zero-drift → export MIDI → render each voice dry → apply DWSR per voice → sum → EQ/DRC → spatialize.

---

## Pitfalls

1. **Comb-filter flanging** — single spring, no dispersion/damping = comb filter (picket-fence resonances). Fix: $S \ge 2$ coprime-length springs + $\alpha > 0$. Verify smooth dense impulse-response spectrum.
2. **Dispersion sign error** — positive allpass coeff ($a>0$) reverses the chirp (upward "doink"). Fix: use $a \in (-1,0)$.
3. **Instability** — loop gain $\ge 1$ rings/blows up. Fix: $|g_d| < 1$ (0.6–0.85), modest $\alpha$, hard-clamp while tuning; verify decay below −60 dB within target $T_{60}$.
4. **Low-end buildup / DC drift** — dispersive allpass delays lows more → muddy tail + DC. Fix: DC-blocking high-pass in the loop; keep bass dry/short-tank.
5. **Tap aliasing / stale reads** — non-integer/negative tap indices click. Fix: integer offsets modulo $L$, zero-fill, advance write pointer before read.
6. **Stateful tail → unpredictable joins** — loud section A rings into B. Fix: expose per-section fade "dump" for clean breaks; use carryover for continuous forms.
7. **Bass through spring = mud** — smears low transients, phase cancellation. Fix: high-pass the send (~150 Hz) or keep bass dry.
8. **Pure-Python per-sample cost** — $S \times M$ first-order sections per sample too slow in a naive loop. Fix: Numba JIT, vectorize as matrix recurrence, or collapse the cascade to one high-order allpass IIR.

---

## Comparison with related methods

| Method | Tail source | Dispersion / chirp | Tonal character | Cost | Stateful carryover |
|---|---|---|---|---|---|
| Convolutive reverb (SP-009) | Recorded room IR | None (linear) | Warm, realistic, tonal | $O(N\log N)$ FFT | No |
| FDN reverb (SP-032) | Delay network + unitary matrix | None (flat delay) | Smooth, neutral, tail-only | $O(K)$/sample | Yes |
| Commuted synthesis (SP-048) | Aggregate excitation + KS loop | None (body factored) | Plucked/struck *instrument* | $O(1)$ | No |
| **Spring reverb (SP-058)** | **Dispersive waveguide** | **Physical "boing" ($c_p\propto\sqrt{\omega}$)** | **Metallic, inharmonic, vintage** | **$O(SM)$/sample** | **Yes** |

---

## References

- Hammond, L. (1941). "Reverberation Device." *U.S. Patent 2,230,836* (filed 1939).
- Välimäki, V., Pakarinen, J., Erkut, C., & Karjalainen, M. (2006). "Discrete-time modelling of musical instruments." *Reports on Progress in Physics* 69(1), 1–78.
- Bilbao, S. (2009). *Numerical Sound Synthesis: Finite Difference Schemes and Simulation in Musical Acoustics.* Wiley.
- Abel, J. S., Berners, D. P., Costello, S., & Smith, J. O. (2006). "Spring reverb emulation using dispersive allpass filters in a waveguide structure." *Audio Engineering Society Convention 121*, preprint 6954.
- Smith, J. O. (2010). *Physical Audio Signal Processing.* W3K Publishing.
- Parker, J. (2011). "Spring reverberation: A physical perspective." *Proc. DAFx-11*.
