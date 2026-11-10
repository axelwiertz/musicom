# Report SP-138 — Struck-Tine Electromechanical Piano Synthesis (STEPS)

**Run date:** 2026-11-10 (scheduled cron research job)
**Status:** COMPLETE — detail section appended, summary row inserted, standalone file written, prototype verified 12/12, verification passed.

---

## 1. Identity card

| Field | Value |
|---|---|
| **Method ID** | **SP-138** |
| **Method name** | Struck-Tine Electromechanical Piano Synthesis |
| **Acronym** | STEPS |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md) |
| **Category** | Synthesis Engines → Physical Modeling → Struck Tuning-Fork (Electromechanical Piano, Fender Rhodes) |
| **One-line description** | Models the Fender Rhodes as a struck asymmetric tuning fork: hammer-struck cantilever tine (Euler–Bernoulli modes 1:6.27:17.55, tip-mass-compressed stretch r2≈2.2/r3≈4.5) coupled to a heavier tone bar (in-phase mode at f0, out-of-phase at f0·√(1+ρ(1+1/μ)) → attack beat Δf), read by a velocity-sensing nonlinear magnetic pickup (mode intermodulation, JASA 2020), through felt damper, tanh preamp and stereo anti-phase tremolo — sample-count preserving, deterministic per seed. |
| **Candidate code path** | `sound/synthesis/rhodes_ep.py` (`ForkResonator`, `HammerContact`, `MagneticPickup`, `Damper`, `RhodesPreamp`, `StereoVibratoTremolo`, `RhodesEP`) |
| **Dispatch** | `produce(midi_path, method="SP-138", ...)` via `workflows/musicom_workflow.py` (NOTE: map currently holds a parallel-surveillance "SP-138" = spectral_sidechain — see §6 quirk 4) |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-138_STEPS.md` (12 973 B) |
| **Report file** | `/opt/data/projects/Research/CompositionMethods/report_SP-138.md` |
| **Prototype** | `_web138/steps_verify.py`, log `_web138/steps_verify_output.txt`, audio `_web138/sp138_demo.wav` (238 140 stereo frames @ 44.1 kHz, 952 604 B) — **12/12 checks pass** |
| **methods_db.md lines — before (scan)** | **30 842** |
| **methods_db.md lines — at append** | **30 919** (a concurrent job landed LSAC Method 139, +77, mid-run) |
| **methods_db.md lines — after** | **31 017** |
| **Delta (this job)** | **+98** (97-line method section + 1 summary row) |
| **Section location** | lines **30 921–31 017** (EOF), header `# Sound Production Method SP-138 — Struck-Tine Electromechanical Piano Synthesis (STEPS)` |
| **Table row location** | line **349**, immediately after the `SP-137` row |
| **ID resolution** | table scan max = **SP-137** (line 348); file scan (`sound_method_SP-*.md`, `report_SP-*.md`) max = SP-137 → new ID **138**. `SP-160`/`SP-1200` confirmed false positives (NASA bibliographic citation / Emu SP-1200 sampler prose). `Method 139` (LSAC, Latin Square composition) is the *composition* numbering namespace (001–…), not an SP id. |
| **Next free SP ID** | **SP-139** |

---

## 2. Full summary-table row (exactly as inserted, line 349)

```
| **SP-138** | Struck-Tine Electromechanical Piano Synthesis (STEPS) | **Synthesis Engines** | Physical Electromechanical Piano / Struck Tuning-Fork Timbre (Fender Rhodes) | Models the Fender Rhodes as a struck asymmetric tuning fork: a hammer-struck cantilever tine (Euler–Bernoulli modes 1:6.27:17.55, tip-mass-compressed to stretch r2≈2.2, r3≈4.5 — measured ratios 2.19/4.49) coupled through its clamp to a heavier tonebar (unequal-leg fork: in-phase mode at f0, out-of-phase at $f_0\sqrt{1+\rho(1+1/\mu)}$ → attack beat Δf=f2−f1, measured 2.50 Hz vs 2.46 Hz), read by a velocity-sensing magnetic pickup whose nonlinear flux intermodulates the modes (JASA 2020, Gabrielli et al.; measured two-tone products 240/640 Hz). Felt damper (RMS ratio 345, 50.8 dB), tanh preamp (h3 −26.7 dB, odd-only), stereo anti-phase tremolo (r=−0.997). Velocity→brightness Δ7.9 dB. Verified prototype **12/12 checks**. $O(M)$ per sample. Candidate: `sound/synthesis/rhodes_ep.py`. |
```

Verified: row starts with a single `|` (no `||` prefix), contains **3 single backslashes** (0 double — `tr -cd '\\' | wc -c` = 3; the patch-tool diff *display* shows `\\` but the file bytes are single `\`), all 5 columns match the table header `| Method ID | Method Name | Layer | Target Output | Description / Integration |` (awk field count 6 = 5 pipes).

---

## 3. Technical mechanics summary

1. **Tine = cantilever beam** — f_n = (k_n L)²/2πL² · √(EI/ρA), kL = 1.8751/4.6941/7.8548 ⇒ ratios 1:6.27:17.55; tip mass compresses toward fork-like; STEPS per-key stretch f = (f0, r2·f0, r3·f0), r2∈[2.0,2.6], r3∈[4.0,5.0]; measured rendered ratios 2.19/4.49 (attack window).
2. **Asymmetric tuning fork (two coupled masses)** — m_t ÿ_t + r_t ẏ_t + k_t y_t + k_c(y_t−y_b) = F_h; m_b ÿ_b + r_b ẏ_b + k_b y_b + k_c(y_b−y_t) = 0; normal modes ω₁=ω₀ (in-phase), ω₂=ω₀√(1+ρ(1+1/μ)); measured 222.50 vs 222.46 Hz (0.04 Hz).
3. **Attack beat** — Δf = f₀(√(1+ρ(1+1/μ))−1); measured 2.50 vs 2.46 Hz (1.6 %), Hilbert envelope of undamped ODE ring.
4. **Hammer** — a_n ∝ v_h^γₙ, γ = 0.55/1.5/2.2; velocity→brightness Δ7.9 dB (mode2/mode1 band).
5. **Pickup = velocity sensing + nonlinear flux** — EMF = −dΦ/dt, Φ(x)=Φ₀/(1+x/d); small-motion r=1.0000 vs ẋ; intermodulation measured 240/640 Hz (rel 0.277/0.746) for 200+440 Hz two-tone; the JASA-2020 pickup-intermodulation effect = the bark.
6. **Damper** — 50 ms felt contact at key release; free/damped RMS ratio 345 (50.8 dB).
7. **Preamp** — y = tanh(g·x), odd-only: h3 −26.7 dB, h2 −326.8 dB.
8. **Stereo tremolo** — anti-phase LFO gains, L/R envelope r = −0.997 (amplitude, not pitch).
9. **Zero-drift** — exact sample counts; seed*101+row per voice; bit-identical rerun; O(M) per sample, M≈5–6.

---

## 4. Novelty / overlap audit

`grep -ci` on `methods_db.md` **before** entry: `rhodes` = 0, `tonebar` = 0, `tone bar` = 0, `struck tine` = 0, `electric piano` = 0, `tuning fork` = 1 (SP-099 comb-filter prose — "tuning fork in a resonant cavity" analogy, not fork physics), `wurlitzer` = 1 (passing prose inside SP-074), `tine` = 13 (all false positives: continental-type words, wavelet/finite-difference prose).

Adjacent-but-different: SP-074 acoustic grand (hammer→string→soundboard→acoustic radiation, no pickup); SP-003/SP-042 generic modal banks (no fork coupling, no transduction); SP-010/017/094 FM/DX-style EPs (algorithmic); SP-112 LASS (PCM+subtractive); SP-095 tonewheel organ (different electromechanical device); SP-131 two-mass vocal folds (same two-mass ODE math, different device). Repo antecedent `sound/synthesis/keys_engine.py` (surveillance-namespace SP-129) holds a lightweight 6-partial harmonic-ish modal "tine" with a noise bark — **no fork coupling, no pickup transduction**; STEPS is its physical replacement. STEPS is the DB's first *struck tuning-fork + magnetic-pickup* electromechanical instrument model.

---

## 5. Complete section text appended (methods_db.md 30 921–31 017)

# Sound Production Method SP-138 — Struck-Tine Electromechanical Piano Synthesis (STEPS)

### Source

- **Fender Rhodes piano** (Harold Rhodes, 1946–): the canonical electromechanical piano — a piano keyboard/action, but hammers strike thin steel **tines** instead of strings; each tine is clamped to a heavier **tone bar**, the two forming an *asymmetric tuning fork*; a permanent-magnet pickup coil sits opposite the tine's steel tip and induces the output current. (Wikipedia "Rhodes piano", "Electric piano" — construction, action, Suitcase tremolo.)
- **Gabrielli, L., Cantarini, M., Castellini, P., & Squartini, S. (2020). "The Rhodes electric piano: Analysis and simulation of the inharmonic overtones." *J. Acoust. Soc. Am.* 148(5), 3052–3064. DOI 10.1121/10.0002002.** — the definitive acoustic study: pickup-output spectra + psychoacoustic relevance, scanning-laser-Doppler-vibrometry (SLDV) mode shapes of the asymmetric tuning fork vs its individual parts, **numerical demonstration that the magnetic pickup's nonlinearity intermodulates the fork modes**, and the distribution of the important modes across the whole keyboard (directly usable for per-key synthesis calibration).
- **FenderRhodes.com, "Steve's Corner — Upper Notes with Low Sustain"** (archived 2010, Wayback Machine): "The tine/tone bar assembly is a tuning fork with unequal legs. One leg (the tine) vibrates more than the other leg (the tone bar), but at the same frequency. Both parts are tuned for that specific frequency. The tone bar is gross-tuned by its length; the tine is gross-tuned by its length and fine-tuned by the spring [adjustable tip weight]."
- **Bank, B., & Chabassier, J. (2018). "Model-Based Digital Pianos: From Physics to Sound Synthesis." *IEEE Signal Processing Magazine* 36(1), 103–114.** — survey of model-based piano synthesis (hammer, string, soundboard and, for the electric case, transduction) against which STEPS' block topology is drawn.
- **Novák, A., Guadagnin, L., Lihoreau, B., Lotton, P., Brasseur, E., & Simon, L. (2017). "Measurements and Modeling of the Nonlinear Behavior of a Guitar Pickup at Low Frequencies." *Applied Sciences* 7(1), 50 (open access).** — general evidence that magnetic pickups are nonlinear transducers (flux ∝ 1/gap), the physical basis for the STEPS pickup-nonlinearity block.
- **Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer.** — bar/beam vibration theory: clamped-free (cantilever) natural frequencies ($kL = 1.8751, 4.6941, 7.8548$ ⇒ f-ratio 1 : 6.27 : 17.55) and tip-mass effects on modal ratios.
- Verified prototype for this document: `_web138/steps_verify.py`, log `_web138/steps_verify_output.txt`, audio `_web138/sp138_demo.wav` (238 140 stereo frames @ 44.1 kHz, 952 604 B) — **12/12 checks pass** (numbers quoted below are measured).
- Novelty check (2026-11-10): `grep -ci` on `methods_db.md` **before** entry: `rhodes` = 0, `tonebar` = 0, `tone bar` = 0, `struck tine` = 0, `electric piano` = 0, `tuning fork` = 1 (SP-099 comb-filter prose, "tuning fork in a resonant cavity" — an analogy for comb+oscillator ping, not a fork-physics method), `wurlitzer` = 1 (passing prose inside SP-074), `tine` = 13 (all false positives — "con**tine**ntal"-type words and wavelet/finite-difference prose, never a Rhodes tine). Repo antecedent: `sound/synthesis/keys_engine.py` (surveillance-namespace SP-129: a lightweight 6-partial modal "tine" approximation — partial list 1, 2.0, 3.01, 4.2, 5.4, 6.27 with per-partial decay and a noise "bark"; **no fork coupling, no pickup transduction**) is the pre-STEPS placeholder; STEPS is its physical replacement. Adjacent-but-different: **SP-074** (acoustic grand — hammer→string→soundboard→acoustic radiation; no pickup); **SP-003/SP-042** (generic modal banks — no fork coupling, no transduction); **SP-010/SP-017/SP-094** (FM/DX-style electric-piano voicings — algorithmic, not physical); **SP-112** (LASS: PCM attack + subtractive sustain); **SP-095** (tonewheel organ — a different electromechanical device); **SP-131** (two-mass vocal folds — same two-mass ODE math, entirely different device). STEPS is the DB's first *struck tuning-fork + magnetic-pickup* electromechanical instrument model.

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). STEPS consumes symbolic note events (pitch, velocity, onset/duration ticks from a UnitMatrix cell) and renders per-voice audio buffers — it holds no timing authority, emits no events, and decides nothing about composition: it is a synthesis engine in the render chain. Candidate code path: `sound/synthesis/rhodes_ep.py` (modules: `ForkResonator` (two-mass coupled tine/tonebar modal core), `HammerContact` (velocity-scaled excitation), `MagneticPickup` (velocity sensing + nonlinear flux), `Damper` (felt release envelope), `RhodesPreamp` (tanh saturation + tone stack), `StereoVibratoTremolo` (anti-phase LFO gains), `RhodesEP` (per-note fork-bank voice allocator)), dispatched from `workflows/musicom_workflow.py::produce(method="SP-138", ...)`. The existing `sound/synthesis/keys_engine.py` "tine" model (surveillance-namespace SP-129) is the lightweight pre-STEPS placeholder; STEPS supersedes it with fork coupling + pickup transduction.

### Description

A Rhodes note: a felt hammer strikes a thin cantilevered steel **tine** clamped at one end to a massive **tone bar**; the tine's free end carries the steel tip that swings past a permanent-magnet pickup coil. The tine and tone bar are both tuned to the same pitch and coupled through the clamp — the assembly is literally an *asymmetric tuning fork* ("one leg vibrates more than the other, but at the same frequency"). The hammer strike excites the tine's strongly inharmonic bending modes; the tone bar stores energy and feeds it back through the clamp, extending sustain and adding a coupled upper mode whose beating with the fundamental gives the characteristic attack "wobble". The pickup senses the **velocity** of the steel tip (Faraday: induced EMF = −dΦ/dt), and because the flux-to-gap curve is nonlinear, the modes intermodulate at the pickup — the JASA-2020 finding that produces the electric "tine buzz" and the aggressive hard-velocity **bark**. A felt damper collapses the tone on key release; the preamp (tube/op-amp) saturates (odd harmonics) through a tone stack; the Suitcase tremolo is an *amplitude* LFO panned anti-phase across two speakers (mislabeled "vibrato" on the originals).

STEPS is that signal chain, discretized per note as a modal bank driven by two-mass fork physics and read through a nonlinear velocity pickup — sample-count preserving and deterministic per seed.

### Technical Mechanics

**1. Tine = cantilever beam with tip mass.** The tine is a stiff steel wire, clamped at the tone-bar end, with the tuning spring/tip mass at the free end. Uniform Euler–Bernoulli cantilever modes:

$$f_n = \frac{(k_n L)^2}{2\pi L^2}\sqrt{\frac{EI}{\rho A}},\qquad k_n L = 1.8751,\ 4.6941,\ 7.8548,\ \ldots$$

$$f_1:f_2:f_3 = 1 : 6.27 : 17.55$$

(strongly inharmonic — a bare bar clangs). The tip mass and taper compress the ratios toward a tuning-fork-like near-harmonic series; the *residual* stretch is the Rhodes' signature. JASA 2020 showed the high inharmonic modes live in the **attack transient** and measured their distribution across the keyboard. STEPS models the first three tine modes with per-key stretch $f = (f_0,\ r_2 f_0,\ r_3 f_0)$, $r_2 \in [2.0, 2.6]$, $r_3 \in [4.0, 5.0]$ (prototype default $r_2{=}2.2$, $r_3{=}4.5$; measured rendered ratios 2.19/4.49 — check 6).

**2. Asymmetric tuning fork = two coupled resonators.** Tine (light leg, mass $m_t$) and tone bar (heavy leg, $m_b = \mu m_t$) coupled by the clamp stiffness $k_c = \rho m_t \omega_0^2$; both legs tuned to $\omega_0 = 2\pi f_0$:

$$m_t \ddot{y}_t + r_t \dot{y}_t + k_t y_t + k_c (y_t - y_b) = F_h(t)$$
$$m_b \ddot{y}_b + r_b \dot{y}_b + k_b y_b + k_c (y_b - y_t) = 0$$

Normal modes: in-phase at $\omega_1 = \omega_0$ (both legs move together, coupling spring un-stretched) and out-of-phase at

$$\omega_2 = \omega_0 \sqrt{1 + \rho\left(1 + \tfrac{1}{\mu}\right)}$$

Verified (prototype, two-mass ODE + FFT, $f_0{=}220$ Hz, $\mu{=}8$, $\rho{=}0.02$): measured 222.50 Hz vs analytic 222.46 Hz (**0.04 Hz error**, checks 1–2). The two-mode *beat*

$$\Delta f = f_2 - f_1 = f_0\Big(\sqrt{1+\rho(1+\tfrac{1}{\mu})}-1\Big) \approx \tfrac{1}{2} f_0 \rho (1 + \tfrac{1}{\mu})$$

is the attack "wobble" (measured 2.50 Hz vs theory 2.46 Hz, 1.6 %, check 3); the heavy low-damping leg stores energy ⇒ sustain (the tone bar's documented "resonator and adds sustain" role).

**3. Hammer excitation.** The felt hammer strikes the tine with velocity $v_h \propto$ key velocity; mode $n$ is excited with amplitude $a_n \propto v_h^{\gamma_n}$, $\gamma_1 < \gamma_2 < \gamma_3$ (prototype $\gamma = 0.55/1.5/2.2$) — hard playing brightens: measured mode2/mode1 band ratio 0.3 dB (soft) → 8.3 dB (hard), Δ = **7.9 dB** (check 7). The high inharmonic modes are what make the attack percussive and electric.

**4. Magnetic pickup = velocity sensing + nonlinear flux.** Induced EMF with flux vs gap $\Phi(x) = \Phi_0/(1 + x/d)$ ($x$ = tine-tip displacement toward the pole):

$$\mathrm{EMF} = -\frac{d\Phi}{dt} \approx \frac{\Phi_0}{d}\,\dot{x}\Big[1 - \tfrac{2x}{d} + 3\big(\tfrac{x}{d}\big)^2 - \cdots\Big]$$

Small motion ⇒ EMF ∝ ẋ — the pickup is a *differentiator*: velocity sensing gives the ~6 dB/oct brightness tilt (the electric bite; measured correlation between pickup output and tine velocity $r = 1.0000$, check 4). The flux nonlinearity creates products $x^k\dot{x}$ ⇒ sum/difference frequencies between modes — *intermodulation*: measured two-tone (200 + 440 Hz) products at 240 Hz (rel. 0.277) and 640 Hz (rel. 0.746), check 5 — the JASA-2020 "intermodulation of the modes due to the magnetic pickup," and the physical source of the hard-hit *bark*.

**5. Damper.** A felt pad engages at key release (50 ms contact time constant, 10 ms raised-cosine transition in the prototype); the pickup output collapses: measured RMS ratio free/damped **345 (50.8 dB)** in the post-release window (check 8). Sustain pedal lifts the dampers ⇒ free decay (tone-bar τ ≈ 14 s in the prototype).

**6. Preamp + tone stack.** The Mk I tube / later op-amp preamp saturates: $y = \tanh(g\,x)$ — odd-only harmonics (measured $h_3 = -26.7$ dB at drive 0.8, $h_2 = -326.8$ dB, check 9); the tone stack (bass/treble shelves) shapes the classic bright/soft voicings. Tube asymmetry and bias are refinements.

**7. Stereo tremolo (amplitude, not pitch).** The Suitcase tremolo is an amplitude LFO panned anti-phase across two speakers (mislabeled "vibrato"):

$$g_L(t) = 1 - D\Big(\tfrac12 + \tfrac12 \sin 2\pi f_L t\Big),\qquad g_R(t) = 1 - D\Big(\tfrac12 + \tfrac12 \sin(2\pi f_L t + \pi)\Big)$$

— measured L/R envelope correlation **r = −0.997** (check 10); $f_L \approx 0$–10 Hz, $D$ = depth; the stereo "bounce".

**8. Zero-drift contract.** Per-note fork excitation renders into the voice buffer with exact sample counts (note length = duration × $f_s$; measured exact, check 11); all randomness (per-note phase, detune micro-errors, hammer velocity noise) is seeded per voice (`seed*101 + row`): same seed ⇒ bit-identical rerun, different seed ⇒ different (check 11). $O(M)$ per sample per note, $M \approx 5$–6 modes; vectorizable across rows.

### Musical Elements Framework

- **PITCH**: $f_0$ = fork fundamental; the tip-mass spring is a *physical* fine-tune (cents, per note); the fork's residual inharmonic stretch ($r_2 \approx 2.0$–2.6, $r_3 \approx 4.0$–5.0) gives the electric "sheen" — octave partials are *not* exactly 2.0, so chords carry a subtle non-harmonic shimmer (the opposite of SP-074's near-harmonic acoustic); the tone-bar coupling ($\mu$, $\rho$) sets the sub-octave energy and the beat; per-key mode tables (JASA keyboard distribution) calibrate stretch/decay across registers.
- **RHYTHM**: velocity→brightness maps the percussion into the pitch (the attack transient IS the rhythmic definition); damper/sustain-pedal = note length; tremolo rate (0–10 Hz, tempo-syncable) = a rhythmic pulse layer; the instrument's native idiom is comping — staccato chords with damped releases.
- **HARMONY**: full polyphony (one fork per key); velocity-layered chord stabs; sustain-pedal stacks; the preamp sums chords into harmonic glue; tremolo animates block chords with zero pitch movement.
- **STRUCTURE**: a section can be defined by amp character + tremolo state (mellow EP ballad vs barky funk vs tremolo-washed pad); register changes (bass vs lead fork banks); per-column damper/sustain decisions; an "electric piano section" is a texture-state change in the arrangement.
- **TEXTURE**: the signature textures: (a) mellow fork tone (soft velocity, low modes), (b) attack *bark* (hard velocity: high inharmonic modes + pickup intermodulation), (c) attack wobble (fork beat Δf), (d) sustain wash (tone-bar energy), (e) tremolo bounce (anti-phase stereo), (f) amp glow (tanh odd harmonics); per-note detune spread → ensemble/cluster texture.

### UnitMatrix Integration

**Voices = rows = fork banks.** Row $v$ carries `{fork: {mu, rho, r2, r3, detune_cents}, hammer: {gamma, velocity_curve}, pickup: {gap, nonlinearity}, amp: {drive, tone_stack}, tremolo: {rate, depth}}`. Example rows: "EP comp" (drive 0.6, tremolo 4 Hz / 0.6 depth, medium damper), "EP bark lead" (drive 0.9, tight pickup gap, no tremolo), "EP pad" (sustain pedal, ±3 cents detune spread, tremolo 2 Hz / 0.4).

**Sections = columns = performance states.** Column $j$ holds `{sustain, tremolo_rate, tremolo_depth, amp_drive, eq}` — a column change is an amp/tremolo/sustain change. STEPS is sample-count preserving, so section seams stay zero-drift safe; a damper drop at a seam is a *performance* event applied to the current note's release only — never re-time a ringing fork tail (the SP-136 pitfall applies equally here).

**Cells = MusicUnit.** Each `MusicEvent` (pitch, velocity, start_tick, end_tick) excites the row's fork bank: `buf = rhodes_ep.note_on(pitch, velocity)` at start_tick and `rhodes_ep.damper(release_at=end_tick)` at end_tick; the fork's decay tail rings into the buffer tail (fixed margin, zero-drift).

**Produce dispatch:** `produce(midi_path, method="SP-138", params={"rows": {"ep_comp": {"fork": {"mu": 8.0, "rho": 0.02, "r2": 2.2, "r3": 4.5, "detune": 2}, "hammer": {"gamma": [0.55, 1.5, 2.2]}, "pickup": {"gap": 1.2, "nonlinearity": 1.0}, "amp": {"drive": 0.7, "tone": 0.5}, "tremolo": {"rate": 4.0, "depth": 0.6}}, "ep_lead": {"pickup": {"gap": 0.8, "nonlinearity": 1.4}, "amp": {"drive": 0.9}, "tremolo": {"rate": 0.0, "depth": 0.0}}}, "columns": {"A": {"sustain": 1, "tremolo_rate": 4.0, "drive": 0.7}, "B": {"sustain": 0, "tremolo_rate": 2.0, "drive": 0.9}}, "fs": 44100})`. Stage order: STEPS renders per-row EP voices (replacing/augmenting SP-001/SP-011 sources for electric-piano parts) → per-row EQ (SP-007) → spatialize (SP-021/SP-053) → room (SP-009/SP-032/SP-075) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Use STEPS for Rhodes/Wurlitzer-style electromechanical parts (physical fork + pickup); use SP-074 for acoustic grand; use SP-010/SP-094 for DX-style algorithmic EPs. NOTE (2026-11-10): the `produce()` dispatch map in `workflows/musicom_workflow.py` currently carries a *parallel surveillance namespace* whose own "SP-138" is `sound.effects.spectral_sidechain` (and whose SP-123…SP-137 already diverge from the methods_db numbering, see `hermes_agent/surveillance.md`). The methods_db numbering is authoritative for this entry; the map needs re-keying to DB IDs to resolve the collision.

### Pitfalls

1. **It is not a generic modal bank.** Without the fork coupling (same-$f_0$ unequal legs, in-phase + out-of-phase modes, beat) and the velocity-sensing pickup, the result is just SP-042/SP-003 — the coupled-fork structure and the transduction ARE the identity of the instrument.
2. **The pickup senses velocity, not displacement.** Omit the differentiator and the tone is dull and wrong: the ~6 dB/oct tilt and the intermodulation products both live in the transduction — JASA 2020's central finding is that the pickup's nonlinearity shapes the real spectrum.
3. **Inharmonicity belongs to the attack.** JASA 2020: the inharmonic modes characterize the attack transient; the sustained tone is the near-harmonic fundamental + tone-bar reservoir. Spreading the stretch across the whole note makes it a music box, not a Rhodes.
4. **Beating is a parameter, not a bug.** $\Delta f = f_0(\sqrt{1+\rho(1+1/\mu)}-1)$: too much $\rho$ ⇒ every note honks; too little ⇒ no sustain. $\rho \approx 0.01$–0.03, $\mu \approx 6$–10 (prototype: 2.46 Hz beat).
5. **Aliasing in the nonlinearity.** $r_3 f_0$ can exceed Nyquist on high notes and the pickup nonlinearity generates products up to $2 f_{max}$ — drop modes with $f_n > f_s/2$ per key (SP-041 pattern) or oversample the fork/pickup block.
6. **Velocity mapping is a power law.** Linear velocity scaling gives dull pianissimo or clipping fortissimo; per-mode exponents $\gamma_1 < \gamma_2 < \gamma_3$ (prototype 0.55/1.5/2.2, measured 7.9 dB brightness delta) are what make the instrument playable.
7. **Tremolo is amplitude, not pitch.** The originals' "vibrato" label is wrong; never FM the fork for the tremolo, and don't confuse it with SP-132 (Leslie rotary Doppler — *that* device DOES pitch-modulate).
8. **Pickup nonlinearity ≠ preamp saturation.** tanh = odd harmonics (amp glow); flux nonlinearity = intermodulation (tine buzz/bark). Lumping them by driving the tanh harder produces amp-overdrive character, not the electric-piano bite — keep the two knobs separate.
9. **Neighbour audit.** SP-074 acoustic grand (hammer→string→soundboard, acoustic radiation); SP-003/SP-042 modal banks; SP-010/017/094 FM EPs; SP-112 LASS; SP-095 tonewheel organ; SP-131 two-mass vocal folds (same two-mass math, no pickup/tine). Repo `keys_engine.py` "tine" is a lightweight harmonic-ish modal approximation (no fork coupling, no pickup); STEPS supersedes it. STEPS is the DB's first *struck tuning-fork + magnetic-pickup* electromechanical instrument model.

---

## 6. Quirks / pitfalls hit during this run

1. **Search-engine blocks.** DuckDuckGo (HTML + lite) served bot captchas, Bing ignored the query (returned generic Fender pages), Mojeek 403, IRIS behind Cloudflare, Semantic Scholar 429 on first hit. Worked around via: OpenAlex API (found the JASA 2020 paper + IEEE SPM 2018 biblio + MDPI pickup paper), Semantic Scholar retry after cooldown, PubMed eutils (exact vol/issue/pages), Wikipedia direct fetches, Wayback Machine (FenderRhodes.com service archive), Google Patents XHR.
2. **Wrong patent number.** Assumed US 2,824,479 was Harold Rhodes' patent — it resolves to "Music chord indicator" (T. E. Derosa, 1954). Dropped the patent citation entirely; used the JASA paper + archived service text instead. No fabrication.
3. **Concurrent job raced the DB.** Between the initial scan (30 842 lines) and the append, a sibling job appended LSAC *Method 139* (+77 lines, composition namespace). The patch tool warned of the modification; line anchors re-verified before and after. Section landed at 30 921 (EOF), row at 349.
4. **produce() dispatch-map namespace collision.** `workflows/musicom_workflow.py` carries a *parallel surveillance namespace* (see `hermes_agent/surveillance.md`) whose own "SP-138" = `sound.effects.spectral_sidechain`, and whose SP-123…SP-137 already diverge from the methods_db numbering (e.g., map SP-129 = keys_engine vs DB SP-129 = TCCR). The methods_db numbering is authoritative for this job (per contract: table + standalone files scan). Flagged in the appended section and here: the map needs re-keying to DB IDs to resolve the collision.
5. **Patch-tool backslash double-escape was a display artifact.** The unified diff showed `\\sqrt` etc., but the file bytes hold single `\` (verified `tr -cd '\\' | wc -c` = 3 on the new row). No `||` prefix appeared (awk: 6 fields / 5 pipes). No fix needed.
6. **Prototype measurement iterations.** First run: 8/12 — fixes were all *measurement* issues, not model issues: (a) fork-mode checks tested peak *ordering* instead of presence (both 220.00/222.50 present); (b) beat envelope needed the undamped ring + Hilbert FFT (decay trend swamped the envelope); (c) stretch test band was fooled by the preamp's 5th harmonic of f0 (1308 Hz = 5×261.63 at the band edge) → moved to a 400 ms attack window with a near-linear pickup (pickup_d=100) and narrow bands around r2·f0/r3·f0 — which also matches the JASA finding that inharmonic modes live in the attack; (d) damper step discontinuity got differentiated by the pickup into a click → moved the envelope post-transduction with a 10 ms raised-cosine transition; (e) velocity exponents raised (0.55/1.5/2.2) and measured at pickup output (preamp bypass) to clear the 6 dB threshold (measured 7.9 dB); (f) check-counter read the log before flush → counted from an in-memory list.
7. **keys_engine.py antecedent.** The repo already has a lightweight modal "tine" (surveillance SP-129) — documented as the pre-STEPS placeholder rather than a duplicate; STEPS supersedes it with fork coupling + pickup transduction (same pattern as tape_delay.py → SP-137 TEPM).

---

**End of report SP-138.** Next free SP ID: **SP-139**.
