# SP-074 — Piano Hammer-String Physical Modeling (PHSP)

**Layer:** absolute (sound production — Synthesis Engines)
**Category:** Synthesis Engines | **Target Output:** Physical Struck-String / Grand-Piano Timbre
**Candidate code path:** `sound/synthesis/piano_hammer.py`
**Status:** documented 2026-09-15 (cron sound-production research job)

One-line: physically calibrated piano — a Hertz-contact felt hammer strikes a stiff,
dispersive waveguide string; detuned unison strings share a bridge impedance
(two-stage decay); soundboard IR + pedal-down sympathetic resonance complete the
instrument. Audio out, from symbolic note events.

---

## 1. Why this method (gap analysis)

| Existing method | What it lacks vs a real piano |
|---|---|
| SP-011 Karplus-Strong | idealized pluck: no hammer, no inharmonicity, no stretch, velocity = amplitude only |
| SP-048 Commuted Synthesis | hammer+body pre-baked into a fixed excitation table: contact dynamics lost |
| SP-033 Digital Waveguide (generic) | waveguide without a piano exciter/dispersion calibration |
| SP-040 FDTD | exact but plate/membrane-oriented; per-note strings at 1/50 the cost via waveguides |

PHSP completes the excitation-type matrix: **pluck** (011/048), **bow** (024),
**lip-reed** (065), **air-jet** (066), **strike** (074).

## 2. Physics

### 2.1 Stiff string
$$\mu\,\partial_t^2 y = T\,\partial_x^2 y - E I\,\partial_x^4 y - R\,\partial_t y,\qquad c=\sqrt{T/\mu}$$
Inharmonic partials (Fletcher 1964):
$$f_n = n f_1\sqrt{1+B n^2},\qquad B=\frac{\pi^3 E d^4}{64\,T\,L^2}\ (\text{solid string})$$
$B$: $\sim4\times10^{-5}$ (wound bass) … $\sim10^{-3}$ (short treble). At $B=10^{-4}$,
partial 8 is ~32 cents sharp of $8f_1$.

### 2.2 Hammer (Boutillon 1988 / Stulov 1995)
While $\xi_h>\xi_s$:
$$F_c = K_c(\xi_h-\xi_s)^p + c_h(\dot\xi_h-\dot\xi_s),\qquad p\approx2.2\text{–}3.5,\qquad m_h\ddot\xi_h=-F_c$$
else $F_c=0$. Strike velocity $v_0=v_{min}(v/127)^{k_v}$ ($v$ = MIDI velocity;
physical $v_0\approx0.2$–5 m/s). Contact 1–5 ms. Faster strike ⇒ deeper felt
penetration ⇒ larger effective $K_c$ ⇒ brighter tone (velocity-dependent
brightness is *in the physics*, not a filter knob).

Injection at the strike point $x_p$ (bidirectional split):
$$y^+ \mathrel{+}= \tfrac{1}{2}F_c/Z_0,\qquad y^- \mathrel{-}= \tfrac{1}{2}F_c/Z_0,\qquad Z_0=\sqrt{T\mu}$$
Strike at $x_p=L/p$ nulls partials $n=p,2p,\dots$ (strike-position comb — free).

### 2.3 Dispersive loop filter
$$H_{loop}(z)=z^{-N}\,H_b(z)\,A_d(z),\qquad A_d(z)=\frac{a_d+z^{-1}}{1+a_d\,z^{-1}}$$
Tune $N$ (fractional part via Lagrange-3 or allpass) and $a_d$ so round-trip phase
at partial $n$ equals $f_s/f_n$ of the *inharmonic* target (Bank 2003 closed form
for the first-order allpass). Loss filter $H_b(z)$ (2nd-order "loss pole") sets the
decay ladder $|H_{loop}(e^{j\omega_n})|^{t f_1/f_s}\cdot$ per-partial $=e^{-t/\tau_n}$:
low partials ring seconds, high partials die in tens of ms.

### 2.4 Coupled unisons → two-stage decay (Weinreich 1977)
$q\in\{2,3\}$ strings detuned by $\delta_i$ (±0.15 Hz), all terminating on a shared
bridge admittance $Z_b(\omega)$ (mass-spring resonance feeding back into all
strings). Energy hand-off at the beat rate $\Delta f$ gives
$$A(t)\approx A_1 e^{-t/\tau_1}+A_2 e^{-t/\tau_2},\qquad\tau_1\ll\tau_2$$
fast attack-decay + long after-sound. $\Delta f$ = lush-sustain knob.

### 2.5 Soundboard & pedals
Bridge force sum → $h_{sb}[n]$ (2–4 kHz decaying IR, 60–200 Hz resonances);
optionally commuted into a per-velocity excitation table (SP-048 trick).
Sustain pedal leaves undamped strings resonating sympathetically (couple through
$Z_b$, never directly, or the loop howls). Una corda shifts strike off-center →
thinner upper partials.

### 2.6 Railsback stretch tuning
$$s(f)=s_{max}\,\mathrm{sgn}(x)\,x^2,\quad x=\log_2(f/261.63),\quad s(\text{A7})\approx+30\text{¢},\ s(\text{A0})\approx-30\text{¢}$$
Per-note $f_1=f_{ET}\,2^{s/1200}$; precompute $N$, $a_d$ from the *stretched* $f_1$.
Also: velocity → transient pitch droop $\Delta f\propto v^2$ (tens of cents, ~50 ms).

## 3. Python/NumPy implementation sketch

```python
import numpy as np
from dataclasses import dataclass, field

@dataclass
class PianoConfig:
    sample_rate: int = 48000
    B_table: str = "fit"        # per-key inharmonicity B(k) (~4e-5 bass → 1e-3 treble)
    unison_detune_hz: float = 0.15
    unison_count: int = 3
    hammer_mass: float = 5.0    # grams (per register)
    hammer_p: float = 2.8       # Boutillon exponent
    soundboard_ir: np.ndarray | None = None   # 2–4 kHz decaying IR

def railsback_cents(f):        # stretch tuning, parabolic in log f
    x = np.log2(f / 261.63)
    return 30.0 * np.sign(x) * x * x

def dispersion_allpass(B, f1, fs):     # 1st-order allpass coefficient (Bank 2003)
    # solve phase delay at partial 2 (or 3) to match f_n = n f1 sqrt(1+B n^2)
    f2_target = 2 * f1 * np.sqrt(1 + 4 * B)
    # a_d from closed-form allpass delay: tau_ap(f) = (1 - a)/(1 + a) / (2 pi f)...
    # numerically: minimize |angle(A_d(e^{jw2})) + 2*pi*f2_target/(fs/2) - N_phase|²
    ...

class PianoStringVoice:
    """Bidirectional waveguide + hammer ODE + loop filters. O(1) per sample."""
    def __init__(self, key, B, f1_stretched, fs, vel, strike_pos=1/7, ...):
        N = fs / f1_stretched
        self.Ni, self.Nfrac = int(N // 2), N / 2 - int(N // 2)   # halves
        self.Dp = np.zeros(self.Ni + 4); self.Dm = np.zeros(self.Ni + 4)
        self.a_d = dispersion_allpass(B, f1_stretched, fs)
        self.hb = loss_filter(f1_stretched, fs)                  # 2nd-order loss pole
        self.zh = 0.0; self.vh = vel_to_ms(vel)                  # hammer state
        self.in_contact = False

    def render(self, n_samples, pedal=False):
        out = np.zeros(n_samples)
        for i in range(n_samples):
            # hammer: semi-implicit Euler substeps while xi_h > xi_s
            xi_s = (self.read_front(self.Dp) + self.read_front(self.Dm)) / 2
            Fc = self.hertz_force(xi_s)                          # 0 if released
            if Fc:
                self.write_tail(self.Dp,  0.5 * Fc / self.Z0)
                self.write_tail(self.Dm, -0.5 * Fc / self.Z0)
            # loop: halves → allpass → loss → bridge sum → back
            bridge = self.loop_step()                            # incl. unison coupling
            out[i] = self.sb_conv_step(bridge)
        if not pedal:
            out *= damper_fade(n_samples)                        # 5–15 ms loop-gain ramp
        return out
```

Full polyphony = dict of active `PianoStringVoice`s (one per note; ≤3 unison
waveguides inside), each O(1)/sample, O(N) memory. Render trigger: note-on →
hammer state init + voice create; note-off → damper (unless pedal).

## 4. Musical Elements Framework

- **PITCH** — physical: inharmonic ladder + Railsback stretch; ff pitch droop.
  Stretched octaves = real-piano beating on octave material (SRG layers).
- **RHYTHM** — 1–5 ms velocity-dependent contact delay (accents lead naturally);
  re-strikes of ringing strings are click-free; damper noise on release.
- **HARMONY** — unison beating; bridge-shared energy bleeds chord tones into each
  other; pedal-down sympathetic wash = emergent harmony.
- **STRUCTURE** — per-section pedal state / hammer voicing (soft-hard felt) =
  macro articulation plan; two-stage decay lets after-sound cross barlines.
- **TEXTURE** — native polyphony (independent physical strings); pedal wash =
  canonical continuous-fill layer (Method Hybridization rule, pairs with sparse
  011/032 grooves); una corda = one-knob darkener.

## 5. UnitMatrix Integration

- Rows (voices) = piano registers or layered pianos (each with own B, hammer
  mass/felt, detune); columns (sections) = pedal state, voicing, soundboard, detune
  depth; cells (MusicUnit) = PITCH → f1/N/a_d (precomputed per key), RHYTHM →
  hammer release/damper timing, HARMONY → simultaneous banks + sympathetic
  excitation, TEXTURE → velocity spread = felt-hardness spread.
- Flow: `compose` (UnitMatrix MIDI) → `produce(method="SP-074")` per-voice render →
  SP-006 humanization feeds strike velocity → SP-009/032/071 reverb if needed →
  SP-008 limit → WAV/OGG. Bypasses SP-001 for piano rows (FluidR3 piano is a
  static sample patch; PHSP is velocity-continuous).

## 6. Pitfalls (condensed)

1. **Delay-free hammer loop** — evaluate contact against incoming wave variables
   only (or 1-sample implicit Newton); naive velocity feedback explodes.
2. **ODE stiffness** — RK4/semi-implicit substeps (4–8) while in contact; cap
   penetration.
3. **Fractional delay detune** — Lagrange-3 + allpass; precompute N from stretched
   f1, not ET.
4. **Treble aliasing** ($B\sim10^{-3}$) — per-note loop lowpass scaling with f1, or
   2× oversample treble voices.
5. **Sympathetic howl** — couple through bridge impedance with its own loss; clamp
   excitation energy; expander on undamped strings.
6. **CPU** — commute soundboard into per-velocity tables (SP-048) or run soundboard
   once on the bridge bus, not per voice.
7. **Velocity zipper** — map v continuously into K_c/p/cutoff; no discrete layers.
8. **Damper clicks** — 5–15 ms loop-gain ramp + felt-noise tail.
9. **Not SP-048** — commuted = fast but no contact dynamics; PHSP for expressive
   keys, SP-048 for cheap beds.

## 7. References
- Boutillon, X. (1988). "Model for piano hammers: Experimental determination and digital simulation." JASA 83(1), 307–317.
- Stulov, A. (1995). "Hysteretic model of the grand piano hammer felt." JASA 97(4), 2571–2577.
- Weinreich, G. (1977). "Coupled piano strings." JASA 62(6), 1474–1484.
- Fletcher, H. (1964). "Normal vibration frequencies of a stiff piano string." JASA 36(1), 218–228.
- Railsback, O. L. (1943). "Scale temperament as applied to piano tuning." JASA 15(4), 807.
- Bank, B. (2003). Physics-Based Sound Synthesis of the Piano. MSc thesis, BME Budapest.
- Smith, J. O. (2010). Physical Audio Signal Processing. W3K Publishing.
- Conklin, H. A. (1996). "Design and tone in the mechanoacoustic piano. Part I." JASA 100(2), 695–708.
- Bensa, J., Bilbao, S., Kronland-Martinet, R., & Smith, J. O. (2003). "The simulation of piano string vibration…," JASA 114(2), 1095–1107.
- Van Duyne, S., & Smith, J. O. (1995). "Physical modeling with the 2-D digital waveguide mesh." Proc. ICMC.
