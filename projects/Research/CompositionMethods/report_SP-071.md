# Report — SP-071 Dattorro Plate Reverb (DPR)

- **Method name:** Dattorro Plate Reverb (DPR)
- **ID:** SP-071
- **Layer:** absolute (sound production — post-processing / DSP)
- **One-line description:** Algorithmic plate reverberator in the style of the EMT 140: four input all-pass lattice diffusers decorrelate the signal into a recirculating "figure-eight" tank (two cross-coupled delay-line loops with in-loop one-pole HF-damping and four modulated all-pass diffusers), read out through seven ±0.6-weighted taps into a synthetic stereo image. Runs at Dattorro's nominal 29 761 Hz with all delays scaled by $f_s/29761$; slow LFO modulation smears tank modes. The dense, warm plate-class member between SP-009 (convolution IR), SP-032 (FDN) and SP-058 (spring reverb).
- **Next free SP ID:** SP-072

## Summary-table row (added)

`| **SP-071** | Dattorro Plate Reverb (DPR) | **Post-Processing / DSP** | Dense / Warm Algorithmic Plate Reverb Tail | Algorithmic plate reverberator in the style of the EMT 140: four input all-pass lattice diffusers decorrelate the signal into a recirculating "figure-eight" tank (two cross-coupled delay-line loops with in-loop one-pole HF-damping and four modulated all-pass diffusers), read out through seven ±0.6-weighted taps into a synthetic stereo image. Runs at a nominal 29761 Hz with all delays scaled by $f_s/29761$. Slow LFO modulation smears tank modes; decay/damping/diffusion/predelay are the knobs. $O(1)$ per sample; the dense, warm plate-class member between SP-009 (convolution IR), SP-032 (FDN) and SP-058 (spring). |`

## Line-count delta

- Before: 17264
- After (summary row + detail section): 17348
- Delta: +84

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-071_dpr.md`
- Report: `/opt/data/projects/Research/CompositionMethods/report_SP-071.md`
- DB: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row line 173, detail header line 17266)

## Candidate code path

`sound/effects/dattorro_plate.py` (sibling to `room_reverb.py`, `reverb.py`, `shimmer_reverb.py`, and the `fdn_reverb`/`severance` modules). DPR is the natural next member of the existing Schroeder/Moorer reverb family already in `sound/effects/`.

## Technical mechanics summary

1. **All-pass lattice diffuser** — the atomic building block: `y[n] = -g·x[n] + x[n-M] + g·y[n-M]`, all-pass when the two coefficients are equal; `g=0` = pure delay, `|g|→1` = up-sampled first-order all-pass (diffuse burst).
2. **Input stage** — mono sum (0.5×) → predelay → one-pole low-pass (bandwidth `bw=0.9995`) → four series input all-pass diffusers (`g=0.75,0.75,0.625,0.625`; `M=142,107,379,277`).
3. **Figure-eight tank** — two cross-coupled halves; each: AP1 (`g=-0.70`, M=672) → D1 (4453/4217) → one-pole damping LP (`d=0.9995`) → AP2 (`g=0.50`, M=1800/2656) → D2 (3720/3163); cross-coupling `leftSum = decay·D2_R`, `rightSum = decay·D2_L`.
4. **Output taps** — seven ±0.6-weighted taps (Table 2) → synthetic stereo from a mono tank.
5. **Delay modulation** — slow LFOs (0.1–0.18 Hz, ±8–16 samples) modulate tank all-passes to smear static comb modes.
6. **Magnitude truncation / DC hygiene** — fixed-point tail-to-silence (N/A in float); keep 20 Hz DC-block + HPF + 0.5× input gain for headroom.
7. **Cost** — ~11 multiplies + ~25 delay reads per sample, $O(1)$; deterministic per seed.

## Quirks / pitfalls hit during this run

1. **ID resolved dynamically, not assumed** — scanned the summary table (max `SP-070`), standalone files (`sound_method_SP-*.md` → max SP-070), and `report_SP-*.md` (max SP-070); the prior `report_SP-070.md` itself declares "Next free SP ID: SP-071". Also cross-checked `grep -c SP-071` == 0 and `grep -c SP-160/SP-96` were false positives (reference titles only). New ID = **SP-071**.
2. **SP_METHODS registry already has SP-071 claimed** — `workflows/musicom_workflow.py` maps `"SP-071"` → `sound.effects.severance` ("Gated Reverb + Dual-Engine Delay..."), a *different* method than this research job's DB assignment. This is a known artifact of the DB (knowledge) vs. registry (code) split: the methods_db summary table (the DB's truth) maxes at SP-070, so SP-071 is the correct DB next-ID per the task contract ("scan the summary table + standalone files"). Flagged here for the weekly registration job: the registry's SP-071..SP-074 rows were pre-allocated to sound-effect modules *without* DB entries, so a future reconciliation should either renumber those registry rows or accept the DB/registry ID-space divergence. No action taken this run (task scope is DB-only).
3. **PDF fetched + parsed successfully** — Dattorro's "Effect Design Part 1" (JAES 45(9), 660–684) retrieved from `ccrma.stanford.edu/~dattorro/EffectDesignPart1.pdf` (2.3 MB, 25 pages, 103k chars extracted via `pypdf`). Confirmed Table 1 default coefficients (decay 0.50, decay diffusion 1/2 = 0.70/0.50, input diffusion 1/2 = 0.750/0.625, bandwidth 0.9995, damping 0.0005, EXCURSION 16, sample rate 29 761 Hz) and Table 2 output taps directly from the primary source.
4. **Exact delay/tap coefficients cross-verified against two independent re-implementations** — the mstratman FV-1 assembly (`dattorro.spn`) and the Valley Audio "Plateau" VCV Rack C++ (`Dattorro.hpp`): tank delays {4453, 3720, 4217, 3163}, input all-passes {142, 107, 379, 277}, tank all-passes {672, 1800, 908, 2656}, LFO excursion 16, all at the 29 761 Hz clock. All constants agree.
5. **Summary row + detail section landed cleanly** — verified `^| **SP-071**` (single pipe, no `||` prefix), zero `\\\\` double-backslash in the new row, detail header `# Dattorro Plate Reverb (DPR) (Method SP-071)` present. Both known patch pitfalls avoided.
6. **ONE-TREE symlink** — `write_file`/`patch` resolved to `/opt/data/repos/musicom/projects/Research/CompositionMethods/...` (symlink target of `/opt/data/projects/Research/...`); identical resolution, no action needed.

## Appendix — complete section text appended

The full detailed section (### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration, ### Pitfalls, ### Comparison With Related Methods, ### References) was appended to `methods_db.md` under "Sound Production Methods Framework" (detail header at line 17266) and is reproduced verbatim in the standalone file `sound_method_SP-071_dpr.md`.
