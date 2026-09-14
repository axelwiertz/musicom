# Report — SP-073 Transient Shaping via Differential Envelope Processing (TSDE)

- **Method name:** Transient Shaping via Differential Envelope Processing (TSDE)
- **ID:** SP-073
- **Layer:** absolute (sound production — post-processing / DSP)
- **One-line description:** Reshapes the attack/sustain balance of a rendered audio buffer by riding a gain derived from two parallel one-pole envelope followers (fast peak detector vs slow sustain detector); the *difference* is the transient content, boosted/attenuated independently by Attack and Sustain gains and recombined with the original phase/time untouched. No threshold, no ratio, level-independent; the SPL Transient Designer differential-envelope technique. $O(1)$ per sample.
- **Next free SP ID:** SP-074

## Summary-table row (added at line 177, after SP-072 row, before the `---` separator)

`| **SP-073** | Transient Shaping via Differential Envelope Processing (TSDE) | **Post-Processing / DSP** | Transient/Punch & Sustain Shaping (Level-Independent Dynamics) | Reshapes the attack/sustain balance of a rendered buffer by riding a gain derived from two parallel one-pole envelope followers (fast peak detector vs slow sustain detector); the *difference* is the transient content, boosted/attenuated independently by Attack and Sustain gains and recombined with the original phase/time untouched. No threshold, no ratio, level-independent; the SPL Transient Designer differential-envelope technique. $O(1)$ per sample. The transient-shaping counterpart to SP-008 (threshold DRC) and the time-domain partner of SP-072 (frequency-domain split). |`

## Line-count delta

- Before: 17631
- After (summary row + detail section): 17711
- Delta: +80

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-073_tsde.md`
- Report: `/opt/data/projects/Research/CompositionMethods/report_SP-073.md`
- DB: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row line 177, detail header line 17634)

## Candidate code path

`sound/effects/transient_shaper.py` (new module, sibling to `overlap_comp.py`, `production_chain.py`, `mastering.py`, `multiband.py` in `sound/effects/`). Reuses the one-pole envelope-follower logic already in the compressor chain. Signature: `transient_shape(x, fs, attack=1.0, sustain=1.0, ...) -> np.ndarray`.

## Technical mechanics summary

1. **Dual envelope followers** — two one-pole smoothers with separate attack/release coefficients: fast peak detector ($\tau_a$≈1–5 ms, $\tau_r$≈30–80 ms) rides the transient leading edge; slow sustain detector ($\tau_a$≈20–60 ms, $\tau_r$≈300–800 ms, optional RMS) rides the steady body. Coefficient $\alpha=1-e^{-1/(\tau f_s)}$.
2. **Differential decomposition** — transient excess $T[n]=\max(0, E_f[n]-E_s[n])$, body $B[n]=E_s[n]$, normalized mix $m[n]=T/(T+B+\varepsilon)$.
3. **Gain riding** — $g[n]=S+(A-S)m[n]$ with Attack $A$ and Sustain $S$; output $y[n]=x[n]g[n]$, optional tanh soft-limit.
4. **Smoothing & make-up** — one-pole lowpass (~5 ms) on $g[n]$ de-zips; make-up gain + post-limiter keep it a *shape* change not a loudness change; optional 2–5 ms look-ahead for true zero-attack.
5. **Cost** — $O(1)$ per sample per channel, no FFT, no sidechain, deterministic (no RNG) → zero-drift gate passes trivially.
6. **Parallel variant** — split into transient audio $x_T=x\,m$ and sustain audio $x_S=x(1-m)$, each through its own FX chain (SP-062 saturation / SP-008 compression), re-sum.

## Quirks / pitfalls hit during this run

1. **ID resolved dynamically, not assumed** — scanned the summary table (max `SP-072`), standalone files (`sound_method_SP-*.md` → max SP-072), and `report_SP-*.md` (max SP-072). Prior `report_SP-072.md` declares "Next free SP ID: SP-073". New ID = **SP-073**. Next free = **SP-074**.
2. **No duplicate** — grepped the DB for candidate names before committing: `transient shaper` (1 hit, only an HPSS "pair with" note), `transient designer` (0), `envelope follower` (2, both passing mentions in FDLMS/other sections), `noise gate` (0), `expander` (0), `bitcrusher` (0). Confirmed no existing transient-shaping or level-independent dynamics method. SP-008 (DRC) is a *threshold* compressor — explicitly different mechanism.
3. **Method-selection check** — rejected several alternatives as already-covered: bitcrusher (no — sample-rate/bit reduction not in DB but low research value for a "sound production method"), noise gate (adjacent to TSDE's sustain-cut behavior but a subset of it), aural exciter (14 "exciter" hits are all physical-model *exciter* = the excitation stage, not an aural-exciter DSP — but TSDE is the cleaner, more canonical gap-filler for the dynamics family next to SP-008).
4. **Primary sources** — network up (Wikipedia `Envelope_detector` / `Noise_gate` / `Dynamic_range_compression` all 200). DuckDuckGo HTML search returned a 302 redirect and the `python3 -c` parsing fallback was blocked by the shell guard, so the SPL patent/whitepaper was not fetched directly this run; the section was written from canonical knowledge of the SPL Transient Designer DET technique (stable, well-documented: fast/slow dual envelope followers + Attack/Sustain difference gains) plus the Blesser 1969 / Giannoulis–Massberg–Reiss 2012 envelope-follower theory.
5. **Summary row + detail section landed cleanly** — verified `^| **SP-073**` (single pipe, no `||` prefix; `grep -c '^\|\| \*\*SP-073'` = 0), zero `\\` double-backslash in the new row (`grep -c '\\\\'` = 0), detail header `# Transient Shaping via Differential Envelope Processing (TSDE) (Method SP-073)` present at line 17634. Both known patch pitfalls avoided.
6. **`_temp_sp073.md` workflow used as required** — `write_file` → `printf '\n' >> methods_db.md` + `cat _temp_sp073.md >> methods_db.md` → `rm` (heredoc/execute_code are blocked in cron). Leading newline separates the detail section from the prior SP-072 section.
7. **ONE-TREE symlink** — `write_file`/`patch`/`cat` resolved to `/opt/data/repos/musicom/projects/Research/CompositionMethods/...` (symlink target of `/opt/data/projects/Research/...`); identical resolution, no action needed.

## Appendix — complete section text appended

The full detailed section (### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration, ### Pitfalls) was appended to `methods_db.md` under "Sound Production Methods Framework" (detail header at line 17634) and is reproduced verbatim (with extended math + NumPy sketch + references) in the standalone file `sound_method_SP-073_tsde.md`.
