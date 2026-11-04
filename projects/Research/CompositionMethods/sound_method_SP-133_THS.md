# SP-133 — Theremin Heterodyne Synthesis (THS)

**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Family:** Synthesis Engines — beat-frequency oscillator / proximity-law gesture voice
**Candidate code path:** `sound/synthesis/theremin.py`
**Status:** documented + physics model verified (`projects/Research/outputs/sp133_proto/`)

---

## 1. What the method is

The Theremin (Lev Termen, 1920; US patent 1,661,058, 1928) is the first
electronic musical instrument and the first *contactless* one. Its sound is not
produced by a vibrating object at all: two radio-frequency LC oscillators —
one fixed at $f_R$, one tuned by the capacitance of the player's hand at $f_P$ —
are multiplied in a nonlinear mixer, and the audio tone is their **beat
(difference) frequency**

```
f_T = |f_R − f_P|,          V_out = A1·A2·sin(ω1 t)·sin(ω2 t)
                              = (A1A2/2)[cos((ω1−ω2)t) − cos((ω1+ω2)t)]   --LP-->  (A1A2/2)·cos((ω1−ω2)t)
```

The hand moves two antennas: the vertical **pitch** antenna (distance $x_P$
→ capacitance $C_A(x_P)$ → $f_P$ → $f_T$) and the horizontal **volume**
antenna (distance $x_V$ → gain $g(x_V)$, nulled when touching).

The method is **absolute**: per-voice gesture trajectories (pitch arcs,
volume arcs) in, audio buffers out, sample-count preserving, deterministic per
seed, zero-drift safe. It is a *synthesis engine* — it replaces the per-row
source (SP-001 FluidSynth / SP-095 tonewheel / SP-131 vocal folds …) for rows
that need the continuous-glissando identity.

---

## 2. Extended mechanics

### 2.1 Heterodyne up-conversion (why ~0.4 pF becomes octaves)

The player's hand changes the antenna capacitance by only a few picofarads
(0.4 pF at 10 cm). The trick is that the oscillator runs near 1 MHz, so the
*fractional* RF change is up-converted into the audio beat:

| hand effect | value |
|---|---|
| $\Delta C_A$ at 10 cm (image-antenna /10 model) | 0.38 pF (theory 0.4) |
| $C_A(\infty)$, 0.5 m rod / 10 mm, $k=0.4$ | 6.61 pF (theory ~7) |
| required $\Delta C$ for one *beat octave* at 1 MHz, 10 pF tank | ~0.01 pF (measured ratio 1.93) |

Superposition is NOT enough: adding two sines produces *amplitude* beats with
no power at the difference frequency; only the **product** (mixer) channels
power into the new frequency (Skeldon §II.A; verified numerically).

### 2.2 Oscillator law (Colpitts)

$$f_P=\frac{1}{2\pi\sqrt{L\,C_{\text{eq}}}},\qquad
\frac{1}{C_{\text{eq}}}=\frac{1}{C_1}+\frac{1}{C_2},\qquad
C_2(x)=C_{\text{fix}}+C_A(\infty)+\Delta C_A(x),\qquad
\frac{\Delta f}{f}=-\frac{\Delta C_{\text{eq}}}{2C_{\text{eq}}}$$

### 2.3 Capacitance model (Skeldon 1998, eqs. 6–7)

Antenna self-capacitance (vertical rod $h$, diameter $d$, ground constant $k≈0.4$):

$$C_A(\infty)=\frac{2\pi\varepsilon_0 h}{\ln(2h/d)-k}\approx 6.6\ \text{pF}$$

Hand proximity (image-antenna + /10 reduction for hand-as-strip, valid $x\gg d$):

$$\Delta C_A(x)\approx\frac{\pi\varepsilon_0 h}{10\,\ln(4x/d)}\qquad\Rightarrow\qquad
\Delta C_A(0.10\,\text{m})=0.38\ \text{pF}$$

### 2.4 Raw pitch field (measured prototype: $L$=280 µH, $C_1$=220 pF, $C_{\text{fix}}$=33 pF, $f_R=f_P(1\,\text{m})$=1.638 MHz)

| $x$ (m) | beat $f_T$ (Hz) | note |
|---|---|---|
| 1.00 | 0 | far hand, silence |
| 0.60 | 221 | ~A3 — mid linear region |
| 0.15 | 1856 | upper mid |
| 0.10 | 2514 | |
| 0.06 | 3561 | near antenna — steep |

Mid-range [0.15, 0.8] m: linear-fit slope **−2252 Hz/m**, max residual
433 Hz over the 157–1856 Hz band. Gradient at 0.08 m is **19.1×** the gradient
at 0.6 m — the raw law compresses the high octaves into a few centimetres near
the antenna. Real instruments fix this with the series **linearizing coil**
(near-linear central 2–3 octaves) or a digital PD→VCO mapping (constant octave
intervals to higher frequency; NAUN 2021 validates the mapping in cents).

### 2.5 Octave sensitivity — operating-point dependence

One beat octave requires $\Delta f_P ≈ 500$ Hz at $f_P ≈ 1$ MHz, i.e.
$\Delta C_{\text{eq}}/C_{\text{eq}} ≈ 10^{-3}$. Verified end-to-end:

| tank $C_2$ | +0.01 pF gives | ratio |
|---|---|---|
| 10.26 pF ($f_R$=1 MHz) | 500 → 965 Hz | **1.93** ≈ octave (the Wikipedia figure's regime) |
| 39.9 pF | 500 → 674 Hz | 1.35 |

Always quote sensitivity with its operating point.

### 2.6 Volume law

Second BFO → LP (~1 kHz) → rectify → integrate (τ≈0.1 s) → DC CV
(0 V touching → −4 V far) → VCR/JFET attenuator: **40 dB** suppression
(Skeldon analog), **80 dB** with SSM-2018 VCA (digital). Model:
$g(x_V)=\exp(-x_V/\lambda)$ (clamped); touch = zero volume.

### 2.7 Digital render (the implementation)

$f_R ≈ 1$ MHz cannot be sampled at 48 kHz — the difference is computed
directly and integrated into phase (the identity is exact):

$$y[n]=g[n]\sin(\phi[n]),\qquad \phi[n]=\phi[n-1]+\frac{2\pi f_T[n]}{f_s}$$

Vibrato = hand tremor: $f_T[n]\to f_T[n]\,(1+m\sin(2\pi f_{\text{vib}}t))$,
$m≈0.5$–1.5 %, $f_{\text{vib}}≈5$–7 Hz.

**Aliasing trap (measured):** rendering the RF *product* at 48 kHz aliases the
sum (341 kHz → 5 kHz) and the low-passed output measures **4717 Hz** where
theory says 1000 Hz. Never sample the product; compute the difference.

---

## 3. NumPy implementation sketch

```python
import numpy as np
from utilities.env import python_bin  # one-env contract (unused here, kept for imports)

FS = 48000
EPS0 = 8.854e-12

def c_antenna(h=0.5, d=0.01, k=0.4):
    """Skeldon eq.6: rod self-capacitance, ~6.6 pF."""
    return 2 * np.pi * EPS0 * h / (np.log(2 * h / d) - k)

def dc_hand(x, h=0.5, d=0.01):
    """Skeldon eq.7: hand proximity capacitance, 0.38 pF @ 10 cm."""
    return np.pi * EPS0 * h / (10 * np.log(4 * x / d))

class ProximityLaw:
    """Hand distance -> beat frequency (raw Colpitts law or linearized)."""
    def __init__(self, L=280e-6, C1=220e-12, C_fix=33e-12, linearize=True,
                 f_min=131.0, f_max=1046.0):
        self.L, self.C1, self.C_fix = L, C1, C_fix
        self.f_ref = self._f_pitch(1.0)          # far hand => beat ~ 0
        self.linearize = linearize
        self.f_min, self.f_max = f_min, f_max

    def _f_pitch(self, x):
        C2 = self.C_fix + c_antenna() + dc_hand(x)
        C_eq = self.C1 * C2 / (self.C1 + C2)
        return 1.0 / (2 * np.pi * np.sqrt(self.L * C_eq))

    def beat(self, x):
        fT = np.abs(self.f_ref - self._f_pitch(x))
        if not self.linearize:                   # raw law: high octaves compressed
            return fT
        # linearized air-keyboard: map x in [x_near, x_far] to [f_max, f_min]
        x_near, x_far = 0.06, 1.0
        u = np.clip((x_far - x) / (x_far - x_near), 0.0, 1.0)
        return self.f_min + u * (self.f_max - self.f_min)

class ThereminVoice:
    """Phase-continuous BFO voice: gesture arcs -> mono audio, length-preserving."""
    def __init__(self, law, vib_rate=5.5, vib_depth=0.012, seed=0):
        self.law, self.vib_rate, self.vib_depth = law, vib_rate, vib_depth
        self.rng = np.random.default_rng(seed)
        self.phase = 0.0

    def render_arc(self, f0, f1, dur, vol_curve=None, contour='arch'):
        n = int(dur * FS)
        tt = np.arange(n) / FS
        # musical glissando: log-frequency interpolation f0 -> f1 over the arc
        f_car = f0 * (f1 / f0) ** (tt / dur)
        # vibrato: hand tremor, phase-continuous
        f_car *= 1 + self.vib_depth * np.sin(2 * np.pi * self.vib_rate * tt + self.rng.uniform(0, 2*np.pi))
        if contour == 'arch':                     # gesture shaping on top of glide
            f_car *= 1 + 0.03 * np.sin(np.pi * tt / dur)
        self.phase = np.mod(self.phase + 2 * np.pi * np.cumsum(f_car) / FS, 2 * np.pi)
        y = np.sin(self.phase)
        if vol_curve is None:                     # 20 ms fade to avoid edge clicks
            vol = np.ones(n); a = int(0.02 * FS)
            vol[:a] = np.linspace(0, 1, a); vol[-a:] = np.linspace(1, 0, a)
        else:
            vol = vol_curve
        return (y * vol).astype(np.float32)       # len == n exactly (zero-drift)

# UnitMatrix integration: row = ThereminVoice, column = arc, cell = (f0, f1, vol_peak)
law = ProximityLaw(linearize=True, f_min=131.0, f_max=1046.0)
voice = ThereminVoice(law, vib_rate=5.5, vib_depth=0.012, seed=7)
y_a = voice.render_arc(220.0, 440.0, 2.0)         # section A: rise arc
y_b = voice.render_arc(440.0, 523.25, 1.5, vol_curve=np.linspace(0, 1, int(1.5*FS)))  # B: swell
```

Dispatch contract (musicom_workflow `produce`):

```python
produce(midi_path, method="SP-133", params={
    "rows": [{"pitch_min_hz": 131, "pitch_max_hz": 1046, "vib_rate": 5.5,
              "vib_depth": 0.012, "vol_shape": "swell", "law": "linearized", "seed": 7}, ...],
    "columns": {"A": {"register": "mid", "contour": "arch", "vibrato": "on"},
                "B": {"register": "high", "contour": "rise", "vibrato": "deep"}, ...},
    "fs": 48000})
```

Stage order: **THS (per-row BFO voice)** → row tone/EQ (SP-007) →
spatialize (SP-021/SP-053/SP-132) → room (SP-009/SP-032/SP-075) →
dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122).

---

## 4. Verification (reference prototype, `projects/Research/outputs/sp133_proto/`)

| check | result |
|---|---|
| heterodyne LP beat ($f_1$=8k, $f_2$=9k) | **1000.0 Hz** (theory 1000) |
| $C_A(\infty)$ | **6.61 pF** (theory ~7) |
| $\Delta C_A(0.10\,\text{m})$ | **0.38 pF** (theory 0.4) |
| raw beat range [1.0, 0.06] m | **0 → 3561 Hz** (2514 Hz @ 10 cm) |
| mid-range linearity | slope **−2252 Hz/m**, max resid 433 Hz over 157–1856 Hz |
| near-antenna steepening | **19.1×** gradient vs 0.6 m |
| +0.01 pF → beat | **1.93×** (10 pF tank), **1.35×** (40 pF tank) |
| const 440 Hz render | **440.0 Hz** (zero-crossing count) |
| gliss 220→440 endpoints | 242 / 398 Hz (theory 244 / 397) |
| zero-drift length | 96000 == 96000 samples |
| RF-product aliasing trap | measured **4717 Hz** vs 1000 (quantified pitfall) |

---

## 5. References

1. Theremin, L. S. (1928). US Patent 1,661,058, "Method of and Apparatus for the Generation of Sounds".
2. Skeldon, K. D., Reid, L. M., McInally, V., Dougan, B., & Fulton, C. (1998). "Physics of the Theremin." *American Journal of Physics* 66(11), 945–955. doi:10.1119/1.19004.
3. Wikipedia, "Theremin" (rev. 2026-11-04) — design facts, 0.01 pF/octave claim, linearizing coil, Open Theremin heterodyne architecture.
4. Wikipedia, "Heterodyne" (rev. 2026-11-04) — mixing identities, BFO radio lineage, Fessenden 1901.
5. Santos, M. R., & Salazar, A. E. C. (2021). "Optical digital theremin with audio synthesis and graphic interface." *NAUN Circuits, Systems and Signal Processing* 15.
6. Glinsky, A. (2000). *Theremin: Ether Music and Espionage*. University of Illinois Press.
