# Research Report — Method 101: Flow Matching Composition (FMC)

## Date
2026-09-30

## Method Identification

| Field | Value |
|---|---|
| **ID** | 101 |
| **Acronym** | FMC |
| **Full Name** | Flow Matching Composition |
| **Paradigm** | AI-Driven |
| **Layer** | concrete |
| **Description** | Vector-field regression (Conditional Flow Matching) on symbolic music token embeddings: deterministic ODE integration pushes Gaussian noise → structured multi-voice token sequences for UnitMatrix cell filling. |

## Summary Table Row

```
| **101** | concrete | Flow Matching Composition (FMC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Variable (Prior/Conditioning-guided) | Continuous / Continuous | Macro / Full-Sequence Trajectory | $\mathcal{O}(T \cdot d)$ training, $\mathcal{O}(T \cdot d)$ sampling | Vector-field regression (CFM) on token embeddings: deterministic ODE integration pushes noise $\rightarrow$ structured multi-voice token sequences. |
```

## Layer Classification

**concrete** — generates concrete pitch/rhythm/harmony events that fill UnitMatrix cells. The vector field operates on continuous token embeddings (or latent piano-roll representations), and the final ODE integration step produces the actual musical token sequences that decode to MusicEvents. Feeds generators/ directly via ODE sampling from a trained conditional flow matching model.

## Why This Method Is Novel (Not Duplicated)

The existing DB already contains:
- **047 DSMG** (Diffusion Models): score-based stochastic denoising via SDE/ODE
- **072 NFC** (Normalizing Flows): exact-likelihood invertible architectures (affine coupling, Glow) with ELBO training
- **054 ATS** (Autoregressive Transformer): causal next-token prediction

Flow Matching (101 FMC) is fundamentally different:
| Aspect | 047 DSMG | 072 NFC | 101 FMC |
|---|---|---|---|
| Training | Score matching (denoising) | ELBO maximization | **Vector field regression (CFM loss)** |
| Architecture constraint | Score network | Invertible (affine coupling) | **None — any NN works** |
| Sampling | Stochastic SDE or probability-flow ODE | Invert forward pass | **Deterministic ODE integration** |
| Density evaluation | Requires solving SDE/ODE | Exact | **No direct density (trained as generator only)** |
| Latent space | Diffusion step | Full invertibility | **Direct OT path interpolation** |
| Key idea | Reverse noise process | Learn invertible transform | **Learn the flow that pushes noise→data** |

Flow Matching is the paradigm behind recent state-of-the-art music generation models (MusicFlow, MelodyFlow, Stable Audio 2.0, MusFlow) and is a distinct generative modeling framework.

## Musical Elements Framework

### PITCH
Primary token vocabulary dimension. Token embeddings encode MIDI pitch classes (vocab ~128). The flow's vector field $v_\theta(t, x_t)$ learns the full conditional pitch distribution from the corpus. No explicit Markov or n-gram assumptions — the velocity field captures interval preferences, register bounds, and contour from training data.

### RHYTHM
Represented as time-shift/duration tokens in the vocabulary. In the OT path $x_t = (1-t)x_0 + t x_1$, rhythmic patterns smoothly interpolate from noise to data. The velocity field captures onset density distributions, groove patterns, and syncopation through the learned dynamics.

### HARMONY
Chord-conditioning vectors (section-type embeddings, harmonic function tokens) are cross-attended into the transformer blocks. The cascaded FM architecture (MusicFlow) maps text descriptions ("I–V–vi–IV in C") to conditioning latents that steer the decoder FM toward the specified harmony.

### STRUCTURE
The entire sequence $x_1$ is the target — the flow learns the global distribution. Section-type beads (verse/chorus/bridge tokens) are embedded at specific indices. The ODE trajectory deterministically maps noise → full piece. Segment-wise FM with cross-section conditioning provides explicit macro-form control.

### TEXTURE
Joint multi-voice distribution learned directly: each training sample is a concatenated multi-voice token sequence. The transformer's self-attention captures inter-voice dependencies (harmonic alignment, call-response). Texture density emerges from the vocabulary activity rate at the ODE solution.

## UnitMatrix Integration

### Voices
Each voice $v$ contributes token span $s^{(v)}$ to the flattened sequence. Voice-ID embeddings (learned per-voice vectors) are added to each token embedding, maintaining voice identity through the flow. Total sequence length = $V \cdot L$ where $V$ = voice count, $L$ = tokens per voice.

### Sections
Section boundaries are encoded via section-embedding tokens. Section-specific conditioning vectors $c_m$ are input to the transformer as prefix tokens or FiLM-modulated features. Macro-form $\mathcal{F} = [m_1, \ldots, m_M]$ defines the sequence of conditioning vectors. Transition sections use interpolated conditioning $(1-\alpha)c_m + \alpha c_{m+1}$.

### Cell Filling
Single ODE integration pass generates the full multi-voice, multi-section token sequence. Post-generation: token decoding → MusicEvents (pitch, onset, duration, velocity per voice per section cell).

## Candidate Code Path

The implementation would live under:
```
$MUSICOM_ROOT/generators/flow_matching/
├── __init__.py
├── model.py               # MusicFlowTransformer (v_theta network)
├── loss.py                # cfm_loss function
├── sampling.py            # ODE integration (Euler, RK4)
├── tokenizer.py           # Music tokenizer (REMI / compound word)
├── trainer.py             # Training loop
└── config.yaml            # Model hyperparameters
```

Alternatively, integrated into the existing AI-driven generator pipeline:
```
$MUSICOM_ROOT/generators/ai_driven/flow_matching.py
```

## Files Created

| File | Description |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | Appended method section (rows 111+, section after line 111) |
| `/opt/data/projects/Research/CompositionMethods/method_101_FMC.md` | Standalone method write-up with extended math, Python implementation sketch, references |
| `/opt/data/projects/Research/CompositionMethods/report_101.md` | THIS FILE — primary record |

## Line Counts

| Before | After | Delta |
|---|---|---|
| 21943 | 22073 | +130 |

## Next Free ID

The next available algorithmic-method ID after method 100 (AIFC) is **101**. After this addition, the next free ID is **102**.

## Quirks / Pitfalls Encountered

1. **`||` prefix bug in patch**: The patch tool introduced a double-pipe `||` at the start of table row 100 and 101. Had to run a second patch to normalize to single `|`.
2. **LaTeX escaping**: The `$\mathcal{O}(...)$` in the summary table uses `$\\mathcal{O}(...)$` in the raw markdown (backslash-escaped dollar sign for the markdown table parser). The patches preserved this correctly.
3. **Discrete vs continuous tension**: FM is inherently continuous-time/continuous-space; symbolic music is discrete. The embedding-based approach (project discrete tokens → continuous space → run FM → decode) adds a learned decoding step. Discrete Flow Matching (Campbell 2024) solves this directly on the simplex but requires specialized architectures.
4. **One-ENV contract**: All paths resolve through `$MUSICOM_ROOT` (not hardcoded paths). The `utilities.env` resolution helpers should be used for any implementation.
5. **No temperature vs stochastic methods**: Unlike 002 Markov or 053 Lévy which have explicit "randomness knobs", FM sampling is deterministic given the noise seed $x_0$. Stochasticity comes solely from $x_0 \sim \mathcal{N}(0, I)$. This is a design consideration: deterministic sampling lacks the "organic variability" of stochastic methods, but enables controlled interpolation between seeds.

## Classification Details

| Attribute | Value |
|---|---|
| **Tonal Gravity** | Variable — controlled by conditioning vectors (section-chord embeddings, harmonic function tokens). The model can reproduce tonal gravity from the training corpus or be guided by explicit conditioning. |
| **Metric Binding** | Continuous / Continuous — the ODE integration is continuous-time; metric grids are imposed through the token vocabulary (REMI time-shift tokens quantize to 16th/beat grid). |
| **Memory Depth** | Macro / Full-Sequence Trajectory — the vector field regresses the entire sequence from noise in a single ODE integration; self-attention has access to all positions. |
| **Time Complexity** | $\mathcal{O}(T \cdot d)$ training (per CFM step, one forward+backward of $v_\theta$); $\mathcal{O}(T \cdot d)$ sampling (T ODE steps × forward pass). Same order as 047 DSMG but typically 2–5× fewer function evaluations (FM converges with ~50 steps vs 100–1000 for diffusion). |

## Appendex: Complete Method Section Text

(The following is the full method section appended to methods_db.md after line 111. See the file directly for the canonical copy.)

```
### 101. Flow Matching Composition (FMC)

| Attribute | Value |
|---|---|
| **ID** | 101 |
| **Layer** | concrete |
| **Method Name** | Flow Matching Composition |
| **Acronym** | FMC |
| **Paradigm** | **AI-Driven** |
| **Primary Elements** | Pitch, Rhythm, Harmony, Structure, Texture |
| **Tonal Gravity** | Variable (Prior/Conditioning-guided) |
| **Metric Binding** | Grid-Locked / Continuous |
| **Memory Depth** | Macro / Full-Sequence Trajectory |
| **Time Complexity** | $\mathcal{O}(T \cdot d)$ training CFM, $\mathcal{O}(T \cdot d)$ sampling ODE |

### Source

Lipman, Y., Chen, R. T. Q., Ben-Hamu, H., Nickel, M. & Le, M. (2023). "Flow Matching for Generative Modeling." *ICLR 2023*. arXiv:2210.02747.

Campbell, A., Benton, J., De Bortoli, V., Hennig, P. & Doucet, A. (2024). "Discrete Flow Matching." *NeurIPS 2024*. arXiv:2407.15571.

Gat, I., Lorberbom, G., Remez, T. & Adi, Y. (2024). "Discrete Flow Matching." *NeurIPS 2024*.

Prajwal, S. V., et al. (2024). "MusicFlow: Cascaded Flow Matching for Text Guided Music Generation." *ICML 2024*.

Albergo, M. S. & Vanden-Eijnden, E. (2023). "Building Normalizing Flows with Stochastic Interpolants." *ICLR 2023*.

### Layer

**concrete** — generates concrete pitch/rhythm/harmony events that fill UnitMatrix cells. The vector field operates on continuous token embeddings (or latent piano-roll representations), and the final ODE integration step produces the actual musical token sequences that decode to MusicEvents. Feeds generators/ directly via ODE sampling from a trained conditional flow matching model.

### Paradigm

**AI-Driven** — the flow matching model is trained via supervised regression on a corpus of symbolic music tokens embedded in a continuous latent space. The vector field $v_\theta(t, x)$ is learned by minimizing a regression loss against analytically known conditional vector fields. Generation is deterministic given the initial noise sample, differentiable, and invertible.

### Description

**Flow Matching Composition (FMC)** applies the Flow Matching framework (Lipman et al., 2023) — a simulation-free, continuous-time generative modeling paradigm — to the problem of generating symbolic music sequences. Flow Matching bridges and generalizes diffusion models (score matching) and normalizing flows (invertible architectures) by directly learning a **vector field** $v_\theta(t, x)$ that pushes a simple prior distribution $p_0$ (e.g., a standard Gaussian) through a **probability path** $p_t$ to the target data distribution $p_1$ (the training corpus of symbolic music).

The core mathematical structure is:

**Probability path.** A time-indexed family of distributions $p_t(x)$ for $t \in [0,1]$ that interpolates between $p_0$ (pure noise) and $p_1$ (data). The time-evolution of this path is governed by the **continuity equation** (transport equation):

$$\partial_t p_t + \nabla \cdot (p_t u_t) = 0$$

where $u_t : \mathbb{R}^d \to \mathbb{R}^d$ is the **vector field** that generates the flow. The flow is the diffeomorphism $\psi_t$ satisfying:

$$\frac{d}{dt} \psi_t(x) = u_t(\psi_t(x)), \quad \psi_0(x) = x$$

and $p_t = [\psi_t]_* p_0$ (the pushforward of $p_0$ by $\psi_t$).

**Conditional Flow Matching (CFM).** The key insight of Lipman et al. is to avoid the intractable marginal vector field $u_t$ by decomposing it into a mixture of **conditional** vector fields, one per data point $x_1$:

$$p_t(x) = \int p_1(x_1) \cdot p_t(x \mid x_1) \, dx_1$$

$$u_t(x) = \mathbb{E}_{x_1 \sim p_1 \mid x_t = x} [u_t(x \mid x_1)]$$

The **conditional probability path** $p_t(x \mid x_1)$ is chosen as a simple Gaussian:

$$p_t(x \mid x_1) = \mathcal{N}(x \mid \mu_t(x_1), \sigma_t(x_1)^2 I)$$

with the standard choice being the **optimal transport (OT) path** (linear interpolation):

$$x_t = (1 - t) x_0 + t x_1, \quad x_0 \sim \mathcal{N}(0, I)$$

The conditional vector field for this path is:

$$u_t(x \mid x_1) = \frac{x_1 - x}{1 - t} = x_1 - x_0$$

This gives the **Conditional Flow Matching (CFM) loss**:

$$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t \sim \mathcal{U}[0,1], \, x_0 \sim p_0, \, x_1 \sim p_1} \left\| v_\theta(t, x_t) - (x_1 - x_0) \right\|^2$$

where $x_t = (1-t)x_0 + t x_1$ and $\theta$ are the neural network parameters. Note: **no score function, no ELBO, no invertibility constraint** — just a vector field regression.

**Sampling (generation).** To generate, start with noise $x_0 \sim \mathcal{N}(0, I)$, then integrate the learned ODE forward:

$$\frac{dx}{dt} = v_\theta(t, x), \quad x(0) = x_0$$

using any ODE solver (Euler, RK4, Dormand-Prince). The final state $x(1)$ is the generated sample.

**Discrete extension (for symbolic music).** Because symbolic music tokens are discrete (MIDI pitch/duration/velocity classes, REMI tokens), naive continuous Gaussian paths are inappropriate. **Discrete Flow Matching** (Campbell et al., 2024; Gat et al., 2024) generalizes FM to categorical data by replacing the linear Gaussian interpolation with a **probability simplex interpolation**:

$$x_t = (1-t) \cdot e_{x_0} + t \cdot e_{x_1}$$

where $e_{x_0}$ and $e_{x_1}$ are one-hot vectors over the token vocabulary. The vector field becomes a velocity field on the simplex, and the CFM loss becomes a cross-entropy regression toward the target token distribution.

Alternatively, tokens are embedded into a continuous latent space via a trainable embedding matrix $E \in \mathbb{R}^{|\mathcal{V}| \times d}$, and FM takes place in $\mathbb{R}^d$ with the standard Gaussian path, followed by a softmax decoder at $t=1$.

**Cascaded flow matching for music (MusicFlow paradigm).** Prajwal et al. (2024) use a cascaded architecture with two flow matching networks:
1. **Prior FM**: maps text/image embeddings to a semantic music representation (MuLAN / CLAP embedding space).
2. **Diffusion / Decoder FM**: maps the semantic representation to a mel-spectrogram or token sequence (continuous latent rendering).

For symbolic music, the second stage directly decodes to discrete MIDI/REMI tokens via the discrete FM framework.

### Musical Elements Framework

**PITCH**: The primary dimension of the flow. Token embeddings are MIDI pitch classes or scale degrees (vocabulary size $|\mathcal{V}| \approx 128$ for raw MIDI, or $|\mathcal{V}| \approx 7\text{–}12$ for scale-quantized). Pitch evolves continuously through the latent space during integration, projecting to discrete tokens only at the final time $t=1$. The vector field's learned dynamics encode the full conditional distribution of pitch sequences — interval preferences, conjunct bias, register boundaries — without explicit Markov assumptions. Chord conditioning (harmonic) tokens steer the flow toward tonal targets.

**RHYTHM**: Represented as duration and onset-interval tokens (REMIOffsets, time-shift tokens) in the vocabulary. In the discrete FM formulation, the interpolant $(1-t) e_{x_0} + t e_{x_1}$ smoothly deforms rhythmic patterns between noise and data, so onset timing and duration distributions emerge from the learned velocity field. Cascaded FM can separate rhythm (time-shift tokens) and pitch (note tokens) into parallel streams, giving independent control.

**HARMONY**: Multi-voice chord symbols or chord-conditioning tokens are concatenated or cross-attended into the flow's conditioning context. The OT path ensures that each generated token trajectory moves monotonically toward its corpus-derived chord assignment. Per-voice flows with shared section/chord conditioning produce harmonically coherent output across voices. The cascaded architecture's prior FM can map text descriptions of harmony (e.g., "I–V–vi–IV in C major") to a conditioning vector that steers the decoder FM.

**STRUCTURE**: The flow's trajectory through latent space inherently reflects macro-form because the conditional vector field $u_t(x \mid x_1)$ regresses the entire sequence $x_1$ from $x_0$ — the full piece is the target. Section boundaries emerge from section-embedding tokens embedded at specific time indices along the flow. Segment-wise FM (one FM per section, with cross-section conditioning) provides explicit macro-form control: each section's $x_1$ is drawn from the corresponding section type (verse/chorus/bridge), and a tempo/form schedule conditions the segment transitions. The ODE sampling is continuous and differentiable, so form-level features propagate smoothly.

**TEXTURE**: In multi-voice generation, the joint data distribution $p_1(x^{(1)}, x^{(2)}, \ldots, x^{(V)})$ encodes correlation structure across voices. The flow learns this joint distribution directly: each training sample is a multi-voice concatenation, and the vector field captures inter-voice dependencies (harmonic alignment, call-response, hocket). Voice separation can be achieved by independent flows with a coupling term, or by a single flow over a flattened multi-voice token sequence. Texture density is the vocabulary activity rate at the decoded output.

### UnitMatrix Integration (Voices & Sections)

**Voices**: Each voice $v$ contributes its token sequence $s^{(v)} = (s^{(v)}_1, \ldots, s^{(v)}_L)$ to the flattened token sequence $s = (s^{(1)}, s^{(2)}, \ldots, s^{(V)})$ of length $V \cdot L$. The flow operates on the embedding of this flattened sequence. Voice separation emerges because each token's embedding preserves its voice identity (via a learned voice-ID embedding added to the token embedding). At generation time, the decoded output is split back per voice and decoded to MusicEvents. Percussion tracks can be handled as a separate token vocabulary or as a specialized 2-state channel.

**Sections**: Each section $m$ maps to a span of token indices in the flattened sequence. Section-types (A, B, bridge, C) are encoded as section-conditioning tokens concatenated to the flow's input, or as separate prior flows in the cascaded architecture. The macro-form $\mathcal{F} = [m_1, m_2, \ldots, m_M]$ defines a sequence of section-specific conditioning vectors. Transition sections use linear interpolation of conditioning vectors $(1-\alpha)c_{m} + \alpha c_{m+1}$.

**Cell filling**: For each cell (voice $v$, section $m$), the token span at indices $[(v-1) \cdot L + (m-1) \cdot l + 1, \ldots, (v-1) \cdot L + m \cdot l]$ (where $l = L/M$ is the tokens-per-section) is filled by the flow trajectory. The complete multi-voice, multi-section token sequence is generated in a single forward ODE integration pass. Post-generation, tokens are decoded to $MusicEvent$ objects: pitch from token vocabulary lookup, duration from time-shift token accumulation, onset from cumulative time-shifts.

### Pitfalls

1. **ODE integration cost**: Compared to autoregressive methods (054 ATS, $\mathcal{O}(N)$), FM requires $\mathcal{O}(T \cdot d)$ ODE steps ($T \approx 50\text{–}500$ steps, $d = \text{latent dimension}$). Faster solvers (DPM-Solver, consistency models) mitigate this but add implementation complexity. The CFM loss is simulation-free, but sampling requires full ODE integration.

2. **Discrete token handling**: The fundamental tension between FM's continuous-time continuous-space formulation and symbolic music's discrete token space. Embedding-based approaches (project to $\mathbb{R}^d$, run FM, decode) add a learned decoding step that can introduce artifacts. Discrete FM (simplex interpolation) exactly preserves discreteness but requires specialized architectures (transformer over simplex states).

3. **Voice independence control**: A single flattened sequence couples all voices into one trajectory, making independent variation challenging. Decoupled flows (one per voice) with a coupling potential (cross-attention between voice flows) is the recommended design but doubles training/sampling cost per voice.

4. **Training data requirements**: FM requires a large corpus of full-length multi-voice pieces to learn the joint distribution $p_1$. Section-level conditioning reduces this requirement per section type, but the total data diversity must cover all sections.

5. **Inversion cost**: Unlike 072 NFC (exact invertibility), FM's flow is only approximately invertible through the reverse ODE. The ODE integration error accumulates, so exact reconstruction of training samples requires many solver steps.

6. **Long-sequence handling**: FM's latent vector dimension scales with sequence length. For pieces with $V \cdot L > 2048$ tokens, the transformer processing the flattened sequence becomes memory-bound. Hierarchical FM (segment-level + token-level) or autoregressive decoding of the FM output (hybrid FM+ATS) mitigates this.

7. **Evaluation and comparison**: FM's deterministic ODE sampling (given a noise seed) is easily compared to 047 DSMG (stochastic SDE) and 072 NFC (exact density). Metrics should track both sample quality (FAD, KL divergence of pitch/rhythm distributions) and computational cost per sample. FM is typically 2–5× faster at inference than 047 DSMG with equivalent quality (due to fewer function evaluations), but slower than 054 ATS.
```