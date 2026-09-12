# SP-071 — Dattorro Plate Reverb (DPR)

**Layer:** absolute (sound production — post-processing / DSP)
**Category:** Post-Processing / DSP
**Target output:** Dense / Warm Algorithmic Plate Reverb Tail
**Complexity:** $O(1)$ per sample (≈11 multiplies + ~25 delay-line reads), deterministic per seed

---

## One-line description

Algorithmic plate reverberator in the style of the EMT 140 physical plate: four input all-pass lattice diffusers decorrelate the signal into a recirculating **figure-eight tank** (two cross-coupled delay-line loops, each with an in-loop one-pole HF-damping filter and two modulated all-pass diffusers), read out through seven ±0.6-weighted taps into a synthetic stereo image. Runs at Dattorro's nominal 29 761 Hz with all delays scaled by $f_s/29761$; slow LFO modulation smears the tank's static modes into a continuously shifting modal field. The dense, warm plate-class member between SP-009 (convolution IR), SP-032 (FDN) and SP-058 (spring reverb).

## Source

- **Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters." *JAES* 45(9), 660–684.** The canonical paper introducing the figure-eight plate topology.
- **Dattorro, J. (1997). "Effect Design, Part 2: Delay-Line Modulation and Chorus." *JAES* 45(10), 764–788.** The fractional-delay modulation used for the tank LFOs.
- **Dattorro, J. (2002). "Effect Design, Part 3: Oscillators and LFOs." *JAES* 51(3).**
- **Schroeder, M. R. (1962). "Natural Sounding Artificial Reverberation." *JAES* 10(3), 219–223.** The parallel-comb + series-allpass ancestor.
- **Griesinger, D. (1989). "Practical Processors and Programs for Digital Reverberation." *Proc. AES 7th Int. Conf.*** The Lexicon 224 plate-class ancestor Dattorro explicitly credits.
- **Valley Audio (2018). *Plateau* VCV Rack module** — the reference C++ re-implementation (coefficients verified against this file at the 29 761 Hz clock).

## Technical mechanics (extended)

### 1. All-pass lattice diffuser (atomic building block)

Each of the eight diffusers is a two-multiplier lattice; all-pass when its two coefficients are equal:

$$y[n] = -g\,x[n] + x[n-M] + g\,y[n-M] \quad\Longleftrightarrow\quad H(z)=\frac{-g + z^{-M}}{1 - g\,z^{-M}}$$

- $g=0$ → pure delay of $M$ samples.
- $|g|\to 1$ → impulse response is an up-sampled first-order all-pass: an exponentially-decaying spread, magnitude flat.
- $g<0$ → multiplies the impulse response by $(-1)^{n-M}$ each period (the "decay diffusion 1" character flip).

### 2. Input stage

mono sum (0.5× L + 0.5× R) → predelay $z^{-P}$ → one-pole low-pass (bandwidth $bw=0.9995$, cutoff ≈ 2 kHz @ 29 761 Hz) → 4 series input all-pass diffusers:

$$g = 0.75,\ 0.75,\ 0.625,\ 0.625 \qquad M = 142,\ 107,\ 379,\ 277\ \text{(samples @ 29761)}$$

### 3. Figure-eight tank

Two identical halves (left / right), each:

$$\underbrace{\text{AP1}(g{=}{-}0.70,\ M{=}672)}_{\text{decay diffusion 1}}
\to \underbrace{D_1}_{\substack{L{=}4453\\R{=}4217}}
\to \underbrace{\text{LP}(\text{damping})}_{\text{one-pole, }d{\approx}0.9995}
\to \underbrace{\text{AP2}(g{=}0.50,\ M{=}1800/2656)}_{\text{decay diffusion 2}}
\to \underbrace{D_2}_{\substack{L{=}3720\\R{=}3163}}$$

Cross-coupling (the figure-eight) closes the loop through the **decay** coefficient ($\text{decay}=0.5$ default):

$$\text{leftSum}[n] = \text{decay}\cdot D_{2,R}[n],\qquad \text{rightSum}[n] = \text{decay}\cdot D_{2,L}[n]$$

The incommensurate delay set $\{4453, 3720, 4217, 3163\}$ (≈100–150 ms) plus four modulated all-pass delays makes echo density climb fast enough to read as a smooth decay, not a loop.

### 4. Output taps (synthetic stereo from a mono tank)

$$Y_L = 0.6\big(t^{(L)}_1 + t^{(L)}_2 - t^{(L)}_3 + t^{(L)}_4 - t^{(L)}_5 - t^{(L)}_6 - t^{(L)}_7\big)$$
$$Y_R = 0.6\big(t^{(R)}_1 + t^{(R)}_2 - t^{(R)}_3 + t^{(R)}_4 - t^{(R)}_5 - t^{(R)}_6 - t^{(R)}_7\big)$$

Tap positions (samples @ 29 761 Hz, scale by $f_s/29761$), from the paper's Table 2:

| tap | left source | right source |
|---|---|---|
| 1 | $D_1$ @ 266 | $D_1$ @ 353 |
| 2 | $D_1$ @ 2974 | $D_1$ @ 3627 |
| 3 | $D_2$ @ 1913 | AP2 @ 1228 |
| 4 | $D_2$ @ 1996 | $D_2$ @ 2673 |
| 5 | $D_1$ @ 1990 | $D_1$ @ 2111 |
| 6 | AP2 @ 187 | AP2 @ 335 |
| 7 | AP2 @ 1066 | $D_2$ @ 121 |

(The Plateau re-implementation interleaves left/right delay lines for a slightly wider image; the principle — interleaved taps with alternating signs — is identical.)

### 5. Delay-line modulation

Two (or four, Plateau-style) slow LFOs modulate the tank all-pass delay lengths:

$$\text{delay}(n) = M + A\,\text{tri}\big(2\pi f_m n / f_s + \phi\big),\qquad f_m \in [0.10,\ 0.18]\ \text{Hz},\quad A \le 16\ \text{samples}$$

Fractional-delay interpolation (linear, or unity-gain first-order allpass — see SP-059) is required because the tap is non-integer. This injects an inaudible (< few cents) pitch undulation that smears the tank's static comb modes — the difference between a plate and a "picket fence."

### 6. Magnitude truncation & DC hygiene

Dattorro's fixed-point implementation uses **magnitude truncation** (truncate-toward-zero) on recursive-lattice writes to drive zero-input limit cycles to absolute silence (12–24 dB noise-floor gain). In float NumPy the limit-cycle issue disappears, but retain: a 20 Hz DC-block on input and output, an input HPF before the tank, and headroom (input gain 0.5) so the all-pass lattices do not clip internally.

## NumPy implementation sketch

```python
import numpy as np

# All delays/taps below are at Dattorro's nominal 29761 Hz clock.
# Scale by sr/29761 before use.

class AllpassLattice:
    """Two-multiplier lattice; allpass when the two coeffs are equal."""
    def __init__(self, M: int, g: float):
        self.buf = np.zeros(M)
        self.g = g
        self.idx = 0

    def tick(self, x: float) -> float:
        m = self.buf[self.idx]               # x[n-M]
        # two-multiplier lattice:
        #   store = x[n] + g * buf[idx];  y = -g*store + buf[idx]; buf[idx]=store
        store = x + self.g * m
        y = -self.g * store + m
        self.buf[self.idx] = store
        self.idx = (self.idx + 1) % len(self.buf)
        return y


class OnePoleLP:
    """y[n] = (1-a) x[n] + a y[n-1]  (a = pole ~ 0.9995 for damping)."""
    def __init__(self, a: float):
        self.a = a
        self.y1 = 0.0
    def tick(self, x: float) -> float:
        self.y1 = (1.0 - self.a) * x + self.a * self.y1
        return self.y1


class DattorroPlate:
    def __init__(self, sr: int = 44100):
        self.k = sr / 29761.0                       # Dattorro's scaling rule
        def s(n): return max(1, int(round(n * self.k)))
        # input stage
        self.predelay = np.zeros(s(4096))
        self.bw = OnePoleLP(0.9995)                 # bandwidth
        self.in_ap = [AllpassLattice(s(M), g) for M, g in
                      ((142, 0.75), (107, 0.75), (379, 0.625), (277, 0.625))]
        # tank (left / right)
        self.ap1 = [AllpassLattice(s(672), 0.70), AllpassLattice(s(908), 0.70)]
        self.d1  = [np.zeros(s(4453)), np.zeros(s(4217))]
        self.damp = [OnePoleLP(0.9995), OnePoleLP(0.9995)]
        self.ap2 = [AllpassLattice(s(1800), 0.50), AllpassLattice(s(2656), 0.50)]
        self.d2  = [np.zeros(s(3720)), np.zeros(s(3163))]
        self.i1 = self.i2 = [0, 0]
        self.decay = 0.5
        self.left_sum = self.right_sum = 0.0
        # output taps (paper Table 2, scaled)
        self.tapsL = [s(t) for t in (266, 2974, 1913, 1996, 1990, 187, 1066)]
        self.tapsR = [s(t) for t in (353, 3627, 1228, 2673, 2111, 335, 121)]

    def process(self, xL, xR):
        yL = np.zeros_like(xL); yR = np.zeros_like(xR)
        for n in range(len(xL)):
            # input: mono sum -> predelay -> bandwidth LP -> 4 input allpasses
            mono = 0.5 * (xL[n] + xR[n])
            pre = self.predelay[n % len(self.predelay)]
            self.predelay[n % len(self.predelay)] = self.bw.tick(mono)
            v = pre
            for ap in self.in_ap:
                v = ap.tick(v)
            tank_feed = v
            # figure-eight tank (full loop elided for clarity — see Dattorro
            # Fig. 1 ordering: ap1 -> d1 -> damp -> ap2 -> d2 -> cross-couple)
            # left_sum = decay * d2_R_prev; right_sum = decay * d2_L_prev
            out = (tank_feed, tank_feed)  # placeholder wet taps
            yL[n] = out[0]
            yR[n] = out[1]
        return yL, yR
```

The sketch above shows the building blocks; a complete, production-ready implementation follows Dattorro's Fig. 1 ordering exactly (input → 4 input all-passes → left tank → right tank → cross-couple → 7 taps → DC-block → 0.5× output gain), as in the Plateau reference.

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| **PITCH** | none added (LTI + slow LFO); LFO imparts < a few cents of undulation, inaudible as vibrato |
| **RHYTHM** | predelay = dry/reflection gap (tune to a subdivision); echo-density ramp = "attack" of the space; decay = onset ring length |
| **HARMONY** | damping + bandwidth low-pass re-tune perceived brightness (low damping = bright metallic, high = dark/warm); tank ~2 kHz cutoff reinforces fundamentals/low partials |
| **STRUCTURE** | per-section `(predelay, decay, diffusion, damping, freeze)` = macro-form; joins = parameter crossfade; freeze = infinite sustain drone |
| **TEXTURE** | instantaneous high-density reflections + smooth exponential decay, phase-randomized recirculation; diffusion = smeared vs discrete; tap weights = stereo width |

## UnitMatrix Integration

- **Rows (Voices)** = bus mode (all voices through one plate, shared tank glue) or per-voice mode (independent decay/damping/predelay per voice, summed or spatialized via SP-021/034/043).
- **Columns (Sections)** = `{STRUCTURE}` = the DPR parameter vector; crossfade across joins.
- **Cells (MusicUnit)** = `{RHYTHM}`→predelay subdivision, `{TEXTURE}`→diffusion/damping, `{HARMONY}`→damping re-voicing. DPR is render-stage: compose/validate the grid (zero-drift gate) exactly as usual, then `produce(method="SP-071")` runs each voice buffer through DPR before EQ/DRC/master.
- **Flow:** `compose` → `produce(method="SP-071")` → DPR render → sum voices → SP-007 EQ / SP-008 DRC → export WAV/OGG.

## Pitfalls (condensed)

1. **Sample-rate coupling** — scale every delay/tap by $f_s/29761$; never copy raw sample counts.
2. **All-pass lattice internal clipping** — float64 + input gain 0.5 + HPF/DC-block before the tank.
3. **Picket-fence modes** — modulate tank all-passes with slow LFOs (0.1–0.18 Hz, ±8–16 samples).
4. **Diffusion/decay interaction** — `decay diffusion 2 = decay + 0.15`, clamped to [0.25, 0.50]; keep $|g|<1.0$.
5. **Damping is a coefficient, not a cutoff** — `damping=0.0005` is a *pole* (low cutoff); `bandwidth=0.9995` is the opposite convention (full bandwidth).
6. **Freeze diverges** — DC-block I/O; crossfade freeze over ~100 ms; keep the tail bounded.
7. **Stereo collapse** — keep the input stereo path or run two detuned instances; the output taps are synthetic-stereo-from-mono.

## References

- Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters." *JAES* 45(9), 660–684.
- Dattorro, J. (1997). "Effect Design, Part 2: Delay-Line Modulation and Chorus." *JAES* 45(10), 764–788.
- Dattorro, J. (2002). "Effect Design, Part 3: Oscillators and LFOs." *JAES* 51(3).
- Schroeder, M. R. (1962). "Natural Sounding Artificial Reverberation." *JAES* 10(3), 219–223.
- Griesinger, D. (1989). "Practical Processors and Programs for Digital Reverberation." *Proc. AES 7th Int. Conf.*
- Valley Audio (2018). *Plateau* VCV Rack module — reference C++ re-implementation.
