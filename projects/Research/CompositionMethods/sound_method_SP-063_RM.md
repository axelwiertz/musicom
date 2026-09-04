# Ring Modulation (Balanced Modulator) Synthesis — Method SP-063

**ID:** SP-063 · **Acronym:** RM · **Layer:** Synthesis Engines (absolute — sound production)
**Target output:** Metallic / Clangorous Bell, Gong & Robotic-Vocal Timbres

## One-line description
Multiplies a modulator signal $x[n]$ by an audio-rate carrier $m[n]=\sin(2\pi f_c n/f_s)$ (four-quadrant balanced multiplier), producing only the sum-and-difference sidebands $f_c \pm f_i$ while suppressing both carrier and modulator. N modulator partials → 2N sidebands; the ratio $r=f_c/f_m$ selects harmonic (integer, consonant) vs inharmonic (irrational, metallic) output; difference sideband folds through 0 Hz. The double-sideband parent of SP-055 FSHT and the audio-rate cousin of AM tremolo; $O(1)$ per sample.

## Source
- Stockhausen, K. (1964/1970/1971). *Mixtur*, *Mantra*, *Telemusik* — scores and *Texte zur Musik*.
- Bode, H. (1961). Ring modulator / frequency shifter patents and instruments.
- Chapman, J. (1981). "On the Application of Ring Modulation to Electronic Music." *Interface* 10(1).
- Roads, C. (1996). *The Computer Music Tutorial*, §6.8 (Amplitude Modulation). MIT Press.
- Analog Devices. *AD633 Low-Cost Analog Multiplier* datasheet (four-quadrant multiply).

## Core equations

**Four-quadrant multiply (discrete time):**
$$y[n] = x[n]\cdot m[n],\qquad m[n]=\sin(2\pi f_c\, n/f_s)$$

**Sine-carrier decomposition of one modulator partial:**
$$y(t) = A\cos(2\pi f_m t)\cos(2\pi f_c t) = \tfrac{A}{2}\Big[\cos\big(2\pi(f_c-f_m)t\big) + \cos\big(2\pi(f_c+f_m)t\big)\Big]$$

**General (N partials → 2N sidebands):**
$$y(t)=\sum_i \frac{A_i}{2}\Big[\cos\big((\omega_c-\omega_i)t-\phi_i\big)+\cos\big((\omega_c+\omega_i)t+\phi_i\big)\Big]$$

**AM recovery via DC bias** (ring mod → AM/tremolo): with $m(t)=1+\cos(\omega_c t)$ the carrier and both sidebands are all present; with a zero-mean carrier the carrier is suppressed (DSB-SC).

**Difference-sideband folding** (through DC): $\omega_c-\omega_i<0$ appears at $|\omega_c-\omega_i|$, mirroring the spectrum around 0 Hz.

## Implementation (NumPy)

```python
import numpy as np

def ring_mod(x, f_c, sr, carrier="sine", mix=1.0):
    """Multiply modulator buffer x by a band-limited carrier at f_c.

    Returns y = mix * (x * m) + (1-mix) * x   (parallel dry/wet).
    """
    n = np.arange(len(x))
    if carrier == "sine":
        m = np.sin(2*np.pi*f_c*n/sr)
    elif carrier == "square":
        # PolyBLEP-band-limited square (cf. SP-029); correction elided.
        ph = np.mod(f_c*n/sr, 1.0)
        m = np.where(ph < 0.5, 1.0, -1.0)
    else:
        raise ValueError(carrier)
    m = m - m.mean()                      # zero-mean carrier: no DC leak (else -> AM)
    wet = x * m
    return mix*wet + (1.0-mix)*x

# Usage:
#   y = ring_mod(voice_audio, f_c=440.0, sr=44100, carrier="sine", mix=0.8)
# Integer-ratio carrier for tonal, irrational for metallic.
```

Candidate code path: `sound/synthesis/ring_mod.py` (new module alongside `phase_mod.py`, `west_coast.py`, `additive.py`).

## References
- Stockhausen, K. (1964/1970/1971). *Mixtur*, *Mantra*, *Telemusik* — scores and *Texte zur Musik*.
- Bode, H. (1961). Ring modulator / frequency shifter patents and instruments.
- Chapman, J. (1981). "On the Application of Ring Modulation to Electronic Music." *Interface* 10(1).
- Roads, C. (1996). *The Computer Music Tutorial*, §6.8. MIT Press.
- Analog Devices. *AD633 Low-Cost Analog Multiplier* datasheet.
- Puckette, M. (2007). *The Theory and Technique of Electronic Music*, §5 (Modulation). World Scientific.
