# SP-068 — Bytebeat Synthesis (Integer-Expression Algorithmic Synthesis)

**Layer:** absolute (sound production)
**Category:** Synthesis Engines
**Target output:** Deterministic Chip / Glitch / Looping Timbre
**Complexity:** $\mathcal{O}(1)$ per sample, zero state, zero memory

---

## One-line description

Evaluate an integer expression $f(t)$ of a monotonic sample counter $t$ once per sample and take the low byte ($y = f(t)\ \&\ 255$) as the waveform — using only integer arithmetic and bitwise operators (shift, AND, XOR) — to synthesize deterministic, inherently-looping chip/glitch timbres with no oscillators, wavetables, or filters.

## Source

Ville-Matias Heikkilä (viznut), 2011 — "Discovering novel computer music techniques by exploring the space of short computer programs" (demoscene / pouet.net / countercomplex). The classic one-liner form `t*((t>>12|t>>8)&63&t>>4)` produces musical arpeggios/basslines from a single expression. Descends from the demoscene procedural-generation tradition; the pure integer-computation member of the synthesis family.

## Technical mechanics

1. **Per-sample eval:** $y[n] = f(t)\ \&\ 255$ with $t = n$ (or $t = n + \phi_0$). Center/scale: $x[n] = (y[n]-128)/128$.
2. **Ramp/saw pitch:** $f(t)=t\cdot K \Rightarrow$ period $T = 256/\gcd(K,256)$ samples, $f = f_s \cdot \gcd(K,256)/256$. Integer pitch lattice, NOT free.
3. **Octave:** `t>>s` slows counter by $2^s$ → pitch down $s$ octaves.
4. **Free pitch (accumulator):** $p \leftarrow p + \mathrm{inc}$; $\mathrm{inc}=\mathrm{round}(256\,f/f_s)$.
5. **Harmony:** additive terms $tA + tB$ = interval; `&`/`^` products = ring-mod sidebands.
6. **Rhythm/texture:** `(t>>s)&mask` = square gates; `t^(t>>s)` = glitch noise.
7. **Form:** high-bit term `t>>P` = section selector every $2^P$ samples.
8. **Band-limit:** oversample ×4–8 + windowed-sinc decimate, or inline one-pole LP.

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| PITCH | $K \to f_s\gcd(K,256)/256$, or phase increment; `t>>s` = octave |
| RHYTHM | `(t>>s)&mask` gates; XOR = percussion |
| HARMONY | additive terms = chord; AND/XOR = metallic |
| STRUCTURE | `t>>P` = macro section; $t \bmod P_{sec}$ = loop |
| TEXTURE | bit depth, XOR density, low-bit brightness |

## UnitMatrix Integration

- Rows (voices) = one additive term/expression per voice.
- Columns (sections) = per-section expression spec / constants; high-bit switch at boundary.
- Cells = PITCH→$K$/inc; RHYTHM→shift/mask; HARMONY→term constants; TEXTURE→bit-depth+velocity.
- Flow: derive expression → vectorized eval → `&255` → center → oversample+LP → mix → post-FX.

## Python/NumPy sketch

```python
import numpy as np

def bytebeat(expr, seconds, sr=44100, oversample=4, bit=8):
    """expr: callable(t_array)->int array. Renders centered, band-limited mono."""
    rsr = sr * oversample
    t = np.arange(int(seconds * rsr), dtype=np.uint32)
    y = expr(t) & ((1 << bit) - 1)               # unsigned byte(s)
    x = (y.astype(np.float64) - (1 << (bit-1))) / (1 << (bit-1))
    # simple windowed-sinc decimation by R
    R = oversample
    from numpy import sinc, hamming
    taps = 32*R
    h = np.sinc(np.linspace(-taps//2, taps//2, taps)/R) * np.hamming(taps)
    h /= h.sum()
    xf = np.convolve(x, h, mode='valid')[::R]
    return xf

# classic viznut line, generalized:
def expr(t):
    return t * ((t >> 12 | t >> 8) & 63 & (t >> 4))

# pitched saw via accumulator at 220 Hz:
def saw_220(t, sr):
    inc = round(256 * 220 / sr)
    return (t * inc)

x = bytebeat(lambda t: t * ((t>>12 | t>>8) & 63 & (t>>4)), seconds=2.0)
```

## Pitfalls

1. Aliasing → oversample+decimate.
2. Unsigned DC → subtract center, DC-block.
3. Integer pitch grid → accumulator for exact pitch.
4. Loop/bar misalignment → $t \bmod P_{sec}$ or snap $K$.
5. 8-bit crunch vs 16-bit headroom → `& 65535` for clean.
6. Expression-search explosion → constrain grammar.
7. Overflow/width dependence → uint32 + explicit mask.
8. Under-used as dense layer → use AS continuous fill under sparse 011/032.

## References

- Heikkilä, V.-M. (2011). "Discovering novel computer music techniques by exploring the space of short computer programs."
- Heikkilä, V.-M. (2011). "The bytebeat — sound synthesis with a single line of code."
- Bytebeat web players: crasno.ca, thebytebeat.com; pouet.net threads.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley.
- Smith, J. O. (2010). *Physical Audio Signal Processing*. CCRMA.
