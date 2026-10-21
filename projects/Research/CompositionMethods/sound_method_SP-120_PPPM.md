# SP-120 — PhISEM Particle Percussion Physical Modeling (PPPM)

**ID:** SP-120
**Layer:** absolute — sound production (Synthesis Engines)
**Candidate code path:** `sound/synthesis/phisem_percussion.py`
**Produce dispatch:** `workflows.musicom_workflow.produce(method="SP-120")`
**One-line:** Stochastic particle-collision percussion synthesis (maraca, cabasa, sekere, tambourine, sleighbells, bamboo, angklung, sandpaper, coke can, guiro, wrench, water drops, gravel, coins) via Poisson-gated impulses into damped biquad resonators — Cook's PhISEM (1997).

---

## 1. Overview

PhISEM (**Ph**ysically **I**nformed **S**tochastic **E**vent **M**odeling) simulates a shaken enclosure of $N$ small hard objects without integrating $N$ particle trajectories. The micro-physics is replaced by a per-sample Poisson collision gate: a collision fires with probability $N/1024$, injecting an impulse equal to the current *shake energy* $E$ into a bank of damped second-order resonators whose poles ARE the instrument's body modes. The macro-physics (energy input, exponential enclosure decay, per-event sound decay) is simulated exactly; collision timing is random. Cost is $\mathcal{O}(1)$ per sample regardless of $N$ — the same code renders a 25-bean maraca and a 1600-particle gravel spray.

The companion PhOLIES set (**Ph**ysically-**O**riented **L**ibrary of **I**mitated **E**nvironmental **S**ounds, Cook 1997–8) extends the same machinery to environmental textures: breaking sticks, crunchy snow, sandpaper, wrench, coins-in-mug.

---

## 2. History & Sources

- **Cook, P. R. (1997).** "Physically Informed Sonic Modeling (PhISM): Synthesis of Percussive Sounds." *Computer Music Journal* 21(3), 38–49. DOI: 10.2307/3681012. — Definitive paper (75+ citations per Crossref). Introduces PhISEM: stochastic event modeling for collisions of multiple independent sound-producing objects.
- **Cook, P. R. (1996).** "Physically Informed Sonic Modeling (PhISM): Percussive Synthesis." *Proc. ICMC 1996*, Hong Kong. — Conference version.
- **Cook, P. R. & Scavone, G. (1995–2023).** *The Synthesis ToolKit (STK)*, `Shakers` class (PhISEM + PhOLIES), `include/Shakers.h`, `src/Shakers.cpp`. https://github.com/thestk/stk — canonical reference implementation; parameter tables and tick() algorithm verified against this source for this write-up.
- **Cook, P. R. (2002).** *Real Sound Synthesis for Interactive Applications*. A K Peters. — book treatment.
- **Van den Doel, K. & Pai, D. K. (1998).** "Synthesis of Shape Dependent Sounds." *Proc. ICAD 1998*. — parallel impulse-resonator contact synthesis.

---

## 3. Technical Mechanics (full)

### 3.1 State

| Variable | Meaning | Typical range |
|---|---|---|
| $E[n]$ | shake energy (global kinetic energy of particle system) | $[0, 1]$, $E_{\min}=0.001$ |
| $s[n]$ | sound level (current resonator excitation) | $[0, \sim 10]$ |
| $N$ | number of colliding objects (may be fractional!) | $1.1 \dots 1600$ |
| $f_i, r_i, g_i$ | resonator center freq, pole radius, gain ($i=1..R$) | see tables |
| $d_{\mathrm{sys}}, d_{\mathrm{snd}}$ | system decay, sound decay | $0.99586 \dots 0.9999$, $0.9 \dots 0.999$ |

### 3.2 Per-sample algorithm (STK `Shakers::tick`)

1. **Energy gate:** if $E[n] < 0.001$ → output 0 (note finished).
2. **System decay:** $E[n] \leftarrow E[n] \cdot d_{\mathrm{sys}}$ — the enclosure/particle kinetic energy drains exponentially; $d_{\mathrm{sys}}$ near 1 ⇒ long shake.
3. **Collision gate:** draw $U \sim \mathcal{U}(0, 1024)$; if $U < N$:
   $$s[n] \mathrel{+}= E[n]$$
   (event probability $N/1024$ per sample ⇒ Poisson rate $\lambda = N f_s/1024$ s⁻¹; impulse amplitude = current shake energy).
   Optional per-collision resonator re-tuning: $f_i \leftarrow f_i(1 + v\,\xi)$, $\xi \sim \mathcal{U}(-1,1)$.
4. **Sound decay:** $s[n] \leftarrow s[n] \cdot d_{\mathrm{snd}}$ — faster than system decay (per-event ringing drain).
5. **Resonator bank** ($R$ parallel biquads):
   $$y_i[n] = g_i G\, s[n] - a_1^{(i)} y_i[n{-}1] - a_2^{(i)} y_i[n{-}2]$$
   $$a_1^{(i)} = -2 r_i \cos(2\pi f_i / f_s), \qquad a_2^{(i)} = r_i^2$$
   $-3$ dB bandwidth $\approx f_s (1-r_i)/\pi$ Hz; pole angle = center frequency. Angklung variant: only a randomly selected tube receives the impulse, others ring freely.
6. **Gain normalization:** $G = \ln(N) \cdot G_{\mathrm{base}} / N$ — more objects ⇒ quieter per event, denser events; total loudness grows only logarithmically with $N$.
7. **Final EQ FIR** (3-tap spectral tilt): maraca `[1,−1,0]` (differentiator highpass tilt), coke can `[1,0,−1]`, angklung `[1,0,−1]`, water `[−1,0,1]`, cabasa/sekere/tambourine/sleigh `[0,1,0]` (flat).

### 3.3 Instrument tables (verified from STK `Shakers.cpp`)

| Instrument | $N$ | Resonators $(f_i$ Hz, $r_i$, $g_i)$ | $d_{\mathrm{sys}}$ | $d_{\mathrm{snd}}$ | $G_{\mathrm{base}}$ | EQ |
|---|---|---|---|---|---|---|
| Maraca | 25 | (3200, .96, 1) | .999 | .95 | 4.0 | [1,−1,0] |
| Cabasa | 512 | (3000, .70, 1) | .997 | .96 | 8.0 | flat |
| Sekere | 64 | (5500, .60, 1) | .999 | .96 | 4.0 | flat |
| Tambourine | 32 | (2300, .96, .1), (5600, .99, .8), (8100, .99, 1) | .9985 | .95 | 1.0 | flat |
| Sleighbells | 32 | (2500,.99,1), (5300,.99,1), (6500,.99,1), (8300,.99,.5), (9800,.99,.3) | .9994 | .97 | 1.0 | flat |
| Bamboo chimes | 1.2 | (2800,.995,1), (2240,.995,1), (3360,.995,1) | .9999 | .90 | .4 | [1,0,−1] |
| Angklung (tuned) | 1.2 | (1046.6, 1174.8, 1397, 1568, 1760, 2093.3, 2350; r=.996, g=1) | .9999 | .95 | .5 | [1,0,−1] |
| Sandpaper | 128 | (4500, .60, 1) | .999 | .999 | .5 | flat |
| Coke can | 48 | (370,.99,1), (1025,.992,1.8), (1424,.992,1.8), (2149,.992,1.8), (3596,.992,1.8) | .999 | .97 | .5 | [1,0,−1] |
| Guiro (ratchet) | 128 | (2500,.97,1), (4000,.97,1) | ratchet | .95 | .4 | flat |
| Wrench (ratchet) | 128 | (3200,.99,1), (8000,.992,1) | ratchet | .95 | .4 | flat |
| Water drops | 10 | (450,600,750; r=.9985, g=1), sweep ×1.0001/sample | .996 | .95 | 1.0 | [−1,0,1] |
| Big rocks | 23 | (6460, .932, 1) | .9965 | .98 | 4.0 | flat |
| Little rocks | 1600 | (9000, .843, 1) | .99586 | .98 | 4.0 | flat |
| Coins in mug | 3 | per-coin 3 modes 1.7–11 kHz, r≈.997–.9996 | .9995 | .97 | .8 | flat |

### 3.4 Controls (STK control-change mapping)

- **Shake energy** (CC2/128, or velocity): $E \mathrel{+}= \text{amp}\cdot 0.1$, clamp $E_{\max}=1$; `noteOff` ⇒ $E=0$ (instant release).
- **System decay** (CC4): $d_{\mathrm{sys}} = d_{\mathrm{base}} + 2(\nu-0.5)\,k\,(1-d_{\mathrm{base}})$, $\nu\in[0,1]$ — shake length.
- **Object count** (CC11): $N' = 2\nu N_{\mathrm{base}} + 1.1$, $G = \ln(N')G_{\mathrm{base}}/N'$ — density knob.
- **Resonance freq** (CC1): $f_i' = f_i \cdot 4^{\nu-0.5}$ — ±1 octave brightness morph.
- **Instrument** (CC1071 / note number): STK maps `(int)(12·log₂(f/220)+57.01) % 32`; musicom port uses explicit names.

### 3.5 Python/NumPy implementation sketch

```python
import numpy as np

class PhISEMPercussion:
    """PhISEM particle percussion physical model (Cook 1997 / STK Shakers)."""

    INSTRUMENTS = {  # name: (N, [(f_Hz, r, gain)...], sys_decay, snd_decay, base_gain, eq_b)
        'maraca':      (25,   [(3200, 0.96, 1.0)],                    0.999,  0.95, 4.0, (1, -1, 0)),
        'cabasa':      (512,  [(3000, 0.70, 1.0)],                    0.997,  0.96, 8.0, (0, 1, 0)),
        'sekere':      (64,   [(5500, 0.60, 1.0)],                    0.999,  0.96, 4.0, (0, 1, 0)),
        'tambourine':  (32,   [(2300, 0.96, 0.1), (5600, 0.99, 0.8), (8100, 0.99, 1.0)], 0.9985, 0.95, 1.0, (0, 1, 0)),
        'sleighbells': (32,   [(2500, 0.99, 1.0), (5300, 0.99, 1.0), (6500, 0.99, 1.0),
                               (8300, 0.99, 0.5), (9800, 0.99, 0.3)], 0.9994, 0.97, 1.0, (0, 1, 0)),
        'cokecan':     (48,   [(370, 0.99, 1.0), (1025, 0.992, 1.8), (1424, 0.992, 1.8),
                               (2149, 0.992, 1.8), (3596, 0.992, 1.8)], 0.999, 0.97, 0.5, (1, 0, -1)),
        'angklung':    (1.2,  [(1046.6, 0.996, 1.0), (1174.8, 0.996, 1.0), (1397, 0.996, 1.0),
                               (1568, 0.996, 1.0), (1760, 0.996, 1.0), (2093.3, 0.996, 1.0),
                               (2350, 0.996, 1.0)], 0.9999, 0.95, 0.5, (1, 0, -1)),
        'waterdrops':  (10,   [(450, 0.9985, 1.0), (600, 0.9985, 1.0), (750, 0.9985, 1.0)],
                             0.996, 0.95, 1.0, (-1, 0, 1)),
    }

    def __init__(self, name='maraca', sample_rate=48000, seed=0):
        self.sr = sample_rate
        self.rng = np.random.default_rng(seed)
        N, res, dsys, dsnd, gbase, eq = self.INSTRUMENTS[name]
        self.N, self.dsys, self.dsnd, self.gbase, self.eq = N, dsys, dsnd, gbase, eq
        self.f = np.array([r[0] for r in res]); self.r = np.array([r[1] for r in res])
        self.g = np.array([r[2] for r in res])
        self.a1 = -2 * self.r * np.cos(2 * np.pi * self.f / self.sr)
        self.a2 = self.r ** 2
        self.y1 = np.zeros_like(self.f); self.y2 = np.zeros_like(self.f)
        self.E = 0.0; self.snd = 0.0; self._eqd = [0.0, 0.0]

    def note_on(self, velocity=1.0):
        self.E = min(1.0, self.E + velocity * 0.1)

    def note_off(self):
        self.E = 0.0

    def render(self, n_samples):
        out = np.empty(n_samples, dtype=np.float32)
        G = np.log(self.N) * self.gbase / self.N if self.N > 0 else 0.0
        gate = self.N / 1024.0
        for n in range(n_samples):
            if self.E < 0.001:
                out[n] = 0.0
                self.snd = 0.0
                continue
            self.E *= self.dsys
            if self.rng.random() < gate:
                self.snd += self.E
            self.snd *= self.dsnd
            x = self.snd * G
            y = self.g * x - self.a1 * self.y1 - self.a2 * self.y2
            self.y2 = self.y1; self.y1 = y
            v = float(np.sum(y))
            e0 = self.eq[0] * v + self.eq[1] * self._eqd[0] + self.eq[2] * self._eqd[1]
            self._eqd[1] = self._eqd[0]; self._eqd[0] = v
            out[n] = e0
        return out
```

---

## 4. Musical Elements Framework

- **PITCH:** quasi-pitched — resonator center frequencies define a fixed spectral signature; angklung carries a real tuned pitch row (1046.6–2350 Hz); coke can has a 370 Hz Helmholtz thump; freq-vary/CC1 shift brightness. Pitch is a timbre parameter, not an event parameter.
- **RHYTHM:** Poisson collision stream (rate $\lambda = N f_s/1024$) gives human-like micro-timing; macro-rhythm from shake-energy stroke patterns; ratchet instruments (guiro/wrench) count discrete strokes per shake.
- **HARMONY:** tuned multi-resonator tables (angklung heptatonic tube set) form stochastic harmonic clouds under sustained shaking; layered tuned PPPM voices create stochastic harmonic beds.
- **STRUCTURE:** section-level automation of $N$ (density), $E$ (intensity), $d_{\mathrm{sys}}$ (shake length), freq-scale (brightness); stroke-pattern per section; stochastic renders re-seeded per section.
- **TEXTURE:** primary dimension — dry granular rustle (maraca) → metallic shimmer (bells, $r \to 1$) → resonant boom (can/water); $N$ sweeps sparse grains → dense spray.

## 5. UnitMatrix Integration

- **Voices:** rows = PPPM instances on channel 9 (`MidiPercussion`), each with `(instrument, seed, N, decay, freq_scale)`; per-voice seed ⇒ deterministic, decorrelated.
- **Sections:** columns carry automation vector `(E_max, N, d_sys, freq_scale, stroke_pattern)`; pattern snaps to bar grid (stroke period = section beat division).
- **Cells:** MusicUnit = shake gesture (stroke list + velocities) → per-cell `note_on/note_off` sequence → fixed-length mono buffer $b_{v,m}[n]$ (section span × sr) → post FX chain (SP-009 reverb, SP-008 compression, SP-021/SP-053 placement). Zero-drift preserved: fixed buffer lengths, seeded determinism.

## 6. Pitfalls

1. Gate saturation at $N \ge 1024$ (little rocks = 1600 fires every sample) — rescale/multi-draw.
2. Sample-rate dependence of gate constant and bandwidths — rescale by $f_s/44100$.
3. $G = \ln(N)G_{\mathrm{base}}/N$ collapse at huge $N$ — master-gain by $1/\lambda$.
4. Long-ringing resonators ($r \ge 0.999$): energy accumulation/clipping — soft limit or lower $r$.
5. `rand()` global state breaks reproducibility — per-voice seeded RNGs.
6. `note_off` zeroes $E$ instantly — can truncate gestures; use CC4 decay for natural stops.
7. STK MIDI-note→instrument kludge — use explicit names in the port.
8. Untuned spectral peaks read as faint "pitches" — avoid masking with tonal voices (SP-007 check).
9. Velocity compression ($E{+}=0.1\cdot\text{amp}$) — nonlinear velocity mapping for dynamics.
10. High $f_i$ near Nyquist (9800 Hz sleighbells @ 44.1 kHz) — keep $f_i < 0.45 f_s$.

---

*References: [1] Cook 1997 CMJ 21(3):38–49, DOI 10.2307/3681012 · [2] Cook 1996 ICMC · [3] Cook & Scavone, STK `Shakers` (verified source) · [4] Cook 2002, Real Sound Synthesis · [5] Van den Doel & Pai 1998, ICAD.*
