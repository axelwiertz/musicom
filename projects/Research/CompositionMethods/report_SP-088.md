# Report SP-088 — Jiles–Atherton Magnetic Tape Saturation Synthesis (JAMS)

**Date:** 2026-09-18 (sound-production research cron job)
**Method ID:** SP-088 (resolved dynamically: global max was SP-087 — summary
table SP-087 TASS; code registry SP-076..SP-086 in
`workflows/musicom_workflow.py`; no `sound_method_SP-088*` / `report_SP-088*`
files existed. Historical sparse-ID hazard avoided by file+code cross-scan.)
**Name:** Jiles–Atherton Magnetic Tape Saturation Synthesis (JAMS)
**Layer:** absolute (sound production — Post-Processing / DSP)
**Paradigm:** Nature-Led-adjacent (physical hysteresis ODE); DB category
Post-Processing / DSP.
**One-line description:** Renders analog tape saturation from magnetic
hysteresis physics rather than a static transfer curve — the Jiles–Atherton
ODE integrates the tape coating's magnetization $M$ sample-by-sample against
the head field $H_e=\alpha M+H$, so compression, slope-dependent harmonics,
NAB head bump, gap loss, and asperity noise emerge from domain physics with
real memory.

## Summary-table row (as appended, line 184 of methods_db.md)

```
| **SP-088** | Jiles–Atherton Magnetic Tape Saturation Synthesis (JAMS) | **Post-Processing / DSP** | Analog Tape Saturation / Magnetic Hysteresis Coloration | Integrates the Jiles–Atherton ferromagnetic hysteresis ODE ($dM/dH_e$ with Langevin anhysteretic $\coth(u)-1/u$, domain pinning $a$, coupling $\alpha$, coercivity $k$, reversibility $c$) per sample against the head field $H_e=\alpha M+H$, so compression, slope-dependent harmonics, NAB head bump, gap loss, and asperity noise emerge from domain physics with real memory (hysteresis state carries across section joins). Feasible ~25 kHz HF bias, singularity-clamped, no oversampling/ADAA needed. Candidate: `sound/effects/tape_saturation.py`. |
```

## Line count

- `methods_db.md` before append: **18679**
- After detailed-section append: 18824 (+145)
- After summary-row patch (current): **18825** lines
- Both landed: summary row at line 184 (verified: single `|` prefix, LaTeX
  backslashes single-escaped — patch-pitfall checks passed), detailed section
  header at line 18681.

## Standalone file

`/opt/data/projects/Research/CompositionMethods/sound_method_SP-088_JAMS.md`
(full write-up: extended math, knob→parameter mapping table, NumPy
implementation sketch, UnitMatrix integration, 8 pitfalls, references).

## Candidate code path

`sound/effects/tape_saturation.py` — sibling of `sound/effects/tape_delay.py`
and the coloration side of `sound/effects/mastering.py`; dispatches via
`workflows.musicom_workflow.produce(method="SP-088")` (registration left to
the weekly-method-code-registration job per the SP collision protocol).

## Technical mechanics (summary)

Per-sample loop: record head (signal×drive + feasible ~25 kHz HF bias) →
effective field $H_e = H + \alpha M$ → delta-method ODE step
$M[n]=M[n-1]+N_{sub}\cdot(dM/dH_e)(H_e)\cdot\Delta H_e$ with

$$dM/dH_e = \frac{(1-c)\,dM_\mathrm{irr}/dH_e + c}{1-\alpha(1-c)\,dM_\mathrm{irr}/dH_e},
\qquad dM_\mathrm{irr}/dH_e = \frac{M_\mathrm{an}-M_\mathrm{irr}}{k\delta-\alpha(M_\mathrm{an}-M_\mathrm{irr})}$$

Langevin $M_\mathrm{an}=M_s[\coth(u)-1/u]$, $\delta=\mathrm{sign}(dH_e/dt)$;
then playback gap-loss LP ($f_g\propto1/\text{speed}$) + NAB head bump shelf
(~70 Hz) + high-passed asperity noise. $\mathcal{O}(N_{sub})$/sample
(~15 flops), monotone under the denominator clamp (no folding → no ADAA /
oversampling needed).

## UnitMatrix integration

Voices = rows (per-voice tape channels with distinct parameter sets);
Sections = columns (per-section drive/bias automation arc; ODE state $M$
carries across joins — never reset mid-song); Cells = MusicUnit (stems from
SP-001/SP-011 post-processed; terminal silent padding must cover the
hysteresis decay tail). Workflow: `compose()` → `produce("SP-001")` →
`produce("SP-088", params=...)` → WAV/OGG.

## Quirks / pitfalls hit during research

1. **ID resolution:** highest table row was SP-087 but code registry top was
   SP-086 — used max(union) = SP-087 → SP-088, per the 2026-09-17 collision
   recipe. No conflicts (`grep SP-088` clean before write).
2. **Sibling subagent concurrent edit:** the summary-row patch returned a
   sibling-modification warning (numeric-methods job active on the same
   file). Mitigation: patch-based targeted edit (not full rewrite), then
   re-verified row line 184, backslashes, `||` prefix, and tail integrity —
   all clean, both jobs' content intact.
3. **Known patch pitfalls avoided:** verified no `\\` double-escaping in the
   new row (`grep -c '\\\\'` = 0) and no `||` prefix.
4. Physics gotchas documented in the section's Pitfalls: denominator
   singularity at loop turning points (clamp $\epsilon$), coth 0/0 near
   zero (Taylor fallback), $M_s$ overshoot (soft clamp), bias aliasing
   (feasible 25 kHz), per-section state reset (carry $M$), LUT regression
   (destroys hysteresis), flux-domain level normalization, double
   saturation when chained after SP-029/SP-019.

## Next free SP ID

**SP-089** (summary table + standalone-file scan both end at SP-088).
