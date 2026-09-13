# Report — SP-072 Harmonic-Percussive Source Separation (HPSS)

- **Method name:** Harmonic-Percussive Source Separation (HPSS)
- **ID:** SP-072
- **Layer:** absolute (sound production — post-processing / DSP)
- **One-line description:** Splits a rendered audio buffer into two re-mixable stems via anisotropic median filtering (or IRLS) of the magnitude STFT: a time-axis median extracts the horizontal spectral ridges (harmonic/sustained), a frequency-axis median extracts the vertical ridges (percussive/transient), and a binary or soft mask splits the complex STFT with the original phase. No training, no pitch model; $O(N \log N)$ per frame. The non-parametric source-separation counterpart to SP-026 phase vocoder / SP-027 SMS / SP-031 cross-synthesis.
- **Next free SP ID:** SP-073

## Summary-table row (added at line 175, after SP-071 row, before the `---` separator)

`| **SP-072** | Harmonic-Percussive Source Separation (HPSS) | **Post-Processing / DSP** | Tonal/Transient Stem Split (Harmonic + Percussive Buffers) | Splits a rendered audio buffer into two re-mixable stems via anisotropic median filtering (or IRLS) of the magnitude STFT: a time-axis median extracts the horizontal spectral ridges (harmonic/sustained), a frequency-axis median extracts the vertical ridges (percussive/transient), and a binary or soft mask splits the complex STFT with the original phase. No training, no pitch model; $O(N \log N)$ per frame. The non-parametric source-separation counterpart to SP-026 phase vocoder / SP-027 SMS / SP-031 cross-synthesis. |`

## Line-count delta

- Before: 17447
- After (summary row + detail section): 17542
- Delta: +95

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-072_hpss.md`
- Report: `/opt/data/projects/Research/CompositionMethods/report_SP-072.md`
- DB: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row line 175, detail header line 17450)

## Candidate code path

`sound/effects/hpss.py` (new module, sibling to the existing spectral-domain processors `phase_vocoder.py`, `spectral_gate.py`, `lpc_synth.py`, `morph_filter.py`). Reuses the STFT/overlap-add machinery already in SP-026; the two median filters use `scipy.signal.medfilt` (or a sliding-window two-heap median for streaming).

## Technical mechanics summary

1. **STFT** — frame $x[n]$ (window $w$, hop $H$), magnitude $Y[k,m]=|X[k,m]|$.
2. **Anisotropic median filters** — time-axis median $\tilde Y_h$ (per bin, length $L_h$) captures harmonic horizontal ridges; frequency-axis median $\tilde Y_p$ (per frame, length $L_p$) captures percussive vertical ridges.
3. **Masks** — binary $M_h=\mathbb{1}[\tilde Y_h > \tilde Y_p]$ or soft $M_h=\tilde Y_h/(\tilde Y_h+\tilde Y_p)$.
4. **Resynthesis** — $x_h=\mathrm{iSTFT}(M_h \odot X)$, $x_p=\mathrm{iSTFT}(M_p \odot X)$, original phase reused; $x \approx x_h + x_p$.
5. **IRLS refinement** — differentiable objective with $\ell_1$ time/frequency-smoothness penalties, iteratively reweighted (Driedger–Müller–Disch 2014); drops filter-length tuning.
6. **Cascaded decomposition** — re-apply HPSS to the residual for intermediate layers (stem tree).
7. **Cost** — $O(N \log N)$ per frame + $O(K \cdot M)$ filters; deterministic (no RNG) → zero-drift gate trivially satisfied.

## Quirks / pitfalls hit during this run

1. **ID resolved dynamically, not assumed** — scanned the summary table (max `SP-071`), standalone files (`sound_method_SP-*.md` → max SP-071), and `report_SP-*.md` (max SP-071). The prior `report_SP-071.md` declares "Next free SP ID: SP-072". Cross-checked `grep -c SP-072` == 0 before starting. New ID = **SP-072**.
2. **No duplicate** — confirmed no existing HPSS / harmonic-percussive / median-filtering / source-separation method in the DB (only SP-027 SMS and SP-031 cross-synthesis, which are resynthesis methods, not stem splitters).
3. **Primary-source PDF 404** — `dafx.de` FitzGerald 2010 PDF and the FAU ISMIR tutorial PDF both returned 404 (network itself is up: google/wikipedia 200/301). Wrote the section from solid canonical knowledge of the FitzGerald (2010) + Driedger–Müller–Disch (2014) algorithms — the equations are textbook-stable. Flagged for the weekly registration job: no additional primary-source fetch was possible this run.
4. **Summary row + detail section landed cleanly** — verified `^| **SP-072**` (single pipe, no `||` prefix), zero `\\` double-backslash in the new row (`grep -c '\\\\'` = 0), detail header `# Harmonic-Percussive Source Separation (HPSS) (Method SP-072)` present at line 17450. Both known patch pitfalls avoided.
5. **`_temp_sp072.md` workflow used as required** — `write_file` → `cat >> methods_db.md` → `rm` (heredoc/execute_code are blocked in cron). Appended with a leading `printf '\n'` so the detail section is separated from the prior section's final reference line.
6. **ONE-TREE symlink** — `write_file`/`patch` resolved to `/opt/data/repos/musicom/projects/Research/CompositionMethods/...` (symlink target of `/opt/data/projects/Research/...`); identical resolution, no action needed.
7. **Typo caught + fixed in standalone** — `per-cussive` → `percussive` (detail table) and `nperseg=nff` → `nperseg=nfft` (code sketch) corrected via `patch` before finalize.

## Appendix — complete section text appended

The full detailed section (### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration, ### Pitfalls, ### Comparison With Related Methods, ### References) was appended to `methods_db.md` under "Sound Production Methods Framework" (detail header at line 17450) and is reproduced verbatim (with extended math + NumPy sketch) in the standalone file `sound_method_SP-072_hpss.md`.
