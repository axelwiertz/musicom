# REPORT — SP-131 Two-Mass Vocal Fold Physical Modeling Synthesis (TMVF)

**Primary record.** Chat delivery is a short caveman summary only; everything is here.

| Field | Value |
|---|---|
| **Method ID** | **SP-131** |
| **Method name** | Two-Mass Vocal Fold Physical Modeling Synthesis (TMVF) |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md): emits audio buffers at sample rate, writes no note events, holds no symbolic state |
| **Category (table)** | **Synthesis Engines** (physical self-oscillating voice source / glottal excitation) |
| **One-line description** | Implements the Ishizaka–Flanagan (1972) two-mass vocal fold model — two coupled nonlinear masses per fold ($m_1{=}1.25{\times}10^{-4}$ kg, $m_2{=}2.5{\times}10^{-5}$ kg, $k_1{=}80$ N/m, $k_2{=}8$ N/m, $k_c{=}25$ N/m) driven by subglottal pressure through a Bernoulli glottal flow $u_g=a_{\min}\sqrt{2P_s/\rho}$ with flow-separation pressures and collision springs — self-oscillating with no vibratory input (van den Berg myoelastic-aerodynamic mechanism), emitting the emergent glottal volume velocity as the physical voice-source replacement for the parametric glottal pulses in SP-015/028/038/067. |
| **Summary table row (verbatim)** | `|| **SP-131** | Two-Mass Vocal Fold Physical Modeling Synthesis (TMVF) | **Synthesis Engines** | Physical Self-Oscillating Glottal Source / Voice Timbre | Implements the Ishizaka–Flanagan (1972) two-mass vocal fold model: two coupled nonlinear masses per fold ($m_1{=}1.25\times10^{-4}$ kg, $m_2{=}2.5\times10^{-5}$ kg, $k_1{=}80$ N/m, $k_2{=}8$ N/m, $k_c{=}25$ N/m), subglottal pressure $P_s$ driving a Bernoulli glottal flow $u_g=a_{\min}\sqrt{2P_s/\rho}$ with flow-separation pressures $P_1=P_s(1-(a_{\min}/a_{g1})^2)$, $P_2=0$ after the vena contracta, and collision springs ($3k$ when the gap closes). Myoelastic-aerodynamic self-oscillation — no vibratory input; RK4 at audio rate. Emergent pitch f0=126.2 Hz at IF72 defaults (measured), f0~k^0.84 tension law, closed quotient 0.18, flow slope −7.7 dB/oct (measured); registers (chest/falsetto/fry) from parameter regimes; breathiness from noise mix. The physical voice-source replacement for the parametric glottal pulses in SP-015/028/038/067; feeds SP-067 KLAT / SP-015 formants / SP-028 LPC unchanged. Deterministic per seed, sample-count preserving (zero-drift safe). Candidate: `sound/synthesis/vocal_fold_model.py`. |` |
| **Candidate code path** | `sound/synthesis/vocal_fold_model.py` (new module) → consumed by `sound/synthesis/kelly_lochbaum.py` (SP-067 tract) or any formant/LPC resonator downstream |
| **Dispatch** | `workflows/musicom_workflow.py::produce(method="SP-131", params={"rows": [...], "columns": {...}, "tract": "kelly_lochbaum"|"formant"|"lpc", "fs": 48000})` |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-131_TMVF.md` (20 521 B) |
| **Verification script** | `/opt/data/repos/musicom/projects/Research/outputs/sp131_research/verify_sp131_tmvf.py` + demo buffers `tmvf_x1/ug/rad.npy` |
| **methods_db.md line count** | **29 613 before** → **29 694 after** section append (+81) → **29 695 after** summary-row insert (+1) |
| **Detailed section location** | `methods_db.md` lines **29 615–29 695** (`# Sound Production Method SP-131 — Two-Mass Vocal Fold Physical Modeling Synthesis (TMVF)` … Pitfall 8), appended at EOF after the BIBDC composition-method tail — per cron-spec write_file → `cat >>` workflow |
| **Summary row location** | `methods_db.md` line **335** (inserted after SP-130 row, before blank line + HOA detailed section) |
| **Next free SP ID** | **SP-132** |

---

## 1. ID resolution (dynamic, not assumed)

| Probe | Result |
|---|---|
| Summary-table scan (`grep -oE '\| \*\*SP-[0-9]{3}\*\* \|'`-style on lines 216–334) | max = **130** (SP-130 row, line 334) |
| `ls sound_method_SP-*.md` (73 files) | max = **130** (`sound_method_SP-130_CNS.md`) |
| `ls report_SP-*.md` (62 files) | max = **130** (`report_SP-130.md`, which itself declares "Next free SP ID: SP-131") |
| `grep -c "SP-131"` before write | **0** (only the two "next free" mentions inside report_SP-130) |
| **Assigned** | **SP-131 = max + 1** |

Numbering-trap note (same as SP-130 run): `workflows/musicom_workflow.py` carries a
separate gear-emulation SP namespace (SP-100…SP-134 — its SP-131 is not the methods-DB
SP-131). The CompositionMethods directory is authoritative for the methods-DB SP space
(report_SP-130 precedent, 2026-11-01), so **SP-131** is correct. Composition "Method
131" (TDRPC) at the DB tail is a different numbering space.

## 2. Novelty check (no duplicate)

| Probe | Hits | Verdict |
|---|---|---|
| `vocal fold` (in methods_db.md) | SP-015 "vocal fold vibrations… glottal pulse source", SP-067 "glottal source (Rosenberg / LF model)" — all *parametric* sources, no physical fold model | gap: physical source missing |
| `two-mass` / `Ishizaka` / `Flanagan two-mass` | **0** in methods_db.md (Flanagan hits are the 1966/1972 *speech textbook* and phase-vocoder references, not the fold model) | no duplicate |
| `laryngeal` / `glottal` as method | SP-067 assumes a glottal pulse; no SP method *is* the glottis | gap confirmed |
| `myoelastic` / `aerodynamic` / `van den Berg` | 0 | — |
| repo code scan `vocal_fold|two_mass|two-mass|Ishizaka|glottal` | 0 code files (only docs + tests mention glottal pulse in `test_singing_voice.py`) | candidate module genuinely new |

Verdict: **genuinely new** — the DB's voice chain (SP-015/028/038/067) all *assume* a
glottal pulse; TMVF *is* the glottis. Closest neighbors distinguished in the doc:
SP-067 (physical tract, parametric source — TMVF replaces that source), SP-121 Van der Pol
(same self-oscillating-oscillator family but aerodynamic drive, not damping sign-flip).

## 3. Research base (web)

- GitHub repo search (`api.github.com/search/repositories`): found two independent
  IF72 implementations — `yossie333/two_mass` (MATLAB, full subglottal/supraglottal tract
  + Pelorson separation) and `kazm00th/ishizaka-flanagan-realtime` (JS/AudioWorklet,
  canonical 1972 parameter values). **Fetched both raw sources** (`two_mass.m` 400 lines,
  `if-core.js` 548 lines) and used them to pin the exact equation forms, the collision
  branch, the ζ-open/ζ-close damping scheme, and the canonical parameter set.
- Wikipedia: "Phonation" (myoelastic-aerodynamic theory, Bernoulli push-pull), "Physical
  modeling synthesis" (vocal fold oscillation + laryngeal airflow as a physical-modeling
  category). Vocal-folds anatomy page had no model equations — did not rely on it.
- Archive.org advancedsearch for the original BSTJ 51(6) 1972 issue scan — the June 1972
  issue is not in the bitsavers BSTJ set (V51N06 missing from the V51N01–V51N10 list);
  used the two MIT-licensed implementations + the published literature (Ishizaka &
  Flanagan 1972; van den Berg 1958; Flanagan & Landgraf 1968; Titze 1988; Story & Titze
  1995; Pelorson 1994; Fant/Liljencrants/Lin 1985 LF model) as the equation authority.

## 4. Verification results (numeric, 48 kHz, NumPy RK4, 0.6 s buffers)

| # | Check | Result | Pass |
|---|---|---|---|
| 1 | Self-oscillation from rest (limit cycle) | amp($\xi_1$) = 4.45e-4 m | ✓ |
| 2 | f0 at IF72 defaults, Ps=800 Pa | 126.2 Hz (male range) | ✓ |
| 3 | Pitch law: kscale=2 → f0 | 226.5 Hz, ratio 1.79 → f0 ~ k^0.84 (super-linear; aerodynamic loading super-stiffens vs linear √(k/m)=1.414) | ✓ |
| 4 | Closed quotient | 0.18 (skewed pulse, 0.1–0.9) | ✓ |
| 5 | u_g unipolar | min = 0.0 | ✓ |
| 6 | Flow spectral slope (200 Hz–4 kHz, steady-state Welch) | −7.7 dB/oct (canonical −6…−14) | ✓ |
| 7 | Radiated dUg/dt slope | −1.7 dB/oct (differentiated, brighter) | ✓ |
| 8 | Determinism (two identical runs) | bit-equal | ✓ |
| 9 | Subglottal threshold (Ps=80 Pa) | decays to 1.4e-9 m — no phonation | ✓ |

**ALL CHECKS: PASS.** Demo buffers (0.4 s @ 48 kHz: fold displacement, glottal flow,
radiated pressure) saved under `outputs/sp131_research/`.

## 5. Quirks / pitfalls hit (this run)

1. **First spectral-slope assertion was wrong, not the code.** The naive single-window
   FFT of the *radiated* derivative measured −0.2 dB/oct — flat, because (a) the window
   included the onset transient, (b) the derivative is genuinely bright. Fixed by
   measuring steady-state Welch slopes of BOTH the flow (which must roll off) and the
   derivative (which is brighter): flow −7.7, radiated −1.7 dB/oct. The physics was
   right; the first measurement was sloppy. Recorded as Doc Pitfall 4/7 nuance.
2. **Pitch scaling is super-linear (f0 ~ k^0.84), not √k.** The linear-spring expectation
   (√2 = 1.414 for kscale=2) measured 1.79 — the aerodynamic pressure coupling adds
   effective stiffness. Reported honestly as the measured law; this is now a documented
   tuning fact (Pitfall 1: naive √(k/m) calibration is ~30% off).
3. **Explicit Euler unstable at the closed phase** (collision springs 3k push the fastest
   eigenmode up) — RK4 required; verified stable at 48 kHz. Documented as Pitfall 2.
4. **Zero-area division** — branch u_g=0 when a_min ≤ 0 (both reference implementations
   do this); documented as Pitfall 3.
5. **`\\` double-escape display trap.** Tool-result rendering JSON-escapes backslashes,
   so `\min` displays as `\\min` and looks like the known patch pitfall (a). Resolved
   with a byte-level check: **SP-131 summary row = 6× single `\`, 0× `\\`; SP-131
   section = 64× single `\` + 1× legitimate `\\` (the `cases` row separator — correct
   LaTeX); standalone = 74× single + 1× legitimate `\\`. No run ≥ 3 anywhere in SP-131
   content.** (The one run-of-4 in the whole file, line 26131, is pre-existing in an old
   section — not mine, left untouched.)
6. **Summary-row pipe prefix.** Inserted with `||` prefix to match SP-127…SP-130
   convention; verified `row.startswith('|| **SP-131**')` True, no `|||`/`|` anomaly.
7. **Append location.** DB tail ends with composition-method docs (BIBDC); the cron
   workflow mandates append-to-EOF (write_file → `cat >>`), which landed the SP-131
   section at lines 29 615–29 695 after that tail. Summary row inserted at the proper
   table position (line 335, after SP-130).

## 6. Deliverables (all written this run)

- [x] Summary table updated: `methods_db.md` line 335 (`|| **SP-131** | … |`)
- [x] Detailed section appended: `methods_db.md` lines 29 615–29 695 (### Source, ### Layer,
      ### Description, ### Technical Mechanics, ### Musical Elements Framework,
      ### UnitMatrix Integration, ### Pitfalls)
- [x] Standalone file: `sound_method_SP-131_TMVF.md` (full math, NumPy implementation
      sketch, references, relation table)
- [x] Report (this file): `report_SP-131.md`
- [x] Verification: `outputs/sp131_research/verify_sp131_tmvf.py` + `tmvf_x1/ug/rad.npy`
      demo buffers; all 9 checks pass
- [x] `wc -l` 29 613 → 29 695; grep SP-131 confirms summary row (335) + detailed section (29 615)

**Next free SP ID: SP-132.**
