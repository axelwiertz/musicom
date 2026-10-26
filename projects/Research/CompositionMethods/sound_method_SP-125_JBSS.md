# Sound Production Method SP-125 — Jawari Buzz-Bridge Sitar Synthesis with Sympathetic Taraf Bank (JBSS)

**Layer:** absolute (sound production) — **Synthesis Engines**
**Candidate code path:** `sound/synthesis/jawari_sitar.py` (`JawariString`, `TarafBank`, presets in `jawari_presets.py`)
**Summary-table row:** `| **SP-125** | Jawari Buzz-Bridge Sitar Synthesis with Sympathetic Taraf Bank (JBSS) | **Synthesis Engines** | Nonlinear Buzz-Bridge Plucked String / Sitar–Tanpura–Biwa Timbre | ... |`
**Instrument families covered:** sitar (jawari bridge, taraf sympathetic strings, chikari drones), tanpura/tambura (jivari), biwa and shamisen (*sawari* — the same obstacle mechanism), rudra veena, sarod (a related but flatter contact), plus a "buzz bridge" variant for prepared/custom instruments.
**Prototype:** `/opt/data/tmp_sitar/jawari_final.py` (executed with `$MUSICOM_PYTHON`, 2026-10-26; numbers in §6 reproduce bit-for-bit).

---

## 1. Why this is a distinct method

Jawari is not a filter and not a distortion. It is a **moving unilateral constraint with energy loss**: the string's termination point is not fixed, because the bridge is a curved surface of finite length over which the string rests and re-collides every half period, and the length of the stopped segment is set by the instantaneous vibration amplitude.

| | termination | nonlinearity | what happens to the spectrum |
|---|---|---|---|
| SP-011 KS, SP-033/SP-101 waveguide | fixed point + loop filter | none | each partial decays exponentially; highs die first, centroid drifts slowly down |
| SP-099 comb, SP-042 modal bank | fixed resonator set | none | static modal weights, no coupling between partials |
| SP-040 FDTD plate/membrane | linear PDE | none | linear superposition of modes |
| SP-049/SP-088 tape, SP-051 WDF, SP-100 Volterra | filter/circuit/polynomial | memoryless or fixed-order | harmonic *generation* on the whole waveform; the string is never re-shaped |
| SP-119/SP-102 AM, pan, chorus | none | none | amplitude/space only |
| **SP-125 JBSS** | **curved obstacle, contact length ∝ √A** | **stateful, geometry-driven, inelastic** | **partials exchange energy; nodal nulls fill in; centroid plunges; brightness tracks the envelope** |

Three falsifiable consequences, all measured in §6:

1. **Descending formants** — the centroid falls much faster than a linear string's would.
2. **Young–Helmholtz violation** — plucking at 1/5 of the length no longer nulls partial 5 (and 10): the collision injects them.
3. **Amplitude-as-timbre** — a 4:1 pluck-amplitude change alters the *relative* partial levels, not just the level.

---

## 2. Physics

### 2.1 Stiff, lossy string

With $y(x,t)$ the transverse displacement in the bridge plane, $\mu$ linear density, $T$ tension, $E$ Young's modulus, $S$ cross-section, $K$ radius of gyration, $\sigma$ a loss rate:

$$\frac{\partial^2 y}{\partial t^2}=c^2\frac{\partial^2 y}{\partial x^2}-\frac{ESK^2}{\mu}\frac{\partial^4 y}{\partial x^4}-2\sigma\frac{\partial y}{\partial t},\qquad c=\sqrt{T/\mu}.$$

The fourth-order term is *stiffness*: it makes the partials inharmonic,

$$f_n = n f_0\sqrt{1+Bn^2},\qquad B=\frac{\pi^2 E S K^2}{T L^2},$$

which is why a sitar's upper partials are already stretched before the bridge touches anything. Typical $B$ for a steel string of this gauge: $10^{-4}$–$10^{-3}$.

### 2.2 FDTD discretisation

With $\Delta x=\lambda c\,\Delta t$ and $Q=ESK^2\Delta t^2/(\mu\Delta x^4)$:

$$y_i^{\,n+1}=2y_i^{\,n}-k\,y_i^{\,n-1}+\lambda^2\big(y_{i+1}^{\,n}-2y_i^{\,n}+y_{i-1}^{\,n}\big)-Q\big(y_{i+2}^{\,n}-4y_{i+1}^{\,n}+6y_i^{\,n}-4y_{i-1}^{\,n}+y_{i-2}^{\,n}\big),$$

$$k = 1-2\sigma\Delta t .$$

Grid sizing: $f_0=f_s/(2N)$ at $\lambda=1$, so $N\approx f_s/(2f_0)$ (183 nodes for C3 at 48 kHz). **Stability** (measured, §6.6): $\lambda=1$ is *marginally* stable for $Q=0$ but diverges for any $Q>0$; use $\lambda=0.99$ and keep $Q\lesssim10^{-3}$.

The equivalent **waveguide** branch (cheaper, and the one Siddiq actually hybridises) is a bidirectional delay line of $N$ samples with

- a loop filter for frequency-dependent loss: one-pole low-pass, $H(z)=g(1+a)/(1+az^{-1})$;
- an **allpass cascade** for dispersion (Rauhala–Välimäki): $A(z)=\dfrac{a+z^{-1}}{1+az^{-1}}$ repeated $M$ times, $a$ from the target $B$;
- and the nonlinear contact segment at the bridge replaced by an FDTD stub coupled through the Krishnaswamy–Smith interface.

### 2.3 The jawari bridge as a curved obstacle

Let $d_j$ = distance in nodes from the bridge crown, $\kappa$ = curvature (displacement units per node²). Admissible region and contact law:

$$y_j \ge s_j = -\kappa d_j^{\,2},$$

$$y_j^{n+1}<s_j \;\Longrightarrow\; y_j^{n+1}=s_j,\quad y_j^{\,n}\leftarrow s_j .$$

The second half (killing the node's previous state, i.e. its velocity) is what makes the collision **inelastic** — Burridge–Kappraff–Morshedi's "one-sided inelastic constraint". Clamping the displacement only leaves the kinetic energy to reappear one step later, contact becomes permanent, and the model degenerates into a shorter string with a rigid end (measured: flux identical to the ideal string).

### 2.4 Why the sound changes with amplitude

The deepest contacted node satisfies $\kappa d_c^2\approx A$, hence

$$d_c(A)=\sqrt{A/\kappa},\qquad L_\text{eff}(A)=L-\Delta x\sqrt{A/\kappa},\qquad \frac{\Delta f}{f}\approx\frac{\Delta x\sqrt{A/\kappa}}{L}.$$

So the bridge eats a longer piece of the string on a loud pluck than on a quiet one. Consequences:

- **Pitch lean**: sharp at the attack, settling as the note decays (and, with a positional pluck, a small glide as the envelope falls). This is the same physical channel as *meend*.
- **Brightness tracks the envelope**: more stopped length ⇒ more high-partial energy destroyed per cycle ⇒ the note darkens as it gets quieter, at a rate no exponential decay law reproduces.
- **Two-stage decay**: the buzz-dominated early part and the "hollow" late part are the same string with different contact geometry.

### 2.5 Output

Radiated sound ∝ bridge force ∝ slope at the termination:

$$F_b(t)=T\left.\frac{\partial y}{\partial x}\right|_{x=L}\approx\frac{T}{\Delta x}\big(y_{N-3}-y_{N-4}\big),$$

then the body response (commuted excitation, SP-048, or a measured body IR, SP-009).

### 2.6 Taraf sympathetic bank

One delay loop per sympathetic string, tuned to the raga degree $f_k$:

$$D_k=\frac{f_s}{2f_k}\quad(\text{+ 1st-order allpass for the fraction}),\qquad y_k[n]=\tfrac12\big(y_k[n-D]+y_k[n-D-1]\big)\rho_k+g_c\,F_b[n]\,\xi_k,$$

$\rho_k$ per string ⇒ T60 of seconds; $\xi_k\sim U(0.7,1)$ de-correlates the bank so it is not a chorus; $g_c\le0.05$ keeps it stable. Because the bank is *tuned*, it answers the degrees the pluck actually contains: HOME is physically louder and longer than a chromatic neighbour. Typical sitar: 11–13 taraf strings over one to two octaves of the raga.

---

## 3. Reference implementation (NumPy)

```python
import numpy as np

FS = 48000
N  = 183                      # f0 = FS/(2N) = 131.15 Hz (C3)
F0 = FS / (2 * N)

def jawari_pluck(amp=0.004, kappa=1.2e-5, Q=3e-4, lam=0.99, sig=2e-5,
                 pluck_pos=0.2, dur=2.4, cn=48):
    """Render one plucked jawari string. Returns the bridge-force signal."""
    NS = int(dur * FS)
    idx = np.arange(N - 1 - cn, N - 2)
    bound = -kappa * (N - 2 - idx).astype(float) ** 2

    y = np.zeros(N)
    p = int(pluck_pos * (N - 1))
    y[:p + 1] = amp * np.arange(p + 1) / p
    y[p:]     = amp * (N - 1 - np.arange(p, N)) / (N - 1 - p)
    ym = y.copy()

    k, lam2 = 1.0 - 2.0 * sig, lam * lam
    lo, hi = 2, N - 2
    out = np.empty(NS)

    for n in range(NS):
        lap1 = np.zeros(N)
        lap1[lo:hi] = y[lo + 1:hi + 1] - 2 * y[lo:hi] + y[lo - 1:hi - 1]
        yn = 2 * y - k * ym + lam2 * lap1
        if Q:                                        # stiffness / dispersion
            lap2 = np.zeros(N)
            lap2[lo:hi] = (y[lo + 2:hi + 2] - 4 * y[lo + 1:hi + 1] + 6 * y[lo:hi]
                           - 4 * y[lo - 1:hi - 1] + y[lo - 2:hi - 2])
            yn -= Q * lap2
        yn[0] = yn[1] = 0.0                          # nut
        yn[N - 2] = yn[N - 1] = 0.0                  # bridge clamp
        pen = yn[idx] < bound                        # NB: fancy index -> copy
        if pen.any():
            jj = idx[pen]
            yn[jj] = bound[pen]                      # inelastic stop
            ym[jj] = bound[pen]                      # momentum killed
        ym, y = y, yn
        out[n] = y[N - 3] - y[N - 4]                 # bridge force
    return out


def taraf_bank(excitation, ratios, gain=0.02, rho=0.9995, seed=0):
    rng = np.random.default_rng(seed)
    acc = np.zeros_like(excitation)
    for r in ratios:
        D = max(2, int(round(FS / (F0 * r))))
        buf = np.zeros(D)
        prev = 0.0
        xi = rng.uniform(0.7, 1.0)
        for n, x in enumerate(excitation):
            v = buf[0]
            buf[:-1] = buf[1:]
            buf[-1] = 0.5 * (v + prev) * rho + gain * x * xi
            prev = v
            acc[n] += v
    return acc
```

**Cost.** 183 nodes × 48 000 samples = 8.8 M node-updates per second of audio; a 2.4 s note takes ≈2.2 s in this naive per-sample loop (≈1.1× real time). For a full instrument (6–7 baj + 3 chikari + 13 taraf) vectorise the node axis into a 2-D array (`y[v, i]`, one row per string) and render all strings in one loop — the per-sample Python overhead then amortises over ~20 strings, giving a comfortable real-time factor.

---

## 4. Musical Elements Framework

**PITCH.** Set by the string ($T,\mu,N$), then deliberately destabilised: $L_\text{eff}(A)$ leans sharp at the attack, and $B$ stretches the partials. Written glides/portamento pass through honestly; the model adds its own micro-lean that no sample-based pitch-shift reproduces.

**RHYTHM.** The collision rate is $2f_0$ — buzz is rhythm at audio rate. It shapes the envelope, not the onset; pluck position sets how much high-partial energy meets the bridge. Chikari strings take their own metric pattern (the "jhin" of a gat); baj strings carry the melodic rhythm.

**HARMONY.** The taraf bank is tuned to the raga: it converts tonal gravity into physical resonance (HOME rings, chromatic neighbours do not). Voicing and register change the halo because the bank is excited by the pluck's spectrum, not by a send.

**STRUCTURE.** κ (jawari amount), pluck position and taraf gain are automatable per column: alap (wide contact, long ring) → jhala (chikari pattern, tighter contact). Taraf ring-out crosses section seams, so boundaries are audible as decay, not cuts.

**TEXTURE.** Two independent generators — broadband amplitude-gated collision (edge, grit, upper-mid thickness) and narrow-band pitched taraf halo (shimmer) — both causal, so texture follows gesture rather than being applied to it.

---

## 5. UnitMatrix integration

| matrix element | maps to |
|---|---|
| **Rows (voices)** | `sitar_baj` (6–7 strings, polyphonic), `chikari` (2–4 drone strings), `taraf` (auto-driven, no events) |
| **Columns (sections)** | `kappa`, `pluck_pos`, `taraf_tuning` (raga degree set), `taraf_gain`, `body_ir` |
| **Cells (MusicUnit)** | plucks: `pitch` → string+fret (fret shortens $N$), `volume` → pluck amplitude $A$ (**this is the nonlinearity**), `start_tick` → pluck instant, `end_tick` → finger damping (kills string state, not a fade) |

Dispatch: `produce(midi_path, method="SP-125", params={"kappa":1.2e-5, "taraf":"Yaman", "pluck_pos":0.18, "taraf_gain":0.35, "oversample":2})`. Ticks → samples via the composer's tempo; render each string, sum rows, drive the taraf bank from the summed bridge force, then the standard post chain (SP-006 already applied in the tick domain; SP-007/SP-103/SP-107/SP-122 downstream). Zero-drift: fixed-length sample-in/sample-out; ring-out tails crossfade into the neighbouring cell; no event is retimed.

---

## 6. Measured prototype behaviour (executed 2026-10-26)

Environment: `$MUSICOM_PYTHON`, 48 kHz, $N=183$, $f_0^\text{nominal}=131.15$ Hz, 2.4 s, $\kappa=1.2\times10^{-5}$, $Q=3\times10^{-4}$, seed 0.

| case | contact hits | envelope flux | centroid start→end | Δ | H5/H1 | H10/H1 |
|---|---|---|---|---|---|---|
| ideal ($\kappa=0$, $Q=0$) | 0 | 0.144 | 6472 → 6470 Hz | 0 % | 0.055 | 0.010 |
| dispersion only ($Q=3\times10^{-4}$) | 0 | 0.144 | 6485 → 6484 Hz | 0 % | 0.055 | 0.011 |
| **jawari, inelastic** | 36 218 | **0.590** | **5712 → 3909 Hz** | **−32 %** | **0.194** | **0.094** |
| jawari + taraf bank | 36 218 | 0.591 | 5382 → 1525 Hz | −72 % | — | — |

Amplitude sweep: $A$=0.001/0.002/0.004/0.008 → hits 4 533 / 14 788 / 36 218 / 67 530, H5/H1 0.08 / 0.15 / 0.19 / 0.30, centroid drop 40 / 41 / 32 / 24 %.

Determinism: identical seeds → bit-identical buffers. Peak amplitude finite everywhere; cost 21.1 M node-updates per 2.4 s note.

### 6.1–6.6 Failure modes found while building it (all reproduced)

1. **Fancy-index copy**: `sub = yn[idx]; sub[pen] = ...` writes to a copy → the model silently renders the *ideal* string. Symptom: identical metrics for $e=0$ and $e=0.95$. Fix: `yn[idx[pen]] = ...`.
2. **λ=1 + Q>0 ⇒ NaN** within 48 000 samples. λ=0.99 stable to $Q\approx10^{-3}$; NaN at $Q=5\times10^{-3}$.
3. **Wrong damping sign**: using $-a\,y^{n-1}$ with $a=2bd-1$ gives a root at $\lambda=2$ → overflow to $10^5$ in 20 samples. Correct: coefficient $\approx-1$ on $y^{n-1}$.
4. **Elastic restitution is the wrong branch**: $e=0.3$ flips the centroid behaviour (5712 → 7911 Hz, i.e. brightening); $e=0.95$ → 11 600 Hz. Real jawari is inelastic.
5. **Long hard clamp = short string**: 40 fully clamped nodes reproduce the ideal spectrum (flux 0.142) because the contact never releases.
6. **Boundary detune**: measured $f_0=123.0$ Hz vs 131.15 nominal (−111 cents) from the 2-node clamps; and naive FFT peak-picking reported 260.7 Hz (H2) at high amplitude — use YIN/autocorrelation.

---

## 7. References

1. Siddiq, S. (2012). A Physical Model of the Nonlinear Sitar String. *Archives of Acoustics* 37(1), 73–79. DOI 10.2478/v10168-012-0010-y.
2. Raman, C. V. (1921). On some Indian stringed instruments. *Proc. Indian Assoc. Cult. Sci.* 7, 29–33.
3. Burridge, R., Kappraff, J., Morshedi, C. (1982). The Sitar String, a Vibrating String with a One-Sided Inelastic Constraint. *SIAM J. Appl. Math.* 42(6), 1231–1251. DOI 10.1137/0142086.
4. Vyasarayani, C. P., Birkett, S., McPhee, J. (2009). Modeling the dynamics of a vibrating string with a finite distributed unilateral constraint: Application to the sitar. *JASA* 125(6), 3673–3682. DOI 10.1121/1.3123403. Also *JASA* 123, 3380 (2008), DOI 10.1121/1.2934018 (3-D impact with friction).
5. Taguti, T. (2007). Numerical Simulation of Vibrating String Subject to Sawari Mechanism. *19th ICA*, Madrid, 1–6.
6. Valette, C., Cuesta, C. (1993). *Mécanique de la corde vibrante*. Hermès, Paris.
7. Smith, J. O. (1992). Physical Modeling Using Digital Waveguides. *Computer Music Journal* 16(4), 74–91.
8. Rauhala, J., Välimäki, V. (2006). Dispersion Modeling in Waveguide Piano Synthesis Using Tunable Allpass Filters. *Proc. DAFx-06*, 71–76.
9. Karjalainen, M. (2002). 1-D Digital Waveguide Modeling for Improved Sound Synthesis. *Proc. ICASSP*, 1869–1872.
10. Krishnaswamy, A., Smith, J. O. (2003). Methods for Simulating String Collisions with Rigid Spatial Obstacles. *IEEE WASPAA*, 233–236.
11. Fletcher, N. H., Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer.
12. Datta, A. K., Sengupta, R., Banerjee, K., Ghosh, D. (2018). Physical and Mechanical Properties of Components of Tanpura. *Signals and Communication Technology*, Springer Singapore. DOI 10.1007/978-981-13-2610-3_4.
13. Shaping the resonance. Sympathetic strings in Hindustani classical instruments. *Proc. Meetings on Acoustics* 21 (2014). DOI 10.1121/1.4896467.
14. Sound synthesis model incorporating sympathetic vibration of strings. *JASA* 101 (1997). DOI 10.1121/1.419832.
15. Bilbao, S. (2009). *Numerical Sound Synthesis*. Wiley (stability of explicit stiff-string schemes, CFL conditions).
