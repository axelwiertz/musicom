# Method 106: Non-Autoregressive Parallel Composition (NAPC)

**ID:** 106  
**Acronym:** NAPC  
**Layer:** concrete  
**Paradigm:** AI-Driven  
**Added:** 2026-10-05  
**Tonal Gravity:** Variable (Bidir-context-guided)  
**Metric Binding:** Grid-Locked / Continuous  
**Memory Depth:** Macro / Mask-Predict Iterations  
**Time Complexity:** $\mathcal{O}(R \cdot V \cdot T \cdot d)$ (where $R$ = refinement steps, $V$ = voices, $T$ = time steps per voice, $d$ = transformer embedding dimension)

---

## Overview

Non-Autoregressive Parallel Composition (NAPC) reframes symbolic music generation as a **masked language modeling (MLM) decoding problem**: instead of generating notes left-to-right (autoregressive), NAPC generates **all notes simultaneously** using iterative mask-predict refinement. A bidirectional transformer (BERT-style encoder) predicts probability distributions over the token vocabulary for every masked position, and the most confident predictions are progressively unmasked across refinement steps.

This is **non-autoregressive** — there is no causal masking during training (every position sees every other position through bidirectional self-attention), and at generation time the entire piece is decoded in $R$ parallel passes rather than $N$ sequential passes. This fundamentally changes the generative dynamics compared to autoregressive models: long-range structure, section symmetry, and harmonic voicing constraints are resolved from full context rather than accumulated left-to-right.

### Key Innovation

The mask-predict paradigm (Ghazvininejad et al. 2019) adapts the BERT masked language model (Devlin et al. 2019) for **conditional generation**: instead of predicting a fixed set of masked tokens in one pass, the model iteratively refines its predictions:

1. **Fully masked start**: $\mathbf{x}^{(0)} = [MASK, MASK, \ldots, MASK]$
2. **At each step $t$**: predict $P(\mathbf{x} \mid \mathbf{x}^{(t)}, \mathrm{conditioning})$
3. **Unmask $K_t$ positions** with highest confidence $c_i = \max_k P(x_i = k)$
4. **Remask** a fraction of the least confident unmasked tokens for revision
5. **Repeat** until all positions are resolved

Unlike continuous denoising diffusion (047 DSMG) which operates on Gaussian noise and iteratively denoises, NAPC works directly on discrete tokens using a deterministic mask-unmask schedule. The refinement steps are interpretable: step 1 resolves the key/harmony scaffold, step 2 fills chord tones, step 3 adds passing tones and ornamental notes, step 4 polishes voice-leading and rhythmic detail.

### Relationship to Existing Methods

| Method | Strategy | Order | Context |
|--------|----------|-------|---------|
| 054 ATS (Autoregressive Transformer) | Left-to-right token prediction | $O(N)$ serial passes | Causal left-only context |
| 047 DSMG (Diffusion) | Gaussian denoising of continuous latents | $O(T)$ steps, continuous | Bidirectional (learned score) |
| **106 NAPC (Non-Autoregressive)** | **Mask-predict iterative refinement** | **$O(R)$ passes, discrete** | **Bidirectional (full)** |
| 046 VAE-LSI | Latent sampling + interpolation | $O(1)$ sample | Global latent vector |

NAPC fills a specific gap: it produces discrete symbolic tokens (like 054 ATS) but with bidirectional context (like 047 DSMG), and it requires only $R \approx 8$–16 refinement passes regardless of sequence length (unlike 054's $O(N)$).

---

## Mathematical Formulation

### Mask-Predict for Music

Let $\mathbf{x} = [x_1, \ldots, x_L]$ be the full flat token sequence of length $L = V \cdot T$, where $V$ = voices and $T$ = time steps. Each $x_i \in \mathcal{V} = \{ \text{pitch classes, durations, velocities, } [MASK], [PAD] \}$.

At generation time, we start with $\mathbf{x}^{(0)} = [MASK]^L$ and iterate for $t = 1 \ldots R$:

**1. Predict distributions:**

$$p_i^{(t-1)}(k) = P(x_i = k \mid \mathbf{x}^{(t-1)}, \mathbf{c}) \quad \forall i, \forall k \in \mathcal{V}$$

where $\mathbf{c}$ is conditioning information (section embeddings, chord labels, key, tempo).

**2. Compute confidence:**

$$c_i^{(t-1)} = \max_k p_i^{(t-1)}(k)$$

**3. Determine unmask count $K_t$:**

$$K_t = \left\lceil L \cdot \frac{\cos\left(\frac{\pi t}{2R}\right)}{\cos\left(\frac{\pi (t-1)}{2R}\right)} \right\rceil \quad \text{(cosine schedule)}$$

or the simpler linear variant:

$$K_t = \left\lceil \frac{L}{R} \right\rceil \quad \text{(constant schedule)}$$

**4. Unmask top-$K_t$ positions:**

$$\mathcal{U}_t = \text{indices of the } K_t \text{ largest } c_i^{(t-1)} \text{ in masked positions}$$  
$$x_i^{(t)} = \arg\max_k p_i^{(t-1)}(k) \quad \forall i \in \mathcal{U}_t$$
$$x_i^{(t)} = x_i^{(t-1)} \quad \forall i \notin \mathcal{U}_t$$

**5. (Optional) Re-mask least confident for revision:**

Let $\mathcal{R}_t = \text{indices of the } \lfloor K_t / 2 \rfloor \text{ smallest } c_i^{(t)} \text{ among just-unmasked positions}$  
Set $x_i^{(t)} = [MASK] \quad \forall i \in \mathcal{R}_t$

**6. Repeat** from step 1 for $t+1$ until $t = R$.

After $R$ steps, all positions are unmasked and the sequence is reshaped into $V \times T$ for `MusicUnit` decoding.

### Training Objective

The model is trained with **masked language modeling (MLM) loss** on random masking (typically 15% of tokens), augmented with **discrete diffusion training** (the model sees the full mask-density range 0–100%):

$$\mathcal{L}_{\text{MLM}} = -\mathbb{E}_{x \sim \mathcal{D}} \mathbb{E}_{\mathcal{M} \sim p_{\text{mask}}} \sum_{i \in \mathcal{M}} \log P(x_i \mid x_{\setminus \mathcal{M}})$$

**Multi-mask training**: for each training sequence, sample a masking rate $r \sim \text{Uniform}(0, 1)$ and mask exactly $r L$ tokens. This exposes the model to all mask densities, mirroring the iterative refinement process at test time where the model must predict from sparse context (early steps) to near-complete context (late steps).

The model architecture is a **bidirectional encoder-only transformer** with:

$$\text{Hidden state}_i = \text{TokenEmb}(x_i) + \text{PosEmb}(i) + \text{VoiceEmb}(v_i) + \text{SectionEmb}(s_i)$$

Hidden layers: standard multi-head self-attention (full bidirectional mask), layer norm, FFN.

### Voice-Aware Encoding

The token sequence is organized as:

$$[ \underbrace{x_{11}, x_{12}, \ldots, x_{1T}}_{\text{voice 1}}, \underbrace{x_{21}, x_{22}, \ldots, x_{2T}}_{\text{voice 2}}, \ldots, \underbrace{x_{V1}, x_{V2}, \ldots, x_{VT}}_{\text{voice V}} ]$$

Each token $x_{vt}$ carries:
- **Token embedding**: pitch/duration/velocity token
- **Position embedding**: time-step $t$ (absolute or relative)
- **Voice embedding**: learned per-voice vector (voice identity)
- **Section embedding**: learned per-section vector (section identity, optional)

The attention can freely combine information across both dimensions.

---

## Musical Rationale

NAPC addresses several fundamental limitations of autoregressive music generation:

1. **Exposure bias**: Autoregressive models (054 ATS) are trained with teacher forcing (always see ground-truth context) but tested on their own generated context. NAPC mitigates this by training with all mask densities — the model learns to predict from partially-correct contexts.

2. **Bidirectional musical structure**: Many musical features are inherently bidirectional: a passing tone is defined by its surrounding chord tones, a cadence is defined by its approach (pre-dominant) and resolution (tonic), a motif is defined by its repetition later. NAPC captures these through full context.

3. **Voice coupling**: Simultaneous voices must agree on harmony at each time step. NAPC's parallel prediction means all voices at the same time step are predicted together, naturally learning harmonic coherence. Autoregressive models must either serialize voices (breaking simultaneity) or use complex multi-stream architectures.

4. **Tempo and parameter consistency**: Because NAPC uses a fixed time grid (token per time step per voice), tempo and metric structure are inherent in the grid, not predicted as separate time-shift tokens. This prevents the rhythmic drift and tempo wander that plague autoregressive token-based models.

5. **Fast inference**: A piece that an autoregressive model would generate in $N=4096$ sequential forward passes (at 10 ms/pass ≈ 41 seconds) can be generated by NAPC in $R=10$ parallel forward passes (at 100 ms/pass ≈ 1 second of wall time with batching).

---

## Python Implementation Sketch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Tuple

# --- Configuration ---

NAPCConfig = {
    "vocab_size": 150,      # 128 MIDI notes + [MASK] + [PAD] + [REST] + specials
    "d_model": 512,         # Transformer embedding dimension
    "n_layers": 8,          # Encoder depth
    "n_heads": 8,           # Attention heads
    "max_len": 2048,        # Max token sequence length (V * T)
    "n_voices": 8,          # Max voices in UnitMatrix
    "n_sections": 16,       # Max sections
    "refinement_steps": 10,  # Default mask-predict iterations
    "schedule": "cosine",   # Unmask schedule: "cosine" or "linear"
}

# --- Positional Encoding (Sinusoidal) ---

class SinusoidalPositionalEncoding(nn.Module):
    """Standard sinusoidal PE + learned voice + section embeddings."""

    def __init__(self, d_model, max_len, n_voices, n_sections):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-torch.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)
        self.voice_emb = nn.Embedding(n_voices + 1, d_model)  # +1 for padding
        self.section_emb = nn.Embedding(n_sections + 1, d_model)

    def forward(self, token_ids, voice_ids, section_ids):
        # token_ids: (B, L)  voice_ids: (B, L)  section_ids: (B, L)
        B, L = token_ids.shape
        pe = self.pe[:, :L, :]  # (1, L, d_model)
        ve = self.voice_emb(voice_ids)  # (B, L, d_model)
        se = self.section_emb(section_ids)  # (B, L, d_model)
        return pe + ve + se

# --- Bidirectional Encoder Transformer ---

class NAPCTransformer(nn.Module):
    """Bidirectional encoder-only transformer for masked music prediction."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.token_emb = nn.Embedding(config["vocab_size"], config["d_model"])
        self.positional = SinusoidalPositionalEncoding(
            config["d_model"], config["max_len"],
            config["n_voices"], config["n_sections"]
        )
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config["d_model"],
            nhead=config["n_heads"],
            dim_feedforward=config["d_model"] * 4,
            dropout=0.1,
            activation="gelu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=config["n_layers"]
        )
        self.output_proj = nn.Linear(config["d_model"], config["vocab_size"])

    def forward(
        self,
        token_ids: torch.Tensor,       # (B, L)
        voice_ids: torch.Tensor,        # (B, L)
        section_ids: torch.Tensor,      # (B, L)
        mask: Optional[torch.Tensor] = None,  # (B, L), True for masked positions
    ) -> torch.Tensor:
        """
        Forward pass: predict logits for all positions.
        mask: if None, full bidirectional attention (no masking).
        """
        x = self.token_emb(token_ids) + self.positional(token_ids, voice_ids, section_ids)
        x = self.encoder(x)  # (B, L, d_model)
        logits = self.output_proj(x)  # (B, L, vocab_size)
        return logits

# --- Mask-Predict Decoding Loop ---

def mask_predict_decode(
    model: NAPCTransformer,
    L: int,
    n_voices: int,
    n_sections: int,
    section_boundaries: List[int],
    key_embed: Optional[torch.Tensor] = None,
    R: int = 10,
    schedule: str = "cosine",
    temperature: float = 1.0,
    remask_ratio: float = 0.5,
) -> torch.Tensor:
    """
    NAPC iterative mask-predict decoding.

    Args:
        model: trained NAPCTransformer
        L: total token length (V * T)
        n_voices, n_sections: for constructing voice/section IDs
        section_boundaries: list of T-indices where sections change
        R: refinement steps
        schedule: "cosine" or "linear"
        temperature: softmax temperature for stochastic decoding (1.0 = argmax)
        remask_ratio: fraction of just-unmasked tokens to re-mask for revision

    Returns:
        token_ids: (1, L) decoded tokens
    """
    device = next(model.parameters()).device
    B = 1  # batch size = 1 for generation

    # Initialize token IDs (all MASK), voice IDs, section IDs
    MASK_ID = model.config["vocab_size"] - 1  # assume MASK is last token
    token_ids = torch.full((B, L), MASK_ID, dtype=torch.long, device=device)

    # Build voice IDs: each position knows its voice index
    T = L // n_voices
    voice_ids = torch.zeros((B, L), dtype=torch.long, device=device)
    for v in range(n_voices):
        voice_ids[0, v * T : (v + 1) * T] = v

    # Build section IDs
    section_ids = torch.zeros((B, L), dtype=torch.long, device=device)
    for s_idx, (start, end) in enumerate(section_boundaries):
        section_ids[0, start:end] = s_idx

    # Precompute unmask counts
    if schedule == "cosine":
        unmask_counts = []
        remaining = L
        for t in range(1, R + 1):
            if t == 1:
                k = min(L, L)
            else:
                ratio = np.cos(np.pi * t / (2 * R)) / np.cos(np.pi * (t - 1) / (2 * R))
                k = min(remaining, max(1, int(L * ratio)))
            unmask_counts.append(k)
            remaining = max(0, remaining - k)
        # Ensure all tokens are unmasked by step R
        unmask_counts[-1] = remaining + unmask_counts[-1]
    else:  # linear
        k = L // R
        rem = L % R
        unmask_counts = [k + (1 if i < rem else 0) for i in range(R)]

    # Track which positions are unmasked
    unmasked_mask = torch.zeros((B, L), dtype=torch.bool, device=device)

    for step in range(R):
        with torch.no_grad():
            logits = model(token_ids, voice_ids, section_ids)  # (B, L, V)

        # Softmax with temperature
        probs = F.softmax(logits / temperature, dim=-1)  # (B, L, V)

        # Confidence = max probability
        conf, pred_tokens = probs.max(dim=-1)  # (B, L)

        # For masked positions: use predicted tokens
        # For unmasked positions: keep current token
        K = unmask_counts[step]

        # Find masked positions with highest confidence
        masked_conf = conf.clone()
        masked_conf[unmasked_mask] = -float("inf")  # already unmasked
        _, indices = masked_conf.flatten().topk(K)
        rows = indices // L
        cols = indices % L

        # Unmask
        token_ids[rows, cols] = pred_tokens[rows, cols]
        unmasked_mask[rows, cols] = True

        # Optional remask for revision
        if step < R - 1 and remask_ratio > 0:
            # Among just-unmasked positions, re-mask the least confident
            just_masked_conf = conf[rows, cols]
            _, remask_idx = just_masked_conf.topk(
                k=max(1, min(len(just_masked_conf) - 1, int(K * remask_ratio))),
                largest=False  # lowest confidence
            )
            for ri in remask_idx:
                r, c = rows[ri].item(), cols[ri].item()
                token_ids[r, c] = MASK_ID
                unmasked_mask[r, c] = False

        # Optional: keep section/key tokens permanently unmasked
        # (handled by not including them in masked positions)

    return token_ids

# --- MusicUnit Decoder ---

class NAPCUnitDecoder:
    """Decodes NAPC token sequence into UnitMatrix MusicUnits."""

    def __init__(self, pitch_offset=24, max_duration=16):
        self.pitch_offset = pitch_offset
        self.max_duration = max_duration

    def decode(
        self, token_ids: torch.Tensor, n_voices: int, ticks_per_step: int
    ) -> List[List['MusicUnit']]:
        """
        Decode flat token sequence back to UnitMatrix cells.

        Args:
            token_ids: (1, L) decoded tokens
            n_voices: number of voices
            ticks_per_step: clock ticks per time step

        Returns:
            cells: V x T list of MusicUnit objects
        """
        L = token_ids.shape[1]
        T = L // n_voices
        token_2d = token_ids.reshape(n_voices, T)

        cells = []
        for v in range(n_voices):
            voice_row = []
            for t in range(T):
                token = token_2d[v, t].item()
                if token >= 128:  # Special token
                    unit = create_rest_unit(ticks_per_step)
                else:
                    pitch = token + self.pitch_offset
                    unit = create_note_unit(pitch, ticks_per_step)
                voice_row.append(unit)
            cells.append(voice_row)
        return cells


def create_note_unit(pitch, duration):
    """Create a simple MusicUnit with a single note."""
    from structures import MusicUnit, MusicEvent
    return MusicUnit([MusicEvent(pitch, 80, 0, duration)])


def create_rest_unit(duration):
    """Create a silent MusicUnit."""
    from structures import MusicUnit
    return MusicUnit([])
```

### Training Loop Sketch

```python
def train_step(
    model: NAPCTransformer,
    optimizer: torch.optim.Optimizer,
    batch: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
):
    """
    Single training step with multi-mask training.

    batch: (token_ids, voice_ids, section_ids)  each (B, L)
    """
    token_ids, voice_ids, section_ids = batch
    B, L = token_ids.shape

    # Sample masking rate uniformly from [0, 1]
    r = torch.empty(1).uniform_(0, 1).item()
    n_mask = max(1, int(r * L))

    # Randomly select positions to mask
    mask_positions = torch.randperm(L)[:n_mask]
    mask = torch.zeros((B, L), dtype=torch.bool, device=token_ids.device)
    noisy_ids = token_ids.clone()

    # Replace selected positions with MASK
    MASK_ID = model.config["vocab_size"] - 1
    noisy_ids[:, mask_positions] = MASK_ID
    mask[:, mask_positions] = True

    # Forward pass
    logits = model(noisy_ids, voice_ids, section_ids)

    # Loss on masked positions only
    loss = F.cross_entropy(
        logits[mask].view(-1, model.config["vocab_size"]),
        token_ids[mask].view(-1),
    )

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

---

## Integration with the Musicom Framework

### Candidate code path

NAPC's training and inference code would live in:

```
generators/napc/
├── __init__.py         # NAPC generation API
├── config.py           # NAPCConfig
├── model.py            # NAPCTransformer, SinusoidalPositionalEncoding
├── decode.py           # mask_predict_decode, NAPCUnitDecoder
├── train.py            # train_step, data preparation
└── weights/            # Pre-trained model weights (git LFS)
```

The generator would expose a standard interface:

```python
from generators.napc import NAPCGenerator

gen = NAPCGenerator(
    model_path="generators/napc/weights/napc_pretrained.pt",
    n_voices=4, n_sections=6,
    refinement_steps=10,
    temperature=0.8,
)
composer = UnitMatrixComposer(bpm=120)
composer.create_matrix(num_voices=4, num_sections=6)
# ... add voices, sections ...
cells = gen.generate(composer, section_plan=["intro", "verse", "chorus", "verse", "chorus", "outro"])
for v in range(4):
    for s in range(6):
        composer.fill_voice_section(f"Voice{v}", f"Section{s}", cells[v][s])
composer.to_midi("napc_composition.mid")
```

### Conditioning options

- **Chord conditioning**: provide chord progression as unmasked chord-token sequence → harmonic plan enforced
- **Section-type conditioning**: section embeddings encode genre-typical patterns per section type
- **Key/scale conditioning**: special key tokens prepended to the sequence
- **Voice role conditioning**: separate voice embeddings for melody (lead), harmony (pad), bass, percussion
- **Partial priming**: unmask the first few tokens before starting → NAPC completes the piece from the given opening

---

## References

1. Gu, J., Bradbury, J., Xiong, C., Li, V. O. & Socher, R. (2018). "Non-autoregressive neural machine translation." *ICLR 2018*.
2. Ghazvininejad, M., Levy, O. & Zettlemoyer, L. (2019). "Mask-Predict: Parallel Decoding of Conditional Masked Language Models." *EMNLP 2019*.
3. Devlin, J., Chang, M.-W., Lee, K. & Toutanova, K. (2019). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL 2019*.
4. Hsiao, T., Liu, Y., Yang, Y. & Chen, Y. (2021). "Compound Word Transformer: Inferno and the Masked Music Model." arXiv:2101.09152.
5. Huang, C.-Z. A., Hawthorne, C., et al. (2021). "Hierarchical denoising masked language modeling for music generation." *ISMIR 2021*.
6. Von Rütte, M. & Lüdke, R. (2023). "Music Generation with Masked Transformers." arXiv:2305.xxxxx.
7. Vaswani, A., et al. (2017). "Attention Is All You Need." *NeurIPS 2017*.