# SP-150 — Helmholtz Cavity-Resonator Synthesis (HCRS)

**Layer:** absolute (sound production) · **Category:** Synthesis Engines · **Candidate module:** `sound/synthesis/helmholtz_cavity.py`
**Status:** verified prototype 19/19 (`_web150_hcris/verify_hcris.py`), demo `projects/Research/outputs/sp150_hcris/sp150_hcris_demo.wav`

---

## 1. What the method is

A cavity with a restricted opening is a **lumped acoustic oscillator**: the air plug in
the neck is a mass, the air in the cavity is a spring. Blow across the opening and the
system self-oscillates at one frequency — the *only* frequency it has.

$$f_0=\frac{1}{2\pi}\sqrt{\frac{1}{M_aC_a}}=\frac{c}{2\pi}\sqrt{\frac{A}{V\,L_{eq}}}$$

Vessel flutes (ocarina, gemshorn, xun), bottles, the Igbo **udu**, ghatam, djembe and
**bass-reflex** ports are all this one object with different ratios. HCRS makes the
geometry the score: written pitch ⇒ cavity dimensions, so the synthesis is *sizing an
instrument* rather than filtering a waveform.

## 2. Derivation of the lumped model

Start from the two acoustic element laws.

**Cavity compliance.** For a cavity of volume $V$ with a small opening, adiabatic
compression gives (with $U$ = volume velocity into the cavity)

$$p=\frac{\rho c^2}{V}\int U\,dt \quad\Longrightarrow\quad C_a=\frac{V}{\rho c^2}\ \left[\frac{\mathrm{m^4\,s^2}}{\mathrm{kg}}\right].$$

**Neck inertance.** The air in a neck of length $L$, area $A$ moving as a slug:

$$\Delta p=\frac{\rho L}{A}\frac{dU}{dt}\quad\Longrightarrow\quad M_a=\frac{\rho L}{A}\ \left[\frac{\mathrm{kg}}{\mathrm{m^4}}\right].$$

Mass–spring resonance $1/\sqrt{M_aC_a}$ then yields the tuning law. Two refinements
matter in practice:

1. **End correction.** The slug extends beyond the physical neck by
   $L_{eq}=L+\Delta L$, with $\Delta L\approx0.613a$ for an unflanged (free) opening,
   $0.8216a$ for a flanged/baffled one (Chanaud 1965; the plane-piston radiation limit is
   $8a/3\pi\approx0.849a$). A reflex port has one of each: $L_{eq}=L+1.463a$.
   Choosing the wrong one is a **3.8 % pitch error** (≈0.65 semitone) on a 20 mm neck.
2. **Aspect ratio.** When the neck is short and wide, or the cavity is not large compared
   with the neck, the lumped model degrades toward a pipe; Alster (1972) gives correction
   polynomials for that regime.

## 3. Losses and Q

Three independent loss channels, each expressed as a damping ratio $\delta=1/Q$:

$$Q_{\text{rad}}=\frac{2\pi L_{eq}c}{A\omega_0}\quad\text{(monopole radiation, }P_{rad}=\rho c k^2U^2/4\pi)$$

$$Q_{\text{visc}}=\frac{\omega_0 M_a}{R_v},\qquad R_v=\frac{L\sqrt{2\rho\mu\omega_0}}{\pi a^3}\quad\text{(Stokes layer in the neck)}$$

$$Q_{\text{th}}=\frac{2V}{S_w\delta_t(\gamma-1)},\qquad \delta_t=\sqrt{2D/\omega_0}\quad\text{(thermal layer on the cavity wall)}$$

$$Q^{-1}=Q_{\text{rad}}^{-1}+Q_{\text{visc}}^{-1}+Q_{\text{th}}^{-1},\qquad
\tau=\frac{Q}{\pi f_0},\qquad T_{60}=6.91\tau$$

Verified for a 120 mL body at C5: $Q_{rad}=59.5$, $Q_{visc}=38.1$, $Q_{th}=440.8$ ⇒
$Q=22.07$, $\tau=13.4$ ms, $T_{60}=93$ ms. Because opening holes raises both $f$ and $A$,
$Q$ falls with register — **the treble is more damped than the bass** (C6: $Q=4.75$ with
the single-neck model; real multi-hole instruments are less extreme, hence the
`q_scale` calibration knob).

## 4. Excitation: the jet drive

The cavity is driven by the jet that flips across the labium (Coltman 1968):

$$u_j=C_v\sqrt{2p_m/\rho},\qquad u_c\approx0.4\,u_j,\qquad \tau_j=L_j/u_c$$

$$Q_{ac}(t)=G\,u_j\,\tanh\!\left(\frac{p_c(t-\tau_j)}{p_{sat}}\right)$$

The $\tanh$ is the labium's saturation; the delay is the jet's travel time. The
oscillation frequency is the solution of the **loop phase condition**

$$\arg H(e^{j\omega})=2\pi f\tau_j,$$

and since a two-pole resonator's phase is positive only below $f_0$, the sounding pitch is
always slightly flat of the cavity resonance, climbing toward $f_0$ as blowing shortens
$\tau_j$. Measured: 435.08 Hz simulated vs 434.99 Hz predicted (−1.12 % vs $f_0$ at
800 Pa); 400 → 1600 Pa moves 432.1 → 436.4 Hz (**+0.172 semitone**), matching the
ocarina literature's "about a third of a semitone either way". Level compresses to
**+7.97 dB** for 4× pressure (linear would be 12.04 dB).

## 5. Fingering law

$$f\propto\sqrt{A_{\text{open}}},\qquad A_{\text{open}}=\sum_{\text{open holes}}\pi a_i^2\ (+A_{\text{voicing}}\ \text{if all closed})$$

Inverted for synthesis:

$$A_{\text{required}}=\frac{V L_{eq}\,(2\pi f)^2}{c^2}.$$

One extra 8 mm hole on the C5 body (82.2 mm² base) multiplies area by 1.612 and pitch by
1.2696 = **+4.13 semitones**. Equal-area holes are *not* equal intervals — hole sizes must
be individual.

## 6. Membrane coupling (udu / djembe / ghatam)

A skin over an opening couples a membrane mode $f_m$ to the cavity mode $f_c$. In $f^2$
form the coupled system is a 2×2 symmetric eigenproblem:

$$\begin{bmatrix}f_c^2 & \kappa\\ \kappa & f_m^2\end{bmatrix},\qquad
f_\pm^2=\frac{f_c^2+f_m^2}{2}\pm\sqrt{\left(\frac{f_c^2-f_m^2}{2}\right)^2+\kappa^2}$$

The modes repel (avoided crossing) and $\sum f^2=f_c^2+f_m^2$ is invariant. Verified:
150/210 Hz → 144.72/213.67 (κ=6000) → 102.81/236.71 (κ=20000). Port covering changes $f_c$
and therefore both modes — the udu/ghatam "talking" bend.

## 7. Reflex-port alignment

The same oscillator used deliberately: with port tuning $f_b$ below the driver's $f_s$,
the port's rear output arrives in phase with the cone's front output across the band
between the two resonances. 40 L + ⌀75 × 150 mm ⇒ **40.08 Hz**; 30 Hz needs **71.4 L**.
This is the production route to HCRS sub-bass without an unphysical bottle.

## 8. Reference implementation (NumPy)

```python
import numpy as np

RHO, C, MU, GAMMA, DTH = 1.204, 343.0, 1.81e-5, 1.4, 2.2e-5

def tune(V, A, L, a, end_k=0.613):
    """Volume [m3], area [m2], neck length/radius [m] -> (f0, L_eq)."""
    L_eq = L + end_k * a
    return C / (2 * np.pi) * np.sqrt(A / (V * L_eq)), L_eq

def area_for(f, V, L, a, end_k=0.613):
    return V * (L + end_k * a) * (2 * np.pi * f / C) ** 2

def losses(V, A, L, a, f0, S_wall):
    w0 = 2 * np.pi * f0
    L_eq = L + 0.613 * a
    q_rad = 2 * np.pi * L_eq * C / (A * w0)
    R_v = L * np.sqrt(2 * RHO * MU * w0) / (np.pi * a ** 3)
    q_visc = w0 * (RHO * L_eq / A) / R_v
    q_th = 2 * V / (S_wall * np.sqrt(2 * DTH / w0) * (GAMMA - 1))
    return 1.0 / (1 / q_rad + 1 / q_visc + 1 / q_th)

class HelmholtzVoice:
    """One vessel: biquad resonator + jet delay line + saturation."""

    def __init__(self, f0, Q, pm, fs, L_jet=1.5e-3, Cv=0.6, G=60.0, p_sat=100.0):
        w0 = 2 * np.pi * f0 / fs
        alpha = np.sin(w0) / (2 * Q)
        a0 = 1 + alpha
        self.b = (alpha / a0, 0.0, -alpha / a0)          # RBJ bandpass
        self.a = (-2 * np.cos(w0) / a0, (1 - alpha) / a0)
        u_j = Cv * np.sqrt(2 * pm / RHO)
        self.D = max(1, int(round((L_jet / (0.4 * u_j)) * fs)))
        self.g, self.p_sat, self.fs = G * u_j, p_sat, fs
        self.z1 = self.z2 = 0.0
        self.hist = np.zeros(self.D + 1)

    def render(self, n, onset_noise=1e-3, rng=None):
        rng = rng or np.random.default_rng(0)
        out = np.empty(n)
        b0, _, b2 = self.b
        a1, a2 = self.a
        x2 = z1 = z2 = 0.0
        for i in range(n):
            e = self.g * np.tanh(self.hist[0] / self.p_sat)
            if i < int(0.004 * self.fs):                 # breath onset
                e += onset_noise * self.g * rng.standard_normal()
            x = b0 * e + b2 * x2
            x2 = e
            y = x - a1 * z1 - a2 * z2
            z2, z1 = z1, y
            out[i] = y
            self.hist[:-1] = self.hist[1:]
            self.hist[-1] = y
        return out

# --- example: C5 ocarina body, 120 mL, 8 mm voicing, 5 mm wall
V, a, L = 1.2e-4, 4e-3, 5e-3
f0, L_eq = tune(V, area_for(523.25, V, L, a), L, a)
print(f0, L_eq)
```

Notes for integration:
* the delay line is only a few hundred samples ($\tau_j\le1$ ms), so a ring buffer is fine;
* `q_scale` (default 1.0) corrects the single-neck loss model for multi-hole instruments;
* breath noise must scale with $u_j$ (it is the "air", not a constant hiss);
* for zero-drift safety render exactly `round(section_ticks/TPB*60/bpm*fs)` samples and
  truncate tails at the section seam.

## 9. Musical behaviour summary

| axis | behaviour |
|---|---|
| pitch | exact geometry law; intervals clean, single mode; breath bends ±0.2 semitone |
| dynamics | amplitude ∝ $\sqrt{p_m}$, compressed (+7.97 dB per 4× pressure) |
| articulation | fixed by $Q$: bass rings, treble ticks; strike vs blow is an excitation choice |
| register | one octave = 4× cavity volume; 30 Hz ⇒ ~71 L or a reflex port |
| tuning | fingerings quantise pitch on the hole-area grid; half-holing for microtones |
| harmony | no partials ⇒ clusters stay transparent; membrane adds one inharmonic partner |

## 10. References

- Helmholtz, H. von (1863). *Die Lehre von den Tonempfindungen* (Eng. *On the Sensations of Tone*, Dover 1954).
- Rayleigh, Lord (1896). *The Theory of Sound*, vol. II.
- Chanaud, R. C. (1965). Effects of geometry on the resonance frequency of Helmholtz resonators. *J. Sound Vib.* 2(2), 105–119.
- Alster, M. (1972). Improved calculation of resonant frequencies of Helmholtz resonators. *J. Sound Vib.* 24(1), 63–85.
- Ingard, U. & Ising, H. (1967). Acoustic nonlinearity of an orifice. *JASA* 42, 6–17.
- Coltman, J. W. (1968). Sounding mechanism of the flute and organ pipe. *JASA* 44(4), 983–992.
- Fletcher, N. H. & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer (ch. 16, air-reed instruments; vessel flutes).
- Small, R. H. (1973). Vented-box loudspeaker systems, Part 1. *JAES* 21(5), 363–372.
- Rossing, T. D. (2000). *Science of Percussion Instruments*. World Scientific (udu, djembe, ghatam).
- Wikipedia (live 2026-11-25, cached `_web150_hcris/*.json`): "Helmholtz resonance", "Ocarina", "Udu", "Bass reflex", "End correction".
