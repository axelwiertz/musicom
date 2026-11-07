# Report SP-136 — Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM)

**Run date:** 2026-11-07 (scheduled cron research job)
**Status:** COMPLETE — detail section appended, summary row inserted, standalone file written, verification passed.

---

## 1. Identity card

| Field | Value |
|---|---|
| **Method ID** | **SP-136** |
| **Method name** | Syahi-Loaded Tension-Modulated Membrane Synthesis |
| **Acronym** | SLTM |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md) |
| **Category** | Synthesis Engines → Physical Modeling → Pitched Membrane |
| **One-line description** | Solves the density-graded circular-membrane eigenproblem of a tabla head so the syahi mass load turns the Bessel-zero series into 1:2:3:4:5, then renders each stroke as a modal sum whose frequencies all scale with √T(t) — the bayan's heel-pressure glide. |
| **Candidate code path** | `sound/synthesis/tabla_membrane.py` (`SyahiProfile`, `RadialMembraneSolver`, `ModalDrum`, `TensionGlide`, `StrikeExcitation`, `TablaVoice`) |
| **Dispatch** | `produce(midi_path, method="SP-136", ...)` via `workflows/musicom_workflow.py` |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-136_SLTM.md` (10 238 B) |
| **Report file** | `/opt/data/projects/Research/CompositionMethods/report_SP-136.md` |
| **Prototype** | `_web136/sp136_verify.py`, log `_web136/sp136_verify_output.txt`, audio `_web136/sp136_demo.wav` (92 610 samples, 185 264 B) |
| **methods_db.md lines — before** | **30 547** |
| **methods_db.md lines — after** | **30 667** |
| **Delta** | **+120** (119-line method section + 1 summary row) |
| **Section location** | lines **30 549–30 667** (EOF), header `# Sound Production Method SP-136 — Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM)` |
| **Table row location** | line **345**, immediately after the `SP-135` row |
| **ID resolution** | table scan max = **SP-135**; file scan (`sound_method_SP-*.md`, `report_SP-*.md`) max = SP-135 → new ID **136**; `grep SP-136` before entry returned 0 hits. (Note: `report_137.md` is the *composition* method 137 — tropical algebra — a separate numbering namespace, not an SP id.) |
| **Next free SP ID** | **SP-137** |

---

## 2. Full summary-table row (exactly as inserted, line 345)

```
| **SP-136** | Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM) | **Synthesis Engines** | Physical Tabla (Dayan/Bayan) / Pitched Harmonic Drum Timbre | Solves the density-graded circular-membrane eigenproblem of a tabla head: the syahi profile $\rho(r,\theta)=1+\frac{\sigma^2-1}{2}\left[1-\tanh\left(\frac{R-k}{\xi}\right)\right]$ turns the Bessel-zero series (1 : 1.593 : 2.136 : 2.296) into $1:2:3:4:5$ (reproduces Sathej–Adhikari Table 1 to 0.5 cent at $\sigma{=}3.125$, $k{=}0.4$). Modal synthesis $\mathcal{O}(N_{\text{modes}})$ per sample; strike-position gains $R_{mn}(r_s)\cos m\theta_s$ select the bol; bayan glide is phase-integrated $\sqrt{T(t)}$ tension modulation ($-3/-5/-7$ semitones = 0.707/0.561/0.445 tension ratio). Eccentric load splits the $m\ge1$ doublets → beating wobble. Candidate: `sound/synthesis/tabla_membrane.py`. |
```

---

## 3. Technical mechanics summary

1. **Uniform membrane** — $f_{mn}=\frac{\alpha_{mn}}{2\pi a}\sqrt{T/\sigma_s}$; Bessel ratios measured 1, 1.5933, 2.1355, 2.2954, 2.6531 (inharmonic ⇒ "thud").
2. **Syahi load** — $\rho(r,\theta)=1+\frac{\sigma^2-1}{2}[1-\tanh((R-k)/\xi)]$, $R=\sqrt{(r\cos\theta-\epsilon)^2+(r\sin\theta)^2}$; eigenproblem $-\nabla^2\psi=(\omega^2/T)\rho\psi$ ⇒ $\mathbf A\psi=\lambda\mathbf B\psi$.
3. **Verification** — radial finite-volume solve (N=1400, m=0..4) reproduces Sathej & Adhikari (2009) Table 1 smooth-model column to **max |Δ| = 0.0009 (0.5 cent)**: 1.0344, 2.0000, 3.0393, 3.0535, 4.0085, 4.1466, 4.7778, 5.0021, 5.2496; centre/edge density 9.76/1.00 at σ=3.125, k=0.4, ξ=0.091. Optimum σ=2.57, k=0.492 gives 1.0994, 2.0000, 2.9584, 3.0535, 3.9545, 4.0203, 4.9038.
4. **Modal sum** — $y=\sum g_n a_n(t)\sin\varphi_n(t)$, $\varphi_n=2\pi\int f_n\,dt$ (cumsum), $a_n=\exp(-\int d\tau/\tau_n)$.
5. **Tension glide** — $T(t)=T_0(1+\beta p(t))$, $f_n=f_n^{(0)}\sqrt{T/T_0}$, $\Delta_{st}=6\log_2(T/T_0)$; verified −3 st = 0.707, −5 st = 0.561, −7 st = 0.445, +2 st = 1.260.
6. **Excitation/bols** — $g_{mn}\propto R_{mn}(r_s)\cos(m\theta_s)|\mathrm{sinc}(\pi f_{mn}w)|$: rim → ring modes (`na`), syahi ring → m=0 (`tin`), damped centre (`ta`), bayan open + heel (`ghe`).
7. **Bayan wobble** — eccentric patch (ε>0) splits the m≥1 doublets → few-Hz beating.
8. **FDTD alternative** — $u^{n+1}=2u^n-u^{n-1}+(T\Delta t^2/\rho_i)\nabla^2_d u^n$, CFL $\Delta t\le\Delta x\sqrt{\rho_{\min}/(2T)}$.
9. **Prototype audio** — `na` centroid 5660 Hz (0.9 s), `ghe` centroid 3066 Hz (1.2 s, −5 st / 160 ms), peak 1.000, RMS 0.147 / 0.207.

---

## 4. Novelty / overlap audit

`grep -ci` on `methods_db.md` **before** entry: `tabla` = 0, `syahi` = 0, `bayan` = 0, `dayan` = 0, `bessel zero` = 0, `circular membrane` = 0, `tension modulat` = 1 (SP-092 nonlinear *string* prose only).

Adjacent-but-different: SP-040 FDTD (uniform material, inharmonic), SP-042 MBED (uniform-object modal bank), SP-033/SP-101 waveguides (1-D), SP-087/SP-089/SP-098 TR-808 circuit emulations, SP-120 PhISEM particle percussion. SLTM is the DB's first *density-graded circular-membrane* method with $\sqrt{T(t)}$ continuous retuning.

---

## 5. Complete section text appended (methods_db.md 30 549–30 667)

# Sound Production Method SP-136 — Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM)

### Source

- Raman, C. V., & Kumar, S. (1920). "Musical drums with harmonic overtones." *Nature* 104, 500–501 — the founding observation: the loaded Indian drum head radiates a *harmonic* series, unlike the Bessel-zero (inharmonic) series of an ideal uniform membrane.
- Ramakrishna, B. S., & Sondhi, M. M. (1954). "Vibrations of Indian musical drums regarded as composite membranes." *Journal of the Acoustical Society of America* 26(4), 523–529 — the two-region composite-membrane model (loaded central patch + bare skin), showing that a suitable mass load pulls the first modes onto integer ratios.
- Sathej, G., & Adhikari, R. (2009). "The eigenspectra of Indian musical drums." *JASA* 125(2), 831–838; arXiv:0809.1320 — the smoothly non-uniform density model adopted here: $\rho(r,\theta)=1+\frac{\sigma^2-1}{2}\left[1-\tanh\left(\frac{R(r,\theta)-k}{\xi}\right)\right]$ solved by Fourier–Chebyshev spectral collocation; optimised $\sigma=2.57$, $k=0.492$, $\xi=0.091$; Table 1 compares measured and modelled dayan eigenfrequencies.
- Malu, S. S., & Siddharthan, A. (2000). "Acoustics of the Indian Drum." arXiv:math-ph/0001030 — demonstrates that the radial density profile alone (no stiffness change) is sufficient to harmonicise the low modes.
- Rossing, T. D., & Sykes, W. A. (1982). "Acoustics of Indian drums." *Percussionist* 19, 58–67 — layer-by-layer syahi application and the measured harmonicity progression per layer (the construction data Sathej & Adhikari optimise against).
- Rossing, T. D. (2000). *Science of Percussion Instruments.* World Scientific — daya/bayan geometry, syahi ≈ 8× the areal density of the goatskin and ≈ a quarter of the head area, kinar edge flap damping the high modes, bayan heel-pressure pitch modulation.
- Patranabis, A., Banerjee, K., Midya, V., Chakraborty, S., Sanyal, S., Banerjee, A., Sengupta, R., & Ghosh, D. (2015). "Harmonic and Timbre Analysis of Tabla Strokes." arXiv:1510.04880 — LTAS-based timbre measurements of nine bols across five tablas.
- Bilbao, S. (2009). *Numerical Sound Synthesis.* Wiley — variable-coefficient FDTD for membranes with non-uniform $\rho$, the grid-level alternative to modal synthesis.
- Verified prototype for this document: `_web136/sp136_verify.py`, log `_web136/sp136_verify_output.txt`, audio `_web136/sp136_demo.wav` (92 610 samples @ 44.1 kHz, 185 264 B). Measured: uniform membrane ratios **1, 1.5933, 2.1355, 2.2954, 2.6531, 2.9173, 3.1555, 3.5001, 3.5985**; loaded head with $\sigma{=}3.125$, $k{=}0.4$, $\xi{=}0.091$ gives **1.0344, 2.0000, 3.0393, 3.0535, 4.0085, 4.1466, 4.7778, 5.0021, 5.2496** — reproducing Sathej & Adhikari's Table 1 smooth-model column (1.0345, 2.0000, 3.0393, 3.0534, 4.0086, 4.1463, 4.7784, 5.0023, 5.2491) to **max |Δ| = 0.0009 (≈0.5 cent)**; centre/edge density 9.76 / 1.00.
- Novelty check (2026-11-07): `grep -ci` on `methods_db.md` before entry: `tabla` = 0, `syahi` = 0, `bayan` = 0, `dayan` = 0, `bessel zero` = 0, `circular membrane` = 0, `tension modulat` = 1 (SP-092 nonlinear *string* prose only). Adjacent-but-different: **SP-040** FDTD (uniform-material grids, inharmonic membranes, no density grading); **SP-042** MBED (modal bank with eigenmodes of *uniform* objects); **SP-033/SP-101** waveguides (1-D strings/pipes); **SP-087/SP-089/SP-098** TR-808 circuit emulations of drum *voices*; **SP-120** PhISEM particle percussion (stochastic collisions, resonator bank — no membrane eigenvalue problem). SLTM is the DB's first *density-graded circular-membrane* method with $\sqrt{T}$ time-varying tuning.

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). SLTM turns a symbolic note (pitch, velocity, articulation, duration) into an air-pressure buffer by solving a membrane eigenproblem and integrating a modal sum; it emits samples only — no onset/duration events, no timing authority, no composition decision. It is a per-row replacement for the default source (SP-001 FluidSynth / SP-112 LASS / SP-098 analog kick …) on percussion rows. Candidate code path: `sound/synthesis/tabla_membrane.py` (modules: `SyahiProfile`, `RadialMembraneSolver`, `ModalDrum`, `TensionGlide`, `StrikeExcitation`, `TablaVoice`), dispatched from `workflows/musicom_workflow.py::produce(method="SP-136", ...)`.

### Description

A tabla head is a circular goatskin membrane loaded at the centre with the *syahi*, a layered paste of soot, iron filings and flour that is roughly eight times as dense as the skin and covers about a quarter of the head. A uniform circular membrane is stubbornly inharmonic — its modes are Bessel zeros, $1 : 1.593 : 2.136 : 2.296 : 2.653\ldots$, which is why a plain drum reads as "thud". The syahi adds mass without adding much stiffness in the low-mode regime, which lowers the fundamental far more than the upper modes and drags the first five or six partials onto an almost exact harmonic series $1\!:\!2\!:\!3\!:\!4\!:\!5$. That is the entire trick of the instrument: a drum that is also a pitched, harmonic resonator (Raman's 1920 "musical drums with harmonic overtones").

SLTM is the synthesis counterpart, in three stages:

1. **Geometric/eigen stage (per drum, cached)** — solve the non-uniform-density membrane eigenproblem for the drum's head ($\sigma$, $k$, $\xi$, radius, tension) and take the lowest 8–16 modes: frequencies $f_n$, radial mode shapes, and a per-mode impulse gain from the strike position.
2. **Excitation stage (per note)** — a short contact pulse (2–8 ms) plus a band-limited noise burst is projected onto the modes with gains $g_{mn}\propto R_{mn}(r_s)\cos(m\theta_s)$; different strike positions therefore select different mode sets, which is exactly what the bol vocabulary does ($na$ = rim, $tin$/$tun$ = syahi ring, $ghe$ = open bayan).
3. **Tension-modulation stage (per note, continuous)** — the bayan's pitch is not fixed: the heel of the hand presses the unloaded part of the head, stretching it and raising $T$. Since $f_n\propto\sqrt{T}$, a played glide is a $\sqrt{T(t)}$ contour applied to *all* modes simultaneously, integrated as a phase, not a frequency.

The result is a physically-grounded, cheap ($\mathcal{O}(N_{\text{modes}})$ per sample) drum voice that is pitched, harmonically tuned, and continuously bendable — a percussion row that can carry harmony instead of only marking rhythm.

### Technical Mechanics

**1. Ideal circular membrane.** With areal density $\sigma_s$ (kg/m²) and uniform tension $T$ (N/m), the transverse displacement obeys

$$\frac{\partial^2 u}{\partial t^2}=c^2\nabla^2u,\qquad c=\sqrt{T/\sigma_s},\qquad u(a,\theta,t)=0$$

Separation $u=R(r)\Theta(\theta)e^{j\omega t}$ gives $\Theta=\cos m\theta$ and $R=J_m(k_{mn}r)$ with $k_{mn}=\alpha_{mn}/a$, $\alpha_{mn}$ the $n$-th positive zero of $J_m$:

$$f_{mn}=\frac{\alpha_{mn}}{2\pi a}\sqrt{\frac{T}{\sigma_s}}$$

Bessel zeros $\alpha_{01}{=}2.40483$, $\alpha_{11}{=}3.83171$, $\alpha_{21}{=}5.13562$, $\alpha_{02}{=}5.52008$, $\alpha_{31}{=}6.38016$, $\alpha_{12}{=}7.01559$, $\alpha_{41}{=}7.58834$, $\alpha_{22}{=}8.41724$, $\alpha_{03}{=}8.65373$; normalised by $\alpha_{01}$ these are the inharmonic ratios measured in the prototype: **1, 1.5933, 2.1355, 2.2954, 2.6531, 2.9173, 3.1555, 3.5001, 3.5985**.

**2. Syahi loading as a density field.** The load is modelled as a smooth areal-density field on the unit-radius head (Sathej & Adhikari Eq. 1–2):

$$\rho(r,\theta)=1+\frac{\sigma^2-1}{2}\left[1-\tanh\left(\frac{R(r,\theta)-k}{\xi}\right)\right],\qquad R(r,\theta)=\sqrt{(r\cos\theta-\epsilon)^2+(r\sin\theta)^2}$$

$\sigma^2$ is the centre/edge density ratio, $k$ the load radius ($k^2$ = loaded area fraction; $k{=}0.492\Rightarrow 24\%\approx$ a quarter of the head), $\xi$ the edge smoothness, $\epsilon$ the eccentricity ($\epsilon{=}0$ daya, concentric; $\epsilon>0$ bayan, off-centre load). Substituting into the wave equation with $u=\psi(\mathbf r)e^{j\omega t}$ gives the **generalised eigenproblem**

$$-\nabla^2\psi=\frac{\omega^2}{T}\,\rho(\mathbf r)\,\psi\quad\Longleftrightarrow\quad \mathbf A\boldsymbol\psi=\lambda\,\mathbf B\boldsymbol\psi,\ \ \mathbf B=\operatorname{diag}\big(\rho(\mathbf r_i)\big)$$

with Dirichlet $\psi(a)=0$. Because mass is added and stiffness is (to first order) unchanged, every eigenvalue falls, and the *low* ones fall most — the mechanism that compresses the series toward integers. Verified with a radial finite-volume discretisation ($N{=}1400$ cells, $m{=}0\ldots4$): $\sigma{=}3.125$, $k{=}0.4$, $\xi{=}0.091$ yields 1.0344, 2.0000, 3.0393, 3.0535, 4.0085, 4.1466, 4.7778, 5.0021, 5.2496 versus the published 1.0345, 2.0000, 3.0393, 3.0534, 4.0086, 4.1463, 4.7784, 5.0023, 5.2491 (max error 0.5 cent), with centre/edge density 9.76/1.00 — i.e. the head's first nine modes sit on $1,2,3,3,4,4,4.8,5,5.25$ instead of the Bessel set. The paper's unconstrained optimum is $\sigma{=}2.57$, $k{=}0.492$, $\xi{=}0.091$, which measures 1.0994, 2.0000, 2.9584, 3.0535, 3.9545, 4.0203, 4.9038 (fundamental 10% sharp, upper modes within ±2%) — the trade-off is inherent: the load that harmonicises mode 2–5 slightly over-sharpens mode 1.

**3. Modal synthesis core.** Once $f_n$, decay $\tau_n$ and gain $g_n$ are known, the note is a sum of damped sinusoids with *time-varying* frequency:

$$y(t)=\sum_n g_n\,a_n(t)\,\sin\!\Big(2\pi\!\int_0^t f_n(\tau)\,d\tau+\phi_n\Big),\qquad a_n(t)=\exp\!\Big(-\int_0^t\frac{d\tau}{\tau_n(\tau)}\Big)$$

Numerically the phase is a running accumulator, $\varphi_n[i+1]=\varphi_n[i]+2\pi f_n[i]/f_s$ (a `np.cumsum`), never $\sin(2\pi f(t)\,t)$ — the latter has instantaneous frequency $f+t\,\dot f$, which overshoots the glide by up to a factor of two at the end of a 150 ms bend. Per-mode decay follows the usual frequency-dependent loss: low modes 0.4–1.0 s on the daya, high modes 40–150 ms, with the kinar edge flap modelled as extra damping on $n\ge 3$ ($\tau_n^{-1}=\tau_{n,\text{body}}^{-1}+\kappa_{\text{kinar}}f_n^{2}$).

**4. Tension modulation (the bayan glide).** Heel pressure $p(t)\in[0,1]$ stretches the unloaded sector, so

$$T(t)=T_0\big(1+\beta\,p(t)\big),\qquad f_n(t)=f_n^{(0)}\sqrt{T(t)/T_0},\qquad \Delta_{\text{st}}=12\log_2\sqrt{T/T_0}=6\log_2(T/T_0)$$

The mapping is **quadratic in pitch, not linear**: $T/T_0=0.5$ is $-6.02$ semitones, $0.707$ is $-3$, $0.561$ is $-5$, $0.445$ is $-7$ (all four verified numerically). A tabla $ghe$ is typically a 3–7 semitone bend over 100–250 ms, i.e. tension excursions of 30–55%. Because the bend scales *every* mode by the same $\sqrt{T(t)}$, the harmonic series stays harmonic during the glide — which is why the bayan keeps its pitch identity while sliding, and why a naive per-partial pitch-shift that stretches the spectrum instead sounds wrong.

**5. Excitation and the bol vocabulary.** A strike at $(r_s,\theta_s)$ with contact half-width $w$ projects onto mode $(m,n)$ with

$$g_{mn}\propto R_{mn}(r_s)\cos(m\theta_s)\,\cdot\,\big|\operatorname{sinc}(\pi f_{mn}w)\big|$$

so a rim strike ($r_s\to a$) excites the $m{\ge}1$ ring modes ($na$, bright, short), a syahi-ring strike excites $m{=}0$ strongly ($tin$/$tun$, pitched), and a centred, damped strike gives the closed $ta$. The contact pulse also injects a noise burst whose bandwidth must be limited to the modelled mode range ($\lesssim 8$ kHz), with amplitude and brightness both scaling with velocity (harder = brighter, as measured in the LTAS studies of tabla strokes).

**6. Eccentric load and the bayan wobble.** For $\epsilon>0$ the load is off-centre, so the $m{\ge}1$ doublets ($\cos m\theta$/$\sin m\theta$) split into two close frequencies $\Delta f$; the two near-degenerate modes beat at $\Delta f$ (typically a few Hz), producing the characteristic wavering, "talking" quality of an open bayan. A concentric model cannot produce this — it is the audible signature of the asymmetry.

**7. Grid alternative (variable-coefficient FDTD).** For nonlinear coupling, membrane-shell interaction or visual/physical coupling, discretise directly:

$$\rho(\mathbf r)\,\frac{\partial^2 u}{\partial t^2}=T\nabla^2u\;\Longrightarrow\;u^{n+1}=2u^n-u^{n-1}+\frac{T\,\Delta t^2}{\rho_i}\nabla^2_d u^n$$

with the 2-D CFL bound $\Delta t\le \Delta x\sqrt{\rho_{\min}/(2T)}$ — the *edge* (lightest) region sets the step, so a syahi-loaded head is cheaper than a uniform one at the same $T$. Modal synthesis is $\mathcal{O}(N_{\text{modes}})$ per sample and is the default; FDTD is reserved for collisions and strong nonlinearity.

### Musical Elements Framework

- **PITCH**: pitch is geometric, not tabled: $f_0\propto(\alpha_{01}/a)\sqrt{T/\sigma_s}$, and the *dayan is tuned to the tonic* ($Sa$) by adjusting the strap tension via the $gatta$ blocks, so one row can be pinned to the key. The syahi makes the partials harmonic, so the drum is a pitched instrument that can double a bass line or carry a pedal. Continuous pitch exists only through tension modulation (the bayan glide): a $\sqrt{T(t)}$ contour, re-derived per note, never a post-hoc pitch-shift. Two drums give two independent pitch anchors (dayan = tonic/dominant, bayan a fifth to an octave below).
- **RHYTHM**: the strike is a sample-exact transient at an absolute tick; the bol sequence ($dha$, $dhin$, $tin$, $na$, $ta$, $ghe$, $ke$) is a rhythmic vocabulary whose articulation is a $(r_s,\theta_s,w,\text{damping})$ tuple, not a MIDI program change. The decay is part of the rhythm: a $ghe$ occupies 0.6–1.2 s of tail, so cells must budget tail time (or deliberately overlap tails for density).
- **HARMONY**: because modes 2–5 are near-integer, the drum's spectrum is consonant with itself and with the ensemble — tuning the dayan to $Sa$ makes every stroke reinforce the tonic; tuning it to the dominant and playing the bayan on $Sa$ gives a two-note drone pair. This is the point of Raman's harmonic drum: percussion that participates in harmony rather than only in rhythm.
- **STRUCTURE**: retuning $T_0$ between sections is a key change performed by the drum (a section-level parameter, not a note-level one); the bayan glide is a cadential gesture (bend down into the next section, or up as a pickup); kinar damping can be increased per section to dry out the texture for a bridge.
- **TEXTURE**: the syahi contrast $\sigma$ is a timbre macro — $\sigma\to1$ gives an inharmonic, tom-like thud, $\sigma\approx2.5$–$3.1$ gives the pitched, bell-like tabla ring; strike position chooses which mode family lights up (ring modes = metallic, $m{=}0$ = round and pitched); the strike-noise/mode ratio sets "skin" vs "tone". All four are continuous parameters, which makes SLTM a morphable percussion voice rather than a sampled one.

### UnitMatrix Integration

**Voices = rows = drums.** Row $v$ carries `{drum: daya|bayan, sigma, k, xi, epsilon, radius, T0, f0, strike: {rs, theta, w}, decay: {tau0, kinar}, glide: {beta_st, ms, shape}, seed}`. Each row solves (or loads from cache) its own eigenproblem — a daya row has $\epsilon{=}0$, a bayan row $\epsilon{>}0$ and a glide map. Percussion rows normally sit on channel 9; SLTM rows bypass FluidSynth entirely and write their own buffer, then are summed with the pitched rows.

**Sections = columns = tuning/damping states.** Column $j$ holds `{T_scale (retune: section key change), kinar_scale (dry/wet per section), glide_default}`. A column change is a *retuning*, applied at the section seam while the tail of the previous stroke rings out — implement as a per-cell $T_0$ multiplier, never as a mid-tail frequency jump (that clicks).

**Cells = MusicUnit.** Each `MusicEvent` maps to one stroke: `pitch` → $f_0$ (i.e. $T_0$ for a fixed head), `volume` → amplitude + strike brightness, `start_tick`/`end_tick` → strike time and damping/gate, and the articulation (recommended: a per-event `bol` tag or a CC-coded index) → `(r_s, θ_s, w, glide)`:

| bol | strike | modes excited | character |
| :--- | :--- | :--- | :--- |
| `na` | rim, `r_s≈0.9a` | $m{=}1,2$ ring | bright, dry, short |
| `tin` | syahi ring | $m{=}0$ + ring | pitched, bell-like, medium |
| `ta` | syahi centre, damped | low $m{=}0$ | closed, thuddy |
| `ghe` | bayan open + heel | low modes + glide | deep, bending, long |
| `ke` | bayan heel slap | noise + low | dry click, no pitch |

**Produce dispatch:** `produce(midi_path, method="SP-136", params={"rows":[{"drum":"daya","sigma":3.125,"k":0.4,"xi":0.091,"f0":146.8,"strike":{"rs":0.35,"theta":0.0,"w":0.004},"decay":{"tau0":0.45,"kinar":1.0}}, {"drum":"bayan","sigma":2.57,"k":0.492,"xi":0.091,"epsilon":0.35,"f0":73.4,"glide":{"beta_st":-5,"ms":160}}], "columns":{"A":{"T_scale":1.0,"kinar_scale":1.0},"B":{"T_scale":1.122,"kinar_scale":0.6}}, "fs":44100})`. Stage order: **eigen solve (cached per row/column)** → **SLTM per cell** replaces the per-row source → per-row EQ (SP-007) → spatialize (SP-021/SP-053) → room (SP-009/SP-032/SP-075) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Use SLTM where a drum must be *pitched and bending*; use SP-001/SP-098 for sampled or circuit-faithful drums; use SP-042 MBED if only inharmonic metal/wood modes are wanted.

### Pitfalls

1. **Do not judge harmonicity against the fundamental.** The loaded head's $\psi_{01}$ is 3–10% sharp, so normalising by it gives 1.82–1.95 instead of 2 for the second mode and makes a correct model look broken (this exact mistake was made and corrected during verification). Compare against the *first overtone* (or fit to integers), and accept that the fundamental is the one mode the syahi over-sharpens — the ear still hears the drum's pitch from the mode pattern.
2. **Glide must be a phase integral, not $\sin(2\pi f(t)t)$.** The naive form has instantaneous frequency $f+t\dot f$ and overshoots a 150 ms bend by up to ~2×; use $\varphi[i{+}1]=\varphi[i]+2\pi f[i]/f_s$.
3. **Tension → pitch is $\sqrt{\ }$.** Halving tension costs 6.02 semitones, not 12; a linear mapping makes every bend twice as deep as intended (verified: $-3$ st = 0.707, $-5$ st = 0.561, $-7$ st = 0.445).
4. **Syahi is mass, not stiffness.** Modelling the patch as a stiffer region raises the modes and destroys the effect; the density contrast $\sigma^2$ (6.6–9.8) is the operative parameter, and adding stiffness on top is a second-order correction only.
5. **Eccentric load is not decoration.** With $\epsilon{=}0$ the $m{\ge}1$ doublets stay degenerate and the bayan loses its beating "wobble"; the off-centre patch is what splits them.
6. **Fixed per-mode decays fight the glide.** Stretching the head changes its losses; integrate the envelope $\exp(-\int d\tau/\tau_n(\tau))$ and let $\tau_n$ shorten as $T$ rises, or long bends end with an unnaturally frozen tail.
7. **Strike noise must be band-limited and velocity-coupled.** White clicks outside the mode range read as a sample-layer artefact; low-pass at the highest modelled $f_n$ and scale both level and bandwidth with velocity.
8. **Tail vs zero-drift.** A drum tail outlives its note and often its cell. Render the tail into the cell buffer, fade 5–20 ms at the section seam or let it ring into the next cell via a carry buffer — never trim the buffer to the note end and never let a later section's retune retro-modify a ringing tail (that clicks).
9. **Cache the eigenproblem.** A 1400-node solve per note is ~1.4 s; per drum/column it is done once, and the $(\sigma,k,\xi,\epsilon)$ tuple is the cache key. Store $f_n,\tau_n,g_n$, not the matrices.
10. **FDTD stability is set by the lightest region.** With graded density the CFL bound uses $\rho_{\min}$ (the bare edge), so a heavily loaded head is *cheaper* at the same tension — but a solver tuned on a uniform head will blow up.
11. **Aliasing at high tuning.** A small daya tuned high pushes mode 9 near 1.3 kHz (safe), but adding 20+ modes at 44.1 kHz or retuning up two octaves can cross Nyquist — band-limit the mode list by $f_s/2$, or oversample ×2.
12. **Do not confuse SLTM with its neighbours.** SP-040 FDTD and SP-042 MBED use uniform material (inharmonic by construction); SP-087/SP-089/SP-098 emulate analog drum *circuits*; SP-120 is stochastic particle percussion. SLTM's distinguishing content is the density-graded eigenvalue problem plus $\sqrt{T(t)}$ continuous retuning of an otherwise harmonic mode set.

---

## 6. Quirks / pitfalls hit during this run

1. **ID namespace confusion.** `report_137.md` exists and documents *composition* method 137 (Tropical Max-Plus Algebra, layer: concrete). The composition methods use a bare numeric ID (`| **137** |`), while sound-production methods use `SP-NNN`. The authoritative SP max was 135 in both the table and the `sound_method_SP-*.md` file scan → SP-136. Do not treat `report_137.md` as an SP id.
2. **Two `\` classes of patch bug avoided.** The row was inserted with the `patch` tool anchored on the tail of the SP-135 row (`...wavenet_synthesis.py`. |` + blank lines + `# Higher-Order Ambisonics`). Post-check: `grep -c '\\\\'` over the new row and new section = **0** (single backslashes everywhere), and the row starts with a single `|` (no `||` prefix). Verified by `awk 'NR==345'`.
3. **Append-at-EOF ordering.** `cat >>` puts SP-136 after the Method-137 composition section that already sits at EOF (30464+), so the SP block is not strictly contiguous with SP-130–135. Grep confirms exactly one `# Sound Production Method SP-136` header and one `| **SP-136** |` table row.
4. **Normalisation trap (real, found by the prototype).** The first verification run sorted all modes and normalised by the lowest one (m=0,n=1), giving ratios 1 / 1.819 / 2.691 / 2.777 and a bogus "1.40 semitone deviation". Sathej & Adhikari normalise so that ψ11 = 2.00 (i.e. by *half the first overtone*); with that scale the solver reproduces their Table 1 to 0.0009. This became Pitfall 1 in the method section — a naive reader would conclude the model is broken.
5. **Sanity anchor for the solver.** Uniform-density case must return the Bessel zeros: measured 2.404, 3.830, 5.134, 5.518, 6.380 — matched to 3 decimals before trusting the graded solve.
6. **Glide equation trap.** `sin(2πf(t)·t)` has instantaneous frequency f + t·ḟ; the prototype uses a `cumsum` phase accumulator. Tension-table values (−3/−5/−7 st → 0.707/0.561/0.445) are computed, not quoted.
7. **FluidSynth not used.** SLTM writes its own float/16-bit buffer; nothing in the pipeline depends on a SoundFont for this row, so no `-g 1.2` tail-truncation concern. Demo WAV verified at 185 264 B / 92 610 frames @ 44.1 kHz.
8. **No temp file left behind** (`_temp_sp136.md` removed after `cat >>`). Only `_web136/` (script, log, demo audio) persists as the verification record.

**Next free SP ID: SP-137.**
