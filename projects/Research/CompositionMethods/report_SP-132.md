# Report — SP-132 Rotary Speaker Doppler–Amplitude-Modulation Spatialization (RSDA)

**Job:** sound-production research cron · executed autonomously
**Date:** 2026-11-03
**Primary record:** this file. Chat message is a stub only.

| Field | Value |
|---|---|
| Method ID | **SP-132** |
| Method name | Rotary Speaker Doppler–Amplitude-Modulation Spatialization |
| Acronym | RSDA |
| Layer | **absolute** (sound production — LAYER_ARCHITECTURE.md) |
| DB family | Sound Production Methods Framework → Post-Processing / DSP |
| Candidate code path | `sound/effects/rotary_speaker.py` (new); dispatch via `workflows/musicom_workflow.py::produce(method="SP-132", ...)` |
| Standalone write-up | `sound_method_SP-132_RSDA.md` |
| Reference prototype | `projects/Research/outputs/sp132_proto/{leslie_proto,crossover_check,run_doc_sketch}.py` |
| Line count before | **29 779** |
| Line count after | **29 874** (+95) |
| Next free SP ID | **SP-133** |

**One-line description:** models the Leslie rotary cabinet as a rotating point
source whose real propagation delay simultaneously produces Doppler frequency
modulation (`frx = f0(1 − vr/c)`) and directivity/1-over-r amplitude modulation,
split by an 800 Hz LR4 crossover into an independently-rotating treble horn and
bass drum, with motor-inertia speed changes and a two-mic stereo capture.

## ID resolution (dynamic, verified)

- Summary-table scan: highest `| **SP-NNN** |` row = **SP-131** (TMVF, line 336).
- File scan (`sound_method_SP-*.md`): highest = `131_TMVF.md`.
- `SP-160` in the DB is **not** a method ID — it is a bibliographic citation
  ("Leissa, A. W. (1973). *Vibration of Plates*. NASA SP-160", line 9449).
- `Method 132` / `Method 133` in the same file are **composition** methods
  (BIBDC, ZRNC) in a separate numbering space, not SP methods.
- ⇒ new ID = **SP-132**. No duplicate: no rotary/Leslie/Doppler-spatialization
  method exists (closest neighbours: SP-119 auto-pan = level-only pan law,
  SP-106 phaser = phase-only, SP-021/053/129 = HRTF/VBAP/transaural placement,
  SP-055 = frequency shifter).

## Full summary-table row (verbatim as written to methods_db.md)

```
| **SP-132** | Rotary Speaker Doppler–Amplitude-Modulation Spatialization (RSDA) | **Post-Processing / DSP** | Rotary Cabinet Render / Animated Doppler + Tremolo Spatialization | Models the Leslie cabinet as a rotating point source with real propagation delay: $y(t)=g(t)\,x(t-\tau_p(t))$, $\tau_p=d(t)/c$, $d(t)=\sqrt{R^2+r^2-2Rr\cos(\theta-\varphi)}$, motor inertia $d\omega/dt=(\omega_t-\omega)/\tau_m$, $\theta=\int\omega$. From that one geometry: Doppler FM $f_{rx}=f_0(1-v_r/c)$, $v_r=Rr\omega\sin(\theta-\varphi)/d$, and directivity AM $D=10^{-(A/20)(1-\cos(\theta-\varphi))/2}$ on top of inverse-distance $R/d$. Measured (48 kHz, 4-pt Lagrange delay, pure tone, AM off): $\pm2.19$ ¢ at 50 rpm and $\pm21.45$ ¢ at 400 rpm vs theory 2.11/21.01 — deviation is constant in cents, speed-linear, hence $\propto f$ in Hz (12.2 Hz at 1 kHz, FM index $\beta=1.83$). AM depth measured $=A+3.5$ dB ($A=3/6/10/15\to6.5/9.5/13.5/18.5$ dB); spin-up 10–90 % = 0.769 s at $\tau_m=0.35$ s; LR4 crossover at 800 Hz sums flat to 0.0000 dB; louvre reflection 2.5 ms/0.8 → 19.1 dB comb, first null 199 Hz; $\pm90°$ mic pair gives 0.583 ms ITD swing at $+0.334$ correlation. Two rotors with separate motors (horn 50/400 rpm at $r=0.10$ m, drum 40/340 rpm at $r=0.15$ m), 0.583/0.875 ms path swing, second horn throat blocked ⇒ AM at $1\times$ rotation. Sample-count preserving, zero-drift safe, deterministic per seed. Candidate: `sound/effects/rotary_speaker.py`. |
```

## Technical mechanics summary

| Quantity | Expression / value | Verified |
|---|---|---|
| Received signal | `y(t) = g(t)·x(t − τp(t))`, `τp = d/c`, `c = 343 m/s` | model identity |
| Path length | `d(t) = sqrt(R² + r² − 2Rr cos(θ − φ))` | 0.400–0.600 m horn, 0.350–0.650 m drum |
| Delay swing | 0.583 ms (horn r=0.10, R=0.5) / 0.875 ms (drum r=0.15) | measured |
| Motor | `dω/dt = (ωt − ω)/τm` | 10–90 % = 0.769 s at τm = 0.35 s; settle 1 % = 1.57 s |
| Doppler | `frx = f0(1 − vr/c)`, `vr = Rrω sin(θ−φ)/d` | ±2.19 ¢ @ 50 rpm vs 2.11 theory; ±21.45 ¢ @ 400 rpm vs 21.01 (2.1 % err) |
| Doppler law | `Δcents = 1200 log2(1 + rω/c)`, pitch-independent, speed-linear | 40→800 rpm table monotone, error ≤3.7 % |
| FM index @1 kHz, 400 rpm | `β = 12.2 Hz / 6.67 Hz = 1.83` | derived from measurement |
| AM | `g = (R/d)·10^(−(A/20)(1−cos(θ−φ))/2)` | total = A + 3.5 dB (A=3→6.52, 6→9.52, 10→13.52, 15→18.52 dB) |
| Distance AM alone | 3.52 dB at R=0.5, r=0.10 | measured |
| Crossover | LR4 (2× Butterworth-2), fc = 800 Hz | `abs(Hlp+Hhp) = 1.000000`, 0.0000 dB max dev, −6.02 dB/band at fc |
| Cabinet comb | 2.5 ms, gain 0.8 | null 199 Hz, depth −19.1 dB |
| Stereo | mics ±90° | ITD swing 0.583 ms, correlation +0.334 |
| Doc sketch run | extracted from the .md and executed | length preserved 24000→24000, all finite |
| Determinism | seeded rotor phase | yes |

## Quirks / pitfalls hit during this job

1. **Patch fuzzy-match misfire.** The V4A/replace patcher matched an earlier
   occurrence of the anchor and appended the whole SP-132 table row to the tail
   of the previous (ZRNC) pitfalls list, producing `...with \`validate()\` gating.| **SP-132** | ...`.
   Detected by re-reading the patched region; repaired with an exact
   line-index script (`outputs/sp132_proto/repair_row.py`) that cuts the
   fragment and re-inserts it after the SP-131 row. Lesson: for a 2 000-char
   single-line insertion, anchor on the *whole* preceding row or use an index
   script — never on a bare header line.
2. **Pre-existing `||` double-pipe rows.** SP-130 and SP-131 summary rows had
   a `||` prefix (earlier patch damage). Both normalised to a single `|`
   (SP-131 by prefix replace, SP-130 likewise). Verified: `grep '^||'` now
   returns nothing.
3. **LaTeX backslash guard.** The new row and section were checked for `\\`
   double-escaping: 0 occurrences after line 29 776 (`grep -c '\\\\'` on the
   appended range). The row has 6 pipes = 5 columns, matching the header.
4. **Hilbert-IF measurement bias.** First prototype measured 6.41 ¢ at 40 rpm
   where theory says 2.11 ¢ — the AM sidebands corrupt the instantaneous-
   frequency estimate of the *full* model. Re-measured with AM and 1/d
   disabled; measurement then tracks theory to 1.6–3.7 %. Recorded as
   Pitfall #1 of the method (it is a genuine verification trap, not just a
   scripting bug).
5. **Comb null detection.** First `crossover_check.py` reported the "first
   null" at 3000 Hz because of a slicing index bug (`argmin(H[10:])+10`).
   Fixed by masking the band; deepest nulls now report 199 Hz (theory 200 Hz).
6. **`/tmp` is write-protected** in this environment — the prototype lives in
   `projects/Research/outputs/sp132_proto/` (which also satisfies the Research
   AGENTS.md output rule).
7. **Model-vs-hardware scope.** rpm values, crossover band split, dual-horn
   with one blocked throat are from hardware documentation; the numeric
   Doppler/AM/spin-up figures are from *this document's* NumPy reference
   implementation, labelled "measured" accordingly. No claim is made that a
   122 measures exactly ±21 ¢ — the radius is a model parameter (`Δcents`
   scales as `log2(1 + rω/c)`).

## Complete section text appended to methods_db.md

# Sound Production Method SP-132 — Rotary Speaker Doppler–Amplitude-Modulation Spatialization (RSDA)

### Source

- Doppler, C. (1842). "Über das farbige Licht der Doppelsterne…" *Abhandlungen der königl. böhmischen Gesellschaft der Wissenschaften* II(2), 465–482 — the moving-source frequency law $f'=f\,c/(c\mp v)$ that a rotating loudspeaker realizes acoustically.
- Leslie, D. J. (1941–1968). US Patents 2,489,653 (1949, "Rotary Tremolo Device"), 3,036,153, 3,157,246 — the original rotating-baffle/rotating-horn cabinet; the two-rotor (horn above 800 Hz, drum below) architecture and the dual-speed motor scheme.
- Wikipedia, "Leslie speaker" (rev. 2026-10-30) — hardware facts used here: model 122 = single 15″ woofer + compression driver, dual horn where **one horn is audibly blocked** (the pair is for mechanical balance only), chorale **50 rpm horn / 40 rpm drum**, tremolo **400 rpm horn / 340 rpm drum**, "chorale"/"tremolo" switching with an audible speed-change gesture.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed., Wiley — ch. 3 (fractional-delay lines, Lagrange/Thiran interpolators, Doppler simulation) and ch. 5 (modulation effects) — the implementation framework used in the reference prototype.
- Smith, J. O. (2010). *Physical Audio Signal Processing*, W3K/CCRMA — variable delay lines, delay-line interpolation and group-delay error bounds.
- Linkwitz, S. H., & Riley, S. (1976). "Active Crossover Networks for Noncoincident Drivers." *JAES* 24(1), 2–8 — the LR4 (two cascaded Butterworth-2) crossover used to split horn/drum bands.
- Moorer, J. A. (1983). "A Digital Signal Processing Approach to Simulating the Response of Nonlinear Horns." *JAES* — plus Morse & Ingard, *Theoretical Acoustics* (1968), §7 — moving-source radiation, directivity factors, and the near-field/far-field transition that sets the AM-depth-vs-distance trade.
- Reference implementation verified for this document: `projects/Research/outputs/sp132_proto/leslie_proto.py` and `crossover_check.py` (NumPy/SciPy, 48 kHz, 3 s runs).

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). RSDA emits audio buffers at sample rate; it reads a rendered per-row buffer and writes a stereo buffer of identical length — no note events, no symbolic state, no timing authority. It is a **post-processing spatialization stage** that sits after per-row synthesis (SP-001/SP-029/SP-131/SP-095 …) and before the room/dynamics chain. Candidate code path: `sound/effects/rotary_speaker.py` (new module: `Rotor`, `LeslieCabinet`, `TwoMicArray`), dispatch via `workflows/musicom_workflow.py::produce(method="SP-132", ...)`.

### Description

Rotary Speaker Doppler–AM Spatialization models the electromechanical Leslie cabinet as a **rotating point source with a real propagation delay**. A treble horn spins above an acoustic crossover and a bass drum below it; the receiver (a microphone at distance $R$) hears the source travel a modulated path, so the received signal is $y(t)=g(t)\,x(t-\tau_p(t))$ with $\tau_p=d(t)/c$. Two effects fall out of the *same* geometry and cannot be decoupled: **(i) Doppler frequency modulation** — instantaneous frequency $f_{rx}=f_0(1-v_r/c)$ — and **(ii) amplitude modulation** — inverse-distance $R/d$ plus the horn's directivity lobe sweeping past the mic, plus the horn's blocked second throat making the lobe single-sided (AM at exactly $1\times$ rotation). A third, smaller component is the **cabinet reflection comb**, whose path length changes as the rotor faces the louvres.

This is not an LFO vibrato and not an auto-pan: the modulation is *frequency-dependent only in Hz, constant in cents* (every partial shifts by the same relative amount, which is why it sounds like a physical object moving and not like a pitch-shifter), the AM and FM are phase-locked by geometry, and the speed transitions are governed by motor inertia (measured 10–90 % rise of **0.769 s** at $\tau=0.35$ s). Layer-**absolute**: it consumes audio buffers, produces audio buffers, sample-count preserving (zero-drift safe), deterministic.

### Technical Mechanics

**Rotor kinematics (motor inertia).** Angular rate follows a first-order servo:

$$\frac{d\omega}{dt}=\frac{\omega_\text{target}-\omega}{\tau_m},\qquad \theta(t)=\theta_0+\int_0^t\omega(s)\,ds,\qquad \omega_\text{target}=2\pi\,\frac{\text{rpm}}{60}$$

Hardware set points: horn 50 rpm (chorale) / 400 rpm (tremolo), drum 40 / 340 rpm. Measured rise times (10–90 %) at 48 kHz: $\tau_m=0.20\to0.439$ s, $0.35\to0.769$ s, $0.60\to1.318$ s; 1 % settle 0.89 / 1.57 / 2.68 s. This *is* the "speed change" gesture of the instrument.

**Path length and propagation delay.** Source on a circle of radius $r$, mic at distance $R$ and bearing $\varphi$:

$$d(t)=\sqrt{R^2+r^2-2Rr\cos\!\big(\theta(t)-\varphi\big)},\qquad \tau_p(t)=\frac{d(t)}{c},\qquad c=343\ \text{m/s}$$

Measured swing for the horn ($r=0.10$ m, $R=0.50$ m): $d\in[0.400,0.600]$ m → **0.583 ms**; drum ($r=0.15$ m): **0.875 ms**.

**Doppler law.** For $y(t)=g(t)x(t-\tau_p(t))$ the received phase of a partial at $f_0$ is $\phi(t)=2\pi f_0\,(t-\tau_p(t))$, hence

$$f_{rx}(t)=f_0\big(1-\tau_p'(t)\big)=f_0\left(1-\frac{v_r(t)}{c}\right),\qquad v_r(t)=\frac{R\,r\,\omega\,\sin(\theta-\varphi)}{d(t)}$$

so the deviation in cents is **speed-linear and pitch-independent**:

$$\Delta_\text{cents}=1200\log_2\!\left(1+\frac{r\,\omega}{c}\right)$$

Measured (cubic-Lagrange fractional delay, pure 440 Hz tone, no AM — interpolation error 1.6–3.7 %): 40 rpm → **2.19 ¢** (theory 2.11), 400 rpm → **21.45 ¢** (21.01), 800 rpm → **42.97 ¢** (41.78). At 1 kHz the 400 rpm case is $\Delta f=12.2$ Hz at $f_m=6.67$ Hz, i.e. FM index $\beta=\Delta f/f_m\approx1.83$ — enough sidebands to be heard as "warble", not as vibrato.

**Amplitude law.** $g(t)=\dfrac{R}{d(t)}\cdot D(\theta)$, with a smooth two-parameter directivity that is exactly $A$ dB deep over a revolution:

$$D(\theta)=10^{-\frac{A}{20}\cdot\frac{1-\cos(\theta-\varphi)}{2}}$$

Measured: the pure inverse-distance term contributes **3.52 dB** at $R=0.5$, $r=0.10$; total measured AM = $A+3.5$ dB ($A=3\to6.52$, $6\to9.52$, $10\to13.52$, $15\to18.52$ dB). Practical $A$: 8–12 dB horn, 4–7 dB drum. Because the 122's second horn is blocked, the lobe is single-sided → AM at $1\times$ rotation; models that assume two open throats get $2\times$ AM and a conspicuous octave error in the tremolo rate.

**Crossover (LR4).** Two cascaded Butterworth-2 sections per band at $f_c=800$ Hz; per band $-6.02$ dB at $f_c$; verified summed magnitude $|H_{lp}+H_{hp}|=1.000000$ across 20 Hz–20 kHz (**0.0000 dB** maximum deviation). Critical: apply the crossover **before** the rotors and delay-compensate the bands, otherwise the two rotors' independent Doppler shears the crossover point and the acoustic sum combs.

**Cabinet reflection.** A louvre reflection at 2.5 ms with gain 0.8 gives nulls at odd multiples of $1/(2\tau)=200$ Hz (measured deepest null **199 Hz**) and a comb depth of **19.1 dB** (= $20\log_{10}\frac{1-0.8}{1+0.8}$). In the real cabinet this comb *sweeps* as the rotor faces the louvres — model it as a second, slowly-varying tap, never as a static comb.

**Fractional delay.** Read pointer at $D[n]=f_s\,\tau_p(t_n)$; 4-point Lagrange (cubic) is the minimum for tremolo speeds. Delay modulation rate is tiny ($\dot D\approx0.012$ samples/sample at 400 rpm) so interpolation error appears as a few-percent *gain* ripple, not aliasing.

**Two-mic capture.** Mics at $\varphi=\pm90°$: measured **ITD swing 0.583 ms**, inter-mic correlation **+0.334** — i.e. a genuinely decorrelated stereo pair, not a pan-pot. Mono compatibility must be auditioned: the sum loses the comb but keeps the pitch warble.

### Musical Elements Framework

- **PITCH**: the rotor *is* a pitch modulator — $\pm21$ ¢ at 6.67 Hz (tremolo) and $\pm2.6$ ¢ at 0.83 Hz (chorale) for a 0.10 m horn, scaling with $r\omega$. Deviation is constant in cents, so a chord's upper partials move further in Hz: the chord's spectral mass breathes. Detuned twin rotors (two cabinets, or two rows at 398/402 rpm) beat at $|f_1-f_2|$ and produce a chorus that is *physically* phase-incoherent. RSDA never changes the composed pitch — it adds a tempo-adjacent pitch LFO that no score can notate, only instruct ("chorale"/"tremolo").
- **RHYTHM**: the rotation period is a rhythmic rate — 1.20 s (50 rpm) and 0.15 s (400 rpm). Tempo-lock is optional: choose $\text{rpm}=60\cdot\text{BPM}\cdot k/n_\text{rev}$ to place the tremolo on a subdivision (e.g. 120 BPM, quarter-note tremolo = 120 rpm gives 2 cycles/beat). The **speed change** is a composed *rhythmic gesture*: a 0.77 s accelerando that functions as a fill, a lift, or a section marker; the motor inertia makes it un-notatable by an LFO and instantly recognizable.
- **HARMONY**: harmonically neutral by construction (no new partials, only Doppler-shifted ones), but two independent rotors on the same chord create real acoustic beating and a shifting stereo image per partial — a "spread" that reads as harmony thickening without adding voices. Splitting a chord across horn and drum registers (800 Hz crossover) makes the upper triad warble while the bass holds, or vice versa.
- **STRUCTURE**: the macro-form is the **rotor state machine** — stop / chorale / tremolo, plus transition times. A section can be defined by its speed state; a reprise is the return to chorale; a drop is a stop (rotor coasting down over ~2 s, an acoustic tape-stop); a build is a speed ramp that outruns the arrangement. Because the state is a physical integrator, "the arrangement changes speed" is a legitimate structural event.
- **TEXTURE**: two bands, two rotors, two AM depths = a two-layer animated texture. Crossover point sets which register "wobbles"; $A$ sets tremolo depth; mic distance $R$ trades AM for Doppler ($R\to r$ exaggerates AM, $R\gg r$ isolates Doppler); the sweeping reflection comb adds a moving "wooden" coloration. Depth of the whole effect is one scalar per band.

### UnitMatrix Integration

**Voices = rows = rotor feeds.** Row $v$ carries `{rpm_horn, rpm_drum, am_db, r, R, mic_deg, phase0, routing: "horn"|"drum"|"full", seed}`. Two idioms: (a) *per-row cabinet* — each row gets its own rotor phase and mic angle, giving $N$ independent warbles (organ trio: organ, guitar, and a re-amped pad on three cabinets); (b) *shared bus* — all rows summed into one cabinet, which is what the real instrument does and what makes the FM coherent. Per-voice child seed (`seed*101 + row`) keeps phase deterministic.

**Sections = columns = rotor states.** Column $j$ holds `{state: stop|chorale|tremolo, transition_tau, target_rpm}` plus an optional speed ramp. Section seams become **speed transitions**, not just gain changes: a chorale→tremolo change spanning the seam is the arrangement's "gear change". Because $\omega$ is an integrator, the phase carries across the boundary — no reset, no click, and the seam sounds continuous by physics.

**Cells = MusicUnit.** Notes are unchanged (RSDA writes no events). The cell's contribution is *how* its audio is spatially animated: velocity → AM depth (louder = deeper tremolo, the real saturation coupling), note length → whether the rotor completes a revolution inside the note (short staccato at 400 rpm = one warble per note; a long pad = a periodic vibrato). `create_note_unit`/`_unit_from_events` fill as usual, `validate()` gates drift, `to_midi()` exports; RSDA runs afterwards on the rendered stems.

**Produce dispatch:** `produce(midi_path, method="SP-132", params={"rows": [{"routing": "full", "rpm_horn": 400, "rpm_drum": 340, "am_db": 10, "r": 0.10, "R": 0.5, "mic_deg": 90, "seed": 7}, ...], "columns": {"A": {"state": "chorale"}, "B": {"state": "tremolo", "transition_tau": 0.35}, ...}, "crossover_hz": 800, "mics": [-90, 90], "fs": 48000})`. Stage order: per-row source (SP-001/SP-095/SP-029/SP-131 …) → row tone/EQ (SP-007) → **RSDA (crossover → horn rotor + drum rotor → sweeping reflection → two-mic sum)** → room (SP-009/SP-032/SP-075) → dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Chaining convention: RSDA is a *spatializer with pitch side-effects*; where a mix needs clean imaging use SP-021/SP-053/SP-129 instead, and where it needs pure modulation use SP-119/SP-106.

### Pitfalls

1. **AM corrupts naive Doppler measurement.** Estimating instantaneous frequency with a Hilbert transform on the *full* model gave 6.41 ¢ at 40 rpm where theory says 2.11 ¢ — the AM sidebands pull the phase-derivative estimate. Measure Doppler with AM disabled (and $1/d$ off), or fit the delay trajectory directly. Verified separately: with AM off, measurement tracks theory to 1.6–3.7 %.
2. **FM is not vibrato.** Deviation is constant in *cents*, so it is $\propto f$ in Hz: at 400 rpm the fundamental moves 12 Hz while the 8th harmonic moves 97 Hz. Emulating it with a pitch-shifter/LFO on f0 (constant Hz) sounds wrong on bright timbres — modulate the *delay*, not the pitch.
3. **Doppler and AM are one gesture.** Setting them independently (e.g. deep tremolo, no pitch wobble) is a synth patch, not a Leslie. Both come from $d(t)$; only their ratio is free, and only through geometry ($r/R$).
4. **Two open horn throats are wrong for a 122.** The dual horn is symmetric for balance with one throat blocked; assuming two radiating lobes doubles the AM rate (13.3 Hz instead of 6.67 Hz) — a full octave of tremolo error.
5. **Crossover before rotors, bands delay-matched.** Rotating first and filtering after smears the crossover point and produces a wandering notch; measured LR4 sum is flat (0.0000 dB) only when both bands are aligned.
6. **Cabinet comb must sweep.** A static 2.5 ms/0.8 tap gives a fixed 19.1 dB null at 200 Hz — audible as a hollow boom, not as a Leslie. Modulate the reflection tap with the rotor angle, or omit it.
7. **Interpolation quality sets the speed ceiling.** Linear interpolation is acceptable at chorale; at 400 rpm it adds audible loss modulation on high partials. Use cubic Lagrange (verified 2–4 % Doppler accuracy) or a windowed-sinc/Thiran interpolator for mastering; never update the delay once per block — the zipper at 6.67 Hz is obvious.
8. **Nonzero latency, zero length change.** The delay line imposes $\ge (R+r)/c\approx1.75$ ms of latency and needs a pre-roll of the same amount; the output length equals the input length, so zero-drift/loop-seam invariants hold, but do not align the dry and wet by sample zero.
9. **$A$ is not the AM depth you get.** Measured AM = $A + 3.5$ dB because the inverse-distance term rides on top; at small $R$ the distance term dominates and the parameter loses meaning — calibrate against the measured curve.
10. **Mono fold-down and tempo-lock.** The ±90° mic pair is only +0.33 correlated: mono collapse removes the comb and much of the width while keeping the warble — audition mono. And do not assume 400 rpm is "musical" at every tempo: 6.67 Hz at 96 BPM is 4.2 cycles/beat; derive rpm from BPM (or accept the deliberate rub against the grid).
11. **Not a pan law.** RSDA is not SP-119 (auto-pan) or SP-106 (phaser): a pan law changes level only, a phaser changes phase only; RSDA changes *arrival time*, which is why it survives on one speaker as pitch warble. Do not substitute one for the other in a chain.
12. **Two rotors, two rate limits.** Horn and drum have separate motors and separate inertias; a single `rpm` knob makes the bass and treble change speed together, which the hardware never does (and which flattens the classic "the top spins up first" effect).
