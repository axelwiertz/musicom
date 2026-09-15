# Report — SP-074 Piano Hammer-String Physical Modeling (PHSP)

**Date:** 2026-09-15 (cron sound-production research job)
**Method:** Piano Hammer-String Physical Modeling (PHSP)
**ID:** SP-074 (resolved dynamically: max existing = SP-073 in both summary table and `sound_method_SP-*` / `report_SP-*` file scan; no duplicate found — grep for piano/hammer/Railsback/inharmonicity confirmed only passing mentions in 039 SMA / SP-048 / SP-040 / SP-055)
**Layer:** **absolute** (sound production — Synthesis Engines; per LAYER_ARCHITECTURE.md every SP method is absolute)
**Category:** Synthesis Engines | **Target Output:** Physical Struck-String / Grand-Piano Timbre
**One-line:** physically calibrated piano — Hertz-contact felt hammer (velocity → brightness) strikes a stiff dispersive waveguide string (inharmonic partials + Railsback stretch); detuned unison strings share a bridge impedance (Weinreich two-stage decay); soundboard IR + pedal-down sympathetic resonance complete the instrument.

## Summary-table row (as appended to methods_db.md)

```
| **SP-074** | Piano Hammer-String Physical Modeling (PHSP) | **Synthesis Engines** | Physical Struck-String / Grand-Piano Timbre | Physically calibrated piano: Hertz-contact felt hammer (velocity → brightness, Boutillon/Stulov) strikes a stiff dispersive waveguide string (inharmonic partials $f_n=nf_1\sqrt{1+Bn^2}$ + Railsback stretch tuning), 2–3 detuned unison strings share a bridge impedance for Weinreich two-stage decay, soundboard IR + pedal-down sympathetic resonance. Emits audio from note events; $O(1)$/sample per note. Completes the excitation family: plucked SP-011/048, bowed SP-024, lip-reed SP-065, air-jet SP-066, struck SP-074. |
```

## Line counts
- Before: **17780** lines
- After: **17906** lines (+126: detailed section; +1 summary row = 17907 total file lines — verified by wc below)

## Candidate code path
`sound/synthesis/piano_hammer.py` (new module, sibling of existing synthesis engines in `sound/synthesis/`); integrates with `workflows.musicom_workflow.produce(method="SP-074")` next to SP-001 / SP-011. Existing `sound/` subdirs confirmed: analysis, effects, generators, modular, render, sync, synthesis, tuning, utils.

## Standalone file
`/opt/data/projects/Research/CompositionMethods/sound_method_SP-074_phsp.md` (extended math, railsback/dispersion helper sketch, NumPy voice-class sketch, full references).

## Detailed section appended (verbatim)
See methods_db.md lines ~17781–17906: `# Piano Hammer-String Physical Modeling (PHSP) (Method SP-074)` with `### Source` (Boutillon 1988, Stulov 1995, Weinreich 1977, Fletcher 1964, Railsback 1943, Bank 2003, Smith 2010), `### Layer` (absolute, code path), `### Description` (5-chain: hammer → dispersive string → coupled unisons → soundboard → dampers/pedals), `### Technical Mechanics` (stiff-string PDE, $f_n=nf_1\sqrt{1+Bn^2}$, Hertz contact $F_c=K_c(\xi_h-\xi_s)^p+c_h\Delta\dot\xi$, waveguide injection $y^\pm\pm F_c/2Z_0$, allpass dispersion tuning, $A(t)=A_1e^{-t/\tau_1}+A_2e^{-t/\tau_2}$, Railsback $s(f)=s_{max}\,\mathrm{sgn}(x)x^2$, velocity mapping, O(1) algorithm block), `### Musical Elements Framework` (PITCH/RHYTHM/HARMONY/STRUCTURE/TEXTURE table), `### UnitMatrix Integration` (rows/cols/cells + produce() flow), `### Pitfalls` (9: delay-free loop, ODE stiffness, fractional delay, treble aliasing, sympathetic howl, CPU/commute, velocity zipper, damper clicks, SP-048 confusion), `### Comparison With Related Methods`, `### References` (10).

## Technical mechanics summary
- Stiff string: $\mu\partial_t^2y=T\partial_x^2y-EI\partial_x^4y-R\partial_ty$ → inharmonic partials $f_n=nf_1\sqrt{1+Bn^2}$, $B=\pi^3Ed^4/(64TL^2)$, $B$ from $4\times10^{-5}$ (bass) to $10^{-3}$ (treble).
- Hammer: Hertz contact $F_c=K_c(\xi_h-\xi_s)^p$ ($p\approx2.2$–3.5) + Stulov hysteretic damping; contact 1–5 ms; strike velocity from MIDI velocity drives loudness AND brightness (felt stiffness) AND transient pitch droop.
- Waveguide: two half-length delay lines + 1st-order dispersion allpass (Bank closed-form tuning to the inharmonic target) + 2nd-order loss pole (decay ladder) + free strike-position comb (strike at $L/7$ nulls 7th partial).
- Coupled unisons: 2–3 detuned strings on a shared bridge impedance → Weinreich double decay + unison beating.
- Soundboard: bridge-sum → decaying IR; commutable into per-velocity excitation tables (SP-048 trick).
- Railsback stretch tuning: parabolic in $\log_2 f$, ±30 cents at extremes; precompute per-key $N$, $a_d$ from stretched $f_1$.

## Quirks / pitfalls hit during execution
- Dynamic ID resolution: table max was SP-073 (line 178), file scan max SP-073 — agreed; historical sparse-ID warning (SP-060/SP-160) did not apply but file scan was used as authoritative anyway.
- Known patch pitfalls avoided: summary row verified post-patch — single leading `|` (no `||`), LaTeX backslashes single (`$\sqrt{1+Bn^2}$` intact in re-read line 179).
- methods_db.md uses `||` prefix on many legacy rows (lines 96–114 etc.) — left untouched; new row written with single `|` matching the SP-block convention.
- Section header format matched recent SP entries: `# Name (Method SP-NNN)` + `### Source/Layer/Description/Technical Mechanics/Musical Elements Framework/UnitMatrix Integration/Pitfalls/Comparison/References`.
- No implementation code written this run (documentation job); candidate path `sound/synthesis/piano_hammer.py` is a proposal, consistent with prior SP entries' "candidate code path" convention.

## Verification
```
$ wc -l methods_db.md            → 17907 (after table row)
$ grep -c "SP-074" methods_db.md → summary row + detailed section headers + cross-refs
```
Next free SP ID: **SP-075**.
