# Multi-Track Generative Adversarial Composition (MT-GAC) (Method 057)

### **Source**
Adapted from generative adversarial networks (Goodfellow et al., 2014, "Generative Adversarial Nets", NeurIPS) and their symbolic-music applications. Core lineage: **MuseGAN** (Dong, Hsiao & Yang, 2018, "MuseGAN: Multi-track Sequential Generative Adversarial Networks for Symbolic Music Generation and Accompaniment", AAAI 2018, arXiv:1709.06298) — the first model to generate multi-track, polyphonic music via GANs; **SeqGAN** (Yu et al., 2017, "SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient", AAAI 2017, arXiv:1609.05473) — GANs for discrete token sequences via policy-gradient (REINFORCE) surrogate; **MidiNet** (Yang et al., 2017, "MidiNet: A Convolutional Generative Adversarial Network for Symbolic-domain Music Generation", ISMIR 2017, arXiv:1703.10847) — CNN GAN with conditional channel expansion for bar-by-bar melody generation; **WGAN-GP** (Gulrajani et al., 2017, arXiv:1704.00028) — Wasserstein objective with gradient penalty, the training stabilization that made MuseGAN practical; DCGAN (Radford et al., 2016, arXiv:1511.06434) for transposed-convolution upsampling conventions. This method fills the adversarial gap in the DB's AI-Driven family: 042 NST (style transfer), 046 VAE-LSI (latent interpolation), 047 DSMG (diffusion), 054 ATS (autoregressive) — none use a generator/discriminator minimax game.

### **Description**
Multi-Track Generative Adversarial Composition (MT-GAC) trains a pair of neural networks in a two-player minimax game. The **generator** $G$ maps a latent noise vector $z \sim \mathcal{N}(0, I)$ to an artificial multi-track piano-roll tensor $\hat{X} = G(z)$; the **discriminator** $D$ learns to distinguish real piano-rolls $X \sim p_{data}$ from generated ones. $G$ is trained to fool $D$; $D$ is trained to catch $G$. At convergence $p_g \approx p_{data}$: the generator has implicitly learned the training corpus' musical statistics and can synthesize novel piano-rolls.

Original GAN objective (Goodfellow 2014):
$$\min_G \max_D \; \mathbb{E}_{x \sim p_{data}}[\log D(x)] + \mathbb{E}_{z \sim p_z}[\log(1 - D(G(z)))]$$

MuseGAN replaces the Jensen-Shannon objective with the **Wasserstein distance** plus **gradient penalty** (WGAN-GP, Gulrajani et al. 2017) to stabilize training and prevent mode collapse:
$$L = \mathbb{E}_{\tilde{x} \sim p_g}[D(\tilde{x})] - \mathbb{E}_{x \sim p_{data}}[D(x)] + \lambda\,\mathbb{E}_{\hat{x} \sim p_{\hat{x}}}[(\|\nabla_{\hat{x}} D(\hat{x})\|_2 - 1)^2]$$

**Representation**: Music is a piano-roll tensor of shape (bar, time_step, pitch, track) — 4 bars × 96 time steps (16th notes) × 84 notes (C1–C8 range) × 5 tracks (bass, drums, guitar, piano, strings) in the original MuseGAN setup (Lakh Pianoroll Dataset, LPD, 173,997 multi-track piano-rolls derived from the Lakh MIDI Dataset). Note grouping (chords, arpeggios, melodies) emerges in the *pitch dimension of each bar*, not as sequential tokens — this is what distinguishes GAN approaches from autoregressive token generation (054 ATS).

**Three track-interaction architectures** (MuseGAN's key musical insight — how tracks relate):
1. **Jamming model**: each track $i$ has its own private generator $G_i$ with private noise $z_i$ → tracks generated independently (free jazz / loose jamming; no inter-track coordination).
2. **Composer model**: a single generator produces ALL tracks jointly from one shared noise vector $z$ → maximum inter-track dependence (through-composed score).
3. **Hybrid model**: each track has a private generator $G_i(z_i)$ but all share an additional inter-track latent vector $z$ → tracks are individually controllable yet collectively harmonious (pop/rock arrangement). MuseGAN's recommended default.

**Temporal structure** (bar-sequence coherence, MuseGAN §3.2): a two-subnetwork generator —
- **Temporal-structure generator** $G_{temp}$: maps noise $z$ to a sequence of per-bar latent vectors $\hat{z} = \{\hat{z}(t)\}_{t=1}^{T}$ (transposed CNN growing the time axis first).
- **Bar generator** $G_{bar}$: consumes each $\hat{z}(t)$ and produces that bar's piano-roll; bars are generated sequentially, so $\hat{z}(t)$ carries cross-bar (phrase-level) information: $G(z) = \{G_{bar}(\hat{z}(t))\}_{t=1}^{T}$.
- **Track-conditional mode**: a human-provided bar sequence $\tilde{y}(t)$ for one track conditions $G'_{bar}$, which then generates the *remaining* tracks bar by bar — human-AI co-composition / accompaniment (MuseGAN's headline extension).

**Training details (verified from the paper)**: $G$ updated once every 5 $D$ updates; batch normalization on $G$ only; total latent length fixed at 128 (one vector of 128, two of 64, or four of 32); last layer uses tanh, output binarized at threshold zero at test time; < 24h training on a Tesla K40m; evaluation via intra-track metrics (EB = empty-bar ratio, UPC = used pitch classes per bar, QN = qualified-note ratio) and inter-track metrics plus a 144-listener user study.

### **Musical Elements Framework**
- **PITCH**: Learned implicitly in the piano-roll's pitch axis. Pitch vocabulary = 84 notes (C1–C8); the generator's convolutions learn local pitch patterns (chords as vertical onsets, arpeggios as diagonal runs). No explicit scale — the corpus (LPD rock/pop) supplies tonal statistics. Pitch contour, register, and chord vocabulary are discriminator-enforced: $D$ rejects pitch usages that deviate from the learned distribution.
- **RHYTHM**: Time axis = 96 steps per bar (16th-note grid, 4 bars per sample). Rhythmic feel (backbeat, syncopation, density) emerges from the corpus. The empty-bar ratio (EB) and qualified-note ratio (QN, notes ≥ 3 time steps = 32nd notes) are the quantitative rhythm-quality gates. Track-conditional mode lets a human set rhythm for one track; the model infers complementary rhythm for the others.
- **HARMONY**: Inter-track verticality is the adversarial game's core target. In the hybrid model, the shared latent $z$ (and the joint discriminator looking at all tracks simultaneously) forces the generated tracks to be *collectively harmonious*; the composer model pushes this to the limit (all tracks from one noise vector). Inter-track metrics (beat-track consistency, empty-bar coordination across tracks) quantify harmonic/textural coordination.
- **STRUCTURE**: Macro-form is learned at phrase scale. $G_{temp}$'s per-bar latent sequence $\hat{z}(t)$ carries the temporal trajectory — the generator learns which bar-level contexts follow which (repetition, contrast, development) from the corpus. The 4-bar segment is the atomic unit; longer forms are stitched from conditioned segments (or, in track-conditional mode, from a human-supplied bar skeleton). Section contrast = distinct latent regions / conditioned segments.
- **TEXTURE**: Track dimension = texture axis. 5 simultaneous tracks (bass, drums, guitar, piano, strings) with three inter-track coupling regimes (jamming = independent, composer = fused, hybrid = shared-guidance) give explicit textural control. Track dropout / per-track latent manipulation re-voices the texture. The track-conditional extension re-orchestrates: keep human bass line, generate new piano/strings/guitar/drums = instant re-texturing.

### **UnitMatrix Integration (Voices & Sections)**
- **Rows (Voices)**: Each voice $v$ maps to one track of the piano-roll tensor — the track dimension IS the voice dimension. Bass, drums, guitar, piano, strings ↔ UnitMatrix rows. In the jamming model each row gets its own generator/seed; in the hybrid model all rows share the inter-track latent $z$ (coordination) plus per-row private noise (individuality).
- **Columns (Sections)**: Each section $s$ maps to a generated segment (4-bar block). The temporal-structure generator $G_{temp}$ produces the per-segment latent trajectory $\hat{z}(s)$; successive segments' $\hat{z}$ values ARE the section sequence. Section A / B / A' contrast arises from distinct latent regions; track-conditional mode can pin a human-composed skeleton column for a specific row.
- **Cells** $U_{v, s}$:
  - `{PITCH}`: The pitch-axis slice of track $v$ in segment $s$'s piano-roll (84-note vocabulary, binarized at threshold 0, quantized to 12-TET scale).
  - `{RHYTHM}`: The time-axis pattern (96 steps/bar) of track $v$ in segment $s$ — onset grid, qualified-note ratio ≥ 3 steps, empty-bar gate.
  - `{TEXTURE}`: Track-coupling mode (jamming/composer/hybrid) + per-track activation; inter-track coordination metrics per segment.
- **Mapping Flow**:
  1. Train (or load) MT-GAC on the target corpus (multi-track piano-rolls, e.g., LPD). $D$ + $G_{temp}$ + $G_{bar}$ per chosen coupling mode.
  2. Sample latent vector(s) $z$ (length 128 split per model: 1×128, 2×64, or 4×32) from $\mathcal{N}(0, I)$.
  3. $G_{temp}$ expands $z$ into per-segment latent trajectory $\hat{z}(1) \ldots \hat{z}(S)$ (one per UnitMatrix column).
  4. $G_{bar}$ generates each segment's multi-track piano-roll; binarize at 0.
  5. Slice the tensor: track axis → rows (voices), segment axis → columns (sections), pitch/time axes → cell content.
  6. Quantize pitches to the target scale (12-TET), snap onsets to the grid, then run musicom Phase-2 rules (chord-tone quantization, voice-leading check) via the two-phase workflow.
  7. Fill UnitMatrix cells and export through `UnitMatrixComposer` (create_matrix → add_voice → add_section → fill_voice_section → validate → to_midi).

### **Pitfalls**
1. **Mode collapse**: generator produces one (or few) musically similar outputs. Mitigate: WGAN-GP objective (instead of JS-divergence), diverse training data, mini-batch discrimination, unrolled GANs.
2. **Discrete-output gradient problem**: piano-roll entries are binary; gradients cannot flow through argmax/threshold sampling. Mitigate: continuous tanh output with 0-threshold binarization at test time (MuseGAN's solution), or policy-gradient surrogate (SeqGAN's REINFORCE approach for token sequences).
3. **Training instability / non-convergence**: G vs D imbalance. Mitigate: 5:1 D:G update ratio, batch-norm on G only (verified MuseGAN settings), gradient penalty λ, learning-rate tuning.
4. **Bar-level incoherence**: bars generated independently lack phrase continuity. Mitigate: $G_{temp}$ per-bar latent sequence (MuseGAN §3.2) so each bar's generation is conditioned on its position in the phrase.
5. **Scale/tonality drift**: GANs learn corpus statistics, not rules — output can wander chromatically or shift key mid-phrase. Mitigate: musicom Phase-2 chord-tone quantization + voice-leading rules (two-phase workflow); optionally condition on a chord/track skeleton (track-conditional mode).
6. **Rhythmic fragmentation**: overly sparse or staccato output (high empty-bar / low qualified-note ratio). Mitigate: QN gate (notes ≥ 3 time steps), corpus filtering, and the sparse+continuous hybrid rule from the method master map (pair with a continuous fill layer).
7. **Fixed-length limitation**: generation is locked to the training segment length (4 bars in MuseGAN). Mitigate: track-conditional mode extends to arbitrary length by feeding a human bar skeleton; or stitch segments with overlap/conditioning.
8. **Compute cost**: GAN training needs GPU hours (MuseGAN: < 24h on Tesla K40m) plus large curated corpora (LPD: 173,997 piano-rolls). Mitigate: distill into a lightweight surrogate, or use pretrained checkpoints for inference-only UnitMatrix filling.
9. **Inter-track metric blindness**: intra-track metrics (EB, UPC, QN) don't measure whether tracks are *coordinated*. Mitigate: use inter-track metrics during training selection; the composer/hybrid architectures enforce coordination structurally.
10. **Reproducibility of texture roles**: without conditioning, the model may blur track identities (e.g., drums playing sustained chords). Mitigate: per-track private latents + shared latent (hybrid), track-conditional generation with fixed role priors, or post-hoc role reassignment by register in Phase 2.

### **Implementation Requirements (Python / NumPy / PyTorch)**
```python
import numpy as np
import torch
import torch.nn as nn

# --- Hyperparameters (verified from MuseGAN paper) ---
BARS, STEPS, NOTES, TRACKS = 4, 96, 84, 5   # segment: 4 bars x 96 16ths x 84 notes (C1-C8) x 5 tracks
LATENT = 128                                  # total noise length: 1x128 / 2x64 / 4x32 per model
D_UPDATES_PER_G = 5                           # update G once every 5 D updates
LAMBDA_GP = 10.0                              # WGAN-GP gradient penalty weight

def make_noise(jamming=False, n_tracks=TRACKS, shared=None):
    """MuseGAN noise scheme: hybrid = shared latent + per-track private noise."""
    if shared is None:
        shared = torch.randn(1, LATENT)                       # inter-track z (hybrid/composer)
    if jamming:
        return [torch.randn(1, LATENT) for _ in range(n_tracks)]  # private only
    private = [torch.randn(1, LATENT // n_tracks) for _ in range(n_tracks)]
    return shared, private

class TempGenerator(nn.Module):
    """G_temp: noise z -> per-bar latent sequence z_hat(1..T). Time axis first (MuseGAN)."""
    def __init__(self, latent=LATENT, bars=BARS, bar_latent=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent, 512), nn.BatchNorm1d(512), nn.ReLU(),
            nn.Linear(512, bars * bar_latent), nn.BatchNorm1d(bars * bar_latent), nn.ReLU(),
        )
        self.bar_latent = bar_latent
    def forward(self, z):
        return self.net(z).view(-1, BARS, self.bar_latent)    # (1, bars, bar_latent)

class BarGenerator(nn.Module):
    """G_bar: per-bar latent z_hat(t) -> bar piano-roll (steps, notes, tracks)."""
    def __init__(self, bar_latent=64):
        super().__init__()
        # transposed-conv upsampling: pitch axis last (MuseGAN grows time then pitch)
        self.net = nn.Sequential(
            nn.ConvTranspose2d(bar_latent, 512, kernel_size=(4, 1), stride=(2, 1), padding=(1, 0)),
            nn.BatchNorm2d(512), nn.ReLU(),
            nn.ConvTranspose2d(512, 256, kernel_size=(4, 2), stride=(2, 2), padding=(1, 0)),
            nn.BatchNorm2d(256), nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=(4, 2), stride=(2, 2), padding=(1, 0)),
            nn.BatchNorm2d(128), nn.ReLU(),
            nn.ConvTranspose2d(128, 64,  kernel_size=(4, 3), stride=(2, 3), padding=(1, 1)),
            nn.BatchNorm2d(64), nn.ReLU(),
            nn.ConvTranspose2d(64, TRACKS, kernel_size=(3, 3), stride=(1, 2), padding=(1, 1)),
            nn.Tanh(),                                        # tanh output, binarize at 0 at test
        )
    def forward(self, z_bar):
        # z_bar: (1, bar_latent) -> (1, bar_latent, 1, 1) -> (1, tracks, 96, 84)
        return self.net(z_bar.view(1, -1, 1, 1)).permute(0, 2, 3, 1)

class Discriminator(nn.Module):
    """D: full segment (bars, steps, notes, tracks) -> realness score (WGAN critic)."""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv3d(1, 128, kernel_size=(3, 3, 3), stride=(2, 2, 2), padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv3d(128, 256, kernel_size=(3, 3, 3), stride=(2, 2, 2), padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv3d(256, 512, kernel_size=(3, 3, 3), stride=(2, 2, 2), padding=1),
            nn.LeakyReLU(0.2),
            nn.Flatten(), nn.Linear(512, 1),                  # no sigmoid: WGAN critic
        )
    def forward(self, x):
        return self.net(x)

def gradient_penalty(D, real, fake):
    """WGAN-GP: ||grad D(interp)||_2 -> 1 (Gulrajani et al. 2017)."""
    alpha = torch.rand(real.size(0), 1, 1, 1, 1)
    interp = alpha * real + (1 - alpha) * fake
    interp.requires_grad_(True)
    d_interp = D(interp)
    grads = torch.autograd.grad(outputs=d_interp, inputs=interp,
                                grad_outputs=torch.ones_like(d_interp),
                                create_graph=True)[0]
    return ((grads.norm(2, dim=1) - 1) ** 2).mean() * LAMBDA_GP

# --- Training loop skeleton (WGAN-GP; G updated once per 5 D updates) ---
def train_step(G_temp, G_bar, D, opt_g, opt_d, real, jamming=False):
    opt_d.zero_grad()
    shared, private = make_noise(jamming)
    if jamming:
        fake = torch.stack([G_bar(G_temp(p)[0]) for p in private], dim=-1).squeeze(1)
    else:
        z_hat = G_temp(shared)                                # (1, BARS, bar_latent)
        fake = torch.stack([G_bar(z_hat[:, t]) for t in range(BARS)], dim=1)
    # fake: (1, BARS, 96, 84, TRACKS) -> (1, 1, BARS, 96, 84*TRACKS) fold tracks into pitch
    fake_folded = fake.permute(0, 1, 2, 3, 4).reshape(1, 1, BARS, STEPS, NOTES * TRACKS)
    real_folded = real.reshape(1, 1, BARS, STEPS, NOTES * TRACKS)
    d_loss = D(fake_folded).mean() - D(real_folded).mean() + gradient_penalty(D, real_folded, fake_folded)
    d_loss.backward(); opt_d.step()
    if step % D_UPDATES_PER_G == 0:
        opt_g.zero_grad()
        g_loss = -D(fake_folded).mean()                        # WGAN generator loss
        g_loss.backward(); opt_g.step()

# --- Inference: fill a UnitMatrix column with a generated segment ---
def generate_segment(G_temp, G_bar, seed=0):
    torch.manual_seed(seed)
    shared, private = make_noise()
    z_hat = G_temp(shared)[0]                                  # (BARS, bar_latent)
    rolls = [G_bar(z_hat[t]).detach() for t in range(BARS)]    # each (1, 96, 84, 5)
    seg = torch.stack(rolls).squeeze(1).numpy()                # (BARS, 96, 84, TRACKS)
    return (seg > 0.0).astype(np.uint8)                        # binarize at threshold 0

# Segment -> UnitMatrix cells: track v -> voice v, bar b -> cell pitch/rhythm grid
def roll_to_units(seg, track_idx, min_note_len=3):
    """Piano-roll slice (BARS, 96, 84) -> list of (start_step, end_step, pitch) events."""
    events = []
    for bar in range(seg.shape[0]):
        grid = seg[bar, :, :, track_idx]                       # (96, 84) onsets
        # run-length encode along time axis per pitch
        for p in range(grid.shape[1]):
            runs = np.diff(np.concatenate(([0], grid[:, p], [0])))
            starts = np.where(runs == 1)[0]
            ends = np.where(runs == -1)[0]
            for s, e in zip(starts, ends):
                if e - s >= min_note_len:                      # qualified-note gate
                    events.append((bar, int(s), int(e), p + 12))  # C1=12 -> MIDI
    return events
```

### **References**
- Goodfellow, I., et al. (2014). "Generative Adversarial Nets." NeurIPS 27. arXiv:1406.2661.
- Dong, H.-W., Hsiao, W.-Y., Yang, L.-C., Yang, Y.-H. (2018). "MuseGAN: Multi-track Sequential Generative Adversarial Networks for Symbolic Music Generation and Accompaniment." AAAI 2018. arXiv:1709.06298. Code: https://salu133445.github.io/musegan/
- Yu, L., et al. (2017). "SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient." AAAI 2017. arXiv:1609.05473.
- Yang, L.-C., Chou, S.-Y., Yang, Y.-H. (2017). "MidiNet: A Convolutional Generative Adversarial Network for Symbolic-domain Music Generation." ISMIR 2017. arXiv:1703.10847.
- Gulrajani, I., et al. (2017). "Improved Training of Wasserstein GANs." NeurIPS 2017. arXiv:1704.00028.
- Radford, A., Metz, L., Chintala, S. (2016). "Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks" (DCGAN). ICLR 2016. arXiv:1511.06434.
- Arjovsky, M., Chintala, S., Bottou, L. (2017). "Wasserstein GAN." ICML 2017. arXiv:1701.07875.
- Raffel, C. (2016). "Learning-Based Methods for Comparing Sequences, with Applications to Audio-to-MIDI Alignment and Matching" (Lakh MIDI Dataset). Ph.D. thesis, Columbia University.
- Dong, H.-W., et al. (2018). "Lakh Pianoroll Dataset (LPD)." Companion dataset to MuseGAN; 173,997 multi-track piano-rolls.
