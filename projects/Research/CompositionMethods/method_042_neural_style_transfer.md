# Neural Style Transfer for Music (Method 042)

## **Description**
Neural Style Transfer (NST) for Music is an AI-driven composition method that applies the stylistic characteristics of a reference musical piece (the "style") to the structural content of another piece (the "content"). Originally developed for visual art (Gatys et al., 2015), NST uses deep convolutional neural networks (CNNs) to separate and recombine content and style representations. In music, this enables the generation of new compositions that maintain the melodic/harmonic/rhythmic structure of a source piece while adopting the textural, timbral, or genre-specific characteristics of a different musical style.

## **Technical Mechanics**
The method operates on audio or MIDI representations through a pre-trained music encoder (e.g., MusicCNN, OpenL3, or a custom CNN trained on musical features). The process involves:

1. **Content Representation**: Extract deep feature maps from intermediate layers of the encoder applied to the content piece. These layers capture high-level structural information (melodic contours, harmonic progressions, rhythmic patterns).

2. **Style Representation**: Compute Gram matrices (feature correlations) from multiple layers of the encoder applied to the style piece. Gram matrices capture texture, timbre, and statistical properties without preserving exact note sequences.

3. **Optimization**: Generate a new audio/MIDI representation by minimizing a joint loss function:
   $$L_{total} = \alpha \cdot L_{content} + \beta \cdot L_{style}$$
   where:
   - $L_{content} = ||F_{content}^{l} - F_{generated}^{l}||^2$ (MSE between content features at layer $l$)
   - $L_{style} = \sum_{l} w_l \cdot ||G_{style}^{l} - G_{generated}^{l}||^2$ (weighted sum of Gram matrix differences across layers)
   - $\alpha, \beta$ control the balance between content preservation and style adoption

4. **Iterative Refinement**: Use gradient descent (Adam optimizer) to update the generated representation until convergence or until the loss falls below a threshold.

## **Musical Elements Framework**
- **PITCH**: Pitch content is primarily inherited from the content piece. The encoder's deep layers preserve melodic contours and harmonic intervals. Style transfer modifies pitch *distribution* (e.g., shifting from diatonic to chromatic if the style piece uses extended harmony) but maintains the underlying pitch *structure*.
- **RHYTHM**: Rhythmic patterns are preserved from the content piece at the structural level (beat grid, phrase lengths). Style transfer affects rhythmic *texture* (e.g., quantization strength, swing feel, micro-timing variations) based on the style piece's rhythmic statistics captured in the Gram matrices.
- **HARMONY**: Harmonic progressions are inherited from the content piece. Style transfer modifies harmonic *vocabulary* (e.g., adding jazz extensions, modal interchange, or microtonal inflections) while preserving the functional harmonic skeleton (I-IV-V-I remains intact, but voicings and extensions change).
- **STRUCTURE**: Macro-form (section boundaries, phrase lengths) is preserved from the content piece. Style transfer can modify *transition characteristics* (e.g., smooth crossfades vs. hard cuts) and *repetition patterns* (e.g., adding variations on repeated sections) based on the style piece's structural statistics.
- **TEXTURE**: Texture is the primary domain of style transfer. Timbral characteristics, instrumental layering, density, and spectral balance are adopted from the style piece. Gram matrices capture the correlation between frequency bands, enabling the transfer of "warmth," "brightness," "sparsity," or "density" without copying exact sounds.

## **UnitMatrix Integration (Voices & Sections)**
- **Rows (Voices)**: Represent individual instrument tracks or frequency bands (e.g., Lead Melody, Harmony Pad, Bass, Percussion). Each voice's content features are extracted separately, allowing per-voice style transfer.
- **Columns (Sections)**: Represent sequential formal sections of the piece (e.g., Intro, Verse, Chorus, Bridge, Outro). Style transfer parameters ($\alpha, \beta$) can vary per section, enabling gradual style morphing or section-specific styling.
- **Cells**: Each cell $U_{v, s}$ contains:
  - `{PITCH}`: Pitch sequence inherited from the content piece, with style-driven modifications to pitch distribution and microtonal inflections.
  - `{RHYTHM}`: Rhythmic structure from the content piece, with style-driven modifications to micro-timing, swing, and quantization.
  - `{TEXTURE}`: Timbral and textural characteristics adopted from the style piece, encoded as spectral envelope parameters, instrumental voicing, and density coefficients.
- **Mapping Flow**:
  1. Encode the content piece into a UnitMatrix representation (voices × sections × features).
  2. Encode the style piece into Gram matrices at multiple encoder layers.
  3. For each section $s$ and voice $v$, initialize a generated representation $G_{v,s}$ as a copy of the content representation $C_{v,s}$.
  4. Iteratively update $G_{v,s}$ using gradient descent to minimize $L_{total}$ with section-specific weights $\alpha_s, \beta_s$.
  5. Decode the optimized $G_{v,s}$ back into MIDI events or audio frames and write them into the UnitMatrix cell.
  6. Validate the result using the musicom engine's zero-drift gate (`composer.validate()`).

## **Implementation Requirements (Python/PyTorch)**
```python
import torch
import torch.nn as nn
import torch.optim as optim
from structures import MusicUnit, MusicEvent, UnitMatrix
from workflows.unitmatrix_composer import UnitMatrixComposer

class MusicEncoder(nn.Module):
    """Pre-trained music encoder (e.g., MusicCNN, OpenL3)."""
    def __init__(self):
        super().__init__()
        # Placeholder for actual encoder architecture
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3)
    
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        gram1 = self.gram_matrix(x)
        x = torch.relu(self.conv2(x))
        gram2 = self.gram_matrix(x)
        x = torch.relu(self.conv3(x))
        return x, [gram1, gram2]
    
    def gram_matrix(self, x):
        b, c, h, w = x.size()
        features = x.view(b, c, h * w)
        gram = torch.bmm(features, features.transpose(1, 2))
        return gram / (c * h * w)

def neural_style_transfer(content_unit, style_grams, encoder, alpha=1.0, beta=1.0, lr=0.01, epochs=500):
    """
    Apply neural style transfer to a MusicUnit.
    content_unit: MusicUnit from the content piece
    style_grams: List of Gram matrices from the style piece
    encoder: Pre-trained MusicEncoder
    alpha: Content weight
    beta: Style weight
    """
    # Initialize generated representation as copy of content
    generated = content_unit.to_tensor().clone().requires_grad_(True)
    optimizer = optim.Adam([generated], lr=lr)
    
    # Extract content features
    with torch.no_grad():
        content_features, _ = encoder(generated.unsqueeze(0).unsqueeze(0))
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        # Forward pass
        gen_features, gen_grams = encoder(generated.unsqueeze(0).unsqueeze(0))
        
        # Content loss
        content_loss = nn.MSELoss()(gen_features, content_features)
        
        # Style loss
        style_loss = 0
        for g_gram, gen_gram in zip(style_grams, gen_grams):
            style_loss += nn.MSELoss()(gen_gram, g_gram.unsqueeze(0))
        
        # Total loss
        loss = alpha * content_loss + beta * style_loss
        loss.backward()
        optimizer.step()
    
    # Convert back to MusicUnit
    return MusicUnit.from_tensor(generated.detach())
```

## **Integration Notes**
- Neural Style Transfer pairs with methods 039 (Spectral Morphology Analysis) and 041 (Ant Colony Optimization): SMA provides spectral features for style encoding, while ACO can optimize the content structure before style transfer.
- The method is computationally expensive ($\mathcal{O}(E \cdot N^2)$ where $E$ = epochs, $N$ = encoder parameters). Use GPU acceleration for real-time applications.
- Style transfer works best when content and style pieces share similar tempo and key. Pre-process with time-stretching and pitch-shifting if needed.
- For MIDI-based workflows, encode MIDI piano rolls as 2D images (pitch × time) and use image-based NST architectures (Gatys et al.) adapted for music.
- The method enables "genre morphing" — take a classical melody and apply jazz harmony texture, or take a pop structure and apply ambient textural characteristics.
- Limitation: NST can produce artifacts (unnatural timbres, rhythmic glitches) if $\beta$ is too high. Use $\alpha/\beta \geq 0.5$ to preserve content integrity.
- Validation: After style transfer, run `composer.validate()` to ensure zero-drift compliance. If validation fails, reduce $\beta$ or increase $\alpha$.
