# Method 054 — Autoregressive Transformer Sequencing (ATS)

**Paradigm:** AI-Driven (Deep Generative)
**Category:** Symbolic sequence generation via causal transformer decoder
**Status:** Indexed in methods_db.md (row 054) + this standalone reference

## Overview

Autoregressive Transformer Sequencing (ATS) generates symbolic music by treating composition as conditional sequence modeling. A musical score (or UnitMatrix) is serialized into a stream of discrete event tokens; a causal (decoder-only) transformer with relative-position attention learns the conditional distribution of the next token given all prior tokens; new music is produced by autoregressive sampling and deserializing the token stream back into grid-aligned symbolic events.

This fills the autoregressive gap in the Musicom method corpus: the DB already covered diffusion (047 DSMG) and VAE latent interpolation (046 VAE-LSI) for deep generation, but no method modeled the discrete symbolic surface token-by-token.

## Tokenization (REMI-style event vocabulary)

A bar of music becomes a token sequence:

```
[ tempo=120 ] [ bar=1 ] [ chord=C ] [ time-shift=0 ] [ note-on C4 ] [ velocity=95 ]
[ time-shift=1 ] [ note-on E4 ] [ time-shift=1 ] [ note-on G4 ] [ time-shift=1 ]
[ note-off C4 ] [ note-off E4 ] [ note-off G4 ] [ bar=2 ] [ chord=Am ] ...
```

Token types:
- **Pitch / Note-on**: discrete MIDI pitch for a sounding note.
- **Velocity**: dynamics token.
- **Note-off**: releases a note (REMI keeps durations explicit).
- **Time-shift**: advances the grid position by a fixed quantization step (e.g., 16th-note).
- **Tempo / Bar / Chord**: control tokens anchoring meter, form, and harmony.
- **Section-id**: form/harmony prompt tokens forcing structural labels.

## Model

Decoder-only transformer (GPT-2 style). For a token sequence $x_1, \dots, x_t$:

$$P(x_{t+1} \mid x_1, \dots, x_t) = \text{softmax}\left(\frac{Q_t K_{<t}^{\top}}{\sqrt{d_k}} \cdot M_{\text{causal}} \right) W_O$$

Relative position biases (Music Transformer) let attention capture long-range motif recall and phrase structure without absolute-position decay.

Training: teacher-forcing cross-entropy over the token vocabulary. Generation: sample from the logits with temperature $\tau$, top-k, and nucleus (top-p) filtering.

## Musical Elements Framework (PITCH / RHYTHM / HARMONY / STRUCTURE / TEXTURE)

- **PITCH**: token vocabulary encodes discrete MIDI pitches; the model learns pitch-transition statistics conditioned on context. Relative attention preserves long-range melodic coherence. Temperature/top-k control conjunct-vs-leaping contour and diatonic-vs-chromatic usage.
- **RHYTHM**: time-shift tokens quantize inter-onset intervals to the grid. The model jointly predicts onset timing and duration, learning genre-specific rhythmic distributions (backbeat, syncopation, groove density). Tempo/beat tokens anchor output to the metric grid.
- **HARMONY**: vertical coherence from learned co-occurrence of simultaneous note-on tokens (chords) plus chord-conditioning tokens encoding the functional progression (HOME/LIFT/TENSE/TURN). Cross-attention to a chord sequence enforces progression adherence.
- **STRUCTURE**: section-id prompt tokens delimit form (Verse/Chorus/Bridge); the model learns section transition patterns. Macro-form controlled by concatenating a structural prompt before the continuation window.
- **TEXTURE**: two strategies — (a) single polyphonic stream where simultaneous tokens populate multiple voices, or (b) per-voice autoregressive streams sharing a common harmonic/structural context with cross-voice attention for voice independence.

## UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: each voice is a token stream (per-voice decoding) or a register/channel grouping from a single polyphonic stream. Generated notes assigned to voice $v$ by MIDI channel/program token.
- **Columns (Sections)**: section-id prompt tokens emitted at column boundaries; each column's context window generated, then the section token advances to the next formal label.
- **Cells**: $U_{v,s}$ holds `{PITCH}` decoded note events, `{RHYTHM}` onsets from time-shift accumulation quantized to the grid, `{TEXTURE}` voice-role config from the conditioning prompt.
- **Mapping Flow**:
  1. Serialize a seed UnitMatrix or structural prompt (key, tempo, section-id sequence, chord tokens) into the token stream.
  2. Run the causal transformer, sampling the next token.
  3. Append token; repeat until the section budget is reached; emit next section-id at boundaries.
  4. Deserialize tokens into channels, note-on/offs, grid ticks; fill cells.
  5. Run musicom Phase-2 rules pass (quantize to chord tones, voice-leading, zero-drift pad) before MIDI export.

## Pairing with Other Methods

- **047 DSMG (diffusion)**: ATS for discrete symbolic surface; DSMG for continuous/timbre levels. Could use ATS sketches as conditioning for diffusion.
- **046 VAE-LSI**: VAE latent trajectory as the initial prompt state for the ATS decoder.
- **022 MCWS**: MCWS constraint post-filter / quantization on ATS raw output.
- **002 Markov**: ATS generalizes Markov transitions (context window > 1) with learned long-range structure.

## Pitfalls

1. **Token-duration ambiguity** — use REMI explicit note-off + time-shift tokens at fixed resolution to keep durations deterministic.
2. **Metric drift** — autoregressive token counts don't enforce bar alignment; quantize to grid + run `composer.validate()` (zero-drift gate).
3. **Context-window limits** — O(N·H·D) relative attention caps usable context; decode per-section with a condensed summary/chord token across boundaries.
4. **Repetition / mode collapse** — low temperature = safe but repetitive; high temperature = incoherent. Use nucleus (p≈0.9) with mild temperature scheduling.
5. **Voice confusion** — single polyphonic stream entangles voices; prefer per-voice decoding with shared harmonic context.
6. **Model size** — public checkpoints are large; use a small distilled/LoRA fine-tune on in-domain data, or a 2-layer transformer on the local corpus.

## References

- Huang, C.-Z. A., et al. (2018). "Music Transformer: Generating Music with Long-Term Structure." *ICLR*.
- Hsiao, Y.-H., et al. (2021). "Compound Word Transformer" and REMI tokenization in *IJCAI*.
- Oore, S., et al. (2020). "This Time with Feeling: Learning Expressive Musical Performance." *Neural Computation*.
- Radford, A., et al. (2019). "Language Models Are Unsupervised Multitask Learners" (GPT-2 decoder).
- Vaswani, A., et al. (2017). "Attention Is All You Need." *NeurIPS*.