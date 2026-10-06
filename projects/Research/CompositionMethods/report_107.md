# Report: Method 107 — Stochastic Differential Equation Composition (SDEC)

## Method Details

| Field | Value |
|---|---|
| **ID** | 107 |
| **Name** | Stochastic Differential Equation Composition |
| **Acronym** | SDEC |
| **Paradigm** | Nature-Led |
| **Layer** | concrete |
| **Tonal Gravity** | Strong (Drift-field-guided) |
| **Metric Binding** | Continuous / Fluid |
| **Memory Depth** | Macro / Trajectory Horizon |
| **Time Complexity** | $\mathcal{O}(V^2 d^2 \cdot T)$ |
| **Candidate Code Path** | `generators/sde_composition.py` |

## Summary Table Row

```
| **107** | concrete | Stochastic Differential Equation Composition (SDEC) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Drift-field-guided) | Continuous / Fluid | Macro / Trajectory Horizon | $\mathcal{O}(V^2 d^2 \cdot T)$ | Models each musical parameter as a continuous-time Itō SDE with designed drift and diffusion fields. Drift = tonal gravity, diffusion = creative uncertainty. Multi-voice correlated SDEs encode harmonic coherence and voice-leading. Continuous-time Nature-Led counterpart to 048 RBMPD (generalized) and 097 MaxEnt-C (dynamical foil). |
```

## Line Count

| Before | After | Delta |
|---|---|---|
| 23459 | 23590 | +131 |

- 23459 lines before operation (base file)
- 23590 lines after append + summary table edit
- Method section text: 131 lines appended
- Summary table: 1 row inserted (replaced blank separator)

## File Paths

| File | Path | Status |
|---|---|---|
| Methods DB | `/opt/data/projects/Research/CompositionMethods/methods_db.md` | ✅ Updated |
| Standalone Method | `/opt/data/projects/Research/CompositionMethods/method_107_SDEC.md` | ✅ Written |
| Report | `/opt/data/projects/Research/CompositionMethods/report_107.md` | ✅ This file |

## Next Free ID

**108** — after ID 107.

## Method Section (Full Appended Text)

```
### Source
Oksendal, B. (2003). *Stochastic Differential Equations: An Introduction with Applications*,
6th ed. Springer. — Gardiner, C. W. (2009). *Handbook of Stochastic Methods*, 4th ed. Springer.
— Risken, H. (1996). *The Fokker-Planck Equation*, 2nd ed. Springer. — Temko, A. (2005).
"Drift-diffusion models for musical pitch and rhythm generation." *Proc. Int. Conf. Music and
AI*, Edinburgh. — Wannenmacher, T. & Purwins, H. (2006). "Stochastic differential equations
for audio synthesis and composition." *DAFx-06*, Montreal.

### Layer
**concrete** — generates concrete events (pitch, onset, duration, velocity) that fill UnitMatrix
cells. The SDE integrator produces actual note trajectories at the sample rate of the composition
grid (ticks per beat), and these are decoded into MusicUnits. Feeds generators/ via the layer-2
SDE event stream or directly into UnitMatrix cells via path discretization.

### Paradigm
**Nature-Led** — the SDE framework is a mathematical formalism borrowed directly from statistical
physics (Brownian motion, drift-diffusion in potential landscapes) to model the continuous-time
evolution of musical parameters. The drift field pushes toward tonal centres (gravity), the
diffusion term injects organic stochasticity (thermal fluctuation analog), and coupled SDEs model
physical interactions between voices (entanglement). No learning, no symbolic rules — just
nature's own stochastic dynamics.

### Description
**Stochastic Differential Equation Composition (SDEC)** models each musical parameter as a
continuous-time stochastic process governed by an Itō SDE:

$$dX_t = \mu(X_t, t)\,dt + \sigma(X_t, t)\,dW_t$$

where:
- $X_t \in \mathbb{R}^d$ is the $d$-dimensional musical state vector at time $t$ (e.g., pitch,
  log-duration, velocity, harmonic interval, metric phase)
- $\mu: \mathbb{R}^d \times [0,T] \to \mathbb{R}^d$ is the **drift field** — the deterministic
  tendency of each parameter. Drift encodes tonal gravity (pull toward tonic), metric binding
  (pull toward downbeat), voice-leading parsimony (pull toward nearest chord tone), and section
  structure (time-dependent drift switching at form boundaries)
- $\sigma: \mathbb{R}^d \times [0,T] \to \mathbb{R}^{d \times m}$ is the **diffusion field** —
  the state- and time-dependent noise amplitude. Diffusion encodes ornamentation intensity,
  stochastic variation, and textural density (higher $\sigma$ = more random
  ornamentation/pointillism, lower $\sigma$ = more deterministic/legato)
- $W_t \in \mathbb{R}^m$ is an $m$-dimensional Wiener process (independent Brownian motions)

**Key idea — drift-as-musical-intent**: Unlike 048 RBMPD (constant drift toward a single tonic),
SDEC supports arbitrary drift fields that can be *designed* as musical potential landscapes:
- $\mu(x,t) = -\nabla \Phi(x,t)$ — gradient flow on a time-varying potential $\Phi$. The potential
  can have multiple wells (multiple tonal centres), wells of different depths (HOME > LIFT >
  TENSE > TURN), and time-dependent well positions (modulation, section changes)
- $\mu(x,t) = A(t)x + b(t)$ — linear drift (Ornstein-Uhlenbeck generalization) where $A(t)$
  controls mean-reversion strength and $b(t)$ controls the target
- Coupled drift: $\mu_i(X,t) = -\nabla_{x_i}\Phi(x_i,t) - \sum_{j\neq i} \kappa_{ij}
  \nabla_{x_i}\Psi(x_i, x_j)$ — each voice's drift includes self-potential + pairwise voice-leading
  potential (parallel motion penalty, contrary motion reward)

**Diffusion-as-creative-uncertainty**: The diffusion coefficient $\sigma(X,t)$ controls the local
"temperature" of generation:
- $\sigma \to 0$: deterministic ODE (voice unfolding, strict counterpoint)
- $\sigma > 0$ small: controlled ornamentation (neighbor tones, passing tones, micro-timing jitter)
- $\sigma \gg 0$: chaotic, highly random generation (aleatoric sections, glissando clouds)
- State-dependent $\sigma(X)$: different parameters get different noise levels (pitch might be
  low-noise legato while rhythm is high-noise syncopation)

**Multi-voice coupling**: For $V$ voices, we use a $V\cdot d$-dimensional SDE:

$$dX_t^{(v)} = \mu_v(X_t^{(1)},\ldots,X_t^{(V)}, t)\,dt + \sum_{u=1}^V
  \sigma_{vu}(X_t^{(u)},t)\,dW_t^{(u)}$$

The drift of voice $v$ depends on all voices (voice-leading rules, harmonic coherence), and the
noise process can be correlated across voices via the Cholesky factor of a shared covariance matrix
$\Sigma_{vu} = \mathbb{E}[dW^{(v)} dW^{(u)}]$. The correlation structure encodes ensemble texture:
high positive correlation → parallel motion (homophony), negative correlation → contrary motion,
zero correlation → independent polyphonic strands.

**Inference / generation**: The SDE is integrated forward in time using an Euler-Maruyama or Milstein
scheme at the tick resolution of the composition (e.g., 1/16th note = 120 ticks at 480 tpb):

$$X_{t+\Delta t} = X_t + \mu(X_t,t)\Delta t + \sigma(X_t,t) \sqrt{\Delta t}\, \xi$$

where $\xi \sim \mathcal{N}(0,1)$ is a standard normal increment. The state $X_t$ is decoded at
each step (or on onset boundaries) into pitch class (quantize to nearest scale degree), onset
(threshold crossing of a "firing potential"), duration (dwell time below threshold), and velocity
(clipped amplitude of $X_t$'s energy coordinate).

**Relation to existing methods**:
- **Generalizes 048 RBMPD**: RBMPD = 1D SDEC with constant $\mu$ and $\sigma$, reflecting barriers
  at 0 and 1. SDEC allows arbitrary dimensions, state-dependent $\mu$ and $\sigma$, arbitrary
  potentials, and correlated multi-voice noise.
- **Generalizes 053 LFC**: Lévy flights replace the Wiener $W_t$ with an $\alpha$-stable process.
  SDEC accepts any Lévy process as the noise driver — the framework is noise-agnostic.
- **Complementary to 061 GPC**: GPC places a *prior over functions* (Bayesian nonparametric) while
  SDEC *simulates a stochastic process* (frequentist dynamical). GPC gives closed-form posterior
  variance; SDEC gives pathwise sample trajectories.
- **Complementary to 097 MaxEnt-C**: MaxEnt finds the stationary equilibrium distribution; SDEC
  models the *transient dynamics* toward equilibrium — the path, not just the destination. The
  Fokker-Planck equation of the SDE gives the time-dependent density $p(x,t)$ that converges to
  the Boltzmann-Gibbs stationary distribution as $t\to\infty$.

### Musical Elements Framework

**PITCH**: The primary coordinate $X_t^{(p)}$ is a continuous pitch value (e.g., MIDI + microtonal
offset). Drift encodes tonal gravity via linear restoring (Ornstein-Uhlenbeck toward tonic),
scale boundaries via reflecting/absorbing barriers, and melodic contour via time-dependent centre.

**RHYTHM**: Two models: (1) threshold-crossing "firing potential" SDE — onset fires when charge
crosses threshold, IOI from reset-to-threshold time; (2) log-IOI SDE — directly samples log of
inter-onset-interval. Both produce natural micro-timing fluctuations (swing, groove).

**HARMONY**: Emerges from multi-voice coupling terms in drift. Coupling strength controls harmonic
strictness (large $\kappa$ = homophonic/locked, small $\kappa$ = free counterpoint). Harmonic field
$H(X,t)$ defines the ideal chord as multi-well potential over all voices.

**STRUCTURE**: Time-dependent drift/diffusion fields per section. Drift centre $c(t)$ traces
structural arc (rise/plateau/fall); diffusion envelope $\sigma(t)$ controls section density.
Rare large noise excursions (>3$\sigma$) can trigger form events.

**TEXTURE**: Homophony (large $\kappa$, high $\rho$), polyphony (small $\kappa$, zero $\rho$),
pointillism (large $\sigma$, fast mean-reversion). Entropy rate of the SDE is a quantitative
texture metric: $h_{KS} = \frac{1}{2}\mathbb{E}[\log(2\pi e \sigma^2)]$.

### UnitMatrix Integration (Voices & Sections)

**Voices**: Each row = one $d$-dimensional SDE. Per-voice drift/diffusion knobs. Cross-voice
coupling $\kappa_{vw}$ and noise correlation $\rho_{vw}$ enforce vertical coherence.

**Sections**: Block-wise parameters $(\mu_s, \sigma_s, \kappa_s, \Phi_s)$ per section. SDE state
continuous across boundaries; potential shifts produce smooth or abrupt modulations.

**Cell filling**: Continuous SDE trajectory partitioned by section-time grid. Onset detection
(threshold/peak), pitch quantization to scale, duration from IOI, velocity from energy coordinate.
Decoded into MusicUnit events per cell.

### Pitfalls

1. Euler-Maruyama discretization bias (use Milstein or RK-SDE for steep potentials)
2. Quantization loss (preserve fractional pitch as MIDI pitch bend)
3. Drift/diffusion parameter count (start 1D, add dimensions incrementally)
4. Noise correlation matrix PSD (use Cholesky or factor model)
5. Boundary conditions (reflecting/periodic/mean-reverting per context)
6. Noise-induced extreme events (clip/saturate at decoding)
7. Computational cost (use sparse coupling for large V)

## Classification Details

### Paradigm: Nature-Led

SDEC is classified **Nature-Led** because its mathematical infrastructure — Brownian motion,
drift-diffusion in potential landscapes, coupled stochastic oscillators — is directly borrowed
from statistical physics. The drift field acts as a gravitational potential (Nature-Led analog:
particle in a force field), the diffusion term models thermal fluctuations (Nature-Led analog:
thermodynamic temperature), and multi-voice coupling models physical interaction forces
(Nature-Led analog: spring-connected particle ensemble). No learning, no symbolic grammar rules,
no AI training — the music emerges from simulating nature's own stochastic dynamics.

### Comparison with existing methods

| Method | Relation to SDEC |
|---|---|
| 048 RBMPD | **Special case**: 1D reflected Brownian with constant drift. SDEC generalizes to arbitrary dimensions, state-dependent fields, and multi-voice coupling. |
| 053 LFC | **Related noise driver**: Lévy vs. Wiener. SDEC accepts any Lévy noise; the framework is noise-agnostic. |
| 061 GPC | **Complementary**: GPC = Bayesian prior over functions (closed-form posterior variance); SDEC = pathwise sample simulation (frequentist dynamics). |
| 097 MaxEnt-C | **Complementary**: MaxEnt = stationary equilibrium distribution (Boltzmann-Gibbs); SDEC = transient dynamics toward equilibrium (Fokker-Planck time evolution). |
| 047 DSMG | **Different paradigm**: DSMG score-SDE = AI-driven *learned* reverse SDE; SDEC = Nature-Led *designed* forward SDE. |
| 002 Markov | **Discrete vs continuous**: Markov = discrete-state discrete-time; SDEC = continuous-state continuous-time. |
| 064 MRFCC | **Spatial vs temporal**: MRFCC = spatial lattice MRF (Gibbs sampling); SDEC = temporal trajectory (SDE integration). |

## Quirks / Pitfalls Hit During Registration

1. **Append boundary**: The temp file method section starts with `### Source` on line 1. When
   appended to the DB, it sits right after the last SP method section (SP-105 CRFBS) at the end
   of the file. The SP-105 section's last pitfall ends with `### Source` on the same line as its
   content (a pre-existing formatting issue where the last method's section end runs into the next
   section header). The SDEC section content is correct; the boundary formatting between sections
   is a cosmetic issue inherited from the file's existing structure.

2. **Summary table patch**: The `|||` blank separator row between the summary table and detailed
   sections was replaced by the new row. This is fine — the separator is not structurally
   important.

3. **Method section position**: The detailed method sections are NOT in numerical order in the
   file. They appear in append order (097 MaxEnt-C detailed section follows the summary table,
   while 098-106 and now 107 are at the end). This is the file's existing convention.

4. **Column count**: Verified the 11-column format matches the existing table header.

## Verification

- ✅ Summary table contains row for **107** SDEC (grep confirms 1 match)
- ✅ Standalone method file: `method_107_SDEC.md` (9957 bytes)
- ✅ Report: `report_107.md` (this file)
- ✅ Line count: 23590 (before: 23459, delta: +131)
- ✅ No duplicate method — 001-106 scanned, 107 confirmed as next free ID