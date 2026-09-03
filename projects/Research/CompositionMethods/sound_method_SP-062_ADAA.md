# Antiderivative Antialiasing for Nonlinear Waveshaping (ADAA) — Method SP-062

**ID:** SP-062 · **Acronym:** ADAA · **Layer:** Post-Processing / DSP (absolute — sound production)
**Target output:** Aliasing-Free Distortion / Saturation / Wavefolding

## One-line description
Anti-aliases an arbitrary memoryless (or stateful) waveshaper $y=f(x)$ without oversampling — the pointwise evaluation is replaced by the average of $f$ over each sample interval, computed as a divided difference of the antiderivative $F(x)=\int f(x)\,dx$ (1st-order linear-segment or 2nd-order quadratic-segment), removing inharmonic "digital grunge" at $\mathcal{O}(1)$ per sample.

## Source
- Parker, Zavalishin & Le Bivic (2016), "Reducing the Aliasing of Nonlinear Waveshaping Using Continuous-Time Convolution," *DAFx-16*, Brno.
- Bilbao, Esqueda, Parker & Välimäki (2017), "Antiderivative Antialiasing for Memoryless Nonlinearities," *IEEE Signal Processing Letters* 24(7), 1049–1053.
- Holters (2019), "Antiderivative Antialiasing for Stateful Systems," *DAFx-19*, Birmingham.
- Albertini, Bernardini & Sarti (2020), "Antiderivative Antialiasing in Nonlinear Wave Digital Filters," *DAFx-20*, Vienna.
- Chowdhury, *ADAA* plugin (BSD-3-Clause), https://github.com/jatinchowdhury18/ADAA.

## Core equations

**The aliasing problem.** A memoryless waveshaper $y=f(x)$ produces harmonics at $m f_0$; sampling folds those above $f_s/2$ into the baseband. Direct evaluation $y[n]=f(x[n])$ discards inter-sample behavior and commits the error.

**Continuous-time convolution.** The anti-aliased output is the box-kernel average over one sample interval:
$$y[n] = \frac{1}{T}\int_{t_{n-1}}^{t_n} f(x(t))\,dt$$

**First-order ADAA** (linear segment $x[n-1]\to x[n]$), by the Fundamental Theorem of Calculus:
$$y[n] = \frac{F(x[n]) - F(x[n-1])}{x[n]-x[n-1]},\qquad F(x)=\int_0^x f(u)\,du$$
with $y[n]=f(x[n])$ where $x[n]=x[n-1]$ (the $h\to0$ limit).

**Second-order ADAA** (quadratic through $x[n-2],x[n-1],x[n]$):
$$y[n] = \frac{2}{x[n]-x[n-2]}\left[\frac{F(x[n])-F(x[n-1])}{x[n]-x[n-1]} - \frac{F(x[n-1])-F(x[n-2])}{x[n-1]-x[n-2]}\right]$$

**Antiderivatives (closed form):**
- Hard clip $f=\operatorname{clip}(x,-1,1)$: $F(x)=\tfrac12 x^2$ for $|x|\le1$, else $x\cdot\operatorname{sgn}(x)-\tfrac12$.
- tanh: $F(x)=\ln\cosh x$; $F_2(x)=\tfrac12\operatorname{Li}_2(-e^{-2x})+\tfrac{x^2}{2}-x\ln 2$ (Taylor near $x=0$).
- Polynomial/Chebyshev (cf. SP-019): antiderivative by inspection.

## Implementation (NumPy)

```python
import numpy as np

def F_hard_clip(x):                          # F of clip(x,-1,1)
    return np.where(np.abs(x) <= 1.0, 0.5*x*x, x*np.sign(x) - 0.5)

def F_tanh(x):                               # F of tanh(x)
    return np.log(np.cosh(x))

def adaa1(x, F, f):
    """1st-order ADAA: anti-aliased y[n]=f(x[n])."""
    xp = np.concatenate(([x[0]], x[:-1]))
    num = F(x) - F(xp)
    den = x - xp
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(np.abs(den) > 1e-12, num/den, f(x))

def adaa2(x, F, f):
    """2nd-order ADAA: quadratic segment, flatter passband."""
    xp  = np.concatenate(([x[0]], x[:-1]))
    xpp = np.concatenate(([x[0], x[0]], x[:-2]))
    d1 = x - xp;  d2 = xp - xpp;  d3 = x - xpp
    g1 = (F(x)-F(xp)) / np.where(np.abs(d1) > 1e-12, d1, 1.0)
    g2 = (F(xp)-F(xpp)) / np.where(np.abs(d2) > 1e-12, d2, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(np.abs(d3) > 1e-12, 2.0*(g1-g2)/d3, f(x))

# Usage: shaped = adaa1(drive * voice_audio, F_hard_clip, lambda x: np.clip(x,-1,1))
```

Candidate code path: `sound/effects/adaa_waveshaper.py` (new module alongside `shimmer_reverb.py`, `bbd_chorus.py`, `tilt_eq.py`).

## References
- Parker, Zavalishin & Le Bivic (2016), *DAFx-16*, Brno.
- Bilbao, Esqueda, Parker & Välimäki (2017), *IEEE Signal Processing Letters* 24(7), 1049–1053.
- Holters (2019), *DAFx-19*, Birmingham.
- Albertini, Bernardini & Sarti (2020), *DAFx-20*, Vienna.
- Chowdhury, *ADAA* plugin, https://github.com/jatinchowdhury18/ADAA.
- Zavalishin, V. (2018), *The Art of VA Filter Design*, 2nd ed.
