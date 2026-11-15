# Sound Production Method SP-142 — WSOLA Time-Stretch Synthesis (Waveform-Similarity Overlap-Add)

> Layer: **absolute** (sound production — LAYER_ARCHITECTURE.md). Candidate code path: `sound/effects/wsola.py` (upgrade the WSOLA-lite `_stretch` of `sound/generators/multimode_sample_player.py`).
> Verified prototype: `_web142_wsola/verify_sp142.py` — **18/18 checks pass**; log `verify_sp142_output.txt`, demos `sp142_stretch_half.wav` (639 872 frames/ch, 2 559 532 B) and `sp142_stretch_15x.wav` (213 291 frames/ch, 853 208 B).

### Source

- **Verhelst, W. & Roelands, M. (1993). "An overlap-add technique based on waveform similarity (WSOLA) for high quality time-scale modification of speech."** *Proc. IEEE ICASSP-93*, vol. 2, pp. 554–557 — the original paper. WSOLA's defining idea: instead of estimating the signal period (SOLA's pitch-detection step, Rabiner & Schafer 1978), align each analysis window to maximize waveform similarity with the *natural progression* of the previous window, within a bounded tolerance.
- **Driedger, J. & Müller, M. (2016). "A Review of Time-Scale Modification of Music Signals."** *Applied Sciences* 6(2), 57 — open-access survey; the recommended reference of the audiotsm project. Establishes the OLA/WSOLA/phase-vocoder taxonomy, the stretching-factor conventions, and the hybrid HPSS+WSOLA extension for extreme stretch.
- **Driedger, J. (2014). `wsolaTSM.m` (TSM Toolbox v2.03, MIT).** International Audio Laboratories Erlangen. Fetched 2026-11-15 from `https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/wsolaTSM.m`. The canonical MATLAB implementation this spec follows: `synHop=512`, `win=win(1024,2)` (Hann), `tolerance=512`, cross-correlation via convolution of the reversed candidate with the natural progression, WOLA normalization by the accumulated window sum, per-channel δ, and a general anchor-point time-stretch function (`s` = n×2 matrix mapping input positions to output positions; constant α is the two-anchor special case).
- **Muges (2021). `audiotsm` v0.1.2 (MIT).** Python reference; source fetched 2026-11-15: `audiotsm/wsola.py` (`WSOLAConverter` — `np.correlate(analysis_frame[:-syn_hop], natural_progression)` argmax → δ; hanning synthesis window, rectangular analysis window), `audiotsm/base/analysis_synthesis.py` (analysis hop = ⌊synthesis hop × speed⌋; WOLA normalize buffer; output started at the window peak via half-frame input zero-pad + `_skip_output_samples`).
- **Wikipedia: "Audio time stretching and pitch scaling"** (rev. 2026) — SOLA / time-domain harmonic scaling background: autocorrelation period detection and period-to-period crossfade (Rabiner & Schafer 1978); the Adobe Audition "centre period closest to a user-specified centre" heuristic that prefigures WSOLA's bounded search; note that SOLA fails when autocorrelation mis-estimates the period on polyphonic material — WSOLA's local-similarity search is the fix.
- **SoundTouch (Parviainen, O., 2001–2024)** — production WSOLA-family open-source library (tempo/pitch/rate, real-time at ~100 ms latency, used by hundreds of commercial apps); industrial validation of the family.
- **Repo antecedent:** `sound/generators/multimode_sample_player.py::_stretch(x, factor, grain=1024, search=128)` (Elektron Model-TG-style "stretch" mode): WSOLA-lite — hanning-grain overlap-add, `a_hop = grain//2`, `s_hop = round(a_hop·factor)` (so `factor` = output/input duration = 1/α), coarse ±`search` sweep in 8-sample strides, dot-product similarity against the previous segment's tail, WOLA division by accumulated window. Its limitations (documented here): stride-8 search misses the true correlation peak; no ±tol full sweep; no shared-delta stereo; no anchor-point time-stretch function. SP-142 is the full-spec method and the upgrade path.
- **Novelty check (2026-11-15):** `grep -ci` on `methods_db.md` **before** entry: `wsola` = **0**, `waveform similarity` = **0**, `verhelst` = **0**, `natural progression` = **0**; standalone `SOLA` = 1 (Hejna & Musicus SOLA-FS 1991, cited inside SP-037 as "related method"); the other 75 SOLA hits are `PSOLA` (SP-037). Time-stretch families already present: **SP-026** (phase vocoder), **SP-037** (PSOLA), **SP-054** (waveset), **SP-016** (granular), **SP-108** (MQSAS), **SP-069** (WPSS). **No SP method documents the waveform-similarity overlap-add family** — WSOLA is the missing third classic TSM family (time-domain, FFT-free, transient-preserving).
- **Verified prototype for this document:** `_web142_wsola/verify_sp142.py` — 18/18 checks; all quoted numbers measured.

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). WSOLA is a post-processing / DSP time-remap stage: it consumes *rendered audio buffers* (output of any Synthesis Engines row — SP-001 FluidSynth, SP-011 Karplus-Strong, SP-098 AKDS, SP-136 SLTM, SP-141 SOSS, …), applies a time-stretch function, emits audio buffers of a different length. No timing authority beyond the buffer, no events emitted, no composition decisions. Stage position: after the voice source, before the mix — per-row stretch → filters/EQ (SP-007/SP-029) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Candidate code path: `sound/effects/wsola.py` — new module (the repo's only WSOLA today is the WSOLA-lite inside `sound/generators/multimode_sample_player.py`); dispatch from `workflows/musicom_workflow.py::produce(method="SP-142", ...)`.

### Description

WSOLA (Waveform-Similarity Overlap-Add) changes the *duration* of an audio buffer without changing its pitch, by cutting the signal into overlapping frames and re-spacing them — with one crucial upgrade over plain OLA: each analysis window is allowed to drift by a bounded offset $\delta \in [-\mathrm{tol}, +\mathrm{tol}]$ so that its overlap region is **waveform-continuous** with the previously copied window. The drift is the argmax of the cross-correlation between the candidate segment and the *natural progression* — the segment that would follow the previous window at natural speed. Overlapping segments that already look alike produce no phase cancellation, no beating, no spectral-envelope shift: the output is locally the same waveform laid out on a longer (or shorter) time axis. No FFT, no phase unwrapping, no f0 estimation. This makes WSOLA the most robust classic OLA-family method on polyphonic/percussive material and the best at transient preservation (verified: impulse peak 3.53 vs OLA 3.49 vs original 3.89 at α=0.5, check 5). The speed factor $\alpha = H_a/H_s$ (α<1 slows, α>1 speeds) makes the output length exact to the sample (verified: 319 936 → 639 872 @ α=0.5 and → 213 291 @ α=1.5, check 10). SoundTouch, the Driedger TSM toolbox, and audiotsm ship WSOLA-family engines; this DB's other TSM families are SP-026 (spectral) and SP-037 (pitch-synchronous).

### Technical Mechanics

**1. Frame scheduling.** Analysis frames of length $N_w$, analysis hop $H_a$; synthesis hop $H_s$ (default $N_w/2$, 50 % overlap):

$$H_a = \lfloor H_s \cdot \alpha \rfloor, \qquad m = \left\lfloor n \cdot H_s/H_a \right\rfloor$$

The hop ratio *is* the speed factor; the output length follows from the hops, not from a resampler. Verified: $|m - n/\alpha| \le H_s + 1$ for α ∈ {0.5, 0.75, 1.5, 2.0} (check 1); ≤ 1 sample on the fluidsynth render (check 10).

**2. OLA skeleton with WOLA normalization.** Every synthesis frame is windowed and overlap-added; the output is divided by the accumulated window sum so overlap never modulates amplitude:

$$y[k H_s + j] \mathrel{+}= w[j]\cdot x[k H_a + \delta_k + j], \qquad o[k H_s + j] \mathrel{+}= w[j], \qquad y \leftarrow y/\max(o, \varepsilon), \quad \varepsilon \approx 10^{-3}$$

With $w$ a Hann window of length $N_w$, $w[j] + w[j + N_w/2] = 1$ → the interior reconstruction is *exact*: verified max |x−y| = 4.44e-16 (machine epsilon) at α=1.0, tol=0 over the interior (check 8).

**3. The WSOLA core.** After copying the $k$-th window (position $k H_a + \delta_k$), the natural progression is the segment one synthesis hop ahead:

$$\mathrm{nat}_k[j] = x\big[(k H_a + \delta_k) + H_s + j\big], \qquad j = 0 \dots N_w-1$$

and the next offset maximizes similarity within the tolerance window:

$$\delta_{k+1} = \arg\max_{\delta \in [-\mathrm{tol}, +\mathrm{tol}]}\; \sum_{j=0}^{N_w-1} x\big[(k{+}1) H_a + \delta + j\big]\cdot \mathrm{nat}_k[j]$$

Implementation: one `np.correlate(region, nat, mode='valid')` per frame, where `region = x[(k+1)H_a - tol : (k+1)H_a + N_w + tol]` spans $2\,\mathrm{tol}+1$ lags; the argmax index maps to δ via `first_lag = region_start - (k+1)H_a`. Verified: max |δ| = 506 ≤ tol = 512 with a genuine interior argmax (check 4).

**4. Output alignment (WOLA start).** Analysis positions live inside a zero-padded buffer offset by $N_w/2 + \mathrm{tol}$; the first frame is written at output sample 0, so the output begins at the Hann *peak* — the standard trick (audiotsm `_skip_output_samples`; Driedger trims `winLenHalf`). **This is the classic silent bug** (Pitfall 1): dropping the pad-front offset delays the entire output by $N_w/2$ while every spectral check still passes. The α=1.0 interior-exactness check is the detector.

**5. Stereo strategy.** Reference implementations compute δ per channel (Driedger, audiotsm). Production practice shares one δ trajectory across channels. Measured (two-tone stereo pair, α=0.5): inter-channel correlation +0.800 → **+0.808 shared-δ** (image preserved) vs **+0.648 per-channel** (decorrelated) (check 9). Shared δ is the default; per-channel trades stereo image for marginally better per-channel waveform continuity.

**6. Anchor-point time-stretch function.** Generalize constant α to a mapping of input↔output positions (Driedger `wsolaTSM.m`): analysis positions `anaPos_k = round(interp1(anchor_out, anchor_in, synPos_k))`; local hop $H_{a,k} = \mathrm{anaPos}_{k+1} - \mathrm{anaPos}_k$; the natural-progression step and δ search are unchanged, using the *local* hop. This is the UnitMatrix seam-safe mode: fit a 2-bar cell into 3 bars with a smooth local-α curve instead of a global ratio.

**7. Complexity & determinism.** Naive δ search: $O(N \cdot (2\,\mathrm{tol}+1) \cdot N_w)$; single `np.correlate` per frame: $O(N \cdot (N_w + 2\,\mathrm{tol}))$; FFT-based correlation: $O(N \log N)$. Prototype (pure NumPy, 44.1 kHz): both full passes (α=0.5 and α=1.5 over 319 936 samples) in ~1.3 s total. Deterministic: bit-identical re-run (check 7).

### Musical Elements Framework

- **PITCH**: untouched by construction — no resampling, no spectral-envelope shift, no formant artifacts (contrast SP-026, which moves pitch with time; SP-037, which needs f0). Verified: dominant partial 440.00 → 440.00 Hz (+0.00 %), harmonic ratios 1 : 2.000 : 3.000 at α=0.5 (checks 2, 3). Pitch is not a WSOLA parameter; time is.
- **RHYTHM**: α is the duration multiplier — onsets, note lengths, groove scale by 1/α. Transients are the crown jewel: impulse peak 3.53 (WSOLA) vs 3.49 (OLA) vs 3.89 (original) at α=0.5 (check 5) — drums/plucks keep their punch where the phase vocoder smears them. Per-section α creates rubato (anchor points pull/push local tempo, pitch unchanged).
- **HARMONY**: none generated, none destroyed — chords, detuned stacks (SP-141), dense mixes pass through with ratios intact (check 3). Inter-voice duration harmony (voices ending together) is preserved when rows share α per section; differing per-row α deliberately desynchronizes.
- **STRUCTURE**: per-section α is the column parameter (`alpha` per column + anchor points at seams): (a) fit a rendered voice exactly into a section length (α = section_len/cell_len — the UnitMatrix seam-safe remap), (b) build-up/drop pacing (α ramp 1.0 → 0.6), (c) phrase rubato via anchor points. Sample-count-exact per section → the zero-drift invariant survives the remap.
- **TEXTURE**: α < 0.7 (stretch > 1.4×) starts to expose graininess on sustained tonal material; tol = alignment aggressiveness (large tol → better transient lock + slight local timing wander; tol = 0 → OLA beating on periodic content). Family: OLA (beating; percussive-only) → WSOLA small tol (clean, phase-stable) → WSOLA large tol (transient-locked, micro-rhythm wander). Stereo width preserved only under shared δ.

### UnitMatrix Integration

**Voices = rows = WSOLA instances.** Row $v$'s rendered buffer (from any Synthesis Engines source per row: SP-001/SP-011/SP-098/SP-136/SP-141) passes through the row's instance: `stretched = wsola_stretch(row_buffer, alpha, syn_hop, win_len, tolerance, shared_delta=True)`. Row params `{alpha, syn_hop, win_len, tolerance, shared_delta, anchor_points}`. Example rows: "stretched pad" (α 0.67, tol 512), "transient-safe drums" (α 0.5, tol 768), "tight lead" (α 1.15, tol 256), "rubato melody" (anchor points).

**Sections = columns = per-section α.** Column $j$ holds `{alpha, tol, anchor_points}` — a column change is a *pacing* change (build-up α 1.0 → 0.6, drop α 1.0 → 1.3). Seam safety: per-section constant α + anchor points pinned at section boundaries reproduces section lengths exactly; crossfade stretched cells at seams so α discontinuities don't click.

**Cells = MusicUnit.** Cell (v, j): the cell's rendered audio buffer is stretched to the section's target length; `MusicEvent` tick bounds are untouched (WSOLA operates post-event, on audio) — the events were already zero-drift; only the audio is remapped.

**Produce dispatch:** `produce(midi_path, method="SP-142", source="SP-001", params={"rows": {"pad": {"alpha": 0.67, "tolerance": 512}, "drums": {"alpha": 0.5, "tolerance": 768}}, "columns": {"A": {"alpha": 1.0}, "B": {"alpha": 0.6}}, "fs": 44100})`. Stage order: **source (any SP) → SP-142 WSOLA (time remap) → per-row filter (SP-029/SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**. WSOLA changes sample counts — run it before sample-count-sensitive stages (delay-line sync, SP-050 GCD grids) or re-quantize to the tick grid.

### Pitfalls

1. **The window-ramp offset bug (bit the prototype).** Analysis positions must be measured inside the zero-padded buffer (offset $N_w/2 + \mathrm{tol}$); forgetting it shifts the *entire* output by $N_w/2$ samples while every spectral check still passes (pitch, harmonics, RMS are shift-invariant). The only reliable detector is the α=1.0, tol=0 interior exactness check (4.44e-16). Ship it.
2. **Per-channel δ decorrelates stereo.** Measured +0.800 → +0.648 (α=0.5) per-channel vs +0.808 preserved shared-δ (check 9). The reference implementations are per-channel — do not copy them blindly for stereo buses. Mid/side processing is the alternative.
3. **Tolerance discipline.** tol = 0 → OLA (beating on periodic content); tol too large → δ wander = local timing jitter on strongly periodic material; δ saturating at ±tol every frame means the window is too small (measured 506/512 healthy after the fix; 512/512 saturated before). Start tol = H_s (512 @ 44.1 kHz); raise for transient lock, lower for metronomic material.
4. **Extreme α.** Beyond α < 0.5 or α > 2.0 frame repetition/dropping artifacts appear (the whole OLA family's limit). Driedger–Müller hybrid (HPSS via SP-072 + WSOLA) is the standard fix; SP-026/SP-108 are the spectral alternatives.
5. **WOLA clamp vs silence.** `y/max(o, 1e-3)` turns true silence into shaped near-silence — fine, but don't lower ε to "recover gain" (numerical floor amplification). Fade edges instead (start mid-window, let the tail drop).
6. **Constant α ≠ section fit.** A global ratio leaves up to ±H_s samples of error — inaudible in loops, audible at seams. Pin anchor points at section boundaries and crossfade.
7. **Naming collision with the other OLA families.** WSOLA ≠ PSOLA (SP-037: pitch-synchronous, f0-marked), ≠ phase vocoder (SP-026: STFT), ≠ granular (SP-016). "SOLA" grep catches all (76 hits, 75 = PSOLA) — write the family explicitly.
8. **Neighbour audit.** SP-026 (spectral, transient blur); SP-037 (time-domain, needs pitch marks; its other half is formant-preserving pitch shift); SP-054 (zero-crossing granular *reordering*, distortion-flavoured); SP-016 (scatter/freeze, not linear remap); SP-108 (sinusoidal tracks, partial-level editing); SP-069 (wavelet time-scale relabel). WSOLA = waveform-similarity time-domain OLA: FFT-free, f0-free, transient-preserving, exact-length, O(N log N) — the missing third family. Repo: `sound/effects/wsola.py` (new; upgrade `multimode_sample_player._stretch` per this spec: full ±tol correlate sweep, WOLA normalize buffer, shared-delta stereo, anchor-point time-stretch function).

### Implementation Sketch (Python/NumPy)

Canonical WSOLA, single channel shown (multi-channel: shared δ default). Deterministic, ~70 lines:

```python
import numpy as np

def hann(L):
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(L) / L)

def wsola_stretch(x, alpha, syn_hop=512, win_len=1024, tolerance=512):
    """alpha<1 slows down.  Returns stretched mono array + per-frame deltas."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    H_s = int(syn_hop)
    H_a = max(1, int(round(H_s * alpha)))        # analysis hop = hop ratio
    tol = int(tolerance)
    m = int(round(n * H_s / H_a))                # exact output length
    w = hann(win_len)
    half = win_len // 2
    pad_front = half + tol                       # WOLA-start offset (Pitfall 1)
    xp = np.zeros(n + pad_front + win_len + tol + H_s)
    xp[pad_front:pad_front + n] = x
    y = np.zeros(m + 2 * win_len)
    ow = np.zeros_like(y)
    ana = pad_front                              # analysis pos in padded buffer
    syn = 0
    d_cur = 0
    deltas = []
    while syn + win_len <= m:
        seg = xp[ana + d_cur:ana + d_cur + win_len]
        y[syn:syn + win_len] += seg * w          # windowed OLA
        ow[syn:syn + win_len] += w
        nxt = ana + H_a
        nat = xp[ana + d_cur + H_s:ana + d_cur + H_s + win_len]   # natural prog
        d_next = 0
        if nxt + win_len + tol < xp.size:
            lo = max(0, nxt - tol)
            hi = min(xp.size, nxt + win_len + tol)
            cc = np.correlate(xp[lo:hi], nat, mode='valid')  # 2tol+1 lags
            d_next = int(np.argmax(cc)) + (lo - nxt)         # argmax -> delta
            d_next = max(-tol, min(tol, d_next))
        deltas.append(d_next)
        ana, syn, d_cur = nxt, syn + H_s, d_next
    y = y[:m] / np.maximum(ow[:m], 1e-3)         # WOLA normalize (Pitfall 5)
    return y, np.array(deltas)
```

Verified numbers (all from `verify_sp142.py`, 18/18): output length exact $|m - n/\alpha| \le 1$; pitch 440.00 → 440.00 Hz; ratios 1:2.000:3.000; max |δ| 506 ≤ 512; α=1.0 interior max err 4.44e-16; transient peak 3.53 (WSOLA) vs 3.49 (OLA) vs 3.89 (orig); RMS drift 0.34 %; stereo corr +0.800 → +0.808 (shared-δ) vs +0.648 (per-channel); fluidsynth pipeline 319 936 → 639 872 (α=0.5) / 213 291 (α=1.5) samples.

### References

1. Verhelst, W. & Roelands, M. (1993). "An overlap-add technique based on waveform similarity (WSOLA) for high quality time-scale modification of speech." *Proc. IEEE ICASSP-93*, vol. 2, pp. 554–557.
2. Driedger, J. & Müller, M. (2016). "A Review of Time-Scale Modification of Music Signals." *Applied Sciences* 6(2), 57. https://www.mdpi.com/2076-3417/6/2/57
3. Driedger, J. (2014). `wsolaTSM.m`, TSM Toolbox v2.03 (MIT), International Audio Laboratories Erlangen — fetched 2026-11-15 from `https://www.audiolabs-erlangen.de/content/resources/MIR/TSMtoolbox/wsolaTSM.m`; toolbox page `.../TSMtoolbox/` (cached in `_web142_wsola/tsmbox.html`).
4. Muges (2021). `audiotsm` v0.1.2 (MIT) — `wsola.py`, `ola.py`, `base/analysis_synthesis.py`, `utils/windows.py` fetched 2026-11-15 from GitHub `Muges/audiotsm` (cached in `_web142_wsola/`).
5. Wikipedia, "Audio time stretching and pitch scaling" (rev. 2026) — cached `_web142_wsola/wiki_timestretch.html`.
6. Parviainen, O. (2001–2024). SoundTouch audio processing library — `https://www.surina.net/soundtouch/` (cached `_web142_wsola/soundtouch.html`).
7. Repo: `sound/generators/multimode_sample_player.py::_stretch()` — WSOLA-lite antecedent (SP-116 registry entry); upgrade target per this spec.
8. Prototype: `_web142_wsola/verify_sp142.py` (18/18), log `verify_sp142_output.txt`, demos `sp142_stretch_half.wav`, `sp142_stretch_15x.wav`.
