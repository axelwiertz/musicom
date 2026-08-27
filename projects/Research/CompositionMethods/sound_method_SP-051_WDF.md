# Wave Digital Filters (WDF) Virtual Analog Circuit Modeling (Method SP-051)

## Extended Technical Reference

### 1. Full Mathematical Framework

#### Wave Variable Transformation

For a port with reference resistance $R_p$, voltage $v$, current $i$:

$$a = v + R_p\, i \quad \text{(incident wave)}$$
$$b = v - R_p\, i \quad \text{(reflected wave)}$$

Inverse:
$$v = \frac{a + b}{2}, \qquad i = \frac{a - b}{2R_p}$$

The reference resistance $R_p$ is a free parameter per port, chosen to make each element's wave relation maximally simple.

#### Linear One-Port Elements

| Element | Constitutive Law | Choose $R_p$ | Wave Relation |
|---|---|---|---|
| Resistor $R$ | $v = R\,i$ | $R_p = R$ | $b = 0$ (absorbed) |
| Capacitor $C$ | $i = C\,dv/dt$ | $R_p = T/(2C)$ | $b(n) = -a(n-1)$ |
| Inductor $L$ | $v = L\,di/dt$ | $R_p = 2L/T$ | $b(n) = a(n-1)$ |
| Open circuit | $i = 0$ | any | $b = a$ |
| Short circuit | $v = 0$ | any | $b = -a$ |
| Voltage source $E$ (series $R_s$) | $v = E - R_s\,i$ | $R_p = R_s$ | $b = 2E - a$ |
| Current source $I_0$ (parallel $G_p$) | $i = I_0 - G_p\,v$ | $R_p = 1/G_p$ | $b = 2R_p I_0 + a$ |

Capacitor and inductor relations derive from applying the bilinear (trapezoidal) transform to their constitutive ODEs.

#### Adaptor Scattering

**$N$-port series adaptor** (KVL: same current, voltages sum to zero):

$$b_j = a_j - \gamma_j \sum_{k=1}^{N} a_k, \qquad \gamma_j = \frac{2R_j}{\sum_{k=1}^{N} R_k}$$

**$N$-port parallel adaptor** (KCL: same voltage, currents sum to zero):

$$b_j = \left(\sum_{k=1}^{N} \gamma_k\, a_k\right) - a_j, \qquad \gamma_k = \frac{2G_k}{\sum_{m=1}^{N} G_m}, \quad G_k = \frac{1}{R_k}$$

In both cases $\sum_j \gamma_j = 2$, guaranteeing the scattering matrix is orthogonal (lossless). The adaptor cannot generate energy.

#### Nonlinear Elements: Reflection-Free Adaptor

A nonlinear one-port (diode, triode grid) attached directly to an adaptor creates a delay-free loop. The R-type adaptor eliminates this by setting the nonlinear port's incident wave to zero and presenting the element with a resistive Thévenin equivalent:

$$V_{th} = \text{linear combination of other ports' incident waves}$$
$$R_{th} = \text{equivalent resistance seen from the nonlinear port}$$

The implicit equation to solve:

$$f(v) = v + R_{th}\, i(v) - V_{th} = 0$$

**Shockley diode**: $i(v) = I_s\left(e^{v/V_T} - 1\right)$

Newton–Raphson iteration:
$$v \leftarrow v - \frac{f(v)}{f'(v)}, \qquad f'(v) = 1 + R_{th}\, \frac{I_s}{V_T} e^{v/V_T}$$

Initial guess: previous sample's voltage (warm start). 3–8 iterations suffice.

**Koren triode** (for tube amp modeling):
$$i_p = G_k \cdot \left(\frac{1}{\mu} \ln\left(1 + e^{\mu(V_g + V_{pk}/\sqrt{k_p + V_{pk}^2}}\right)\right)^{3/2}$$

Parameters: $\mu$ (amplification factor), $G_k$ (transconductance gain), $k_p$ (knee sharpness), $V_{pk}$ (plate-cathode voltage). Solved via Newton–Raphson in the same framework.

### 2. Bilinear Frequency Warping

The bilinear transform maps analog frequency $\omega_a$ to digital frequency $\omega_d$:

$$\omega_d = \frac{2}{T} \arctan\left(\frac{\omega_a T}{2}\right)$$

To match a target analog frequency $f_c$:

$$C_{warped} = \frac{C}{\tan(\pi f_c T)}, \qquad L_{warped} = L \cdot \tan(\pi f_c T)$$

### 3. Passivity and Stability

Each wave-domain element is passive: the reflected wave power never exceeds the incident wave power. Adaptors are lossless scattering matrices. Therefore:

**Theorem** (Fettweis 1971): A WDF network derived from a passive analog reference circuit is unconditionally stable for any sampling rate, regardless of element values.

This is the key advantage over direct discretization of analog circuits, which can be unstable at high gains or with certain topologies.

### 4. Python/NumPy Implementation Sketch

```python
import numpy as np

class Capacitor:
    """Capacitor C as wave one-port: b(n) = -a(n-1), Rp = T/(2C)."""
    def __init__(self, C, fs):
        self.Rp = 1.0 / (2.0 * C * fs)
        self.state = 0.0
    def reflect(self, a):
        b = -self.state
        self.state = a
        return b

class Inductor:
    """Inductor L as wave one-port: b(n) = a(n-1), Rp = 2L/T."""
    def __init__(self, L, fs):
        self.Rp = 2.0 * L * fs
        self.state = 0.0
    def reflect(self, a):
        self.state = a
        return self.state  # b(n) = a(n-1)

class Resistor:
    """Resistor R: b = 0 when Rp = R (absorbed into adaptor)."""
    def __init__(self, R):
        self.Rp = R

class Diode:
    """Shockley diode as nonlinear one-port."""
    def __init__(self, Is=2.52e-9, Vt=25.85e-3):
        self.Is, self.Vt = Is, Vt
    def current(self, v):
        return self.Is * (np.exp(np.clip(v / self.Vt, -50, 50)) - 1.0)
    def solve(self, Vth, Rth, iters=8):
        v = 0.0  # initial guess
        for _ in range(iters):
            ev = np.exp(np.clip(v / self.Vt, -50, 50))
            f = v + Rth * self.Is * (ev - 1.0) - Vth
            fp = 1.0 + Rth * self.Is / self.Vt * ev
            v -= f / fp
        return v

class SeriesAdaptor:
    """N-port series adaptor (KVL)."""
    def __init__(self, R_ports):
        self.R = np.asarray(R_ports, dtype=float)
        self.gamma = 2.0 * self.R / self.R.sum()
    def scatter(self, a):
        a = np.asarray(a, dtype=float)
        return a - self.gamma * a.sum()

class ParallelAdaptor:
    """N-port parallel adaptor (KCL)."""
    def __init__(self, R_ports):
        self.R = np.asarray(R_ports, dtype=float)
        G = 1.0 / self.R
        self.gamma = 2.0 * G / G.sum()
    def scatter(self, a):
        a = np.asarray(a, dtype=float)
        return self.gamma.dot(a) - a

def wdf_diode_clipper(x, fs, Rs=1e3, R1=1e3, C1=1e-6,
                      Is=2.52e-9, Vt=25.85e-3):
    """WDF diode clipper: source(Rs) -- R1 -- node -- (C1 || diode)."""
    cap = Capacitor(C1, fs)
    dio = Diode(Is, Vt)
    Rth = Rs * R1 / (Rs + R1)
    y = np.zeros_like(x)
    for n in range(len(x)):
        Vth = x[n] * R1 / (Rs + R1)
        v_node = dio.solve(Vth, Rth)
        # capacitor update
        a_cap_in = v_node
        cap.reflect(a_cap_in)
        y[n] = v_node
    return y
```

### 5. Extended Circuit Examples

**Diode clipper** (fuzz pedal): source → series R → node → (C || diode). Produces hard asymmetric clipping.

**Tube preamp** (triode stage): source → coupling C → grid → triode → plate load R → output C. Produces warm even-harmonic saturation.

**Ladder filter** (Moog-style): cascade of 4 RC lowpass stages with feedback. Produces resonant 24 dB/octave filtering.

**Diode-bridge compressor**: sidechain detector (diode + C) controls a diode-bridge VCA. Produces pumping compression artifacts.

### 6. References

- Fettweis, A. (1971). "Digital filter structures related to classical filter networks." *AEÜ* 25, pp. 79–89.
- Fettweis, A. (1986). "Wave digital filters: Theory and practice." *Proc. IEEE* 74(2), pp. 270–327.
- Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing.
- Karjalainen, M., and Pakarinen, J. (2006). "Wave digital simulation of a vacuum-tube amplifier." *Proc. ICASSP 2006*.
- Yeh, D. T., Abel, J. S., and Smith, J. O. (2008). "Simulating guitar distortion circuits using wave digital and nonlinear state-space formulations." *Proc. DAFx-08*.
- De Sanctis, G., and Sarti, A. (2010). "Virtual analog modeling in the wave-digital domain." *IEEE Trans. Audio, Speech, Language Process.* 18(4), pp. 715–727.
- Werner, K. J., Bernardini, A., and Smith, J. O. (2016). "An improved and generalized diode clipper model for wave digital filters." *Proc. DAFx-16*.
- Werner, K. J., et al. (2014). "Resolving wave digital filters with nonlinear multiport elements." *Proc. DAFx-14*.
