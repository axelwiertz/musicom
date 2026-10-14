# Method 115 — Keplerian Orbital Resonance Composition (KORC)

**ID:** 115 · **Paradigm:** Nature-Led · **Layer:** concrete · **Registered:** 2026-10-14

**One-line:** Each UnitMatrix voice becomes a planet on an elliptical orbit — Kepler's three laws generate pitch contour (1st law ellipse), rubato onsets (2nd law equal-areas time law), register/scale (3rd law P²∝a³), and harmony/macro-form (mean-motion resonances: 2:1, 3:2, Laplace 4:2:1) — reproducing Kepler's 1619 *Harmonice Mundi* interval table as direct physics.

---

## 1. The mathematics: Kepler's three laws as musical operators

### 1.1 Kepler's first law — the orbit is an ellipse

A body on a bound Keplerian orbit (star at one focus) has radial distance as a function of true anomaly ν (angle from perihelion):

$$r(\nu) = \frac{a\,(1-e^2)}{1 + e\cos\nu}$$

- $a$ = semi-major axis (mean orbital size), $e$ = eccentricity ($0 \le e < 1$), $\nu$ = true anomaly.
- $r_{\min} = a(1-e)$ at perihelion (ν=0); $r_{\max} = a(1+e)$ at aphelion (ν=π).

**Musical operator:** pitch contour. Sampling $N$ evenly spaced true anomalies per orbit and mapping $r(\nu_k)$ to pitch produces a contour that *descends toward perihelion and ascends toward aphelion* (or inverted), with amplitude governed by $e$: circular orbit ($e=0$) gives a flat contour, high eccentricity a deep one. The ellipse is the melodic shape.

### 1.2 Kepler's second law — equal areas in equal times (the time law)

The radius vector sweeps equal areas in equal times, so angular velocity is not constant:

$$\frac{\mathrm{d}\nu}{\mathrm{d}t} = \frac{h}{r(\nu)^2}, \qquad h = \frac{2\pi a^2\sqrt{1-e^2}}{P}$$

where $P$ = orbital period. The body rushes at perihelion and lingers at aphelion. Integrating gives the exact time at which the body reaches true anomaly ν:

$$t(\nu) = \frac{P}{2\pi}\,M(\nu), \qquad M = E - e\sin E, \qquad \tan\frac{E}{2} = \sqrt{\frac{1-e}{1+e}}\,\tan\frac{\nu}{2}$$

($M$ = mean anomaly — the "clock" angle that advances uniformly; $E$ = eccentric anomaly; the equation $M = E - e\sin E$ is *Kepler's equation*).

**Musical operator:** rhythmic rubato, exact and closed-form. Generate events at $\nu_k = 2\pi k/N$ ($k=1..N$), solve $E_k$ from ν_k (one arctan + no iteration needed in this direction), get $M_k$, and read the onset time $t_k$. The inter-onset interval as a function of position:

$$\Delta t(\nu) \propto \frac{\mathrm{d}t}{\mathrm{d}\nu} \propto r(\nu)^2 \propto \frac{1}{(1+e\cos\nu)^2}$$

So onsets *crowd at perihelion* ($\nu=0$, shortest $\Delta t$) and *spread at aphelion* ($\nu=\pi$, longest), with the extreme ratio

$$\frac{\Delta t_{\max}}{\Delta t_{\min}} = \left(\frac{1+e}{1-e}\right)^2$$

This is exactly Kepler's own musical quantity: the ratio of maximum to minimum *angular velocity* (velocities are inversely proportional to $\Delta t$), which he tabulated as each planet's interval in *Harmonice Mundi* Book V (1619):

| Planet | e (modern) | ((1+e)/(1−e))² | Nearest just ratio | Kepler's interval |
|---|---|---|---|---|
| Venus   | 0.007  | 1.028 | 25:24 (=1.0417, diesis) | diesis 24:25 |
| Earth   | 0.017  | 1.071 | 16:15 (=1.0667, semitone) | semitone, mi–fa |
| Jupiter | 0.048  | 1.213 | 6:5 (=1.2, minor third) | minor third 5:6 |
| Saturn  | 0.054  | 1.242 | 5:4 (=1.25, major third) | major third 4:5 |
| Mars    | 0.093  | 1.455 | 3:2 (=1.5, fifth) | fifth 2:3 |
| Mercury | 0.206  | 2.303 | 9:4 (octave + major second) | — |

All within one diesis of the pure ratios, exactly as Kepler discovered (Walker 1964; Groves; IEEE Pulse). **KORC reproduces the historical table as physics, then composes with it**: eccentricity $e$ becomes the *rubato dial* AND the *interval-size dial* simultaneously — a conceptually elegant unification of rhythm and harmony from one parameter.

### 1.3 Kepler's third law — P² ∝ a³ (the scale generator)

$$P = 2\pi\sqrt{\frac{a^3}{GM}} \quad\Rightarrow\quad \log_2 P = \tfrac{3}{2}\log_2 a + \text{const}$$

Kepler's own sesquialtera phrasing: *the ratio of any two planets' periodic times is precisely the 3:2 power of the ratio of their mean distances* (*Harmonice Mundi* p. 189).

**Musical operator:** register and scale. Mapping $\log_2 P_v$ (per voice $v$) to MIDI pitch — shorter period = higher pitch, the NASA exoplanet-sonification convention — turns orbital architecture into pitch architecture: a chain of bodies whose $a$ grows by factor $r$ yields periods growing by $r^{3/2}$, so successive voices sit $\tfrac32 \log_2 r$ apart in pitch-class space. Choosing $a$ ratios deliberately gives diatonic/harmonic results: $a$ ratio $2^{2/3}$ → period ratio exactly 2 (octave); $2^{4/9}$ → $P$ ratio 3:2 (fifth). The harmonic series arises from real orbital ratios.

### 1.4 Mean-motion resonance — the harmony engine

Two bodies are in a $p{:}q$ mean-motion resonance when $p\,n_1 = q\,n_2$ (mean motions $n = 2\pi/P$), i.e. period ratio $P_1:P_2 = p:q$. Canonical cases:

- **2:1** — Io–Europa; the inner body laps the outer every outer orbit.
- **3:2** — Neptune–Pluto; Laplace "great inequality" Jupiter–Saturn is near 5:2.
- **Laplace resonance 4:2:1** — Io–Europa–Ganymede: two coupled 2:1 resonances with mean motions in exact 4:2:1 commensurability; apsides anti-aligned ($\varpi_{\text{Io}} - \varpi_{\text{Europa}} \approx \pi$) and the resonant argument librates about 180° with tiny amplitude and ~2000-day period.

**Musical operators:**
1. **Polyrhythmic hierarchy** — $N_v$ events per common cycle in ratio $p:q$ reproduces a $p$-against-$q$ polyrhythm; the Laplace chain gives 4-against-2-against-1 across three voices, exactly the classic "4:2:1" drum-hierarchy.
2. **Cadence schedule** — conjunction epochs (longitude alignments) recur every $q$ inner orbits; these are physical, periodic *resolution points*. Anti-aligned apsides mean the harmonic state oscillates between aligned (conjunctive sonority) and anti-aligned (disjunctive) — a deterministic tension pendulum.
3. **Macro-form** — the *resonance-capture chain* (the differential-migration sequence the real Galilean system followed: 3:2 → 2:1 → Laplace 4:2:1; Peale & Lee 2002) is a ready-made dramatic arc: sparse wide conjunctions → locked 2:1 → dense three-way 4:2:1 climax.

## 2. The full compositional mapping

| Parameter | Musical product |
|---|---|
| $a_v$ (semi-major axis) | register (log₂P), voice order |
| $e_v$ (eccentricity) | rubato depth, contour amplitude, characteristic interval (the Kepler table) |
| $P_v$ (period) | cycle length = section length (outer "year") |
| $N_v$ (events/orbit) | density per voice; $N$ ratios = polyrhythm ratios |
| $\varpi_v$ (apsidal orientation) | phase: anti-aligned = hocket/interleave, aligned = tutti rushes |
| $p{:}q$ resonance | harmonic rhythm, cadence epochs, tension pendulum |
| $\nu_k$ (true anomaly sampling) | onset time law → rubato stream |

## 3. Python implementation sketch

```python
"""generators/kepler_orbit_composer.py — KORC (Method 115), Nature-Led, concrete layer.
Feeds UnitMatrix cells as MusicUnit event sequences (zero-drift compliant).
"""
import math
from dataclasses import dataclass, field
from typing import List, Tuple

# ---------- Kepler kernel (closed-form, no iteration needed) ----------

def true_anomaly_time(nu: float, e: float, P: float) -> float:
    """Exact time (fraction of period P) at which a body on orbit (e, P)
    reaches true anomaly nu. Derived from the equal-areas law:
        tan(E/2) = sqrt((1-e)/(1+e)) * tan(nu/2);  M = E - e sin E;  t = P M / 2pi.
    """
    E_half = math.atan(math.sqrt((1 - e) / (1 + e)) * math.tan(nu / 2.0))
    E = 2.0 * E_half
    M = E - e * math.sin(E)
    return (P / (2.0 * math.pi)) * M

def radius_at(nu: float, a: float, e: float) -> float:
    """Kepler's 1st law: radial distance at true anomaly nu."""
    return a * (1.0 - e * e) / (1.0 + e * math.cos(nu))

def kepler_interval(e: float) -> float:
    """Ratio of max to min angular velocity == ratio of max to min ISI.
    = ((1+e)/(1-e))**2.  This is Kepler's Harmonice Mundi interval."""
    return ((1.0 + e) / (1.0 - e)) ** 2

def period_from_axis(a: float, GM: float = 1.0) -> float:
    """Kepler's 3rd law: P = 2 pi sqrt(a^3 / GM)."""
    return 2.0 * math.pi * math.sqrt(a ** 3 / GM)

def nearest_just_ratio(r: float) -> Tuple[float, str]:
    """Quantize a velocity ratio to the nearest low-limit just ratio (name)."""
    just = [(1, 1, "unison"), (16, 15, "semitone"), (9, 8, "M2"),
            (6, 5, "m3"), (5, 4, "M3"), (4, 3, "P4"), (3, 2, "P5"),
            (8, 5, "m6"), (5, 3, "M6"), (15, 8, "M7"), (2, 1, "octave")]
    best = min(just, key=lambda j: abs(math.log(r / (j[0] / j[1]))))
    return best

# ---------- Voice model ----------

@dataclass
class PlanetVoice:
    """One UnitMatrix voice = one Keplerian body."""
    name: str
    a: float                     # semi-major axis (orbital scale/register)
    e: float                     # eccentricity (rubato + contour + interval)
    n_events: int                # events per orbit ("resolution" / density)
    period_ratio: float = 1.0    # working period P_v (ticks) derived from this
    root_midi: int = 60
    contour_span: int = 12       # semitones of contour sweep per orbit
    apsidal_phase: float = 0.0   # varpi: rotation of the whole orbit in time
    invert_contour: bool = False

    def events(self, P_ticks: float) -> List[Tuple[float, int, int]]:
        """Return (onset_tick_fraction, pitch, velocity) for one orbit.
        onsets are fractions of P_ticks (scale later to section length).
        velocity from areal speed h/r^2 (loudest at perihelion)."""
        out = []
        for k in range(1, self.n_events + 1):
            nu = 2.0 * math.pi * k / self.n_events + self.apsidal_phase
            t_frac = true_anomaly_time(nu, self.e, 1.0)      # fraction of P
            r = radius_at(nu, self.a, self.e)
            r_min, r_max = self.a * (1 - self.e), self.a * (1 + self.e)
            span = (r - r_min) / (r_max - r_min)             # 0..1, 1 at aphelion
            if self.invert_contour:
                span = 1.0 - span
            pitch = self.root_midi + int(round(self.contour_span * span))
            vel = int(40 + 87 * (r_min / r))                 # areal speed ∝ 1/r²
            out.append((t_frac, pitch, vel))
        return out

# ---------- Resonance / form layer ----------

@dataclass
class ResonanceChain:
    """Mean-motion commensurability p:q between consecutive voices.
    conjunction epoch = when inner body has lapped outer q times."""
    p: int                       # inner body laps per outer orbit
    q: int                       # outer orbits per cycle
    def conjunction_fractions(self, n_cycles: int) -> List[float]:
        return [i / self.q for i in range(n_cycles * self.q + 1)]

def synodic_period(P1: float, P2: float) -> float:
    """Recurrence period of the relative configuration (P1<P2)."""
    return P1 * P2 / abs(P1 - P2)

# ---------- UnitMatrix cell filling ----------

def fill_voice_section(voice: PlanetVoice, section_len_ticks: int,
                       section_start: int = 0) -> "MusicUnit":
    """Build one voice×section cell: orbit scaled to section_len_ticks.
    Returns a MusicUnit whose events terminate exactly at section_len
    (zero-drift invariant)."""
    from structures import MusicEvent
    P_ticks = float(section_len_ticks) / voice.period_ratio
    evs = voice.events(P_ticks)
    events = []
    for t_frac, pitch, vel in evs:
        t0 = section_start + int(round(t_frac * P_ticks))
        # duration: dwell until next onset (or legato cap)
        t1 = section_start + len(events)*0  # placeholder, see pitfall #2/#3
        events.append(MusicEvent(pitch, vel, t0, min(t0 + 960, section_start + section_len_ticks)))
    # pad terminal landmark so sum(durations) == section_len_ticks
    return MusicUnit.from_events_padded(events, section_len_ticks)   # engine helper

# ---------- main ----------
if __name__ == "__main__":
    # synthesis: Laplace 4:2:1 chain, 3 voices, 1 section/column each
    io  = PlanetVoice("Io",      a=1.0, e=0.20, n_events=16, period_ratio=4.0, root_midi=72)
    eu  = PlanetVoice("Europa",  a=1.6, e=0.12, n_events=8,  period_ratio=2.0, root_midi=60)
    gan = PlanetVoice("Ganymede",a=2.5, e=0.06, n_events=4,  period_ratio=1.0, root_midi=48)
    for v in (io, eu, gan):
        print(v.name, kepler_interval(v.e), nearest_just_ratio(kepler_interval(v.e)),
              len(v.events(P_ticks=1920)))
```

## 4. References

- Kepler, J. (1619). *Harmonice Mundi*, Book V. Linz. (Aiton/Duncan/Field trans., Amer. Phil. Soc., 1997.)
- Walker, D. P. (1964). "Kepler's Celestial Music." *J. Warburg & Courtauld Institutes* 30, 249.
- Voelkel, J. R. (1995). "The Music of the Heavens: Kepler's Harmonic Astronomy." *Physics Today* 48(6), 59–60.
- IEEE Pulse — "Music Therapy and the Planets' Consonances" (Kepler interval table; major/minor thirds of Saturn/Jupiter; Mars 2:3; Earth 15:16; Venus 24:25).
- "*An even more 'harmonic' version of Kepler's third law.*" *The Physics Teacher* 61(2), 150 — sesquialtera P-ratio form.
- Grove Music Online, "Kepler, Johannes".
- Wikipedia: "Orbital resonance" (Laplace resonance 4:2:1; libration ≈180°, ~2000-day period; anti-aligned apsides).
- NASA SVS #5653 "Sonification of Exoplanet Discoveries by Month"; NASA "5000 Exoplanets: Listen to the Sounds of Discovery" — period → pitch practice.
- Peale, S. J. & Lee, M. H. (2002). "A primordial origin of the Laplace relation among the Galilean satellites." *Science* 298, 593–597 — resonance-capture sequence 3:2 → 2:1 → 4:2:1.

## 5. Sibling relations (anti-duplication)

- **020 SMSTC** — gravity/kinematics as *unbound event-cloud drivers*; KORC uses *bound elliptical orbits* with exact time laws and period ratios.
- **043 SATM** — chaotic self-same attractors (Lorenz/Rössler); Keplerian orbits are *regular, closed, deterministic*, the opposite dynamical regime.
- **012 Euclidean / 069 Christoffel** — abstractly distribute k onsets/pulses; KORC's onset distribution *derives from r(ν)⁻² physics* (same ratios, physical origin).
- **045 Hawkes** — stochastic self-exciting aftershocks; KORC's perihelion clustering is *deterministic areal-speed clustering* (the deterministic counterpart).
- **038 KOPS** — coupled phase oscillators seeking synchronization; KORC's 2:1/3:2/4:2:1 are *true gravitational commensurabilities* with conjunction epochs, not pulled phases.
- **039 SMA / 113 PCFSC** — spectral/Fourier pitch design; KORC's intervals come from *orbital velocity ratios* (a physical harmonic series), not spectral analysis.

Candidate code path: `generators/kepler_orbit_composer.py` (see §3).