# Method 135 — Susceptible-Infected-Recovered Composition (SIRC)

- **Paradigm:** Nature-Led
- **Layer:** concrete (fills UnitMatrix cells directly; candidate module `generators/sir_contagion.py`)
- **DB entry:** `methods_db.md` § "Susceptible-Infected-Recovered Composition (SIRC) (Method 135)" (summary row line 145)
- **Verification harness:** `verify_135_SIRC.py` (green: VERDICT PASS), demo at `projects/Research/outputs/sirc135_demo/sirc135_demo.mid`
- **Web cache:** `_web135/` (arxiv_sir_music.xml, arxiv_epidemic_music.xml, wiki_kermack.json, wiki_compartmental.json)

---

## 1. One-line idea

Compose by running a *disease* over the musical material: the material population is split into
**S**usceptible (unused), **I**nfectious (sounding now), **R**ecovered (resolved, permanently immune),
and the Kermack–McKendrick equations drive the piece — $R_0 = \beta S_0/\gamma$ is the form dial, the
prevalence $I(t)$ is the tension/density curve, the peak time is the climax, and the **final size**
$\ln(S_0/S_\infty) = (\beta/\gamma)(S_0 + I_0 - S_\infty)$ is a *provable ending*.

## 2. Why this is not a re-skin of an existing method

| Existing | What it constrains | What SIRC adds |
|---|---|---|
| 045 Hawkes self-exciting point process | event rate increases after each event ("contagion") | no compartments, no immunity, no final size — fire keeps catching; SIRC *exhausts itself* (susceptible depletion is the decay mechanism) |
| 036 Abelian sandpile | conserved grains, threshold toppling, always critical | conservation broken: transmission + removal, system settles to a *definite final size* < 100% |
| 093 percolation | static bond/site occupation, one giant component | static connectivity; SIRC is *dynamical* (time course, recovery, re-seeding) — only related at criticality (Grassberger 1983) |
| 037 FitzHugh–Nagumo spiking | per-neuron 2D ODE with refractory | no susceptible pool, no removal, no threshold theorem, no final size |
| 030 reaction–diffusion | continuous concentrations on a lattice | no immunity, no mass-action transmission with depletion |
| 045/086/087 point-process/HMM families | probabilistic *transitions* | SIRC composes the *epidemic itself* — a closed population with provable global outcomes |

Prior art in *theory*, none in the DB: Kermack–McKendrick SIR (1927–1933), Reed–Frost chain-binomial
(1928), network epidemic thresholds (Pastor-Satorras et al. 2015), SIR↔percolation (Grassberger 1983).
Musical precedents exist for *tension arcs* (004 prosody, 084 Zipf) but not for transmission-with-removal
dynamics as the generating law.

## 3. Extended mathematics

### 3.1 The ODE and the threshold

Closed population $N = S + I + R$ constant:

$$\frac{dS}{dt} = -\beta S I, \qquad \frac{dI}{dt} = \beta S I - \gamma I, \qquad \frac{dR}{dt} = \gamma I .$$

Linearising near $I=0$: $dI/dt \approx I(\beta S_0 - \gamma)$, so the infection grows iff
$\beta S_0/\gamma > 1$. Define the **basic reproduction number**

$$R_0 = \frac{\beta S_0}{\gamma} \qquad (\text{absolute-count convention; } \beta = R_0\gamma/S_0).$$

Verified: $R_0 = 2$ and $R_0 = 5$ both produce epidemics (prevalence peaks above $I_0$); $R_0 = 0.5$
decays monotonically — no climax.

### 3.2 Exact peak and final size

Dividing $dI/dt$ by $dS/dt$: $dI/dS = -1 + \gamma/(\beta S)$, integrate:

$$I(S) = I_0 + S_0 - S + \frac{\gamma}{\beta}\ln\frac{S}{S_0}.$$

**Peak** at $dI/dt = 0 \Rightarrow S^* = \gamma/\beta = \rho$ (the relative removal rate), giving the
closed-form peak value

$$\boxed{\,I^* = S_0 + I_0 - \rho\Big(1 - \ln\frac{\rho}{S_0}\Big)\,}$$

verified to $4.9\times10^{-9}$ ($R_0=2$) and $4.3\times10^{-6}$ ($R_0=5$; RK4-truncation-limited).

**Final size** at $t\to\infty$ ($I_\infty = 0$):

$$\boxed{\,\ln\frac{S_0}{S_\infty} = \frac{\beta}{\gamma}\Big(S_0 + I_0 - S_\infty\Big)\,}$$

verified to $3\times10^{-13}$ — note the $+I_0$ term: omitting it produces error exactly
$(\beta/\gamma)I_0$ (measured 2.2e-3 / 5.05e-3). $S_\infty/N$ is the *silence budget*: 18.3% at $R_0=2$,
0.7% at $R_0=5$.

### 3.3 The Kermack–McKendrick sech² approximation (and its honest error)

K&M 1927's approximate bell curve $I(t) \approx A\,\mathrm{sech}^2\!\big(\tfrac{\gamma}{2}(t-t_0)\big)$
(peak-anchored: $A = I^*$, $t_0 = t_{\text{peak}}$) was measured against RK4: **max relative deviation
0.22** at $R_0=2$. Cause: the true curve is asymmetric (fast exponential rise, slower removal-limited
decay) while sech² is symmetric. Compose with RK4; treat the closed form as intuition only (pitfall 3).

### 3.4 Reed–Frost chain-binomial (sections = generations)

Discrete generations, each susceptible contacts the $I_g$ infectives independently with probability $p$:

$$P(\text{infected}\mid I_g) = 1 - (1-p)^{I_g}, \qquad I_{g+1} \sim \operatorname{Binomial}\!\big(S_g,\; 1-(1-p)^{I_g}\big).$$

Verified: realized sizes inside the 3-σ binomial band; small-$pI$ limit $E[I_{g+1}] \approx pI_g S_g$ =
Euler step of $-dS/dt = \beta SI$ with $\beta = p/\Delta t$ (first-order error $-0.0186$).

### 3.5 Spatial contact process (the UnitMatrix lattice)

Cells = hosts on a $V \times S$ grid. Melodic contact: same-voice previous section, probability $p$.
Harmonic contact: vertical neighbors in the same section, probability $1-(1-p)^{\#\text{contacts}}$.
Infectious period = one section; recovery = permanent. Column prevalence $I_j$ = per-section density.
The lattice has its own threshold (Pastor-Satorras et al., $\lambda_c = \langle k\rangle/\langle k^2\rangle$):
verified $p=0.60$ ⇒ outbreak (152/192 cells, reserve 40), $p=0.15$ ⇒ die-out (6/192, reserve 186).

## 4. Verified numbers (2026-11-05, `verify_135_SIRC.py`)

```
[A] SIR ODE (RK4, dt=2e-4, t=100)
  epidemic R0=2      cons_max=1000.000000  epidemic=True  S(peak)=449.9979 vs rho=450
                     peak_err=4.94e-09  fin_size_err=2.75e-13  unimodal=True
  epidemic R0=5      cons_max=1000.000000  epidemic=True  S(peak)=197.9587 vs rho=198
                     peak_err=4.30e-06  fin_size_err=2.52e-13  unimodal=True
  subcritical R0=0.5 cons_max=1000.000000  epidemic=False (monotone decay)
                     fin_size_err=1.96e-13
  [A7] K&M sech^2 closed form: max rel deviation vs RK4 = 0.2195 (approx)
[B] Reed-Frost chain binomial: 4 generations to extinction; within 3-sigma; Euler limit -0.0186
[C] spatial: p=0.60 => 152/192 cells (reserve 40); p=0.15 => 6/192 (reserve 186); threshold holds
[D] UnitMatrix: 8 voices x 6 sections, validate()=True, 180 events, MIDI 1839 bytes, preflight OK
VERDICT: PASS
```

## 5. Python implementation sketch

```python
# generators/sir_contagion.py — SIRC (Method 135)
import math, random
import numpy as np


class SIRModel:
    """Kermack-McKendrick ODE, RK4. R0 convention: beta = R0*gamma/S0."""

    def __init__(self, R0, gamma=1.0, S0=900.0, I0=1.0, N=1000.0):
        self.beta = R0 * gamma / S0
        self.gamma, self.S0, self.I0, self.N = gamma, S0, I0, N

    def curve(self, dt=2e-4, steps=500000):
        b, g, S, I, R = self.beta, self.gamma, self.S0, self.I0, self.N - self.S0 - self.I0
        SS, II = [S], [I]
        for _ in range(steps):
            def f(s, i, r):
                return (-b*s*i, b*s*i - g*i, g*i)
            k1 = f(S, I, R); k2 = f(S+dt/2*k1[0], I+dt/2*k1[1], R+dt/2*k1[2])
            k3 = f(S+dt/2*k2[0], I+dt/2*k2[1], R+dt/2*k2[2])
            k4 = f(S+dt*k3[0], I+dt*k3[1], R+dt*k3[2])
            S += dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
            I += dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
            R += dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
            SS.append(S); II.append(I)
        return np.array(SS), np.array(II)

    def peak_value(self):                 # exact closed form
        rho = self.gamma / self.beta
        return self.S0 + self.I0 - rho * (1.0 - math.log(rho / self.S0))

    def final_size(self, S_inf):          # exact identity, includes +I0
        return abs(math.log(self.S0 / S_inf)
                   - (self.beta/self.gamma) * (self.S0 + self.I0 - S_inf))


class ReedFrostChain:
    """Chain-binomial: generations = sections."""

    def __init__(self, p, S0, I0, rng=None):
        self.p, self.S0, self.I0 = p, S0, I0
        self.rng = rng or random.Random()

    def generate(self, gens=30):
        S, I = self.S0, self.I0
        out = []
        for g in range(gens):
            prob = 1.0 - (1.0 - self.p) ** I
            new = sum(self.rng.random() < prob for _ in range(S))
            out.append((g, S, I, new))
            S -= new; I = new
            if new == 0:
                break
        return out


class GridContactProcess:
    """Spatial Reed-Frost on the VxS UnitMatrix lattice.
    Melodic contact = same voice, previous section. Harmonic = vertical neighbors.
    Infectious period = one section; recovery = permanent immunity."""

    def __init__(self, V, S, p_mel, p_harm, seeds, seed=1352, sweeps=3):
        self.V, self.S, self.p_mel, self.p_harm = V, S, p_mel, p_harm
        self.seeds, self.seed, self.sweeps = seeds, seed, sweeps

    def run(self):
        r = random.Random(self.seed)
        act = [[False]*self.S for _ in range(self.V)]
        for (v, j) in self.seeds:
            act[v][j] = True
        pc = [0]*self.S; pc[0] = len(self.seeds)
        for _ in range(self.sweeps):                       # seed-column spread
            for v in range(self.V):
                if act[v][0]:
                    continue
                c = sum(act[w][0] for w in (v-1, v+1) if 0 <= w < self.V)
                if c and r.random() < 1 - (1 - self.p_harm) ** c:
                    act[v][0] = True
        pc[0] = sum(act[v][0] for v in range(self.V))
        for j in range(self.S - 1):
            for v in range(self.V):                        # melodic (forward)
                if act[v][j] and not act[v][j+1] and r.random() < self.p_mel:
                    act[v][j+1] = True
            for _ in range(self.sweeps):                   # harmonic (same gen)
                for v in range(self.V):
                    if act[v][j+1]:
                        continue
                    c = sum(act[w][j+1] for w in (v-1, v+1) if 0 <= w < self.V)
                    if c and r.random() < 1 - (1 - self.p_harm) ** c:
                        act[v][j+1] = True
            pc[j+1] = sum(act[v][j+1] for v in range(self.V))
        return act, pc
```

## 6. UnitMatrix realisation

```python
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (UnitMatrixComposer, create_note_unit,
                                           _unit_from_events)

plan = GridContactProcess(V=8, S=24, p_mel=0.60, p_harm=0.60,
                          seeds=[(2,0),(3,0),(4,0),(5,0)]).run()   # active, prev_col

composer = UnitMatrixComposer(bpm=96, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=8, num_sections=6)               # 6 sections x 4 gens
for v, prog in enumerate([MidiInstrument.FLUTE, MidiInstrument.VIOLIN, MidiInstrument.TRUMPET,
                          MidiInstrument.STRING_ENSEMBLE, MidiInstrument.SYNTH_PAD,
                          MidiInstrument.CHURCH_ORGAN, MidiInstrument.BASS, MidiInstrument.PIANO]):
    composer.add_voice(f"V{v}", program=prog, channel=v)
for j in range(6):
    composer.add_section(f"S{j}", bars=4)

BAR = 1920
for v in range(8):
    for j in range(6):
        infected = any(active[v][4*j+k] for k in range(4) if 4*j+k < 24)
        events = []
        if infected:                                            # infected cell sounds
            for k in range(n_notes):                            # density from prevalence
                events.append((pitch_of(v, k), k*(BAR//n_notes), int(BAR/n_notes)-120))
        ev = [MusicEvent(p, 92, s, s+d) for (p, s, d) in events]
        composer.fill_voice_section(f"V{v}", f"S{j}",
                                    _unit_from_events(ev, section_len=BAR))  # S/R cells silent, padded

ok, msg = composer.validate()       # zero-drift gate — MUST be True (verified True)
composer.to_midi("out/sirc135.mid")
```

Rows = hosts; an infected row sounds its register, a susceptible/recovered row is **silent but padded**
(`_unit_from_events`), so every row still ends every section on the terminal landmark. Columns =
generations (or waves under a single $R_0$). Cells = `MusicUnit`.

## 7. References

1. Kermack, W. O., & McKendrick, A. G. (1927). A contribution to the mathematical theory of epidemics. *Proc. R. Soc. Lond. A* 115(772), 700–721.
2. Kermack, W. O., & McKendrick, A. G. (1932/1933). Parts II and III. *Proc. R. Soc. Lond. A* 138, 55–83; 141, 94–122.
3. Reed, L. J., & Frost, W. H. (1928). Some conceptions of epidemics in general. (Lecture; publ. *Am. J. Epidemiol.* 103(2), 1976.)
4. Abbey, H. (1952). An examination of the Reed–Frost theory of epidemics. *Human Biology* 24(3), 201–233.
5. Pastor-Satorras, R., Castellano, C., Van Mieghem, P., & Vespignani, A. (2015). Epidemic processes in complex networks. *Rev. Mod. Phys.* 87(3), 925–979.
6. Grassberger, P. (1983). On the critical behavior of the general epidemic process and dynamical percolation. *Math. Biosci.* 63(2), 157–172.
7. Hethcote, H. W. (2000). The mathematics of infectious diseases. *SIAM Review* 42(4), 599–653.
8. Bailey, N. T. J. (1975). *The Mathematical Theory of Infectious Diseases* (2nd ed.). Griffin.
9. Wikipedia. Compartmental models in epidemiology (rev. 2026-10-03); Kermack–McKendrick theory (rev. 2025-04-30). Cached `_web135/`.
10. arXiv API novelty queries: `all:"SIR model" AND all:music` → 0; `all:"epidemic model" AND all:music` → 1 (P2P piracy, not composition). Cached `_web135/`.

## 8. Pitfalls (compressed)

$R_0 = \beta S_0/\gamma$ in the absolute-count convention (not $\beta N/\gamma$); the final-size
equation carries $+I_0$ (omitting it errs by $(\beta/\gamma)I_0$); K&M's sech² closed form is
approximate (measured rel. deviation 0.22 — use RK4); stiff peaks ($R_0=5$) need $dt \le 2\times10^{-4}$
and a conservation assert; the grid has its own threshold ($p=0.60$ outbreak vs $p=0.15$ die-out),
not the ODE $R_0$; melodic contact is forward-only, harmonic contact needs a sweep cap; immunity is
per-cell not per-voice; silent S/R cells must be padded to section length (zero-drift); seed everything
(per-voice child seeds `seed*101+row`); don't confuse with 045 Hawkes — SIRC's signature is the final
size (self-exhaustion), not the contagion.
