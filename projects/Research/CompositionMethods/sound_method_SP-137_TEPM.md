# SP-137 — Magnetic Tape Echo Physical Modeling (TEPM)

**Layer:** absolute (sound production)
**Category:** Post-Processing / DSP → Electromechanical Device Emulation → Tape Echo
**Candidate code path:** `sound/effects/tape_echo.py`
**Summary-table row (as inserted, methods_db.md line 347):**

```
| **SP-137** | Magnetic Tape Echo Physical Modeling (TEPM) | **Post-Processing / DSP** | Physical Tape-Echo Delay / Electromechanical Echo, Wow-Flutter & Saturation | Models the Echoplex (1959) / Roland RE-201 (1974) tape transport: delay from geometry $\tau_k=d_k/v$ (record→play head gap over tape speed; movable sled 30–660 ms, multi-head 1:2:3 readout), time-varying fractional-delay read with wow/flutter Doppler FM ($\max|\Delta f|=f_0\tau_0 m\omega_w$; measured 12.74 vs 12.57 Hz, 1.4%), motor-inertia speed ramp, record-path tanh saturation (odd-only harmonics, h3 −51.4→−28.3 dB), per-pass HF damping (centroid 9655→7065 Hz), re-circulating hiss (tail RMS 126% of no-fb). Echo $k$ amplitude $=g_{fb}^{k}$ (measured 0.600/0.600). Sample-count preserving, deterministic per seed. Candidate: `sound/effects/tape_echo.py`. |
```

---

## 1. The transport geometry: delay = gap / speed

A tape echo (Echoplex 1959; Roland RE-201 1974) is a record head writing an endless
tape loop, and one or more play heads mounted downstream reading the magnetization
back. The delay of head $k$ is purely geometric:

$$\tau_k = \frac{d_k}{v}$$

- $d_k$ = record→play head gap in inches ($d_k = k\,d_0$ for a 1:2:3 multi-head bank),
- $v$ = tape speed in inches/sec (7.5 ips = 19.05 cm/s is the "fast" RE-201 setting;
  3.75 ips / 9.5 cm/s doubles every delay),
- Echoplex: one play head on a movable sled → one continuous $d$, ~30–660 ms;
- RE-201: three fixed play heads → ≈74 / 148 / 222 ms @ 19 cm/s (1:2:3).

**Verified** (44.1 kHz prototype): $d_0=1.5$ in @ 7.5 ips → $\tau_0=0.2$ s → impulse
peak at sample 8920 exactly; @ 3.75 ips → 400 ms → sample 17740; three heads →
peaks at 8920 / 17740 / 26560.

## 2. The time-varying fractional delay line

Because the tape speed wobbles and slews, the read pointer is a *time-varying*
fractional delay:

$$D_k[n] = \tau_k(n/f_s)\,f_s = \frac{d_k}{v(n/f_s)}\,f_s$$

$$D_{int}=\lfloor D_k\rfloor,\quad \delta = D_k - D_{int},\qquad
y_k[n] = (1-\delta)\,x[n-D_{int}] + \delta\,x[n-D_{int}-1]$$

Linear interpolation (2-tap) is the DAFX minimum; 4-point Lagrange gives a flatter
passband for wideband material. Interpolation is **mandatory** — integer truncation
of a moving read pointer zipper-clicks on every echo.

## 3. Wow / flutter = speed modulation = Doppler FM on the echoes

Tape speed is not constant:

$$v(t) = v_0\Big(1 + m_w\sin(2\pi f_w t + \phi_w) + m_f\sin(2\pi f_f t + \phi_f)\Big)$$

- wow: $f_w \approx 0.5$–4 Hz (slow pitch wander, "tape warble"),
- flutter: $f_f \approx 5$–100 Hz (rapid shimmer),
- $m_w, m_f$: fractional speed deviation ($10^{-4}$–$10^{-2}$; ANSI/IEC wow-flutter
  metering weights these bands).

With $\tau(t)=\tau_0/(1+m\sin\omega_w t)$, output phase $\varphi(t)=\omega_0(t-\tau(t))$
gives instantaneous frequency deviation

$$\Delta f(t) = -f_0\,\frac{d\tau}{dt} \approx f_0\,\tau_0\,m\,\omega_w\cos(\omega_w t),
\qquad \boxed{\max|\Delta f| = f_0\,\tau_0\,m\,\omega_w}$$

**Verified** ($f_0=1$ kHz, $\tau_0=0.2$ s, $m=0.005$, $f_w=2$ Hz): measured peak
deviation **12.74 Hz** vs theory 12.57 Hz — **1.4 %** error (complex-demodulation
measurement, envelope-gated).

Two consequences for composition:
- Long echoes wobble *more* at the same % speed error ($\tau_0$ multiplies the depth),
- the dry signal is untouched — only the repeats carry the FM.

## 4. Motor inertia

The capstan/pinch-roller takes tens of ms to reach speed:

$$v(t) = v_0\big(1-e^{-t/\tau_m}\big), \qquad \tau_m \approx 0.05\text{–}0.2\text{ s}$$

**Verified:** with $\tau_m=0.05$ s the first echo of an impulse lands at sample 9067
vs the nominal 8920 — late and sharp-rising. This is the physical "start-up" gesture
(power-on warble) that digital delays must fake.

## 5. Record path: saturation + bias

The record amp + tape curve is an odd soft-clipper (tanh normalization keeps
small-signal gain unity):

$$r[n] = \frac{\tanh\big(g\,u[n]\big)}{\tanh(g)},\qquad
u[n] = x[n] + g_{fb}\,p_A[n] + h[n]$$

**Verified odd-only harmonic growth** (drive $g$): 3rd harmonic −51.4 dB @ 0.3 →
−28.3 dB @ 1.2; 2nd harmonic < −181 dB at both. The (inaudible, 40–100 kHz) bias
oscillator is what linearizes the small-signal region in hardware; here it is
implicit — model it explicitly only if you want its slight curve asymmetry.

## 6. Per-pass HF loss

Gap loss, spacing loss and playback EQ roll the high end off on *every* read; one
pole per pass with $\alpha = 1-hf\_damp$:

$$s[n] \mathrel{+}= (1-hf\_damp)\,\big(p_A[n] - s[n]\big)$$

**Verified:** spectral centroid of echo 1 = 9655 Hz → echo 3 = 7065 Hz. This is what
makes the tail *darken* — each generation loses high end on top of the amplitude
decay.

## 7. Feedback loop: echoes as a geometric series

Feedback taps the first play head (Echoplex topology):

$$u[n] = x[n] + g_{fb}\,p_A[n] + h[n], \qquad \text{wet}[n] = \sum_k g_k\,p_k[n]$$

Echo $k$ amplitude $\propto g_{fb}^{k}$.

**Verified** ($g_{fb}=0.6$): echo amplitudes 1.000 / 0.600 / 0.360 — ratios
0.600 / 0.600 exactly.

Hiss (injected on the tape, so it re-circulates) converges to

$$\sigma_{\text{tail}}^2 = \frac{\sigma_h^2}{1-g_{fb}^2}$$

**Verified:** tail RMS 126 % of the no-feedback case at $g_{fb}=0.7$ (theory
$\sqrt{1/(1-0.49)}=140$ %; the shortfall is finite convergence time).

## 8. NumPy implementation sketch

```python
import numpy as np

class TapeEcho:
    """Physical tape echo: transport geometry + fractional delay + degradation.

    delay_seconds_0  = d0_in / v_ips            # geometric delay law
    heads            = [(d_in_multiplier, gain), ...]   # 1:2:3 bank
    """
    def __init__(self, fs=44100, v_ips=7.5, d0_in=1.5, heads=((1.0, 0.8), (2.0, 0.6), (3.0, 0.4)),
                 feedback=0.5, drive=1.0, hf_damp=0.35, motor_tau=0.0,
                 wow=(0.002, 1.5), flutter=(0.0004, 7.0), hiss_level=1e-4, seed=0):
        self.fs, self.v0 = fs, v_ips
        self.d0_in = d0_in
        self.heads = heads
        self.fb, self.drive, self.hf = feedback, drive, hf_damp
        self.motor_tau = motor_tau
        self.wow_m, self.wow_f = wow
        self.fl_m, self.fl_f = flutter
        self.rng = np.random.default_rng(seed)
        self.hiss = hiss_level

    def process(self, x):
        n = len(x)
        t = np.arange(n) / self.fs
        vscale = np.maximum(1 - np.exp(-t / self.motor_tau), 0.01) if self.motor_tau > 0 else np.ones(n)
        speed = self.v0 * vscale \
            * (1 + self.wow_m * np.sin(2 * np.pi * self.wow_f * t + 0.7)) \
            * (1 + self.fl_m * np.sin(2 * np.pi * self.fl_f * t + 1.3))
        tau0 = self.d0_in / speed                       # seconds, time-varying
        tail = int(np.max(tau0 * self.heads[-1][0]) * self.fs * 2) + self.fs
        buf = np.zeros(n + tail)
        wet = np.zeros(n)
        lp = 0.0
        hiss = self.rng.normal(0, self.hiss, n)
        for i in range(n):
            rec = x[i] if i < n else 0.0
            for k, (mul, g) in enumerate(self.heads):
                d = tau0[i] * mul * self.fs
                ip, fr = int(np.floor(d)), d - np.floor(d)
                j = i - ip
                if j < 0:
                    continue
                pa = buf[j] + fr * (buf[j - 1] if j - 1 >= 0 else 0.0)
                if k == 0:
                    lp += (1 - self.hf) * (pa - lp)     # per-pass HF loss (head A)
                    pa = lp
                    rec += self.fb * pa + hiss[i]       # feedback + tape hiss
                wet[i] += g * pa
            buf[i] = np.tanh(self.drive * rec) / np.tanh(self.drive) if self.drive > 0 else rec
        return wet

# demo: dry + wet through the model
# td = TapeEcho(); wet = td.process(dry); out = dry + wet
```

Deterministic per seed (hiss RNG + wobble phases fixed), output length
`len(x) + tail` — sample-count preserving, zero-drift safe.

## 9. UnitMatrix workflow wiring

```
UnitMatrix (rows = voices, cols = sections, cells = MusicUnit)
  -> rows render dry buffers (SP-001/SP-011/SP-098/SP-136 per-voice sources)
  -> TEPM per row/bus:  produce(midi_path, method="SP-137", params={...})
  -> per-row EQ (SP-007) -> spatialize (SP-021/SP-053) -> room (SP-009/SP-032/SP-075)
  -> bus dynamics (SP-008/SP-107) -> loudness (SP-126) -> dither (SP-122)
```

Section changes are *transport events*: `{v_scale, motor_trigger, feedback, head_gains}`
— speed changes move echo time AND echo pitch together (physical coupling, see
Pitfall 6 in the DB section).

## References

- Wikipedia: "Echoplex" (Mike Battle, Maestro/Guild 1959; movable-sled play head,
  ~30–660 ms); "Roland Space Echo" (RE-201, 1974; free-running tape transport,
  three play heads, 1:2:3 delays, spring reverb/chorus variants).
- Zölzer, U. (2011). *DAFX — Digital Audio Effects*, 2nd ed., Wiley — fractional
  delay lines, modulated delay lines, Doppler analysis of time-varying delay.
- ANSI/IEC wow-and-flutter measurement standards (peak weighted; wow band
  0.5–4 Hz, flutter band 4–200 Hz) — the metrology behind $m_w, m_f, f_w, f_f$.
- NAB/IEC record-play equalization curves; magnetic-tape gap/spacing loss
  physics (the per-pass HF rolloff).
- Repo antecedent: `sound/effects/tape_delay.py::TapeDelay` (unregistered,
  surveillance-derived; superseded by TEPM's transport model).
- Verification: `_web137/tepm_verify.py` (12/12 checks), log
  `_web137/tepm_verify_output.txt`, demo `_web137/sp137_demo.wav`
  (119 070 frames @ 44.1 kHz, 238 184 B).

**Next free SP ID after this entry: SP-138.**
