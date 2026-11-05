# SP-134 — Conical Single-Reed (Saxophone) Bore Synthesis (CSRB)

**Layer:** absolute (sound production) · **Category:** Synthesis Engines · **Candidate module:** `sound/synthesis/conical_reed.py`

One line: model a saxophone as a truncated cone closed by a nonlinear single reed and shortened by a lattice of open toneholes — pitch from geometry, dynamics from blowing pressure, articulation from tonguing the reed.

---

## 1. Why this method exists

Every "sax" patch built from a subtractive or FM oscillator fails in three specific ways: it has no register break (the octave key does nothing physical), no low-register darkening (there is no tonehole-lattice cutoff), and no breath/growl coupling (the reed is not a valve being pushed around by the bore). CSRB is the smallest model that produces all three from first principles, and it is the *only* difference that matters between the sax and the clarinet (SP-023): the bore taper.

The clarinet is a **stopped cylinder**: closed at the reed, open at the bell → modes at odd multiples of $c/4L$, overblowing at the twelfth. The sax is a **truncated cone**: the apex behaves as a pressure node, so the air column is effectively open at *both* ends → modes at all multiples of $c/2L$, overblowing at the octave. Same length, an octave apart in pitch, and completely different spectra. That is the whole method in one sentence, and it is what the numbers below measure.

---

## 2. Bore acoustics

### 2.1 Webster horn equation

For a duct whose cross-section $S(x)$ varies slowly compared with the wavelength:

$$\frac{1}{S(x)}\frac{\partial}{\partial x}\left(S(x)\frac{\partial p}{\partial x}\right)=\frac{1}{c^2}\frac{\partial^2 p}{\partial t^2}$$

### 2.2 Conical solution

With $S(x)=S_0 (x/x_0)^2$ the substitution $p(x,t)=q(x,t)/x$ makes the equation exactly planar:

$$\frac{\partial^2 q}{\partial x^2}=\frac{1}{c^2}\frac{\partial^2 q}{\partial t^2}\quad\Longrightarrow\quad p(x,t)=\frac{A}{x}e^{j(\omega t-kx)}+\frac{B}{x}e^{j(\omega t+kx)}$$

Particle velocity from the momentum equation $\rho\,\partial u/\partial t=-\partial p/\partial x$:

$$u(x,t)=-\frac{1}{j\omega\rho}\frac{\partial p}{\partial x}=\frac{1}{j\omega\rho}\left[\frac{A}{x^2}e^{j(\omega t-kx)}+\frac{B}{x^2}e^{j(\omega t+kx)}+\frac{jkA}{x}e^{j(\omega t-kx)}-\frac{jkB}{x}e^{j(\omega t+kx)}\right]$$

### 2.3 Input impedance of the truncated cone

Bell at $x=L$ is a pressure release ($p=0$) → $B=-A e^{-2jkL}$. At the mouthpiece $x=x_0$:

$$Z_{\text{in}}(\omega)=\frac{p(x_0)}{u(x_0)}=j\rho c\,\frac{k x_0\sin\!\big(k(L-x_0)\big)}{k x_0\cos\!\big(k(L-x_0)\big)+\sin\!\big(k(L-x_0)\big)}$$

Write $L_t=L-x_0$ (the physical, truncated length). Then

$$Z_{\text{in}}=j\rho c\,\frac{k x_0\sin kL_t}{k x_0\cos kL_t+\sin kL_t}$$

* **Poles** (resonances, $Z\to\infty$): $\tan(kL_t)=-k x_0$.
* **Zeros** ($Z=0$): $\sin(kL_t)=0 \Rightarrow f=n c/2L_t$.
* Poles and zeros alternate, so the impedance is a ladder with one pole per $c/2L_t$ — the source of the *complete* harmonic series.

### 2.4 The series is stretched

Solving $\tan u=-a u$ with $u=kL_t$, $a=x_0/L_t$: first order gives $k(L_t+x_0)=n\pi$, i.e. $f_n=n c/2L$ with $L$ the **full** cone length (apex included). The audible deviation is the next order term:

$$\frac{f_n}{n f_1}=1+\frac{\pi^2 n^2 a^3}{3(1+a)^3}+\cdots$$

so the stretch grows as $n^2$ and as the cube of the taper parameter. Alto-sized geometry ($x_0=0.102$ m, $L_t=1.370$ m, $L=1.472$ m, $a=0.0745$, $f_1=116.65$ Hz) measured with the exact equation:

| $n$ | pole (Hz) | $f_n/(nf_1)$ | cents vs $nf_1$ |
|---|---|---|---|
| 1 | 116.65 | 1.000 | 0.0 |
| 2 | 233.99 | 1.003 | +5.1 |
| 3 | 352.29 | 1.007 | +11.5 |
| 4 | 471.99 | 1.012 | +19.8 |
| 5 | 592.53 | 1.016 | +27.3 |
| 8 | 959.20 | 1.028 | +47.5 |
| 12 | 1453.71 | 1.039 | +65.4 |
| 32 | 3948.58 | 1.057 | +97.2 |

Musical consequence: sax high partials are progressively sharp — the physical reason altissimo fingerings need lipping and why a saxophone's spectrum is not a stretched-harmonic-free "organ" spectrum.

### 2.5 Control experiment: the stopped cylinder

$$Z_{\text{cyl}}=j\rho c\tan(kL_t),\qquad f_n=(2n-1)\frac{c}{4L_t}$$

Same $L_t=1.370$ m: 62.53, 187.75, 313.00, 438.18 Hz — one octave lower, odd harmonics only.

---

## 3. Reed valve

### 3.1 Equation of motion

$$m_r\ddot x+r_r\dot x+k_r x=-S_r\,\Delta p,\qquad \Delta p=p_{\text{mouth}}-p_{\text{bore}}$$

$x$ positive opens the reed. Dalmont, Gilbert & Ollivier (2003) show the reed is **stiffness-dominated** at musical dynamics (mass/inertia small), so the quasi-static opening is

$$H=H_0-\frac{S_r}{k_r}\Delta p .$$

### 3.2 Bernoulli orifice flow

$$u=\alpha\,w\,H\,\operatorname{sgn}(\Delta p)\sqrt{\frac{2|\Delta p|}{\rho}}\qquad (H>0),\qquad u=0\ (H\le0)$$

$\alpha$ lumps the vena-contracta ratio and the jet/opening proportionality, both measured constant over a wide opening range.

### 3.3 The negative-resistance band (the gain mechanism)

$$u(\Delta p)=\alpha w\left(H_0-\frac{S_r}{k_r}\Delta p\right)\sqrt{\frac{2\Delta p}{\rho}}$$

$$\frac{du}{d\Delta p}=0\;\Longrightarrow\;\Delta p^*=\frac{k_rH_0}{3S_r},\qquad \Delta p_{\text{close}}=\frac{k_rH_0}{S_r}$$

Between $\Delta p^*$ and $\Delta p_{\text{close}}$ the flow *falls* as pressure rises: a negative differential resistance that pumps energy into any bore oscillation at the right phase. This is why the instrument has a playing range and why "blow harder" changes timbre before it changes loudness.

Prototype values ($k_r=1500$ N/m, $S_r=1$ cm², $H_0=0.8$ mm): $\Delta p_{\text{close}}=12\,000$ Pa, $\Delta p^*=4000$ Pa (verified numerically to the pascal), $u_{\max}=0.366$ L/s — consistent with measured sax flows of 0.3–0.6 L/s.

### 3.4 Reed slap

At $H\to0$ the reed hits the lay. Model as a unilateral stop with restitution $e\approx0.3$ (or a residual $H_{\min}\approx0.02H_0$). The bounce is a broadband impulse — the physical origin of slap-tongue, reed buzz and the brightness increase at high blowing pressure.

---

## 4. Tonehole lattice, register hole, bell

* **Toneholes.** An open hole is a shunt admittance. The periodic lattice is a low-pass structure: below cutoff, the wave propagates and the first open hole defines $L_{\text{eff}}$ (the fingering); above cutoff it is evanescent and the bell radiates. Measured on real alto saxes: cutoff near the 3rd mode for low first-register notes, the 4th mode for high ones, and the 2nd mode for every note of the second register (Ukshini & Dirckx 2025); cutoff falls markedly from high to low notes of register 1 (Petersen et al. 2020).
* **Register hole.** A small leak near a pressure maximum of mode 2 detunes and damps mode 1, forcing the bore to lock onto mode 2 → the octave key. Because the cone's mode 2 is at $2f_1$, the sax overblows at the octave (the clarinet, whose mode 2 is suppressed, overblows at the twelfth).
* **Bell.** The flare matches bore impedance to free air; radiation resistance rises with frequency, giving a natural high-frequency lift, and adds the end correction $\delta\approx0.6\,r_{\text{bell}}$ (≈3.9 cm on an alto = ≈45 cents at $f_1$ if omitted).

---

## 5. Implementation

### 5.1 Modal bank (used in the verification)

```python
import numpy as np

c, rho, fs = 343.0, 1.2, 48000.0

def cone_poles(x0, Lt, fmax=4000.0, df=0.25):
    f = np.arange(1.0, fmax, df)
    k = 2*np.pi*f/c
    Z = 1j*rho*c*k*x0*np.sin(k*Lt) / (k*x0*np.cos(k*Lt) + np.sin(k*Lt))
    a = np.abs(Z)
    idx = np.where((a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]))[0] + 1
    idx = [i for i in idx if a[i] > 5*np.median(a)]
    out = []
    for i in idx:                                  # parabolic peak refinement
        y0, y1, y2 = a[i-1], a[i], a[i+1]
        d = 0.5*(y0-y2)/(y0-2*y1+y2)
        out.append(f[i] + d*df)
    return np.array(out)

def render(p_mouth, fm, Q0=14.0, dur=0.8):
    n = int(dur*fs)
    Q  = Q0*(fm/fm[0])**0.6
    r  = np.exp(-np.pi*fm/(Q*fs))
    a1 = 2*r*np.cos(2*np.pi*fm/fs); a2 = -r*r
    g  = 1.0/(1.0 + (fm/fm[0])**1.2)               # radiation/viscothermal rolloff
    y1 = np.zeros_like(fm); y2 = np.zeros_like(fm)
    m_r, fr, Qr = 1e-5, 1600.0, 4.0
    rr = 2*np.pi*fr*m_r/Qr
    k_r, S_r, H0 = 1500.0, 1e-4, 0.8e-3
    alpha, w = 0.7, 0.012
    x = xd = 0.0; pb = 0.0
    out = np.empty(n)
    for i in range(n):
        dp = p_mouth - pb
        for _ in range(4):                          # substep the stiff reed ODE
            h = 1.0/(4*fs)
            xdd = (-S_r*dp - rr*xd - k_r*x)/m_r
            xd += h*xdd; x += h*xd
            if x < -0.97*H0:                        # lay stop, restitution
                x = -0.97*H0; xd = -0.3*xd
        H  = H0 + x
        uv = 0.0 if H <= 1e-9 else alpha*w*H*np.sqrt(2*abs(dp)/rho)*np.sign(dp)
        yn = a1*y1 + a2*y2 + g*uv
        y2, y1 = y1, yn
        pb = 420.0*yn.sum()                         # bore->reed feedback gain
        out[i] = pb
    return out
```

### 5.2 Kelly–Lochbaum cone lattice (alternative, passivity-guaranteed)

$$\Delta x=\frac{c}{f_s},\quad A_i=A_0(x_0+i\Delta x)^2,\quad k_i=\frac{A_i-A_{i+1}}{A_i+A_{i+1}}\ (\approx-\Delta x/x)$$

$$p^+_{i+1}=(1+k_i)p^+_i+k_i\,p^-_{i+1},\qquad p^-_i=(1-k_i)p^-_{i+1}-k_i\,p^+_i$$

The taper alone produces the even harmonics; no extra filter. An alto (1.37 m) is ~190 sections at 48 kHz.

### 5.3 FDTD Webster (alternative, arbitrary profile)

$$p^{m+1}_i=2p^m_i-\big(1-\sigma\Delta t\big)p^{m-1}_i+\lambda^2\Big[(p^m_{i+1}-2p^m_i+p^m_{i-1})+\tfrac{S'_i}{2S_i}(p^m_{i+1}-p^m_{i-1})\Big]$$

with $\lambda=c\Delta t/\Delta x\le0.9$ and $\sigma$ a broadband loss. Handles polycylindrical necks and the bell flare directly.

### 5.4 Cost

Modal: $O(N_{\text{mode}})$ per sample (≈30 modes → 30 multiply-adds), no CFL constraint. Lattice: $O(N_{\text{sections}})$ per sample, passive. FDTD: $O(N_{\text{grid}})$ with CFL. All are real-time at 48 kHz for a handful of voices in NumPy with per-sample loops moved to Numba/C.

---

## 6. Verification (this document)

Script `projects/Research/CompositionMethods/_web136/sp134_verify.py`, log `_web136/sp134_out/verify_output.txt`, audio `sax_cone.wav` / `sax_cyl.wav` (48 kHz, 16-bit, 0.8 s).

| Check | Result |
|---|---|
| Cone poles | 116.65, 233.99, 352.29, 471.99, 592.53 Hz (all harmonics) |
| Stretch | +5.1 ¢ (n=2) → +65.4 ¢ (n=12) → +97.2 ¢ (n=32) |
| Cylinder poles, same length | 62.53, 187.75, 313.00 Hz (1:3:5) |
| Reed flow peak | 4000 Pa = $kH_0/3S$ exactly; closing 12 000 Pa |
| Reed $u_{\max}$ | 0.366 L/s |
| Cone render | f0 = 116.25 Hz, harmonics 0/−23.5/−38.0/−50.9/−65.2 dB |
| Cylinder render | f0 = 63.75 Hz, h2 −64.5 dB, h4 −96.5 dB |
| Even-harmonic contrast | +41 dB (h2) and +46 dB (h4) in favour of the cone |
| Zero drift | 0.8 s = 38 400 samples exactly; WAV 76 844 B |

---

## 7. UnitMatrix workflow

* **Rows = voices = bores/players.** One reed + one air column per row; monophonic by physics.
* **Columns = sections = phrase regions.** Per-column register, dynamics (→ $p_{\text{mouth}}$), articulation, vibrato, growl.
* **Cells = MusicUnit.** Events → (fingering → $L_{\text{eff}}$, pressure envelope, gate, tongue). Overlapping events in a row are a validation error, not a chord.

```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from structures import MidiInstrument

c = UnitMatrixComposer(bpm=96)
c.create_matrix(num_voices=2, num_sections=3)
c.add_voice("Sax1", program=65, channel=0)      # GM 65 = Alto Sax
c.add_section("A", bars=4); c.add_section("B", bars=4); c.add_section("C", bars=4)
c.fill_voice_section("Sax1", "A", create_note_unit(57, 4*1920))
ok, msg = c.validate()            # must be True
c.to_midi("sax.mid")
# then: produce("sax.mid", method="SP-134", params={...})
```

---

## 8. References

1. Benade, A. H. (1990). *Fundamentals of Musical Acoustics*, 2nd ed. Dover.
2. Chaigne, A., & Kergomard, J. (2016). *Acoustics of Musical Instruments*. Springer.
3. Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed. Springer.
4. Smith, J. O. (2010). *Physical Audio Signal Processing*. CCRMA (online).
5. Dalmont, J.-P., Gilbert, J., & Ollivier, S. (2003). JASA 114(4), 2253–2262. doi:10.1121/1.1603235
6. Dalmont, J.-P., & Nederveen, C. J. (1997). ISMA 1997. doi:10.25144/15149
7. Dalmont, J.-P., Gazengel, B., & Kergomard, J. (2006). JASA 119(5) (ASA abstract). doi:10.1121/1.4786090
8. Muñoz Arancón, A., Gazengel, B., Dalmont, J.-P., & Conan, C. (2016). JASA 139. doi:10.1121/1.4948774
9. Kergomard, J., Guillemain, P., Sanchez, P., & Vergez, C. (2019). Acta Acustica united with Acustica. doi:10.3813/AAA.919320
10. Petersen, E., Colinot, T., Kergomard, J., & Guillemain, P. (2020). Acta Acustica 4. doi:10.1051/aacus/2020012
11. Ukshini, E., & Dirckx, J. J. J. (2025). Acoustics 7(1):15. doi:10.3390/acoustics7010015
12. Scavone, G. P., & Smith, J. O. (1996). JASA 100. doi:10.1121/1.416582
13. Darabundit, C., & Scavone, G. P. (2025). Front. Signal Process. 5:1519450. doi:10.3389/frsip.2025.1519450
