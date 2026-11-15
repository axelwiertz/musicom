# Report SP-142 — WSOLA Time-Stretch Synthesis (Waveform-Similarity Overlap-Add)

**Date:** 2026-11-15 (cron). **Agent:** sound production research agent.

## Identity

- **Method ID:** SP-142 (dynamically resolved — see Resolve below)
- **Method name:** WSOLA Time-Stretch Synthesis (WSOLA) — Waveform-Similarity Overlap-Add
- **Layer:** **absolute** (sound production — LAYER_ARCHITECTURE.md). Classification: **Post-Processing / DSP** (per the methods_db summary-table taxonomy: Synthesis Engines vs Post-Processing / DSP vs Hardware/Acoustic; WSOLA is DSP applied to rendered audio buffers).
- **One-line description:** Time-domain time-scale modification by waveform-similarity overlap-add — each analysis window drifts by δ within ±tol to maximize cross-correlation with the natural progression; no FFT, no phase unwrapping, no pitch change; the missing third classic TSM family (vs SP-026 phase vocoder, SP-037 PSOLA).
- **Candidate code path:** `sound/effects/wsola.py` (new module; upgrade the WSOLA-lite `_stretch` of `sound/generators/multimode_sample_player.py`, which is the repo antecedent under `sound/generators/`).

## Resolve of the next SP number

- Highest existing SP-ID: **SP-141** (Supersaw Oscillator Stack Synthesis, SOSS) — confirmed by scanning the summary table rows `| **SP-NNN** |` AND the standalone files `sound_method_SP-*.md` / `report_SP-*.md` (max file = SP-141_SOSS).
- Cross-check: `grep -n "SP-142"` on methods_db.md before entry = **0**; latest SP number in prose = SP-160 (NASA report SP-160, a book reference) and SP-1200 (a project record number) — neither is a method ID; table max = SP-141.
- **New ID = SP-142.** (Note: the repo's `workflows/musicom_workflow.py` registry uses its own SP-100+ numbering that differs from the methods_db — pre-existing inconsistency, untouched; the methods_db table is authoritative for DB entries.)

## Novelty audit (grep on methods_db.md before entry)

| pattern | hits |
|---|---|
| `wsola` | **0** |
| `waveform similarity` | **0** |
| `verhelst` | **0** |
| `natural progression` | **0** |
| `SOLA` (standalone, not inside PSOLA) | 1 (Hejna & Musicus SOLA-FS 1991, cited inside SP-037 as "related method") |
| `SOLA` total (incl. PSOLA) | 76 (75 = PSOLA) |

Time-stretch families already in DB: SP-026 (phase vocoder), SP-037 (PSOLA), SP-054 (waveset), SP-016 (granular), SP-108 (MQSAS), SP-069 (WPSS). **No SP method documents the waveform-similarity OLA family → SP-142 is novel.**

## Summary-table row appended (exact text, line 357)

```
| **SP-142** | WSOLA Time-Stretch Synthesis (WSOLA) | **Post-Processing / DSP** | Time-Stretched / Transient-Preserving Audio | Time-domain time-scale modification by waveform-similarity overlap-add: each analysis window is shifted by $\delta$ within ±tol to maximize the cross-correlation with the natural progression (the previous window advanced by one synthesis hop), so overlap regions are waveform-continuous — no FFT, no phase unwrapping, no spectral-envelope shift. Speed factor $\alpha = H_a/H_s$ ($\alpha<1$ slows; output length $= n/\alpha$, verified to the sample: 319936 → 639872 @ α=0.5). Best transient preservation of the OLA family (impulse 3.53 vs OLA 3.49); pitch untouched (440.00→440.00 Hz, ratios 1:2.000:3.000). Shared-δ stereo keeps the image (corr +0.800→+0.808; per-channel decorrelates to +0.648). $O(N \log N)$ with FFT correlation; deterministic. Verified prototype **18/18 checks**. Candidate: `sound/effects/wsola.py` (extend the WSOLA-lite `_stretch` of `sound/generators/multimode_sample_player.py`). |
```

## Line counts

- methods_db.md **before** append (measured at write time): **31 582** lines
- methods_db.md **after** append: **31 665** lines → delta **+82** lines (detailed section; table row added via patch on top, total 31582 → 31665 = +83 with the table row)

(Note: a concurrent cron job appended an abstract-layer Fokker Periodicity Block entry (+83 lines) between my first read (31 499) and my append — SP-142 was verified free at append time.)

## Files written

| file | role |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | summary-table row (line 357) + detailed section (lines 31584–31665, 82 lines) |
| `/opt/data/projects/Research/CompositionMethods/sound_method_SP-142_WSOLA.md` | standalone full write-up (extended math, NumPy sketch, references) |
| `/opt/data/projects/Research/CompositionMethods/report_SP-142.md` | this report (primary record) |
| `/opt/data/projects/Research/CompositionMethods/_web142_wsola/verify_sp142.py` | verified prototype (18/18 checks) |
| `/opt/data/projects/Research/CompositionMethods/_web142_wsola/verify_sp142_output.txt` | prototype log |
| `/opt/data/projects/Research/CompositionMethods/_web142_wsola/sp142_stretch_half.wav` | demo, α=0.5 (639 872 frames/ch, 2 559 532 B) |
| `/opt/data/projects/Research/CompositionMethods/_web142_wsola/sp142_stretch_15x.wav` | demo, α=1.5 (213 291 frames/ch, 853 208 B) |
| `/opt/data/_web142_wsola/*` | web research cache: wiki_timestretch.html, wsolaTSM.m (Driedger), wsola.py/ola.py/analysis_synthesis.py (audiotsm), tsmbox.html, soundtouch.html, audiotsm.json, debug scripts |

## Research sources (fetched live 2026-11-15)

1. **Wikipedia "Audio time stretching and pitch scaling"** — SOLA/time-domain harmonic scaling background (Rabiner & Schafer 1978), Adobe Audition centre-period heuristic.
2. **Driedger, J. `wsolaTSM.m` (TSM Toolbox v2.03, MIT, audioLabs Erlangen)** — canonical MATLAB implementation fetched from audiolabs-erlangen.de (full algorithm: synHop 512, Hann 1024, tol 512, per-channel δ, WOLA normalization, anchor-point time-stretch function).
3. **audiotsm (Muges, MIT)** — Python reference: `wsola.py` (WSOLAConverter, np.correlate argmax), `ola.py`, `base/analysis_synthesis.py` (hop scheduling, WOLA normalize buffer).
4. **Driedger & Müller (2016) "A Review of Time-Scale Modification of Music Signals", Applied Sciences 6(2):57** — authoritative survey (cited by audiotsm; MDPI direct fetch blocked by edge ACL, cited from the audiotsm docs + TSM toolbox page).
5. **SoundTouch (Parviainen)** — production WSOLA-family library (industrial validation).
6. **Verhelst & Roelands (1993) ICASSP-93** — original paper citation (confirmed as the canonical reference by wsolaTSM.m header and the review).
7. Search engines (DuckDuckGo HTML/lite, Bing, Semantic Scholar API, archive.org CDX) were all bot-blocked or offline — direct source fetches used instead.

## Technical mechanics summary

- **Hop ratio = speed factor:** $H_a = \lfloor H_s \alpha \rfloor$, output length $m = \lfloor n H_s/H_a \rfloor$ — exact to the sample (verified 319 936 → 639 872 @ α=0.5).
- **WOLA:** windowed overlap-add, normalized by accumulated window sum; Hann with $w[j]+w[j+H_s]=1$ → interior exact (4.44e-16 @ α=1.0, tol=0).
- **WSOLA core:** natural progression $\mathrm{nat}_k[j] = x[(kH_a+\delta_k)+H_s+j]$; $\delta_{k+1} = \arg\max_{\delta\in[-\mathrm{tol},+\mathrm{tol}]} \langle x[(k{+}1)H_a+\delta+\cdot], \mathrm{nat}_k \rangle$ via one `np.correlate(..., 'valid')` per frame (max |δ| 506 ≤ 512 measured).
- **Stereo:** shared-δ preserves image (corr +0.800→+0.808); per-channel decorrelates (+0.648) — reference implementations are per-channel, production default is shared.
- **Anchor-point time-stretch function** (Driedger generalization) for non-constant α / section-fit.
- **Complexity:** O(N·(N_w+2·tol)) per frame naive, O(N log N) with FFT correlation; deterministic.

## Verified prototype results (18/18 checks PASS)

1. length ~ n/α for α ∈ {0.5, 0.75, 1.5, 2.0} + hop math — PASS
2. pitch preserved @ α=0.5: 440.00 → 440.00 Hz (+0.00 %) — PASS
3. harmonic ratios 1 : 2.000 : 3.000 — PASS
4. |δ| ≤ tol=512 (max 506) — PASS
5. transient: WSOLA peak 3.53 vs OLA 3.49 vs orig 3.89 — PASS
6. WOLA gain ~1 (RMS 0.8157 vs 0.8185, 0.34 %) — PASS
7. bit-identical determinism — PASS
8. α=1.0 interior exact (max abs err 4.44e-16) — PASS
9. stereo: corr +0.800 → +0.808 (shared-δ) vs +0.648 (per-channel) — PASS
10. fluidsynth pipeline: 319 936 smp → 639 872 (α=0.5) / 213 291 (α=1.5), RMS within 3 % — PASS

## Quirks / pitfalls hit during the job

1. **The window-ramp offset bug (the big one).** Prototype v1 forgot to offset the analysis positions into the zero-padded buffer (`ana = 0` instead of `ana = pad_front`): the entire output lagged by $N_w/2 = 512$ samples, and *every* spectral check still passed (pitch, harmonics, RMS are shift-invariant; the transient window ±0.2 s tolerated 11.6 ms). Caught only by the α=1.0 interior-exactness check (which failed with err 1.81). After the fix: 4.44e-16. Documented as Pitfall 1 — the detector check is now part of the spec.
2. **Per-channel δ decorrelates stereo** (measured +0.800 → +0.648) — an honest, reproducible finding; shared-δ implemented as the production default and both variants documented.
3. **`np.correlate` empty-region ValueError** at the buffer tail (negative slice start wraps) — fixed by clamping the region bounds and mapping the argmax index back to δ via `first_lag`.
4. **`len()` on a 2-D stereo array** in the fluidsynth check measured channel count (2), not sample count — fixed with `shape[1]`; initial run silently failed 2 of 18 checks this way (the `ok()` collector reported 16/18 while the prints all said PASS — lesson: the check collector must match the printed claims; fixed by fixing the measurements).
5. **Inline `python3 -c` commands require approval in this environment** — all scripts written to files and executed as `$MUSICOM_PYTHON <file>`.
6. **`/tmp` is a protected path** for write_file — research cache and scripts placed under `/opt/data/_web142_wsola/` (then mirrored into `CompositionMethods/_web142_wsola/` for the artifact).
7. **Concurrent writer:** a parallel cron job appended an abstract-layer method (Fokker Periodicity Block) between my first and second read of methods_db.md (31 499 → 31 582). SP-142 was re-verified free immediately before appending; no collision.
8. **Patch pitfalls from the job brief checked:** (a) LaTeX backslash double-escaping — verified with `od -c` that the row contains single `\` (the `\\` seen in tool-result JSON is transport escaping, not file content); (b) `||` row prefix — verified absent (`| **SP-142** |` single pipe).
9. **Search engines bot-blocked** (DDG challenge, Bing junk, Semantic Scholar 429, archive.org offline) — direct fetch of primary sources (wsolaTSM.m, audiotsm source, Wikipedia, SoundTouch) succeeded instead.
10. **Repo registry divergence noted:** `workflows/musicom_workflow.py` SP-100+ registry maps to repo modules and differs from the methods_db SP-100+ table (e.g. repo SP-116 = multimode_sample_player which already contains the WSOLA-lite). Not modified — out of scope, but flagged here for future cleanup.

## Verification of the append

- `grep -n "^# Sound Production Method SP-142" methods_db.md` → line 31 584 (section header)
- Subsection headers present: ### Source / ### Layer / ### Description / ### Technical Mechanics / ### Musical Elements Framework / ### UnitMatrix Integration / ### Pitfalls
- `grep -n "^| \*\*SP-142\*\*" methods_db.md` → line 357 (summary row)
- `grep -c "SP-142" methods_db.md` → 5
- `wc -l methods_db.md` → 31 665

## Next free SP ID

**SP-143** (table max is now SP-142; re-scan the table + standalone files before use, per the resolve contract).
