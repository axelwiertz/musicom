# Air-Jet Labium (Flute) Physical Modeling (FLUE) — Method SP-066

**Layer:** absolute (sound production — Synthesis Engines / physical modeling)
**Acronym:** FLUE (Flue-pipe / Flute Labium Unsteady Excitation)
**Candidate code path:** `sound/synthesis/flute_jet.py` in `/opt/data/repos/musicom/sound/synthesis/`

---

## Overview

The flute and the organ flue pipe are the only common instruments sustained by a
**fluid-mechanical oscillator with no vibrating solid**. Mouth pressure pushes a thin
air jet out of a slit; the jet is unstable and flips across a sharp edge (the
*labium*), alternately pumping acoustic flow into and out of a resonant pipe. The pipe
drives the jet, the jet drives the pipe: a feedback loop whose "valve" is a fluid
instability (Kelvin–Helmholtz wave on the jet + edge-tone vortex shedding), not a reed,
lip, or string. FLUE models this loop so that symbolic `MusicUnit` note events render
to breathy, woodwind audio.

This is the missing fourth member of the physical-model exciter taxonomy already
documented in musicom: single reed (SP-023), bowed friction (SP-024), lip-reed/brass
(SP-065) — FLUE adds **air-jet/labium**.

---

## Physics

### 1. Jet formation (Bernoulli)

Mouth pressure $p_m$ accelerates air through the flue slit into a jet of velocity

$$v_j = C_v\sqrt{2p_m/\rho},$$

with air density $\rho\approx1.2\ \mathrm{kg/m^3}$ and vena-contracta coefficient
$C_v\approx0.6$. The jet half-width $b$ is set by the flue (slit) height.

### 2. Jet convection and transit delay

The transverse (side-to-side) disturbance of the jet is a wave that convects at the
*jet-wave velocity* $u_c\approx0.4\,v_j$ — a consequence of the jet's parabolic velocity
profile and the growing Kelvin–Helmholtz instability. For flue-to-labium distance $L_j$,
the transit delay is

$$\tau_j = \frac{L_j}{u_c} = \frac{L_j}{0.4\,v_j}.$$

Because $v_j$ grows with $p_m$, the delay **depends on blowing pressure** — a dynamic
delay line (see Pitfall 1).

### 3. Jet deflection (delay + low-pass)

The pipe's acoustic particle velocity $u_n$ at the flue exit deflects the jet. At the
labium the transverse displacement is a delayed, inertially-smoothed copy of $u_n$:

$$\eta_L(\omega) = G_j\, e^{-j\omega\tau_j}\, H_{LP}(j\omega)\, u_n(\omega),
\qquad G_j = \frac{L_j}{v_j}.$$

Discretely: a jet delay line of $D_j=\mathrm{round}(f_s\tau_j)$ samples followed by a
one-pole low-pass (jet inertia / wave spreading; pole $a_j\approx-0.7$).

### 4. Edge splitting (nonlinear saturation)

The labium splits the jet; the acoustic volume flow injected into the pipe saturates
because the jet cannot deflect farther than its own width:

$$Q_{ac}(t) = v_j\,b\cdot \mathrm{clip}\!\left(\frac{\eta_L(t)}{\eta_{\max}},\,-1,\,1\right).$$

The soft-clip is the **harmonic source**. Soft blowing keeps $\eta_L$ in the linear
region → few harmonics (dark, hollow). Hard blowing drives $\eta_L$ into saturation →
many harmonics (bright, edgy *forte*).

### 5. Bore resonator

A flute is a cylindrical tube open at both ends. With effective length $L_{eff}$
(physical length + finger-hole shortening + end corrections), the half-wave resonances are

$$f_n \approx \frac{(n+1)\,c}{2L_{eff}},\qquad n=0,1,2,\dots$$

The embouchure imposes the input impedance $Z_p(\omega)$; mouth pressure
$p = Z_p\,Q_{ac}$.

### 6. Regeneration condition

The loop (bore delay + jet delay + lip filter) sustains where loop gain ≥ 1 and total
loop phase $=2\pi n$. Harder blowing raises $v_j$ → shortens $\tau_j$ → the operating
frequency drifts; the jet-delay phase also makes overblown modes run slightly sharp —
the famous flute "octave stretch" the player corrects with embouchure.

### 7. Breath noise

Turbulence in the flue channel injects broadband noise (one-pole LP, cutoff ≈ 3–6 kHz)
with amplitude $\propto p_m$, present only while blowing. This is what separates a flute
from an organ.

---

## Waveguide realization (Cook / STK style)

A lean per-sample loop (the STK `Flute` layout):

- **bore delay line** — length $N=\mathrm{round}(f_s/f_n)$; fractional tuning via a
  first-order allpass.
- **open-end reflection filter** $R_\omega$ — one-pole low-pass with pole ≈ −0.98
  (end reflection rolls off highs).
- **jet delay line** — length $D_j$ (dynamic, see above).
- **jet filter** — one-pole LP, pole ≈ −0.7.
- **lip/embouchure filter** — one-pole LP, pole ≈ −0.97.
- **DC blocker** — one-pole high-pass ≈ 20 Hz (kills near-DC loop drift).
- **breath noise** — seeded RNG → one-pole LP → summed at the mouth.

**Cost:** $\mathcal{O}(1)$ per sample plus a few delay reads; vectorizable across
voices; deterministic per seed.

---

## NumPy implementation sketch

*Placeholder constants and couplings — exact coefficients come from Coltman (1968),
Fletcher (1976), Cook (1992), De la Cuadra (2005). This sketch demonstrates the loop
topology, not calibrated audio.*

```python
import numpy as np

def flute_jet(f0, dur, fs=44100, pm=1.0, breath=0.3, vib_depth=0.0,
              vib_rate=5.0, seed=0):
    """Jet-drive (Cook/STK-style) waveguide flute. Deterministic (seeded RNG)."""
    rng = np.random.default_rng(seed)
    n = int(dur * fs)

    # Bore: one half-wave traversal at f0 (open-open tube).
    N_bore = max(2, int(round(fs / f0)))
    bore = np.zeros(N_bore)

    # Jet delay: velocity from mouth pressure (Bernoulli), convection at 0.4*vj.
    vj = 0.6 * np.sqrt(2.0 * pm / 1.2)          # m/s, rho ~1.2 kg/m^3 (placeholder)
    Lj = 0.008                                  # flue -> labium ~8 mm
    Dj = max(1, int(round(fs * Lj / (0.4 * vj))))
    jetline = np.zeros(Dj)

    # One-pole filter poles (STK-style placeholder values).
    a_jet, a_lip, a_ref = -0.7, -0.97, -0.98
    jet_lp = lip_lp = dc = 0.0
    out = np.zeros(n)

    for i in range(n):
        t = i / fs
        p_env = pm * (1.0 + vib_depth * np.sin(2 * np.pi * vib_rate * t))

        # Breath noise (seeded; scaled by blowing pressure).
        noise = rng.normal() * breath * p_env

        # Jet read + inertia low-pass.
        j = jetline[0]
        jet_lp = a_jet * (jet_lp - j) + j

        # Edge split: soft-clip saturation (harmonic source).
        q = np.tanh(jet_lp)

        # Bore reflection loop: read mouth pressure, reflect at open end, inject jet.
        p = bore[0]
        lip_lp = a_lip * (lip_lp - p) + p
        bore = np.roll(bore, -1)
        bore[-1] = a_ref * lip_lp + q

        # Jet deflection driven by the bore's acoustic velocity at the mouth.
        jetline = np.roll(jetline, -1)
        jetline[-1] = 0.4 * lip_lp            # deflection source (placeholder coupling)

        # DC blocker on the output path.
        s = lip_lp + noise
        out[i] = s - dc
        dc += 0.995 * (out[i])                 # one-pole HP ~ 20-40 Hz

    return out / (np.max(np.abs(out)) + 1e-9)
```

### Musical Elements Framework mapping

| Element | Mechanism |
|---|---|
| PITCH | finger-hole state → $L_{eff}$ → $f_n$; embouchure selects/overblows mode (octave/12th); jet delay bends pitch sharp at high modes |
| RHYTHM | onset = $p_m$ ramp (tongue = $p_m$ interrupt); articulation = $p_m$ envelope; flutter-tongue = $p_m$ modulation ≈ 20 Hz |
| HARMONY | one voice = one jet+bore pair; chord = $N$ parallel instances; overblow = partial shift; breath-noise ratio changes chord blend |
| STRUCTURE | per-section fingering/embouchure schedule; dynamics via $p_m$; breath-noise level per section |
| TEXTURE | $p_m$ → brightness (edge saturation); breath-noise ratio → airy vs pure; vibrato = $p_m$/embouchure LFO |

### UnitMatrix integration

- **Rows (Voices)** = one FLUE instance per voice (flute 1/2, alto flute, piccolo);
  render independently, then sum (spatialize via SP-021/034/043).
- **Columns (Sections)** = per-section state in `{STRUCTURE}`: fingering
  (effective-length) schedule, overblow mode, section dynamic ($p_m$), breath level.
- **Cells (MusicUnit)** = `{PITCH}` → bore length + overblow flag; `{RHYTHM}` → $p_m$
  envelope; `{TEXTURE}` → velocity → $p_m$ peak → brightness + breath mix.
- **Flow:** note-event consumer → section buffer → mix → post-FX (SP-007/008/009/032).
  Deterministic; `validate()` zero-drift gate unaffected (audio layer, no MIDI).

---

## References

- Coltman, J. W. (1968). "Sounding mechanism of the flute and organ pipe." *J. Acoust. Soc. Am.* 44(4), 983–992.
- Fletcher, N. H. (1976). "Jet-drive mechanism in organ pipes." *J. Acoust. Soc. Am.* 60(2), 481–483.
- Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer, Ch. 16.
- Howe, M. S. (1975). "Contributions to the theory of aerodynamic sound, with application to excess jet noise and the theory of the flute." *J. Fluid Mech.* 71(4), 625–673.
- Cook, P. R. (1992). "A meta-wind-instrument physical model, and a meta-controller for real-time performance control." *Proc. ICMC* 1992, San Jose.
- Cook, P. R., & Scavone, G. P. (1999). *The Synthesis ToolKit (STK)* — `StkFlute`.
- Verge, M.-P., Fabre, B., Hirschberg, A., & Wijnands, A. P. J. (1994/97). "Jet formation and jet velocity fluctuations in a flue organ pipe." *J. Acoust. Soc. Am.* 95(2), 1119–1132; "Aeroacoustics of musical instruments." *Ann. Rev. Fluid Mech.*
- De la Cuadra, P. (2005). "The sound of oscillating air jets: physics, modeling and simulation in flute-like instruments." PhD thesis, Stanford University (CCRMA).
