# Sound Production Method SP-139 — Conical Double-Reed Bore Synthesis (CDRB)

### Source

- **Guillemain, P. (2004). "A Digital Synthesis Model of Double-Reed Wind Instruments."** *EURASIP Journal on Applied Signal Processing* 2004(4), 473–481. DOI 10.1155/s1110865704402194 — the direct predecessor: a digital model of oboe/bassoon double reeds (two reeds sharing the flow, nonlinear channel, conical resonator); the reference CDRB's valve+bore topology is drawn against. (Verified via Crossref.)
- **Polychronopoulos, S., Marini, N., Bakogiannis, A., & Kouroupetroglou, G. (2021). "Physical Modeling of the Ancient Greek Wind Musical Instrument Aulos: A Double-Reed Exciter Linked to an Acoustic Resonator."** *IEEE Access* 9, 98150–98162. DOI 10.1109/ACCESS.2021.3095720 — a double-reed exciter coupled to a resonator, with measured reed parameters; the two-blade excitation structure follows its block diagram. (Verified via Crossref.)
- **Kergomard, J., Guillemain, P., Sanchez, C., & Vergez, C. (2019). "Role of the Resonator Geometry on the Pressure Spectrum of Reed Conical Instruments."** *Acta Acustica united with Acustica* 105(6), 1161–1172. DOI 10.3813/AAA.919320 — why the conical bore gives the complete harmonic series and how the reed's nonlinearity shapes the radiated pressure spectrum of sax/oboe-class instruments. (Verified via Crossref.)
- **Ducasse, E. (2003). "A Physical Model of a Single-Reed Wind Instrument, Including Actions of the Player."** *Computer Music Journal* 27(1), 59–75. DOI 10.1162/01489260360613344 — the lumped reed model (mass-spring-damper + Bernoulli channel + bore impedance) that CDRB extends to two blades. (Verified via Crossref.)
- **Avanzini, F., & Rocchesso, D. (2002). "Efficiency, accuracy, and stability issues in discrete-time simulations of single reed wind instruments."** *J. Acoust. Soc. Am.* 111(5), 2299–2311. DOI 10.1121/1.1467674 — discrete-time reed stability analysis; the symplectic-integrator requirement documented in CDRB's Pitfalls follows this line of work. (Verified via Crossref.)
- **Dalmont, J.-P., Gazengel, B., Gilbert, J., & Kergomard, J. (1995). "Some aspects of tuning and clean intonation in reed instruments."** *Applied Acoustics* 46(1), 19–62. DOI 10.1016/0003-682X(95)93950-M — oscillation just *below* the impedance maxima (the measured −5.9-cent playing offset in CDRB), threshold behavior. (Verified via Crossref.)
- **Fuks, L., & Sundberg, J. (2023). "Blowing pressures in reed woodwinds."** Proc. ISMA 2023. DOI 10.25144/15150 — measured blowing pressures: oboe the highest (~4–8 kPa), matching CDRB's operating band. (Verified via Crossref.)
- **Aragó Bishop, R., Campbell, D. M., & Woolley, A. (2024). "Double reed sound production on the bass crumhorn."** Proc. ISMA 2023. DOI 10.25144/23678 — double-reed + conical-bore physics from the Edinburgh acoustics group; the near-collapse high-pressure regime. (Verified via Crossref.)
- **Paquier, M., Hendrickx, J., & Jeannin, A. (2016). "Effect of wood on the sound of oboe as simulated by the chanter of a 16-inch French bagpipe."** *Applied Acoustics* 104, 91–96. DOI 10.1016/j.apacoust.2015.10.008 — the bagpipe-chanter-with-oboe-reed bridge between the two CDRB voicings. (Verified via Crossref.)
- **Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer. Ch. 13 "Sound Generation by Reed and Lip Vibrations" (DOI 10.1007/978-0-387-21603-4_13) and Ch. 15 "Woodwind Reed Instruments" (DOI 10.1007/978-0-387-21603-4_15)** — the canonical treatment of reed self-oscillation (negative resistance, impedance peaks) and of the oboe/bassoon double-reed conical-bore family. (Verified via Crossref.)
- **Scavone, G. P., & Smith, J. O. (1996). "Digital waveguide modeling of woodwind toneholes."** *J. Acoust. Soc. Am.* 100(4), 2627. DOI 10.1121/1.416582 — tonehole scattering for the fingered-bore extension (register holes, chanter finger holes). (Verified via Crossref.)
- **Wikipedia**: "Oboe" (Hornbostel–Sachs 422.112-71 double-reeded aerophone with conical bore), "Bassoon" (double reed + conical bore), "Reed (mouthpiece)" (double reeds: two blades facing, no rigid lay), "Great Highland Bagpipe" (chanter = double reed + conical bore, two tenor + one bass drone reeds). Cached in `_web139/wiki_{oboe,bassoon,reed,bagpipe}.html`.
- **Novelty check (2026-11-11):** `grep -ci` on `methods_db.md` **before** entry: `double reed` = 0, `bagpipe` = 0, `bassoon` = 0, `didgeridoo` = 0, `chanter` = 0, `double-reed` = 0, `staple` = 0 (`oboe` = 2 — passing prose: SP-134's sax-formant comparison and SP-135's conditioning-row mention, never a method; `reed` = 167 — all SP-023/SP-065/SP-066/SP-124/SP-131 prose; `conical` = 7 — all inside SP-134 CSRB's own entry, the single-reed saxophone sibling). Repo antecedent: `sound/synthesis/conical_reed.py` (surveillance-namespace SP-134, single-reed sax) covers the conical *bore*; **no method models a beating double-reed valve** (two coupled blades, aperture = inter-blade gap, no lay). Adjacent-but-different: **SP-023** clarinet (single reed, stopped cylinder, odd-only harmonics, $c/4L$); **SP-134** CSRB (single reed, conical bore — saxophone; CDRB's bore treatment matches, the *valve* is new); **SP-065** brass lip reed (buzzing lips, cylindrical flaring bore); **SP-066** flute air jet (no vibrating blade); **SP-124** FRAP free reed (one cantilever, slot, pitch by the reed — the drone-reed class; bagpipe drones use it); **SP-131** two-mass vocal folds (two coupled masses, but self-oscillating glottis, no bore-impedance feedback loop, different device). CDRB is the DB's first *beating double-reed + conical-bore* wind-instrument model — the oboe/bassoon/crumhorn/chanter voice class.
- **Verified prototype for this document:** `_web139/verify_sp139.py`, log `_web139/verify_sp139_output.txt`, audio `_web139/sp139_demo_oboe.wav` (70 560 stereo frames @44.1 kHz, 141 164 B, 1.6 s) and `_web139/sp139_demo_chanter.wav` (52 920 frames, 105 884 B, 1.2 s) — **12/12 checks pass** (all numbers quoted below are measured).
### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). CDRB consumes symbolic note events (pitch, velocity, onset/duration ticks from a UnitMatrix cell) and renders per-voice audio buffers — it holds no timing authority, emits no events, and decides nothing about composition: it is a synthesis engine in the render chain. Candidate code path: `sound/synthesis/double_reed.py` (modules: `DoubleReedValve` (two coupled cantilever blades + travel clamps), `InertantChannel` ($L_a$ flow with quadratic resistance), `ConicalBoreModes` (modal bank at $f_n = nc/2L_{eff}$), `CDRBSynth` (per-note voice allocator + blowing-pressure envelope + breath noise)), dispatched from `workflows/musicom_workflow.py::produce(method="SP-139", ...)`. It is the double-reed sibling of `sound/synthesis/conical_reed.py` (SP-134 CSRB) and the beating-valve complement to `sound/synthesis/free_reed.py` (SP-124 FRAP).

### Description

An oboe note: the player blows through two thin cane blades clamped at the staple, tips facing each other inside the mouth; mouth pressure $p_m$ pushes **both** blades inward, narrowing the gap between them — a valve with **no rigid lay**, whose aperture is the distance between two moving walls. The blades are soft cantilevers ($k \approx 450$ N/m, tip opening $\approx 1$ mm total); the reed's natural frequency $f_r \approx 2$–3 kHz sits well above the playing register, and the flow through the channel carries the air's inertia (channel inertance $L_a$), which makes the flow *lag* the reed motion and pump energy into the oscillation — the aerodynamic negative damping that sustains the tone at the high blowing pressures (4–8 kPa, the highest of any woodwind, Fuks & Sundberg) this instrument family needs. The blades' oscillation modulates the channel flow into a *conical bore* whose resonances are a **complete harmonic series** $f_n = nc/2L_{eff}$ (the cone's signature — all harmonics, unlike the clarinet's odd-only stopped cylinder). The reed–flow–bore loop self-oscillates above a threshold pressure (~3 kPa, measured) and locks to the bore's fundamental, playing a few cents *below* the impedance peak (Dalmont et al. 1995); raising the pressure toward collapse makes the tone louder and radically brighter until the reed slams its travel limits (the near-collapse "squawk"/overblow). The same valve drives the oboe, bassoon, crumhorn, and the highland bagpipe chanter (whose twin drone reeds are the *free*-reed class of SP-124).

CDRB is that signal chain, discretized per note as a two-blade valve + inertant channel + modal conical bore — sample-count preserving and deterministic per seed.
### Technical Mechanics

**1. Two-blade valve (the double reed).** Per blade $i \in \{1,2\}$: a damped cantilever with effective mass $m_i$, stiffness $k_i$, damping $r_i$, tip displacement $x_i$ (positive = closing); the mouth pressure $p_m$ acts on the outer face, the bore pressure $p$ on the inner face, so the net closing force is $S_i(p_m - p)$; the blades couple through the common staple ($k_c$):

$$m_i \ddot{x}_i + r_i \dot{x}_i + k_i x_i = S_i (p_m - p) - k_c (x_i - x_j), \qquad i, j \in \{1,2\}, \; i \ne j$$

There is **no rigid lay**: the channel aperture is the gap between the two moving blades,

$$A(x_1, x_2) = W\,(2H - x_1 - x_2), \qquad \mathrm{clamped\ to\ } [0,\, 2WH]$$

with $H$ = rest half-gap per blade and $W$ = channel width at the tip. Static behavior (no bore): each blade sits at $x_i = S p_m/k_i$, so the opening follows the two-springs-in-series law

$$A = W\Big(2H - S p_m\big(\tfrac{1}{k_1} + \tfrac{1}{k_2}\big)\Big)$$

(measured 0.733 mm symmetric / 0.644 mm asymmetric vs analytic 0.733 / 0.644 mm — checks 1–2), and the reed collapses ($A = 0$) at

$$p_m^{\mathrm{coll}} = \frac{k H}{S} \qquad (\text{symmetric blades})$$

(measured 8000 Pa vs analytic 7484 Pa, 6.9 % — check 3). Parameters used: $m = 2.35\times10^{-6}$ kg, $k = 450$ N/m ($f_r = 2200$ Hz, measured 2300 Hz — check 4), $r = 2\zeta\sqrt{km}$ with $\zeta_r = 0.22$, $H = 5\times10^{-4}$ m, $S = 3\times10^{-5}$ m², $W = 5\times10^{-3}$ m, $C_d = 0.6$.

**2. Channel flow with inertance.** The quasi-static Bernoulli map $u = C_d A\sqrt{2|p_m-p|/\rho}\,\mathrm{sgn}(p_m-p)$ is NOT sufficient: at operating pressures the static aperture effect gives a *positive* flow conductance ($du/dp > 0$, verified analytically — the aperture opens as the bore pressure relieves the closing force), so the oscillation cannot start from the N-shaped resistance alone. The sustaining mechanism is the aerodynamic negative damping of the air mass in the channel (the mechanism behind SP-124 FRAP and Guillemain 2004):

$$L_a \frac{du}{dt} = (p_m - p) - R_q(u)\,u, \qquad R_q = \frac{\rho}{2 C_d^2 A^2}\,|u|, \qquad L_a = \frac{\rho\,l_{\mathrm{ch}}}{A}$$

The quadratic resistance $R_q u$ is the Bernoulli pressure drop written as a nonlinear resistor; the inertance $L_a$ makes the flow **lag** the reed motion, so the channel pressure drop drives the blades with a phase that pumps energy into the oscillation below $f_r$. Steady state ($du/dt = 0$) recovers the Bernoulli law exactly. Seeded breath noise can be injected into $u$ (scaled by $\sqrt{A}$).

**3. Conical bore = complete harmonic series.** An ideal cone, reed at the apex end and open at the bell, has input-impedance poles solving $\tan(kL_t) = -kx_0$ (the same geometry SP-134 derives for the saxophone), whose solutions are the **complete** series

$$f_n = \frac{n c}{2 L_{\mathrm{eff}}}, \qquad n = 1, 2, 3, \dots$$

— all harmonics, in contrast to the stopped cylinder's odd-only $c/4L$ (the clarinet). CDRB realizes the bore as a modal bank with those exact pole locations,

$$\ddot{p}_n + 2\zeta_n \omega_n \dot{p}_n + \omega_n^2 p_n = \mu_n \frac{du}{dt}, \qquad \mu_n = \frac{2\zeta_n \omega_n Z_{\mathrm{peak}}}{n}, \qquad p(t) = \sum_{n=1}^{N} p_n$$

so the resonant pressure gain of mode $n$ is $p/u \approx Z_{\mathrm{peak}}/n$: $Z_{\mathrm{peak}} = 4\times10^7$ Pa·s/m³ sets the fundamental peak at the $\rho c/S_{\mathrm{bell}}$-scale of a real woodwind input impedance, and the $1/n$ participation makes high resonances weaker. Per-mode damping grows with frequency (viscothermal + radiation losses): $\zeta_n = 0.008 + 0.004\,n$ ($N = 14$ modes, $f_{14} = 4140$ Hz). **Important scale lesson (verified):** the plane-wave scale $\rho c/S_{\mathrm{reed}} \sim 10^5$–$10^6$ gives an open-loop gain of $10^{-4}$ and NO oscillation; the resonance-scale peak $\sim 4\times10^7$ is what a real bore presents at its impedance maxima.
**4. Self-oscillation.** The loop: blade displacement → aperture → inertant flow → bore modes → mouthpiece pressure → blade force. Above a threshold blowing pressure the negative aerodynamic damping beats the losses and the loop locks to the fundamental: measured onset floor $2.8\times10^{-4}$ RMS @2.5 kPa → $7.4\times10^{-3}$ @3.0 kPa → $1.3\times10^{-1}$ @3.5 kPa → $5.3\times10^{2}$ @5.0 kPa (**threshold $\approx$ 3.0 kPa — check 5**, matching the real oboe's onset). The playing frequency sits just **below** the impedance maximum (Dalmont 1995): measured peak **294.7 Hz vs theoretical $f_0 = c/2L_{eff} = 295.7$ Hz (−5.9 cents — check 6)**. The conical bore's complete series is the spectral signature: sustained tone at 6.5 kPa gives h1…h6 = 0 / −15.0 / −32.6 / −26.7 / −43.1 / −37.6 dB — **all harmonics present, h2 at −15 dB** — while a matched stopped-cylinder bank (odd-only modes, clarinet-style) gives h2 = −44.4 dB: a **29.4 dB h2 contrast** (check 7, the conical-vs-cylinder discriminator).

**5. Pressure = amplitude AND brightness.** Velocity/blowing maps straight into the reed's nonlinear regime: measured spectral centroid **860 Hz @4 kPa → 1916 Hz @6.5 kPa (2.23×, check 8)**, RMS growing 26× over the same band; near collapse ($p_m \to p_m^{\mathrm{coll}} \approx 7.5$ kPa) the blades slam the travel limits and the tone squawks/overblows. The valve itself is a harmonic generator even without the bore: a 300 Hz sinusoidal pressure drive at $p_m = 4$ kPa produces flow harmonics h2 = −14.4 dB, h3 = −39.7 dB (check 9 — the Bernoulli + aperture nonlinearities).

**6. Numerical.** The reed is integrated with **velocity-first semi-implicit (symplectic) Euler** — REQUIRED: the naive position-first update is unstable whenever $\omega^2 dt^2 > (r/m)\,dt$ (verified: the stiff blade diverges to $10^{12}$ m under position-first, settles to the analytic equilibrium under symplectic). Modes use explicit Euler ($\omega_{14} dt = 0.30$, stable). Blade travel is clamped with dead stops: $x \in [-1.2H,\, H]$ (the open-travel limit and the closing slap); restitution is omitted for numerical safety. The flow ceiling is clamped at $2\,C_d(2WH)\sqrt{2p_m/\rho}$. Deterministic per seed (breath noise seeded; same seed → bit-identical buffer, different seed → different — check 10); sample-count preserving (note length = duration × $f_s$, verified — check 12); $O(N)$ per sample per note, $N = 14$ modes, vectorizable across rows.

**7. Chanter / bassoon voicings.** One valve + one modal bank covers the whole family by $L_{eff}$: oboe $f_0$ 295.7 Hz ($L_{eff} = 0.58$ m), highland chanter low-A $f_0$ 466 Hz ($L_{eff} = 0.368$ m — measured peak 463.6 Hz, −8.8 cents, check 11), bassoon $f_0 \approx 66$ Hz ($L_{eff} \approx 2.6$ m). Chanter + drone texture = CDRB row (chanter) layered with SP-124 free-reed rows (drones).
### Musical Elements Framework

- **PITCH**: $f_0 = c/2L_{\mathrm{eff}}$ — the bore length IS the pitch (register = finger holes; the modal bank's pole locations shift with $L_{eff}$). The playing peak sits a few cents below the impedance maximum (measured −5.9 cents — the Dalmont effect), so per-note tuning is stable but not grid-exact; the reed resonance $f_r$ (~2.2 kHz) caps the usable register (notes above $\sim f_r/2$ lose amplitude as the reed's response rolls off). Velocity → pressure → the same pitch with a brighter spectrum (a physical re-voicing, not an LFO).
- **RHYTHM**: the attack is the oscillation build-up (measured ~20–40 ms to full amplitude — the instrument's characteristic "chiff"-less soft attack); the release is the reed ring-down ($\tau = 1/\zeta_r \omega_r \approx 0.3$ ms — staccato by pressure release, no tail); the near-collapse slap adds a percussive bite at high dynamics; breath noise (seeded) rides under the tone as a texture floor; tempo-syncable pressure envelopes put rhythm on the blowing column.
- **HARMONY**: monophonic by nature (one valve, one pressure), but polyphonic in the matrix: independent CDRB rows layer double-reed voices (oboe + bassoon doublings, chanter + drone stacks via SP-124 free-reed rows), and the near-harmonic complete series makes CDRB chords blend cleanly with conical-family instruments (SP-134 sax rows share the bore series).
- **STRUCTURE**: sections = blowing states: soft/plain/hard/squawk columns (pressure 3.8/5.0/6.0/6.4 kPa) + register columns ($L_{eff}$ changes); a crescendo is a pressure ramp column; an "oboe section" is a texture-state change in the arrangement (like SP-138's EP-section idiom).
- **TEXTURE**: (a) the conical complete-series brightness (h2 −15 dB — the oboe's "piercing" identity vs the clarinet's hollow odd stack, 29.4 dB h2 contrast measured), (b) the pressure→brightness axis (centroid 2.23× over 4→6.5 kPa), (c) the near-collapse squawk/overblow (blades slamming the travel limits), (d) the soft-attack reed "voicing", (e) breath-noise floor, (f) chanter's compact bright tone (f0 466 Hz, h2 −24 / h3 −23 dB).

### UnitMatrix Integration

**Voices = rows = reed+bore instruments.** Row $v$ carries `{reed: {m, k, zeta, H, S, W, k1/k2 (asymmetry), kc}, flow: {Cd, L_ch}, bore: {L_eff (pitch), zpeak, zeta_n, nmode}, blowing: {pm, attack_ms, release_ms, breath}}`. Example rows: "oboe lead" (L_eff 0.58, pm 5000, breath 1e-6), "oboe soft" (pm 3800), "oboe squawk" (pm 6400, near-collapse), "chanter A" (L_eff 0.368, pm 5200), "bassoon" (L_eff 2.6, pm 5500). Row asymmetry ($k_1 \ne k_2$) is the "scraped reed" timbre dial.

**Sections = columns = blowing/register states.** Column $j$ holds `{pm, attack, release, breath, L_eff_mult, squawk}` — a column change is a pressure/register change. CDRB is sample-count preserving, so section seams stay zero-drift safe; a release at a seam is the reed's fast ring-down (never re-time a tail — the SP-136/SP-138 seam rule applies).

**Cells = MusicUnit.** Each `MusicEvent` (pitch, velocity, start_tick, end_tick): pitch → $L_{eff} = c/(2f)$; velocity → blowing pressure (power-law map $p_m = p_{m0}(v/100)^\gamma$, $\gamma \approx 1.2$; velocity is the *loudness and brightness* control); start_tick → valve pressure onset (attack ramp); end_tick → pressure release (the reed damps in ~0.3 ms; a short tail rings into the buffer margin).

**Produce dispatch:** `produce(midi_path, method="SP-139", params={"rows": {"oboe_lead": {"reed": {"m": 2.35e-6, "k": 450.0, "zeta": 0.22, "H": 5e-4, "S": 3e-5, "W": 5e-3, "asym": 1.0}, "bore": {"L_eff": 0.58, "zpeak": 4e7, "nmode": 14}, "blowing": {"pm": 5000.0, "attack_ms": 25, "breath": 1e-6}}, "chanter": {"bore": {"L_eff": 0.368}, "blowing": {"pm": 5200.0}}}, "columns": {"A": {"pm": 4500.0}, "B": {"pm": 6000.0, "squawk": 1}}, "fs": 44100})`. Stage order: CDRB renders per-row double-reed voices (replacing/augmenting SP-001/SP-011/SP-134 sources for oboe-family parts) → per-row EQ (SP-007) → spatialize (SP-021/SP-053) → room (SP-009/SP-032/SP-075) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Use CDRB for oboe/bassoon/crumhorn/chanter parts; use SP-134 for saxophone (single reed); use SP-023 for clarinet (stopped cylinder); use SP-124 for free-reed drones and accordion/harmonica; use SP-065/SP-066 for brass/flute. NOTE (2026-11-11): the `produce()` dispatch map in `workflows/musicom_workflow.py` carries a parallel surveillance namespace whose SP numbering diverges from methods_db (see `hermes_agent/surveillance.md`); the methods_db numbering is authoritative for this entry.

### Pitfalls

1. **Symplectic Euler or the blades fly.** The position-first update is unstable for stiff blades ($\omega^2 dt^2 > (r/m)\,dt$, verified: blade diverges to $10^{12}$ m); velocity-first semi-implicit Euler settles to the exact static equilibrium. Never "fix" it by adding artificial damping — that silently changes the reed Q and the threshold.
2. **The quasi-static Bernoulli does not oscillate.** At operating pressures the static flow conductance is *positive* (aperture opens as bore pressure relieves the closing force — verified analytically and numerically); without the channel inertance $L_a$ the loop gain never reaches 1 at any pressure. The inertance IS the sustaining mechanism (SP-124's lesson, shared).
3. **Impedance scale.** The plane-wave scale $\rho c/S_{\mathrm{reed}} \approx 10^5$–$10^6$ gives open-loop gain ~$10^{-4}$ (measured) and silence; the resonance-scale peak $\approx 4\times10^7$ (a real bore's impedance maximum) is required. If the note is silent, check $Z_{\mathrm{peak}}$ first, not the reed.
4. **Reed parameters ARE the instrument.** $p_m^{\mathrm{coll}} = kH/S$ fixes the ceiling; playing pressure lives at 40–85 % of it; too stiff a reed → no oscillation below collapse; too soft → collapses at a whisper. $k \approx 400$–$800$ N/m, $H \approx 0.4$–$0.6$ mm, $S \approx 2$–$4\times10^{-5}$ m² reproduce the oboe's 3–8 kPa band.
5. **Asymmetric blades change the aperture law** (the two-spring series, check 2). Real reeds are scraped asymmetric; symmetric blades are the simplified special case, and $k_c$ coupling shifts the two normal modes (in-phase at $\sqrt{k/m}$, out-of-phase at $\sqrt{(k+2k_c)/m}$).
6. **Travel clamps are the amplitude governor.** Without the dead-stop limits the oscillation slams the numerical ceiling at high pressure; with restitution it chatters. Dead stops (no bounce) are the stable choice; restitution is a refinement for the slap texture.
7. **Neighbour audit.** SP-023 (single reed, stopped cylinder, odd harmonics, $c/4L$); SP-134 (single reed, conical bore — saxophone; same bore series, different valve); SP-065 (lip reed — brass); SP-066 (air jet — flute); SP-124 (free reed — drones, accordion; pitch by the reed, not the bore); SP-131 (two-mass vocal folds — two coupled masses but a glottal source, not a wind-instrument valve). CDRB's identity: **two coupled blades, no rigid lay, aperture = inter-blade gap, bore-controlled pitch, inertance-sustained**. Repo `sound/synthesis/conical_reed.py` (SP-134) and `sound/synthesis/free_reed.py` (SP-124) are the closest modules; CDRB's `double_reed.py` sits between them.
### Python / NumPy Implementation Sketch

```python
"""SP-139 CDRB core (verified prototype: _web139/verify_sp139.py, 12/12 checks)."""
import numpy as np

FS = 44100; RHO = 1.2; C = 343.0
# oboe reed defaults (per blade)
M, FR = 2.35e-6, 2200.0
K = M*(2*np.pi*FR)**2                      # ~450 N/m
ZETA_R, R = 0.22, 2*0.22*np.sqrt(K*M)
H, S, W, CD, L_CH = 5e-4, 3e-5, 5e-3, 0.6, 0.012
X_OPEN, X_CLOS = -1.2*H, H                  # travel limits (dead stops)
ZPEAK, NMODE = 4e7, 14

class DoubleReed:
    def __init__(self, L_eff=0.58, pm=5000.0, zeta_n0=0.008, zeta_slope=0.004,
                 k1=None, k2=None, kc=0.0, seed=1, breath=1e-6):
        self.L_eff, self.pm = L_eff, pm
        self.k1 = k1 or K; self.k2 = k2 or K; self.kc = kc
        self.rng = np.random.default_rng(seed); self.breath = breath
        f0 = C/(2*L_eff)
        n = np.arange(1, NMODE+1)
        self.wn = 2*np.pi*f0*n
        self.zn = zeta_n0 + zeta_slope*n
        self.mu = 2*self.zn*self.wn*ZPEAK/n     # modal drive; p/u at resonance n = ZPEAK/n
        self.x1 = self.v1 = self.x2 = self.v2 = 0.0
        self.u = 0.0
        self.pn = np.zeros(NMODE); self.vpn = np.zeros(NMODE)

    def render(self, dur):
        N = int(dur*FS); dt = 1.0/FS
        out = np.zeros(N)
        umax = CD*(2*W*H)*np.sqrt(2*self.pm/RHO)*2.0
        for t in range(N):
            p = float(self.pn.sum())
            a1 = (S*(self.pm - p) - self.k1*self.x1 - R*self.v1 - self.kc*(self.x1 - self.x2))/M
            a2 = (S*(self.pm - p) - self.k2*self.x2 - R*self.v2 - self.kc*(self.x2 - self.x1))/M
            # velocity-first symplectic Euler (stability: see Pitfall 1)
            self.v1 += dt*a1; self.x1 += dt*self.v1
            self.v2 += dt*a2; self.x2 += dt*self.v2
            if self.x1 > X_CLOS: self.x1, self.v1 = X_CLOS, 0.0
            elif self.x1 < X_OPEN: self.x1, self.v1 = X_OPEN, 0.0
            if self.x2 > X_CLOS: self.x2, self.v2 = X_CLOS, 0.0
            elif self.x2 < X_OPEN: self.x2, self.v2 = X_OPEN, 0.0
            A = min(max(W*(2*H - self.x1 - self.x2), 0.0), 2*W*H)   # no rigid lay
            La = RHO*L_CH/max(A, 1e-12)
            Rq = RHO/(2*CD*CD*A*A)*abs(self.u) if A > 0 else 0.0
            du = (self.pm - p - Rq*self.u)/La                        # inertant channel
            un = self.u + dt*du
            if self.breath > 0:
                un += self.breath*self.rng.standard_normal()*np.sqrt(A)
            un = min(max(un, -umax), umax)
            dudt = (un - self.u)/dt; self.u = un
            self.vpn += dt*(-2*self.zn*self.wn*self.vpn - self.wn**2*self.pn + self.mu*dudt)
            self.pn  += dt*self.vpn                                   # conical modal bank
            out[t] = self.pn.sum()
        return out

# two voicings, one engine
oboe  = DoubleReed(L_eff=0.58,  pm=5000.0)   # f0 = 295.7 Hz (played 294.7, -5.9 cents)
chanter = DoubleReed(L_eff=0.368, pm=5200.0) # f0 = 466 Hz (played 463.6)
```

Cost: $O(N)$ per sample per note ($N$ = 14 modes), pure-Python prototype ~2.5× slower than realtime per note at 44.1 kHz (vectorize across rows / use Numba for the production path). Deterministic per seed; sample-count exact.
### Verification Summary (prototype `_web139/verify_sp139.py`, 2026-11-11)

**12/12 checks pass.** Measured numbers (log `_web139/verify_sp139_output.txt`):

| # | Check | Measured vs reference |
|---|-------|----------------------|
| 1 | static opening vs pressure (symmetric) | 0.733 mm = analytic 0.733 mm |
| 2 | asymmetric blades (k1=1.5K, k2=0.5K) | 0.644 mm = analytic 0.644 mm |
| 3 | collapse pressure | 8000 Pa vs analytic 7484 Pa (6.9 %) |
| 4 | reed free resonance | 2300 Hz vs 2200 Hz (4.5 %) |
| 5 | self-oscillation onset | threshold ≈ 3.0 kPa (floor 2.8e-4 @2.5k → 5.3e2 @5k) |
| 6 | playing pitch | 294.7 Hz vs f0 295.7 Hz (−5.9 cents, Dalmont below-peak) |
| 7 | complete harmonic series + conical-vs-cylinder | h1…h6 = 0/−15.0/−32.6/−26.7/−43.1/−37.6 dB; cylinder h2 −44.4 → 29.4 dB contrast |
| 8 | brightness vs pressure | centroid 860 → 1916 Hz (2.23×) over 4 → 6.5 kPa |
| 9 | valve harmonic generation (300 Hz drive) | flow h2 −14.4 dB, h3 −39.7 dB |
| 10 | determinism | same seed bit-identical; different seed differs |
| 11 | chanter voicing (L_eff 0.368) | 463.6 Hz vs 466 Hz (−8.8 cents), sustained |
| 12 | WAV artifacts + sample count | 141 164 / 105 884 B; lengths exactly 1.6 s / 1.2 s × 44100 × 2 + 44 |

Demo audio: `_web139/sp139_demo_oboe.wav` (peak 295.0 Hz, h2 −24.7 dB), `_web139/sp139_demo_chanter.wav` (peak 465.0 Hz, h2 −23.8 / h3 −22.8 dB).

### References

- Guillemain, P. (2004). "A Digital Synthesis Model of Double-Reed Wind Instruments." *EURASIP J. Applied Signal Processing* 2004(4), 473–481. DOI 10.1155/s1110865704402194.
- Polychronopoulos, S., Marini, N., Bakogiannis, A., & Kouroupetroglou, G. (2021). "Physical Modeling of the Ancient Greek Wind Musical Instrument Aulos: A Double-Reed Exciter Linked to an Acoustic Resonator." *IEEE Access* 9, 98150–98162. DOI 10.1109/ACCESS.2021.3095720.
- Kergomard, J., Guillemain, P., Sanchez, C., & Vergez, C. (2019). "Role of the Resonator Geometry on the Pressure Spectrum of Reed Conical Instruments." *Acta Acustica united with Acustica* 105(6), 1161–1172. DOI 10.3813/AAA.919320.
- Ducasse, E. (2003). "A Physical Model of a Single-Reed Wind Instrument, Including Actions of the Player." *Computer Music Journal* 27(1), 59–75. DOI 10.1162/01489260360613344.
- Avanzini, F., & Rocchesso, D. (2002). "Efficiency, accuracy, and stability issues in discrete-time simulations of single reed wind instruments." *J. Acoust. Soc. Am.* 111(5), 2299–2311. DOI 10.1121/1.1467674.
- Dalmont, J.-P., Gazengel, B., Gilbert, J., & Kergomard, J. (1995). "Some aspects of tuning and clean intonation in reed instruments." *Applied Acoustics* 46(1), 19–62. DOI 10.1016/0003-682X(95)93950-M.
- Fuks, L., & Sundberg, J. (2023). "Blowing pressures in reed woodwinds." Proc. ISMA 2023. DOI 10.25144/15150.
- Aragó Bishop, R., Campbell, D. M., & Woolley, A. (2024). "Double reed sound production on the bass crumhorn." Proc. ISMA 2023. DOI 10.25144/23678.
- Paquier, M., Hendrickx, J., & Jeannin, A. (2016). "Effect of wood on the sound of oboe as simulated by the chanter of a 16-inch French bagpipe." *Applied Acoustics* 104, 91–96. DOI 10.1016/j.apacoust.2015.10.008.
- Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer. Ch. 13 (DOI 10.1007/978-0-387-21603-4_13), Ch. 15 (DOI 10.1007/978-0-387-21603-4_15).
- Scavone, G. P., & Smith, J. O. (1996). "Digital waveguide modeling of woodwind toneholes." *J. Acoust. Soc. Am.* 100(4), 2627. DOI 10.1121/1.416582.
- Wikipedia: "Oboe", "Bassoon", "Reed (mouthpiece)", "Great Highland Bagpipe" (cached `_web139/wiki_*.html`).
