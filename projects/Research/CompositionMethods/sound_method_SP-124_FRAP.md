# Sound Production Method SP-124 — Free-Reed Aerophone Physical Modeling (FRAP)

**Layer:** absolute (sound production) — **Synthesis Engines**
**Candidate code path:** `sound/synthesis/free_reed.py`
**Summary-table row:** `| **SP-124** | Free-Reed Aerophone Physical Modeling (FRAP) | **Synthesis Engines** | Oscillator Reed / Accordion–Harmonica–Harmonium Timbre | ... |`
**Instrument families covered:** accordion, bandoneon, concertina, harmonica (diatonic/chromatic), reed organ & harmonium, shruti box, sheng, khaen, melodica.

---

## 1. Why this is a distinct method (and not SP-023 / SP-065 / SP-066)

| | exciter | what sets pitch | bore/cavity role | spectrum | attack |
|---|---|---|---|---|---|
| **SP-065 LIPS** (brass) | lip valve, mass-spring + Bernoulli | lip resonance locks to a bore mode; pressure jumps registers | primary (mode selection) | brass formants, brassy | brassy "blat", register jumps |
| **SP-066 FLUE** (flute/organ) | air jet flipping across a labium | bore half-wave modes | primary | odd/even depending on open-open | chiff, breath noise |
| **SP-023 clarinet** | single beating reed on a closed bore | bore (reed is compliant, pulled to bore) | primary | odd harmonics only | reed slap + bore onset |
| **SP-124 FRAP** (free reed) | *tongue chopping its own slot flow* | **the reed itself** (bore pulls a few cents) | secondary (formant, colour only) | full harmonic series, buzzy, edge-rich | 20–80 cent glide + run-down |

The free reed is the only aerophone where the vibrating element and the pitch-determining element are the same object and the resonator is a *filter*, not a *tuner*. That single fact invalidates every delay-line tuning approach: a Karplus-Strong or waveguide model tuned by delay length will always sound like a plucked string or a pipe, never like an accordion.

---

## 2. Reed mechanics (Euler–Bernoulli cantilever)

PDE for the tongue (length $L$, width $w$, thickness $h$, $A=wh$, $I=wh^3/12$, density $\rho_r$, modulus $E$):

$$EI\frac{\partial^4 y}{\partial x^4}+\rho_r A\frac{\partial^2 y}{\partial t^2}=f(x,t)$$

Clamped at $x=0$, free at $x=L$. Separation $y(x,t)=\sum_n\phi_n(x)q_n(t)$ gives

$$\phi_n(x)=A_n\Big[\cosh\beta_nx-\cos\beta_nx-\sigma_n(\sinh\beta_nx-\sin\beta_nx)\Big],\qquad \sigma_n=\frac{\cosh\beta_nL+\cos\beta_nL}{\sinh\beta_nL+\sin\beta_nL}$$

with the eigenvalue equation $\cos\beta_nL\cosh\beta_nL=-1$:

$$\beta_1L=1.87510,\quad \beta_2L=4.69409,\quad \beta_3L=7.85476,\qquad \omega_n=\beta_n^2\sqrt{\frac{EI}{\rho_r A L^4}}$$

so $f_2/f_1=(4.69409/1.87510)^2=6.27$ and $f_3/f_1=17.55$ (not $11.2$ — that figure belongs to the *clamped-clamped* family; use 6.27/17.55 here). Cottingham (2013) shows modes 2–3 are what make the high-pressure "rattle".

Fundamental in engineering form:

$$f_1=\frac{1.87510^2}{2\pi}\sqrt{\frac{EI}{\rho_rAL^4}}=0.55959\sqrt{\frac{EI}{\rho_rAL^4}}=0.16154\,\frac{h}{L^2}\sqrt{\frac{E}{\rho_r}}$$

**Tuning arithmetic** (why reed making is delicate):
- $\partial f/f=\partial h/h$ → at $h=250\,\mu$m, **1 µm of thickness = 0.4 % = ~7 cents**.
- $f\propto L^{-2}$ → 1 % length error = 34 cents.
- tip mass loading: $\Delta f/f=-\tfrac12\Delta m/m$ → solder is a coarse, stable-flattening tool.
- steel $\sqrt{E/\rho_r}\approx5.1$ km/s — the reason reeds are spring steel or brass and the reason $f$ is stable with temperature (±0.02 %/K).

Reduced-order oscillator (static-deflection trial function, tip displacement $y$):

$$M_r\ddot y+R_r\dot y+K_ry=F_a,\qquad K_r=\frac{3EI}{L^3},\quad M_r=\frac{33}{140}\rho_rAL\ (\approx0.236\,m),\quad R_r=2\zeta_r\omega_1M_r$$

$\zeta_r=0.002$–$0.02$ ($Q=25$–$500$). Exact mode-shape generalized mass is $\approx0.25m$; the static shape is within 1.5 % on $f_1$ and keeps $K_r$ equal to the measurable tip stiffness.

---

## 3. Aperture and orifice flow

The tongue sits over a slot wider than itself by the clearance; at rest it is displaced downstream by the **set** $y_0$ (0.02–0.06 mm typical). Gap and flow:

$$g(y)=\max(y+y_0,0),\qquad U=C_d\,w\,g(y)\,\mathrm{sgn}(\Delta p)\sqrt{\frac{2\lvert\Delta p\rvert}{\rho_a}}$$

$C_d\approx0.55$–$0.75$ (vena contracta). Saturation at large $g$ (the jet detaches from the slot walls) is essential:

$$U_\text{sat}=C_d\,w\,g_\text{sat}\sqrt{2\lvert\Delta p\rvert/\rho_a},\qquad g\to g_\text{sat}\tanh(g/g_\text{sat})\ \text{or piecewise blend above } g\approx w/2$$

Practical caveat discovered in the prototype: the model is *very* sensitive to the effective pressure area $A_f$. Calibrate it so the static deflection at nominal playing pressure is of order $y_0$:

$$A_f\approx\frac{K_r\,y_0}{p_{m,\text{nom}}}\quad(\text{accordion: }\sim2\times10^{-9}\ \mathrm{m^2}\ \text{at } p_m=1.5\ \mathrm{kPa})$$

Using the geometric area $wL\approx3\times10^{-5}$ m² instead gives a static deflection of 0.5 mm — the reed is slammed wide open and the model becomes a flow modulator with no oscillation.

---

## 4. Slot inertance, cavity, radiation

Air in the slot is a mass; it cannot follow $y$ instantaneously:

$$L_a(y)=\frac{\rho_a\,l_s}{w\,g(y)}\ \ (l_s=\text{plate thickness}),\qquad L_a\dot U=p_m-p_c-R_aU$$

$$C_c\dot p_c=U-\frac{p_c}{R_\text{rad}},\qquad C_c=\frac{V_c}{\rho_ac^2}$$

$R_a\sim10^5$–$10^7$ Pa·s/m³ (viscous), $R_\text{rad}\sim4\times10^6$–$4\times10^7$ (radiation), $V_c$ = chamber volume (accordion cassotto ~20–200 cm³; harmonica "tract" 20–100 cm³, tunable by the player). Radiated far-field pressure of a compact source:

$$p_\text{rad}(t)\approx\frac{\rho_a}{4\pi r}\frac{dU}{dt}$$

i.e. **the output is the derivative of the chopped flow**, not the tongue's surface motion. Because $U$ is a rectified, square-root-shaped pulse train, $dU/dt$ carries a full harmonic series with sharp edges — the "buzzy" free-reed signature. Apply a one-pole at 6–9 kHz for the slot's radiation roll-off.

---

## 5. Linear stability: where the negative damping comes from

Perturb about $y=0$: $U=U_0+A\,y-B\,(p_c-p_{c0})$ with

$$A=C_dw\sqrt{2(p_m-p_{c0})/\rho_a},\qquad B=\frac{C_dwy_0}{2}\sqrt{\frac{2}{\rho_a(p_m-p_{c0})}}$$

and $p_c$ driven by $U$ through the cavity. The cavity impedance $Z_c=R_\text{rad}/(1+j\omega R_\text{rad}C_c)$ gives a pressure that lags the displacement by $\varphi=\arctan(\omega R_\text{rad}C_c)$. Since the force is $F_a=A_f(p_m-p_c)$, a lagging $p_c$ yields a force component **in phase with velocity**:

$$R_\text{aero}\approx-\frac{A_fA\sin\varphi}{\omega},\qquad \varphi=\arctan(\omega R_\text{rad}C_c)$$

Oscillation when $|R_\text{aero}|>R_r$, i.e.

$$\boxed{\ \frac{A_f\,A\,\sin\varphi}{\omega_r}>2\zeta_r\omega_rM_r\ }$$

Two regimes the criterion exposes:
- $\omega R_\text{rad}C_c\ll1$ (tiny cavity or big radiation loss): $\varphi\to0$, no negative damping, no sound. This is why an *open* reed plate without a chamber is a poor radiator.
- $\omega R_\text{rad}C_c\gg1$: $\varphi\to90°$, maximum negative damping but the pressure becomes a pure reactance → the model also loses its threshold (see pitfall 13). The musical sweet spot is $\varphi\approx30$–$70°$.

Practical onset pressure (energy form, $\oint F_a\,dy>\oint R_r\dot y^2dt$): $p_\text{onset}\sim0.3$–$2$ kPa, scaling as $\propto\zeta_r\omega_rM_r y_0/(A_fw)$ — stiffer/heavier reed or smaller set ⇒ harder to start. Playing pressure is only 0.5–3 kPa, which is why the accordion's dynamic range is narrow (≈15–20 dB) and why velocity must map to a *clipped* pressure band, not linearly.

---

## 6. Validated prototype (2026-10-25, NumPy, 48 kHz)

Parameters: $f_r=194$ Hz steel reed ($h=0.25$ mm, $w=3$ mm, $L$ from the tuning inversion $\approx32$ mm), $y_0=40\,\mu$m, $C_d=0.62$, $A_f$ calibrated, $\zeta_r=0.02$, $V_c=20$ cm³, semi-implicit reed / explicit flow-cavity.

Measured behaviour:

| quantity | result |
|---|---|
| self-oscillation | yes, over a broad parameter region (sweep of $\zeta$, $R_\text{rad}$, $V_c$, $A_f$) |
| settled frequency | 197.1 Hz for $f_r=194$ Hz → **+27 cents** (matches the documented real-reed pitch pull) |
| pitch vs pressure | 197.7 Hz @50 Pa → 197.0 Hz @4 kPa (mild flattening, ±0.5 %) |
| timbre, reed swing $<$ set | THD = **0.004** — a pure sine (wrong sound) |
| timbre, reed swing 4.6× set | THD = **0.53**, H2/H1 = 0.51, H3/H1 = 0.13 — the buzz |
| no slot-contact limiter | swing grows to 20 mm = 500× the set (unphysical) |
| determinism | bit-identical re-runs (array_equal = True) |

**Conclusion of the prototype:** the physics is right and cheap, but two nonlinearities are *load-bearing*: (i) the unilateral slot-contact limiter (amplitude ceiling + buzz), and (ii) an explicit onset gate/hysteresis if a hard $p_\text{onset}$ is wanted, because the pure lumped loop already oscillates at 50 Pa.

---

## 7. Implementation sketch

```python
# sound/synthesis/free_reed.py  (vectorised over voices/reeds; validated core)
import numpy as np

RHO, C_AIR, CD = 1.2, 343.0, 0.62

class FreeReed:
    """One tongue. State: y (tip disp), v, U (slot flow), pc (chamber)."""
    def __init__(self, f0, h=0.25e-3, w=3e-3, y0=40e-6, zeta=0.008,
                 Vc=20e-6, Rrad=4e7, Ra=2e5, l_s=1e-3,
                 E=200e9, rho_r=7850.0, clearance=60e-6, fs=48000.0):
        self.fs = fs
        self.L = np.sqrt(0.16154 * h * np.sqrt(E / rho_r) / f0)   # tuning inversion
        I = w * h**3 / 12.0
        self.K = 3 * E * I / self.L**3
        self.M = (33.0 / 140.0) * rho_r * w * h * self.L
        self.w0 = 2 * np.pi * f0
        self.R = 2 * zeta * self.w0 * self.M
        self.w, self.h, self.y0 = w, h, y0
        self.Cc = Vc / (RHO * C_AIR**2)
        self.Rrad, self.Ra, self.l_s = Rrad, Ra, l_s
        self.clear = clearance
        self.reset()

    def reset(self):
        self.y, self.v, self.U, self.Uprev, self.pc = 0.0, 0.0, 0.0, 0.0, 0.0
        self.sounding = False

    def _force(self, pm):
        """Aero force with calibrated effective area + slot-contact limiter."""
        Af = self.K * self.y0 / 1.5e3                    # calibrated at 1.5 kPa
        F = (pm - self.pc) * Af
        # unilateral contact: reed cannot pass the slot wall beyond clearance
        if abs(self.y) > self.clear:
            F -= (abs(self.y) - self.clear) * 4e4 * np.sign(self.y)
        return F

    def tick(self, pm):
        g = max(self.y + self.y0, 0.0)
        dp = pm - self.pc
        # onset gate + hysteresis (physical threshold behaviour)
        if not self.sounding and pm > 700.0:
            self.sounding = True
        if self.sounding and pm < 350.0:
            self.sounding = False
        if not self.sounding:
            self.y, self.v, self.U = 0.0, 0.0, 0.0
            return 0.0
        U = CD * self.w * g * np.sign(dp) * np.sqrt(2 * abs(dp) / RHO)
        acc = (-self.K * self.y - self.R * self.v + self._force(pm)) / self.M
        self.v += acc / self.fs                       # semi-implicit (symplectic)
        self.y += self.v / self.fs
        self.pc += (U - self.pc / self.Rrad) / self.Cc / self.fs
        out = (U - self.Uprev) * self.fs              # dU/dt -> monopole radiation
        self.Uprev = U
        return out
```

Voice = a **rank** of `FreeReed`s whose $f_0$ are detuned by the section's musette width, sharing one $p_c$ (chamber) and one $p_m$ (bellows); sum the outputs, apply 2–3 biquad formants, then the radiation one-pole. Presets:

| preset | reeds | detune (cents) | set $y_0$ | zeta | chamber | formants |
|---|---|---|---|---|---|---|
| accordion dry | 2 (8′+8′) | 0, ±2 | 40 µm | 0.008 | 100 cm³ | 500/1500/2500 Hz |
| accordion musette | 3 (8′) | −12, 0, +12 | 40 µm | 0.008 | 100 cm³ | 500/1500/2500 |
| bandoneon | 2 | −6, +6 | 50 µm | 0.012 | 60 cm³ | 700/1800/3000 |
| harmonica | 1 | — | 20 µm | 0.006 | tract 40 cm³ (bend-tunable 250–1200 Hz) | 600/1200 |
| harmonium | 2 (8′+16′) | 0 | 50 µm | 0.015 | 200 cm³ | 300/900/1600 |
| sheng / khaen | 1–2 + pipe | 0 | 20 µm | 0.010 | pipe-loaded | pipe modes |

Cost: 4 states/reed, ~6 flops/state/stage; a 3-reed musette × 10 notes = 30 reeds ≈ 3.6 M state-updates/s — real time in NumPy, trivially real time vectorised across voices.

---

## 8. UnitMatrix integration (summary; full text in methods_db.md)

- **Voices = rows** → a row is a *rank* (`Accordion RH (musette)`, `LH bass 16′+8′`, `Harmonium drone`), with a MIDI-note → reed-geometry table and one shared chamber.
- **Sections = columns** → `register` bitmask (L/M/H), `pressure` curve (0.6–2.5 kPa), `detune_cents` (musette width), `bend` curve (harmonica), `valve_noise` gain, optional bellows-shake LFO 4–8 Hz.
- **Cells = MusicUnit** → each `MusicEvent` gives an onset pressure ($p_\text{onset}+v\,(p_\text{max}-p_\text{onset})$) and a valve window; the ODE runs through the note plus its run-down tail; tails cross cell seams rather than being clipped.
- Determinism: seeded valve/air noise, deterministic ODE ⇒ re-renders are bit-identical; ticks untouched ⇒ zero-drift gate unaffected.

Musical upshot: dynamics are *pressure* (narrow, compressive), articulation is *valve timing* (bounded by onset latency and run-down), and the register switch is a real timbral/level/loading change — three levers that map cleanly onto sections, and a physical reason for the accordion's characteristic "breathing" phrasing.

---

## 9. Pitfalls (condensed)

1. Tuning by delay line = category error (reed sets pitch).
2. Direction: one reed per flow direction, else half the bellows cycle is silent.
3. Onset threshold + hysteresis; do not reuse a proportional envelope.
4. No attack glide (20–80 cents, 15–40 ms) = no realism.
5. Clipping $g$ at zero is $C^0$ not $C^1$ → aliasing; smooth it or oversample.
6. Forward Euler on a stiff loop diverges; RK4 or semi-implicit Newmark; clamp $L_a$ from below.
7. Musette is acoustic beating of detuned reeds sharing a chamber, not a chorus effect (SP-059).
8. Registers change level, attack and pitch droop, not just octave content.
9. Chamber formants *are* the instrument (no cavity = kazoo).
10. Bellow/valve/key noise is mandatory for realism.
11. Full beam FDTD costs 100–1000× the 1-DOF model for a marginal gain — start reduced.
12. Limit amplitude physically (orifice saturation + slot contact), never with a limiter.
13. Measured prototype: without a slot-contact limiter the swing reaches 500× the set; without an onset gate the model sounds at 50 Pa; without slot clipping the timbre is a pure sine (THD 0.004 vs 0.53).

---

## References

1. Cottingham, J. P. (2011). "Acoustics of free-reed instruments." *Physics Today* 64(3), 44–48. DOI 10.1063/1.3563819.
2. Caussé, R., Misdariis, N. & Ricot, D. (1999). "Studies of accordion reed vibrations—Applications in sound synthesis." *JASA* 106(4), 2287. DOI 10.1121/1.427818.
3. Cottingham, J. P. (2013). "Modes of reed vibration and transient phenomena in free reed instruments." *POMA* 19, 035061. DOI 10.1121/1.4799611.
4. Biernat, J. & Cottingham, J. P. (2014). "Attack transients in free reed instruments." *POMA* 20, 035002. DOI 10.1121/1.4891627.
5. Busha, M., Cottingham, J. P. & Koopman, P. D. (2002). "Laboratory measurements on free reeds from the reed organ, accordion, and khaen." *JASA* 111(5), 2376. DOI 10.1121/1.4778054.
6. Millot, L. & Baumann, C. (2007). "A Proposal for a Minimal Model of Free Reeds." *Acta Acustica united with Acustica* 93(1), 122–137.
7. Ricot, D. (2003). *Modélisation du fonctionnement de l'anche libre et synthèse sonore.* PhD thesis, Université du Maine / IRCAM.
8. Li, K. & Rogers, C. (2025). "Harmonica reed fluid dynamics modeling and investigation—Initiation and bending." *JASA* 158(4), A384. DOI 10.1121/10.0041239.
9. Shimamura, Y., Tohgo, K. & Araki, H. (2008). "Fatigue of Metal Free Reed due to Self-Excited Oscillation." *Adv. Mater. Res.* 33–37, 267–272. DOI 10.4028/www.scientific.net/AMR.33-37.267.
10. Tarnopolsky, A. Z., Fletcher, N. H. & Lai, J. C. S. (2000). "Oscillating reed valves—an experimental study." *JASA* 108(1), 400–406.
11. Fletcher, N. H. & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer (ch. 12–13).
12. Wheeler, P. A. (2009). "The adoption of the accordion and other bellow-blown free-reed instruments in world cultures." *JASA* 126(4), 2216. DOI 10.1121/1.3248793.
