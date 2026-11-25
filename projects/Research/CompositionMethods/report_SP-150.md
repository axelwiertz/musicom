# REPORT — SP-150 Helmholtz Cavity-Resonator Synthesis (HCRS)

- **Method name:** Helmholtz Cavity-Resonator Synthesis
- **ID:** SP-150 (next free SP ID after this run: **SP-151**)
- **Acronym:** HCRS
- **Layer:** **absolute** (sound production — LAYER_ARCHITECTURE.md)
- **Category:** Synthesis Engines
- **One-line description:** Renders vessel-flute / bottle / udu / reflex-port sound as a lumped
  acoustic oscillator whose pitch *is* its geometry, `f0 = (c/2pi)*sqrt(A/(V*L_eq))`, excited by a
  saturating jet drive, with losses, hole fingering, membrane coupling and port alignment all
  derived from the same one-mode model.
- **Candidate code path:** `sound/synthesis/helmholtz_cavity.py` (NumPy only; the lumped sibling of
  `sound/synthesis/air_pipe.py`, SP-066). Dispatch: `produce(midi_path, method="SP-150", params=...)`.
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-150_HCRS.md`
- **Prototype:** `_web150_hcris/verify_hcris.py` → `_web150_hcris/verify_hcris_results.txt`
  (**19/19 checks pass**); demo `projects/Research/outputs/sp150_hcris/sp150_hcris_demo.wav`
  (1,536,044 B, 8.0 s stereo, 48 kHz, peak 0.89).
- **Line count of `methods_db.md`:** **before 33,180 → after 33,311** (+131: 130 lines of section,
  plus one line from normalising the trailing newline when the two table rows were reordered).

## Full summary-table row (appended after SP-149)

| **SP-150** | Helmholtz Cavity-Resonator Synthesis (HCRS) | **Synthesis Engines** | Vessel-Flute / Bottle / Udu / Reflex-Port Cavity Timbre | Air in the neck is a mass and air in the cavity a spring, so pitch is geometry: $f_0=\frac{c}{2\pi}\sqrt{A/(V L_{eq})}$ with $L_{eq}=L+0.613a$ (unflanged) / $0.8216a$ (flanged) / $1.463a$ (reflex port). One mode, no partials (harmonics < 0.006 % at any pressure); fingering sums the open hole area ($f\propto\sqrt{A}$ — one extra 8 mm hole on the C5 body = +4.13 semitones); register is volume with a fixed exchange rate of **one octave per 4x cavity** (120 mL = C5, 480 mL = C4, 71.4 L = 30 Hz). Losses are geometric: $Q^{-1}=Q_{rad}^{-1}+Q_{visc}^{-1}+Q_{th}^{-1}$ ($Q$=22.07, tau=13.4 ms, T60=93 ms for 120 mL at C5; treble is *more* damped — C6 $Q$=4.75). Excitation is the flute jet drive reduced to $u_j=C_v\sqrt{2p_m/\rho}$, $u_c=0.4u_j$, $\tau_j=L_j/u_c$ with saturating acoustic flow $G u_j\tanh(p_c(t-\tau_j)/p_{sat})$; the loop phase condition puts the note 1.1 % below $f_0$ and lets breath bend it up +0.17 semitone over 400→1600 Pa (the ocarina's "third of a semitone") with level compressed to +7.97 dB per 4x pressure. Membrane coupling (udu/djembe/ghatam) is the avoided-crossing eigenproblem $f_\pm^2=\frac{f_c^2+f_m^2}{2}\pm\sqrt{((f_c^2-f_m^2)/2)^2+\kappa^2}$ (150/210 Hz → 102.8/236.7 Hz at kappa=20000, trace conserved); a reflex port is the same oscillator tuned below $f_s$ (40 L + 75 mm x 150 mm = 40.08 Hz). $O(1)$ state, ~10 ops/sample, deterministic per seed, sample-count exact (zero-drift safe). Verified prototype **19/19 checks** (`_web150_hcris/verify_hcris.py`; 8.0 s stereo demo WAV, 1,536,044 B). Candidate: `sound/synthesis/helmholtz_cavity.py`. |


## Technical mechanics (condensed)

1. **Tuning law.** `f0 = (c/2pi)*sqrt(A/(V*L_eq))`, `L_eq = L + 0.613a` (unflanged) /
   `0.8216a` (flanged) / `1.463a` (reflex port, one flanged + one free end). Verified 500 mL
   bottle with a 20 mm x 20 mm neck: **267.69 Hz**; flanged variant 257.61 Hz (−3.8 %).
2. **Scaling.** Exactly `f ∝ V^-1/2` and `f ∝ A^+1/2`; one octave down = **4x cavity volume**
   (verified to 1e-12: 120 mL → 480 mL takes C5 to C4). 30 Hz requires 71.4 L with a 75 mm port.
3. **Fingering.** `f ∝ sqrt(sum of open hole areas)`; inverting gives the required area for a
   written pitch. One extra 8 mm hole on the C5 body: x1.2696 = **+4.13 semitones**.
4. **Losses/Q.** `Q^-1 = Q_rad^-1 + Q_visc^-1 + Q_th^-1`, `τ = Q/(π f0)`, `T60 = 6.91τ`.
   Verified 120 mL C5: Q_rad 59.5, Q_visc 38.1, Q_th 440.8 → **Q 22.07, τ 13.4 ms, T60 93 ms**;
   C6 with 4x open area → Q 4.75, τ 1.4 ms (treble is more damped — physical, documented).
5. **Jet drive.** `u_j = Cv*sqrt(2p_m/rho)`, `u_c = 0.4 u_j`, `τ_j = L_j/u_c`, acoustic flow
   `G*u_j*tanh(p_c(t-τ_j)/p_sat)`. Loop phase condition `arg H = 2π f τ_j` puts the note
   **−1.12 %** below f0 at 800 Pa (pred 434.99 vs sim 435.08 Hz, 0.02 % agreement), and breath
   raises it **+0.172 semitone** over 400→1600 Pa (the ocarina "third of a semitone").
6. **Level.** +7.97 dB for 4x mouth pressure vs 12.04 dB linear (labium saturation).
7. **Spectrum.** Harmonics above 1.5 f0 stay **< 0.006 %** at any pressure — the cavity is a
   single mode, so spectral richness must come from breath noise, membrane coupling or the room.
8. **Membrane coupling.** `f±² = (fc²+fm²)/2 ± sqrt(((fc²−fm²)/2)² + κ²)`; avoided crossing,
   sum f² conserved. 150/210 Hz → 144.72/213.67 (κ=6000) → 102.81/236.71 (κ=20000).
9. **Reflex port.** Same oscillator tuned below fs: 40 L + 75 mm x 150 mm → **40.08 Hz**.
10. **Cost / determinism.** One biquad + one delay line + one tanh ≈ 10 ops/sample, O(1) state;
    byte-identical per seed; exact sample count (zero-drift safe).

## Verification summary (19 checks, all pass)

1 bottle 267.69 Hz · 2 exact V/A scaling · 3 end-correction variants (0.25 % vs Wikipedia form) ·
4 C5 needs 82.2 mm² on 120 mL · 5 one hole x1.26958 · 6 losses → Q 22.07 · 7 biquad f0 0.02 % /
Q 0.05 % · 8 jet oscillation 0.02 % vs phase prediction · 9 breath +0.172 semitone, monotone ·
10 +7.97 dB per 4x pressure · 11 avoided crossing, trace conserved · 12 port 40.08 Hz ·
13 30 Hz ↔ 71.4 L · 14 bit-exact determinism, exact length · 15 top register 4.2 % of fs ·
16 harmonics < 0.006 % · 17 octave = 4x volume · 18 C6 more damped than C5 · 19 demo WAV valid.

## Quirks and pitfalls hit during this run

- **Patch/escape check:** the summary row was written with single backslashes and verified with
  `grep -o 'f_0=.\{0,30\}'` — the file stores single `\frac`/`\sqrt` (the diff/read views are
  JSON-escaped, which looks like `\\`; do not "fix" it). The only literal double backslash in the
  section is the matrix row separator `\\` (correct).
- **Table row landed above SP-149:** the anchor patch inserted before the matched row. Fixed by a
  small script that swaps the two adjacent rows; verified order SP-149 → SP-150 and re-checked the
  line count (the rewrite normalised the trailing newline, hence 33,310 → 33,311).
- **Model bugs (all caught by the checks, worth recording for the implementer):**
  (a) *silent synth* — the saturated feedback starts from zero and stays zero; the prototype needed
  an onset noise burst to start oscillation (physically: the player's breath);
  (b) *overflow* — the hand-written RBJ recurrence first used the additive coefficient form and a
  one-sample input history, which is unstable; RBJ is subtractive (`y = x − a1·y1 − a2·y2`) and
  needs two input history taps;
  (c) *Q read 20 % high* — the Hilbert-envelope log-fit picked up end-of-signal artefacts; fixed by
  a median of successive block-log ratios over ~3.7τ;
  (d) *amplitude collapsed as pressure rose* — normalising loop gain by `u_j` removed the very
  pressure dependence that should survive; the flow must scale with `u_j` and be limited by
  `tanh(p_c/p_sat)`;
  (e) *wrong musical claim* — the first draft asserted "harder blowing adds harmonics"; measurement
  showed the opposite (a one-mode resonator filters its own distortion), so the claim was replaced
  by the verified single-mode-purity statement;
  (f) duplicate check numbering after inserting tests — renumbered.
- **Honest limitation:** the single-neck viscous loss model over-damps the treble (C6 Q=4.75);
  real multi-hole ocarinas are less damped, so `q_scale` is exposed as an explicit calibration knob
  (default 1.0) instead of being tuned silently.

## Complete section text appended to `methods_db.md`

# Sound Production Method SP-150 — Helmholtz Cavity-Resonator Synthesis (HCRS)

### Source

- **Helmholtz, H. von (1863), *Die Lehre von den Tonempfindungen* (Eng. *On the Sensations of Tone*, 1875/1954 Dover)** — the cavity-with-a-neck oscillator as an acoustic analyser, and the first derivation of its natural frequency from neck mass and cavity compliance.
- **Rayleigh, Lord (1896), *The Theory of Sound*, vol. II** — the classical treatment of the "Helmholtz resonator" as a single-degree-of-freedom system, and the radiation-resistance argument behind its finite Q.
- **Chanaud, R. C. (1965), "Effects of geometry on the resonance frequency of Helmholtz resonators," *J. Sound and Vibration* 2(2), 105–119** — the geometry-dependent end corrections used here: $\Delta L = 0.613a$ for an **unflanged** (free) opening and $0.8216a$ for a **flanged** (baffled) one.
- **Alster, M. (1972), "Improved calculation of resonant frequencies of Helmholtz resonators," *J. Sound and Vibration* 24(1), 63–85** — practical neck/cavity aspect-ratio corrections for the regime between a pure lump and a pipe.
- **Ingard, U. & Ising, H. (1967), "Acoustic nonlinearity of an orifice," *JASA* 42, 6–17** — amplitude-dependent orifice resistance: the reason pitch and loss move with blowing level.
- **Fletcher, N. H. & Rossing, T. D. (1998), *The Physics of Musical Instruments*, 2nd ed., Springer** — ch. 16 (air-reed instruments) and the vessel-flute discussion: jet drive, the ocarina as a Helmholtz resonator whose pitch is set by *total open hole area*, and the weak overblowing of vessel flutes.
- **Coltman, J. W. (1968), "Sounding mechanism of the flute and organ pipe," *JASA* 44(4), 983–992** — the jet-drive mechanism reused here as the exciter (jet convection at $\approx 0.4\,u_j$, saturating deflection at the labium).
- **Small, R. H. (1973), "Vented-box loudspeaker systems, Part 1: Small-signal analysis," *JAES* 21(5), 363–372** — the bass-reflex port as the *same* Helmholtz oscillator, tuned below the driver's resonance; source of the port-alignment use case.
- **Rossing, T. D. (2000), *Science of Percussion Instruments*, World Scientific** — udu, djembe and ghatam as **cavity + membrane** coupled systems, where covering the port retunes the air spring that loads the skin.
- **Wikipedia, fetched live 2026-11-25 (cached in `_web150_hcris/`):** "Helmholtz resonance" (formula $f_H=\frac{v}{2\pi}\sqrt{A/(V_0L_{eq})}$, $L_{eq}=L_n+0.3D$, applications incl. ocarina/djembe/mouth cavity), "Ocarina" ("blowing more softly lowers the pitch; blowing harder raises it… about a third of a semitone either way is useful; small changes to the flow of air will change the tuning rather than the loudness"), "Udu" (Igbo vessel drum; bass by striking the large hole, pitch by hand position over the small hole), "Bass reflex" (port + box air spring resonance, backwave phase inversion), "End correction" ($\Delta L=0.6r$ for one opening).
- **Verified prototype (this run):** `_web150_hcris/verify_hcris.py` → `verify_hcris_results.txt`; demo `projects/Research/outputs/sp150_hcris/sp150_hcris_demo.wav` (1,536,044 B, 8.0 s stereo 48 kHz). **19/19 checks pass** (Technical Mechanics §10).
- **Novelty check (2026-11-25), `grep -ci` on `methods_db.md` before entry:** `ocarina` = **0**, `vessel flute` = **0**, `bass reflex` = **0**, `udu drum` = **0**, `cavity reson` = **0**, `HCRS` = **0**. `helmholtz` = 24 hits, of which the only *models* are **SP-120** (a 370 Hz coke-can cavity used as the resonance of a *shaker*, driven by particle collisions) and **SP-147** (one Helmholtz **port** supplying the bass drone *inside* a hammered steel shell idiophone). Both treat the cavity as one component of a larger object; **HCRS inverts that — the cavity mode IS the instrument, and the score parameters are the cavity geometry** (volume $V$, open area $A$, neck length $L$), with hole-by-hole fingering, jet-drive tuning, membrane coupling and reflex-port alignment. Adjacent-but-different: SP-066 FLUE (air jet into a **distributed** open-open bore; harmonic series, strong overblowing), SP-101/SP-033/SP-023 (waveguides — many modes), SP-136 (membrane + syahi), SP-149 MBRS (Minnaert **gas bubble** — wall compliance and surface tension, not a rigid cavity), SP-003/SP-042/SP-105/SP-147 (solid eigenmodes). **SP-150 is novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). HCRS is a **Synthesis Engines** sample-rate generator: it consumes note events (pitch, velocity, duration) from rendered UnitMatrix cells plus per-row/per-column geometry parameters and emits PCM of exactly the requested length — no symbolic state, no timing authority, no compositional decisions. It **replaces the per-row source** (SP-001 FluidSynth / SP-066 / SP-101 / SP-149 …) for one or more rows. Stage position: **source** → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140/SP-148) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Candidate code path: `sound/synthesis/helmholtz_cavity.py` (NumPy only — one biquad, one short delay line, one `tanh`, no training, no corpus); dispatch from `workflows/musicom_workflow.py::produce(method="SP-150", ...)`. It is the **lumped sibling** of `sound/synthesis/air_pipe.py` (SP-066): same exciter family, resonator reduced from a bore to a single air spring.

### Description

Blow across a bottle and you hear one note. The air plug in the neck is a **mass**, the air in the cavity is a **spring**, and the pair is the simplest acoustic oscillator there is:

$$f_0=\frac{1}{2\pi}\sqrt{\frac{1}{M_aC_a}}=\frac{c}{2\pi}\sqrt{\frac{A}{V\,L_{eq}}}$$

Everything a vessel flute does follows from that one line. An **ocarina** is this resonator with finger holes: the *summed open hole area* is $A$, so the fingering chart is literally a square-root table. An **udu** is this resonator with a skin over one opening: the membrane loads the air spring, and the two modes repel each other. A **bass-reflex** cabinet is this resonator used as a tuned port. A **bottle** is the unscaled original.

HCRS makes **geometry the score**. Unlike every filter-based method in this database, the timbre is not sculpted — it is *sized*. Three consequences define the method:

1. **One mode, no partials.** The cavity breathes in and out as a whole; the radiated tone is essentially a sine (verified: harmonic energy above $1.5f_0$ is $<0.006\%$ at any blowing pressure). Contrast SP-066/SP-101, where the bore's harmonic series is the sound. Harmonic *content* must therefore be supplied by the exciter noise, the membrane coupling, or the space — never by the resonator.
2. **Register is volume, and the exchange rate is fixed: one octave = 4× cavity volume** ($f\propto V^{-1/2}$, verified exactly). A 120 mL body plays C5; 480 mL plays C4; a 71 L box with a 75 mm port reaches 30 Hz. Pitch is *bought with air*, which is why deep bass requires a reflex port or a membrane rather than a bigger bottle.
3. **Q is geometry, not a knob.** Radiation, neck boundary-layer and cavity thermal losses fix the decay, and because opening holes raises $f$ while raising $A$, treble notes are *more* damped than bass notes (C5: $Q=22.1$; C6: $Q=4.8$ with the single-neck loss model). The instrument gets weaker as it goes higher — the familiar ocarina problem, and a physically honest alternative to a velocity-to-brightness curve.

Pitch is also **breath-sensitive**: the jet's transit delay is part of the oscillation phase condition, so harder blowing shortens the delay and pulls the note *up* — measured +0.17 semitone from 400→1600 Pa, matching the ocarina literature's "about a third of a semitone either way". That is a real expressive axis, but a small one: unlike a flute, breath mostly buys level (and only +8 dB for 4× pressure, because the jet saturates).

In the mix HCRS behaves as a **pure-tone vessel voice**: `ocarina` (melodic, single mode, bright-ish mid register), `bottle` (hollow, breathy, short), `udu` (pitched bass thump with membrane bend), `ghatam` (port-covered pitch bends), `port-pad` (sustained drone whose note is the cavity), `sub-port` (bass-reflex-tuned thump for kick reinforcement).

### Technical Mechanics

**1. Lumped elements and the tuning law.** Neck air mass and cavity compliance:

$$M_a=\frac{\rho L_{eq}}{A}\ \left[\frac{\mathrm{kg}}{\mathrm{m^4}}\right],\qquad
C_a=\frac{V}{\rho c^2}\ \left[\frac{\mathrm{m^4\,s^2}}{\mathrm{kg}}\right],\qquad
f_0=\frac{1}{2\pi\sqrt{M_aC_a}}=\frac{c}{2\pi}\sqrt{\frac{A}{V L_{eq}}}$$

The end correction is where the accuracy lives: $L_{eq}=L+0.613a$ (unflanged, free opening), $L_{eq}=L+0.8216a$ (flanged/baffled), and $L_{eq}=L+1.463a$ for a reflex port (one flanged + one free end, $0.8216+0.613$). Verified (§10.1–3): a 500 mL bottle with a 20 mm dia × 20 mm neck resonates at **267.69 Hz**; choosing flanged over unflanged moves it to 257.61 Hz (**−3.8 %**), and Wikipedia's $0.3D=0.6r$ approximation lands within **0.25 %** of the unflanged value.

**2. Verified tuning table.**

| object | $V$ | $A$ | $L_{eq}$ | $f_0$ |
|---|---|---|---|---|
| bottle | 500 mL | 314 mm² (⌀20) | 26.1 mm | 267.7 Hz |
| ocarina body (C5) | 120 mL | 82.2 mm² | 7.45 mm | 523.3 Hz |
| same body, octave up | 120 mL | 329 mm² | 7.45 mm | 1046.5 Hz |
| one octave down | 480 mL | 82.2 mm² | 7.45 mm | 261.6 Hz |
| bass-reflex box | 40 L | 4418 mm² (⌀75) | 204.9 mm | 40.1 Hz |
| 30 Hz in the same box | 71.4 L | 4418 mm² | 204.9 mm | 30.0 Hz |

**3. Hole-area fingering.** Total open area is the sum of each uncovered hole (plus the voicing window when all are closed): $f\propto\sqrt{A_{\text{open}}}$. Opening one extra 8 mm hole on the C5 body multiplies area by 1.612 and pitch by **1.2696 = +4.13 semitones**. Because the law is a square root, holes are *not* equally spaced in pitch: a small hole near the top of the range changes pitch far more than one at the bottom — the reason ocarina hole sizes are individually tuned and why a naive equal-area fingering chart is badly out of tune.

**4. Losses, Q, decay.** Three loss channels as damping ratios ($Q=1/\delta$):

$$Q_{\text{rad}}=\frac{2\pi L_{eq}c}{A\omega_0},\qquad
Q_{\text{visc}}=\frac{\omega_0 M_a}{R_v},\ R_v=\frac{L\sqrt{2\rho\mu\omega_0}}{\pi a^3},\qquad
Q_{\text{th}}=\frac{2V}{S_w\delta_t(\gamma-1)},\ \delta_t=\sqrt{\frac{2D}{\omega_0}}$$

$$Q^{-1}=Q_{\text{rad}}^{-1}+Q_{\text{visc}}^{-1}+Q_{\text{th}}^{-1},\qquad \tau=\frac{Q}{\pi f_0},\qquad T_{60}=6.91\,\tau$$

Verified for the 120 mL C5 body: $Q_{\text{rad}}=59.5$, $Q_{\text{visc}}=38.1$, $Q_{\text{th}}=440.8$ → $Q_{tot}=22.07$, $\tau=13.4$ ms, $T_{60}=93$ ms. Radiation and the neck boundary layer dominate; thermal losses are an order of magnitude weaker and can be dropped for speed without changing the character.

**5. Jet excitation (why it sounds blown).** The exciter is the flute mechanism reduced to its essentials — jet speed, convection, saturation:

$$u_j=C_v\sqrt{2p_m/\rho},\qquad u_c=0.4\,u_j,\qquad \tau_j=L_j/u_c,$$
$$Q_{ac}(t)=G\,u_j\,\tanh\!\big(p_c(t-\tau_j)/p_{sat}\big)+\text{breath noise}$$

so the acoustic flow into the cavity scales with blowing speed and saturates at the labium, while the delay line carries the jet's travel time. Verified: with $L_j=1.5$ mm and $p_m=800$ Pa, $\tau_j=0.171$ ms and the loop self-oscillates at **435.1 Hz**.

**6. The pitch law falls out of the phase condition.** Oscillation requires the cavity's phase to cancel the jet delay:

$$\arg H(e^{j\omega}) = 2\pi f\tau_j .$$

A two-pole bandpass has $\arg H>0$ only *below* $f_0$, so the note always sits slightly flat of the cavity resonance, and as $u_j$ rises $\tau_j$ shrinks and the note climbs toward $f_0$. Verified: predicted 434.99 Hz vs simulated 435.08 Hz (**0.02 %** agreement), which is **−1.12 % (−0.19 semitone)** below $f_0$; sweeping 400 → 800 → 1600 Pa gives 432.1 / 435.1 / 436.4 Hz, i.e. **+0.172 semitone** — the documented ocarina breath range. No pitch table is required: the deviation is computed from geometry and pressure.

**7. Level saturation.** Amplitude is proportional to jet speed but compressed by the labium's $\tanh$: 4× mouth pressure (2× jet speed) yields **+7.97 dB**, not +12.04 dB. That sub-linear compression is what makes a vessel flute feel "supported" rather than "hit".

**8. Membrane coupling (udu, djembe, ghatam).** A skin over an opening turns the system into two coupled oscillators. In $f^2$ form the modes are the eigenvalues of

$$\begin{bmatrix} f_c^2 & \kappa \\ \kappa & f_m^2\end{bmatrix},\qquad
f_\pm^2=\frac{f_c^2+f_m^2}{2}\pm\sqrt{\Big(\frac{f_c^2-f_m^2}{2}\Big)^2+\kappa^2}$$

with $\kappa$ (Hz²) the coupling. The modes **repel** — an avoided crossing, not a mix. Verified: $f_c=150$, $f_m=210$ Hz gives 150.0/210.0 at $\kappa=0$; $\kappa=6000$ gives 144.7/213.7 (spread 68.95); $\kappa=20000$ gives 102.8/236.7 (spread 133.89), with the trace $\sum f^2$ conserved to machine precision. Musically: the further the skin is tuned from the cavity, the more the pair spreads — the udu's "talking" bend and the djembe's bass/tonic/slap zones come from this one matrix.

**9. Bass-reflex alignment.** The same oscillator with a duct: choosing $f_b$ below the driver's $f_s$ makes the port's rear radiation arrive in phase with the cone's front radiation over the band between the two resonances (Wikipedia "Bass reflex", verified live). 40 L + ⌀75 × 150 mm port tunes to **40.08 Hz**; a 30 Hz tuning needs **71.4 L**. This is the production route to HCRS sub-bass without an unphysically large bottle.

**10. Verified prototype — 19/19** (`_web150_hcris/verify_hcris.py`): (1) bottle 267.69 Hz; (2) exact $V^{-1/2}$ and $A^{+1/2}$ scaling; (3) end-correction variants 267.69/257.61 Hz, Wikipedia form within 0.25 %; (4) ocarina C5 needs 82.2 mm² on 120 mL; (5) one 8 mm hole → ×1.26958; (6) loss decomposition → $Q=22.07$, $\tau=13.4$ ms, $T_{60}=93$ ms; (7) biquad recovers $f_0$ to 0.02 % and $Q$ to 0.05 % from its impulse response; (8) jet-drive oscillation within 0.02 % of the phase-condition prediction; (9) breath → +0.172 semitone, monotone; (10) +7.97 dB for 4× pressure; (11) avoided crossing with $\sum f^2$ conserved; (12) reflex port 40.08 Hz; (13) 30 Hz ↔ 71.4 L; (14) bit-exact determinism and exact sample count; (15) top register 4.2 % of $f_s$; (16) harmonics < 0.006 %; (17) octave = 4× volume to 1e-12; (18) C6 is more damped than C5 ($Q$ 4.75 vs 22.07); (19) demo WAV 8.0 s stereo, 1,536,044 B.

**11. Cost.** Per voice: one biquad (5 multiply-adds), one delay-line read, one `tanh`, one noise generator — $\mathcal{O}(1)$ state and ≈10 ops/sample, cheaper than a Karplus-Strong string. The delay line is at most a few hundred samples ($\tau_j\le1$ ms).

### Musical Elements Framework

- **PITCH**: pitch is exact and analytic — $f=c/2\pi\sqrt{A/(VL_{eq})}$ — so any tuning (including just intonation and microtonal grids) is realised without resampling or filter error, and the same written pitch implies a *specific physical instrument*. Two vessels a few cents apart beat at $\Delta f$, which is the only beating available; there are no upper partials to smear the interval. Bends are real: cover the port, change $A$, and the note glides by the square-root law (the ghatam/udu "talking" gesture). Breath-bend gives a further ±0.2 semitone of natural intonation drift, which is a feature on slow lines and a tuning hazard on fast ones.
- **RHYTHM**: each note is a damped single mode, so articulation is fixed by geometry: bass vessels ring ($\tau$ tens of ms), treble vessels tick ($\tau$ ≈ 1.4 ms at C6). Event density and port-strike technique (strike vs slap vs scrape) are the rhythmic controls; a repeated 4-per-bar udu pattern reads as a pitched bass figure, whereas the same pattern on a bottle row reads as hollow percussion. Because onsets are jet-driven, attack time is a pressure parameter, not a fixed sample — the same cell can be a soft "hoo" or a hard "pop".
- **HARMONY**: with one partial per voice, harmony is literal and transparent — dense clusters stay clean, and the method's harmonic signature is registral rather than spectral. The cavity's pitch can be *retuned mid-note* by port coverage, giving glissando chords and portamento that no sample library can produce. Membrane coupling adds an inharmonic partner mode, so udu rows supply a second, slightly detuned pitch per hit — a controlled beating drone under the harmony.
- **STRUCTURE**: section state is the **instrument itself**: cavity volume (register), hole/port configuration (key), membrane tension (coupling), jet pressure (dynamics). Because each of those is a physical parameter with a known law, a section change can be a *re-instrumentation* (ocarina → udu → reflex sub) rather than an EQ move, and a volume ramp over a section is a smooth registral descent of exactly 6 dB/octave in volume terms (one octave per 4× $V$).
- **TEXTURE**: `pure` (single mode, surgical), `breath` (jet noise up, the "air" of a real ocarina), `membrane` (udu bounce and pitch bend), `port` (covered/uncovered formants and bends), `sub` (reflex-tuned low thump), `cluster` (parallel vessels at slightly different volumes → chorused pure tones). Textural change is coherent because the underlying object stays the same: the ear hears *different vessels*, not different effects.

### UnitMatrix Integration

**Voices = rows = vessels.** Row $v$ carries `{kind: ocarina|bottle|udu|reflex, V_mL, holes: [d_mm, ...], hole_open: 0..1 per note, L_neck_mm, a_mm, end_k, q_scale, breath_pa: [lo, hi], L_jet_mm, membrane: null | {f_mem_hz, kappa_hz2, decay}, seed}`. Each row owns its geometry — so a row has a fixed physical identity (a specific instrument) and its own RNG stream for jet noise, meaning rows never phase-lock.

**Sections = columns = fingering/port state and technique.** Column $j$ holds `{finger_pattern, port_cover: 0..1, breath_pa, technique: blow|strike|slap|scrape, membrane_tension, room_send}`. Fingering is a *column* property because it is the instrument's state; breath is a column-level dynamic contour. Crossfade geometry over ≥50 ms — because each note is rendered from its parameters at onset, no click can occur; only the next events change character.

**Cells = MusicUnit.** Cell $(v,j)$ is a sequence of events: `start_tick` → onset (jet onset ramp or strike), `end_tick` → render window (the mode may ring past `end_tick`; the tail is summed into the row buffer), `pitch` → solved geometry. Given the row's $V$ and $L_{eq}$, the engine solves $A_{\text{open}}=V L_{eq}(2\pi f/c)^2$ and then picks the hole subset whose summed area is closest — **inverting the fingering law**, so the written pitch is realised by an actual playable fingering (and any residual error is reported, not hidden). `velocity` → breath pressure (level + micro-pitch) or strike force.

**Produce dispatch:** `produce(midi_path, method="SP-150", params={"rows": {"lead": {"kind": "ocarina", "V_mL": 120, "holes": [8,8,7,6,5,5,4,4], "breath_pa": [500, 1400], "seed": 4}, "bass": {"kind": "udu", "V_mL": 3200, "port_mm": 90, "membrane": {"f_mem_hz": 138, "kappa_hz2": 6000, "decay": 0.55}, "seed": 9}, "sub": {"kind": "reflex", "V_mL": 40000, "port_mm": [75, 150], "seed": 13}}, "columns": {"A": {"port_cover": 0.0, "breath_pa": 700, "room_send": 0.10}, "B": {"port_cover": 0.35, "breath_pa": 1100, "room_send": 0.28}, "C": {"port_cover": 0.8, "breath_pa": 900, "room_send": 0.42}, "crossfade_ms": 80}})` — stage order **HCRS (per-row source) → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140/SP-148) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**. The single mode means the room does most of the timbral work: a short plate makes the ocarina read as a clay toy, a long hall makes the same row read as a ritual vessel.

### Pitfalls

1. **Expecting a harmonic series.** The cavity is one mode. Writing a "flute-like" line with HCRS gives a pure, slightly hollow tone with no breathy overtones and no overblown octave. Overblowing a real ocarina is famously hard precisely because the next mode is far away; do not fake it by adding harmonics — use SP-066/SP-101 if the bore's series is what you want, or layer SP-019/SP-062 for edge.
2. **Forgetting that register is volume.** Asking for a 40 Hz vessel means a ~70 L cavity unless a reflex port or a membrane is used. The engine should refuse (or warn and substitute a `reflex`/`udu` kind) rather than silently rescale $f_0$ — rescaling breaks the whole "geometry is the score" premise and produces a physically impossible instrument.
3. **The single-neck loss model over-damps the treble.** Verified: C6 comes out at $Q=4.75$ ($\tau=1.4$ ms) because $R_v\propto a^{-3}$ is applied to a body whose extra area actually comes from *many* holes with their own edge losses. Real ocarinas are less damped up high. Keep `q_scale` per row as an explicit calibration knob (default 1.0), and record it in provenance — do not silently multiply $Q$ by 4 and call it physics.
4. **Modulating $f_0$ directly for a bend.** A port-cover or breath bend must integrate phase, $y=\sin(2\pi\!\int f\,dt)$, not $\sin(2\pi f(t)t)$ — otherwise every parameter update clicks. Better: drive the delay-line pressure and let the phase condition produce the bend, as in the prototype.
5. **Picking the wrong end correction.** Unflanged vs flanged is a 3.8 % pitch difference (≈0.65 semitone) — audible and untraceable if the convention is not recorded. Store `end_k` per row and never mix conventions inside one ensemble.
6. **Unstable jet drive.** Without the $\tanh$ saturation the loop either explodes or decays to nothing; with saturation but too little loop gain, low-pressure notes simply fail to speak (observed during development: 400 Pa produced 0.002 RMS at $G=10$). Verify oscillation onset at the *lowest* pressure in `breath_pa` before rendering a take.
7. **Treating coupled modes as a mix.** Cavity + membrane is an eigenvalue problem: the modes move apart and the trace $\sum f^2$ is conserved. Crossfading two sine generators gives a completely different (and wrong) sound, and naive averaging of $f_c$ and $f_m$ misses the split entirely.
8. **Hole-area quantisation.** Because $f\propto\sqrt{A}$, fingerings on a fixed hole set can only hit a discrete pitch grid; requesting a pitch between two fingerings yields a few cents of error (or none, if you allow half-holing). Report the residual and prefer microtonal hole sets over retuning.
9. **Ignoring breath noise.** A perfectly periodic single mode sounds synthetic. The exciter noise (`jitter`, proportional to jet speed) is not decoration: it is the "air" that identifies the instrument, and it should scale with pressure, not be a constant hiss.
10. **Determinism / zero drift.** Seed jet noise per (row, cell, event index) as `seed*101 + row`; same seed and params ⇒ byte-identical WAV. The rendered row buffer must fill exactly the section's tick-converted sample count, with mode tails summed in and truncated at the section seam, asserted before mixing — the same discipline as SP-145/SP-146/SP-147/SP-148/SP-149.
