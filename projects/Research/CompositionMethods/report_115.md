# Report 115 — Keplerian Orbital Resonance Composition (KORC)

**Registered:** 2026-10-14 · **Job:** scheduled cron (music research agent) · **DB:** `methods_db.md`

---

## Method identity

- **Method ID:** 115 (next free ID after scanning; max pre-existing = 114 FSBC)
- **Name:** Keplerian Orbital Resonance Composition (KORC)
- **Paradigm:** **Nature-Led**
- **LAYER:** **concrete** (generates concrete rhythmic onsets + pitch events filling UnitMatrix cells; NOT abstract — emits `MusicUnit` events, not pitch-pool subsets; NOT absolute — no sound production)
- **One-line description:** Each UnitMatrix voice becomes a planet on an elliptical orbit — Kepler's three laws generate pitch contour (1st law ellipse r(ν)=a(1−e²)/(1+e·cos ν)), rubato onsets (2nd law equal-areas time law t=(P/2π)(E−e·sin E), giving the ((1+e)/(1−e))² rush/linger ratio), register/scale (3rd law P²∝a³ → log₂P pitch), and harmony/macro-form (mean-motion resonances 2:1, 3:2, Laplace 4:2:1 → polyrhythms, conjunction epochs as cadence schedule, anti-aligned apsides as tension pendulum) — reproducing Kepler's 1619 *Harmonice Mundi* interval table (Saturn 5:4, Jupiter 6:5, Mars 3:2, Earth 16:15, Venus 24:25) as direct physics.

## Summary-table row (as inserted at DB line 125)

```
| **115** | concrete | Keplerian Orbital Resonance Composition (KORC) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Kepler interval-graded) | Continuous / Fluid | Macro / Orbital Period | $O(N)$ per event (closed-form Kepler time) | Each UnitMatrix voice = a planet on an elliptical orbit; Kepler's 1st law r(ν)=a(1−e²)/(1+e·cos ν) sweeps pitch contour; 2nd law (equal areas) yields exact onset times t=(P/2π)(E−e·sin E) — events crowd at perihelion, spread at aphelion ("rush/linger" rubato, ratio ((1+e)/(1−e))² = the Harmonice Mundi interval table: Saturn 5:4, Jupiter 6:5, Mars 3:2, Earth 16:15, Venus 24:25); 3rd law P²∝a³ → log₂P register scale (NASA exoplanet sonification practice); mean-motion resonances (2:1, 3:2, Laplace 4:2:1 Io–Europa–Ganymede) → polyrhythmic hierarchy, periodic conjunction epochs = cadence schedule, anti-aligned apsides = tension oscillation. Section = synodic cycle / orbital year; macro-form = resonance-capture chain (3:2→2:1→4:2:1). Nature-Led foil to 020 SMSTC (unbound clouds) / 043 SATM (chaotic attractors); physically-sourced continuous-time sibling of 012 Euclidean / 069 Christoffel; deterministic counterpart to 045 Hawkes / 038 KOPS. |
```

## Classification details

- **Paradigm justification:** celestial mechanics — the generator integrates the real physical laws of two-body orbital motion (Kepler's 1st/2nd/3rd laws). No randomness in the core (deterministic given orbital elements), no learned parameters, no stochastic transition kernels; the dynamics of an actual natural system produce the music. Contrasts Stochastic (002 Markov, 053 Lévy), Rules-Based (012 Euclidean), AI-Driven (054 ATS).
- **Layer justification (concrete):** KORC emits concrete `MusicUnit` events: onset ticks from the 2nd-law time law (ν→E→M closed form), pitch from r(ν) contour / log₂P register, velocity from areal speed h/r². Feeds `generators/kepler_orbit_composer.py`. Follows LAYER_ARCHITECTURE.md: concrete = realization plan, unitmatrix cells (voices × sections), resolved MusicEvents, zero-drift.
- **Tonal Gravity:** Moderate (Kepler interval-graded) — no fixed key, but the velocity-ratio intervals ((1+e)/(1−e))² quantize to just harmonic-series ratios (5:4, 6:5, 3:2, 16:15, 24:25), self-consistent consonance; optional strict mode anchors pitch class via 3/2·log₂P mod 12 over a chosen root ("the star").
- **Metric Binding:** Continuous / Fluid — onset times are continuous physical times; optional quantization to 480-tpb grid with terminal-landmark padding preserves the zero-drift invariant.
- **Memory Depth:** Macro / Orbital Period — section = one orbital year or synodic cycle; macro-form = the resonance-capture chain spanning whole sections.
- **Time Complexity:** `$O(N)$` per event (closed-form Kepler time: one arctan + one sine, no iteration in the ν→t direction; Newton only needed for the t→ν inverse).

## Line-count delta

- Before: **25,188** lines (`wc -l` pre-append).
- After: **25,274** lines (`wc -l` post-append + post-row-insert).
- Delta: **+86** lines (85-line method section append + 1 summary-table row).

## Standalone file

- `/opt/data/projects/Research/CompositionMethods/method_115_KORC.md` — full write-up: Kepler law math (§1), complete mapping table (§2), Python implementation sketch with `PlanetVoice`/`ResonanceChain`/`SynodicForm`/`kepler_time`/`kepler_interval`/`nearest_just_ratio` (§3), references (§4), sibling anti-duplication relations (§5).

## Candidate code path

`generators/kepler_orbit_composer.py` — `PlanetVoice(a, e, n_events, period_ratio, root_midi, contour_span, apsidal_phase, invert_contour)` (body state: ν_k, per-event t_k via analytic ν→E→M chain, r(ν) pitch contour, areal-speed velocity), `ResonanceChain(p, q)` (commensurability + conjunction epochs), `SynodicForm(section_architectures)` (per-section θ_s: period scaling to section ticks, resonance-capture arc), plus kernels `true_anomaly_time(nu, e, P)`, `radius_at(nu, a, e)`, `kepler_interval(e)`, `period_from_axis(a, GM)`, `nearest_just_ratio(r)`. Consumed by the UnitMatrix cell-filling helper (pad to section terminal landmark → `composer.validate()` → `to_midi`). Sits beside `generators/farey_composer.py` (FSBC), the closest structural sibling.

---

## Complete method section appended to methods_db.md

(verbatim, as appended at DB lines 25192–25273)

---

### Source

[1] Kepler, J. (1619). *Harmonice Mundi* [The Harmony of the World], Book V. Linz: Johann Planck. — The founding document of algorithmic celestial music: Kepler assigns to each planet a musical interval equal to the ratio of its maximum angular velocity (perihelion) to its minimum (aphelion), measured from the Sun — Saturn ≈ 4:5 (major third), Jupiter ≈ 5:6 (minor third), Mars ≈ 2:3, Earth ≈ 15:16 (semitone, mi–fa), Venus ≈ 24:25 (diesis); all within one diesis except Mars–Jupiter (18:19). English trans. Aiton, Duncan & Field (1997), American Philosophical Society.
[2] Walker, D. P. (1964). "Kepler's Celestial Music." *Journal of the Warburg and Courtauld Institutes* 30, 249–. — Historical reconstruction of Kepler's tuning scheme (whether the "sounds" were monochords struck by planetary angels — his sectio canonis) and its derivation from Book III harmonic ratios.
[3] Voelkel, J. R. (1995). "The Music of the Heavens: Kepler's Harmonic Astronomy." *Physics Today* 48(6), 59–60. — Modern summary of Kepler's harmonic astronomy; the max/min angular-velocity ratio table.
[4] Grove Music Online, "Kepler, Johannes" — his harmony of the spheres is based on the relative maximum and minimum angular velocities of the planets measured from the Sun.
[5] "An even more 'harmonic' version of Kepler's third law." *The Physics Teacher* 61(2), 150 (AIP). — The sesquialtera form: the ratio of any two planets' periodic times is precisely the 3:2 power (sesquialtera) of the ratio of their mean distances (Kepler's own statement, *Harmonice Mundi* p. 189); period ratios derived from distance ratios.
[6] Wikipedia: "Orbital resonance." — Mean-motion commensurability p:q (n₁·p ≈ n₂·q); the Laplace resonance: Io–Europa–Ganymede mean motions in 4:2:1 commensurability (two coupled 2:1 resonances; triples satisfy n₁ − 2n₂ + ϖ ≈ 0 with anti-aligned apsides); libration about 180°.
[7] NASA SVS (2024). "Sonification of Exoplanet Discoveries by Month" (svs.gsfc.nasa.gov/5653) and NASA "5000 Exoplanets: Listen to the Sounds of Discovery." — Modern practice precedent: orbital period → guitar-note pitch (shorter period = higher pitch); the direct scientific-sonification ancestor of the P→pitch mapping below.

### Layer

**concrete** — KORC generates concrete `MusicUnit` events that fill UnitMatrix cells: onset ticks derived from the true-anomaly time law (Kepler's 2nd law, solved exactly via Kepler's equation), pitch from period/radius ratios (Kepler's 3rd law + per-planet velocity ratios), velocity from the 2nd-law areal speed. Feeds `generators/kepler_orbit_composer.py` (composite generator: `PlanetVoice`, `ResonanceChain`, `SynodicForm`). Not abstract: it emits events with pitch/onset/duration/velocity, not pitch-pool subsets. Not absolute: no sound production.

### Paradigm

**Nature-Led** — celestial mechanics. The generator integrates the real physical laws of two-body orbital motion: Kepler's 1st law (elliptical orbit, Sun at a focus), 2nd law (equal areas in equal times → non-uniform angular velocity), and 3rd law (P² ∝ a³). No randomness in the core (deterministic given orbital elements), no learning, no stochastic transition kernels — the dynamics of an actual natural system (the Solar System, any exoplanet system, or any synthetic orbital architecture) produce the music. Contrast stochastic (002 Markov, 053 Lévy), rules-based (012 Euclidean), and AI-driven (054 ATS) methods.

### Description

**Keplerian Orbital Resonance Composition (KORC)** composes by placing each UnitMatrix voice on a Keplerian orbit and reading the notation directly off the orbital dynamics. A voice = a body (planet, moon, or exoplanet) characterized by orbital elements (semi-major axis $a$, eccentricity $e$, period $P$). Three physical laws become three compositional operators:

**Kepler's 1st law — the orbit is an ellipse.** Position (radial distance and true anomaly $\nu$) at any time:
$$r(\nu) = \frac{a(1-e^2)}{1 + e\cos\nu}$$
The radial sweep $r(\nu)$ maps to pitch contour: perihelion (near the star) is the register's lowest peri-approach, aphelion the highest; the flattening of the ellipse stretches/compresses intervals.

**Kepler's 2nd law — equal areas in equal times.** Angular velocity is not constant; the planet rushes at perihelion and lingers at aphelion. The areal-speed law gives the time-position relation exactly:
$$\frac{\mathrm{d}\nu}{\mathrm{d}t} = \frac{h}{r^2}, \qquad h = \frac{2\pi a^2\sqrt{1-e^2}}{P}$$
so the time at which the body reaches true anomaly $\nu_k$ is
$$t(\nu_k) = \frac{P}{2\pi}\Big(M(\nu_k)\Big), \qquad M = E - e\sin E, \qquad \tan\frac{E}{2} = \sqrt{\frac{1-e}{1+e}}\,\tan\frac{\nu}{2}$$
($M$ = mean anomaly, $E$ = eccentric anomaly — Kepler's equation). Sampling $N$ evenly spaced true anomalies per orbit and converting to $t$ yields onsets that *crowd at perihelion* (fast, dense passages — the "rush") and *spread at aphelion* (slow, sparse — the "linger"): built-in rubato with physically exact timing, no quantization needed. Eccentricity $e$ controls rubato depth: $e=0$ (circular) = metronomic grid; $e \to 0.5$+ = dramatic Ionian-style agogic swells. **The ratio of max to min angular velocity is $((1+e)/(1-e))^2$** — and this is precisely the ratio Kepler heard as the planet's interval in *Harmonice Mundi*: Saturn $e{=}0.054 \Rightarrow \approx 5{:}4$ major third; Jupiter $e{=}0.048 \Rightarrow \approx 6{:}5$ minor third; Mars $e{=}0.093 \Rightarrow \approx 3{:}2$ fifth; Earth $e{=}0.017 \Rightarrow \approx 16{:}15$ semitone; Venus $e{=}0.007 \Rightarrow \approx 24{:}25$ diesis — all within one diesis, exactly as Kepler tabulated (Walker 1964; Voelkel 1995). KORC therefore reproduces the historical Keplerian interval table as a *direct consequence of the physics*, then turns it into composition.

**Kepler's 3rd law — P² ∝ a³.** Period governs the rate of the whole orbital cycle; the sesquialtera form (Kepler's own phrasing, AIT: the ratio of periods is the 3:2 power of the ratio of mean distances) means period ratios follow distance ratios as $P_1/P_2 = (a_1/a_2)^{3/2}$. Mapping $\log_2 P$ to pitch (NASA exoplanet-sonification practice: shorter period = higher pitch; SVS 2024) converts orbital architecture into a *scale*: a chain of bodies whose distances grow by $r$ yields periods growing by $r^{3/2}$, so pitch classes step by $\tfrac32 \log_2 r$ — the harmonic series emerges from real orbital ratios.

**Mean-motion resonance — the harmony engine.** When two bodies' mean motions are commensurable, $p\, n_1 = q\, n_2$ (period ratio $P_1:P_2 = p:q$, e.g., the 2:1 Io–Europa, 3:2 Neptune–Pluto, or the 4:2:1 Laplace chain Io–Europa–Ganymede), their conjunctions (longitude alignments) recur periodically — a physical *cadence schedule*. The Laplace resonance is two coupled 2:1 resonances with anti-aligned apsides ($\varpi_1 - \varpi_2 \approx \pi$) and libration about 180°, which in music becomes a recurring *anti-phase* two-against-one groove that periodically snaps to alignment (conjunction) — a deterministic tension/release oscillator. Chained resonances (4:2:1) give polyrhythmic hierarchies exactly like 4:2:1 over a common stroke: three voices in 4:2:1 (Io:Europa:Ganymede) produce the polyrhythm of 4 against 2 against 1 events per cycle.

**Compositional mapping summary.** Per voice $v$ (planet) and per section $s$ (one orbital "year" or synodic cycle): events $k = 1..N_v$; $\nu_k = 2\pi k / N_v$; onset $t_k$ from the 2nd-law time law (above); pitch from $r(\nu_k)$ or from $\log_2 P_v$ register; velocity from areal speed $h/r^2$ (louder through perihelion); durations from dwell time until the next event (or legato fraction of it); section boundaries at conjunction epochs of the controlling resonance or at the outer body's period; macro-form from a resonance chain (capture sequence 3:2 → 2:1 → 4:2:1) or from a synthetic exoplanet system parameterized by $(a, e)$ per section.

KORC is the celestial-mechanics foil to 020 SMSTC (kinematic *clouds* with gravity as an attractor — KORC uses *bound orbits* with exact time laws) and 043 SATM (chaotic self-same attractors — Keplerian orbits are regular, closed, deterministic); a continuous-time, physically-sourced sibling of 012 Euclidean / 069 Christoffel (which abstractly distribute $k$ onsets — KORC gets its distribution from $r^{-2}$ dynamics); and the deterministic Nature-Led counterpart to 045 Hawkes (stochastic self-excitation vs deterministic areal-speed clustering) and 038 KOPS (phase oscillators coupling vs true resonance commensurability).

### Musical Elements Framework

**PITCH** — Three layers. (i) *Register from orbit scale*: bodies ordered by semi-major axis $a$ get registers by $\log_2 P = \tfrac32\log_2 a$ (3rd law), so orbital architecture = pitch architecture (outer = low, inner = high; NASA practice). (ii) *Contour from ellipse*: within one orbit, pitch follows $r(\nu_k)$ — falling toward perihelion, rising toward aphelion; eccentricity deepens the contour amplitude. (iii) *Intervals from velocity ratios*: each voice's perihelion:aphelion speed ratio $((1+e)/(1-e))^2$ sets its characteristic span (Kepler's table), quantized to the nearest just interval (5:4, 6:5, 3:2, 16:15, 24:25, ...) or 12-TET semitone. Optional strict mode: pitch CLASS from $\tfrac32\log_2(P_v) \bmod 12$ over a chosen root = the star.

**RHYTHM** — Onset times are the physical answer to "when does the planet pass angle $\nu_k$?": $t_k = \frac{P}{2\pi}(E_k - e\sin E_k)$ with $E_k$ from $\nu_k$. The resulting inter-onset interval is $\Delta t(\nu) \propto r(\nu)^2 \propto (1+e\cos\nu)^{-2}$: shortest at perihelion ($\nu=0$), longest at aphelion ($\nu=\pi$), ratio $((1+e)/(1-e))^2$ exactly. So eccentricity is a *rhythmic* dial: $e=0$ → isochronous; $e=0.3$ → 3.4:1 rush/linger; $e=0.6$ → 16:1 (dramatic cadenza swells). Number of events per orbit $N_v$ controls density per voice; the ratio $N_v$ across resonant voices implements the p:q polyrhythm directly (4:2:1 Laplace = 4/2/1 events per common cycle). Continuous-time output; optional quantization to a tick grid preserves zero-drift.

**HARMONY** — Resonances ARE chords. A p:q mean-motion commensurability makes the two bodies re-align every $q$ orbits of the inner body: the recurrence of conjunction is the harmonic rhythm, and the stack of bodies' simultaneous pitch classes at conjunction is the sonority. Two-body 2:1 → octave-framed periodic re-affirmation; 3:2 → fifth-cycle cadence; Laplace 4:2:1 → the three-body chord set with anti-aligned apsides producing the alternation of a "conjunctive" sonority (all three aligned) and a "disjunctive" one (libration peak), a physical chord-tension pendulum. Superposed velocity-ratio intervals (5:4, 6:5, 3:2) are just intervals built from the harmonic series — self-consistent consonance without a scale table.

**STRUCTURE** — Sections map to orbital epochs: a section = one outer-body orbit ("year"), or one synodic cycle $T_\mathrm{syn} = P_1 P_2 / |P_1 - P_2|$ of a controlling pair (the recurrence period of the harmonic situation), or one conjunction-to-conjunction arc. Macro-form = a *resonance chain*: compose sections whose bodies are captured into successively lower resonances (3:2 → 2:1 → 4:2:1, the differential-migration capture sequence the real Galilean system followed; Peale & Lee 2002), giving a deterministic tension arc: sparse wide conjunctions → locked dense polyrhythm → three-way alignment climax → release (dephased, higher section). Alternatively a synthetic exoplanet system: each section varies $(a_v, e_v)$ of the voice ensemble, so the same resonator morphs across sections (form as orbital evolution).

**TEXTURE** — Voice count = body count; each voice is a separate resonator with its own $\theta_v = (a_v, e_v, N_v)$: bass voices on slow outer orbits (low $N$, deep sub-rhythms), leads on fast inner orbits (high $N$, perihelion rushes), mid voices in 2:1/3:2 couplings. Density surges through perihelion = internal textural crescendo per cycle; the apsidal anti-alignment of Laplace-type chains makes voices' dense phases interleave (one voice rushes while another lingers) → hocket-like textural counterpoint. Areal-speed velocity mapping gives per-event dynamic swells; the star (focus) is the textural center of gravity.

### UnitMatrix Integration (Voices & Sections)

**Voices** = rows, each a Keplerian body with parameter cluster $\theta_v = (a_v, e_v, P_v, N_v, \mathrm{root}_v, \mathrm{mode})$:
- Voice 1 (Lead): inner, fast orbit — small $a$, $e \approx 0.2$–0.5, high $N_v$ (16–32 events/orbit), register mid-high; pitch from $r(\nu)$ contour.
- Voice 2 (Harmony): 2:1 resonant with Lead (e.g., $P_2 = 2P_1$), $e$ low, $N_2 = N_1/2$ — its conjunction with Lead every Lead-orbit creates the harmonic anchor.
- Voice 3 (Bass): outer, slow — $P_3 = 4P_1$ (completing a Laplace 4:2:1 chain), $N_3 = N_1/4$, low register from $\log_2 P$; sparse downbeats.
- Additional voices take further commensurabilities (3:2, 5:4) or independent eccentricities for texture; apsidal orientation $\varpi_v$ controls phase (anti-aligned = hocket, aligned = tutti rushes).

**Sections** = columns, each with a target orbit architecture $\theta_s = ((a_v, e_v)_{v=1..V}, \text{resonance chain}_s, T_s, \text{quantize})$: section length $T_s$ = one outer "year" or one synodic/recurrence period of the section's controlling resonance; resonance chains ascend (3:2 → 2:1 → 4:2:1) across the form for a capture-sequence arc, or descend for release. A 5-section form: Intro (circular orbits, $e \approx 0$, sparse $N$), Verse (2:1 locked, $e=0.1$), Pre-Chorus (capture toward Laplace, $e$ rising), Chorus (full 4:2:1 Laplace, $e$ peak — perihelion rushes + triple conjunction), Outro (release: dephase apsides, circularize $e \to 0$).

**Cell filling** (zero-drift invariant preserved) for cell $(v, s)$:
1. Read $\theta_v$, $\theta_s$; set section start tick $T_{\text{start}}$, section length $L_s$ ticks; scale the outer period to $L_s$: $P_v^{(\text{ticks})} = L_s \cdot P_v / P_{\text{outer}}$.
2. Generate events $k = 1..N_v$: $\nu_k = 2\pi k/N_v$; solve $E_k$ from $\tan\frac{E_k}{2} = \sqrt{\frac{1-e}{1+e}}\tan\frac{\nu_k}{2}$; $M_k = E_k - e\sin E_k$; tick offset $t_k = T_{\text{start}} + \mathrm{round}(\frac{P_v^{(\text{ticks})}}{2\pi} M_k + \phi_v)$ ($\phi_v$ = apsidal phase).
3. Pitch: register from $\log_2 P_v$; contour $p_k = \mathrm{root}_v + \mathrm{round}(\mathrm{span}_v \cdot \frac{r(\nu_k) - r_{\min}}{r_{\max} - r_{\min}})$ (span_v from the velocity-ratio interval) — or strict mode: pitch class from $\frac32 \log_2 P_v \bmod 12$.
4. Velocity: $v_k \propto h/r(\nu_k)^2$ normalized to 40–127; duration = min(dwell to next onset, legato cap).
5. Pack into `create_note_unit` sequences; pad the cell to exactly `section_len` ticks (terminal landmark at `sum(events+durations) == section_len`) so `composer.validate()` passes.
6. Export via `UnitMatrixComposer.to_midi(path)` (quantize to 480 tpb grid or continuous ticks).

### Pitfalls

1. **Kepler solves for time-from-angle, not angle-from-time.** The closed form maps $\nu \to t$ (via $E \to M$); if you instead need the body's position at a fixed clock time you must invert Kepler's equation $M = E - e\sin E$ by Newton iteration (converges in ~5 iterations for $e<0.9$ from $E_0 = M$). Prefer event-driven generation (angle-sampled, time-solved) — it is exact, cheap, and avoids iteration entirely.
2. **Zero-drift vs continuous-time onsets.** The 2nd-law times are generally not on the 480-tpb grid. Quantize with `round()` AND pad the last event to the section terminal landmark (per AGENTS.md); or generate in continuous ticks and let `create_note_unit` carry micro-timing — but never let the last onset+duration fall short of `section_len` (validate() fails on track-length mismatch).
3. **Eccentricity blow-up.** $e \ge 1$ is unbound (parabolic/hyperbolic escape); the $(1-e)^{-2}$ factors diverge. Clamp $e \le 0.7$ for musical rubato; near $e \to 1$ the perihelion rush becomes a single degenerate cluster — musically a scrape/roll, useful only deliberately.
4. **Density explosion at perihelion.** $\Delta t \propto (1+e\cos\nu)^{-2}$ concentrates events: at $e=0.5$, perihelion inter-onset spacing is 9× tighter than aphelion. With $N_v = 32$ events/orbit the perihelion cluster can exceed human/articulation rates or exceed tick resolution (inter-onset < 1 tick at 480 tpb). **Fix**: cap effective $N_v$ per cell so $\min \Delta t \ge 2$ ticks, or resample with a minimum-dwell floor, or lower $e$.
5. **Period-scaling quantization.** Mapping $P_v$ to ticks by $L_s \cdot P_v / P_{\mathrm{outer}}$ is exact only when the period ratio is rational (real orbits are slightly incommensurable — Io/Europa/Ganymede librate, they are not exact integers). **Fix**: snap the working periods to exact rationals (2:1, 3:2, 4:2:1, ...) for generation; report the real system's libration amplitude as a *micro-timing Jitter knob* (deterministic phase wobble), which is physically honest and musically alive.
6. **Register collision in strict 3rd-law mode.** $\log_2 P$ grows slowly ($\Delta \log_2 P = 1.5\,\Delta\log_2 a$); a 10× distance span = only ~5 octaves of register. Wide systems cram many voices into few octaves. **Fix**: distribute voices across octaves by integer transposition after the $\log_2 P$ ranking.
7. **Conjunction ≠ always consonance.** A real conjunction is an alignment of longitudes — the *chord quality* depends on the pitch mapping (often a $\sqrt{}$-octave stack = a cluster). Deliberately choose the pitch mapping (velocity-ratio intervals vs $\log P$ classes) so that conjunction epochs land on the sonorities you want; the physics gives the *timing* of harmonic rhythm, not its quality.
8. **Relation to existing methods.** Document the siblings in prose to avoid duplication accusations: KORC is the *bound-orbit, exact-time-law* cousin of 020 SMSTC (which uses gravity/kinematics for *unbound event clouds*) and 043 SATM (chaotic self-same attractors); the continuous-time ratio source of 012 Euclidean / 069 Christoffel rhythms (which distribute $k$ onsets abstractly); the deterministic foil of 045 Hawkes (stochastic self-exciting events) and 038 KOPS (coupled phase oscillators, no two-body gravity); and the *rhythm/pitch* partner of 039 SMA (audio-domain spectra; KORC's intervals come from orbital velocity ratios). Kepler's own 1619 *Harmonice Mundi* is the historical anchor, not a duplicate of any DB entry.

---

Candidate code path: `generators/kepler_orbit_composer.py` — implements `PlanetVoice(semi_major_axis_a, eccentricity_e, n_events, period_ratio, root_midi, span_interval)` (body state: $\nu_k$, per-event $t_k$ via the analytic $\nu \to E \to M$ chain, $r(\nu)$ pitch contour, areal-speed velocity), `ResonanceChain(pairs)` (checks $p\,n_1 = q\,n_2$ commensurability, returns conjunction epochs + libration phase), `SynodicForm(section_architectures)` (per-section $\theta_s$: period scaling to section ticks, resonance-capture arc), `kepler_time(nu, e, P)` (the closed-form onset law), `kepler_interval(e)` (the $((1+e)/(1-e))^2$ → nearest just ratio / semitone), `period_from_axis(a, GM)` (3rd law) and `pitch_from_period(P, root)` ($\frac32 \log_2 P$ class or register). Feeds UnitMatrix cells as `MusicUnit` sequences like `generators/farey_composer.py` does for FSBC.

---

## Workflow / verification log

- ID resolution: grep of summary table rows (`| **NNN** |`) → max numeric ID = **114** (rows 100, 110–114 present; rows 101–109 and 058 absent historically — sparse IDs confirmed); standalone file scan (`method_*.md`) → `method_114_FSBC.md` exists; → **next free = 115**. No existing method duplicates KORC (no Kepler/orbit/planet/resonance entry in 001–114; checked 020/038/043/045/012/069 closely).
- Layer read: `LAYER_ARCHITECTURE.md` — abstract = pitch-pool/subset + tension (feeds rules/subset_network.py; e.g., DB row 113 PCFSC); concrete = events filling UnitMatrix cells (this method); absolute = sound production (SP-*, separate job). KORC classified **concrete**.
- Temp-file workflow: wrote `_temp_method_115.md` via write_file → `cat >> methods_db.md` → `rm` (no heredoc/execute_code).
- Summary-table insertion: single row appended after line 124 (row 114) via patch. **Pitfall checks:** (a) backslash escaping — used `$O(N)$` plain style (matching row 114) inside the table; verified 0 occurrences of double-escaped `\\mathcal{O}` in the inserted row; (b) `||` prefix — verified inserted row starts with exactly `| **115**` (grep `'^| \*\*115\*\*'` = 1). Re-read line 125 to confirm.
- Section append verified: grep shows `### Source` (line 25192), `### Layer` (25102...), `### Paradigm`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Pitfalls` for the KORC section; `wc -l` before = 25188, after = 25274.
- Quirks hit: table rows 101–109 and 058 are absent from the summary table though standalone files exist — historical sparse-ID anomaly; did NOT renumber or backfill (out of scope; task is append-only). Row 113 PCFSC is the only `abstract`-layer entry — used as the layer-format reference.

## Next free ID

**116** (after 115 KORC).