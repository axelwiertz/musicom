p = "/opt/data/projects/Research/CompositionMethods/methods_db.md"
lines = open(p).read().split("\n")
i0 = next(i for i, l in enumerate(lines) if l.startswith("# Sound Production Method SP-150"))
section = "\n".join(lines[i0:]).rstrip() + "\n"
row = next(l for l in lines if l.startswith("| **SP-150** |"))

pre = """# REPORT — SP-150 Helmholtz Cavity-Resonator Synthesis (HCRS)

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

"""

mid = """
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
  `grep -o 'f_0=.\\{0,30\\}'` — the file stores single `\\frac`/`\\sqrt` (the diff/read views are
  JSON-escaped, which looks like `\\\\`; do not "fix" it). The only literal double backslash in the
  section is the matrix row separator `\\\\` (correct).
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

"""

report = pre + row + "\n\n" + mid + section
out = "/opt/data/projects/Research/CompositionMethods/report_SP-150.md"
open(out, "w").write(report)
print("wrote", out, len(report), "chars")
print("section lines:", section.count("\n"))
