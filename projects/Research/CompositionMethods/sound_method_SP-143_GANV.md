# Sound Production Method SP-143 — Neural GAN Vocoder Synthesis (GANV)

> Layer: **absolute** (sound production — LAYER_ARCHITECTURE.md). Candidate code path: `sound/synthesis/gan_vocoder.py` (inference wrapper over pretrained HiFi-GAN / Parallel WaveGAN checkpoints + mel front-end).
> Sources fetched live 2026-11-16: arXiv abs/2010.05646 (HiFi-GAN), abs/1910.11480 (Parallel WaveGAN), `jik876/hifi-gan` `models.py` + `config_v1.json`, `kan-bayashi/ParallelWaveGAN` `stft_loss.py` — cached in `/opt/data/_web143_ganv/`.

### Source

- **Kong, J., Kim, J., & Bae, J. (2020). "HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis."** *NeurIPS 2020*. arXiv:2010.05646 — canonical GAN vocoder: mel-conditioned raw-waveform generator (transposed convs + multi-receptive-field fusion MRF residual blocks) trained adversarially against multi-period (MPD) + multi-scale (MSD) discriminators with mel-L1 + feature-matching losses. MOS 4.36 (V1) vs 4.49 natural; 167.9× real-time on V100 @ 22.05 kHz; V2 13.4× real-time on CPU.
- **Yamamoto, R., Song, E., & Kim, J.-M. (2020). "Parallel WaveGAN: A Fast Waveform Generation Model Based on Generative Adversarial Networks with Multi-Resolution Spectrogram."** *ICASSP 2020*. arXiv:1910.11480 — non-autoregressive WaveNet generator (1.44 M params, 24 kHz, 28.68× real-time GPU) trained with multi-resolution STFT loss + LS-GAN, no distillation.
- **Kumar, K., et al. (2019). "MelGAN: Generative Adversarial Networks for Conditional Waveform Synthesis."** *NeurIPS 2019*. arXiv:1910.06711 — family ancestor (transposed-conv + dilation residual stacks, multi-scale waveform discriminators, feature matching).
- **Yang, G., et al. (2021). "Multi-band MelGAN: Faster Waveform Generation for High-Quality Text-to-Speech."** arXiv:2005.05106 — 4 parallel sub-band generators, 48 kHz.
- **Reference code (MIT):** `jik876/hifi-gan` (`models.py`, config_v1: 22.05 kHz / 80 mel / FFT 1024 / hop 256 / win 1024 / fmin 0 / fmax 8000 / upsample_rates [8,8,2,2] / kernels [16,16,4,4] / init_ch 512 / resblock kernels [3,7,11] / dilations [[1,3,5]×3]); `kan-bayashi/ParallelWaveGAN` (`stft_loss.py`: MultiResolutionSTFTLoss fft [1024,2048,512], hop [120,240,50], win [600,1200,240]; `parallel_wavegan.py`).
- **Novelty check (2026-11-16, before entry):** `hifi`=1, `wavegan`=0, `melgan`=2 (SP-060 mentions only), `melspec`=0; all 222 `GAN` hits are the symbolic MuseGAN method 057. Neural family present: SP-135 autoregressive WaveNet, SP-060 diffusion, SP-045 DDSP. **GAN vocoder family undocumented → SP-143 novel.**

### Layer

**absolute** (sound production). **Synthesis Engines** — neural raw-waveform generator. Consumes log-mel-spectrogram condition (80 bins × hop grid) → emits waveform. Source-stage (acoustic model → mel → waveform) or neural-resynthesis stage (rendered audio → mel → waveform). No events emitted, no composition decisions; waveform length = mel frames × hop. Stage order: source → **SP-143 GANV** → per-row filter (SP-007/SP-029) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122).

### Description

GAN vocoders generate the entire raw waveform in one parallel forward pass of a convolutional generator $G$ conditioned on a mel-spectrogram, trained adversarially against discriminators $D$. Non-autoregressive (contrast SP-135 WaveNet: one sample at a time), non-iterative (contrast SP-060 diffusion: $T$ denoise steps), no explicit DSP prior (contrast SP-045 DDSP). HiFi-GAN's insight: audio is periodic at many simultaneous periods → multi-period discriminator (reshape waveform into period-2D images, $p \in \{2,3,5,7,11\}$) + multi-scale discriminator + multi-receptive-field generator fusion. Loss = LS-GAN adversarial + mel-L1 (λ=45) + feature matching (λ=2). Parallel WaveGAN: non-autoregressive WaveNet generator with multi-resolution STFT loss (spectral convergence + log-magnitude L1, 3 resolutions, λs=4). Speed: HiFi-GAN V1 167.9× real-time (V100, 22.05 kHz); V2 13.4× real-time CPU; PWG 28.7× real-time GPU, 1.44 M params. MOS 4.36 (V1) / 4.16 (PWG in TTS) — near-natural. Deterministic per mel input.

### Technical Mechanics

**1. Mel front-end.**

$$M = \log\bigl(\max(H\,\lvert\mathrm{STFT}(x)\rvert,\ \varepsilon)\bigr), \qquad \mathrm{STFT}\colon\ \mathrm{FFT}\ 1024,\ \mathrm{hop}\ 256,\ \mathrm{win}\ 1024$$

$H$ = 80×513 mel filterbank (22.05 kHz, fmin 0, fmax 8000). Frame ≈ 11.61 ms; output length = frames × 256 samples.

**2. HiFi-GAN generator (V1).** mel (B,80,$T_f$) → Conv1d(80→512, k7, p3) → 4 × [LReLU(0.1), ConvTranspose1d rate/kernel [8,8,2,2]/[16,16,4,4], channels 512→256→128→64→32] → after each upsample, MRF: $x \leftarrow \tfrac{1}{K}\sum_{k=1}^{K}\mathrm{ResBlock}_k(x)$ with ResBlock1 = two Conv1d(k3) per dilation $d \in \{1,3,5\}$, skip-add; kernels [3,7,11] → LReLU → Conv1d(32→1, k7, p3) → tanh. Upsample total 256 = hop ratio. Params: V1 ≈ 13.9 M, V2 ≈ 0.93 M, V3 ≈ 4.2 M.

**3. Losses.**

$$\mathcal{L}_D = \mathbb{E}_y[(D(y)-1)^2] + \mathbb{E}_x[D(G(x))^2], \qquad \mathcal{L}_G^{\mathrm{adv}} = \mathbb{E}_x[(D(G(x))-1)^2]$$

$$\mathcal{L}_{\mathrm{mel}} = \lVert M(y) - M(G(x)) \rVert_1, \qquad \mathcal{L}_{\mathrm{fm}} = \sum_i \tfrac{1}{N_i}\lVert D^i(y) - D^i(G(x)) \rVert_1$$

$$\mathcal{L}_G = \mathcal{L}_G^{\mathrm{adv}} + 2\,\mathcal{L}_{\mathrm{fm}} + 45\,\mathcal{L}_{\mathrm{mel}}$$

**4. Discriminators.** MPD: waveform (1,$T$) → reshape (1, $T/p$, $p$), reflect-pad if $T \bmod p \neq 0$; 2-D conv stack (k5×1, stride 3, ch 32→128→512→1024→1024→1), LReLU. MSD: 3 × 1-D conv stacks (k41 group convs, spectral norm first) at scales raw, ×1/2, ×1/4 (AvgPool1d(4,2)).

**5. Parallel WaveGAN.** Generator = non-autoregressive WaveNet: 3 blocks × 10 dilated causal convs (dilations 1..512), residual/skip 64, cond 4 channels from 80-mel via 1×1 conv + transposed-conv upsample. Loss: $\mathcal{L}_G = \mathcal{L}_G^{\mathrm{adv}} + 4.0\,\mathcal{L}_s$ with

$$\mathcal{L}_s = \tfrac{1}{3}\sum_{r \in \{(1024,120,600),(2048,240,1200),(512,50,240)\}} \Bigl[\tfrac{\lVert Y_r - \hat{Y}_r\rVert_F}{\lVert Y_r\rVert_F} + \lVert \log Y_r - \log \hat{Y}_r\rVert_1\Bigr]$$

(magnitudes clamped 1e-7; both terms averaged over resolutions — verified against `stft_loss.py`).

**6. Complexity.** One parallel forward: $O(T)$ for length-$T$ audio (few conv layers), no autoregressive loop, no iterative steps. Deterministic per mel (no sampling). PyTorch ≥ 1.7 (`torch.stft`), pretrained checkpoints; CPU real-time with V2/small footprint.

### Python implementation sketch (inference, PyTorch)

```python
# sound/synthesis/gan_vocoder.py — SP-143 inference wrapper (sketch)
import json, math
import numpy as np
import torch, torchaudio

def mel_from_audio(x: np.ndarray, fs: int, cfg: dict) -> np.ndarray:
    """STFT -> magnitude -> log-mel condition (B, n_mels, T_frames)."""
    n_fft, hop, n_mels, fmin, fmax = (cfg["fft_size"], cfg["hop_size"],
                                       cfg["num_mels"], cfg["fmin"], cfg["fmax"])
    win = torch.hann_window(n_fft)
    spec = torch.stft(torch.from_numpy(x).float(), n_fft, hop,
                      win_length=n_fft, window=win, return_complex=True)
    mag = spec.abs()                                   # (T_frames, n_fft//2+1)
    fb = torchaudio.functional.melscale_fbanks(
        n_fft // 2 + 1, fmin, fmax, n_mels, fs, None)  # (n_fft//2+1, n_mels)
    mel = torch.log(torch.clamp(mag @ fb, min=1e-5))   # (T_frames, n_mels)
    return mel.T[None]                                 # (1, n_mels, T_frames)

def gan_vocode(mel: torch.Tensor, gen, cfg: dict) -> np.ndarray:
    """One parallel forward: mel (1,80,T_f) -> waveform (1, T_f*hop)."""
    assert mel.shape[1] == cfg["num_mels"], "mel bins mismatch — load checkpoint config!"
    with torch.no_grad():
        gen.eval()
        y = gen(mel)                                   # (1, 1, T)
    return y.squeeze().cpu().numpy()

# --- UnitMatrix dispatch (workflows/musicom_workflow.py produce "SP-143") ---
# produce(midi_path, method="SP-143", params={
#   "rows": {"lead": {"checkpoint": "hifigan_v1_lj", "source": "SP-001"},
#            "pad":  {"checkpoint": "pwg_vctk",      "source": "SP-141"}},
#   "mel": {"n_mels": 80, "hop": 256, "fmin": 0, "fmax": 8000, "fs": 22050},
#   "columns": {"A": {"mel_gain_db": 0}, "B": {"mel_gain_db": -3}}})
# row pipeline: source render -> mel_from_audio -> gan_vocode -> per-row DSP
```

### Musical Elements Framework

- **PITCH** — in the mel condition (bin energy → fundamental + partials). Transpose = shift mel on frequency axis (formant-preserving). Not an oscillator parameter; contrast SP-045 (explicit f0), SP-135 (conditional distribution), SP-060 (denoise steps).
- **RHYTHM** — mel hop grid = temporal quantum (≈11.6 ms @ 22.05 kHz). GAN renders what the mel has; no invented onsets. Frame-exact length = zero-drift audio analogue: `frame = tick · fs / (ticks_per_beat · hop)`.
- **HARMONY** — chords sum linearly in mel, re-rendered coherently; no intermodulation beyond condition. Speech checkpoints vocalize instrumental harmony (Pitfall 2).
- **STRUCTURE** — mel tensor IS the macro-form: sections = mel-frame blocks; conditioning = control surface (like DDAS, but one parallel pass).
- **TEXTURE** — learned prior adds natural micro-variation (breath, roughness, detune). Checkpoint = timbre palette (LJ / VCTK 109 spk / universal). MPD keeps periodic content clean.

### UnitMatrix Integration

**Voices = rows** — per-row mel condition $M_v$ + optional per-row checkpoint; source method per row (any Synthesis Engines SP) for the neural-resynthesis path, or an acoustic-model front-end (F0/loudness → mel). **Sections = columns** — mel-frame blocks; a column change is a conditioning/timbre change; contiguous section-mel tensor → click-free single-pass generation. **Cells = MusicUnit** — tick bounds map to mel frames via the hop ratio; cell-level mel edits = local spectral surgery. Dispatch: `produce(midi_path, method="SP-143", ...)` with row source resolved first; fixed-rate output (22.05/24 kHz) — resample before sample-count-sensitive stages.

### Pitfalls

1. **Checkpoint–mel mismatch** (#1): every checkpoint is bound to n_mels/hop/FFT/fmin/fmax/fs — always load its `config.json`.
2. **Speech checkpoints vocalize instruments** — use music/singing fine-tunes, universal checkpoints, or embrace as choir effect.
3. **Determinism vs diversity** — GAN inference is deterministic per mel; perturb mel or use SP-060/SP-135 for variety.
4. **Training** — GPU-bound; LS-GAN + λ_fm=2 + λ_mel=45 (HiFi-GAN), λ_s=4 (PWG) are the stable defaults; inference-only with pretrained checkpoints is the sanctioned UnitMatrix path.
5. **Edge artifacts** — transposed convs smear edges; keep tensor length multiple of hop (256), trim/pad.
6. **Budget** — V1 13.9 M params offline; CPU real-time needs V2/PWG; batch whole section tensor.
7. **Neighbour audit** — SP-135 autoregressive WaveNet; SP-060 diffusion; SP-045 DSP prior; 057 symbolic piano-roll GAN. SP-143 = adversarial non-autoregressive vocoder: parallel, fast, mel-conditioned, deterministic. Repo: `sound/synthesis/gan_vocoder.py`.

### References

1. Kong, J., Kim, J., Bae, J. (2020). HiFi-GAN. NeurIPS 2020. arXiv:2010.05646.
2. Yamamoto, R., Song, E., Kim, J.-M. (2020). Parallel WaveGAN. ICASSP 2020. arXiv:1910.11480.
3. Kumar, K., et al. (2019). MelGAN. NeurIPS 2019. arXiv:1910.06711.
4. Yang, G., et al. (2021). Multi-band MelGAN. arXiv:2005.05106.
5. jik876/hifi-gan — https://github.com/jik876/hifi-gan (MIT).
6. kan-bayashi/ParallelWaveGAN — https://github.com/kan-bayashi/ParallelWaveGAN (MIT).
7. Oord, A., et al. (2016). WaveNet (SP-135 antecedent). arXiv:1609.03499.
8. Goodfellow, I., et al. (2014). Generative Adversarial Nets. NeurIPS. (origin of the adversarial objective)
9. Mao, X., et al. (2017). Least Squares GAN. ICCV 2017. (LS-GAN objective)
