# SP-145 — Campanological Bell Partial Synthesis (CBPS)

**Layer:** absolute (sound production)
**Category:** Synthesis Engines — physical/acoustical modeling
**Candidate code path:** `sound/synthesis/church_bell.py`
**Status:** documented + verified prototype (8/8 checks)

---

## 1. What a bell is, acoustically

A bell is a **shell of revolution** — a body whose mass and stiffness distributions are
(ideally) invariant under rotation about the vertical axis. Its modes of vibration are
therefore classified by

* $m$ — the number of nodal *meridians* (vertical node lines), $m=0,1,2,\dots$
* $n$ — the number of nodal *circles* (horizontal node rings), $n=0,1,2,\dots$

For every $m\ge 1$ the eigenvalue problem is doubly degenerate: two orthogonal solutions
share one natural frequency,

$$\Phi^{c}_{mn}(r,\theta)=\psi_{mn}(r)\cos m\theta,\qquad
\Phi^{s}_{mn}(r,\theta)=\psi_{mn}(r)\sin m\theta .$$

A real casting is never perfectly axisymmetric (unequal wall thickness, the mould seam,
the inscription band, the crown staples). The imperfection removes the degeneracy and
splits each pair by a small $\Delta f_{mn}$, typically 0.1–1 Hz — the **doublet**. Because
the clapper strikes at one azimuth $\theta_s$, the two members are excited with gains
$|\cos m\theta_s|$ and $|\sin m\theta_s|$; both usually sound, and their superposition
beats. That beat is the **warble** of an old bell (Hibbert, *Doublets or warble in bells*).

## 2. The partial series

Campanology names the lowest partials by their musical function, not by mode index.
For a **true-harmonic** bell (Simpson's rule; the English ideal since the Hemonys):

| name | ratio to nominal | cents | interval | audible role |
|---|---|---|---|---|
| hum | 0.25 | −2400 | two octaves below nominal | the long pedal |
| prime | 0.50 | −1200 | octave below | the octave support |
| tierce | 0.60 | −900 | **narrow** minor third above prime | "minor" colour |
| quint | 0.75 | −500 | fifth above prime | the open fifth |
| nominal | 1.00 | 0 | named note | loudest partial |
| superquint | 1.50 | +702 | fifth above nominal | strike ladder 1 |
| octave nominal | 2.00 | +1200 | octave above nominal | strike ladder 2 |
| upper third | 2.50 | +1586 | major third, 2nd octave | strike ladder 3 |
| upper fifth (I-7) | 3.00 | +1902 | fifth, 2nd octave | strike ladder 4 |
| double octave (I-8) | 4.00 | +2400 | two octaves | strike ladder 5 |

Measured deviations for a Taylor bell of the 1980s (nominal 1171.5 Hz; Hibbert,
*Basic principles of bell tuning*):

```
hum        293.1 Hz   -2399.3 cents
prime      585.9 Hz   -1199.3
tierce     692.9 Hz    -908.9      <- 290.4 cents above the prime, not 300
quint      882.0 Hz    -491.4
nominal   1171.5 Hz       0.0
superquint 1761.0 Hz   +705.6
oct-nom   2437.0 Hz   +1268.1      <- tuned sharp; this moves the strike pitch
I5        2619.1 Hz   +1392.9
I-7       3403.4 Hz   +1846.4
I-8       3982.5 Hz   +2118.4
```

Two structural facts matter:

1. **The upper ladder is not independently tunable.** Hibbert's regression over 8,071
   bells (9 centuries, 15 countries, 19 kg–65 t) shows that the intervals of the upper
   partials to the nominal are fixed linear functions of the octave-nominal interval:
   thinning the sound-bow sharpens *all* of them together. Only hum, prime and quint can
   be moved independently by the founder; the tierce follows the sound-bow design.
   A synthesis model therefore has **one** degree of freedom for the whole ladder, not ten.
2. **The tierce is narrow.** 290–291 cents is a *neutral* third, between minor (300) and
   a Pythagorean minor third (294). This is why bells are neither major nor minor and
   blend with both — and why equal-tempered bell samples never sound quite right.

## 3. Virtual pitch: the strike note

The strike ladder

$$f_{S,k}\in f_N\cdot\{1,\;1.5,\;2,\;2.5,\;3,\;4\}$$

consists of integer multiples of $f_P=f_N/2$ — harmonics 2, 3, 4, 5, 6 and 8 of the
prime. A set of spectral components at integer multiples of $f_P$ is heard by the
auditory system as a single pitch at $f_P$ even when no energy exists at $f_P$
(missing-fundamental / virtual pitch; Terhardt; demonstrated for bells by Eggen &
Houtsma and by Hibbert's listening tests). The perceived note of a bell is thus

$$f_{\text{strike}}=\gcd\{f_{S,k}\}=f_N/2,$$

and it need not coincide with any partial. Rayleigh (1890) established the octave
relation empirically; the modern explanation is periodicity detection in the ear.

Consequences for synthesis:

* Never synthesise the perceived pitch as a partial — it must emerge from the ladder.
* The perceptual pitch is **sensitive to the ladder's spacing**: compressing it (thick,
  heavy bells) flattens the strike note; widening it (thin bells) sharpens it. Hibbert
  measured 20–35 cents of apparent detuning in trebles whose nominal was in tune to
  within a cent.
* Above ~1500 Hz nominal, listeners increasingly hear the *prime*; below ~500 Hz, many
  hear a secondary strike from I-7. The nominal is not always the anchor.

## 4. Amplitude, decay, and radiation

Each mode is a damped oscillator,

$$\ddot{x}_n + 2\zeta_n\omega_n\dot{x}_n + \omega_n^2 x_n = F_n(t)/m_n,$$

whose free response is $A_n e^{-t/\tau_n}\sin(2\pi f_n t+\varphi_n)$ with
$\tau_n = 1/(\zeta_n\omega_n) = T_{60,n}/6.9078$.

Radiation damping grows with frequency (a vibrating shell radiates more efficiently as
wavelength shrinks toward the coincidence frequency), so the hum outlives everything:

$$T_{60,n}=T_{60,N}\left(\frac{f_n}{f_N}\right)^{-\alpha},\qquad \alpha\approx0.8 .$$

With $T_{60,N}=8$ s: hum 24.2 s, prime 13.9 s, tierce 12.2 s, quint 10.0 s, nominal 8.0 s,
superquint 5.8 s, octave nominal 4.5 s, double octave 2.6 s. For a large tenor with
$T_{60,N}\approx30$ s the hum rings for well over a minute. This differential decay —
not the ratio set — is what makes a bell sound *struck* rather than *played*.

Radiated amplitudes are not equal: the nominal dominates the low spectrum, the hum and
prime are strong but perceptually weak at low frequencies (equal-loudness), and the
ladder carries most of the "clang". Model $A_n$ as a per-partial table, default

$$A=\{0.50,0.65,0.45,0.40,1.00,0.30,0.25,0.18,0.15,0.10\}$$

for hum…double-octave, then weight by $|\Phi_n(\theta_s)|$ and strike velocity.

## 5. Excitation

The clapper (or hammer) contacts the **sound-bow** for 3–6 ms. Two components:

* **Modal injection.** Mode $n$ receives $A_n\propto|\Phi_n(\theta_s)|$, and because
  $\Phi^{c}\propto\cos m\theta$, $\Phi^{s}\propto\sin m\theta$, the azimuth trades one
  doublet member against the other. In the prototype, moving the strike point from
  $\theta=0$ to $\theta=\pi/8$ shifts the tierce/quint balance by **7.8 dB**.
* **Contact transient.** A short noise burst (exponential, $\tau\approx1.5$ ms) models
  metal-on-metal contact; it excites all modes and gives the attack its edge. Level =
  "strike hardness" (felt hammer vs iron clapper); a soft hammer lowers the burst and
  tilts energy toward the low partials.

Velocity mapping: $v\in(0,1]\mapsto$ overall amplitude $\propto v^{1.2}$ and a mild
brightness tilt (higher modes gain slightly faster with force, as the contact stiffens).

## 6. NumPy implementation sketch

```python
import numpy as np

FS = 44100

IDEAL = [(0.25, "hum", 0.50, 2), (0.50, "prime", 0.65, 2),
         (0.60, "tierce", 0.45, 4), (0.75, "quint", 0.40, 3),
         (1.00, "nominal", 1.00, 4), (1.50, "superquint", 0.30, 5),
         (2.00, "oct-nom", 0.25, 6), (2.50, "up3", 0.18, 6),
         (3.00, "up5", 0.15, 7), (4.00, "dbl-oct", 0.10, 8)]

def t60(ratio, t60_n=8.0, alpha=0.8):
    return t60_n * ratio ** (-alpha)

def bell(f_nom, dur=12.0, partials=IDEAL, theta=0.37, v=0.8,
         doublet_cents=1.2, hardness=0.06, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * FS)
    t = np.arange(n) / FS
    y = np.zeros(n)
    for ratio, name, amp, m in partials:
        f = ratio * f_nom
        if f > FS / 2 - 500:
            continue
        env = 10 ** (-3 * t / t60(ratio)) * np.minimum(t / 0.004, 1.0)
        gc, gs = abs(np.cos(m * theta)), abs(np.sin(m * theta))
        d = 2 ** (doublet_cents / 1200.0)
        for fi, g in ((f / np.sqrt(d), gc), (f * np.sqrt(d), gs)):
            y += amp * v ** 1.2 * g * env * np.sin(
                2 * np.pi * fi * t + rng.uniform(0, 2 * np.pi))
    nb = int(0.006 * FS)
    burst = rng.normal(0, 1, nb) * np.exp(-np.arange(nb) / (0.0015 * FS))
    y[:nb] += hardness * v * burst
    y /= np.max(np.abs(y))
    return 0.98 * y
```

Streaming variant: replace the additive sum with $K$ two-pole resonators

$$y_n[n]=2\rho_n\cos\omega_n\,y_n[n-1]-\rho_n^2\,y_n[n-2]+\rho_n\sin\omega_n\,x[n-1],
\qquad \rho_n=e^{-1/(\tau_n f_s)},$$

which is the same response with $O(K)$ state and allows per-sample modulation of
$f_n$ (bell bending) or $\tau_n$ (hand damping).

## 7. Parameters and musical mapping

| parameter | physical meaning | musical effect |
|---|---|---|
| `f_nominal` | nominal frequency | the notated pitch (heard one octave lower) |
| `preset` | ideal / Taylor / Mears / custom | true-harmonic vs old-style timbre |
| `T60_N` | nominal decay | bell size: handbell ≈ 1–3 s, tenor 20–60 s |
| `alpha` | radiation law exponent | how fast the clang dies relative to the hum |
| `doublet_cents` | asymmetry split | no warble (modern) → "medieval" wobble |
| `strike_azimuth` | where the clapper hits | doublet balance, sweet/dead spot |
| `hardness` | contact transient level | felt hammer → iron clapper |
| per-partial `A_n` | radiated amplitude | tierce-forward (old) vs bright true-harmonic |

Size scaling: for a fixed profile, $f_N\propto 1/D$ and mass $\propto D^3$, so a bell an
octave lower is roughly twice the diameter and eight times the mass. In the model, scale
$f_N$ down and $T_{60,N}$ up together.

## 8. Verification output

`_web145_cbpm/verify_cbpm.py` (NumPy + SciPy, 12 s render, 44.1 kHz):

```
CBPM verification
  [PASS] 1 peak accuracy: max err 0.006 %
  [PASS] 2 tierce narrow minor 3rd: 290.4 cents (equal-tempered minor 3rd = 300)
  [PASS] 3 doublet beat rate: requested Δf=20.302 Hz, measured 20.333 Hz
  [PASS] 4 strike series -> virtual pitch: strike/prime = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
         -> f_virtual = nominal/2 = 585.8 Hz
  [PASS] 5 radiation decay ordering: T60 hum=24.3s, prime=13.9s, nominal=8.0s, double-oct=2.6s
  [PASS] 6 strike azimuth rebalances modes: tierce/quint ratio shifts +7.8 dB
  [PASS] 7 DC / peak / finite: mean=-1.08e-06, peak=0.980
  [PASS] 8 wav written: 1058444 bytes
8/8 checks passed
```

## 9. References

1. B. Hibbert, *The Sound of Bells* — <https://www.hibberts.co.uk/>; pages: *Basic
   principles of bell tuning*, *The strike note of bells*, *Doublets or warble in
   bells*, *The upper partials of bells*, *The musical sound quality of church bells*
   (fetched 2026-11-19).
2. B. Hibbert, PhD thesis, Open University 2008 — the acoustics of bells and the note
   heard when a bell is rung.
3. Lord Rayleigh, "On the pitch of bells", *Phil. Mag.* 1890.
4. E. Terhardt, "Pitch, consonance, and harmony", *JASA* 55 (1974); E. Terhardt,
   G. Stoll, M. Seewann, "Algorithm for extraction of pitch and pitch salience from
   complex tonal signals", *JASA* 71 (1982).
5. J. M. Houtsma & J. L. Goldstein / Eggen & Houtsma — virtual pitch in bell-like
   inharmonic complexes.
6. T. D. Rossing (ed.), *Acoustics of Bells* (Dowden, Hutchinson & Ross, 1984);
   T. D. Rossing, *Science of Percussion Instruments* (World Scientific, 2000), ch. on
   bells and gongs.
7. R. Perrin, T. Charnley, J. dePont, "Normal modes of an English church bell",
   *J. Sound Vib.* (1983).
8. A. Lehr, "The theory of bell tuning" (partial coupling during tuning).
9. Canon A. B. Simpson, true-harmonic tuning papers, *Pall Mall Magazine* (1890s).
10. Wikipedia, "Bell" and "Strike tone" (partial nomenclature; fetched 2026-11-19).

## 10. Neighbours (what this is *not*)

* **SP-042 MBED** — generic eigenmode bank for bars/plates; mentions bell partial names
  in passing. CBPS supplies the campanological ratio set, doublet warble, azimuthal
  excitation and the virtual-pitch contract.
* **SP-105 CRFBS** — *nonlinear* coupled resonator bank (cymbals, plates). Bells are
  linear; the doublet beat is linear superposition, not energy exchange.
* **SP-039 / SP-116 / SP-144** — additive engines with arbitrary partials / closed-form
  sums / wavetable spectra. CBPS is a *physical* parameterisation: nominal, size,
  casting asymmetry, strike point.
* **SP-136 SLTM** — tabla *membrane* eigenproblem (circular plate + syahi). Different
  topology (flat loaded membrane, not a shell), different physics (tension, not bending).
* **SP-033 / SP-101 / SP-058** — 1-D waveguides (strings, bores, springs). A bell is a
  2-D shell with a dense, non-harmonic modal set; no delay-line loop reproduces it.
