# Sound Method SP-138 — Struck-Tine Electromechanical Piano Synthesis (STEPS)

**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines → Physical Modeling → Struck Tuning-Fork (Electromechanical Piano)
**Candidate code path:** `sound/synthesis/rhodes_ep.py` (`ForkResonator`, `HammerContact`, `MagneticPickup`, `Damper`, `RhodesPreamp`, `StereoVibratoTremolo`, `RhodesEP`)
**Dispatch:** `produce(midi_path, method="SP-138", ...)` via `workflows/musicom_workflow.py`
**Verified prototype:** `_web138/steps_verify.py` → log `steps_verify_output.txt`, audio `sp138_demo.wav` (238 140 stereo frames @ 44.1 kHz, 952 604 B) — **12/12 checks pass**

---

## 1. What it models

The Fender Rhodes electric piano: a piano action strikes a thin cantilevered steel **tine** clamped to a massive **tone bar** — an *asymmetric tuning fork* ("one leg vibrates more than the other, but at the same frequency" — FenderRhodes.com service archive). A permanent-magnet pickup coil senses the steel tip's motion; the preamp saturates; the Suitcase tremolo bounces the output anti-phase across two speakers.

Signal chain (per note):

```
hammer (velocity v_h) → tine (cantilever modes f0, r2·f0, r3·f0, inharmonic)
                      → tone bar (heavy leg, f0, low damping = sustain)
                      → coupling clamp (ρ) → in-phase f0 + out-of-phase f0·√(1+ρ(1+1/μ)) → beat Δf
→ magnetic pickup: EMF = −dΦ/dt ≈ velocity sensing + flux nonlinearity → mode intermodulation
→ damper (felt, key release)
→ preamp y = tanh(g·x) + tone stack
→ stereo tremolo g_L/g_R anti-phase LFO
```

## 2. Physics & math (extended)

### 2.1 Tine: cantilever beam

Euler–Bernoulli beam, clamped at the tone-bar end, free at the struck end:

$$\frac{\partial^2 y}{\partial t^2} = -\frac{EI}{\rho A}\frac{\partial^4 y}{\partial x^4}$$

Separation of variables with clamped-free boundary conditions gives the natural frequencies

$$f_n = \frac{(k_n L)^2}{2\pi L^2}\sqrt{\frac{EI}{\rho A}},\qquad k_n L = 1.8751,\ 4.6941,\ 7.8548,\ 10.9955,\ \ldots$$

so the *uniform* cantilever's partial ratios are strongly inharmonic:

$$f_1:f_2:f_3 = 1 : 6.27 : 17.55$$

A real tine carries a tip mass (the tuning spring/weight). A heavy tip mass compresses the ratios toward the tuning-fork limit (near 2 : 3 : 4); the residual stretch is the Rhodes signature. STEPS parameterizes the first three tine modes per key:

$$f = (f_0,\ r_2 f_0,\ r_3 f_0),\qquad r_2 \in [2.0, 2.6],\ r_3 \in [4.0, 5.0]$$

(prototype default $r_2=2.2$, $r_3=4.5$; measured rendered ratios 2.19 / 4.49 — check 6). JASA 2020 (Gabrielli et al.) measured the actual mode distribution across the whole keyboard via scanning laser Doppler vibrometry and showed these inharmonic modes **characterize the attack transient** — calibrate $r_2, r_3, \tau_n$ per key from that distribution.

### 2.2 Asymmetric tuning fork: two coupled resonators

Tine (light leg, $m_t$) and tone bar (heavy leg, $m_b = \mu m_t$), both tuned to $\omega_0 = 2\pi f_0$, coupled by clamp stiffness $k_c = \rho m_t \omega_0^2$:

$$m_t \ddot{y}_t + r_t \dot{y}_t + k_t y_t + k_c (y_t - y_b) = F_h(t)$$
$$m_b \ddot{y}_b + r_b \dot{y}_b + k_b y_b + k_c (y_b - y_t) = 0$$

Normal-mode analysis ($y = A e^{j\omega t}$):

$$(-\omega^2 + \omega_0^2 + \tfrac{k_c}{m_t})(-\omega^2 + \omega_0^2 + \tfrac{k_c}{m_b}) - \tfrac{k_c^2}{m_t m_b} = 0$$

$$\Rightarrow\quad \omega_1^2 = \omega_0^2 \quad(\text{in-phase}),\qquad
\omega_2^2 = \omega_0^2\left[1 + \rho\left(1 + \tfrac{1}{\mu}\right)\right]\quad(\text{out-of-phase})$$

The in-phase mode is the sounding fundamental (both legs move together, coupling spring un-stretched); the out-of-phase mode sits just above it. Their beat

$$\Delta f = f_2 - f_1 = f_0\left(\sqrt{1+\rho(1+\tfrac{1}{\mu})}-1\right) \approx \tfrac{1}{2} f_0\,\rho\left(1+\tfrac{1}{\mu}\right)$$

is the attack "wobble" (prototype: $f_0=220$ Hz, $\mu=8$, $\rho=0.02$ → theory 2.46 Hz, measured 2.50 Hz, 1.6 %). The heavy leg's low damping stores energy and re-injects it through the clamp — the documented "resonator and adds sustain" role.

### 2.3 Hammer excitation

Strike velocity $v_h \propto$ key velocity; mode $n$ excited with amplitude

$$a_n \propto v_h^{\gamma_n},\qquad \gamma_1 < \gamma_2 < \gamma_3 \quad (\text{prototype } 0.55/1.5/2.2)$$

Hard playing brightens (measured mode2/mode1 band ratio 0.3 dB → 8.3 dB, Δ = 7.9 dB). The high inharmonic modes make the attack percussive and electric.

### 2.4 Magnetic pickup: velocity sensing + nonlinear flux

Flux vs tine-tip gap $x$: $\Phi(x) = \Phi_0/(1 + x/d)$. Faraday:

$$\mathrm{EMF} = -\frac{d\Phi}{dt} = \frac{\Phi_0}{d}\,\dot{x}\,\frac{1}{(1+x/d)^2}
\approx \frac{\Phi_0}{d}\,\dot{x}\left[1 - \tfrac{2x}{d} + 3\left(\tfrac{x}{d}\right)^2 - \cdots\right]$$

- Small motion ⇒ EMF ∝ ẋ: the pickup is a **differentiator** (velocity sensing, measured $r=1.0000$ vs numeric derivative) — this gives the ~6 dB/oct brightness tilt, the electric bite.
- Nonlinear terms $x^k \dot{x}$ create **intermodulation**: for modes at $f_a, f_b$ the output contains $|f_b - f_a|$ and $f_b + f_a$ (and $2f$ products). Prototype two-tone (200 + 440 Hz) measurement: 240 Hz at rel. 0.277, 640 Hz at rel. 0.746. This is JASA 2020's "intermodulation of the modes due to the magnetic pickup" and the physical source of the hard-hit **bark**.

### 2.5 Damper

Felt pad engages at key release; pickup output collapses with a ~50 ms contact time constant (10 ms raised-cosine transition in the prototype). Measured free/damped RMS ratio in the post-release window: **345 (50.8 dB)**. Sustain pedal ⇒ free decay (tone-bar τ ≈ 14 s).

### 2.6 Preamp

$y = \tanh(g\,x)$ — odd-only harmonics (measured $h_3 = -26.7$ dB at drive 0.8, $h_2 = -326.8$ dB). Tone stack = bass/treble shelves.

### 2.7 Stereo tremolo (amplitude, not pitch)

$$g_L(t) = 1 - D\left(\tfrac12 + \tfrac12 \sin 2\pi f_L t\right),\qquad
g_R(t) = 1 - D\left(\tfrac12 + \tfrac12 \sin(2\pi f_L t + \pi)\right)$$

Measured L/R envelope correlation **r = −0.997**. $f_L$ ≈ 0–10 Hz, tempo-syncable.

### 2.8 Complexity / determinism

$O(M)$ per sample per note, $M \approx 5$–6 modes (3 tine + tone bar + coupled upper + optional beat); vectorizable across rows. Sample-count exact; per-note phases/detune/velocity-noise seeded per voice (`seed*101 + row`): same seed ⇒ bit-identical, different seed ⇒ different (check 11).

## 3. Python/NumPy implementation sketch

```python
import numpy as np

class ForkResonator:
    """Two-mass coupled tine/tonebar modal core (per note)."""
    def __init__(self, f0, mu=8.0, rho=0.02, zeta_t=0.004, zeta_b=0.002, fs=44100):
        self.fs = fs
        w0 = 2*np.pi*f0
        self.mt, self.mb = 1.0, mu
        self.kt, self.kb = self.mt*w0**2, self.mb*w0**2
        self.kc = rho*self.mt*w0**2
        self.rt, self.rb = 2*zeta_t*w0*self.mt, 2*zeta_b*w0*self.mb
        self.f0 = f0
        self.f_up = f0*np.sqrt(1 + rho*(1 + 1/mu))   # out-of-phase mode
        self.beat = self.f_up - f0                   # attack wobble

    def ring(self, dur, strike=1.0):
        """Impulse-strike the tine; returns (y_t, y_b). Semi-implicit Euler."""
        dt = 1/self.fs; n = int(dur*self.fs)
        yt = np.zeros(n); yb = np.zeros(n)
        vt = np.zeros(n); vb = np.zeros(n); vt[0] = strike
        for i in range(n-1):
            at = (-self.kt*yt[i] - self.rt*vt[i] - self.kc*(yt[i]-yb[i]))/self.mt
            ab = (-self.kb*yb[i] - self.rb*vb[i] - self.kc*(yb[i]-yt[i]))/self.mb
            vt[i+1] = vt[i] + at*dt; vb[i+1] = vb[i] + ab*dt
            yt[i+1] = yt[i] + vt[i+1]*dt; yb[i+1] = yb[i] + vb[i+1]*dt
        return yt, yb

def render_note(f0, vel, dur, fs=44100, r2=2.2, r3=4.5, gamma=(0.55, 1.5, 2.2),
                tau=(2.2, 0.35, 0.12), damp_tau=0.05, drive=0.8, pickup_d=1.2,
                trem=None, seed=0, release_at=None):
    """Modal note: tine modes + tonebar + coupled upper mode -> nonlinear pickup
    -> tanh preamp -> damper -> stereo tremolo. Returns (n, 2) float."""
    rng = np.random.default_rng(seed)
    n = int(dur*fs); tt = np.arange(n)/fs
    fsig = np.array([f0, r2*f0, r3*f0])
    amp = np.array([1.0, 0.45, 0.20]) * vel**np.array(gamma)
    amp /= amp.max() + 1e-9
    ph = rng.uniform(0, 2*np.pi, 3)
    x = np.zeros(n)
    for a, f, t, p in zip(amp, fsig, tau, ph):
        x += a*np.exp(-tt/t)*np.sin(2*np.pi*f*tt + p)
    x += 0.35*vel**0.55*np.exp(-tt/14.0)*np.sin(2*np.pi*f0*tt + ph[0] + 0.4)   # tonebar
    f_up = f0*np.sqrt(1 + 0.02*(1 + 1/8.0))
    x += 0.06*vel**0.8*np.exp(-tt/0.8)*np.sin(2*np.pi*f_up*tt + ph[1])          # coupled upper
    Phi = 1.0/(1.0 + x/pickup_d)
    x = -np.diff(Phi, prepend=Phi[0])*fs                                       # pickup EMF
    if drive > 0:
        x = np.tanh(drive*x)                                                   # preamp
    if release_at is not None:                                                 # damper
        rel = int(release_at*dur*fs); env = np.ones(n)
        env[rel:] = np.exp(-(tt[rel:]-tt[rel])/damp_tau)
        tr = int(0.01*fs); env[rel:rel+tr] *= 0.5 - 0.5*np.cos(np.pi*np.arange(tr)/tr)
        x *= env
    x *= 0.8/(np.abs(x).max() + 1e-9)
    if trem:
        rate, depth = trem
        gL = 1 - depth*(0.5 + 0.5*np.sin(2*np.pi*rate*tt))
        gR = 1 - depth*(0.5 + 0.5*np.sin(2*np.pi*rate*tt + np.pi))
        return np.stack([x*gL, x*gR], axis=1)
    return np.stack([x, x], axis=1)
```

## 4. Verified numbers (prototype `_web138/steps_verify.py`, 12/12)

| # | Check | Measured |
|---|---|---|
| 1 | fork in-phase mode = f0 | 220.00 Hz present |
| 2 | out-of-phase mode = theory | 222.50 vs 222.46 Hz (0.04 Hz) |
| 3 | fork beat (energy slosh) | 2.50 vs 2.46 Hz (1.6 %) |
| 4 | pickup = velocity sensing | r = 1.0000 |
| 5 | pickup mode intermodulation | 240 Hz @ 0.277, 640 Hz @ 0.746 |
| 6 | inharmonic stretch (attack) | ratios 2.19 / 4.49 (r2∈(2.0,2.6), ≠2.0) |
| 7 | velocity → brightness | 0.3 → 8.3 dB (Δ 7.9 dB) |
| 8 | damper release | free/damped RMS 345 (50.8 dB) |
| 9 | tanh preamp odd-only | h3 −26.7 dB, h2 −326.8 dB |
| 10 | stereo tremolo anti-phase | r = −0.997 |
| 11 | zero-drift + determinism | exact length; seed-identical; seed-different |
| 12 | demo WAV | 238 140 frames, 952 604 B |

## 5. UnitMatrix integration (summary)

- **Rows = voices = fork banks** (`fork {mu, rho, r2, r3, detune}`, `hammer {gamma}`, `pickup {gap, nonlinearity}`, `amp {drive, tone}`, `tremolo {rate, depth}`).
- **Columns = sections = performance states** (`sustain`, `tremolo_rate/depth`, `amp_drive`, `eq`); sample-count preserving ⇒ zero-drift safe seams.
- **Cells = MusicUnit**: `note_on(pitch, velocity)` at start_tick, `damper(release_at=end_tick)` at end_tick; fixed tail margin.
- **Dispatch:** `produce(midi_path, method="SP-138", params={...})`.

## 6. Pitfalls (short form)

1. Not a generic modal bank — fork coupling + velocity pickup are the identity.
2. Pickup senses velocity, not displacement (differentiator mandatory).
3. Inharmonic modes belong to the attack (JASA 2020); keep the sustain near-harmonic.
4. Beat is a parameter: ρ≈0.01–0.03, μ≈6–10; too much ρ ⇒ honk, too little ⇒ no sustain.
5. Aliasing: drop modes with f_n > f_s/2 per key or oversample the nonlinear pickup.
6. Velocity mapping is a per-mode power law (γ₁<γ₂<γ₃) — linear scaling is unplayable.
7. Tremolo is amplitude, not pitch (unlike SP-132 Leslie).
8. Pickup nonlinearity ≠ preamp saturation — two separate knobs (buzz vs glow).
9. Neighbours: SP-074 acoustic grand; SP-003/042 modal banks; SP-010/017/094 FM EPs; SP-095 tonewheel; SP-131 two-mass vocal folds. Repo `keys_engine.py` "tine" = lightweight placeholder; STEPS supersedes.

## 7. References

1. Gabrielli, L., Cantarini, M., Castellini, P., & Squartini, S. (2020). "The Rhodes electric piano: Analysis and simulation of the inharmonic overtones." *J. Acoust. Soc. Am.* 148(5), 3052–3064. DOI 10.1121/10.0002002. PMID 33261386.
2. Wikipedia: "Rhodes piano"; "Electric piano" (construction: tine + tone bar tuning-fork assembly, pickup, Suitcase tremolo).
3. FenderRhodes.com, "Steve's Corner — Upper Notes with Low Sustain" (archived 2010-10-28, Wayback Machine) — asymmetric tuning fork, same-frequency tuning, spring fine-tune.
4. Bank, B., & Chabassier, J. (2018). "Model-Based Digital Pianos: From Physics to Sound Synthesis." *IEEE Signal Processing Magazine* 36(1), 103–114.
5. Novák, A., Guadagnin, L., Lihoreau, B., Lotton, P., Brasseur, E., & Simon, L. (2017). "Measurements and Modeling of the Nonlinear Behavior of a Guitar Pickup at Low Frequencies." *Applied Sciences* 7(1), 50. DOI 10.3390/app7010050 (open access).
6. Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed. Springer — bar vibration (clamped-free kL = 1.8751/4.6941/7.8548; f-ratios 1:6.27:17.55), tip-mass effects.
