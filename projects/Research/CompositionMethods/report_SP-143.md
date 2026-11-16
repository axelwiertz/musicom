# Report SP-143 — Neural GAN Vocoder Synthesis (GANV)

**Date:** 2026-11-16 (cron). **Agent:** sound production research agent.

## Identity

- **Method ID:** SP-143 (dynamically resolved — see Resolve below)
- **Method name:** Neural GAN Vocoder Synthesis (GANV) — HiFi-GAN / Parallel WaveGAN / MelGAN family
- **Layer:** **absolute** (sound production — LAYER_ARCHITECTURE.md). Classification: **Synthesis Engines** (per the methods_db summary-table taxonomy; neural raw-waveform generator, sibling of SP-135/SP-060/SP-045).
- **One-line description:** Generates raw waveforms from a log-mel-spectrogram condition via a GAN-trained non-autoregressive convolutional generator — HiFi-GAN (transposed-conv + multi-receptive-field-fusion, LS-GAN + mel-L1 + feature-matching losses, multi-period/multi-scale discriminators) and Parallel WaveGAN (non-autoregressive WaveNet + multi-resolution STFT loss); parallel one-pass inference, 167.9× real-time (V100), deterministic per mel.
- **Candidate code path:** `sound/synthesis/gan_vocoder.py` (new module; inference wrapper over pretrained HiFi-GAN / Parallel WaveGAN checkpoints + mel front-end; dispatch from `workflows/musicom_workflow.py::produce(method="SP-143", ...)`).

## Resolve of the next SP number

- Highest existing SP-ID: **SP-142** (WSOLA Time-Stretch Synthesis) — confirmed by scanning the summary table rows `| **SP-NNN** |` (max SP-142 at line 357) AND the standalone files `sound_method_SP-*.md` (max = SP-142_WSOLA) AND `report_SP-*.md` (max = report_SP-142.md).
- Cross-check: `grep -n "SP-143"` on methods_db.md before entry = **0** hits.
- **New ID = SP-143.**

## Novelty audit (grep on methods_db.md before entry)

| pattern | hits | meaning |
|---|---|---|
| `hifi` / `HiFi` | 1 | SP-060 pitfall: "invert with a neural vocoder (HiFi-GAN/MelGAN)" — suggestion only, no method |
| `wavegan` / `WaveGAN` | **0** | family absent |
| `melgan` / `MelGAN` | 2 | both inside SP-060's DDAS entry (mentions only) |
| `melspec` | **0** | — |
| `GAN` | 222 | all symbolic MuseGAN (method 057, piano-roll domain); 0 raw-waveform |
| `adversarial` | 18 | all in 057 / SP-060 context; no GAN-vocoder method |

Neural synthesis already in DB: SP-135 (WaveNet autoregressive), SP-060 (DDAS diffusion), SP-045 (DDSP deterministic DSP prior). **No SP method documents the adversarial non-autoregressive vocoder family → SP-143 is novel** (the missing fourth neural family).

## Summary-table row appended (exact text, line 358)

```
| **SP-143** | Neural GAN Vocoder Synthesis (GANV) | **Synthesis Engines** | Neural Adversarial / Mel-to-Waveform Raw-Audio Timbres | Generates raw waveforms from a log-mel-spectrogram condition via a GAN-trained non-autoregressive generator: HiFi-GAN transposed-conv + multi-receptive-field-fusion (MRF) generator (V1 ≈ 13.9 M params) trained with LS-GAN adversarial + mel-L1 (λ=45) + feature-matching (λ=2) losses against multi-period (p∈{2,3,5,7,11}) and multi-scale discriminators; Parallel WaveGAN variant wraps a non-autoregressive WaveNet (1.44 M params) with a 3-resolution STFT loss (spectral convergence + log-magnitude L1, λs=4). Parallel one-pass inference — 167.9× real-time (V100, 22.05 kHz), 13.4× real-time CPU (V2), deterministic per mel. The missing adversarial member of the neural family (vs SP-135 autoregressive, SP-060 diffusion, SP-045 DSP). Candidate: `sound/synthesis/gan_vocoder.py`. |
```

## Line counts

- methods_db.md **before** append: **31 665** lines (measured `wc -l` immediately before `cat >>`)
- methods_db.md **after** append + table-row patch: **31 747** lines → my delta **+82** (detailed section +81: 31665 → 31746, then table row +1: 31746 → 31747)
- **Concurrent cron hazard (observed):** while this job ran, a second cron job appended a Langford/Skolem "LSPC" abstract-layer method — 1 summary-table row + a 92-line section — shifting my row to line 359 and my section to lines 31668–31748 (SP-142's section header moved 31584 → 31586). Final file count: **31 840** lines. My content is byte-intact (verified post-shift: row 359 single-pipe, section 31668–31748 with all 7 subsections, 81 lines).

## Files written

| file | role |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | summary-table row (line 359 after concurrent-shift; appended at 358) + detailed section (lines 31668–31748, 81 lines) |
| `/opt/data/projects/Research/CompositionMethods/sound_method_SP-143_GANV.md` | standalone full write-up (extended math, PyTorch implementation sketch, references) |
| `/opt/data/projects/Research/CompositionMethods/report_SP-143.md` | this report (primary record) |
| `/opt/data/_web143_ganv/*` | web research cache: hifigan_abs.html, pwg_abs.html, hifigan_readme.md, hifigan_models.py, pwg_readme.md, pwg_stft_loss.py, pwg_model.py |

## Research sources (fetched live 2026-11-16)

1. **arXiv abs/2010.05646** — HiFi-GAN paper (Kong, Kim, Bae, NeurIPS 2020): abstract fetched, MOS 4.36 vs 4.49 natural, 167.9× real-time V100 @ 22.05 kHz, V2 13.4× real-time CPU.
2. **arXiv abs/1910.11480** — Parallel WaveGAN paper (Yamamoto, Song, Kim, ICASSP 2020): abstract fetched, 1.44 M params, 24 kHz, 28.68× real-time GPU, MOS 4.16.
3. **jik876/hifi-gan** (GitHub, MIT) — `models.py` fetched raw (Generator/ResBlock1/ResBlock2/MRF, DiscriminatorP/MPD, DiscriminatorS/MSD, feature_loss, LS losses) + README (config v1/v2/v3, pretrained checkpoints, fine-tuning, inference_e2e).
4. **kan-bayashi/ParallelWaveGAN** (GitHub, MIT) — `stft_loss.py` fetched raw (SpectralConvergenceLoss, LogSTFTMagnitudeLoss, MultiResolutionSTFTLoss: fft [1024,2048,512], hop [120,240,50], win [600,1200,240], 1e-7 magnitude clamp) + README + `parallel_wavegan.py`.
5. Context references (no live fetch needed): MelGAN (NeurIPS 2019), Multi-band MelGAN (arXiv:2005.05106), WaveNet (SP-135), LS-GAN (Mao et al. 2017), Goodfellow 2014.
6. Search engines remain bot-blocked — direct source fetches used (same pattern as SP-142).

## Technical mechanics summary

- **Mel front-end:** $M = \log(\max(H\,|\mathrm{STFT}(x)|, \varepsilon))$, 80 mel bins, FFT 1024 / hop 256 / win 1024, fmin 0 / fmax 8000 @ 22.05 kHz; frame ≈ 11.61 ms; output length = frames × 256.
- **HiFi-GAN generator (V1):** Conv1d(80→512, k7) → 4 × [LReLU(0.1) + ConvTranspose1d rates [8,8,2,2] kernels [16,16,4,4] 512→…→32] → per-stage MRF (sum of 3 ResBlock1 branches, kernels [3,7,11], dilations (1,3,5), averaged) → Conv1d(32→1, k7) → tanh. Total upsample 256 = hop ratio. Params ≈ 13.9 M (V1) / 0.93 M (V2) / 4.2 M (V3).
- **Losses:** LS-GAN $L_D = \mathbb{E}[(D(y)-1)^2] + \mathbb{E}[D(G(x))^2]$, $L_G^{adv} = \mathbb{E}[(D(G(x))-1)^2]$; mel-L1 λ=45; feature matching λ=2.
- **Discriminators:** MPD — waveform reshaped to 2-D period images $p \in \{2,3,5,7,11\}$, 2-D conv stack (k5×1, stride 3); MSD — 3 × 1-D conv stacks at scales raw, ×1/2, ×1/4 (AvgPool1d(4,2)).
- **Parallel WaveGAN:** non-autoregressive WaveNet (3×10 dilated causal convs, residual/skip 64, cond 4) + $L_s$ = spectral convergence + log-magnitude L1 averaged over 3 STFT resolutions, λ_s = 4.0.
- **Complexity:** one parallel forward $O(T)$; no autoregressive loop, no diffusion steps; deterministic per mel input.

## Verification (post-append)

- `wc -l methods_db.md` = **31 747** (before 31 665 → delta +82).
- `grep -n "SP-143"` → summary-table row at line 358 AND detailed section header `# Sound Production Method SP-143 — Neural GAN Vocoder Synthesis (GANV)` at line 31666 (81-line section).
- Patched row re-read: single leading `|` (no `||` corruption), no LaTeX double-escape in the new row (unicode λ used deliberately — zero backslashes in the row, pitfall dodged).

## Quirks / pitfalls hit

1. **Patch tool double-escape avoidance:** the SP-143 table row was written with **zero LaTeX backslashes** (unicode λ, plain ∈) so the known `\\` double-escape pitfall cannot trigger; re-read confirmed clean.
2. **`||` prefix check:** re-read of line 358 shows content `| **SP-143** | …` — single pipe; the `||` seen in raw output is the line-number separator of the reader, not file content.
3. **File-tail newline:** verified methods_db.md ends with `\n` (od -c) before `cat >>` so the appended header did not weld onto the last line.
4. **Concurrent-cron hazard:** the DB grew between first read (31 582 in SP-142's report era) and this run (31 665 at append time) — SP-143 was verified free at append time by grep.
5. **Novelty trap:** `GAN` grep = 222 hits but all symbolic (057 MuseGAN); the raw-waveform adversarial family was genuinely absent (wavegan=0, melgan=2 mentions, hifi=1 mention). SP-143 fills the fourth neural family slot.

## Next free SP ID

**SP-144** (SP-143 is now the highest in both the summary table and the standalone/report files).
