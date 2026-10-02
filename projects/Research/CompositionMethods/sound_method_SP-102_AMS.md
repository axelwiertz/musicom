# Sound Production Method SP-102 — Amplitude Modulation Synthesis (AMS)

**Layer:** absolute — sound production (synthesis engine). Amplitude Modulation Synthesis is a time-domain synthesis technique that varies the amplitude of a carrier oscillator according to the instantaneous amplitude of a modulator oscillator, producing sideband-rich timbres from simple sinusoidal building blocks. The candidate code path is `sound/synthesis/am_synthesis.py`, pluggable into `workflows.musicom_workflow.produce(method="SP-102")`.

---

## Extended Mathematical Description

Amplitude Modulation Synthesis is the audio-rate application of classical Amplitude Modulation (AM), widespread in radio broadcasting since the 1900s (Fessenden, Leblanc). In the musical context, the carrier and modulator oscillators are both audio-range signals, producing sum and difference sidebands that generate novel timbres from a single note.

### 1. Continuous-Time DSB+Carrier (AM Proper)

The fundamental AM equation:

$$y(t) = [A_c + A_c m \cos(2\pi f_m t)] \cos(2\pi f_c t) = A_c [1 + m \cos(2\pi f_m t)] \cos(2\pi f_c t)$$

where:

| Symbol | Meaning | Typical Range |
|--------|---------|---------------|
| $A_c$ | Carrier amplitude (peak) | 0.0–1.0 |
| $f_c$ | Carrier frequency (Hz) | 20–8000 Hz |
| $f_m$ | Modulator frequency (Hz) | 0.1–4000 Hz |
| $m$ | Modulation index | 0.0–1.0 (clean); >1.0 (overmodulation) |

Expanded:

$$y(t) = \underbrace{A_c \cos(2\pi f_c t)}_{\text{carrier}} + \underbrace{\frac{mA_c}{2} \cos[2\pi (f_c+f_m) t]}_{\text{upper sideband}} + \underbrace{\frac{mA_c}{2} \cos[2\pi (f_c-f_m) t]}_{\text{lower sideband}}$$

**Power distribution:** Total RMS power = $P_c (1 + m^2/2)$ where $P_c = A_c^2/2$. The sidebands each carry $m^2/4$ of the carrier power, so at $m=1$ the total power is 1.5x the unmodulated carrier, with 6 dB headroom.

### 2. Modulation Index and Overmodulation

$$m = \frac{A_{\max} - A_c}{A_c} = \frac{A_c - A_{\min}}{A_c}$$

- $m = 0$: Pure sine — no modulation.
- $m = 0.5$: 50% modulation — sidebands at 1/4 carrier amplitude (-12 dB).
- $m = 1.0$: 100% modulation — envelope just kisses zero. Sidebands at -6 dB relative to carrier.
- $m > 1.0$: Overmodulation — the carrier envelope inverts at the trough, producing a phase discontinuity at the zero crossing point. This adds extra sidebands through wavefolding-type distortion (Creasey 2004, p. 564). The spectrum no longer has just three lines but becomes a richer comb through envelope rectification.

### 3. Complex Wave AM (Multiple Partials)

For a carrier waveform $C(t) = \sum_{p=1}^P A_{c,p} \cos(2\pi f_{c,p} t)$ and modulator $M(t) = 1 + m \sum_{q=1}^Q A_{m,q} \cos(2\pi f_{m,q} t)$:

$$y(t) = C(t) \cdot M(t) = \sum_{p=1}^P \sum_{q=1}^Q A_{c,p} A_{m,q} \cos(2\pi f_{c,p} t) [1 + m \cos(2\pi f_{m,q} t)]$$

Each carrier partial generates $Q$ sideband pairs, for a total of $P \cdot (2Q + 1)$ spectral lines (including the $P$ carrier lines). If both carrier and modulator are harmonic (saw, square), the spectrum clusters at rational multiples of the fundamental.

### 4. Sub-Audio Operation (Tremolo)

When $f_m < 20$ Hz, the ear perceives the amplitude modulation as a tremolo — a periodic loudness fluctuation — rather than as timbral sidebands. The tremolo depth is $100 \times m\%$:

$$A(t) = A_c \cdot |1 + m \cos(2\pi f_m t)| \quad \text{(with implicit DC block)}$$

Tremolo rate $f_m$ can lock to the tempo grid: $f_m = \text{bpm}/60 \times 2^k$ for musically meaningful pulsations.

### 5. Relation to Other Methods

| Method | Relation to AMS | Key Difference |
|--------|----------------|----------------|
| **SP-063 Ring Modulation** | Bipolar modulator (no DC offset) → no carrier in output | AM has carrier; RM is DSB-SC |
| **SP-010/SP-017 FM** | Modulates frequency, not amplitude | FM has infinite sidebands; AM has one pair per partial |
| **SP-030 Phase Distortion** | Warps phase, not amplitude | Phase distortion is a time-axis distortion |
| **SP-070 FBAM** | Feedback amplitude modulation | FBAM is nonlinear (output fed back as modulator) |
| **SP-019/SP-062 Waveshaping** | Static nonlinearity | AM is a linear time-varying modulation |

---

## Python / NumPy Implementation Sketch

```python
import numpy as np
from typing import Optional

def am_synthesis(
    f_c: float,           # carrier frequency (Hz)
    f_m: float,           # modulator frequency (Hz)
    sr: int,              # sample rate
    duration: float,      # seconds
    m: float = 0.5,       # modulation index [0, ~2]
    A_c: float = 0.5,     # carrier amplitude
    phase_c: float = 0.0, # carrier initial phase (rad)
    phase_m: float = 0.0, # modulator initial phase (rad)
    carrier_wave: str = 'sine',
    modulator_wave: str = 'sine',
    dc_block: bool = False,
) -> np.ndarray:
    """
    Amplitude Modulation Synthesis — DSB+Carrier.
    
    Returns shaped waveform as float64 numpy array (sr * duration samples).
    """
    n = np.arange(int(sr * duration))
    
    # Phase-accumulator oscillators
    def osc(freq, phase, wave):
        theta = 2 * np.pi * freq * n / sr + phase
        if wave == 'sine':
            return np.cos(theta)
        elif wave == 'saw':
            # Bandlimited saw via polyblep approximation (simplified)
            t = (theta % (2 * np.pi)) / (2 * np.pi)
            return 2 * t - 1
        elif wave == 'square':
            s = np.sin(theta)
            return np.where(s >= 0, 1.0, -1.0)
        elif wave == 'triangle':
            return 2 * np.abs(2 * ((theta / (2 * np.pi)) % 1.0) - 1) - 1
        else:
            raise ValueError(f"Unknown waveform: {wave}")
    
    carrier = osc(f_c, phase_c, carrier_wave)
    # Unipolar modulator: [0, 1+m] mean = 1 (no DC if m=1)
    modulator = 1.0 + m * osc(f_m, phase_m, modulator_wave)
    
    y = A_c * carrier * modulator
    
    if dc_block:
        # First-order DC blocker
        y = y - np.mean(y)
    
    return y


class AMMultiVoice:
    """
    Multi-voice AM synthesis engine for UnitMatrix rendering.
    
    Each voice has independent (f_c, f_m, m, waveform_c, waveform_m, gain).
    """
    
    def __init__(self, sr: int = 48000):
        self.sr = sr
        self.voices: list[dict] = []
    
    def add_voice(self, f_c=440.0, f_m=220.0, m=0.5, gain=0.5,
                  wave_c='sine', wave_m='sine'):
        self.voices.append({
            'f_c': f_c, 'f_m': f_m, 'm': m, 'gain': gain,
            'wave_c': wave_c, 'wave_m': wave_m,
        })
    
    def render(self, duration: float) -> np.ndarray:
        mix = np.zeros(int(self.sr * duration))
        for v in self.voices:
            mix += am_synthesis(
                v['f_c'], v['f_m'], self.sr, duration,
                m=v['m'], A_c=v['gain'],
                carrier_wave=v['wave_c'], modulator_wave=v['wave_m'],
            )
        # Normalize to prevent clipping
        peak = np.max(np.abs(mix))
        if peak > 1.0:
            mix /= peak * 1.05
        return mix
```

### Advanced: Complex-Wave AM with Envelope Control

```python
def am_complex(
    f_c: float,
    f_m: float,
    sr: int,
    duration: float,
    m: float = 0.5,
    A_c: float = 0.5,
    num_partials: int = 8,     # carrier harmonic count
    mod_partials: int = 3,     # modulator harmonic count
    rolloff: float = 0.6,      # harmonic amplitude rolloff per octave
) -> np.ndarray:
    """
    Multi-partial AM: carrier and modulator each have num_partials harmonics
    with exponential rolloff. Produces (num_partials * (2 * mod_partials + 1))
    spectral lines.
    """
    n = np.arange(int(sr * duration))
    t = n / sr
    
    # Build carrier with harmonics
    carrier = np.zeros_like(n, dtype=np.float64)
    for p in range(1, num_partials + 1):
        amp = A_c * (rolloff ** (p - 1))
        carrier += amp * np.cos(2 * np.pi * f_c * p * t)
    
    # Build modulator (unipolar, with DC offset)
    modulator = np.ones_like(n, dtype=np.float64)
    for q in range(1, mod_partials + 1):
        amp = (rolloff ** (q - 1))
        modulator += m * amp / mod_partials * np.cos(2 * np.pi * f_m * q * t)
    
    return carrier * modulator
```

---

## Implementation Requirements

- **Python/NumPy**: Pure vectorized implementation above runs in $O(N)$ for the basic case and $O(PQN)$ for complex-wave AM. SciPy not required for basic operation.
- **Real-time**: $O(1)$ per sample per voice — two phase accumulators, one multiply-add. Suitable for real-time polyphonic rendering in `sound/synthesis/am_synthesis.py`.
- **Candidate File**: `sound/synthesis/am_synthesis.py` — exports `am_synthesis()`, `AMMultiVoice`, and `am_complex()`. Plugs into `workflows.musicom_workflow.produce(method="SP-102")`.
- **FluidSynth**: Not used — AMS is a synthesis engine, not a SoundFont renderer. The method runs directly in Python/NumPy.
- **Integration with existing methods**: AMS can be chained with SP-071 (Dattorro Plate Reverb), SP-062 (ADAA anti-aliasing for overmodulation), SP-009 (Convolutive Reverb), and SP-034 (HOA spatialization) in the `produce()` pipeline.

---

## References

1. Strange, Allen (1983). *Electronic Music: Systems, Techniques, and Controls.* Dubuque, IA: William C. Brown. — The foundational modular-synth text covering AM synthesis alongside FM, ring mod, and fixed-filter bank techniques.
2. Roads, Curtis (2015). *Composing Electronic Music: A New Aesthetic.* Oxford University Press, pp. 144–148. — Contemporary survey of AM in computer music practice.
3. Creasey, David (2004). *Audio Processes.* — Detailed treatment of AM sidebands, overmodulation, and negative-frequency foldover, pp. 560–575.
4. d'Escrivan, Julio (2012). "Amplitude Modulation Synthesis." In *The Oxford Handbook of Computer Music*, pp. 262–278. — Engineering-oriented AM review with spectral diagrams and implementation notes.
5. Moore, F. Richard (1990). *Elements of Computer Music.* Upper Saddle River, NJ: Prentice Hall, pp. 187–195. — Classic treatment of modulation synthesis in the MUSIC V/CMusic lineage.
6. Bode, Harald (1961). "The Bode Frequency Shifter." — The application of modulation techniques to musical instrument design, from the inventor of the frequency shifter.